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
    process.stdout.write(`${JSON.stringify(readiness)}\n`);
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
