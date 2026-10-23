(function () {
  'use strict';
  // /map_data.json is fetched once through MapDataCache and retained for one hour.

  var root = document.getElementById('paper-map');
  if (!root) return;
  var status = document.getElementById('map-status');
  var detail = document.getElementById('map-detail');
  var detailContent = document.getElementById('map-detail-content');
  var detailClose = document.getElementById('map-detail-close');
  var hoverCard = document.getElementById('map-hover-card');
  var hoverImage = document.getElementById('map-hover-image');
  var hoverText = document.getElementById('map-hover-text');
  var terrainToggle = document.getElementById('map-terrain-toggle');
  var runtimeConfig = window.__PAPER_MAP_CONFIG__ || {}; // Backward compatibility; public tiles need no key.
  var MAPLIBRE_MODULE_URL = 'https://unpkg.com/maplibre-gl@6.15.0/dist/maplibre-gl.mjs';
  var MAPLIBRE_CSS_URL = 'https://unpkg.com/maplibre-gl@6.15.0/dist/maplibre-gl.css';
  var TERRAIN_TILE_URL = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png';
  var PHYSICAL_MAX_NATIVE_ZOOM = 8;
  var currentPayload = null;
  var leafletMap = null;
  var terrainMap = null;
  var terrainLoading = false;
  var carouselTimer = null;
  var hoverHideTimer = null;
  var activeHoverPlace = null;
  var activeHoverPapers = null;
  var LOCATION_META = {
    school: { icon: '🎓', label: '高校与科研院所' }, company: { icon: '🏢', label: '企业研究机构' },
    publisher: { icon: '📚', label: '出版与学术组织' }, virtual: { icon: '☁', label: '线上会议' },
    venue: { icon: '🎤', label: '会议举办地' }, affiliation: { icon: '◆', label: '作者机构' }
  };
  var CITY_TAGLINES = {
    'Hong Kong': '繁华之城', Beijing: '思想与工程交汇之城', Boston: '跨学科之城',
    Hefei: '基础研究之城', Hanoi: '生长中的技术之城', London: '开放与多元之城',
    Singapore: '连接亚洲研究之城', Virtual: '跨越时区之地'
  };

  function setStatus(kind, title, message) {
    status.className = 'map-status map-status--' + kind;
    status.replaceChildren();
    var copy = document.createElement('div');
    var heading = document.createElement('strong');
    var paragraph = document.createElement('p');
    heading.textContent = title;
    paragraph.textContent = message;
    copy.append(heading, paragraph);
    status.appendChild(copy);
  }

  function createPaperList(papers) {
    var list = document.createElement('ol');
    list.className = 'map-paper-list';
    papers.forEach(function (paper) {
      var item = document.createElement('li');
      var link = document.createElement('a');
      var meta = document.createElement('span');
      link.href = paper.url;
      link.textContent = paper.title;
      meta.textContent = [paper.date, paper.venue_name].filter(Boolean).join(' · ');
      item.append(link, meta);
      list.appendChild(item);
    });
    return list;
  }

  function stopCarousel() {
    if (carouselTimer) clearInterval(carouselTimer);
    carouselTimer = null;
  }

  function createCarousel(place) {
    var images = Array.from(new Set([place.image].concat(place.city_images || []).filter(Boolean)));
    var frame = document.createElement('figure');
    var image = document.createElement('img');
    var count = document.createElement('figcaption');
    var active = 0;
    var loading = false;
    var failed = {};
    frame.className = 'map-place-carousel';
    image.alt = place.name + '城市图景';
    image.decoding = 'async';
    count.className = 'map-place-carousel__count';
    count.textContent = '1 / ' + Math.max(images.length, 1);
    frame.append(image, count);

    function loadNextCarouselImage(requestedIndex) {
      if (loading || !images.length) return;
      var attempts = 0;
      var next = requestedIndex;
      while (attempts < images.length && failed[images[next]]) {
        next = (next + 1) % images.length;
        attempts += 1;
      }
      if (attempts >= images.length) return;
      loading = true;
      var nextImage = new Image();
      nextImage.decoding = 'async';
      nextImage.onload = function () {
        loading = false;
        active = next;
        image.classList.add('is-switching');
        image.src = nextImage.src;
        count.textContent = (active + 1) + ' / ' + images.length;
        requestAnimationFrame(function () { image.classList.remove('is-switching'); });
      };
      nextImage.onerror = function () {
        loading = false;
        failed[images[next]] = true;
        loadNextCarouselImage((next + 1) % images.length);
      };
      nextImage.src = images[next];
    }

    image.onerror = function () {
      failed[images[active]] = true;
      loadNextCarouselImage((active + 1) % images.length);
    };
    loadNextCarouselImage(0);
    if (images.length > 1) {
      carouselTimer = setInterval(function () {
        loadNextCarouselImage((active + 1) % images.length);
      }, 1000);
    }
    return frame;
  }

  function semanticPlaceCopy(place, papers) {
    var meaning = LOCATION_META[place.location_type] || LOCATION_META.affiliation;
    var raw = String(place.description || '');
    var generic = !raw || /论文.*机构.*城市.*相遇|研究发生之地/.test(raw);
    return {
      title: place.name + ' · ' + meaning.label,
      description: generic
        ? meaning.label + '标记，收录 ' + papers.length + ' 篇与此地直接相关的论文。'
        : raw,
      hover: place.name + ' · ' + meaning.label + ' · ' + papers.length + ' 篇论文'
    };
  }

  function createInstitutionList(institutions) {
    var section = document.createElement('section');
    section.className = 'map-institution-list';
    institutions.forEach(function (institution) {
      var article = document.createElement('article');
      var heading = document.createElement('h3');
      var copy = document.createElement('p');
      heading.textContent = institution.name;
      copy.textContent = institution.description;
      article.append(heading, copy);
      section.appendChild(article);
    });
    return section;
  }

  function buildPlaceCard(place, papers) {
    var card = document.createElement('article');
    var body = document.createElement('div');
    var title = document.createElement('h2');
    var description = document.createElement('p');
    card.className = 'map-place-card';
    body.className = 'map-place-card__body';
    var copy = semanticPlaceCopy(place, papers);
    title.textContent = copy.title;
    description.className = 'map-place-card__description';
    description.textContent = copy.description;
    body.append(title, description);
    if ((place.institutions || []).length) body.appendChild(createInstitutionList(place.institutions));
    body.appendChild(createPaperList(papers));
    card.append(createCarousel(place), body);
    return card;
  }

  function showDetail(place, papers) {
    stopCarousel();
    hideHover();
    detailContent.replaceChildren(buildPlaceCard(place, papers));
    detail.classList.add('is-open');
    detail.setAttribute('aria-hidden', 'false');
  }

  function hideDetail() {
    detail.classList.remove('is-open');
    detail.setAttribute('aria-hidden', 'true');
    stopCarousel();
  }

  function showHover(place, originalEvent) {
    clearTimeout(hoverHideTimer);
    activeHoverPlace = place;
    var stage = root.getBoundingClientRect();
    var left = Math.min(originalEvent.clientX - stage.left + 18, stage.width - 290);
    var top = Math.max(14, originalEvent.clientY - stage.top - 112);
    hoverImage.src = place.hover_image || place.image;
    hoverImage.alt = place.name + '城市图景';
    hoverText.textContent = semanticPlaceCopy(place, activeHoverPapers || []).hover;
    hoverCard.style.transform = 'translate3d(' + Math.max(14, left) + 'px,' + top + 'px,0) scale(1)';
    hoverCard.classList.add('is-visible');
    hoverCard.setAttribute('aria-hidden', 'false');
  }

  function hideHover() {
    clearTimeout(hoverHideTimer);
    hoverCard.classList.remove('is-visible');
    hoverCard.setAttribute('aria-hidden', 'true');
  }

  function scheduleHideHover() {
    clearTimeout(hoverHideTimer);
    hoverHideTimer = setTimeout(hideHover, 220);
  }

  function renderMap(payload, requestedView) {
    if (!window.L) throw new Error('Leaflet failed to load');
    var L = window.L;
    if (leafletMap) leafletMap.remove();
    root.replaceChildren();
    var initialView = requestedView || { lat: 25, lng: 15, zoom: 2 };
    var map = L.map('paper-map', { zoomControl: true, worldCopyJump: true, minZoom: 2 })
      .setView([initialView.lat, initialView.lng], initialView.zoom);
    leafletMap = map;
    var BASEMAPS = [
      {
        id: 'physical',
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}',
        maxNativeZoom: 8, maxZoom: 19
      },
      {
        id: 'topographic',
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        maxZoom: 19
      },
      { id: 'osm', url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', maxZoom: 19 }
    ];
    var REFERENCE_LAYER = {
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
      maxZoom: 19
    };
    var osmAttribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
    var esriAttribution = 'Tiles &copy; Esri — Sources: Esri, HERE, Garmin, FAO, NOAA, USGS, OpenStreetMap contributors';
    var basemapIndex = 0;
    var tileErrorCount = 0;
    var failedBasemaps = {};

    function createBasemap(definition) {
      var options = {
        maxZoom: definition.maxZoom,
        attribution: definition.id === 'osm' ? osmAttribution : esriAttribution,
        updateWhenIdle: true, keepBuffer: 2, zIndex: 100
      };
      if (definition.maxNativeZoom) options.maxNativeZoom = definition.maxNativeZoom;
      return L.tileLayer(definition.url, options);
    }

    var tiles = createBasemap(BASEMAPS[basemapIndex]);

    function findBasemapIndex(id) {
      return BASEMAPS.findIndex(function (definition) { return definition.id === id; });
    }

    function switchBasemap(id) {
      var nextIndex = findBasemapIndex(id);
      if (nextIndex < 0 || failedBasemaps[id] || nextIndex === basemapIndex) return;
      if (map.hasLayer(tiles)) map.removeLayer(tiles);
      basemapIndex = nextIndex;
      tileErrorCount = 0;
      tiles = createBasemap(BASEMAPS[basemapIndex]);
      tiles.on('tileerror', useFallback);
      tiles.addTo(map);
    }

    function useFallback() {
      tileErrorCount += 1;
      if (!(tileErrorCount >= 3)) return;
      if (basemapIndex >= BASEMAPS.length - 1) {
        setStatus('error', '底图暂时不可用', '论文坐标仍然完整，请稍后刷新。');
        return;
      }
      failedBasemaps[BASEMAPS[basemapIndex].id] = true;
      map.removeLayer(tiles);
      basemapIndex += 1;
      tileErrorCount = 0;
      tiles = createBasemap(BASEMAPS[basemapIndex]);
      tiles.on('tileerror', useFallback);
      tiles.addTo(map);
    }

    tiles.on('tileerror', useFallback);
    tiles.addTo(map);
    map.on('zoomend', function () {
      if (map.getZoom() > PHYSICAL_MAX_NATIVE_ZOOM && basemapIndex === findBasemapIndex('physical')) {
        switchBasemap('topographic');
      } else if (map.getZoom() <= PHYSICAL_MAX_NATIVE_ZOOM && basemapIndex === findBasemapIndex('topographic')) {
        switchBasemap('physical');
      }
    });
    var referenceTileErrorCount = 0;
    var referenceTiles = L.tileLayer(REFERENCE_LAYER.url, {
      maxZoom: REFERENCE_LAYER.maxZoom,
      attribution: esriAttribution,
      updateWhenIdle: true, keepBuffer: 2, zIndex: 200
    });
    referenceTiles.on('tileerror', function () {
      referenceTileErrorCount += 1;
      if (referenceTileErrorCount >= 3 && map.hasLayer(referenceTiles)) map.removeLayer(referenceTiles);
    });
    referenceTiles.addTo(map);
    var ignoreNextMapClick = false;
    map.on('click', function () {
      if (ignoreNextMapClick) {
        ignoreNextMapClick = false;
        return;
      }
      hideDetail();
    });
    var markers = [];
    var markerLayer = payload.places.length > 100 && L.markerClusterGroup
      ? L.markerClusterGroup({ chunkedLoading: true, showCoverageOnHover: false })
      : L.layerGroup();

    payload.places.forEach(function (place) {
      var papers = place.papers || payload.papers.filter(function (paper) { return paper.city_id === place.id; });
      var meaning = LOCATION_META[place.location_type] || LOCATION_META.affiliation;
      var icon = L.divIcon({
        className: 'paper-map-div-icon',
        html: '<span class="paper-map-marker paper-map-marker--' + place.location_type + '">' +
          '<span aria-hidden="true">' + meaning.icon + '</span></span>',
        iconSize: [42, 42], iconAnchor: [21, 21]
      });
      var marker = L.marker([place.wgs84[1], place.wgs84[0]], {
        icon: icon, title: place.name, riseOnHover: true, keyboard: true,
        alt: place.name + '，' + meaning.label + '，' + papers.length + ' 篇论文',
        bubblingMouseEvents: false
      });
      marker._paperMapLabel = place.name + '，' + meaning.label + '，' + papers.length + ' 篇论文';
      marker.on('click', function (event) {
        ignoreNextMapClick = true;
        if (event.originalEvent) L.DomEvent.stopPropagation(event.originalEvent);
        showDetail(place, papers);
        setTimeout(function () { ignoreNextMapClick = false; }, 0);
      });
      marker.on('mouseover', function (event) {
        activeHoverPapers = papers;
        var markerElement = marker.getElement();
        if (markerElement) markerElement.classList.add('is-hovered');
        if (event.originalEvent) showHover(place, event.originalEvent);
      });
      marker.on('mouseout', function () {
        var markerElement = marker.getElement();
        if (markerElement) markerElement.classList.remove('is-hovered');
        scheduleHideHover();
      });
      markerLayer.addLayer(marker);
      markers.push(marker);
    });

    markerLayer.addTo(map);
    markers.forEach(function (marker) {
      var markerElement = marker.getElement();
      if (!markerElement) return;
      markerElement.setAttribute('aria-label', marker._paperMapLabel);
    });

    if (!requestedView && markers.length > 1) {
      map.fitBounds(L.featureGroup(markers).getBounds(), { padding: [48, 48], maxZoom: 5 });
    }
    status.classList.add('map-status--hidden');
    if (terrainToggle) terrainToggle.disabled = false;
  }

  function loadMapLibreCss() {
    if (document.getElementById('maplibre-terrain-css')) return;
    var link = document.createElement('link');
    link.id = 'maplibre-terrain-css';
    link.rel = 'stylesheet';
    link.href = MAPLIBRE_CSS_URL;
    document.head.appendChild(link);
  }

  function captureLeafletView() {
    if (!leafletMap) return { lat: 25, lng: 15, zoom: 2 };
    var center = leafletMap.getCenter();
    return { lat: center.lat, lng: center.lng, zoom: leafletMap.getZoom() };
  }

  function captureTerrainView() {
    if (!terrainMap) return { lat: 25, lng: 15, zoom: 2 };
    var center = terrainMap.getCenter();
    return { lat: center.lat, lng: center.lng, zoom: terrainMap.getZoom() };
  }

  function restoreLeaflet(message, requestedView) {
    var view = requestedView || captureTerrainView();
    if (terrainMap) {
      try { terrainMap.setTerrain(null); } catch (error) { /* Map may have failed before style load. */ }
      try { terrainMap.setProjection({ type: 'mercator' }); } catch (error) { /* Keep fallback unconditional. */ }
      try { terrainMap.remove(); } catch (error) { /* The Leaflet restore below is authoritative. */ }
      terrainMap = null;
    }
    terrainLoading = false;
    if (terrainToggle) {
      terrainToggle.disabled = false;
      terrainToggle.setAttribute('aria-pressed', 'false');
      terrainToggle.textContent = '3D 地形';
    }
    if (currentPayload) renderMap(currentPayload, view);
    if (message) {
      setStatus('error', '三维地形已安全退出', message + ' 已恢复二维地图。');
      window.setTimeout(function () { status.classList.add('map-status--hidden'); }, 3200);
    }
  }

  function createTerrainMarker(maplibregl, place, papers) {
    var meaning = LOCATION_META[place.location_type] || LOCATION_META.affiliation;
    var button = document.createElement('button');
    var markerBody = document.createElement('span');
    var icon = document.createElement('span');
    button.type = 'button';
    button.className = 'maplibre-paper-marker';
    button.setAttribute('aria-label', place.name + '，' + meaning.label + '，' + papers.length + ' 篇论文');
    markerBody.className = 'paper-map-marker paper-map-marker--' + place.location_type;
    icon.setAttribute('aria-hidden', 'true');
    icon.textContent = meaning.icon;
    markerBody.appendChild(icon);
    button.appendChild(markerBody);
    button.addEventListener('click', function (event) {
      event.stopPropagation();
      showDetail(place, papers);
    });
    button.addEventListener('mouseenter', function (event) {
      activeHoverPapers = papers;
      button.classList.add('is-hovered');
      showHover(place, event);
    });
    button.addEventListener('mouseleave', function () {
      button.classList.remove('is-hovered');
      scheduleHideHover();
    });
    new maplibregl.Marker({ element: button, anchor: 'center' })
      .setLngLat(place.wgs84)
      .addTo(terrainMap);
  }

  function terrainStyle() {
    var esriAttribution = 'Tiles &copy; Esri — Sources: Esri, HERE, Garmin, FAO, NOAA, USGS, OpenStreetMap contributors';
    return {
      version: 8,
      sources: {
        physical: {
          type: 'raster',
          tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}'],
          tileSize: 256,
          maxzoom: PHYSICAL_MAX_NATIVE_ZOOM,
          attribution: esriAttribution
        },
        topographic: {
          type: 'raster',
          tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}'],
          tileSize: 256,
          maxzoom: 19,
          attribution: esriAttribution
        },
        terrain: {
          type: 'raster-dem',
          tiles: [TERRAIN_TILE_URL],
          tileSize: 256,
          maxzoom: 15,
          encoding: 'terrarium',
          attribution: 'Elevation data &copy; Mapzen, Amazon Web Services'
        },
        reference: {
          type: 'raster',
          tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'],
          tileSize: 256,
          maxzoom: 19,
          attribution: esriAttribution
        }
      },
      layers: [
        { id: 'physical', type: 'raster', source: 'physical', maxzoom: PHYSICAL_MAX_NATIVE_ZOOM + 0.5 },
        { id: 'topographic', type: 'raster', source: 'topographic', minzoom: PHYSICAL_MAX_NATIVE_ZOOM + 0.5 },
        {
          id: 'terrain-hillshade', type: 'hillshade', source: 'terrain',
          paint: { 'hillshade-exaggeration': 0.42, 'hillshade-shadow-color': '#675941', 'hillshade-highlight-color': '#fff7de' }
        },
        { id: 'reference', type: 'raster', source: 'reference' }
      ],
      terrain: { source: 'terrain', exaggeration: 1.15 }
    };
  }

  async function enableTerrain() {
    if (terrainLoading || terrainMap || !currentPayload) return;
    terrainLoading = true;
    var view = captureLeafletView();
    if (terrainToggle) {
      terrainToggle.disabled = true;
      terrainToggle.textContent = '载入地形…';
    }
    try {
      loadMapLibreCss();
      var module = await import(MAPLIBRE_MODULE_URL);
      var maplibregl = module.default && module.default.Map ? module.default : module;
      if (typeof maplibregl.supported === 'function' && !maplibregl.supported()) {
        throw new Error('WebGL is unavailable');
      }
      if (leafletMap) {
        leafletMap.remove();
        leafletMap = null;
      }
      root.replaceChildren();
      var terrainErrorCount = 0;
      var fallbackStarted = false;
      terrainMap = new maplibregl.Map({
        container: root,
        style: terrainStyle(),
        center: [view.lng, view.lat],
        zoom: view.zoom,
        pitch: 58,
        bearing: -12,
        maxPitch: 80,
        canvasContextAttributes: { antialias: true }
      });
      terrainMap.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'bottom-left');
      terrainMap.on('error', function (event) {
        if (fallbackStarted || (event.sourceId && event.sourceId !== 'terrain')) return;
        terrainErrorCount += 1;
        if (terrainErrorCount >= 3) {
          fallbackStarted = true;
          restoreLeaflet('全球高程服务连续请求失败。', view);
        }
      });
      terrainMap.on('load', function () {
        if (!terrainMap || fallbackStarted) return;
        currentPayload.places.forEach(function (place) {
          var papers = place.papers || currentPayload.papers.filter(function (paper) { return paper.city_id === place.id; });
          createTerrainMarker(maplibregl, place, papers);
        });
        terrainLoading = false;
        status.classList.add('map-status--hidden');
        if (terrainToggle) {
          terrainToggle.disabled = false;
          terrainToggle.setAttribute('aria-pressed', 'true');
          terrainToggle.textContent = '返回 2D';
        }
      });
    } catch (error) {
      restoreLeaflet('浏览器或地形模块未能完成初始化。', view);
    }
  }

  detail.addEventListener('click', function (event) { event.stopPropagation(); });
  detailClose.addEventListener('click', hideDetail);
  hoverCard.addEventListener('mouseenter', function () { clearTimeout(hoverHideTimer); });
  hoverCard.addEventListener('mouseleave', scheduleHideHover);
  hoverCard.addEventListener('click', function () {
    if (activeHoverPlace) showDetail(activeHoverPlace, activeHoverPapers || []);
  });
  hoverCard.addEventListener('keydown', function (event) {
    if ((event.key === 'Enter' || event.key === ' ') && activeHoverPlace) {
      event.preventDefault();
      showDetail(activeHoverPlace, activeHoverPapers || []);
    }
  });
  if (terrainToggle) {
    terrainToggle.addEventListener('click', function () {
      if (terrainMap) {
        restoreLeaflet('', captureTerrainView());
      } else {
        enableTerrain();
      }
    });
  }
  hideDetail();
  hideHover();

  window.MapDataCache.load()
    .then(function (payload) {
      if (!payload.meta.enabled) {
        setStatus('disabled', '地图正在积累可信坐标', '现有坐标尚未达到开放标准。');
        return;
      }
      currentPayload = payload;
      renderMap(payload);
    })
    .catch(function () {
      setStatus('error', '地图暂时没有展开', '地图数据或 Leaflet 加载失败，请稍后重试。');
    });
})();
