#!/usr/bin/env node
// Run against the generated non-public proof, never a public deployment.
// NODE_PATH may point at an isolated install of playwright@1.51.1.
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { createRequire } from 'node:module';
import { resolve, join } from 'node:path';
import { parseArgs } from 'node:util';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const { values } = parseArgs({ options: {
  'proof-dir': { type: 'string' }, output: { type: 'string' },
} });
assert(values['proof-dir'] && values.output, 'Required: --proof-dir PATH --output PATH');
const proofDir = resolve(values['proof-dir']);
const output = resolve(values.output);
await mkdir(output, { recursive: true });
const html = await readFile(join(proofDir, 'index.html'), 'utf8');
const payloadBytes = await readFile(join(proofDir, 'proof.json'));
const payload = JSON.parse(payloadBytes);
const ids = [
  'claim-atl-1466-1-733v-heydenreich-date-v1',
  'claim-atl-1466-1-733v-pedretti-date-v1',
];
assert.deepEqual(payload.record.claims.map(claim => claim.id).sort(), [...ids].sort());
const clickHandler = "button.addEventListener('click', () => setFocus(claim.id));";
assert.equal(html.split(clickHandler).length, 2, 'Negative control must remove exactly one focus binding');
const brokenHtml = html.replace(clickHandler, '// Negative control: focus binding removed.');
const wrongIdentity = structuredClone(payload);
wrongIdentity.record.object_ref = 'invalid-proof-identity';

