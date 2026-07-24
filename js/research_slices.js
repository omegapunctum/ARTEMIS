import { fetchPublicApi, fetchWithAuth, buildApiError } from './auth.js';

const BASE_PATH = '/api/research-slices';
const SCHEMA_VERSION = '2.0';
const ANNOTATION_TYPES = ['fact', 'interpretation', 'hypothesis'];
const ANNOTATION_TYPE_LABELS = {
  fact: 'Fact',
  interpretation: 'Interpretation',
  hypothesis: 'Hypothesis'
};
const EVIDENCE_KINDS = new Set(['source', 'relation']);

function normalizeCount(value) {
  if (value === null || value === undefined || value === '') return null;
  const num = Number(value);
  if (!Number.isFinite(num) || num < 0) return null;
  return Math.trunc(num);
}

function buildCompactTimeRangeSummary(timeRange) {
  if (!timeRange || typeof timeRange !== 'object') return '';
  const start = Number(timeRange.start);
  const end = Number(timeRange.end);
  if (!Number.isFinite(start) || !Number.isFinite(end)) return '';
  if (timeRange.mode === 'point' || start === end) return `${Math.trunc(start)}`;
  return `${Math.trunc(start)}–${Math.trunc(end)}`;
}

function buildSliceFindings(annotationInputs) {
  const source = annotationInputs && typeof annotationInputs === 'object' ? annotationInputs : {};
  const baseId = Date.now().toString(36);
  const findings = [];
  ANNOTATION_TYPES.forEach((type, index) => {
    const text = String(source[type] || '').trim();
    if (!text) return;
    findings.push({
      id: `ann-${baseId}-${type}-${index + 1}`,
      type,
      text
    });
  });
  return findings;
}

export function parseEvidenceRefs(value) {
  if (Array.isArray(value)) {
    return value.map((entry) => ({
      kind: String(entry?.kind || '').trim().toLowerCase(),
      ref_id: String(entry?.ref_id || '').trim(),
      supports_finding_ids: Array.isArray(entry?.supports_finding_ids)
        ? [...new Set(entry.supports_finding_ids.map((id) => String(id || '').trim()).filter(Boolean))]
        : []
    })).filter((entry) => EVIDENCE_KINDS.has(entry.kind) && entry.ref_id);
  }

  const tokens = String(value || '')
    .split(/[\n,]+/)
    .map((token) => token.trim())
    .filter(Boolean);
  const refs = [];
  const seen = new Set();
  tokens.forEach((token) => {
    const match = token.match(/^(source|relation)\s*:\s*(.+)$/i);
    if (!match) {
      throw new Error(`Invalid evidence reference "${token}". Use source:<id> or relation:<id>.`);
    }
    const kind = match[1].toLowerCase();
    const refId = match[2].trim();
    if (!refId) throw new Error('Evidence reference id is required.');
    const key = `${kind}:${refId}`;
    if (seen.has(key)) return;
    seen.add(key);
    refs.push({ kind, ref_id: refId, supports_finding_ids: [] });
  });
  return refs;
}

export function formatEvidenceRefs(value) {
  return parseEvidenceRefs(value).map((entry) => `${entry.kind}:${entry.ref_id}`).join('\n');
}

export function buildSliceAnnotationDisplayPlan(slice) {
  const findings = Array.isArray(slice?.findings)
    ? slice.findings
    : (Array.isArray(slice?.annotations) ? slice.annotations : []);
  const groupsMap = new Map();

  ANNOTATION_TYPES.forEach((type) => {
    groupsMap.set(type, { type, label: ANNOTATION_TYPE_LABELS[type], items: [] });
  });

  findings.forEach((finding) => {
    const type = String(finding?.type || '').trim();
    const text = String(finding?.text || '').trim();
    if (!ANNOTATION_TYPES.includes(type) || !text) return;
    groupsMap.get(type)?.items.push({ text });
  });

  const groups = ANNOTATION_TYPES
    .map((type) => groupsMap.get(type))
    .filter((group) => Array.isArray(group?.items) && group.items.length > 0);

  const count = groups.reduce((sum, group) => sum + group.items.length, 0);
  return { count, groups };
}

