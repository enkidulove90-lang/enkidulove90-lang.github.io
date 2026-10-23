# Research City Terrain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a production-ready terrain-to-research-city map with truthful city aggregation, curated core-city navigation, cinematic 3D arrival, and safe 2D fallback.

**Architecture:** Add a small CommonJS/browser-compatible `map-experience` module that owns deterministic city aggregation, ranking, and camera profiles. Keep `paper-map.js` responsible for DOM and MapLibre/Leaflet orchestration, and keep all network behavior opt-in behind the existing 3D toggle.

**Tech Stack:** Hexo 7, vanilla JavaScript, Node test runner, Leaflet 1.9, MapLibre GL JS 6.15, CSS, GitHub Pages.

---

## File map

- `source/js/map-experience.js`: pure city normalization, aggregation, ranking, and camera-plan functions; browser export plus CommonJS export.
- `source/js/paper-map.js`: render city navigation, aggregate city details, run 2D/3D arrival, and enhance terrain style.
- `source/css/paper-map.css`: Butterfly-compatible city rail, core markers, arrival caption, responsive and reduced-motion styles.
- `source/map/index.md`: semantic containers and cache-busted script include.
- `tests/map-experience.test.js`: behavioral unit tests for city truthfulness and deterministic camera plans.
- `tests/map-data.test.js`: page/style/runtime contract assertions.

### Task 1: City aggregation and ranking core

**Files:**
- Create: `source/js/map-experience.js`
- Create: `tests/map-experience.test.js`

- [ ] **Step 1: Write failing aggregation tests**

Create fixtures where Beijing has separate school/company places, Singapore has one recent paper, and New York has no place. Assert that `buildResearchCities(payload, { now: '2026-10-23' })` merges Beijing, deduplicates institutions and papers, includes all four core cities, and leaves New York at zero.

```js
const cities = experience.buildResearchCities(payload, { now: '2026-10-23T00:00:00Z', limit: 6 });
assert.deepEqual(cities.slice(0, 4).map(city => city.key), ['beijing', 'hangzhou', 'singapore', 'new-york']);
assert.equal(cities.find(city => city.key === 'beijing').paperCount, 2);
assert.equal(cities.find(city => city.key === 'new-york').paperCount, 0);
```

- [ ] **Step 2: Run the test and verify RED**

Run: `node --test tests/map-experience.test.js`

Expected: FAIL because `source/js/map-experience.js` does not exist.

- [ ] **Step 3: Implement the pure module**

Define:

```js
const CORE_CITY_PROFILES = [
  { key: 'beijing', name: '北京', aliases: ['beijing'], center: [116.4074, 39.9042], approach: [115.7, 40.35], zoom: 8.2, pitch: 61, bearing: -18 },
  { key: 'hangzhou', name: '杭州', aliases: ['hangzhou'], center: [120.1551, 30.2741], approach: [119.45, 29.85], zoom: 8.7, pitch: 62, bearing: 24 },
  { key: 'singapore', name: '新加坡', aliases: ['singapore'], center: [103.8198, 1.3521], approach: [103.25, 1.02], zoom: 9.2, pitch: 60, bearing: -28 },
  { key: 'new-york', name: '纽约', aliases: ['new york', 'new york city'], center: [-74.006, 40.7128], approach: [-74.7, 40.2], zoom: 8.8, pitch: 62, bearing: 20 }
];
```

Export `normalizeCityKey`, `aggregatePayloadCities`, `buildResearchCities`, and `buildArrivalPlan`. Score non-core cities from paper count, unique institution count, and papers within 365 days. Never copy papers between cities.

- [ ] **Step 4: Run the test and verify GREEN**

