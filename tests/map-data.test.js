const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const {
  buildMapPayload
} = require('../scripts/map_data');

function date(value) {
  return { format(pattern) { return pattern === 'YYYY' ? value.slice(0, 4) : value; } };
}

test('map payload joins posts to valid places and sorts papers newest first', () => {
  const posts = [
    { title: 'Older', path: 'article/older/', date: date('2025-01-01'), venue_type: '会议', venue_name: 'RecSys', venue_city: 'Bari' },
    { title: 'Newest', path: 'article/newest/', date: date('2026-09-01'), venue_type: '会议', venue_name: 'SIGIR', venue_city: 'Padua' },
    { title: 'Missing city', path: 'article/missing/', date: date('2026-10-01'), venue_type: '会议', venue_name: 'KDD' },
    { title: 'Preprint', path: 'article/preprint/', date: date('2026-10-02'), venue_type: 'arXiv预印本', venue_name: 'arXiv' }
  ];
  const places = [
    { id: 'bari', name: 'Bari', wgs84: [16.8719, 41.1171], image: '/images/map/bari.jpg', description: 'Adriatic city' },
    { id: 'padua', name: 'Padua', wgs84: [11.8768, 45.4064], image: '/images/map/padua.jpg', description: 'University city' }
  ];

  const payload = buildMapPayload(posts, places, 0.6);

  assert.equal(payload.meta.total_papers, 4);
  assert.equal(payload.meta.eligible_papers, 3);
  assert.equal(payload.meta.located_papers, 2);
  assert.equal(payload.meta.coverage, 2 / 3);
  assert.equal(payload.meta.enabled, true);
  assert.deepEqual(payload.papers.map(item => item.title), ['Newest', 'Older']);
  assert.ok(payload.places.every(place => place.image.startsWith('/images/map/')));
  assert.equal(payload.links.length, 2);
  assert.deepEqual(payload.unlocated.map(item => item.title), ['Preprint', 'Missing city']);
  assert.equal(payload.meta.unlocated_papers, 2);
});

test('map payload derives a readable introduction from article content', () => {
  const posts = [{
    slug: 'real-intro', title: 'Real intro', path: 'article/real-intro/', date: date('2026-01-01'),
    venue_type: '会议',
    _content: '> 论文：[arXiv](https://arxiv.org/abs/1234.56789)\n\n## 背景\n\n这项工作研究推荐系统中的长尾问题，并解释为什么传统排序方法会失效。\n\n第二段。'
  }];
  const places = [{ id: 'bari', name: 'Bari', wgs84: [16, 41], image: '/images/map/bari.jpg', description: 'Bari' }];
  const assignments = [{ paper_id: 'real-intro', place_id: 'bari', location_type: 'school', location_label: 'University of Bari' }];

  const payload = buildMapPayload(posts, places, 0, assignments);

  assert.match(payload.papers[0].description, /这项工作研究推荐系统中的长尾问题/);
  assert.doesNotMatch(payload.papers[0].description, /<[^>]+>/);
});

test('coverage gate remains closed below sixty percent', () => {
  const posts = [
    { title: 'Located', path: 'article/located/', date: date('2026-01-01'), venue_type: '会议', venue_city: 'Bari' },
    { title: 'Missing one', path: 'article/missing-1/', date: date('2026-01-02'), venue_type: '会议' },
    { title: 'Missing two', path: 'article/missing-2/', date: date('2026-01-03'), venue_type: '会议' },
    { title: 'Not eligible', path: 'article/preprint/', date: date('2026-01-04'), venue_type: 'arXiv预印本' }
  ];
  const places = [{ id: 'bari', name: 'Bari', wgs84: [16, 41], image: '/images/map/bari.jpg', description: 'Bari' }];

  assert.equal(buildMapPayload(posts, places, 0.6).meta.enabled, false);
});

