(function () {
  'use strict';

  var root = document.getElementById('paper-map');
  if (!root) return;
  var status = document.getElementById('map-status');
  var detail = document.getElementById('map-detail');
  var detailContent = document.getElementById('map-detail-content');
  var detailClose = document.getElementById('map-detail-close');
  var hoverCard = document.getElementById('map-hover-card');
  var hoverImage = document.getElementById('map-hover-image');
  var hoverText = document.getElementById('map-hover-text');
  var runtimeConfig = window.__PAPER_MAP_CONFIG__ || {};
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
    var images = Array.from(new Set((place.city_images || [place.image]).filter(Boolean)));
    var frame = document.createElement('figure');
    var image = document.createElement('img');
    var count = document.createElement('figcaption');
    var active = 0;
    frame.className = 'map-place-carousel';
    image.src = images[0] || place.image;
    image.alt = place.name + '城市图景';
    image.decoding = 'async';
    count.className = 'map-place-carousel__count';
    count.textContent = '1 / ' + Math.max(images.length, 1);
    frame.append(image, count);
    if (images.length > 1) {
      carouselTimer = setInterval(function () {
        var next = (active + 1) % images.length;
        var nextImage = new Image();
        nextImage.decoding = 'async';
        nextImage.onload = function () {
          active = next;
          image.classList.add('is-switching');
          image.src = nextImage.src;
          count.textContent = (active + 1) + ' / ' + images.length;
          requestAnimationFrame(function () { image.classList.remove('is-switching'); });
        };
        nextImage.src = images[next];
      }, 1000);
    }
    return frame;
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
    title.textContent = place.name + '：' + (CITY_TAGLINES[place.name] || '研究发生之地');
    description.className = 'map-place-card__description';
    description.textContent = place.description || '';
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
    hoverText.textContent = place.hover_text || place.description || place.name;
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

  function renderMap(payload) {
    if (!window.L) throw new Error('Leaflet failed to load');
    var L = window.L;
    var map = L.map('paper-map', { zoomControl: true, worldCopyJump: true, minZoom: 2 }).setView([25, 15], 2);
    var physicalUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}';
    var osmUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
    var osmAttribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
    var physicalAttribution = 'Powered by <a href="https://www.esri.com/">Esri</a> · Source: US National Park Service';
    var cartoAttribution = osmAttribution + ', &copy; <a href="https://carto.com/attribution/">CARTO</a>';
    var tileMode = 'physical';
    var tiles = L.tileLayer(physicalUrl, {
      maxNativeZoom: 8, maxZoom: 12, attribution: physicalAttribution,
      updateWhenIdle: true, keepBuffer: 2, detectRetina: false
    });

    function useFallback() {
      map.removeLayer(tiles);
      if (tileMode === 'physical' && runtimeConfig.cartoApiKey) {
        tileMode = 'carto';
        tiles = L.tileLayer(
          'https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png?key=' +
            encodeURIComponent(runtimeConfig.cartoApiKey),
          { maxZoom: 20, attribution: cartoAttribution, updateWhenIdle: true, keepBuffer: 2 }
        );
      } else if (tileMode !== 'osm') {
        tileMode = 'osm';
        tiles = L.tileLayer(osmUrl, { maxZoom: 19, attribution: osmAttribution, updateWhenIdle: true, keepBuffer: 2 });
      } else {
        setStatus('error', '底图暂时不可用', '论文坐标仍然完整，请稍后刷新。');
        return;
      }
      tiles.once('tileerror', useFallback);
      tiles.addTo(map);
    }

    tiles.once('tileerror', useFallback);
    tiles.addTo(map);
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

    if (markers.length > 1) {
      map.fitBounds(L.featureGroup(markers).getBounds(), { padding: [48, 48], maxZoom: 5 });
    }
    status.classList.add('map-status--hidden');
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
  hideDetail();
  hideHover();

  fetch('/map_data.json', { cache: 'default' })
    .then(function (response) {
      if (!response.ok) throw new Error('map data request failed');
      return response.json();
    })
    .then(function (payload) {
      if (!payload.meta.enabled) {
        setStatus('disabled', '地图正在积累可信坐标', '现有坐标尚未达到开放标准。');
        return;
      }
      renderMap(payload);
    })
    .catch(function () {
      setStatus('error', '地图暂时没有展开', '地图数据或 Leaflet 加载失败，请稍后重试。');
    });
})();
