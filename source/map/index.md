---
title: 论文足迹
date: 2026-10-19 12:00:00
type: page
comments: false
aside: false
top_img: false
---

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css">
<link rel="stylesheet" href="/css/paper-map.css">

<section class="paper-map-shell" aria-label="论文足迹世界地图">
  <div class="map-stage">
    <div id="paper-map" role="application" aria-label="论文机构与会议城市交互地图"></div>
    <div id="map-status" class="map-status" role="status">
      <span class="map-status__pulse" aria-hidden="true"></span>
      <div><strong>正在加载研究坐标</strong><p>地图马上展开。</p></div>
    </div>
    <div class="map-legend" aria-label="地图图例">
      <a href="/map/school/">🎓 高校与科研院所</a>
      <a href="/map/company/">🏢 企业研究机构</a>
      <a href="/map/publisher/">📚 出版与学术组织</a>
      <a href="/map/virtual/">☁ 线上会议</a>
      <a href="/map/venue/">🎤 会议举办地</a>
    </div>
    <div id="map-hover-card" class="map-hover-card" role="button" tabindex="0" aria-label="打开城市详情" aria-hidden="true">
      <img id="map-hover-image" alt="">
      <p id="map-hover-text"></p>
    </div>
    <aside id="map-detail" class="map-detail" aria-hidden="true" aria-live="polite">
      <button id="map-detail-close" class="map-detail__close" type="button" aria-label="关闭城市详情">×</button>
      <div id="map-detail-content"></div>
    </aside>
  </div>
</section>

<script defer src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script defer src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script defer src="/js/map-carto-config.js"></script>
<script defer src="/js/paper-map.js"></script>
