(() => {
  'use strict';
  const MIN = 91, MAX = 1519;
  const MOBILE_QUERY = '(max-width:640px), (max-width:960px) and (max-height:500px)';
  const bounds = value => Math.max(MIN, Math.min(MAX, Math.round(value)));
  function temporal(state) { return {mode:state.mode,startYear:state.startYear,endYear:state.endYear,cursorYear:state.cursorYear}; }
  function stepDraft(draft, field, delta) {
    if (!['startYear','endYear','cursorYear'].includes(field) || !Number.isFinite(delta)) return {...draft};
    const next = {...draft,[field]:bounds(draft[field] + delta)};
    if (field === 'startYear') next.startYear = Math.min(next.startYear,next.endYear);
    if (field === 'endYear') next.endYear = Math.max(next.endYear,next.startYear);
    return next;
  }
  function commitDraft(draft) { return draft.mode === 'scrub' ? {cursorYear:draft.cursorYear} : {startYear:draft.startYear,endYear:draft.endYear}; }
  function signature(state) { return JSON.stringify(temporal(state)); }
  const words = {
    en:{layers:'Layers',records:'Search',settings:'View',close:'Close panel',expand:'Expand calendar',collapse:'Collapse calendar',apply:'Apply',cancel:'Cancel',sources:'Map sources',start:'Interval start year CE',end:'Interval end year CE',cursor:'Current year CE',previous:'Previous year',next:'Next year',pending:'Pending dates',ce:'CE'},
    ru:{layers:'Слои',records:'Поиск',settings:'Вид',close:'Закрыть панель',expand:'Развернуть календарь',collapse:'Свернуть календарь',apply:'Применить',cancel:'Отменить',sources:'Источники карты',start:'Начальный год интервала, н. э.',end:'Конечный год интервала, н. э.',cursor:'Текущий год, н. э.',previous:'Предыдущий год',next:'Следующий год',pending:'Даты не применены',ce:'н. э.'}
  };
  function mount({runtime,applyState,layout}) {
    const byId = id => document.getElementById(id), header = byId('workspace-header'), dock = byId('time-dock');
    const mobile = () => window.matchMedia(MOBILE_QUERY).matches;
    let draft = temporal(runtime.state), canonical = signature(runtime.state), dirty = false, selected = null;
    let headerReturn = null, expanded = false;
    const wheels = [['mobile-range-start','startYear','start'],['mobile-range-end','endYear','end'],['mobile-cursor-year','cursorYear','cursor']];
    const w = key => words[runtime.state.language === 'ru' ? 'ru' : 'en'][key];
    function headerPanel(panel, restore = false) {
      if (!panel && restore && headerReturn) headerReturn.focus();
      header.dataset.headerPanel = panel || '';
      if (byId('header-panel-title')) byId('header-panel-title').textContent = panel ? w(panel) : '';
      for (const key of ['layers','records','settings']) byId(`mobile-${key}`).setAttribute('aria-expanded',String(panel === key));
      layout();
    }
    function setExpanded(value) {
      expanded = value; dock.dataset.expanded = String(value);
      byId('dock-toggle').setAttribute('aria-expanded',String(value));
      byId('dock-toggle').setAttribute('aria-label',w(value ? 'collapse' : 'expand'));
      byId('dock-toggle-label').textContent = w(value ? 'collapse' : 'expand');
      layout();
    }
    function cancel() { draft = temporal(runtime.state); dirty = false; render(); }
    function stage(field, delta) {
      if (!runtime.ready || !mobile()) return;
      draft = stepDraft(draft,field,delta); dirty = signature(draft) !== canonical;
      setExpanded(true); render();
    }
    function apply() {
      if (!runtime.ready || !dirty) return;
      const patch = commitDraft(draft); dirty = false; applyState(patch);
      draft = temporal(runtime.state); canonical = signature(runtime.state); render();
    }
    function render() {
      const nextSignature = signature(runtime.state);
      // Incumbent sliders, presets, URL navigation and modes remain canonical.
      // Their committed changes discard a staged wheel edit; language does not.
      if (nextSignature !== canonical) { canonical = nextSignature; draft = temporal(runtime.state); dirty = false; }
      for (const key of ['layers','records','settings']) byId(`mobile-${key}`).textContent = w(key);
      if (byId('header-panel-title')) byId('header-panel-title').textContent = header.dataset.headerPanel ? w(header.dataset.headerPanel) : '';
      byId('header-close').setAttribute('aria-label',w('close')); byId('header-close').textContent = w('close');
      byId('attribution-toggle').textContent = w('sources');
      byId('mobile-apply').textContent = w('apply'); byId('mobile-cancel').textContent = w('cancel');
      byId('mobile-apply').disabled = !runtime.ready || !dirty; byId('mobile-cancel').disabled = !dirty;
      dock.dataset.draft = String(dirty);
      for (const [id,field,label] of wheels) {
        const wheel = byId(id), value = draft[field];
        const min = field === 'endYear' ? draft.startYear : MIN, max = field === 'startYear' ? draft.endYear : MAX;
        wheel.setAttribute('aria-label',w(label)); wheel.setAttribute('aria-valuemin',String(min)); wheel.setAttribute('aria-valuemax',String(max)); wheel.setAttribute('aria-valuenow',String(value));
        wheel.setAttribute('aria-valuetext',`${value} ${w('ce')}`); wheel.setAttribute('aria-disabled',String(!runtime.ready)); wheel.tabIndex = runtime.ready ? 0 : -1;
        wheel.querySelector('.wheel-value').textContent = String(value);
        for (const [selector,delta] of [['.wheel-prev',-1],['.wheel-next',1]]) {
          const neighbor = wheel.querySelector(selector); neighbor.textContent = value + delta >= min && value + delta <= max ? String(value + delta) : '—';
          neighbor.setAttribute('aria-hidden','true');
        }
      }
      const dates = draft.mode === 'scrub' ? String(draft.cursorYear) : `${draft.startYear}–${draft.endYear}`;
      byId('mobile-time-summary').textContent = `${dates} ${w('ce')}${dirty ? ` · ${w('pending')}` : ''}`;
      // The timeline previews the same staged dates as its adjacent wheels.
      // Only Apply (or an incumbent slider change) can update canonical state.
      if (mobile() || !dirty) {
        byId('range-start-handle').value = draft.startYear; byId('range-end-handle').value = draft.endYear;
        byId('time-cursor').value = draft.cursorYear;
      }
      setExpanded(expanded);
    }
    for (const key of ['layers','records','settings']) {
      const button = byId(`mobile-${key}`);
      button.addEventListener('click',() => { headerReturn = button; headerPanel(header.dataset.headerPanel === key ? null : key); });
    }
    byId('header-close').addEventListener('click',() => headerPanel(null,true));
    byId('attribution-toggle').addEventListener('click',() => { const app = byId('app'); const value = app.dataset.attributionOpen !== 'true'; app.dataset.attributionOpen = String(value); byId('attribution-toggle').setAttribute('aria-expanded',String(value)); layout(); });
    byId('dock-toggle').addEventListener('click',event => { if (event.detail && suppressDockClick) { suppressDockClick = false; return; } setExpanded(!expanded); });
    byId('mobile-apply').addEventListener('click',apply); byId('mobile-cancel').addEventListener('click',cancel);
    for (const [id,field] of wheels) {
      const wheel = byId(id);
      wheel.addEventListener('click',() => { if (runtime.ready) setExpanded(true); });
      wheel.addEventListener('keydown',event => {
        const keys = {ArrowUp:1,ArrowDown:-1,PageUp:10,PageDown:-10,Home:MIN-draft[field],End:MAX-draft[field]};
        if (Object.hasOwn(keys,event.key)) { event.preventDefault(); event.stopPropagation(); stage(field,keys[event.key]); }
        else if (event.key === 'Enter') { event.preventDefault(); apply(); }
      });
      wheel.addEventListener('wheel',event => { if (!mobile() || !runtime.ready || !event.deltaY) return; event.preventDefault(); event.stopPropagation(); stage(field,event.deltaY > 0 ? 1 : -1); },{passive:false});
      let drag = null;
      wheel.addEventListener('pointerdown',event => {
        if (!mobile() || !runtime.ready || event.button !== 0 || event.target.closest('button')) return;
        event.preventDefault(); event.stopPropagation(); wheel.focus(); setExpanded(true);
        drag = {pointer:event.pointerId,y:event.clientY,draft:{...draft},dirty}; wheel.setPointerCapture(event.pointerId);
      });
      wheel.addEventListener('pointermove',event => {
        if (!drag || drag.pointer !== event.pointerId) return;
        event.preventDefault(); event.stopPropagation();
        draft = stepDraft(drag.draft,field,Math.trunc((drag.y-event.clientY)/18)); dirty = signature(draft) !== canonical; render();
      });
      wheel.addEventListener('pointerup',event => { if (drag?.pointer === event.pointerId) { drag = null; if (wheel.hasPointerCapture(event.pointerId)) wheel.releasePointerCapture(event.pointerId); } });
      wheel.addEventListener('pointercancel',event => { if (drag?.pointer === event.pointerId) { draft = drag.draft; dirty = drag.dirty; drag = null; render(); } });
      wheel.addEventListener('lostpointercapture',event => { if (drag?.pointer === event.pointerId) { draft = drag.draft; dirty = drag.dirty; drag = null; render(); } });
    }
    let dockDrag = null, suppressDockClick = false;
    const handle = byId('dock-toggle');
    handle.addEventListener('pointerdown',event => { if (!mobile() || event.button !== 0) return; dockDrag = {pointer:event.pointerId,y:event.clientY}; handle.setPointerCapture(event.pointerId); });
    handle.addEventListener('pointerup',event => {
      if (!dockDrag || dockDrag.pointer !== event.pointerId) return;
      const delta = event.clientY-dockDrag.y; dockDrag = null;
      if (Math.abs(delta) >= 24) { suppressDockClick = true; setTimeout(() => { suppressDockClick = false; },0); setExpanded(delta < 0); }
      if (handle.hasPointerCapture(event.pointerId)) handle.releasePointerCapture(event.pointerId);
    });
    handle.addEventListener('pointercancel',() => { dockDrag = null; suppressDockClick = false; });
    document.addEventListener('keydown',event => {
      if (!mobile() || event.key !== 'Escape') return;
      if (dirty) cancel();
      else if (header.dataset.headerPanel) headerPanel(null,true);
      else if (expanded) { setExpanded(false); handle.focus(); }
      else return;
      event.preventDefault(); event.stopImmediatePropagation();
    },true);
    window.matchMedia(MOBILE_QUERY).addEventListener?.('change',event => {
      if (event.matches) return;
      cancel(); headerPanel(null); setExpanded(false);
      byId('app').dataset.attributionOpen = 'false'; byId('attribution-toggle').setAttribute('aria-expanded','false');
    });
    function selectionChanged(id) { if (id && id !== selected && mobile()) headerPanel(null); selected = id; }
    return {render,selectionChanged};
  }
  const api = Object.freeze({MIN,MAX,MOBILE_QUERY,temporal,stepDraft,commitDraft,mount});
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof window !== 'undefined') window.ARTEMIS_MOBILE = api;
})();