test('map page opens as a full color map with a transparent floating legend', () => {
  const root = path.resolve(__dirname, '..');
  const page = fs.readFileSync(path.join(root, 'source/map/index.md'), 'utf8');
  const script = fs.readFileSync(path.join(root, 'source/js/paper-map.js'), 'utf8');
  assert.doesNotMatch(script, /cache:\s*['"]no-store['"]/);
  const css = fs.readFileSync(path.join(root, 'source/css/paper-map.css'), 'utf8');

  assert.match(page, /id="paper-map"/);
  assert.match(page, /leaflet@1\.9\.4/);
  assert.doesNotMatch(page, /map-intro|map-metrics|map-unlocated/);
  assert.match(page, /class="map-legend"/);
  assert.match(page, /class="map-detail"[^>]*aria-hidden="true"/);
  assert.match(script, /map_data\.json/);
  assert.match(script, /meta\.enabled/);
  assert.doesNotMatch(script, /World_Physical_Map\/MapServer\/tile/);
  assert.match(script, /primary:\s*\{[\s\S]*World_Topo_Map/);
  assert.match(script, /fallback:\s*\{[\s\S]*tile\.openstreetmap\.org/);
  assert.match(script, /__PAPER_MAP_CONFIG__/);
  assert.match(script, /function useFallback/);
  assert.match(script, /openstreetmap\.org\/copyright/);
  assert.match(script, /tileerror/);
  assert.match(script, /L\.tileLayer/);
  assert.match(script, /L\.divIcon/);
  assert.match(script, /html:\s*'<span class="paper-map-marker/);
  assert.match(script, /map\.on\('click', function/);
  assert.match(script, /ignoreNextMapClick/);
  assert.doesNotMatch(script, /L\.DomEvent\.disableClickPropagation/);
  assert.match(script, /bubblingMouseEvents:\s*false/);
  assert.match(script, /classList\.add\('is-open'\)/);
  assert.match(script, /classList\.remove\('is-open'\)/);
  assert.doesNotMatch(script, /bindPopup|openPopup|updateMetrics|renderUnlocated/);
  assert.match(css, /@media\s*\(max-width:\s*820px\)/);
  assert.match(css, /\.map-status--error/);
  assert.doesNotMatch(css, /\.leaflet-tile-pane\s*\{[^}]*filter:/s);
  assert.match(css, /\.map-legend\s*\{[^}]*position:\s*absolute/s);
  assert.match(css, /\.map-legend\s*\{[^}]*right:/s);
  assert.match(css, /\.map-legend\s*\{[^}]*background:\s*transparent/s);
  assert.match(css, /\.map-legend\s*\{[^}]*border:\s*0/s);
  assert.match(css, /\.map-legend\s*\{[^}]*color:\s*#000/s);
  assert.match(css, /\.map-detail\.is-open/);
  assert.match(css, /font-family:\s*SimSun/);
});

test('the primary color basemap does not depend on a browser API key', () => {
  const root = path.resolve(__dirname, '..');
  const generatorPath = path.join(root, 'scripts/map_carto_config.js');
  const page = fs.readFileSync(path.join(root, 'source/map/index.md'), 'utf8');
  const script = fs.readFileSync(path.join(root, 'source/js/paper-map.js'), 'utf8');

  assert.equal(fs.existsSync(generatorPath), true);
  assert.match(page, /\/js\/map-carto-config\.js["']/);
  assert.doesNotMatch(script, /\?key=/);
  assert.match(script, /World_Topo_Map/);
  assert.doesNotMatch(script, /basemaps\.cartocdn\.com/);
  assert.doesNotMatch(page + script, /cb1_[A-Za-z0-9_]+/);
});

test('map navigation is present without waiting for an asynchronous coverage gate', () => {
  const config = fs.readFileSync(path.resolve(__dirname, '../_config.butterfly.yml'), 'utf8');
  assert.match(config, /论文足迹:\s*\/map\//);
  assert.doesNotMatch(config, /map-nav-gate\.js/);
});

test('resolved assignments preserve marker meaning and explanatory metadata', () => {
  const posts = [{
    slug: 'paper-one', title: 'Paper one', path: 'article/paper-one/', date: date('2026-05-01'),
    venue_type: '会议'
  }];
  const places = [{ id: 'beijing', name: 'Beijing', wgs84: [116.39, 39.9], image: '/images/map/beijing.jpg', description: 'Beijing' }];
  const assignments = [{
    paper_id: 'paper-one', place_id: 'beijing', location_type: 'school',
    location_label: 'Tsinghua University', source: 'affiliation_dictionary'
  }];

  const payload = buildMapPayload(posts, places, 0.6, assignments);

  assert.equal(payload.papers[0].location_type, 'school');
  assert.equal(payload.papers[0].location_label, 'Tsinghua University');
  assert.equal(payload.places[0].location_type, 'school');
  assert.match(payload.places[0].id, /school/);
  assert.equal(payload.meta.city_count, 1);
});

test('institutions in the same city share one semantic marker and paper list', () => {
  const posts = [
    { slug: 'hku-paper', title: 'HKU paper', path: 'article/hku-paper/', date: date('2026-02-01'), venue_type: '会议' },
    { slug: 'polyu-paper', title: 'PolyU paper', path: 'article/polyu-paper/', date: date('2026-01-01'), venue_type: '会议' }
  ];
  const places = [
    { id: 'hku', name: 'Hong Kong', city: 'Hong Kong', wgs84: [114.1378, 22.283], image: '/images/map/hong-kong.jpg',
      hover_text: '香港：繁华与竞争之地', city_images: ['/images/map/hong-kong.jpg', '/images/map/hong-kong-2.jpg'],
      institution: { name: 'HKU', description: 'Hong Kong university' }, description: 'Hong Kong' },
    { id: 'polyu', name: 'Hong Kong', city: 'Hong Kong', wgs84: [114.1796, 22.305], image: '/images/map/hong-kong.jpg',
      institution: { name: 'PolyU', description: 'Kowloon university' }, description: 'Hong Kong' }
  ];
  const assignments = [
    { paper_id: 'hku-paper', place_id: 'hku', location_type: 'school', location_label: 'HKU' },
    { paper_id: 'polyu-paper', place_id: 'polyu', location_type: 'school', location_label: 'PolyU' }
  ];

  const payload = buildMapPayload(posts, places, 0.6, assignments);

  assert.equal(payload.places.length, 1);
  assert.equal(payload.papers.length, 2);
  assert.equal(new Set(payload.papers.map(item => item.city_id)).size, 1);
  assert.equal(payload.places[0].papers.length, 2);
  assert.equal(payload.places[0].institutions.length, 2);
  assert.deepEqual(payload.places[0].city_images, ['/images/map/hong-kong.jpg', '/images/map/hong-kong-2.jpg']);
  assert.equal(payload.places[0].hover_text, '香港：繁华与竞争之地');
});

test('map UI defines distinct visual markers for five location meanings', () => {
  const script = fs.readFileSync(path.resolve(__dirname, '../source/js/paper-map.js'), 'utf8');
  const css = fs.readFileSync(path.resolve(__dirname, '../source/css/paper-map.css'), 'utf8');
  ['school', 'company', 'publisher', 'virtual', 'venue'].forEach(type => {
    assert.match(script, new RegExp(type));
    assert.match(css, new RegExp('paper-map-marker--' + type));
  });
});

test('map UI uses one hover card, managed carousel lifecycle, and optional clustering', () => {
  const root = path.resolve(__dirname, '..');
  const page = fs.readFileSync(path.join(root, 'source/map/index.md'), 'utf8');
  const script = fs.readFileSync(path.join(root, 'source/js/paper-map.js'), 'utf8');
  const css = fs.readFileSync(path.join(root, 'source/css/paper-map.css'), 'utf8');

  assert.match(page, /id="map-hover-card"/);
  assert.match(page, /leaflet\.markercluster/);
  assert.match(script, /carouselTimer/);
  assert.match(script, /clearInterval\(carouselTimer\)/);
  assert.match(script, /new Image\(\)/);
  assert.match(script, /onerror/);
  assert.match(script, /loadNextCarouselImage/);
  assert.match(script, /mouseover/);
  assert.match(script, /markerClusterGroup/);
  assert.match(script, /setInterval\([\s\S]*?,\s*1000\)/);
  assert.match(script, /scheduleHideHover/);
  assert.match(script, /hoverCard\.addEventListener\('mouseenter'/);
  assert.match(script, /hoverCard\.addEventListener\('click'/);
  assert.match(css, /\.map-hover-card\.is-visible[^}]*pointer-events:\s*auto/s);
  assert.doesNotMatch(css, /\.leaflet-tile-pane\s*\{[^}]*filter:/s);
});

test('unlocated papers stay in the audit list and are never mislabeled as virtual meetings', () => {
  const posts = [
    { slug: 'located', title: 'Located', path: 'article/located/', date: date('2026-01-01'), venue_type: '会议' },
    { slug: 'unknown', title: 'Unknown', path: 'article/unknown/', date: date('2026-01-02'), venue_type: 'arXiv预印本' }
  ];
  const places = [
    { id: 'beijing', name: 'Beijing', city: 'Beijing', wgs84: [116.4, 39.9], image: '/images/map/beijing.jpg' },
    { id: 'virtual', name: '线上空间', city: 'Virtual', wgs84: [0, 20], image: '/images/map/virtual.svg' }
  ];
  const assignments = [{ paper_id: 'located', place_id: 'beijing', location_type: 'school', location_label: 'THU' }];

  const payload = buildMapPayload(posts, places, 0.6, assignments);

  assert.equal(payload.papers.length, 1);
  assert.equal(payload.meta.mapped_papers, 1);
  assert.equal(payload.meta.physical_located_papers, 1);
  assert.equal(payload.meta.virtual_unlocated_papers, 0);
  assert.equal(payload.meta.unlocated_papers, 1);
  assert.equal(payload.unlocated[0].title, 'Unknown');
  assert.equal(payload.places.some(place => place.location_type === 'virtual'), false);
});

test('canonical arxiv identity prevents the same online paper appearing twice', () => {
  const posts = [
    { slug: 'paper-a', title: 'One', path: 'article/paper-a/', arxiv_id: '2403.06447', date: date('2026-01-01') },
    { slug: 'paper-b', title: 'One copy', path: 'article/paper-b/', paper_url: 'https://arxiv.org/abs/2403.06447v2', date: date('2026-01-02') }
  ];
  const places = [{ id: 'ucsd', name: 'La Jolla', city: 'La Jolla', wgs84: [-117, 32], image: '/images/map/la-jolla.jpg' }];
  const assignments = [
    { paper_id: 'paper-a', place_id: 'ucsd', location_type: 'school', location_label: 'UC San Diego' },
    { paper_id: 'paper-b', place_id: 'ucsd', location_type: 'school', location_label: 'UC San Diego' }
  ];

  const payload = buildMapPayload(posts, places, 0.6, assignments);

  assert.equal(payload.papers.length, 1);
  assert.equal(payload.meta.duplicate_papers, 1);
});

test('map legend links to five location catalog pages and navigation is static', () => {
  const root = path.resolve(__dirname, '..');
  const page = fs.readFileSync(path.join(root, 'source/map/index.md'), 'utf8');
  const config = fs.readFileSync(path.join(root, '_config.butterfly.yml'), 'utf8');

  ['school', 'company', 'publisher', 'virtual', 'venue'].forEach(type => {
    assert.match(page, new RegExp('href="/map/' + type + '/"'));
    assert.equal(fs.existsSync(path.join(root, 'source/map', type, 'index.md')), true);
  });
  assert.match(config, /论文足迹:\s*\/map\//);
  assert.doesNotMatch(config, /map-nav-gate\.js/);
});

test('map catalog follows institution-group then paper-card hierarchy', () => {
  const root = path.resolve(__dirname, '..');
  const script = fs.readFileSync(path.join(root, 'source/js/map-catalog.js'), 'utf8');
  const css = fs.readFileSync(path.join(root, 'source/css/map-catalog.css'), 'utf8');

  assert.match(script, /map_data\.json/);
  assert.match(script, /location_label/);
  assert.match(script, /map-catalog__institution/);
  assert.match(script, /map-catalog__paper-card/);
  assert.match(script, /place\.city_images/);
  assert.match(script, /paper\.description/);
  assert.match(script, /chooseUniqueImage/);
  assert.doesNotMatch(script, /cache:\s*['"]no-store['"]/);
  assert.match(script, /sessionStorage/);
  assert.match(css, /\.map-catalog__institution/);
  assert.match(css, /\.map-catalog__paper-card/);
  assert.match(css, /grid-template-columns:\s*1fr/);
});

test('company catalog links enterprise cards to a dedicated papers page', () => {
  const root = path.resolve(__dirname, '..');
  const script = fs.readFileSync(path.join(root, 'source/js/map-catalog.js'), 'utf8');
  const css = fs.readFileSync(path.join(root, 'source/css/map-catalog.css'), 'utf8');
  const page = fs.readFileSync(path.join(root, 'source/map/company/index.md'), 'utf8');

  assert.match(script, /type === 'company'/);
  assert.match(script, /map-catalog__company-card/);
  assert.match(script, /\/map\/company\/papers\/\?company=/);
  assert.doesNotMatch(script, /map-catalog__company-papers/);
  assert.match(script, /group\.description/);
  assert.match(script, /group\.images/);
  assert.match(script, /lead\.description/);
  assert.match(page, /data-company-search/);
  assert.match(css, /\.map-catalog__company-grid/);
  assert.match(css, /\.map-catalog__company-card/);
});

test('company papers page uses a searchable virtual list instead of rendering every paper', () => {
  const root = path.resolve(__dirname, '..');
  const pagePath = path.join(root, 'source/map/company/papers/index.md');
  const scriptPath = path.join(root, 'source/js/company-papers.js');

  assert.equal(fs.existsSync(pagePath), true);
  assert.equal(fs.existsSync(scriptPath), true);
  const page = fs.readFileSync(pagePath, 'utf8');
  const script = fs.readFileSync(scriptPath, 'utf8');
  assert.match(page, /data-company-paper-search/);
  assert.match(page, /data-company-paper-viewport/);
  assert.match(script, /URLSearchParams/);
  assert.match(script, /computeVirtualRange/);
  assert.match(script, /overscan/);
  assert.match(script, /scrollTop/);
  assert.match(script, /translateY/);
  assert.match(script, /loading\s*=\s*['"]lazy['"]/);
});

test('virtual company paper range renders only the viewport plus overscan', () => {
  const { computeVirtualRange } = require('../source/js/company-papers');
  const range = computeVirtualRange({
    scrollTop: 1320,
    viewportHeight: 660,
    rowHeight: 330,
    itemCount: 100,
    overscan: 2
  });

  assert.deepEqual(range, { start: 2, end: 8 });
  assert.ok(range.end - range.start < 100);
});

test('map avoids cache-busting data requests and eager gallery preloading', () => {
  const root = path.resolve(__dirname, '..');
  const mapScript = fs.readFileSync(path.join(root, 'source/js/paper-map.js'), 'utf8');
  const catalogScript = fs.readFileSync(path.join(root, 'source/js/map-catalog.js'), 'utf8');

  assert.doesNotMatch(mapScript, /map_data\.json\?v=['"]?\s*\+\s*Date\.now/);
  assert.doesNotMatch(catalogScript, /map_data\.json\?v=['"]?\s*\+\s*Date\.now/);
  assert.doesNotMatch(mapScript, /preloadImages\(images\)/);
  assert.match(mapScript, /image\.decoding\s*=\s*['"]async['"]/);
});

test('map data uses a one-hour local cache with stale fallback', () => {
  const cacheScript = fs.readFileSync(path.join(__dirname, '../source/js/map-data-cache.js'), 'utf8');
  assert.match(cacheScript, /60\s*\*\s*60\s*\*\s*1000/);
  assert.match(cacheScript, /localStorage\.getItem/);
  assert.match(cacheScript, /localStorage\.setItem/);
  assert.match(cacheScript, /stale/i);
  for (const scriptName of ['paper-map.js', 'map-catalog.js', 'company-papers.js']) {
    const script = fs.readFileSync(path.join(__dirname, '../source/js', scriptName), 'utf8');
    assert.match(script, /MapDataCache\.load/);
    assert.doesNotMatch(script, /fetch\(['"]\/map_data\.json/);
  }
});

test('the colorful world topographic map is primary and fallback waits for three tile errors', () => {
  const script = fs.readFileSync(path.join(__dirname, '../source/js/paper-map.js'), 'utf8');
  assert.match(script, /primary:\s*\{[\s\S]*World_Topo_Map/i);
  assert.match(script, /fallback:\s*\{[\s\S]*openstreetmap/i);
  assert.match(script, /tileErrorCount\s*>=\s*3/);
});

test('map copy explains the marker meaning instead of using the generic encounter slogan', () => {
  const script = fs.readFileSync(path.join(__dirname, '../source/js/paper-map.js'), 'utf8');
  assert.match(script, /function semanticPlaceCopy/);
  assert.match(script, /meaning\.label/);
  assert.doesNotMatch(script, /论文、机构与城市在这里相遇/);
});

test('map image conversion tool rewrites gallery references and can remove originals', () => {
  const script = fs.readFileSync(path.join(__dirname, '../tools/convert_map_images.py'), 'utf8');
  assert.match(script, /\.webp/);
  assert.match(script, /--remove-originals/);
  assert.match(script, /places\.json/);
});

test('map pages version their JavaScript assets so deployments replace stale browser code', () => {
  const root = path.resolve(__dirname, '..');
  const mapPage = fs.readFileSync(path.join(root, 'source/map/index.md'), 'utf8');
  const companyPage = fs.readFileSync(path.join(root, 'source/map/company/index.md'), 'utf8');

  assert.match(mapPage, /paper-map\.js\?v=[a-z0-9-]+/i);
  assert.match(companyPage, /map-catalog\.css\?v=[a-z0-9-]+/i);
  assert.match(companyPage, /map-catalog\.js\?v=[a-z0-9-]+/i);
});

test('map terminology is precise and the navigation stays above the map canvas', () => {
  const root = path.resolve(__dirname, '..');
  const page = fs.readFileSync(path.join(root, 'source/map/index.md'), 'utf8');
  const script = fs.readFileSync(path.join(root, 'source/js/paper-map.js'), 'utf8');
  const mapCss = fs.readFileSync(path.join(root, 'source/css/paper-map.css'), 'utf8');
  const navCss = fs.readFileSync(path.join(root, 'source/css/left-nav.css'), 'utf8');

  for (const label of ['高校与科研院所', '企业研究机构', '出版与学术组织', '线上会议', '会议举办地']) {
    assert.match(page + script, new RegExp(label));
  }
  assert.match(mapCss, /\.paper-map-shell\s*\{[^}]*z-index:\s*0/s);
  assert.match(navCss, /#sidebar\s*\{[^}]*z-index:\s*(?:1[0-9]{3}|[2-9][0-9]{3,})/s);
});

test('category and tag list icons use portable glyphs instead of mismatched Font Awesome codepoints', () => {
  const css = fs.readFileSync(path.resolve(__dirname, '../source/css/pages.css'), 'utf8');

  assert.match(css, /content:\s*"📁"/);
  assert.match(css, /content:\s*"📄"/);
  assert.match(css, /content:\s*"🏷"/);
  assert.doesNotMatch(css, /Font Awesome 6 Free/);
});
