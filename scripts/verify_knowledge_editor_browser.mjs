#!/usr/bin/env node
// Real local-backend verification. All records and accounts below are synthetic CI fixtures.
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const { chromium } = await import(process.env.ARTEMIS_PLAYWRIGHT_MODULE || 'playwright');

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const baseURL = process.env.KNOWLEDGE_EDITOR_URL || 'http://127.0.0.1:8000';
const output = resolve(process.env.KNOWLEDGE_EDITOR_EVIDENCE_DIR || join(root, '.impeccable/review'));
const API = '/api/knowledge-editor';
const password = 'Synthetic-editor-CI-2026!';
const sha256 = value => createHash('sha256').update(value).digest('hex');
const git = args => execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim();
const sourceCommit = git(['rev-parse', 'HEAD']);
if (process.env.ARTEMIS_SOURCE_COMMIT) assert.equal(sourceCommit, process.env.ARTEMIS_SOURCE_COMMIT, 'Evidence checkout must match ARTEMIS_SOURCE_COMMIT');
const report = {
  schema_version: 1, synthetic_data: true, verification_scope: 'local_backend_native_browser_not_public_deployment',
  source_commit: sourceCommit, source_tree: git(['rev-parse', 'HEAD^{tree}']),
  script_sha256: sha256(await readFile(fileURLToPath(import.meta.url))),
  source_files: {}, screenshots: [], snapshots: [], exports: [], scenarios: [], status: 'running',
};
for (const path of ['app/main.py', 'app/knowledge_editor/__init__.py', 'app/knowledge_editor/schemas.py', 'app/knowledge_editor/service.py', 'app/knowledge_editor/routes.py',
  'app/knowledge_editor/public_export.py', 'app/knowledge_editor/public_export.schema.json', 'scripts/verify_knowledge_editor_export.py',
  'app/knowledge_editor/static/index.html', 'app/knowledge_editor/static/editor.css', 'app/knowledge_editor/static/editor.js']) {
  report.source_files[path] = sha256(await readFile(join(root, path)));
}
await mkdir(output, { recursive: true });
const forbiddenAccountKeys = new Set(['owner_id', 'actor_id', 'reviewer_id', 'user_id', 'email', 'access_token', 'refresh_token']);
const privateExpressions = [];
const errors = [];
let browser;

function publicPrivacy(payload) {
  const text = JSON.stringify(payload);
  for (const expression of privateExpressions) assert.ok(!text.includes(expression), 'Private source expression escaped into public JSON');
  assert.ok(!text.includes('PRIVATE_EDITOR_CI_'), 'Private source marker escaped into public JSON');
  const walk = value => {
    if (Array.isArray(value)) return value.forEach(walk);
    if (value && typeof value === 'object') for (const [key, child] of Object.entries(value)) {
      assert.ok(!forbiddenAccountKeys.has(key), `Forbidden account field in public response: ${key}`);
      assert.notEqual(key, 'native_expression', 'Private source expression field escaped into public response');
      walk(child);
    }
  };
  walk(payload);
}

