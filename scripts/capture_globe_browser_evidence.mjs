#!/usr/bin/env node

import { spawn, execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
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
  values.sourceAwareResearch = values['source-aware-research'] === 'true';
  values.sharedPreviewNavigation = values['shared-preview-navigation'] === 'true';
  values.projectionSwitch = values['projection-switch'] === 'true';
  if (![values.width, values.height, values.timeoutMs].every(Number.isFinite)) {
    throw new Error('Width, height and timeout must be finite numbers');
  }
  return values;
}

async function waitForDevToolsPort(profileDirectory, browser, deadline) {
  const portFile = join(profileDirectory, 'DevToolsActivePort');
  while (Date.now() < deadline) {
    if (browser.exitCode !== null || browser.signalCode !== null) {
      throw new Error(`Chrome exited before DevTools became available: ${browser.exitCode ?? browser.signalCode}`);
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

async function connectCdp(webSocketUrl, deadline) {
  const socket = new WebSocket(webSocketUrl);
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('Timed out connecting Chrome DevTools')), Math.max(1, deadline - Date.now()));
    socket.addEventListener('open', () => { clearTimeout(timer); resolve(); }, { once: true });
    socket.addEventListener('error', () => { clearTimeout(timer); reject(new Error('Chrome DevTools WebSocket failed')); }, { once: true });
  });

  let nextId = 0;
  const pending = new Map();
  socket.addEventListener('close', () => {
    for (const { reject, timer } of pending.values()) {
      clearTimeout(timer);
      reject(new Error('Chrome DevTools WebSocket closed'));
    }
    pending.clear();
  });
  socket.addEventListener('message', (event) => {
    const message = JSON.parse(String(event.data));
    if (!message.id || !pending.has(message.id)) return;
    const { resolve, reject, timer } = pending.get(message.id);
    clearTimeout(timer);
    pending.delete(message.id);
    if (message.error) reject(new Error(JSON.stringify(message.error)));
    else resolve(message.result || {});
  });

  return {
    async send(method, params = {}) {
      const id = ++nextId;
      const response = new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
          pending.delete(id);
          reject(new Error(`Timed out waiting for Chrome DevTools ${method}`));
        }, Math.max(1, deadline - Date.now()));
        pending.set(id, { resolve, reject, timer });
      });
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
    throw new Error(response.exceptionDetails.exception?.description || response.exceptionDetails.text || 'Runtime.evaluate failed');
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

async function verifyPlaceLabels(cdp) {
  await cdp.send('Emulation.setFocusEmulationEnabled', {enabled: true});
  return evaluate(cdp, `(async () => {
    const r = window.__ARTEMIS_GLOBE_SPIKE;
    const nodes = [...document.querySelectorAll('.life-path-marker')];
    if (nodes.length !== 9 || r.data.lifePath.presences.length !== 11) throw new Error('Expected 9 Places / 11 Presences');
    const labels = nodes.filter(n => !n.hidden).map(n => n.querySelector('.place-label'));
    const shown = labels.filter(n => getComputedStyle(n).visibility !== 'hidden');
    for (let i = 0; i < shown.length; i++) for (let j = i + 1; j < shown.length; j++) {
      const a = shown[i].getBoundingClientRect(), b = shown[j].getBoundingClientRect();
      const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (w > 1 && h > 1) throw new Error('Visible Place-label overlap: ' + shown[i].textContent + ' / ' + shown[j].textContent);
    }
    for (const label of shown) for (const node of nodes.filter(n => !n.hidden)) {
      if (label.closest('.life-path-marker') === node) continue;
      const a = label.getBoundingClientRect(), b = node.querySelector('.place-dot').getBoundingClientRect();
      const w = Math.min(a.right, b.right + 2) - Math.max(a.left, b.left - 2);
      const h = Math.min(a.bottom, b.bottom + 2) - Math.max(a.top, b.top - 2);
      if (w > 1 && h > 1) throw new Error('Foreign Place dot overlaps label: ' + label.textContent + ' / ' + node.title);
    }
    let suppressed = 0;
    for (const label of labels) if (label.classList.contains('is-suppressed')) {
      suppressed++;
      const node = label.closest('.life-path-marker');
      if (node.hidden || node.getBoundingClientRect().width < 24 || !node.title || !node.getAttribute('aria-label')) throw new Error('Suppression hid anchor or accessible meaning');
      node.focus({preventScroll: true});
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      if (getComputedStyle(label).visibility === 'hidden') throw new Error('Suppressed label unavailable on keyboard focus: ' + JSON.stringify({place:node.dataset.placeId, focused:document.activeElement === node, matches:node.matches(':focus'), pageFocus:document.hasFocus(), nodeVisibility:getComputedStyle(node).visibility, html:node.outerHTML, rules:[...document.styleSheets].flatMap(s => {try {return [...s.cssRules].filter(r => r.selectorText?.includes('place-label')).map(r => r.cssText);} catch {return [];}})}));
      node.blur();
    }
    const selected = r.data.lifePath.presences.find(p => p.presence_id === r.selectedPresenceId);
    if (selected && getComputedStyle(r.placeMarkers.get(selected.place_ref).getElement().querySelector('.place-label')).visibility === 'hidden') throw new Error('Selected Place label suppressed');
    if (/numbered place|Numbers show chronology|Build from/i.test(document.body.innerText)) throw new Error('Obsolete visible copy');
    return {anchors: nodes.length, visibleLabels: shown.length, suppressedLabels: suppressed, materialLabelOverlaps: 0, materialForeignDotOverlaps: 0};
  })()`, true);
}

async function verifyRegionDisclosure(cdp, deadline) {
  // Retest the two failed user tasks through visible UI, before touching runtime internals.
  const entry = await evaluate(cdp, `(() => {
    const note = document.getElementById('region-reconstruction-note');
    const link = document.getElementById('region-provenance-link');
    function visible(node) {
      if (!node || !node.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })) return false;
      const rect = node.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.left >= 0
        && rect.bottom <= innerHeight && rect.right <= innerWidth;
    }
    if (!visible(note) || note.innerText !== 'Approximate scholarly reconstruction · not exact historical borders.') throw new Error('Failed task: reconstruction limits are not visibly stated');
    if (!visible(link) || !link.innerText.includes('provenance & license (CC-BY-4.0)')) throw new Error('Failed task: provenance/license access is not visible');
    const rect = link.getBoundingClientRect();
    const x = rect.left + rect.width / 2, y = rect.top + rect.height / 2;
    if (!link.contains(document.elementFromPoint(x, y))) throw new Error('Provenance link is obstructed or not clickable');
    if (new URL(link.href).origin !== location.origin || !new URL(link.href).pathname.endsWith('/source_manifest.json')) throw new Error('Provenance link escaped the published source package');
    return { x, y, href: link.href, returnUrl: location.href, note: note.innerText };
  })()`);
  await cdp.send('Input.dispatchMouseEvent', { type: 'mousePressed', x: entry.x, y: entry.y, button: 'left', clickCount: 1 });
  await cdp.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: entry.x, y: entry.y, button: 'left', clickCount: 1 });
  let opened = null;
  const navigationDeadline = Math.min(deadline, Date.now() + 15000);
  while (Date.now() < navigationDeadline) {
    try {
      opened = await evaluate(cdp, `(() => ({ url: location.href, text: document.body?.innerText || '' }))()`);
      if (opened.url === entry.href && opened.text.includes('"attribution"') && opened.text.includes('CC-BY-4.0') && opened.text.includes('ad28a691b7c07c1fca89d0e0636d324667d2a258')) break;
    } catch (_) { /* Navigation replaces the evaluation context. */ }
    await delay(100);
  }
  if (opened?.url !== entry.href || !opened.text.includes('"attribution"') || !opened.text.includes('CC-BY-4.0') || !opened.text.includes('ad28a691b7c07c1fca89d0e0636d324667d2a258')) throw new Error('Failed task: clicking provenance did not open the pinned licensed manifest');
  await cdp.send('Page.navigate', { url: entry.returnUrl });
  await waitForVisualReadiness(cdp, deadline);
  return { reconstructionVisible: true, reconstructionText: entry.note, provenanceLinkVisible: true, provenanceClickOpenedManifest: true, manifestUrl: entry.href, license: 'CC-BY-4.0' };
}

async function verifyTemporalRegion(cdp) {
  return evaluate(cdp, `(async () => {
    const runtime = window.__ARTEMIS_GLOBE_SPIKE;
    if (runtime.data.lifePath.available !== false) throw new Error('Region artifact unexpectedly enabled Leonardo Life Path');
    const presets = runtime.viewIndex?.temporal_presets || [];
    if (presets.length !== 3) throw new Error('Expected three source-supported Region time presets');
    const selector = document.getElementById('temporal-preset');
    if (!selector || selector.options.length !== 3 || selector.hidden) throw new Error('Canonical Region time selector is not available');
    if (document.querySelector('.mode-switch') && !document.querySelector('.mode-switch').hidden) throw new Error('Leonardo Range/Scrub mode switch leaked into Region proof');
    const snapshots = [];
    const nativeIntervals = ['91–105 CE', '106–113 CE', '114–116 CE'];
    for (const [index, preset] of presets.entries()) {
      selector.value = preset.preset_id;
      selector.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      const item = (runtime.data.projection.items || []).find(item => item.object_ref === 'region-roman-empire');
      if (!item || item.object_type !== 'Region' || item.temporal_membership !== 'active' || item.geometry_refs.length !== 1) throw new Error('Canonical time did not project an active Region');
      if (runtime.data.state.temporal_selection.start !== preset.temporal_selection.start) throw new Error('Canonical time differs from selected preset');
      if (!selector.selectedOptions[0].textContent.includes(nativeIntervals[index])) throw new Error('Selected label lost the source-native interval');
      const geometry = runtime.data.projection.geometries.find(g => g.geometry_ref === item.geometry_refs[0]);
      if (!geometry?.geometry) throw new Error('Selected Region geometry is missing');
      if (runtime.data.projection.geometries.some(g => g.geometry?.type === 'LineString')) throw new Error('Region proof introduced route geometry');
      runtime.selectItem(item.item_id);
      const card = document.getElementById('selection-card');
      for (const disclosure of card.querySelectorAll('details')) disclosure.open = true;
      const details = card.textContent;
      for (const expected of ['Cliopatria', 'CC-BY-4.0', 'source_manifest.json', 'scholarly_reconstruction', 'source_reconstruction', 'no day precision or interpolation', 'not exact historical borders', 'missing coverage is not historical absence', nativeIntervals[index]]) {
        if (!details.includes(expected)) throw new Error('Region details lost: ' + expected);
      }
      if (!/[/]blob[/][a-f0-9]{40}[/]/.test(details) || !/[/]features[/][0-9]+/.test(details)) throw new Error('Pinned source/evidence locator is missing');
      if (document.querySelector('.sequence-note, .route-note') || /dashed links|chevrons|not travel routes|numbered place|Build from/i.test(document.body.textContent)) throw new Error('Life Path copy leaked into Region artifact');
      snapshots.push({ preset: preset.preset_id, interval: nativeIntervals[index], geometryRef: item.geometry_refs[0], geometry: JSON.stringify(geometry.geometry), canonicalTime: runtime.data.state.temporal_selection.start });
    }
    if (new Set(snapshots.map(snapshot => snapshot.geometry)).size !== 3) throw new Error('The three source-native outlines are not distinct');
    return { presets: presets.map(p => p.preset_id), snapshots: snapshots.map(({ geometry, ...snapshot }) => snapshot), routeGeometry: null, chronologyNotesAbsent: true, provenanceAndUncertaintyPreserved: true };
  })()`, true);
}

