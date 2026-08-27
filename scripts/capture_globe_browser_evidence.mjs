#!/usr/bin/env node

import { spawn } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

function parseArguments(argv) {
  const values = {};
  for (let index = 2; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || value === undefined) {
      throw new Error(`Expected --name value arguments; received ${key || '<empty>'}`);
    }
    values[key.slice(2)] = value;
  }
  const required = ['browser', 'url', 'width', 'height', 'dom', 'screenshot'];
  for (const key of required) {
    if (!values[key]) throw new Error(`Missing required --${key} argument`);
  }
  values.width = Number(values.width);
  values.height = Number(values.height);
  values.timeoutMs = Number(values['timeout-ms'] || 30000);
  values.reducedMotion = values['reduced-motion'] === 'true';
  values.verifyUrlState = values['verify-url-state'] === 'true';
  if (![values.width, values.height, values.timeoutMs].every(Number.isFinite)) {
    throw new Error('Width, height and timeout must be finite numbers');
  }
  return values;
}

async function waitForDevToolsPort(profileDirectory, browser, deadline) {
  const portFile = join(profileDirectory, 'DevToolsActivePort');
  while (Date.now() < deadline) {
    if (browser.exitCode !== null) {
      throw new Error(`Chrome exited before DevTools became available: ${browser.exitCode}`);
    }
    try {
      const [port] = (await readFile(portFile, 'utf8')).trim().split(/\r?\n/);
      if (port) return Number(port);
    } catch (error) {
      if (error?.code !== 'ENOENT') throw error;
    }
    await delay(100);
  }
  throw new Error('Timed out waiting for Chrome DevToolsActivePort');
}

