(function (root) {
  'use strict';
  var KEY = 'paper-map-data:v1';
  var TTL = 60 * 60 * 1000;
  var pending = null;

  function read() {
    try { return JSON.parse(root.localStorage.getItem(KEY) || 'null'); }
    catch (_) { return null; }
  }

  function load() {
    var cached = read();
    if (cached && cached.savedAt && Date.now() - cached.savedAt < TTL) {
      return Promise.resolve(cached.payload);
    }
    if (pending) return pending;
    pending = root.fetch('/map_data.json', { cache: 'default' })
      .then(function (response) {
        if (!response.ok) throw new Error('map data request failed');
        return response.json();
      })
      .then(function (payload) {
        try { root.localStorage.setItem(KEY, JSON.stringify({ savedAt: Date.now(), payload: payload })); }
        catch (_) { /* storage quota/private mode: network result still works */ }
        return payload;
      })
      .catch(function (error) {
        if (cached && cached.payload) return cached.payload; // stale cache is safer than an empty map
        throw error;
      })
      .finally(function () { pending = null; });
    return pending;
  }

  function observeImages(container) {
    var images = Array.from((container || document).querySelectorAll('img[data-src]'));
    function reveal(image) { image.src = image.dataset.src; image.removeAttribute('data-src'); }
    if (!('IntersectionObserver' in root)) { images.forEach(reveal); return; }
    var observer = new root.IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        reveal(entry.target);
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '240px 0px' });
    images.forEach(function (image) { observer.observe(image); });
  }

  root.MapDataCache = { load: load, observeImages: observeImages, ttl: TTL };
})(window);