export function buildSliceListMetaSummary(slice) {
  const payload = slice && typeof slice === 'object' ? slice : {};
  const parts = [];

  if (payload.is_shared === true) parts.push('общая ссылка активна');

  const featureCount = normalizeCount(payload.feature_count);
  if (featureCount !== null) parts.push(`${featureCount} объектов`);

  const hasCanonicalFindingCount = payload.finding_count !== null && payload.finding_count !== undefined;
  const findingCount = normalizeCount(hasCanonicalFindingCount ? payload.finding_count : payload.annotation_count);
  if (findingCount !== null) parts.push(`${hasCanonicalFindingCount ? 'findings' : 'ann'}: ${findingCount}`);
  if (payload.evidence_state === 'missing') parts.push('evidence отсутствует');
  if (payload.conclusion_status === 'unresolved') parts.push('вопрос открыт');
  if (payload.content_status === 'incomplete') parts.push('нужно дополнить');

  const compactRange = buildCompactTimeRangeSummary(payload.saved_view?.time_range || payload.time_range);
  if (compactRange) parts.push(compactRange);

  const stamp = String(payload.updated_at || payload.created_at || '').trim();
  if (stamp) parts.push(stamp.slice(0, 10));

  return parts.join(' · ');
}

export function buildResearchSlicePayload({
  title,
  description = '',
  researchQuestion,
  selectionRationale,
  evidenceInput = '',
  evidenceRefs,
  selectedFeatureId,
  selectedFeatureIds = [],
  annotationInputs = {},
  conclusionStatus = 'unresolved',
  conclusion = '',
  uncertaintyNotes = '',
  timeRange,
  map,
  enabledLayerIds = [],
  activeQuickLayerIds = [],
  filterState = {},
  contentVersion = 1
} = {}) {
  const normalizedTitle = String(title || '').trim();
  if (!normalizedTitle) {
    throw new Error('Title is required to save a research slice.');
  }

  const normalizedQuestion = String(researchQuestion || normalizedTitle).trim();
  if (!normalizedQuestion) throw new Error('Research question is required.');
  const normalizedDescription = String(description || '').trim();
  const normalizedRationale = String(
    selectionRationale || normalizedDescription || 'Selection rationale was not captured.'
  ).trim();
  if (!normalizedRationale) throw new Error('Selection rationale is required.');

  const featureIds = [...new Set((Array.isArray(selectedFeatureIds) ? selectedFeatureIds : [])
    .map((id) => String(id || '').trim()).filter(Boolean))];
  const featureId = String(selectedFeatureId || '').trim();
  if (!featureIds.length && featureId) featureIds.push(featureId);
  if (!featureIds.length) {
    throw new Error('Select a map object before saving a research slice.');
  }
  const primaryFeatureId = featureId || featureIds[0];

  const start = Number(timeRange?.start);
  const end = Number(timeRange?.end);
  if (!Number.isFinite(start) || !Number.isFinite(end)) {
    throw new Error('Invalid time range for research slice.');
  }

  const center = map?.getCenter?.();
  const lng = Number(center?.lng);
  const lat = Number(center?.lat);
  const zoom = Number(map?.getZoom?.());
  if (!Number.isFinite(lng) || !Number.isFinite(lat) || !Number.isFinite(zoom)) {
    throw new Error('Map view is not ready for research slice save.');
  }

  const findings = buildSliceFindings(annotationInputs);
  const normalizedEvidenceRefs = parseEvidenceRefs(evidenceRefs ?? evidenceInput);
  const normalizedConclusionStatus = conclusionStatus === 'concluded' ? 'concluded' : 'unresolved';
  const normalizedConclusion = String(conclusion || '').trim();
  if (normalizedConclusionStatus === 'concluded' && !normalizedConclusion) {
    throw new Error('Conclusion text is required when the research is marked concluded.');
  }

  const normalizedTimeRange = {
    start: Math.trunc(start),
    end: Math.trunc(end),
    mode: timeRange?.mode === 'point' ? 'point' : 'range'
  };
  const normalizedViewState = {
    center: [lng, lat],
    zoom,
    enabled_layer_ids: [...new Set((Array.isArray(enabledLayerIds) ? enabledLayerIds : [])
      .map((id) => String(id || '').trim()).filter(Boolean))],
    active_quick_layer_ids: [...new Set((Array.isArray(activeQuickLayerIds) ? activeQuickLayerIds : [])
      .map((id) => String(id || '').trim()).filter(Boolean))],
    selected_feature_id: primaryFeatureId
  };
  const savedView = {
    time_range: normalizedTimeRange,
    view_state: normalizedViewState,
    filter_state: filterState && typeof filterState === 'object' ? filterState : {},
    comparison_feature_ids: featureIds
  };

  return {
    title: normalizedTitle,
    description: normalizedDescription,
    research_question: normalizedQuestion,
    selection_rationale: normalizedRationale,
    feature_refs: featureIds.map((id) => ({ feature_id: id })),
    evidence_state: normalizedEvidenceRefs.length ? 'supported' : 'missing',
    evidence_refs: normalizedEvidenceRefs,
    findings,
    conclusion_status: normalizedConclusionStatus,
    conclusion: normalizedConclusion,
    uncertainty_notes: String(uncertaintyNotes || '').trim(),
    saved_view: savedView,
    schema_version: SCHEMA_VERSION,
    content_version: Math.max(1, Math.trunc(Number(contentVersion) || 1)),
    // Compatibility mirrors for one rolling-deployment cycle.
    time_range: normalizedTimeRange,
    view_state: normalizedViewState,
    annotations: findings
  };
}

