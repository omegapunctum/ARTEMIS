(() => {
  const DEFAULT_PROBE_TIMEOUT_MS = 3500;
  const source = window.ARTEMIS_DEPLOYMENT_CONFIG && typeof window.ARTEMIS_DEPLOYMENT_CONFIG === 'object'
    ? window.ARTEMIS_DEPLOYMENT_CONFIG
    : {};
  const requestedCapabilities = source.capabilities && typeof source.capabilities === 'object'
    ? source.capabilities
    : {};

  function normalizeApiBase(value) {
    return String(value || '').trim().replace(/\/+$/, '');
  }

  function disabledCapabilities() {
    return {
      explore: true,
      backend: false,
      account: false,
      slices: false,
      stories: false
    };
  }

  function enabledCapabilities() {
    return {
      explore: true,
      backend: true,
      account: requestedCapabilities.account === true,
      slices: requestedCapabilities.slices === true,
      stories: requestedCapabilities.stories === true
    };
  }

  function publishRuntimeState(status, capabilities, error = '') {
    const nextCapabilities = Object.freeze({ ...capabilities });
    const nextStatus = Object.freeze({
      apiBase,
      status,
      error: String(error || ''),
      checkedAt: new Date().toISOString()
    });
    window.ARTEMIS_CAPABILITIES = nextCapabilities;
    window.ARTEMIS_RUNTIME_STATUS = nextStatus;
    window.dispatchEvent?.(new CustomEvent('artemis:runtime-capabilities-changed', {
      detail: { capabilities: nextCapabilities, runtime: nextStatus }
    }));
    return nextStatus;
  }

  const apiBase = normalizeApiBase(source.apiBase);
  const timeoutMs = Math.max(500, Number(source.probeTimeoutMs) || DEFAULT_PROBE_TIMEOUT_MS);
  window.ARTEMIS_API_BASE = apiBase;
  window.ARTEMIS_CAPABILITIES = Object.freeze(disabledCapabilities());
  window.ARTEMIS_RUNTIME_STATUS = Object.freeze({
    apiBase,
    status: apiBase ? 'checking' : 'unconfigured',
    error: '',
    checkedAt: null
  });

  if (!apiBase) {
    window.ARTEMIS_RUNTIME_READY = Promise.resolve(
      publishRuntimeState('unconfigured', disabledCapabilities())
    );
    return;
  }

  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort('runtime-probe-timeout'), timeoutMs);
  window.ARTEMIS_RUNTIME_READY = fetch(`${apiBase}/health`, {
    method: 'GET',
    credentials: 'omit',
    cache: 'no-store',
    headers: { Accept: 'application/json' },
    signal: controller.signal
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Health probe returned HTTP ${response.status}.`);
      }
      return publishRuntimeState('available', enabledCapabilities());
    })
    .catch((error) => {
      const message = error?.name === 'AbortError'
        ? 'API health probe timed out.'
        : (error?.message || 'API health probe failed.');
      console.info('ARTEMIS public API unavailable; backend capabilities remain disabled.', {
        apiBase,
        message
      });
      return publishRuntimeState('unavailable', disabledCapabilities(), message);
    })
    .finally(() => window.clearTimeout(timeoutId));
})();
