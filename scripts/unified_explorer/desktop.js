(() => {
  'use strict';
  const MOBILE_QUERY = '(max-width:640px), (max-width:960px) and (max-height:500px)';
  function mount({runtime,layout}) {
    const byId = id => document.getElementById(id), media = window.matchMedia(MOBILE_QUERY);
    const records = byId('desktop-records-body'), inspector = byId('inspector');
    const moves = [
      [document.querySelector('.record-search'),byId('desktop-search')],
      [byId('search-status'),byId('desktop-chooser')],
      [document.querySelector('.record-picker'),byId('desktop-chooser')],
      [byId('search-hint'),byId('desktop-chooser')],
      [byId('layer-controls'),byId('desktop-layer-body')],
      [byId('layer-status'),byId('desktop-layer-body')]
    ].map(([element,target]) => {
      const anchor = document.createComment('desktop control origin');
      element.before(anchor); return {element,target,anchor};
    });
    const select = byId('record-select'), originalSize = select.getAttribute('size');
    const originalLabels = new WeakMap();
    let collapsedRecords = false, collapsedInspector = false, selected = null;
    const ru = () => runtime.state.language === 'ru';
    function render() {
      // Short display labels retain the full native label as a tooltip and
      // restore it on mobile. Values, membership and selection stay canonical.
      for (const option of select.options) {
        if (!originalLabels.has(option)) originalLabels.set(option,option.textContent);
        const item = runtime.registry.get(option.value);
        if (!media.matches && item) {
          option.title = originalLabels.get(option);
          const date = item.interval ? (item.interval.start === item.interval.end ? `${item.interval.start}` : `${item.interval.start}–${item.interval.end}`) : ru() ? 'время неизвестно' : 'time unknown';
          option.textContent = `${item.labels?.[runtime.state.language] || item.label} · ${date}`;
        } else { option.textContent = originalLabels.get(option); option.removeAttribute('title'); }
      }
      byId('records-toggle').textContent = ru() ? collapsedRecords ? 'Развернуть записи' : 'Свернуть записи' : collapsedRecords ? 'Expand records' : 'Collapse records';
      byId('records-toggle').setAttribute('aria-expanded',String(!collapsedRecords));
      byId('inspector-toggle').textContent = ru() ? collapsedInspector ? 'Развернуть' : 'Свернуть' : collapsedInspector ? 'Expand' : 'Collapse';
      byId('inspector-toggle').setAttribute('aria-expanded',String(!collapsedInspector));
      records.hidden = collapsedRecords;
      inspector.dataset.desktopCollapsed = String(collapsedInspector && !media.matches);
    }
    function responsive() {
      const active = document.activeElement;
      const inInspector = inspector.contains(active);
      const inLayers = byId('desktop-layers').contains(active) || byId('layer-controls').contains(active) || active?.id === 'mobile-layers';
      const inRecords = moves.some(({element}) => element.contains(active)) ||
        ['records-toggle','mobile-records','header-close'].includes(active?.id);

      for (const {element,target,anchor} of moves) {
        if (media.matches) anchor.after(element); else target.append(element);
      }
      if (media.matches) {
        if (originalSize === null) select.removeAttribute('size'); else select.setAttribute('size',originalSize);
      } else select.setAttribute('size','7');
      render(); layout();
      // Reparenting can blur native controls; a breakpoint can also hide their
      // previous owner. Restore only keyboard focus, never selection or panels.
      if (active && active !== document.body) {
        const visible = node => node && !node.disabled && node.checkVisibility({checkVisibilityCSS:true});
        const fallback = media.matches
          ? byId(inInspector ? 'close-details' : inLayers ? 'mobile-layers' : inRecords ? 'mobile-records' : 'mobile-settings')
          : byId(inInspector ? 'inspector-toggle' : inLayers || inRecords ? 'records-toggle' : 'language-en');
        if (visible(active)) active.focus({preventScroll:true});
        else if (visible(fallback)) fallback.focus({preventScroll:true});
      }
    }
    byId('records-toggle').addEventListener('click',() => {
      byId('records-toggle').focus(); collapsedRecords = !collapsedRecords; render(); layout();
    });
    byId('inspector-toggle').addEventListener('click',() => {
      byId('inspector-toggle').focus(); collapsedInspector = !collapsedInspector; render(); layout();
    });
    byId('desktop-layers').addEventListener('toggle',layout);
    media.addEventListener('change',responsive);
    responsive();
    return {render,selectionChanged(id) {
      if (selected !== id) { selected = id; collapsedInspector = false; render(); }
    }};
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {MOBILE_QUERY,mount};
  if (typeof window !== 'undefined') window.ARTEMIS_DESKTOP = Object.freeze({mount});
})();