export function normalizeSliceForRestore(slice) {
  const payload = slice && typeof slice === 'object' ? slice : {};
  const savedView = payload.saved_view && typeof payload.saved_view === 'object' ? payload.saved_view : {};
  const timeRange = savedView.time_range && typeof savedView.time_range === 'object'
    ? savedView.time_range
    : (payload.time_range && typeof payload.time_range === 'object' ? payload.time_range : {});
  const viewState = savedView.view_state && typeof savedView.view_state === 'object'
    ? savedView.view_state
    : (payload.view_state && typeof payload.view_state === 'object' ? payload.view_state : {});

  const start = Number(timeRange.start);
  const end = Number(timeRange.end);
  const mode = timeRange.mode === 'point' ? 'point' : 'range';
  const featureIds = (Array.isArray(payload.feature_refs) ? payload.feature_refs : [])
    .map((entry) => String(entry?.feature_id || '').trim())
    .filter(Boolean);
  const uniqueFeatureIds = [...new Set(featureIds)];
  const selectedFeatureId = String(viewState.selected_feature_id || '').trim() || uniqueFeatureIds[0] || null;
  const center = Array.isArray(viewState.center) ? viewState.center : [];
  const lng = Number(center[0]);
  const lat = Number(center[1]);
  const zoom = Number(viewState.zoom);

  return {
    id: String(payload.id || '').trim(),
    title: String(payload.title || '').trim(),
    researchQuestion: String(payload.research_question || payload.title || '').trim(),
    selectionRationale: String(payload.selection_rationale || payload.description || '').trim(),
    evidenceState: payload.evidence_state === 'supported' ? 'supported' : 'missing',
    evidenceRefs: parseEvidenceRefs(payload.evidence_refs || []),
    findings: Array.isArray(payload.findings) ? payload.findings : (Array.isArray(payload.annotations) ? payload.annotations : []),
    conclusionStatus: payload.conclusion_status === 'concluded' ? 'concluded' : 'unresolved',
    conclusion: String(payload.conclusion || '').trim(),
    uncertaintyNotes: String(payload.uncertainty_notes || '').trim(),
    contentVersion: Math.max(1, Math.trunc(Number(payload.content_version) || 1)),
    start: Number.isFinite(start) ? start : null,
    end: Number.isFinite(end) ? end : null,
    mode,
    featureIds: uniqueFeatureIds,
    center: Number.isFinite(lng) && Number.isFinite(lat) ? [lng, lat] : null,
    zoom: Number.isFinite(zoom) ? zoom : null,
    enabledLayerIds: (Array.isArray(viewState.enabled_layer_ids) ? viewState.enabled_layer_ids : [])
      .map((id) => String(id || '').trim()).filter(Boolean),
    activeQuickLayerIds: (Array.isArray(viewState.active_quick_layer_ids) ? viewState.active_quick_layer_ids : [])
      .map((id) => String(id || '').trim()).filter(Boolean),
    filterState: savedView.filter_state && typeof savedView.filter_state === 'object' ? savedView.filter_state : {},
    comparisonFeatureIds: (Array.isArray(savedView.comparison_feature_ids) ? savedView.comparison_feature_ids : uniqueFeatureIds)
      .map((id) => String(id || '').trim()).filter(Boolean),
    selectedFeatureId,
    featureCount: uniqueFeatureIds.length
  };
}