async function verifyUrlStateRestoration(cdp, deadline) {
  const interaction = await evaluate(cdp, `(async () => {
    const runtime = window.__ARTEMIS_GLOBE_SPIKE;
    const initialStatus = document.getElementById('temporal-map-status')?.textContent || '';
    const presences = runtime.data.lifePath.presences;
    const axisValues = runtime.data.lifePath.time_axis.values;
    if (presences.length !== 11) throw new Error('M5 whole-life path does not expose eleven presences');
    if ((runtime.data.lifePath.macro_periods || []).length !== 6) {
      throw new Error('M5 whole-life path does not expose six macro periods');
    }
    if (!runtime.map.getLayer('life-path-chronology-line')) {
      throw new Error('M5 chronological presentation links are missing');
    }
    if (runtime.data.lifePath.route_policy.historical_route_geometry_permitted !== false
        || runtime.data.lifePath.route_policy.chronological_connector_is_route !== false
        || runtime.data.lifePath.transitions.some((link) => link.route_geometry !== null || link.route_status !== 'unknown_route')) {
      throw new Error('Chronological presentation must not promote unknown historical routes');
    }
    const uniquePlaces = new Set(presences.map(p => p.place_ref));
    if (document.querySelectorAll('.life-path-marker').length !== uniquePlaces.size) throw new Error('Map must have one anchor per Place');
    for (const place of uniquePlaces) {
      const episodes = presences.filter(p => p.place_ref === place);
      const anchor = runtime.placeMarkers.get(place);
      if (episodes.some(p => runtime.lifePathMarkers.get(p.presence_id) !== anchor)) throw new Error('Presence aliases must share the Place anchor');
      const coordinate = anchor.getLngLat();
      if (Math.abs(coordinate.lng - episodes[0].coordinates[0]) > 1e-9 || Math.abs(coordinate.lat - episodes[0].coordinates[1]) > 1e-9) throw new Error('Place anchor moved: ' + JSON.stringify({place, actual: coordinate, expected: episodes[0].coordinates}));
      if (episodes.length > 1) {
        for (const episode of episodes) {
          runtime.selectPresence(episode.presence_id);
          if (runtime.selectedPresenceId !== episode.presence_id || anchor.getElement().getAttribute('aria-pressed') !== 'true') throw new Error('Repeated Presence selection collapsed');
          if (new URLSearchParams(location.search).get('presence') !== episode.presence_id) throw new Error('Repeated Presence URL identity lost');
        }
      }
    }
    const nonzero = runtime.data.lifePath.transitions.filter(t => { const a = presences.find(p => p.presence_id === t.from_presence_ref), b = presences.find(p => p.presence_id === t.to_presence_ref); return a.coordinates.some((v, i) => v !== b.coordinates[i]); });
    if (runtime.chronologyCues.size !== nonzero.length) throw new Error('Expected one cue per nonzero connector');
    for (const cue of runtime.chronologyCues.values()) {
      const [a, b] = cue.coordinates, point = cue.marker.getLngLat();
      if (Math.abs(point.lng - (a[0]+b[0])/2) > 1e-9 || Math.abs(point.lat - (a[1]+b[1])/2) > 1e-9) throw new Error('Direction cue must stay at segment midpoint');
      if (![0.12, 0.95].includes(Number(cue.marker.getElement().firstChild.style.opacity))) throw new Error('Cue emphasis missing from glyph');
      if (cue.marker.getElement().getAttribute('aria-hidden') !== 'true') throw new Error('Direction cue is presentation only');
    }
    document.getElementById('close-details')?.click();
    document.getElementById('mode-scrub')?.click();
    const scrubStart = document.getElementById('scrub-start');
    const scrubCurrent = document.getElementById('scrub-current');
    if (scrubStart || !scrubCurrent) throw new Error('Scrub must have one current-time control and no Build from');
    if (runtime.lifePathStartIndex !== 0) throw new Error('Default Scrub origin is not the earliest axis extent');
    scrubCurrent.value = String(axisValues.indexOf('1502'));
    scrubCurrent.dispatchEvent(new Event('input', { bubbles: true }));
    const marker = [...document.querySelectorAll('.life-path-marker')].find(
      (button) => button.getAttribute('aria-label')?.startsWith('Show Cesena summary,')
    );
    if (!marker || marker.hidden) throw new Error('Visible Cesena map marker is unavailable');
    const cameraBefore = {
      center: runtime.map.getCenter().toArray(),
      zoom: runtime.map.getZoom()
    };
    marker.click();
    await new Promise((resolve) => setTimeout(resolve, 320));
    const popupText = document.querySelector('.presence-popup-card')?.textContent || '';
    const detailsAfterFirstClick = document.getElementById('inspector')?.hidden === false;
    marker.click();
    await new Promise((resolve) => setTimeout(resolve, 320));
    const cameraAfter = {
      center: runtime.map.getCenter().toArray(),
      zoom: runtime.map.getZoom()
    };

    const params = new URLSearchParams(window.location.search);
    return {
      initialStatus,
      updatedStatus: document.getElementById('temporal-map-status')?.textContent || '',
      cardText: document.getElementById('selection-card')?.textContent || '',
      popupText,
      detailsAfterFirstClick,
      detailsAfterSecondClick: document.getElementById('inspector')?.hidden === false,
      cameraBefore,
      cameraAfter,
      mode: runtime.lifePathMode,
      from: axisValues[runtime.lifePathStartIndex],
      at: axisValues[runtime.lifePathEndIndex],
      presence: runtime.selectedPresenceId,
      item: runtime.selectedItemId,
      visiblePresenceCount: Number(document.documentElement.dataset.artemisVisiblePresenceCount || 0),
      urlMode: params.get('mode'),
      urlFrom: params.get('from'),
      urlAt: params.get('at'),
      urlPresence: params.get('presence'),
      urlItem: params.get('item')
    };
  })()`, true);

  if (!interaction.mode || !interaction.presence || !interaction.item) {
    throw new Error(`Interaction did not select life-path state: ${JSON.stringify(interaction)}`);
  }
  for (const requiredText of [
    'Cesena',
    'Leonardo documented in the Cesena survey context',
    'Not established beyond the documented source anchor',
    'exact historical position unknown',
    'Record and location details'
  ]) {
    if (!interaction.cardText.includes(requiredText)) {
      throw new Error(`Life-path presence card did not expose ${requiredText}`);
    }
  }
  if (!interaction.popupText.includes('Cesena') || !interaction.popupText.includes('Open details')) {
    throw new Error(`First marker click did not open a compact popup: ${JSON.stringify(interaction)}`);
  }
  if (interaction.detailsAfterFirstClick || !interaction.detailsAfterSecondClick) {
    throw new Error(`Marker selection did not preserve the two-stage detail flow: ${JSON.stringify(interaction)}`);
  }
  if (JSON.stringify(interaction.cameraBefore) !== JSON.stringify(interaction.cameraAfter)) {
    throw new Error(`Single marker clicks changed the map camera: ${JSON.stringify(interaction)}`);
  }
  if (interaction.initialStatus === interaction.updatedStatus) {
    throw new Error('Timeline interaction did not update the visible globe status');
  }
  if (interaction.visiblePresenceCount !== 7) {
    throw new Error(`Scrub mode did not reveal seven accumulated anchors through 1502: ${JSON.stringify(interaction)}`);
  }
  if (
    interaction.urlMode !== interaction.mode
    || interaction.urlFrom !== interaction.from
    || interaction.urlAt !== interaction.at
    || interaction.urlPresence !== interaction.presence
    || interaction.urlItem !== interaction.item
  ) {
    throw new Error(`Life-path state was not written to the URL: ${JSON.stringify(interaction)}`);
  }

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
    const axisValues = runtime.data.lifePath.time_axis.values;
    return {
      mode: runtime.lifePathMode,
      from: axisValues[runtime.lifePathStartIndex],
      at: axisValues[runtime.lifePathEndIndex],
      presence: runtime.selectedPresenceId,
      item: runtime.selectedItemId,
      popupPresence: runtime.popupPresenceId,
      popupText: document.querySelector('.presence-popup-card')?.textContent || '',
      detailsOpen: document.getElementById('inspector')?.hidden === false
    };
  })()`);
  if (JSON.stringify(restored) !== JSON.stringify({
    mode: interaction.mode,
    from: interaction.from,
    at: interaction.at,
    presence: interaction.presence,
    item: interaction.item,
    popupPresence: interaction.presence,
    popupText: interaction.popupText,
    detailsOpen: false
  })) {
    throw new Error(`URL state did not survive reload: ${JSON.stringify({ interaction, restored })}`);
  }

  const invalidCanonical = await evaluate(cdp, `(() => {
    const url = new URL(window.location.href);
    url.searchParams.set('mode', 'invalid-mode');
    url.searchParams.set('start', 'invalid-start');
    url.searchParams.set('end', 'invalid-end');
    url.searchParams.set('from', 'invalid-from');
    url.searchParams.set('at', 'invalid-at');
    url.searchParams.set('presence', 'invalid-presence');
    url.searchParams.set('item', 'invalid-item');
    history.pushState({ invalid: true }, '', url);
    window.dispatchEvent(new PopStateEvent('popstate', { state: history.state }));
    const runtime = window.__ARTEMIS_GLOBE_SPIKE;
    const axisValues = runtime.data.lifePath.time_axis.values;
    const params = new URLSearchParams(window.location.search);
    return {
      mode: runtime.lifePathMode,
      start: axisValues[runtime.lifePathStartIndex],
      end: axisValues[runtime.lifePathEndIndex],
      presence: runtime.selectedPresenceId,
      item: runtime.selectedItemId,
      urlMode: params.get('mode'),
      urlStart: params.get('start'),
      urlEnd: params.get('end'),
      urlFrom: params.get('from'),
      urlAt: params.get('at'),
      urlPresence: params.get('presence'),
      urlItem: params.get('item')
    };
  })()`);
  if (
    invalidCanonical.urlMode !== invalidCanonical.mode
    || invalidCanonical.urlStart !== invalidCanonical.start
    || invalidCanonical.urlEnd !== invalidCanonical.end
    || invalidCanonical.urlFrom !== null
    || invalidCanonical.urlAt !== null
    || invalidCanonical.urlPresence !== invalidCanonical.presence
    || invalidCanonical.urlItem !== invalidCanonical.item
  ) {
    throw new Error(`Invalid popstate URL was not canonicalized: ${JSON.stringify(invalidCanonical)}`);
  }

  await evaluate(cdp, 'history.back()');
  let popstateRestored = null;
  while (Date.now() < reloadDeadline) {
    popstateRestored = await evaluate(cdp, `(() => {
      const runtime = window.__ARTEMIS_GLOBE_SPIKE;
      const axisValues = runtime.data.lifePath.time_axis.values;
      return {
        mode: runtime.lifePathMode,
        from: axisValues[runtime.lifePathStartIndex],
        at: axisValues[runtime.lifePathEndIndex],
        presence: runtime.selectedPresenceId,
        item: runtime.selectedItemId
      };
    })()`);
    if (
      popstateRestored.mode === interaction.mode
      && popstateRestored.from === interaction.from
      && popstateRestored.at === interaction.at
      && popstateRestored.presence === interaction.presence
      && popstateRestored.item === interaction.item
    ) break;
    await delay(100);
  }
  if (
    popstateRestored.mode !== interaction.mode
    || popstateRestored.from !== interaction.from
    || popstateRestored.at !== interaction.at
    || popstateRestored.presence !== interaction.presence
    || popstateRestored.item !== interaction.item
  ) {
    throw new Error(`Back navigation did not restore Explorer State: ${JSON.stringify(popstateRestored)}`);
  }
  return { interaction, restored, invalidCanonical, popstateRestored };
}

async function verifyKeyboardInteraction(cdp, isRegion) {
  async function key(key, code, virtualKey, modifiers = 0) {
    await cdp.send('Input.dispatchKeyEvent', {
      type: 'keyDown', key, code, windowsVirtualKeyCode: virtualKey, nativeVirtualKeyCode: virtualKey, modifiers,
      ...(key === 'Enter' ? { text: '\\r', unmodifiedText: '\\r' } : {})
    });
    await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', key, code, windowsVirtualKeyCode: virtualKey, modifiers });
  }
  await cdp.send('Emulation.setFocusEmulationEnabled', { enabled: true });
  if (isRegion) {
    const before = await evaluate(cdp, `(() => {
      const control = document.getElementById('temporal-preset');
      control.focus();
      return { value: control.value, count: control.options.length };
    })()`);
    await key('Home', 'Home', 36);
    await key('ArrowDown', 'ArrowDown', 40);
    const changed = await evaluate(cdp, `(() => {
      const control = document.getElementById('temporal-preset'), runtime = window.__ARTEMIS_GLOBE_SPIKE;
      return { focused: document.activeElement === control, value: control.value, expected: control.options[1].value, active: runtime.activeTemporalPresetId };
    })()`);
    if (!changed.focused || changed.value !== changed.expected || changed.active !== changed.value) throw new Error('Keyboard Region selector did not update canonical view');
    await key('Home', 'Home', 36);
    // Restore the incoming state; the owned three-period scenario runs separately.
    await evaluate(cdp, `(() => { const control = document.getElementById('temporal-preset'); control.value = ${JSON.stringify(before.value)}; control.dispatchEvent(new Event('change', { bubbles: true })); })()`);
    return { method: 'CDP keyboard input after explicit focus', control: 'temporal-preset', canonicalViewUpdated: true };
  }
  await evaluate(cdp, "document.getElementById('mode-range').focus()");
  await key('Tab', 'Tab', 9);
  const focused = await evaluate(cdp, "document.activeElement?.id");
  if (focused !== 'mode-scrub') throw new Error('Tab did not reach Scrub from Range');
  async function activate(id) {
    await key('Enter', 'Enter', 13);
    await evaluate(cdp, 'new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))', true);
    const expectedMode = id === 'mode-scrub' ? 'scrub' : 'range';
    const stateAndAriaAgree = () => evaluate(
      cdp,
      `window.__ARTEMIS_GLOBE_SPIKE.lifePathMode === '${expectedMode}' && document.getElementById('${id}').getAttribute('aria-pressed') === 'true'`
    );
    if (await stateAndAriaAgree()) return 'Enter';
    // Chromium headless does not synthesize button activation from Enter in every
    // CDP configuration; Space is the equivalent native button activation key.
    await key(' ', 'Space', 32);
    await evaluate(cdp, 'new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))', true);
    if (!(await stateAndAriaAgree())) throw new Error(`Keyboard activation did not activate ${id}`);
    return 'Space';
  }
  const firstActivation = await activate('mode-scrub');
  await key('Tab', 'Tab', 9, 8);
  if ((await evaluate(cdp, "document.activeElement?.id")) !== 'mode-range') throw new Error('Shift-Tab did not return to Range');
  const secondActivation = await activate('mode-range');
  return { method: 'CDP Tab/Shift-Tab plus native button activation', activationKeys: [firstActivation, secondActivation], controls: ['mode-range', 'mode-scrub'], stateAndAriaAgree: true };
}

async function verifyFirstUse(cdp, options) {
  const result = await evaluate(cdp, `(async () => {
    const r = window.__ARTEMIS_GLOBE_SPIKE;
    const initial = r.selectedPresenceId;
    const life = r.data.lifePath;
    const original = JSON.stringify(life);
    const check = (ok, message) => { if (!ok) throw new Error('First-use: ' + message); };
    document.getElementById('language-en').click();
    check(document.getElementById('life-period-label').innerText === 'Life periods', 'life-period label');
    check(document.getElementById('documented-presence-label').innerText === 'Documented presences', 'Presence label');
    check(document.querySelectorAll('#macro-periods button').length === 6, 'six coarse periods');
    check(document.querySelectorAll('#presence-sequence button').length === 11, 'eleven episodes');
    check(document.getElementById('active-mode-explanation').textContent === 'Within the selected interval', 'Range explanation');
    const checked = [];
    for (const p of life.presences) {
      r.selectPresence(p.presence_id, {openDetails: true});
      const card = document.getElementById('selection-card');
      const period = life.macro_periods.find(x => x.presence_refs.includes(p.presence_id))
        || life.macro_periods.find(x => x.axis_start_index <= p.axis_start_index && x.axis_end_index >= p.axis_end_index);
      check(card.dataset.presenceId === p.presence_id, 'detail identity');
      check(document.querySelector('#presence-sequence button[aria-pressed="true"]').dataset.presenceId === p.presence_id, 'row identity');
      check(document.querySelector('#macro-periods button[aria-current="true"]').dataset.periodId === period.period_id, 'containing period');
      const periodBounds = document.querySelector('#macro-periods button[aria-current="true"]').getBoundingClientRect();
      const periodRow = document.getElementById('macro-periods').getBoundingClientRect();
      check(periodBounds.right > periodRow.left && periodBounds.left < periodRow.right, 'containing period visible in scrolling row');
      check(r.placeMarkers.get(p.place_ref).getElement().getAttribute('aria-pressed') === 'true', 'map anchor');
      check(new URLSearchParams(location.search).get('presence') === p.presence_id, 'URL identity');
      const top = [...card.children].slice(0, 5);
      check(top[0].textContent === p.place_label && top[1].className === 'stop-card-date', 'Place then source-native time');
      check(top[2].textContent === 'Documented presence' && top[3].textContent.includes(p.short_description), 'record/context');
      check(top[4].textContent.includes('Exact historical positionUnknown') && top[4].textContent.includes('RouteUnknown'), 'explicit spatial/route limits');
      check(top[4].textContent.includes(p.duration_status === 'range_not_continuous_position' ? 'Residence range; daily presence not established' : 'Not established'), 'duration limit');
      check(top.every(el => el.getBoundingClientRect().bottom <= document.getElementById('inspector').getBoundingClientRect().bottom), 'first-open limits inside drawer viewport: ' + JSON.stringify({presence:p.presence_id, viewport:{width:innerWidth,height:innerHeight}, inspector:document.getElementById('inspector').getBoundingClientRect().toJSON(), primary:top.map(el=>({className:el.className,text:el.textContent.slice(0,100),rect:el.getBoundingClientRect().toJSON()}))}));
      check(![...card.querySelectorAll('summary')].some(s => /Reviewed package|Material uncertainty|Coverage.*corpus/.test(s.textContent)), 'primary vocabulary');
      const global = document.getElementById('presence-prototype-coverage');
      check(!card.contains(global) && !global.querySelector('details').open && !document.getElementById('prototype-details').open, 'collapsed global coverage outside selected evidence');
      const record = r.knowledgeByItem.get(p.event_item_id) || p;
      const sources = card.querySelector('.presence-sources');
      check(!sources.open && sources.querySelector('summary').textContent === 'Sources supporting this presence · ' + record.sources.length, 'direct counted source disclosure');
      sources.open = true;
      for (const source of record.sources) check(sources.textContent.includes(source.title), 'existing source title');
      for (const evidence of record.evidence_links) check([...sources.querySelectorAll('code')].some(c => c.textContent === evidence.locator), 'existing locator');
      for (const link of sources.querySelectorAll('a')) {
        const luminance = color => color.match(/[0-9.]+/g).slice(0, 3).map(Number).map(v => {
          v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
        }).reduce((sum, v, i) => sum + v * [0.2126, 0.7152, 0.0722][i], 0);
        const text = luminance(getComputedStyle(link).color);
        const background = luminance(getComputedStyle(link.closest('.evidence-group')).backgroundColor);
        check((Math.max(text, background) + 0.05) / (Math.min(text, background) + 0.05) >= 4.5, 'source link contrast');
      }
      const why = sources.querySelector('.source-scope');
      check(why.textContent.includes('These sources are linked to this displayed record.')
        && why.textContent.includes('does not mean the historical claims have been verified')
        && why.textContent.includes('See “Claims & evidence”'), 'status-neutral source inclusion');
      check(why.textContent.includes('Other historical sources may exist; this list is not exhaustive.'), 'non-exhaustiveness');
      check(why.textContent.includes('does not assign source reliability or credibility scores'), 'no source scoring');
      const links = (await r.map.getSource('life-path-chronology').getData()).features;
      const active = links.filter(f => f.properties.emphasis > 0);
      const arrival = life.transitions.find(t => t.to_presence_ref === p.presence_id);
      check(active.length === 1 && active[0].properties.transition_id === (arrival || life.transitions[0]).transition_id, 'one episode-specific transition');
      check(links.every(f => f.properties.route_geometry === null && f.properties.is_historical_route_geometry === false), 'null historical routes');
      checked.push({presence: p.presence_id, place: p.place_ref, sources: record.sources.length, transition: active[0].properties.transition_id});
    }
    check(JSON.stringify(life) === original, 'source/domain data unchanged');
    r.selectPresence(initial, {openDetails: true});
    return {episodes: checked, initial, domainDataUnchanged: true, visualAcceptance: 'not_assessed'};
  })()`, true);
  async function capture(suffix) {
    await evaluate(cdp, 'new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))', true);
    const screenshot = options.screenshot.replace(/\.png$/, '-' + suffix + '.png');
    const dom = options.dom.replace(/\.html$/, '-' + suffix + '.html');
    const png = await cdp.send('Page.captureScreenshot', {format: 'png', fromSurface: true, captureBeyondViewport: false});
    await writeFile(screenshot, Buffer.from(png.data, 'base64'));
    await writeFile(dom, await evaluate(cdp, 'document.documentElement.outerHTML'), 'utf8');
    return {screenshot, dom, screenshotSha256: createHash('sha256').update(await readFile(screenshot)).digest('hex')};
  }
  const details = await capture('details');
  // Native keyboard disclosure activation, followed by source/locator capture.
  // The diagnostic loop above can leave its last record's Sources open when
  // there was no initial selection to restore. Establish the closed precondition
  // with keyboard input too; otherwise a working Space toggle looks like failure.
  await cdp.send('Emulation.setFocusEmulationEnabled', {enabled: true});
  await evaluate(cdp, "document.querySelector('.presence-sources > summary').focus()");
  await evaluate(cdp, 'new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))', true);
  if (!await evaluate(cdp, "document.hasFocus() && document.activeElement === document.querySelector('.presence-sources > summary')")) throw new Error('Sources summary did not receive keyboard focus');
  const sourcesInitiallyOpen = await evaluate(cdp, "document.querySelector('.presence-sources').open");
  async function toggleSourcesWithKeyboard() {
    await cdp.send('Input.dispatchKeyEvent', {type: 'keyDown', key: ' ', code: 'Space', windowsVirtualKeyCode: 32});
    await cdp.send('Input.dispatchKeyEvent', {type: 'keyUp', key: ' ', code: 'Space', windowsVirtualKeyCode: 32});
    await evaluate(cdp, 'new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))', true);
  }
  if (sourcesInitiallyOpen) {
    await toggleSourcesWithKeyboard();
    if (await evaluate(cdp, "document.querySelector('.presence-sources').open")) throw new Error('Sources did not close with keyboard');
  }
  await toggleSourcesWithKeyboard();
  if (!await evaluate(cdp, "document.querySelector('.presence-sources').open")) throw new Error('Sources not reachable by keyboard');
  const sources = await capture('sources');
  await evaluate(cdp, `(() => {
    const why = document.querySelector('.source-scope'); why.open = true;
    why.scrollIntoView({block: 'center'});
  })()`);
  const sourceScope = await capture('why-sources');
  const localized = await evaluate(cdp, `(() => {
    document.getElementById('language-ru').click();
    const card = document.getElementById('selection-card');
    const why = card.querySelector('.source-scope'); why.open = true;
    window.ARTEMIS_I18N.refresh();
    if (!why.textContent.includes('не исчерпывающий') || !why.textContent.includes('не присваивает')
      || !why.textContent.includes('Эти источники связаны с показанной записью.')
      || !why.textContent.includes('не означает, что исторические утверждения проверены')
      || !why.textContent.includes('«Утверждения и свидетельства»')) throw new Error('Russian source explanation lost');
    if (document.getElementById('life-period-label').innerText !== 'Периоды жизни' || document.getElementById('documented-presence-label').innerText !== 'Документированные присутствия') throw new Error('Russian row labels lost');
    if (!card.querySelector('.presence-sources > summary').innerText.startsWith('Источники, подтверждающие это присутствие')) throw new Error('Russian source heading lost');
    card.querySelector('.presence-sources').open = false;
    document.getElementById('inspector').scrollTop = 0;
    return true;
  })()`);
  const russian = await capture('details-ru');
  await evaluate(cdp, `(() => {
    document.getElementById('language-en').click();
    const coverage = document.querySelector('#presence-prototype-coverage details');
    coverage.open = true; coverage.scrollIntoView({block: 'center'});
  })()`);
  const coverage = await capture('coverage');
  await evaluate(cdp, `(() => {
    document.querySelector('#presence-prototype-coverage details').open = false;
    document.getElementById('language-en').click();
    document.getElementById('mode-scrub').click();
    if (document.getElementById('active-mode-explanation').textContent !== 'From the beginning to the current time') throw new Error('Scrub explanation lost');
    document.getElementById('mode-range').click();
    window.__ARTEMIS_GLOBE_SPIKE.selectPresence(${JSON.stringify(result.initial)});
  })()`);
  return {...result, localized, keyboardSourceDisclosure: true,
    keyboardSourceDisclosureMethod: 'Native Space activation after explicit summary focus; not full keyboard navigation',
    sourcesInitiallyOpen, captures: {details, sources, sourceScope, russian, coverage}};
}

async function verifySourceAwareResearch(cdp, options, deadline) {
  // This task uses browser input. Runtime reads below diagnose identity and data
  // preservation; they never select an episode or change temporal state.
  const bindings = [
    ['presence-rimini-1502-08-08', 'claim-rimini-presence-1502-08-08', 'source-uniurb-volpe-chronology', '78r'],
    ['presence-cesena-1502-08-10', 'claim-cesena-presence-1502-08-10', 'source-uniurb-volpe-chronology', '46v'],
    ['presence-cesenatico-1502-09-06', 'claim-cesenatico-presence-1502-09-06', 'source-uniurb-volpe-chronology', '66v'],
    ['presence-imola-autumn-1502', 'claim-imola-map-work-autumn-1502', 'source-rct-imola-map', '912284'],
  ];
  const rangeIds = bindings.map(row => row[0]);
  const scrubIds = [
    'presence-leonardo-vinci-birth-1452',
    'presence-leonardo-florence-st-luke-1472',
    'presence-leonardo-milan-altarpiece-contract-1483',
    ...rangeIds,
  ];
  const captures = [];
  const original = await evaluate(cdp, 'JSON.stringify(window.__ARTEMIS_GLOBE_SPIKE.data.lifePath)');
  const check = (ok, message) => { if (!ok) throw new Error('Source-aware task: ' + message); };
  async function settle() {
    await evaluate(cdp, 'new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))', true);
  }
  async function click(selector) {
    await evaluate(cdp, `document.querySelector(${JSON.stringify(selector)})?.scrollIntoView({block: 'nearest', inline: 'nearest'})`);
    await settle();
    const point = await evaluate(cdp, `(() => {
      const node = document.querySelector(${JSON.stringify(selector)});
      if (!node) throw new Error('Missing control: ' + ${JSON.stringify(selector)});
      const box = node.getBoundingClientRect(), x = box.x + box.width / 2, y = box.y + box.height / 2;
      if (!box.width || !box.height || !node.contains(document.elementFromPoint(x, y))) throw new Error('Obstructed control: ' + ${JSON.stringify(selector)});
      return {x, y};
    })()`);
    await cdp.send('Input.dispatchMouseEvent', {type: 'mousePressed', button: 'left', clickCount: 1, ...point});
    await cdp.send('Input.dispatchMouseEvent', {type: 'mouseReleased', button: 'left', clickCount: 1, ...point});
    await settle();
  }
  async function key(key, code, virtualKey) {
    await cdp.send('Input.dispatchKeyEvent', {type: 'keyDown', key, code, windowsVirtualKeyCode: virtualKey});
    await cdp.send('Input.dispatchKeyEvent', {type: 'keyUp', key, code, windowsVirtualKeyCode: virtualKey});
  }
  async function slider(id, year) {
    const state = await evaluate(cdp, `(() => {
      const input = document.getElementById(${JSON.stringify(id)});
      input.focus();
      return {min: Number(input.min), max: Number(input.max), target: window.__ARTEMIS_GLOBE_SPIKE.data.lifePath.time_axis.values.indexOf(${JSON.stringify(year)})};
    })()`);
    check(state.target >= state.min && state.target <= state.max, 'calendar year outside slider');
    const fromEnd = state.max - state.target < state.target - state.min;
    await key(fromEnd ? 'End' : 'Home', fromEnd ? 'End' : 'Home', fromEnd ? 35 : 36);
    for (let i = 0; i < (fromEnd ? state.max - state.target : state.target - state.min); i++) {
      await key(fromEnd ? 'ArrowLeft' : 'ArrowRight', fromEnd ? 'ArrowLeft' : 'ArrowRight', fromEnd ? 37 : 39);
    }
    await settle();
    check(await evaluate(cdp, `document.getElementById(${JSON.stringify(id)}).getAttribute('aria-valuetext') === ${JSON.stringify(year)}`), 'native keyboard slider year');
  }
  async function state() {
    return evaluate(cdp, `(() => {
      const r = window.__ARTEMIS_GLOBE_SPIKE;
      return {mode: r.lifePathMode, start: r.data.lifePath.time_axis.values[r.lifePathStartIndex],
        end: r.data.lifePath.time_axis.values[r.lifePathEndIndex], selected: r.selectedPresenceId,
        visible: [...document.querySelectorAll('#presence-sequence button')].filter(b => !b.hidden).map(b => b.dataset.presenceId),
        places: [...document.querySelectorAll('.life-path-marker')].filter(b => !b.hidden).map(b => b.dataset.placeId),
        count: Number(document.documentElement.dataset.artemisVisiblePresenceCount), url: location.href};
    })()`);
  }
  async function membership(expected, mode, start, end) {
    const current = await state();
    check(JSON.stringify([...current.visible].sort()) === JSON.stringify([...expected].sort()), 'exact Presence membership');
    check(current.count === expected.length && current.places.length === expected.length, 'Presence/Place counts');
    check(current.mode === mode && current.start === start && current.end === end, 'temporal controls/state agree');
    return current;
  }
  async function capture(suffix) {
    const screenshot = options.screenshot.replace(/\.png$/, '-source-aware-' + suffix + '.png');
    const dom = options.dom.replace(/\.html$/, '-source-aware-' + suffix + '.html');
    const image = await cdp.send('Page.captureScreenshot', {format: 'png', fromSurface: true, captureBeyondViewport: false});
    await writeFile(screenshot, Buffer.from(image.data, 'base64'));
    await writeFile(dom, await evaluate(cdp, 'document.documentElement.outerHTML'));
    captures.push({screenshot, dom, screenshotSha256: createHash('sha256').update(await readFile(screenshot)).digest('hex')});
  }
  async function reload(expected) {
    await evaluate(cdp, "document.documentElement.dataset.artemisSourceAwareReload = 'before'");
    await cdp.send('Page.reload', {ignoreCache: false});
    while (Date.now() < deadline) {
      if (await evaluate(cdp, "document.documentElement?.dataset.artemisSourceAwareReload !== 'before'").catch(() => false)) break;
      await delay(100);
    }
    await waitForVisualReadiness(cdp, deadline);
    const restored = await membership(expected.visible, expected.mode, expected.start, expected.end);
    check(restored.selected === expected.selected, 'selected stable identity survives URL reload');
    return restored;
  }

  await click('#language-en');
  if (await evaluate(cdp, "!document.getElementById('inspector').hidden")) await click('#close-details');
  await click('#mode-range');
  await slider('range-start', '1502');
  await slider('range-end', '1502');
  await membership(rangeIds, 'range', '1502', '1502');
  const records = [];
  for (const [presenceId, claimId, sourceId, locatorFragment] of bindings) {
    const camera = await evaluate(cdp, 'JSON.stringify({center: window.__ARTEMIS_GLOBE_SPIKE.map.getCenter(), zoom: window.__ARTEMIS_GLOBE_SPIKE.map.getZoom()})');
    await click('#presence-sequence button[data-presence-id="' + presenceId + '"]');
    check(await evaluate(cdp, `window.__ARTEMIS_GLOBE_SPIKE.popupPresenceId === ${JSON.stringify(presenceId)} && document.getElementById('inspector').hidden`), 'single selection opens correct compact popup');
    check(await evaluate(cdp, 'JSON.stringify({center: window.__ARTEMIS_GLOBE_SPIKE.map.getCenter(), zoom: window.__ARTEMIS_GLOBE_SPIKE.map.getZoom()})') === camera, 'single click must not move camera');
    await click('.popup-details');
    check(await evaluate(cdp, `document.getElementById('selection-card').dataset.presenceId === ${JSON.stringify(presenceId)} && !document.getElementById('inspector').hidden && !document.querySelector('.presence-popup-card')`), 'correct drawer replaces popup');
    await click('.presence-sources > summary');
    const record = await evaluate(cdp, `(() => {
      const r = window.__ARTEMIS_GLOBE_SPIKE, p = r.data.lifePath.presences.find(p => p.presence_id === ${JSON.stringify(presenceId)});
      const record = r.knowledgeByItem.get(p.event_item_id), claim = record.claims.find(c => c.id === ${JSON.stringify(claimId)});
      const evidence = record.evidence_links.find(e => e.claim_id === claim?.id && e.source_id === ${JSON.stringify(sourceId)} && e.locator.includes(${JSON.stringify(locatorFragment)}));
      const source = record.sources.find(s => s.id === evidence?.source_id), sources = document.querySelector('.presence-sources');
      if (!claim || !evidence || !source || !sources.open) throw new Error('Claim/source binding missing');
      if (![...sources.querySelectorAll('code')].some(c => c.textContent === evidence.locator)) throw new Error('Visible source disclosure lost exact locator');
      const href = source.artifact_uri || source.uri || source.url;
      if (![...sources.querySelectorAll('a')].some(a => a.href === href)) throw new Error('Source URL missing');
      return {presenceId: p.presence_id, claimId: claim.id, sourceId: source.id, locator: evidence.locator,
        sourceUrl: href, reviewState: claim.review_state, evidenceState: claim.evidence_state,
        confidence: claim.confidence, evidenceReviewState: evidence.review_state};
    })()`);
    check(record.reviewState === 'draft' && record.evidenceState === 'missing' && record.confidence === 'unknown' && record.evidenceReviewState === 'draft', 'historical source status must stay unpromoted');
    await click('#selection-card > .knowledge-details > summary');
    await click('#selection-card > .knowledge-details .knowledge-details-body > .knowledge-disclosure > summary');
    record.disclosedClaims = await evaluate(cdp, `(() => {
      const r = window.__ARTEMIS_GLOBE_SPIKE, p = r.data.lifePath.presences.find(p => p.presence_id === ${JSON.stringify(presenceId)});
      const record = r.knowledgeByItem.get(p.event_item_id);
      return record.claims.map(claim => {
        const group = [...document.querySelectorAll('#selection-card .evidence-group')].find(g => g.querySelector('.record-id')?.textContent === claim.id);
        const meta = group?.querySelector('.record-meta');
        const expected = claim.review_state + ' · confidence ' + claim.confidence + ' · evidence ' + claim.evidence_state;
        if (!meta?.checkVisibility() || meta.innerText !== expected) throw new Error('Recorded Claim status not disclosed: ' + claim.id);
        for (const link of record.evidence_links.filter(e => e.claim_id === claim.id)) {
          const row = [...group.querySelectorAll('.evidence-row')].find(e => [...e.querySelectorAll('code')].some(c => c.textContent === link.locator));
          if (!row || !row.innerText.includes(link.relation_to_claim + ' · ' + link.evidence_strength + ' · ' + link.review_state)) throw new Error('Evidence relation/status not disclosed');
        }
        return {claimId: claim.id, reviewState: claim.review_state, confidence: claim.confidence, evidenceState: claim.evidence_state};
      });
    })()`);
    if (presenceId === rangeIds[1]) {
      check(record.disclosedClaims.some(c => c.claimId === 'claim-cesena-survey-folios-9r-10r'
        && c.reviewState === 'rejected' && c.confidence === 'low' && c.evidenceState === 'missing'), 'Cesena folios 9r–10r rejection must remain distinct');
      await evaluate(cdp, `([...document.querySelectorAll('#selection-card .evidence-group')].find(g => g.querySelector('.record-id')?.textContent === 'claim-cesena-survey-folios-9r-10r')).querySelector('.record-meta').scrollIntoView({block: 'center'})`);
      await settle();
      await capture('cesena-claim-status');
    }
    records.push(record);
    if (presenceId === rangeIds[0]) {
      await click('.source-scope > summary');
      await capture('source-status-en');
      for (const lang of ['en', 'ru']) {
        await click('#language-' + lang);
        const status = await evaluate(cdp, `(() => {
          const card = document.getElementById('selection-card'), why = card.querySelector('.source-scope');
          const claim = [...card.querySelectorAll('.evidence-group')].find(g => g.querySelector('.record-id')?.textContent === ${JSON.stringify(claimId)});
          const meta = claim?.querySelector('.record-meta');
          if (!meta || !meta.checkVisibility()) throw new Error('Claim status not visibly disclosed');
          return {copy: why.innerText, status: meta.innerText};
        })()`);
        check(status.status === 'draft · confidence unknown · evidence missing', 'native Claim status visible in both locales');
        check(status.copy.includes(lang === 'en' ? 'These sources are linked to this displayed record.' : 'Эти источники связаны с показанной записью.'), 'neutral source binding in both locales');
        check(status.copy.includes(lang === 'en' ? 'See “Claims & evidence”' : '«Утверждения и свидетельства»'), 'status disclosure pointer');
        check(!status.copy.includes('current reviewed evidence') && !status.copy.includes('текущие проверенные свидетельства'), 'no unconditional reviewed-evidence promotion');
        if (lang === 'ru') await capture('source-status-ru');
      }
      await click('#language-en');
    }
    await click('#close-details');
  }
  // Exercise source access with keyboard on the same normal sequence selection.
  await click('#presence-sequence button[data-presence-id="' + rangeIds[0] + '"]');
  const rangeRestored = await reload(await membership(rangeIds, 'range', '1502', '1502'));
  await click('.popup-details');
  await evaluate(cdp, "document.querySelector('.presence-sources > summary').focus()");
  await key(' ', 'Space', 32);
  await settle();
  check(await evaluate(cdp, "document.querySelector('.presence-sources').open"), 'native keyboard source disclosure');
  await evaluate(cdp, "document.querySelector('#selection-card > .knowledge-disclosure:not(.presence-sources) > summary').focus()");
  await key(' ', 'Space', 32);
  await settle();
  check(await evaluate(cdp, `(() => {
    const section = document.querySelector('#selection-card > .knowledge-disclosure:not(.presence-sources)');
    return section.open && [...section.querySelectorAll('.uncertainty-card')].some(node => node.checkVisibility() && node.innerText.trim());
  })()`), 'native keyboard uncertainty disclosure');
  await capture('range-keyboard');
  await click('#close-details');
  await click('#mode-scrub');
  await slider('scrub-current', '1502');
  await membership(scrubIds, 'scrub', '1452', '1502');
  await click('#presence-sequence button[data-presence-id="' + rangeIds[2] + '"]');
  const scrubRestored = await reload(await membership(scrubIds, 'scrub', '1452', '1502'));
  await capture('scrub-restored');
  await click('#mode-range');
  await slider('range-start', '1501');
  await slider('range-end', '1501');
  const empty = await membership([], 'range', '1501', '1501');
  check(await evaluate(cdp, "document.getElementById('selection-card').textContent.includes('No documented presence overlaps this calendar window.')"), 'corpus-qualified empty state');
  check(empty.selected === null, 'empty corpus window clears selected Presence');
  await capture('empty-corpus');
  check(await evaluate(cdp, 'JSON.stringify(window.__ARTEMIS_GLOBE_SPIKE.data.lifePath)') === original, 'frozen presentation input unchanged');
  return {outcome: 'TECHNICAL_TASK_PASS', method: 'CDP mouse and native keyboard input; runtime reads for diagnostics only',
    records, rangeRestored, scrubRestored, empty, keyboardSourceDisclosure: true, keyboardUncertaintyDisclosure: true,
    domainDataUnchanged: true, captures,
    limitations: ['Source URLs and locators verified against the existing package; remote source reachability and historical evidence were not revalidated.', 'Automated technical task evidence, not human comprehension or user-value validation.']};
}

async function verifySharedPreviewNavigation(cdp, options, deadline) {
  const base = new URL('../', options.url);
  const routes = {leonardo: new URL('globe/', base), region: new URL('region/', base)};
  const captures = [], transitions = [], restorations = [], sourceAccess = [], defaults = {};
  const check = (ok, message) => { if (!ok) throw new Error('Example navigation: ' + message); };
  async function settle() {
    await evaluate(cdp, 'new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))', true);
  }
  async function key(key, code, virtualKey) {
    await cdp.send('Input.dispatchKeyEvent', {type: 'keyDown', key, code, windowsVirtualKeyCode: virtualKey,
      ...(key === 'Enter' ? {text: '\r', unmodifiedText: '\r'} : {})});
    await cdp.send('Input.dispatchKeyEvent', {type: 'keyUp', key, code, windowsVirtualKeyCode: virtualKey});
  }
  async function waitNavigation(previousToken, path) {
    let arrived = false;
    while (Date.now() < deadline) {
      arrived = await evaluate(cdp, `location.pathname === ${JSON.stringify(path)} && document.documentElement?.dataset.navigationProbeToken !== ${JSON.stringify(previousToken)}`).catch(() => false);
      if (arrived) break;
      await delay(100);
    }
    check(arrived, 'document navigation did not reach ' + path);
    await waitForVisualReadiness(cdp, deadline);
    await cdp.send('Emulation.setFocusEmulationEnabled', {enabled: true});
  }
  async function mark() {
    const token = String(Date.now()) + '-' + Math.random();
    // A diagnostic document token only; never supplies temporal/selection state.
    await evaluate(cdp, `document.documentElement.dataset.navigationProbeToken = ${JSON.stringify(token)}`);
    return token;
  }
  async function navigate(url) {
    const token = await mark();
    await cdp.send('Page.navigate', {url: String(url)});
    await waitNavigation(token, new URL(url).pathname);
  }
  async function input(selector, keyboard = false, navigates = false) {
    await evaluate(cdp, `document.querySelector(${JSON.stringify(selector)})?.scrollIntoView({block: 'nearest', inline: 'nearest'})`);
    await settle();
    const point = await evaluate(cdp, `(() => {
      const node = document.querySelector(${JSON.stringify(selector)});
      if (!node) throw new Error('Missing control: ' + ${JSON.stringify(selector)});
      const box = node.getBoundingClientRect(), x = box.x + box.width / 2, y = box.y + box.height / 2;
      if (!box.width || !box.height || !node.contains(document.elementFromPoint(x,y))) throw new Error('Obstructed control: ' + ${JSON.stringify(selector)});
      node.focus({preventScroll:true});
      if (document.activeElement !== node) throw new Error('Control did not receive focus');
      return {x,y,href:node.href || null};
    })()`);
    const token = navigates ? await mark() : null;
    if (keyboard) await key('Enter','Enter',13);
    else {
      await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,x:point.x,y:point.y});
      await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,x:point.x,y:point.y});
    }
    if (navigates) await waitNavigation(token,new URL(point.href).pathname);
    else await settle();
    return {method: keyboard ? 'native Enter after explicit focus' : 'native mouse input', href:point.href};
  }
  async function semantic() {
    return evaluate(cdp, `(() => {
      const r = window.__ARTEMIS_GLOBE_SPIKE;
      return {lifePathAvailable:r.data.lifePath.available, mode:r.lifePathMode,
        start:r.data.lifePath.time_axis?.values[r.lifePathStartIndex] ?? null,
        end:r.data.lifePath.time_axis?.values[r.lifePathEndIndex] ?? null,
        preset:r.activeTemporalPresetId, layers:[...r.activeLayerRefs].sort(),
        presence:r.selectedPresenceId, item:r.selectedItemId, temporal:r.data.state.temporal_selection};
    })()`);
  }
  async function inspect(dataset,lang,suffix) {
    const result = await evaluate(cdp, `(() => {
      const dataset=${JSON.stringify(dataset)}, lang=${JSON.stringify(lang)};
      const names = lang === 'ru' ? {leonardo:'Леонардо · 1452–1519',region:'Римская империя · 91–116 н. э.'} : {leonardo:'Leonardo · 1452–1519',region:'Roman Empire · 91–116 CE'};
      const status=lang === 'ru' ? 'Публичный исследовательский прототип · продуктовая ценность не подтверждена' : 'Public research prototype · not a validated product';
      const coverage=dataset === 'leonardo' ? (lang === 'ru' ? '11 выбранных эпизодов присутствия · 1452–1519' : '11 selected presence episodes · 1452–1519') : (lang === 'ru' ? '3 реконструированных периода · 91–116 н. э.' : '3 reconstructed periods · 91–116 CE');
      const nav=document.getElementById('research-examples');
      if (!nav || nav.getAttribute('aria-label') !== (lang === 'ru' ? 'Исследовательские примеры' : 'Research examples')) throw new Error('Navigation accessible name');
      const current=document.getElementById('example-'+dataset), other=document.getElementById('example-'+(dataset === 'region' ? 'leonardo' : 'region'));
      if (current?.getAttribute('aria-current') !== 'page' || current.tagName !== 'SPAN' || current.innerText !== names[dataset]) throw new Error('Current example indication');
      if (other?.tagName !== 'A' || other.innerText !== names[dataset === 'region' ? 'leonardo' : 'region']) throw new Error('Sibling native link');
      const sibling=new URL(other.href);
      if ([...sibling.searchParams.keys()].sort().join(',') !== 'lang,view' || sibling.searchParams.get('lang') !== lang || sibling.searchParams.get('view') !== window.__ARTEMIS_GLOBE_SPIKE.presentationView || sibling.hash) throw new Error('Foreign state in sibling link');
      const atlas=document.getElementById('atlas-compatibility-link'), atlasUrl=new URL(atlas.href);
      if (atlasUrl.pathname !== ${JSON.stringify(new URL('atlas/',base).pathname)} || atlasUrl.search || atlasUrl.hash || !atlas.innerText.includes(lang === 'ru' ? 'режим совместимости' : 'compatibility')) throw new Error('Atlas compatibility boundary');
      if (!document.getElementById('example-coverage')?.innerText.includes(coverage) || !document.body.innerText.includes(status)) throw new Error('Visible coverage/status');
      if (document.getElementById('language-'+lang).getAttribute('aria-pressed') !== 'true' || document.getElementById('language-'+(lang === 'en' ? 'ru' : 'en')).getAttribute('aria-pressed') !== 'false') throw new Error('Language pressed state');
      const visible=node => { if (!node?.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})) return false; const b=node.getBoundingClientRect(); return b.width>0 && b.height>0 && b.left>=0 && b.top>=0 && b.right<=innerWidth+1 && b.bottom<=innerHeight+1; };
      for (const node of [nav,current,other,atlas,document.getElementById('example-coverage')]) if (!visible(node)) throw new Error('Header information outside viewport');
      if (document.documentElement.scrollWidth > innerWidth+1) throw new Error('Horizontal overflow');
      const header=document.getElementById('spike-banner').getBoundingClientRect();
      for (const node of document.querySelectorAll('#timeline-dock, .maplibregl-ctrl-top-right, .maplibregl-ctrl-top-left')) {
        if (!visible(node)) continue;
        const b=node.getBoundingClientRect();
        if (Math.min(header.right,b.right)-Math.max(header.left,b.left)>1 && Math.min(header.bottom,b.bottom)-Math.max(header.top,b.top)>1) throw new Error('Header overlaps time/map controls');
      }
      if (dataset === 'region') {
        for (const id of ['region-reconstruction-note','region-provenance-link']) if (!visible(document.getElementById(id))) throw new Error('Region provenance obligation hidden');
        const detailsButton=document.getElementById('region-details');
        if (!visible(detailsButton) || detailsButton.disabled || detailsButton.getAttribute('aria-controls') !== 'inspector'
          || detailsButton.innerText !== (lang === 'ru' ? 'Сведения о регионе' : 'Region details')) throw new Error('Region evidence entry unavailable');
        if (!document.getElementById('region-reconstruction-note').innerText.includes('Approximate scholarly reconstruction') || !document.getElementById('region-provenance-link').innerText.includes('CC-BY-4.0')) throw new Error('Region limits/license lost');
        if (window.__ARTEMIS_GLOBE_SPIKE.data.lifePath.available !== false || document.getElementById('temporal-preset').options.length !== 3) throw new Error('Region dataset isolation');
      } else if (window.__ARTEMIS_GLOBE_SPIKE.data.lifePath.presences.length !== 11) throw new Error('Leonardo dataset isolation');
      return {dataset,locale:lang,url:location.href,sibling:other.href,atlas:atlas.href,current:current.innerText,coverage,status,viewport:{width:innerWidth,height:innerHeight},headerBottom:header.bottom};
    })()`);
    const screenshot=options.screenshot.replace(/\.png$/,'-navigation-'+suffix+'.png');
    const dom=options.dom.replace(/\.html$/,'-navigation-'+suffix+'.html');
    const image=await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});
    await writeFile(screenshot,Buffer.from(image.data,'base64'));
    await writeFile(dom,await evaluate(cdp,'document.documentElement.outerHTML'));
    captures.push({...result,screenshot,dom,screenshotSha256:createHash('sha256').update(await readFile(screenshot)).digest('hex')});
    return result;
  }
  async function assertDefault(dataset,lang) {
    check(JSON.stringify(await semantic()) === JSON.stringify(defaults[dataset]),dataset+' target did not start in its own default state');
    const url=new URL(await evaluate(cdp,'location.href'));
    const permitted=dataset === 'region' ? ['time','layers','item','lang','view'] : ['mode','start','end','presence','item','lang','view'];
    check([...url.searchParams.keys()].every(name=>permitted.includes(name)) && !url.hash,'foreign query/hash survived cross-example navigation');
    check(url.searchParams.get('lang') === lang,'target locale continuity');
  }
  async function reloadSaved(saved,expected) {
    // Back has already returned to this exact saved URL. Page.navigate to the
    // same URL containing a fragment can be a same-document navigation, which
    // cannot prove reconstruction from URL and retains the document token.
    // Leave the source document first, then explicitly reopen the exact saved
    // URL. A different dataset document prevents a fragment-only no-op.
    check(await evaluate(cdp,'location.href') === saved,'reopen is not starting from the captured saved URL');
    const opposite=new URL(saved).pathname === routes.leonardo.pathname ? routes.region : routes.leonardo;
    await navigate(opposite);
    await navigate(saved);
    check(JSON.stringify(await semantic()) === JSON.stringify(expected),'saved URL did not restore semantic time/selection');
  }
  async function back(saved,expected) {
    const history=await cdp.send('Page.getNavigationHistory');
    const target=history.entries[history.currentIndex-1];
    check(target?.url === saved,'native browser history lost saved source URL');
    const token=await mark();
    await cdp.send('Page.navigateToHistoryEntry',{entryId:target.id});
    await waitNavigation(token,new URL(saved).pathname);
    check(JSON.stringify(await semantic()) === JSON.stringify(expected),'Back did not restore semantic time/selection');
  }
  async function disclosures(dataset) {
    // Reopening a selected saved URL establishes the selection; native Space is
    // the only operation that opens disclosures in this keyboard evidence.
    if (dataset === 'leonardo') {
      const presence = await evaluate(cdp, 'window.__ARTEMIS_GLOBE_SPIKE.selectedPresenceId');
      await input('#presence-sequence button[data-presence-id="' + presence + '"]', true);
      await input('.popup-details', true);
    } else {
      const before = await semantic(), url = await evaluate(cdp, 'location.href');
      await input('#region-details', true);
      check(await evaluate(cdp, "!document.getElementById('inspector').hidden && document.getElementById('region-details').getAttribute('aria-expanded') === 'true'"), 'Region details did not open with native input');
      check(JSON.stringify(before) === JSON.stringify(await semantic()) && url === await evaluate(cdp, 'location.href'), 'Opening Region details changed selection/time/URL');
    }
    const selectors=await evaluate(cdp,`(() => {
      const card=document.getElementById('selection-card');
      return [...card.querySelectorAll('details')].map((d,i)=>({index:i,hasSource:!!d.querySelector('a'),uncertainty:!!d.querySelector('.uncertainty-card')})).filter(d=>d.hasSource||d.uncertainty);
    })()`);
    check(selectors.some(d=>d.hasSource) && selectors.some(d=>d.uncertainty),'source/uncertainty disclosures missing');
    const results=[];
    for (const entry of selectors) {
      await evaluate(cdp,`(() => {
        const summary=document.querySelectorAll('#selection-card details')[${entry.index}].querySelector('summary');
        summary.scrollIntoView({block:'nearest'});summary.focus({preventScroll:true});
        if(document.activeElement!==summary)throw new Error('Disclosure focus failed: '+JSON.stringify({
          dataset:${JSON.stringify(dataset)},index:${entry.index},summary:summary.textContent,
          inspectorHidden:document.getElementById('inspector').hidden,
          visible:summary.checkVisibility({checkVisibilityCSS:true}),
          focused:document.activeElement?.outerHTML?.slice(0,300),
          parents:[...function*(){for(let p=summary.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')yield {label:p.querySelector('summary')?.textContent,open:p.open};}()]
        }));
      })()`);
      await settle();
      const open=await evaluate(cdp,`document.querySelectorAll('#selection-card details')[${entry.index}].open`);
      if (!open) {await key(' ','Space',32);await settle();}
      check(await evaluate(cdp,`document.querySelectorAll('#selection-card details')[${entry.index}].open`),'native Space did not open disclosure');
      results.push(entry);
    }
    const accessible=await evaluate(cdp,`(() => {const card=document.getElementById('selection-card');const link=[...card.querySelectorAll('a')].find(a=>a.checkVisibility({checkVisibilityCSS:true}));if(!link)throw new Error('No disclosed source link');link.scrollIntoView({block:'nearest'});link.focus({preventScroll:true});if(document.activeElement!==link)throw new Error('Source link cannot receive keyboard focus');return {href:link.href,text:link.textContent};})()`);
    return {dataset,method:'native Space after explicit summary focus; source link focus',disclosures:results,source:accessible};
  }
  async function closeRegionDetails(escape = false) {
    const before=await semantic(), url=await evaluate(cdp,'location.href');
    if (escape) {await key('Escape','Escape',27);await settle();}
    else await input('#close-details',true);
    check(await evaluate(cdp,"document.getElementById('inspector').hidden && document.getElementById('region-details').getAttribute('aria-expanded') === 'false' && document.activeElement === document.getElementById('region-details')"),'Region details close did not restore entry focus');
    check(JSON.stringify(before)===JSON.stringify(await semantic())&&url===await evaluate(cdp,'location.href'),'Closing Region details changed selection/time/URL');
    return {method:escape?'native Escape':'native Enter on close button',focusRestored:true,semanticStatePreserved:true};
  }
  // Capture actual clean defaults rather than invent a cross-dataset timeline.
  for (const dataset of ['leonardo','region']) {
    await navigate(routes[dataset]);
    defaults[dataset]=await semantic();
    await inspect(dataset,'en',dataset+'-missing-locale');
  }
  for (const lang of ['en','ru']) {
    await navigate(new URL('?lang='+lang,routes.leonardo));
    await inspect('leonardo',lang,'leonardo-'+lang);
    const outward=await input('#example-region',lang==='ru',true);
    await assertDefault('region',lang);
    await inspect('region',lang,'region-'+lang);
    sourceAccess.push({locale:lang,...await disclosures('region')});
    await inspect('region',lang,'region-sources-'+lang);
    const close=await closeRegionDetails(lang==='ru');
    const inward=await input('#example-leonardo',true,true);
    await assertDefault('leonardo',lang);
    transitions.push({locale:lang,outward,inward,defaultsIsolated:true,regionDetailsClose:close});
  }
  // URL containing valid semantic state plus intentionally unrelated parameters.
  const savedLeonardo=new URL('?mode=range&start=1502&end=1502&presence=presence-rimini-1502-08-08&lang=en&camera=foreign&diagnostic=foreign&unknown=foreign#foreign',routes.leonardo);
  await navigate(savedLeonardo);
  const before=await semantic(), beforeUrl=await evaluate(cdp,'location.href');
  await input('#language-ru',true);
  const saved=await evaluate(cdp,'location.href'), expected=await semantic();
  const previous=new URL(beforeUrl), localized=new URL(saved);previous.searchParams.delete('lang');localized.searchParams.delete('lang');
  check(previous.href===localized.href && JSON.stringify(before)===JSON.stringify(expected),'locale change changed source semantics/query/hash');
  check(new URL(saved).searchParams.get('lang')==='ru','language button did not write locale');
  await input('#example-region',true,true);await assertDefault('region','ru');
  await back(saved,expected);await reloadSaved(saved,expected);
  restorations.push({dataset:'leonardo',saved,semantic:expected,back:true,reopen:true,sourceDisclosures:await disclosures('leonardo')});
  await inspect('leonardo','ru','leonardo-sources-ru');
  const englishSaved=new URL(saved);englishSaved.searchParams.set('lang','en');
  await navigate(englishSaved);
  sourceAccess.push({locale:'en',...await disclosures('leonardo')});
  await inspect('leonardo','en','leonardo-sources-en');
  // A non-default Region period and selected Region item; values come from its
  // own existing view index, then the saved URL is applied by normal navigation.
  await navigate(new URL('?lang=ru',routes.region));
  const regionChoice=await evaluate(cdp,`(() => {
    const r=window.__ARTEMIS_GLOBE_SPIKE,p=r.viewIndex.temporal_presets[1];
    // A preset has both empty-layer and political-territory views. Preserve the
    // dataset's active layers when choosing its non-default saved period.
    const layers=[...r.activeLayerRefs].sort();
    const v=[...r.viewByKey.values()].find(v=>v.temporal_preset_id===p.preset_id
      && JSON.stringify([...v.active_layer_refs].sort())===JSON.stringify(layers));
    const item=v?.projection.items.find(i=>i.object_type==='Region');
    if(!item)throw new Error('Non-default Region view has no Region item for current layers: '+JSON.stringify({preset:p.preset_id,layers}));
    return {preset:p.preset_id,layers:layers.join(','),item:item.item_id};
  })()`);
  const regionUrl=new URL(routes.region);for(const [k,v]of Object.entries({time:regionChoice.preset,layers:regionChoice.layers,item:regionChoice.item,lang:'ru'}))regionUrl.searchParams.set(k,v);
  await navigate(regionUrl);const regionSaved=await evaluate(cdp,'location.href'), regionState=await semantic();
  check(regionState.preset===regionChoice.preset&&regionState.item===regionChoice.item,'Region saved state was not selected');
  await input('#example-leonardo',true,true);await assertDefault('leonardo','ru');
  await back(regionSaved,regionState);await reloadSaved(regionSaved,regionState);
  restorations.push({dataset:'region',saved:regionSaved,semantic:regionState,back:true,reopen:true,sourceDisclosures:await disclosures('region')});
  await inspect('region','ru','region-saved-sources-ru');
  restorations.at(-1).detailsClose=await closeRegionDetails(true);
  for(const dataset of ['leonardo','region']) {
    await navigate(new URL('?lang=invalid&unknown=foreign#foreign',routes[dataset]));
    await inspect(dataset,'en',dataset+'-invalid-locale');
    const target=dataset==='region'?'leonardo':'region';await input('#example-'+target,true,true);await assertDefault(target,'en');
  }
  return {routes:Object.fromEntries(Object.entries(routes).map(([k,v])=>[k,v.href])),defaults,transitions,restorations,sourceAccess,captures,
    keyboardScope:'Named navigation/language controls and selected-record disclosures after explicit focus; not a full keyboard audit',
    valueValidation:'not_assessed'};
}

async function verifyProjectionSwitch(cdp, options, deadline) {
  // Native UI input drives this scenario. Runtime reads compare actual state;
  // no fixture substitution, test-hook mutation or synthetic renderer pass.
  const base = new URL('../', options.url);
  const routes = {leonardo: new URL('globe/', base), region: new URL('region/', base)};
  const captures = [], comparisons = [], histories = [], defaults = {}, picking = [], renderSettlements = [];
  const check = (ok, message) => { if (!ok) throw new Error('Projection switch: ' + message); };
  const hash = value => createHash('sha256').update(JSON.stringify(value)).digest('hex');
  async function settle() {
    await evaluate(cdp, 'new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))', true);
  }
  async function mapIdle(reason) {
    const timeoutMs=Math.min(20000,deadline-Date.now());
    check(timeoutMs>0,'render settlement exhausted the scenario deadline');
    const result=await evaluate(cdp, `(async () => {
      const r=window.__ARTEMIS_GLOBE_SPIKE,map=r.map;
      if(!map)throw new Error('Map unavailable before native render settlement');
      await new Promise((resolve,reject) => {
        const timeout=setTimeout(() => {map.off('idle',idle);reject(new Error('Native map idle timed out'));},${timeoutMs});
        function idle() {
          clearTimeout(timeout);
          // App-owned idle listeners reposition labels and chronology cues.
          // Two frames then include their resulting DOM/layout updates.
          requestAnimationFrame(() => requestAnimationFrame(resolve));
        }
        map.once('idle',idle);
        // This public repaint request guarantees a fresh native render/idle
        // event even if a fast map was already idle before this observer.
        // It supplies no semantic or UI state and skips no engine transition.
        map.triggerRepaint();
      });
      const result={loaded:map.loaded(),moving:map.isMoving(),projection:map.getProjection().type,
        ready:document.documentElement.dataset.artemisVisualReady==='true'};
      if(!result.loaded||result.moving||!result.ready)throw new Error('Native idle did not establish rendered readiness: '+JSON.stringify(result));
      return result;
    })()`,true);
    renderSettlements.push({reason,...result});
    return result;
  }
  async function key(key, code, virtualKey, navigates = false) {
    await cdp.send('Input.dispatchKeyEvent', {type:'keyDown',key,code,windowsVirtualKeyCode:virtualKey,
      ...(key === 'Enter' ? {text:'\r',unmodifiedText:'\r'} : {})});
    await cdp.send('Input.dispatchKeyEvent', {type:'keyUp',key,code,windowsVirtualKeyCode:virtualKey});
    if (!navigates) await settle();
  }
  async function click(selector, keyboard = false, navigates = false) {
    const point = await evaluate(cdp, `(() => {
      const node=document.querySelector(${JSON.stringify(selector)});
      if(!node)throw new Error('Missing control '+${JSON.stringify(selector)});
      node.scrollIntoView({block:'nearest',inline:'nearest'});
      node.focus({preventScroll:true});
      const b=node.getBoundingClientRect(), x=b.x+b.width/2,y=b.y+b.height/2;
      if(node.disabled || !b.width || !b.height || !node.contains(document.elementFromPoint(x,y))) throw new Error('Control obstructed '+${JSON.stringify(selector)});
      if(document.activeElement!==node)throw new Error('Control cannot receive focus');
      return {x,y,href:node.href || null};
    })()`);
    if (keyboard) await key(navigates ? 'Enter' : ' ', navigates ? 'Enter' : 'Space', navigates ? 13 : 32, navigates);
    else {
      await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,x:point.x,y:point.y});
      await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,x:point.x,y:point.y});
      // A navigation destroys the source document. Awaiting its animation
      // frames here can reject before the destination context is ready.
      if (!navigates) await settle();
    }
    return point;
  }
  async function waitDocumentNavigation(priorOrigin, path) {
    let arrived=false;
    while (Date.now()<deadline) {
      try {
        arrived=await evaluate(cdp,`performance.timeOrigin!==${JSON.stringify(priorOrigin)} && location.pathname===${JSON.stringify(path)}`);
      } catch (error) {
        // Only a context being replaced during the requested navigation may
        // remain pending. Other transport/runtime failures stay immediately fatal.
        if (!/Inspected target navigated or closed|Execution context was destroyed|Cannot find (?:default execution context|context with specified id)/.test(String(error))) throw error;
      }
      if(arrived)break;await delay(100);
    }
    check(arrived,'new destination document did not load: '+path);
    await waitForVisualReadiness(cdp,deadline);
    check(await evaluate(cdp, `location.pathname===${JSON.stringify(path)}`),'navigation reached wrong dataset');
    await cdp.send('Emulation.setFocusEmulationEnabled',{enabled:true});
    await mapIdle('document navigation');
  }
  async function navigate(url) {
    // Read-only document identity distinguishes a new destination context from
    // source-page readiness, without mutating either page or semantic state.
    const priorOrigin = await evaluate(cdp, 'performance.timeOrigin');
    await cdp.send('Page.navigate',{url:String(url)});
    await waitDocumentNavigation(priorOrigin,new URL(url).pathname);
  }
  async function semantic() {
    return evaluate(cdp, `(() => {
      const r=window.__ARTEMIS_GLOBE_SPIKE;
      return {dataset:r.data.meta.semantic_dataset,lifePathAvailable:r.data.lifePath.available,
        state:r.data.state, mode:r.lifePathMode,start:r.lifePathStartIndex,end:r.lifePathEndIndex,
        preset:r.activeTemporalPresetId,layers:[...r.activeLayerRefs].sort(),
        presence:r.selectedPresenceId,item:r.selectedItemId};
    })()`);
  }
  async function snapshot() {
    return evaluate(cdp, `(async () => {
      const r=window.__ARTEMIS_GLOBE_SPIKE;
      return {data:r.data,viewIndex:r.viewIndex,knowledge:[...r.knowledgeByItem],
        semanticSource:await r.map.getSource('artemis-semantic').getData(),
        chronology:r.map.getSource('life-path-chronology') ? await r.map.getSource('life-path-chronology').getData() : null,
        item:r.selectedItemId,presence:r.selectedPresenceId,preset:r.activeTemporalPresetId,
        mode:r.lifePathMode,start:r.lifePathStartIndex,end:r.lifePathEndIndex,layers:[...r.activeLayerRefs].sort(),
        alternatives:r.alternativesVisible,popup:r.popupPresenceId,
        inspectorHidden:document.getElementById('inspector').hidden,
        disclosures:[...document.querySelectorAll('#selection-card details')].map(d=>({label:d.querySelector('summary')?.textContent,open:d.open})),
        card:document.getElementById('selection-card').textContent,
        unresolved:document.getElementById('unresolved-items')?.textContent || null,
        camera:{center:r.map.getCenter().toArray(),zoom:r.map.getZoom(),bearing:r.map.getBearing(),pitch:r.map.getPitch()}};
    })()`,true);
  }
  async function mode(expected) {
    const actual=await evaluate(cdp, `(() => {
      const r=window.__ARTEMIS_GLOBE_SPIKE,button=document.getElementById('view-'+${JSON.stringify(expected)});
      return {view:r.presentationView,projection:r.map.getProjection().type,ready:r.projectionReady,
        pressed:button.getAttribute('aria-pressed'),other:document.getElementById('view-'+(${JSON.stringify(expected)}==='map'?'globe':'map')).getAttribute('aria-pressed'),
        disabled:button.disabled,url:new URL(location.href).searchParams.get('view') || 'globe'};
    })()`);
    check(actual.view===expected && actual.projection===(expected==='map'?'mercator':'globe') && actual.ready && !actual.disabled && actual.pressed==='true' && actual.other==='false' && actual.url===expected,'UI/runtime/URL projection disagreement: '+JSON.stringify(actual));
    return actual;
  }
  async function capture(dataset,lang,view,suffix='') {
    await mapIdle('capture '+dataset+'/'+lang+'/'+view);
    await mode(view);
    const layout=await evaluate(cdp, `(() => {
      const lang=${JSON.stringify(lang)},view=${JSON.stringify(view)};
      const names=lang==='ru'?{globe:'Глобус',map:'Карта 2D'}:{globe:'Globe',map:'2D map'};
      const visible=n=>{if(!n?.checkVisibility({checkVisibilityCSS:true}))return false;const b=n.getBoundingClientRect();return b.width>0&&b.height>0&&b.left>=0&&b.top>=0&&b.right<=innerWidth+1&&b.bottom<=innerHeight+1;};
      for(const id of ['projection-switch','view-globe','view-map'])if(!visible(document.getElementById(id)))throw new Error('Projection control outside viewport: '+id);
      for(const v of ['globe','map'])if(document.getElementById('view-'+v).innerText!==names[v])throw new Error('Projection label lost locale');
      if(document.documentElement.scrollWidth>innerWidth+1)throw new Error('Horizontal overflow');
      const header=document.getElementById('spike-banner').getBoundingClientRect();
      for(const node of document.querySelectorAll('#timeline-dock,.maplibregl-ctrl-top-right,.maplibregl-ctrl-top-left')) {
        if(!visible(node))continue;const b=node.getBoundingClientRect();
        if(Math.min(header.right,b.right)-Math.max(header.left,b.left)>1&&Math.min(header.bottom,b.bottom)-Math.max(header.top,b.top)>1)throw new Error('Header overlaps map/time control');
      }
      return {width:innerWidth,height:innerHeight,headerBottom:header.bottom};
    })()`);
    const stem='-projection-'+dataset+'-'+lang+'-'+view+(suffix?'-'+suffix:'');
    const screenshot=options.screenshot.replace(/\.png$/,stem+'.png'),dom=options.dom.replace(/\.html$/,stem+'.html');
    const image=await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});
    await writeFile(screenshot,Buffer.from(image.data,'base64'));
    await writeFile(dom,await evaluate(cdp,'document.documentElement.outerHTML'));
    captures.push({dataset,locale:lang,view,...layout,screenshot,dom,screenshotSha256:createHash('sha256').update(await readFile(screenshot)).digest('hex')});
  }
  async function toggle(view,scenario,keyboard=false) {
    await mapIdle('before '+scenario);
    const before=await snapshot(),beforeUrl=new URL(await evaluate(cdp,'location.href'));
    await click('#view-'+view,keyboard);await mapIdle('after '+scenario);await mode(view);
    const after=await snapshot(),afterUrl=new URL(await evaluate(cdp,'location.href'));
    check(JSON.stringify(before)===JSON.stringify(after),scenario+' changed semantic/source/selection/disclosure/camera state');
    beforeUrl.searchParams.delete('view');afterUrl.searchParams.delete('view');
    check(beforeUrl.href===afterUrl.href,scenario+' changed semantic URL or hash');
    comparisons.push({scenario,view,method:keyboard?'native Space after explicit focus':'native mouse',beforeSha256:hash(before),afterSha256:hash(after),knowledgeBeforeSha256:hash(before.knowledge),knowledgeAfterSha256:hash(after.knowledge),neutralProjectionSha256:hash(before.data.projection),adapterSourceSha256:hash(before.semanticSource),disclosuresBeforeSha256:hash(before.disclosures),disclosuresAfterSha256:hash(after.disclosures),semanticSourceDisclosureCameraPreserved:true});
  }
  async function slider(id,year) {
    const bounds=await evaluate(cdp,`(() => {const n=document.getElementById(${JSON.stringify(id)});n.focus();return {min:Number(n.min),max:Number(n.max),target:window.__ARTEMIS_GLOBE_SPIKE.data.lifePath.time_axis.values.indexOf(${JSON.stringify(year)})};})()`);
    check(bounds.target>=bounds.min&&bounds.target<=bounds.max,'native temporal slider target missing');
    const fromEnd=bounds.max-bounds.target<bounds.target-bounds.min;
    await key(fromEnd?'End':'Home',fromEnd?'End':'Home',fromEnd?35:36);
    for(let i=0;i<(fromEnd?bounds.max-bounds.target:bounds.target-bounds.min);i++)await key(fromEnd?'ArrowLeft':'ArrowRight',fromEnd?'ArrowLeft':'ArrowRight',fromEnd?37:39);
    check(await evaluate(cdp,`document.getElementById(${JSON.stringify(id)}).getAttribute('aria-valuetext')===${JSON.stringify(year)}`),'2D keyboard timeline did not update');
    await mode('map');
  }
  async function openSources(dataset) {
    if(dataset==='leonardo')await click('.popup-details');else await click('#region-details');
    const disclosures=await evaluate(cdp,`[...document.querySelectorAll('#selection-card details')].map((d,i)=>({i,source:!!d.querySelector('a'),uncertainty:!!d.querySelector('.uncertainty-card')})).filter(d=>d.source||d.uncertainty)`);
    check(disclosures.some(d=>d.source)&&disclosures.some(d=>d.uncertainty),'source/uncertainty access missing');
    for(const {i} of disclosures){
      await evaluate(cdp,`document.querySelectorAll('#selection-card details')[${i}].querySelector('summary').focus()`);
      if(!await evaluate(cdp,`document.querySelectorAll('#selection-card details')[${i}].open`))await key(' ','Space',32);
      check(await evaluate(cdp,`document.querySelectorAll('#selection-card details')[${i}].open`),'native source disclosure failed');
    }
    check(await evaluate(cdp,"[...document.querySelectorAll('#selection-card a')].some(a=>a.checkVisibility({checkVisibilityCSS:true}))"),'no visible source link');
    return disclosures;
  }
  async function historyStep(direction,expectedView,expectedSemantic) {
    const history=await cdp.send('Page.getNavigationHistory'),entry=history.entries[history.currentIndex+direction];
    check(!!entry,'missing presentation history entry');
    await cdp.send('Page.navigateToHistoryEntry',{entryId:entry.id});
    let restored=false;
    while(Date.now()<deadline){
      restored=await evaluate(cdp,`window.__ARTEMIS_GLOBE_SPIKE.presentationView===${JSON.stringify(expectedView)}`).catch(()=>false);
      if(restored)break;await delay(100);
    }
    check(restored,'Back/Forward did not restore presentation');await mapIdle('presentation history');await mode(expectedView);
    check(JSON.stringify(await semantic())===JSON.stringify(expectedSemantic),'Back/Forward lost recorded semantic state');
  }
  async function pickRegion() {
    // A read-only rendered hit identifies the actual native mouse target.
    await mapIdle('before native Region picking');
    const point=await evaluate(cdp,`(() => {
      const r=window.__ARTEMIS_GLOBE_SPIKE,canvas=r.map.getCanvas().getBoundingClientRect();
      for(let y=canvas.top+20;y<canvas.bottom-20;y+=12)for(let x=canvas.left+20;x<canvas.right-20;x+=12){
        if(document.elementFromPoint(x,y)!==r.map.getCanvas())continue;
        const hit=r.map.queryRenderedFeatures([x-canvas.left,y-canvas.top],{layers:['artemis-region-primary-fill']}).find(f=>f.properties.item_id);
        if(hit)return {x,y,item:hit.properties.item_id};
      }throw new Error('No unobstructed Region feature pixel for native 2D picking');
    })()`);
    await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,x:point.x,y:point.y});
    await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,x:point.x,y:point.y});await settle();
    check((await semantic()).item===point.item,'2D Region canvas picking lost item identity');
    picking.push({dataset:'region',view:'map',method:'native mouse on rendered Region pixel',item:point.item});
    return point;
  }
  // Clean defaults are captured from each real dataset, separately from view.
  for(const dataset of ['leonardo','region']){await navigate(routes[dataset]);defaults[dataset]=await semantic();await mode('globe');}
  const leonardo=new URL('?mode=range&start=1502&end=1502&presence=presence-rimini-1502-08-08&lang=en&view=globe&unknown=preserve#preserve',routes.leonardo);
  await navigate(leonardo);
  check((await semantic()).presence==='presence-rimini-1502-08-08','non-default Leonardo saved selection failed');
  await openSources('leonardo');
  await capture('leonardo','en','globe');await toggle('map','Leonardo Range source drawer');await capture('leonardo','en','map');
  await click('#language-ru');await capture('leonardo','ru','map');await toggle('globe','Leonardo Russian source drawer',true);await capture('leonardo','ru','globe');
  await click('#close-details');await click('#language-en');await toggle('map','Leonardo Range map interaction');
  await slider('range-start','1501');await slider('range-end','1501');
  check((await semantic()).presence===null,'empty 2D Range retained out-of-window Presence');
  await slider('range-end','1502');await slider('range-start','1502');
  // Locate the existing anchor by accessible label, without assuming a new ID.
  const cesenaSelector=await evaluate(cdp,`(() => {const n=[...document.querySelectorAll('.life-path-marker')].find(n=>n.getAttribute('aria-label')?.startsWith('Show Cesena summary,'));if(!n||n.hidden)throw new Error('Cesena anchor unavailable in 2D');return '.life-path-marker[data-place-id="'+n.dataset.placeId+'"]';})()`);
  await click(cesenaSelector);await delay(320);
  check((await semantic()).presence==='presence-cesena-1502-08-10','2D map marker failed to select existing Presence');
  picking.push({dataset:'leonardo',view:'map',method:'native mouse on existing map Place anchor',presence:(await semantic()).presence});
  await click('#mode-scrub');await slider('scrub-current','1502');
  await toggle('globe','Leonardo Scrub selected Presence');await toggle('map','Leonardo Scrub round trip',true);
  const saved=await evaluate(cdp,'location.href'),savedSemantic=await semantic();
  await toggle('globe','Leonardo presentation history entry');await historyStep(-1,'map',savedSemantic);await historyStep(1,'globe',savedSemantic);
  histories.push({dataset:'leonardo',back:true,forward:true,semanticPreserved:true});
  await navigate(routes.region);await navigate(saved);await mode('map');
  check(JSON.stringify(await semantic())===JSON.stringify(savedSemantic),'saved 2D Leonardo URL lost semantic state');
  histories.at(-1).savedUrlReopened=true;
  const regionSnapshots=[];
  await navigate(new URL('?lang=en&view=map',routes.region));
  for(let index=0;index<3;index++){
    await evaluate(cdp,"document.getElementById('temporal-preset').focus()");await key('Home','Home',36);
    for(let step=0;step<index;step++)await key('ArrowDown','ArrowDown',40);
    await mode('map');
    const selected=await evaluate(cdp,`(() => {const r=window.__ARTEMIS_GLOBE_SPIKE,p=r.viewIndex.temporal_presets[${index}],item=r.data.projection.items.find(i=>i.object_type==='Region');if(r.activeTemporalPresetId!==p.preset_id||!item)throw new Error('2D Region native time failed');return {preset:p.preset_id,item:item.item_id,geometryRefs:item.geometry_refs};})()`);
    await pickRegion();await openSources('region');await toggle('globe','Region preset '+index+' source drawer');
    if(index===1){await capture('region','en','globe');await toggle('map','Region English capture');await capture('region','en','map');await click('#language-ru');await capture('region','ru','map');await toggle('globe','Region Russian source drawer',true);await capture('region','ru','globe');await click('#language-en');}
    await toggle('map','Region preset '+index+' round trip');
    await click('#close-details');regionSnapshots.push(selected);
  }
  check(new Set(regionSnapshots.map(s=>s.geometryRefs.join(','))).size===3,'2D Region presets did not select distinct native outlines');
  const regionLayer=await evaluate(cdp, `(() => {const n=[...document.querySelectorAll('#layer-controls input')].find(n=>n.checked);if(!n)throw new Error('No active Region layer');return '#layer-controls input[value=\"'+n.value+'\"]';})()`);
  await click(regionLayer,true);await click(regionLayer,true);await mode('map');
  check((await semantic()).item===null,'native Region layer round trip did not establish unselected picking precondition');
  await delay(250);
  // Find a currently rendered Region pixel. Query is read-only; only native
  // mouse input below changes picking/selection, using the existing handlers.
  await pickRegion();
  const regionSaved=await evaluate(cdp,'location.href'),regionSemantic=await semantic();
  await toggle('globe','Region picked item');await historyStep(-1,'map',regionSemantic);await historyStep(1,'globe',regionSemantic);
  histories.push({dataset:'region',back:true,forward:true,semanticPreserved:true});
  await navigate(routes.leonardo);await navigate(regionSaved);await mode('map');
  check(JSON.stringify(await semantic())===JSON.stringify(regionSemantic),'saved 2D Region URL lost semantic state');histories.at(-1).savedUrlReopened=true;
  const crossExample=[];
  for(const dataset of ['region','leonardo']){
    await navigate(new URL('?lang=ru&view=map',routes[dataset]));
    const target=dataset==='region'?'leonardo':'region';
    const link=await evaluate(cdp,`document.getElementById('example-'+${JSON.stringify(target)}).href`),url=new URL(link);
    check([...url.searchParams.keys()].sort().join(',')==='lang,view'&&url.searchParams.get('lang')==='ru'&&url.searchParams.get('view')==='map'&&!url.hash,'cross-example presentation allowlist failed');
    const priorOrigin=await evaluate(cdp,'performance.timeOrigin');
    const clicked=await click('#example-'+target,false,true);
    await waitDocumentNavigation(priorOrigin,routes[target].pathname);await mode('map');
    check(JSON.stringify(await semantic())===JSON.stringify(defaults[target]),'cross-example link leaked foreign semantics');
    check(await evaluate(cdp,"document.getElementById('language-ru').getAttribute('aria-pressed')==='true'"),'cross-example link lost locale');
    crossExample.push({from:dataset,to:target,href:clicked.href,view:'map',locale:'ru',targetSemanticDefaults:true});
  }
  const invalid=[];
  for(const dataset of ['leonardo','region']){
    await navigate(new URL('?lang=en&view=invalid',routes[dataset]));await mode('globe');
    invalid.push({dataset,invalidViewDefaultsTo:'globe'});
  }
  return {outcome:'TECHNICAL_PROJECTION_PASS',method:'Native mouse/Space controls, native keyboard timeline and native canvas/marker picking; actual runtime snapshots',
    defaults,comparisons,renderSettlements,regionSnapshots,picking,histories,crossExample,invalid,captures,
    valueValidation:'not_assessed',
    limitations:['One MapLibre engine using two cartographic projections; not independent adapter parity.',
      'Runtime/source geometry and knowledge equality are technical checks, not historical validation.',
      'Named control focus and keyboard activation only; not a complete keyboard or assistive technology audit.']};
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
    cdp = await connectCdp(endpoint, deadline);
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    process.stderr.write('[browser evidence] initial navigation\n');
    await cdp.send('Page.navigate', { url: options.url });
    process.stderr.write('[browser evidence] readiness\n');
    const readiness = await waitForVisualReadiness(cdp, deadline);
    const isRegion = await evaluate(cdp, "window.__ARTEMIS_GLOBE_SPIKE?.data?.lifePath?.available === false");
    const placeLabels = isRegion ? null : await verifyPlaceLabels(cdp);
    process.stderr.write('[browser evidence] regionDisclosureRetest\n');
    const regionDisclosureRetest = isRegion ? await verifyRegionDisclosure(cdp, deadline) : null;
    process.stderr.write('[browser evidence] temporalRegion\n');
    const temporalRegion = isRegion ? await verifyTemporalRegion(cdp) : null;
    const capturedUrl = await evaluate(cdp, 'location.href');
    const dom = await evaluate(cdp, 'document.documentElement.outerHTML');
    const capture = await cdp.send('Page.captureScreenshot', {
      format: 'png',
      fromSurface: true,
      captureBeyondViewport: false
    });
    await writeFile(options.dom, `${dom}\n`, 'utf8');
    await writeFile(options.screenshot, Buffer.from(capture.data, 'base64'));
    const firstUse = isRegion ? null : await verifyFirstUse(cdp, options);
    const urlStateRestoration = !isRegion && options.verifyUrlState
      ? await verifyUrlStateRestoration(cdp, deadline)
      : null;
    // Run keyboard probes after capture and the existing semantic checks so the
    // probe cannot alter the captured artifact or downstream domain assertions.
    process.stderr.write('[browser evidence] keyboardInteraction\n');
    const keyboardInteraction = await verifyKeyboardInteraction(cdp, isRegion);
    const sourceAwareResearch = !isRegion && options.sourceAwareResearch
      ? await verifySourceAwareResearch(cdp, options, deadline)
      : null;
    const sharedPreviewNavigation = options.sharedPreviewNavigation
      ? await verifySharedPreviewNavigation(cdp, options, deadline)
      : null;
    const projectionSwitch = options.projectionSwitch
      ? await verifyProjectionSwitch(cdp, options, deadline)
      : null;
    const sha256 = value => createHash('sha256').update(value).digest('hex');
    const provenance = {
      schemaVersion: '1.0.0',
      nodeVersion: process.version,
      evidenceKind: 'automated_browser_check',
      visualAcceptance: 'not_assessed',
      capturedUrl,
      recordedAtUtc: new Date().toISOString(),
      checkoutCommit: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
      workflowRunUrl: process.env.GITHUB_RUN_ID
        ? `https://github.com/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID}` : null,
      workflowRunAttempt: process.env.GITHUB_RUN_ATTEMPT || null,
      browser: await cdp.send('Browser.getVersion'),
      requestedWindow: { width: options.width, height: options.height },
      reducedMotionRequested: options.reducedMotion,
      runnerSha256: sha256(await readFile(new URL(import.meta.url))),
      domSha256: sha256(await readFile(options.dom)),
      screenshotSha256: sha256(await readFile(options.screenshot)),
      limitations: ['Checkout identity is test-code provenance, not proof of the deployed commit.', 'DOM and screenshot precede the separate URL-restoration scenario.', 'Keyboard checks cover named controls only, not a full keyboard or assistive-technology audit.']
    };
    const report = { ...readiness, keyboardInteraction, placeLabels, firstUse, regionDisclosureRetest, temporalRegion, urlStateRestoration, sourceAwareResearch, sharedPreviewNavigation, projectionSwitch, provenance };
    if (options.report) await writeFile(options.report, JSON.stringify(report, null, 2) + '\n', 'utf8');
    process.stdout.write(`${JSON.stringify(report)}\n`);
  } catch (error) {
    // Save the failing UI before teardown. This is diagnostic evidence only;
    // the original assertion remains fatal and no successful report is emitted.
    if (cdp) {
      const failureDom=options.dom.replace(/\.html$/, '')+'-failure.html';
      const failureScreenshot=options.screenshot.replace(/\.png$/, '')+'-failure.png';
      const diagnostics=await Promise.race([
        Promise.allSettled([
          evaluate(cdp,'document.documentElement.outerHTML').then(dom=>writeFile(failureDom,dom,'utf8')).then(()=>failureDom),
          cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false})
            .then(capture=>writeFile(failureScreenshot,Buffer.from(capture.data,'base64'))).then(()=>failureScreenshot)
        ]),
        delay(3000).then(()=>null)
      ]);
      process.stderr.write('[browser evidence] failure diagnostics '+JSON.stringify(diagnostics
        ? diagnostics.map(result=>result.status==='fulfilled'?{path:result.value}:{captureError:String(result.reason)})
        : {captureError:'Best-effort capture exceeded three seconds'})+'\n');
    }
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