// Serve only the generated files; all fault injection stays in memory.
const server = createServer((request, response) => {
  const path = new URL(request.url, 'http://localhost').pathname;
  const missing = path === '/missing/proof.json';
  const json = path.endsWith('/proof.json');
  const body = json ? (missing ? '{}' : path === '/invalid/proof.json'
    ? JSON.stringify(wrongIdentity) : payloadBytes)
    : path === '/broken/' ? brokenHtml : html;
  response.writeHead(missing ? 503 : 200, {
    'Content-Type': json ? 'application/json' : 'text/html; charset=utf-8',
    'Cache-Control': 'no-store',
  });
  response.end(body);
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const evidence = {
  schema_version: 1,
  purpose: 'Non-public ATL technical browser regression; not human or user-value evidence',
  source_commit: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
  source_dirty: Boolean(execFileSync('git', ['status', '--porcelain'], { encoding: 'utf8' }).trim()),
  proof_sha256: createHash('sha256').update(payloadBytes).digest('hex'),
  html_sha256: createHash('sha256').update(html).digest('hex'),
  reviewed_package_blob: payload.reviewed_package_blob,
  playwright_version: require('playwright/package.json').version,
  checks: [], screenshots: [], captures: [], passed: false,
  source_navigation: 'URL activation intercepted locally; external source availability not verified',
};
let browser;
let page;
const pageErrors = [];
const card = id => page.locator(`article[data-claim-id="${id}"]`);

async function snapshot(name) {
  const filename = `${name}.png`;
  await page.screenshot({ path: join(output, filename), fullPage: true });
  await writeFile(join(output, `${name}.html`), await page.content());
  evidence.screenshots.push(filename);
  evidence.captures.push({ filename, ...await page.evaluate(() => ({
    viewport_width: innerWidth, viewport_height: innerHeight,
    document_width: document.documentElement.scrollWidth,
  })) });
}

async function loaded(path = '/') {
  await page.goto(origin + path);
  await page.waitForFunction(() => document.querySelectorAll('#positions article').length === 2
    && document.querySelector('#positions button[aria-pressed]'));
}

async function assertFocus(expected) {
  const href = await page.evaluate(() => location.href);
  assert.equal(new URL(href).searchParams.get('claim'), expected, 'focus URL must match selected Claim');
  assert.equal(await page.locator('#clear-focus').isVisible(), Boolean(expected));
  for (const id of ids) {
    assert(await card(id).isVisible(), 'Focusing must preserve both alternatives');
    assert.equal(await card(id).getAttribute('data-focused'), String(id === expected));
    assert.equal(await card(id).locator('button').getAttribute('aria-pressed'), String(id === expected));
  }
}

async function noOverflow() {
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    'Narrow layout must not overflow horizontally');
}

async function check(name, action) {
  await action();
  evidence.checks.push({ name, passed: true });
}

try {
  browser = await chromium.launch({ headless: true });
  evidence.browser_version = browser.version();
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  // External source activation is observed, not fetched or declared reachable.
  const sourceUris = payload.record.sources.map(source => source.uri);
  await context.route('**/*', async route => {
    const url = route.request().url();
    if (url.startsWith(origin + '/')) return route.continue();
    if (sourceUris.includes(url)) return route.fulfill({ contentType: 'text/html', body: '<title>Source navigation observed</title>' });
    return route.abort();
  });
  page = await context.newPage();
  page.setDefaultTimeout(5000);
  page.on('pageerror', error => pageErrors.push(error.message));

  await check('default identity and unresolved alternatives', async () => {
    await loaded();
    assert.equal(await page.locator('#artifact').innerText(), payload.record.label + ' — one artifact');
    assert.match(await page.locator('.status').innerText(), /Dating disputed/);
    assert.match(await page.locator('.status').innerText(), /neither is an established production date/);
    assert.equal(await page.locator('#qualifier').innerText(), payload.conditional_qualifier);
    assert.match(await page.locator('#review-status').innerText(), /unvalidated/);
    for (const claim of payload.record.claims) {
      assert.equal(await card(claim.id).locator('h3').innerText(), claim.statement);
    }
    assert.equal(await page.locator('input[type="range"]').count(), 0);
    await assertFocus(null);
    await snapshot('desktop-default');
  });

  await check('both focus states, URL reload and reversible reset', async () => {
    for (const [index, id] of ids.entries()) {
      await card(id).locator('button').click();
      await assertFocus(id);
      await snapshot(`desktop-focus-${index + 1}`);
      await page.reload();
      await page.waitForSelector('#positions button[aria-pressed]');
      await assertFocus(id);
    }
    await page.locator('#clear-focus').click();
    await assertFocus(null);
  });

  await check('separate locators, mediated attribution and source activation', async () => {
    const locators = [];
    for (const id of ids) {
      const link = payload.record.evidence_links.find(item => item.claim_id === id);
      const source = payload.record.sources.find(item => item.id === link.source_id);
      await card(id).locator('summary').click();
      const details = await card(id).locator('details').innerText();
      assert(details.includes('Locator: ' + link.locator));
      assert.match(details, /Attribution mediated by the Museo Galileo catalogue/);
      assert.match(details, /original publication was not independently inspected/);
      locators.push(link.locator);
      const anchor = card(id).locator('a');
      assert.equal(await anchor.getAttribute('href'), source.uri);
      assert.equal(await anchor.getAttribute('target'), '_blank');
      assert.match(await anchor.getAttribute('rel'), /noopener/);
      const popupPromise = page.waitForEvent('popup');
      await anchor.click();
      const popup = await popupPromise;
      await popup.waitForLoadState('domcontentloaded');
      assert.equal(popup.url(), source.uri);
      await popup.close();
    }
    assert.equal(new Set(locators).size, 2, 'Each Claim must disclose its distinct accepted locator');
    await snapshot('desktop-provenance');
  });

  await check('narrow keyboard focus, disclosure and reset without overflow', async () => {
    await page.setViewportSize({ width: 375, height: 812 });
    await loaded();
    await noOverflow();
    await page.keyboard.press('Tab');
    assert(await card(ids[0]).locator('button').evaluate(node => node === document.activeElement));
    await page.keyboard.press('Enter');
    await assertFocus(ids[0]);
    await page.keyboard.press('Tab');
    assert(await card(ids[0]).locator('summary').evaluate(node => node === document.activeElement));
    await page.keyboard.press('Enter');
    assert(await card(ids[0]).locator('details').evaluate(node => node.open));
    await page.keyboard.press('Tab'); // First source link.
    assert(await card(ids[0]).locator('a').evaluate(node => node === document.activeElement));
    await page.keyboard.press('Tab'); // Second position button.
    assert(await card(ids[1]).locator('button').evaluate(node => node === document.activeElement));
    await page.keyboard.press('Space');
    await assertFocus(ids[1]);
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter');
    assert(await card(ids[1]).locator('details').evaluate(node => node.open));
    await page.keyboard.press('Tab'); // Second source link.
    await page.keyboard.press('Tab'); // Clear focus.
    assert(await page.locator('#clear-focus').evaluate(node => node === document.activeElement));
    await noOverflow();
    await snapshot('narrow-keyboard-provenance');
    await page.keyboard.press('Enter');
    await assertFocus(null);
  });

  await check('unavailable payload and wrong identity fail closed', async () => {
    for (const [path, message] of [
      ['/missing/', 'Reviewed proof record is unavailable'],
      ['/invalid/', 'Proof identity/Claim closure failed'],
    ]) {
      await page.goto(origin + path);
      await page.waitForFunction(() => document.querySelector('#artifact').textContent === 'Review proof unavailable');
      assert.equal(await page.locator('#scope').innerText(), message);
      assert.equal(await page.locator('#positions article').count(), 0);
      assert.equal(await page.locator('#clear-focus').isVisible(), false);
    }
    await snapshot('invalid-payload');
  });

  await check('negative control rejects a removed focus handler', async () => {
    await loaded('/broken/');
    await card(ids[0]).locator('button').click();
    await assert.rejects(() => assertFocus(ids[0]), /focus URL must match selected Claim/);
  });
  assert.deepEqual(pageErrors, [], 'Unexpected browser runtime errors');
  evidence.passed = true;
} catch (error) {
  evidence.error = error.stack || String(error);
  if (page) await snapshot('failure').catch(() => {});
  process.exitCode = 1;
} finally {
  evidence.page_errors = pageErrors;
  await writeFile(join(output, 'evidence.json'), JSON.stringify(evidence, null, 2) + '\n');
  await browser?.close();
  await new Promise(resolve => server.close(resolve));
}
console.log(JSON.stringify(evidence, null, 2));