export async function listResearchSlices() {
  const response = await fetchWithAuth(BASE_PATH, { method: 'GET' });
  if (!response.ok) throw await buildApiError(response, 'Failed to load research slices.');
  return await response.json();
}

export async function getResearchSlice(sliceId) {
  const response = await fetchWithAuth(`${BASE_PATH}/${encodeURIComponent(sliceId)}`, { method: 'GET' });
  if (!response.ok) throw await buildApiError(response, 'Failed to open research slice.');
  return await response.json();
}

export async function createResearchSlice(payload) {
  const response = await fetchWithAuth(BASE_PATH, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw await buildApiError(response, 'Failed to save research slice.');
  return await response.json();
}

export async function updateResearchSlice(sliceId, payload) {
  const response = await fetchWithAuth(`${BASE_PATH}/${encodeURIComponent(sliceId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw await buildApiError(response, 'Failed to update research slice.');
  return await response.json();
}

export async function deleteResearchSlice(sliceId) {
  const response = await fetchWithAuth(`${BASE_PATH}/${encodeURIComponent(sliceId)}`, { method: 'DELETE' });
  if (!response.ok) throw await buildApiError(response, 'Failed to delete research slice.');
}

export async function createResearchSliceShare(sliceId) {
  const response = await fetchWithAuth(`${BASE_PATH}/${encodeURIComponent(sliceId)}/share`, { method: 'POST' });
  if (!response.ok) throw await buildApiError(response, 'Failed to create a read-only share link.');
  return await response.json();
}

export async function revokeResearchSliceShare(sliceId) {
  const response = await fetchWithAuth(`${BASE_PATH}/${encodeURIComponent(sliceId)}/share`, { method: 'DELETE' });
  if (!response.ok) throw await buildApiError(response, 'Failed to revoke the share link.');
}

export async function getSharedResearchSlice(shareToken) {
  const token = String(shareToken || '').trim();
  const response = await fetchPublicApi('/api/public/research-slices/shared', {
    method: 'GET',
    headers: { 'X-ARTEMIS-Share-Token': token }
  });
  if (!response.ok) throw await buildApiError(response, 'Shared research slice is unavailable.', { logLevel: 'warn' });
  return await response.json();
}

export function getSharedSliceTokenFromLocation(locationLike = window.location) {
  const rawHash = String(locationLike?.hash || '').replace(/^#/, '');
  const token = new URLSearchParams(rawHash).get('share');
  return String(token || '').trim();
}

export function buildResearchSliceShareUrl(shareToken, locationLike = window.location) {
  const token = String(shareToken || '').trim();
  if (!token) throw new Error('Share token is required.');
  const url = new URL(String(locationLike?.href || locationLike || ''), window.location.href);
  url.hash = new URLSearchParams({ share: token }).toString();
  return url.href;
}
