  // Стили карты
  const MAP_STYLES = {
    dark:    'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    light:   'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
    voyager: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
  };


  // ── ИНИЦИАЛИЗАЦИЯ КАРТЫ ───────────────────────────────────
  const map = new maplibregl.Map({
    container: 'map',
    style:     MAP_STYLES.dark,
    center:    [12, 48],
    zoom:      4,
  });
  map.addControl(new maplibregl.NavigationControl(), 'top-right');
  map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-right');