Run: `node --test tests/map-experience.test.js`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add source/js/map-experience.js tests/map-experience.test.js
git commit -m "feat(map): rank truthful research city hubs"
```

### Task 2: City navigation and aggregate detail UI

**Files:**
- Modify: `source/map/index.md`
- Modify: `source/css/paper-map.css`
- Modify: `source/js/paper-map.js`
- Modify: `tests/map-data.test.js`

- [ ] **Step 1: Write failing DOM contract tests**

Assert that the page contains `map-city-nav`, `map-arrival`, and loads `/js/map-experience.js` before `/js/paper-map.js`. Assert CSS has mobile horizontal scrolling and reduced-motion handling.

```js
assert.match(page, /id=["']map-city-nav["']/);
assert.match(page, /id=["']map-arrival["']/);
assert.ok(page.indexOf('/js/map-experience.js') < page.indexOf('/js/paper-map.js'));
assert.match(css, /prefers-reduced-motion:\s*reduce/);
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `node --test tests/map-data.test.js`

Expected: FAIL on missing city navigation and arrival elements.

- [ ] **Step 3: Add semantic markup and styling**

Add a `nav` inside `.map-stage`, a status-like arrival caption, and the experience script. Style the rail as translucent warm-white Butterfly cards with teal active state, keyboard focus, mobile overflow, and no paper/editorial texture.

- [ ] **Step 4: Render cities from the pure module**

In `paper-map.js`, call:

```js
researchCities = window.PaperMapExperience.buildResearchCities(payload, {
  now: payload.meta.generated,
  limit: 8
});
renderCityNavigation(researchCities);
```

Each button displays name and truthful paper count. Selecting a city aggregates its places for `buildPlaceCard`; a zero-paper core city shows an explicit empty-state message.

- [ ] **Step 5: Run focused and full tests**

Run: `node --test tests/map-data.test.js tests/map-experience.test.js`

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add source/map/index.md source/css/paper-map.css source/js/paper-map.js tests/map-data.test.js
git commit -m "feat(map): add core research city navigation"
```

### Task 3: Vivid terrain and cinematic city arrival

**Files:**
- Modify: `source/js/paper-map.js`
- Modify: `source/css/paper-map.css`
- Modify: `tests/map-data.test.js`
- Modify: `tests/map-experience.test.js`

- [ ] **Step 1: Write failing terrain contract tests**

Assert separate `terrain` and `hillshade` raster-dem sources, `sky`, raster saturation/contrast, dynamic `setTerrain`, `flyTo`, and a reduced-motion branch. Unit-test that core profiles produce two camera stages and generated cities produce a deterministic fallback.

- [ ] **Step 2: Run tests and verify RED**

Run: `node --test tests/map-data.test.js tests/map-experience.test.js`

Expected: FAIL on missing style and camera behavior.

- [ ] **Step 3: Enhance the MapLibre style**

Use duplicate DEM source definitions for terrain and hillshade, add `sky: {}`, and tune Physical raster paint:

```js
paint: {
  'raster-saturation': 0.24,
  'raster-contrast': 0.14,
  'raster-brightness-min': 0.04,
  'raster-brightness-max': 0.96
}
```

Initialize global terrain at exaggeration `1.0`, pitch about `36`, and retain the existing three-error Leaflet fallback.

- [ ] **Step 4: Implement arrival orchestration**

For 3D, execute profile `approach` then `center` using `flyTo`; call `setTerrain({ source: 'terrain', exaggeration: 1.42 })` for final arrival. For 2D, use `flyTo`/`setView` without loading MapLibre. With reduced motion, use `jumpTo` in 3D and `setView` in 2D. Update button `aria-pressed` and arrival caption.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `npm test`

Expected: all Node tests PASS.

- [ ] **Step 6: Commit**

```powershell
git add source/js/paper-map.js source/css/paper-map.css tests/map-data.test.js tests/map-experience.test.js
git commit -m "feat(map): animate vivid terrain city arrivals"
```

### Task 4: Build and browser evidence

**Files:**
- Modify only if verification finds a test-backed defect.
- Create: `reports/research-city-terrain-evidence.md`

- [ ] **Step 1: Run complete automated verification**

Run:

```powershell
npm test
npm run test:python
npm run build
git diff --check
```

Expected: all tests pass, Hexo build succeeds, and diff check prints no errors.

- [ ] **Step 2: Start the local Hexo server**

Run: `npm run server -- --port 4000`

Expected: `/map/` returns HTTP 200.

- [ ] **Step 3: Capture browser evidence**

Verify at desktop and mobile widths:

- 2D loads without MapLibre/DEM requests.
- Core city buttons show 北京、杭州、新加坡、纽约.
- 3D produces visible terrain and clear labels.
- Each core city selection changes camera and truthful detail.
- DEM request blocking restores Leaflet.
- Keyboard and reduced-motion paths remain usable.

Record exact observed results and screenshot paths in the evidence report; do not claim evidence that was not captured.

- [ ] **Step 4: Commit evidence and final fixes**

```powershell
git add reports/research-city-terrain-evidence.md
git commit -m "test(map): document research city terrain evidence"
```

