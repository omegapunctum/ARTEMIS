(() => {
  'use strict';
  const host = document.getElementById('startup-status');
  let phase = 'scripts', timer;
  const labels = {scripts:'Loading workspace scripts…',data:'Loading local workspace data…',map:'Starting the globe…'};
  function fail(message) {
    if (document.documentElement.dataset.artemisBoot === 'failed') return;
    clearTimeout(timer);
    document.documentElement.dataset.artemisBoot = 'failed';
    host.hidden = false;
    host.textContent = `ARTEMIS could not start: ${message}. Reload this page after checking the server window.`;
  }
  window.ARTEMIS_STARTUP = Object.freeze({
    phase(value) {if (document.documentElement.dataset.artemisBoot === 'failed') return; phase = value; host.textContent = labels[value] || value;},
    fail,
    ready() {if (document.documentElement.dataset.artemisBoot === 'failed') return; clearTimeout(timer); document.documentElement.dataset.artemisBoot = 'ready'; host.hidden = true;}
  });
  document.documentElement.dataset.artemisBoot = 'loading';
  window.addEventListener('error',event => {
    if (document.documentElement.dataset.artemisBoot === 'ready') return;
    if (event.target?.tagName === 'SCRIPT') fail(`local script unavailable: ${event.target.getAttribute('src')}`);
    else if (event.message) fail(event.message);
  },true);
  window.addEventListener('unhandledrejection',event => {
    if (document.documentElement.dataset.artemisBoot !== 'ready') fail(event.reason?.message || String(event.reason));
  });
  timer = setTimeout(() => {
    host.hidden = false;
    host.textContent = `ARTEMIS is still waiting: ${labels[phase] || phase} If this persists, send a screenshot of this message.`;
  },20000);
})();