async function jsonRequest(request, endpoint, { token, method = 'GET', data, status = 200 } = {}) {
  const response = await request.fetch(endpoint, {
    method, ...(data === undefined ? {} : { data }),
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  assert.equal(response.status(), status, `${method} ${endpoint} returned unexpected status`);
  return { payload: await response.json(), response };
}

async function idle(page) {
  await page.waitForFunction(() => document.body.getAttribute('aria-busy') === 'false');
}

async function uiAction(page, selector, endpoint, method = 'POST', status = 200) {
  const [response] = await Promise.all([
    page.waitForResponse(response => new URL(response.url()).pathname === endpoint && response.request().method() === method),
    page.locator(selector).click(),
  ]);
  assert.equal(response.status(), status, `UI ${method} ${endpoint} returned unexpected status`);
  const payload = await response.json();
  await idle(page);
  return payload;
}

async function authenticate(page, email, register = false) {
  await page.goto('/editor/');
  await idle(page);
  await page.locator('#email').fill(email);
  await page.locator('#password').fill(password);
  const response = await uiAction(page, register ? '#register-submit' : '#login-submit', `/api/auth/${register ? 'register' : 'login'}`, 'POST', register ? 201 : 200);
  await page.locator('#workspace').waitFor({ state: 'visible' });
  assert.equal(await page.locator('#password').inputValue(), '', 'Password must be cleared after authentication');
  return response.access_token; // Kept in process memory only, never included in artifacts or logs.
}

async function openDraft(page, name, draftId, list = '#draft-list') {
  const disclosure = page.locator('#record-navigation-disclosure');
  const summary = disclosure.locator(':scope > summary');
  if (!await disclosure.evaluate(node => node.open)) {
    await summary.focus();
    await summary.press('Enter');
    assert.equal(await disclosure.evaluate(node => node.open), true, 'Keyboard must open record navigation');
  }
  await uiAction(page, `${list} button:has-text("${name}")`, `${API}/drafts/${draftId}`, 'GET');
  if (page.viewportSize().width <= 760 && await disclosure.evaluate(node => node.open)) {
    await summary.focus();
    await summary.press('Enter');
    assert.equal(await disclosure.evaluate(node => node.open), false, 'Keyboard must close record navigation');
  }
}

async function firstViewportForm(page, label) {
  // Inspect the first screen, rather than the scroll position used for the last action.
  await page.evaluate(() => new Promise(resolve => {
    window.scrollTo(0, 0);
    requestAnimationFrame(resolve);
  }));
  const controls = page.viewportSize().width <= 760 ? ['entity_name', 'save-draft-top'] : ['entity_name'];
  const bounds = await page.evaluate(ids => ids.map(id => {
    const node = document.getElementById(id);
    const rect = node.getBoundingClientRect();
    return { id, visible: node.getClientRects().length > 0, top: rect.top, bottom: rect.bottom,
      left: rect.left, right: rect.right, viewport_height: innerHeight, viewport_width: innerWidth };
  }), controls);
  for (const control of bounds) {
    assert.ok(control.visible && control.top >= 0 && control.bottom <= control.viewport_height
      && control.left >= 0 && control.right <= control.viewport_width,
    `${label}: ${control.id} must be fully visible on the first screen`);
  }
  return bounds;
}

async function layout(page, label) {
  const result = await page.evaluate(() => ({
    viewport: window.innerWidth,
    documentWidth: document.documentElement.scrollWidth,
    overflowing: [...document.querySelectorAll('input,textarea,select,button')].filter(node => {
      if (!node.getClientRects().length) return false;
      const bounds = node.getBoundingClientRect();
      return bounds.left < -1 || bounds.right > window.innerWidth + 1;
    }).map(node => node.id),
  }));
  assert.ok(result.documentWidth <= result.viewport + 1, `${label}: document has horizontal overflow`);
  assert.deepEqual(result.overflowing, [], `${label}: controls overflow viewport`);
  return result;
}

async function screenshot(page, filename, phase) {
  await page.screenshot({ path: join(output, filename), fullPage: true, animations: 'disabled' });
  report.screenshots.push({ file: filename, phase, sha256: sha256(await readFile(join(output, filename))), viewport: page.viewportSize() });
}

async function snapshot(request, snapshotId) {
  const endpoint = `${API}/public/snapshots/${snapshotId}`;
  const { payload, response } = await jsonRequest(request, endpoint);
  publicPrivacy(payload);
  const entry = { snapshot_id: snapshotId, endpoint, payload, response_sha256: sha256(await response.text()) };
  report.snapshots.push(entry);
  return entry;
}

async function downloadPublic(page, entityId, expectedSnapshots, filename, keyboard = false) {
  const endpoint = `${API}/public/objects/${entityId}/export`;
  const button = page.getByRole('button', { name: 'Скачать опубликованную историю (JSON)', exact: true });
  assert.ok((await page.locator('#public-export-help').innerText()).includes('даже если открыта старая версия'), 'Download must explain object-wide history scope');
  if (keyboard) {
    await page.locator('#public-card ol a').last().focus();
    await page.keyboard.press('Tab');
    assert.equal(await button.evaluate(node => node === document.activeElement), true, 'Tab order must reach the native download button from publication history');
  }
  const [download, response] = await Promise.all([
    page.waitForEvent('download'),
    page.waitForResponse(response => new URL(response.url()).pathname === endpoint),
    keyboard ? page.keyboard.press('Enter') : button.click(),
  ]);
  assert.equal(response.status(), 200, 'Public export download must succeed');
  assert.equal(response.request().headers().authorization, undefined, 'Download must be anonymous');
  assert.equal(response.headers()['cache-control'], 'no-store');
  assert.equal(response.headers()['x-content-type-options'], 'nosniff');
  assert.equal(download.suggestedFilename(), `artemis-editor-${entityId}-public.json`, 'Native download must retain server filename');
  const path = join(output, filename);
  await download.saveAs(path);
  assert.equal(await download.failure(), null, 'Native attachment must actually be saved');
  const bytes = await readFile(path);
  assert.deepEqual(bytes, await response.body(), 'Saved JSON must retain authoritative backend bytes');
  const payload = JSON.parse(bytes.toString('utf8'));
  publicPrivacy(payload);
  assert.equal(payload.entity_id, entityId);
  assert.equal(payload.current_snapshot_id, expectedSnapshots.at(-1).snapshot_id);
  assert.deepEqual(payload.snapshots, expectedSnapshots.map(entry => entry.payload), 'Download must include every exact public snapshot');
  const verified = execFileSync(process.env.ARTEMIS_PYTHON || 'python', [join(root, 'scripts/verify_knowledge_editor_export.py'), path], { cwd: root, encoding: 'utf8' }).trim();
  assert.ok(verified.includes('Public export integrity verified'), 'Actual native download must pass the offline verifier');
  await button.waitFor({ state: 'visible' });
  await page.waitForFunction(() => document.getElementById('download-public-history').getAttribute('aria-busy') === 'false');
  assert.equal(await page.locator('#public-export-error').isVisible(), false, 'Successful download must not display an error');
  return { entity_id: entityId, endpoint, file: filename, response_sha256: sha256(bytes), package_digest: payload.package_digest,
    snapshot_ids: payload.snapshots.map(item => item.snapshot_id), offline_verifier: 'PASS', activation: keyboard ? 'keyboard_enter' : 'pointer' };
}

async function failedPublicDownload(page, context, expectedStatement) {
  let downloads = 0;
  const count = () => downloads++;
  page.on('download', count);
  await context.setOffline(true);
  try {
    await page.locator('#download-public-history').click();
    await page.locator('#public-export-error').waitFor({ state: 'visible' });
    await page.waitForFunction(() => document.getElementById('download-public-history').getAttribute('aria-busy') === 'false');
    assert.equal(downloads, 0, 'Failed export must not trigger a download');
    assert.equal(await page.locator('#public-card .statement').textContent(), expectedStatement, 'Failed download must retain displayed card');
    assert.ok((await page.locator('#public-export-error').innerText()).includes('Не удалось скачать'), 'Failure must name download problem and retry');
    assert.equal(await page.locator('#public-export-error').getAttribute('role'), 'alert');
    assert.equal(await page.locator('#download-public-history').isEnabled(), true, 'Failure must allow retry');
  } finally {
    await context.setOffline(false);
    page.off('download', count);
  }
}

async function verifyPublic(page, entityId, expectedStatement, filename) {
  await page.goto(`/editor/?object=${encodeURIComponent(entityId)}`);
  await idle(page);
  await page.locator('#public-card').waitFor({ state: 'visible' });
  assert.equal(await page.locator('#public-card .statement').textContent(), expectedStatement, 'Public Claim must render as literal text');
  assert.equal(await page.locator('#public-card img').count(), 0, 'Claim markup must not create image elements');
  assert.equal(await page.evaluate(() => window.__editorXss), undefined, 'Claim markup must not execute script');
  const text = await page.locator('#public-card').innerText();
  assert.ok(text.includes('Черновик') && text.includes('Отсутствует'), 'Public card must preserve draft/missing epistemic status');
  assert.ok(!text.includes('PRIVATE_EDITOR_CI_'), 'Private source expression escaped into public DOM');
  assert.ok(!text.includes('owner@example.com') && !text.includes('reviewer@example.com'), 'Account identity escaped into public DOM');
  const html = await page.content();
  assert.ok(!html.includes('PRIVATE_EDITOR_CI_'), 'Private source expression escaped into public HTML');
  const layoutResult = await layout(page, filename);
  await screenshot(page, filename, 'published_corrected_candidate_anonymous');
  const domFile = filename.replace('.png', '.html');
  await writeFile(join(output, domFile), html);
  report.screenshots.at(-1).dom_file = domFile;
  report.screenshots.at(-1).dom_sha256 = sha256(html);
  return layoutResult;
}

try {
  browser = await chromium.launch();
  report.browser_version = browser.version();
  const anonymous = await browser.newContext({ baseURL });
  for (const [index, viewport] of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }].entries()) {
    const label = index === 0 ? 'desktop' : 'mobile';
    const scenario = { label, viewport, checks: [] };
    report.scenarios.push(scenario);
    const ownerContext = await browser.newContext({ baseURL, viewport });
    const reviewerContext = await browser.newContext({ baseURL, viewport });
    const owner = await ownerContext.newPage();
    const reviewer = await reviewerContext.newPage();
    for (const page of [owner, reviewer]) {
      page.on('pageerror', error => errors.push({ viewport: label, message: error.message }));
      page.on('dialog', dialog => dialog.accept());
    }
    let ownerToken = await authenticate(owner, 'owner@example.com', index === 0);
    if (index === 0) {
      // Registration creates no refresh cookie. A real login proves resumable sessions.
      await uiAction(owner, '#logout', '/api/auth/logout');
      ownerToken = await authenticate(owner, 'owner@example.com');
    }
    scenario.initial_form_viewport = await firstViewportForm(owner, `${label} initial form`);
    await owner.locator('#entity_name').focus();
    await owner.keyboard.insertText(`Синтетический павильон ${label}`);
    await owner.keyboard.press('Tab');
    if (viewport.width <= 760) {
      assert.equal(await owner.locator('#save-draft-top').evaluate(node => document.activeElement === node), true, 'Keyboard must reach mobile quick Save');
      await owner.keyboard.press('Tab');
    }
    assert.equal(await owner.locator('#record-fields details > summary').first().evaluate(node => document.activeElement === node), true, 'Keyboard must reach object description disclosure');
    const name = `Синтетический павильон ${label}`;
    let draft = await uiAction(owner, viewport.width <= 760 ? '#save-draft-top' : '#save-draft', `${API}/drafts`, 'POST', 201);
    assert.equal(draft.content.source.title, '', 'Incomplete draft must remain incomplete');
    scenario.checks.push('keyboard_navigation', 'incomplete_draft_saved');
    await owner.reload();
    await idle(owner);
    await owner.locator('#workspace').waitFor({ state: 'visible' });
    await openDraft(owner, name, draft.id);
    assert.equal(await owner.locator('#entity_name').inputValue(), name, 'Draft must resume after browser reload');
    scenario.resumed_form_viewport = await firstViewportForm(owner, `${label} resumed form`);
    let submitRequests = 0;
    const countSubmits = request => { if (new URL(request.url()).pathname.endsWith('/submit')) submitRequests += 1; };
    owner.on('request', countSubmits);
    await owner.locator('#submit-review').click();
    await owner.locator('#error').waitFor({ state: 'visible' });
    assert.equal(await owner.locator('#source_title').evaluate(node => document.activeElement === node), true, 'Submission gaps must focus first missing field');
    assert.equal(submitRequests, 0, 'Incomplete form must not claim successful submission');
    owner.off('request', countSubmits);
    scenario.checks.push('reload_resume', 'submission_gap_focus');

    const nativeExpression = `  PRIVATE_EDITOR_CI_${label}: synthetic source wording.\n\n  Preserve whitespace.  `;
    privateExpressions.push(nativeExpression);
    const locator = '  Synthetic catalogue, page 7, entry A.  ';
    const originalStatement = '<img src=x onerror="window.__editorXss=true"> Источник сообщает о синтетическом павильоне.';
    for (const [id, value] of Object.entries({ source_title: 'Синтетический каталог · проверка интерфейса',
      source_url: 'https://example.com/editor-synthetic-source', source_expression: nativeExpression,
      claim_statement: originalStatement, evidence_locator: locator,
      claim_uncertainty: 'Это искусственный пример для проверки программы; исторических сведений не заявляет.' })) {
      await owner.locator(`#${id}`).fill(value);
    }
    await owner.locator('#author_attestation').check();
    draft = await uiAction(owner, '#save-draft', `${API}/drafts/${draft.id}`, 'PUT');
    assert.ok(draft.content.evidence.native_expression === nativeExpression, 'Private source expression must remain literal');
    assert.ok(draft.content.evidence.locator === locator, 'Locator whitespace must remain literal');
    assert.equal(draft.content.claim.confidence, 'unknown', 'No confidence may be invented');
    scenario.checks.push('literal_source_preservation', 'unknown_confidence_preserved');

    // A second real authenticated write advances the server version, exercising genuine CAS failure.
    const serverContent = structuredClone(draft.content);
    serverContent.claim.uncertainty = 'Серверная версия после конкурентного сохранения.';
    await jsonRequest(ownerContext.request, `${API}/drafts/${draft.id}`, { token: ownerToken, method: 'PUT', data: { expected_version: draft.version, content: serverContent } });
    const unsaved = 'Локальный несохранённый текст после конкурирующего изменения.';
    await owner.locator('#claim_statement').fill(unsaved);
    await uiAction(owner, '#save-draft', `${API}/drafts/${draft.id}`, 'PUT', 409);
    assert.equal(await owner.locator('#claim_statement').inputValue(), unsaved, '409 must preserve entered text');
    await owner.locator('#conflict-panel').waitFor({ state: 'visible' });
    await uiAction(owner, '#reload-record', `${API}/drafts/${draft.id}`, 'GET');
    assert.equal(await owner.locator('#claim_statement').inputValue(), originalStatement, 'Explicit reload must use actual server version');
    assert.equal(await owner.locator('#claim_uncertainty').inputValue(), serverContent.claim.uncertainty, 'Explicit reload must expose competing server change');
    scenario.checks.push('real_stale_version_409', '409_preserves_text', 'explicit_conflict_reload');

    await owner.locator('#claim_statement').fill(unsaved);
    await ownerContext.setOffline(true);
    await owner.locator('#save-draft').click();
    await idle(owner);
    await owner.locator('#error').waitFor({ state: 'visible' });
    assert.equal(await owner.locator('#claim_statement').inputValue(), unsaved, 'Network failure must preserve entered text');
    assert.ok((await owner.locator('#error').innerText()).includes('Сохранение не подтверждено'), 'Offline error must not assert saved state');
    await ownerContext.setOffline(false);
    await owner.locator('#claim_statement').fill(originalStatement);
    draft = await uiAction(owner, '#save-draft', `${API}/drafts/${draft.id}`, 'PUT');
    scenario.checks.push('real_offline_failure_preserves_text', 'recovery_save');
    scenario.saved_form_viewport = await firstViewportForm(owner, `${label} saved form`);
    scenario.editor_layout = await layout(owner, label);
    await screenshot(owner, `${label}.png`, 'complete_saved_draft_before_review');
    draft = await uiAction(owner, '#submit-review', `${API}/drafts/${draft.id}/submit`);
    await owner.locator('#review-reason').fill('Проверен синтетический пример; это проверка автором, историческая достоверность не заявлена.');
    draft = await uiAction(owner, '#review-accept', `${API}/drafts/${draft.id}/review`);
    assert.equal(draft.review_mode, 'owner_self_review');
    assert.equal(draft.published_snapshot_id, null, 'Editorial acceptance must not publish automatically');
    await jsonRequest(anonymous.request, `${API}/public/objects/${draft.entity_id}`, { status: 404 });
    draft = await uiAction(owner, '#publish-record', `${API}/drafts/${draft.id}/publish`);
    const initial = await snapshot(anonymous.request, draft.published_snapshot_id);
    assert.equal(initial.payload.claim.review_state, 'draft');
    assert.equal(initial.payload.claim.evidence_state, 'missing');
    assert.equal(initial.payload.source.review_state, 'draft');
    assert.equal(initial.payload.evidence.review_state, 'draft');
    assert.equal(initial.payload.entity.position, null);
    assert.equal(initial.payload.entity.world_time, null);
    scenario.checks.push('owner_self_review_disclosed', 'acceptance_not_publication', 'explicit_initial_publication', 'epistemic_states_not_promoted');

    await owner.locator('#correction-reason').fill('Исправить формулировку синтетического примера, сохранив исходную публикацию.');
    const correction = await uiAction(owner, '#start-correction', `${API}/revisions/${draft.accepted_revision_id}/corrections`, 'POST', 201);
    assert.equal(correction.predecessor_revision_id, draft.accepted_revision_id);
    assert.equal(await owner.locator('#author_attestation').isChecked(), false, 'Correction must require new human attestation');
    const correctedStatement = `${originalStatement} Поправка: описание уточнено.`;
    await owner.locator('#claim_statement').fill(correctedStatement);
    await owner.locator('#author_attestation').check();
    await uiAction(owner, '#save-draft', `${API}/drafts/${correction.id}`, 'PUT');
    await uiAction(owner, '#submit-review', `${API}/drafts/${correction.id}/submit`);
    let latest = await jsonRequest(anonymous.request, `${API}/public/objects/${draft.entity_id}`);
    assert.equal(latest.payload.snapshot_id, initial.snapshot_id, 'Pending correction must retain current publication');

    await authenticate(reviewer, 'reviewer@example.com', index === 0);
    await openDraft(reviewer, name, correction.id, '#review-queue');
    await reviewer.locator('#review-reason').fill('Другой аккаунт проверил синтетическую поправку; независимость и историческая достоверность не заявлены.');
    let accepted = await uiAction(reviewer, '#review-accept', `${API}/drafts/${correction.id}/review`);
    assert.equal(accepted.review_mode, 'separate_principal_review');
    latest = await jsonRequest(anonymous.request, `${API}/public/objects/${draft.entity_id}`);
    assert.equal(latest.payload.snapshot_id, initial.snapshot_id, 'Accepted correction must await explicit publication');
    accepted = await uiAction(reviewer, '#publish-record', `${API}/drafts/${correction.id}/publish`);
    const final = await snapshot(anonymous.request, accepted.published_snapshot_id);
    assert.equal(final.payload.predecessor_revision_id, initial.payload.revision_id);
    assert.equal(final.payload.claim.statement, correctedStatement);
    const initialAfter = await jsonRequest(anonymous.request, initial.endpoint);
    assert.deepEqual(initialAfter.payload, initial.payload, 'Historical snapshot must remain immutable after correction');
    assert.equal(sha256(await initialAfter.response.text()), initial.response_sha256, 'Historical raw response must remain immutable');
    latest = await jsonRequest(anonymous.request, `${API}/public/objects/${draft.entity_id}`);
    publicPrivacy(latest.payload);
    assert.equal(latest.payload.snapshot_id, final.snapshot_id);
    assert.equal(latest.payload.published_snapshots.length, 2, 'Publication history must expose both snapshots');
    scenario.entity_id = draft.entity_id;
    scenario.initial_snapshot_id = initial.snapshot_id;
    scenario.corrected_snapshot_id = final.snapshot_id;
    scenario.checks.push('correction_predecessor_preserved', 'separate_account_review_disclosed', 'correction_requires_explicit_publication', 'old_snapshot_bytes_immutable', 'public_history_retained');

    const publicPage = await anonymous.newPage();
    await publicPage.setViewportSize(viewport);
    publicPage.on('pageerror', error => errors.push({ viewport: label, message: error.message }));
    scenario.public_layout = await verifyPublic(publicPage, draft.entity_id, correctedStatement, `public-${label}.png`);
    const exported = await downloadPublic(publicPage, draft.entity_id, [initial, final], `public-${label}.json`);
    report.exports.push(exported);
    await publicPage.goto(`/editor/?snapshot=${encodeURIComponent(initial.snapshot_id)}`);
    await idle(publicPage);
    assert.equal(await publicPage.locator('#public-card .statement').textContent(), originalStatement, 'Anonymous historical card must show original Claim');
    assert.ok(!(await publicPage.content()).includes('PRIVATE_EDITOR_CI_'), 'Historical public DOM must omit private source wording');
    await failedPublicDownload(publicPage, anonymous, originalStatement);
    const historicalExport = await downloadPublic(publicPage, draft.entity_id, [initial, final], `public-${label}-from-old-snapshot.json`, true);
    assert.equal(historicalExport.response_sha256, exported.response_sha256, 'Old-snapshot keyboard download must return identical current published-history bytes');
    scenario.export_downloads = [exported, historicalExport];
    const allPublished = await jsonRequest(anonymous.request, `${API}/public/objects`);
    publicPrivacy(allPublished.payload);
    const history = await jsonRequest(anonymous.request, `${API}/public/objects/${draft.entity_id}/history`);
    publicPrivacy(history.payload);
    assert.equal(history.payload.length, 2);
    scenario.checks.push('anonymous_public_and_historical_cards', 'literal_html_rendering_no_execution', 'private_source_and_account_fields_absent', 'no_horizontal_overflow',
      'native_download_saved_json_offline_verified', 'server_attachment_bytes_and_filename_preserved', 'old_snapshot_keyboard_download_full_current_history',
      'repeat_export_bytes_identical', 'offline_export_failure_retains_card_no_download', 'export_retry_after_failure');
    await publicPage.close();
    await ownerContext.close();
    await reviewerContext.close();
  }
  assert.deepEqual(errors, [], 'Native UI must not emit uncaught JavaScript errors');
  report.uncaught_js_errors = errors;
  report.status = 'passed';
  await anonymous.close();
} catch (error) {
  report.status = 'failed';
  report.failure = error.message;
  throw error;
} finally {
  report.completed_at = new Date().toISOString();
  await writeFile(join(output, 'browser-report.json'), `${JSON.stringify(report, null, 2)}\n`);
  if (browser) await browser.close();
}
console.log(`Knowledge editor native browser verification passed: ${report.scenarios.length} viewports, ${report.snapshots.length} immutable synthetic snapshots.`);