async function waitForPageEndpoint(port, deadline) {
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/list`);
      if (response.ok) {
        const targets = await response.json();
        const page = targets.find((target) => target.type === 'page');
        if (page?.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
      }
    } catch (_error) {
      // Chrome may publish the port before the target endpoint is ready.
    }
    await delay(100);
  }
  throw new Error('Timed out waiting for a Chrome page target');
}

async function connectCdp(webSocketUrl) {
  const socket = new WebSocket(webSocketUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true });
    socket.addEventListener('error', () => reject(new Error('Chrome DevTools WebSocket failed')), { once: true });
  });

  let nextId = 0;
  const pending = new Map();
  socket.addEventListener('message', (event) => {
    const message = JSON.parse(String(event.data));
    if (!message.id || !pending.has(message.id)) return;
    const { resolve, reject } = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) reject(new Error(JSON.stringify(message.error)));
    else resolve(message.result || {});
  });

  return {
    async send(method, params = {}) {
      const id = ++nextId;
      const response = new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
      socket.send(JSON.stringify({ id, method, params }));
      return response;
    },
    close() {
      socket.close();
    }
  };
}

async function evaluate(cdp, expression, awaitPromise = false) {
  const response = await cdp.send('Runtime.evaluate', {
    expression,
    awaitPromise,
    returnByValue: true
  });
  if (response.exceptionDetails) {
    throw new Error(response.exceptionDetails.text || 'Runtime.evaluate failed');
  }
  return response.result?.value;
}

async function waitForVisualReadiness(cdp, deadline) {
  let lastState = null;
  while (Date.now() < deadline) {
    lastState = await evaluate(cdp, `(() => {
      const root = document.documentElement?.dataset || {};
      const fatal = document.getElementById('fatal-error');
      return {
        ready: root.artemisVisualReady === 'true',
        runtimeReady: root.artemisRuntimeReady === 'true',
        contextSourceFeatureCount: Number(root.artemisContextSourceFeatureCount || 0),
        contextRenderedFeatureCount: Number(root.artemisContextRenderedFeatureCount || 0),
        fatal: fatal && !fatal.hidden ? fatal.textContent : null
      };
    })()`);
    if (lastState?.fatal) throw new Error(lastState.fatal);
    if (
      lastState?.ready
      && lastState.contextSourceFeatureCount > 0
      && lastState.contextRenderedFeatureCount > 0
    ) {
      await evaluate(
        cdp,
        'new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))',
        true
      );
      return lastState;
    }
    await delay(250);
  }
  throw new Error(`Timed out waiting for visual readiness: ${JSON.stringify(lastState)}`);
}

async function verifyUrlStateRestoration(cdp, deadline) {
  const interaction = await evaluate(cdp, `(() => {
    const runtime = window.__ARTEMIS_GLOBE_SPIKE;
    const initialStatus = document.getElementById('temporal-map-status')?.textContent || '';
    const initialTime = runtime.activeTemporalPresetId;
    const initialLayers = [...runtime.activeLayerRefs];
    const allLayers = (runtime.viewIndex.layer_options || []).map((option) => option.layer_ref);
    runtime.selectView(initialTime, allLayers);
    const region = (runtime.data.projection.items || []).find((item) => item.object_type === 'Region');
    if (!region) throw new Error('All-layer view does not expose a Region alternative');
    runtime.selectItem(region.item_id);
    const regionDisclosure = document.getElementById('selection-card')?.textContent || '';
    runtime.selectView(initialTime, initialLayers);

    const range = document.getElementById('temporal-preset');
    range.value = range.max;
    range.dispatchEvent(new Event('input', { bubbles: true }));

    const checkedLayers = [...document.querySelectorAll('#layer-controls input:checked')];
    if (checkedLayers.length > 1) {
      checkedLayers[0].checked = false;
      checkedLayers[0].dispatchEvent(new Event('change', { bubbles: true }));
    }

    const unresolved = document.querySelector('.unresolved-item');
    if (!unresolved) throw new Error('No keyboard-accessible unresolved record is available');
    const unresolvedDisclosure = unresolved.closest('details');
    if (unresolvedDisclosure) unresolvedDisclosure.open = true;
    if (unresolved.getClientRects().length === 0) {
      throw new Error('Unresolved record did not become visibly keyboard-accessible');
    }
    unresolved.click();

    const params = new URLSearchParams(window.location.search);
    return {
      initialStatus,
      updatedStatus: document.getElementById('temporal-map-status')?.textContent || '',
      regionDisclosure,
      ariaValueText: range.getAttribute('aria-valuetext'),
      expectedValueText: (runtime.viewIndex.temporal_presets || []).find(
        (preset) => preset.preset_id === runtime.activeTemporalPresetId
      )?.label || null,
      time: runtime.activeTemporalPresetId,
      layers: [...runtime.activeLayerRefs].sort(),
      item: runtime.selectedItemId,
      urlTime: params.get('time'),
      urlLayers: (params.get('layers') || '').split(',').filter(Boolean).sort(),
      urlItem: params.get('item')
    };
  })()`);

  if (!interaction.time || !interaction.item) throw new Error(`Interaction did not select state: ${JSON.stringify(interaction)}`);
  for (const requiredText of [
    'Reconstruction alternatives',
    'scholarly_reconstruction',
    'analytical_model',
    'Geometry withheld; not rendered.',
    'Coverage / corpus limits'
  ]) {
    if (!interaction.regionDisclosure.includes(requiredText)) {
      throw new Error(`Region inspector did not expose ${requiredText}`);
    }
  }
  if (interaction.initialStatus === interaction.updatedStatus) {
    throw new Error('Timeline interaction did not update the visible globe status');
  }
  if (!interaction.ariaValueText || interaction.ariaValueText !== interaction.expectedValueText) {
    throw new Error('Timeline interaction did not expose a source-bound aria-valuetext');
  }
  if (interaction.urlTime !== interaction.time) throw new Error('Timeline state was not written to the URL');
  if (JSON.stringify(interaction.urlLayers) !== JSON.stringify(interaction.layers)) {
    throw new Error('Layer state was not written to the URL');
  }
  if (interaction.urlItem !== interaction.item) throw new Error('Selection state was not written to the URL');

  await evaluate(cdp, "document.documentElement.dataset.artemisUrlTestReload = 'before'");
  await cdp.send('Page.reload', { ignoreCache: false });
  const reloadDeadline = Math.max(deadline, Date.now() + 30000);
  while (Date.now() < reloadDeadline) {
    const marker = await evaluate(
      cdp,
      "document.documentElement?.dataset?.artemisUrlTestReload || null"
    ).catch(() => 'before');
    if (marker !== 'before') break;
    await delay(100);
  }
  await waitForVisualReadiness(cdp, reloadDeadline);
  const restored = await evaluate(cdp, `(() => {
    const runtime = window.__ARTEMIS_GLOBE_SPIKE;
    return {
      time: runtime.activeTemporalPresetId,
      layers: [...runtime.activeLayerRefs].sort(),
      item: runtime.selectedItemId,
      cardItem: document.getElementById('selection-card')?.dataset.itemId || null
    };
  })()`);
  if (JSON.stringify(restored) !== JSON.stringify({
    time: interaction.time,
    layers: interaction.layers,
    item: interaction.item,
    cardItem: interaction.item
  })) {
    throw new Error(`URL state did not survive reload: ${JSON.stringify({ interaction, restored })}`);
  }

  const invalidCanonical = await evaluate(cdp, `(() => {
    const url = new URL(window.location.href);
    url.searchParams.set('time', 'invalid-time');
    url.searchParams.set('layers', 'invalid-layer');
    url.searchParams.set('item', 'invalid-item');
    history.pushState({ invalid: true }, '', url);
    window.dispatchEvent(new PopStateEvent('popstate', { state: history.state }));
    const runtime = window.__ARTEMIS_GLOBE_SPIKE;
    const params = new URLSearchParams(window.location.search);
    return {
      time: runtime.activeTemporalPresetId,
      layers: [...runtime.activeLayerRefs].sort(),
      item: runtime.selectedItemId,
      urlTime: params.get('time'),
      urlLayers: (params.get('layers') || '').split(',').filter(Boolean).sort(),
      urlItem: params.get('item')
    };
  })()`);
  if (
    invalidCanonical.urlTime !== invalidCanonical.time
    || JSON.stringify(invalidCanonical.urlLayers) !== JSON.stringify(invalidCanonical.layers)
    || invalidCanonical.urlItem !== invalidCanonical.item
  ) {
    throw new Error(`Invalid popstate URL was not canonicalized: ${JSON.stringify(invalidCanonical)}`);
  }

  await evaluate(cdp, 'history.back()');
  let popstateRestored = null;
  while (Date.now() < reloadDeadline) {
    popstateRestored = await evaluate(cdp, `(() => {
      const runtime = window.__ARTEMIS_GLOBE_SPIKE;
      return {
        time: runtime.activeTemporalPresetId,
        layers: [...runtime.activeLayerRefs].sort(),
        item: runtime.selectedItemId
      };
    })()`);
    if (
      popstateRestored.time === interaction.time
      && JSON.stringify(popstateRestored.layers) === JSON.stringify(interaction.layers)
      && popstateRestored.item === interaction.item
    ) break;
    await delay(100);
  }
  if (
    popstateRestored.time !== interaction.time
    || JSON.stringify(popstateRestored.layers) !== JSON.stringify(interaction.layers)
    || popstateRestored.item !== interaction.item
  ) {
    throw new Error(`Back navigation did not restore Explorer State: ${JSON.stringify(popstateRestored)}`);
  }
  return { interaction, restored, invalidCanonical, popstateRestored };
}

async function main() {
  const options = parseArguments(process.argv);
  const profileDirectory = await mkdtemp(join(tmpdir(), 'artemis-chrome-profile-'));
  const deadline = Date.now() + options.timeoutMs;
  const chromeArguments = [
    '--headless=new',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--use-gl=angle',
    '--use-angle=swiftshader',
    '--enable-unsafe-swiftshader',
    '--run-all-compositor-stages-before-draw',
    '--remote-debugging-port=0',
    `--user-data-dir=${profileDirectory}`,
    `--window-size=${options.width},${options.height}`,
    ...(options.reducedMotion ? ['--force-prefers-reduced-motion=reduce'] : []),
    'about:blank'
  ];
  const browser = spawn(options.browser, chromeArguments, { stdio: ['ignore', 'ignore', 'pipe'] });
  let browserLog = '';
  browser.stderr.on('data', (chunk) => {
    browserLog = `${browserLog}${chunk}`.slice(-20000);
  });
  let cdp = null;

  try {
    const port = await waitForDevToolsPort(profileDirectory, browser, deadline);
    const endpoint = await waitForPageEndpoint(port, deadline);
    cdp = await connectCdp(endpoint);
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Page.navigate', { url: options.url });
    const readiness = await waitForVisualReadiness(cdp, deadline);
    const dom = await evaluate(cdp, 'document.documentElement.outerHTML');
    const capture = await cdp.send('Page.captureScreenshot', {
      format: 'png',
      fromSurface: true,
      captureBeyondViewport: false
    });
    await writeFile(options.dom, `${dom}\n`, 'utf8');
    await writeFile(options.screenshot, Buffer.from(capture.data, 'base64'));
    const urlStateRestoration = options.verifyUrlState
      ? await verifyUrlStateRestoration(cdp, deadline)
      : null;
    process.stdout.write(`${JSON.stringify({ ...readiness, urlStateRestoration })}\n`);
  } catch (error) {
    if (browserLog) process.stderr.write(browserLog);
    throw error;
  } finally {
    cdp?.close();
    if (browser.exitCode === null) {
      const browserExited = new Promise((resolve) => browser.once('exit', resolve));
      browser.kill('SIGTERM');
      await Promise.race([browserExited, delay(2000)]);
    }
    await rm(profileDirectory, {
      recursive: true,
      force: true,
      maxRetries: 5,
      retryDelay: 100
    });
  }
}

main().catch((error) => {
  process.stderr.write(`${error?.stack || error}\n`);
  process.exitCode = 1;
});
