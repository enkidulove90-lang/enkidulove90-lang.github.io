(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && root.document) {
    const start = () => api.mountHeroVideo(root).catch(() => {});
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', start, { once: true });
    else start();
  }
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  function chooseVideo(videos, rng = Math.random) {
    if (!Array.isArray(videos) || videos.length === 0) return null;
    const value = Number(rng());
    const index = Math.min(videos.length - 1, Math.max(0, Math.floor((Number.isFinite(value) ? value : 0) * videos.length)));
    return videos[index];
  }

  function localAsset(path, extension) {
    return typeof path === 'string' && new RegExp(`^/videos/hero/[a-z0-9-]+\\.${extension}$`).test(path);
  }

  async function mountHeroVideo(win, options = {}) {
    const doc = win.document;
    if (win.location.pathname !== '/' || win.innerWidth < 768 ||
      win.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return false;
    const header = doc.querySelector('#page-header.full_page');
    if (!header || header.querySelector('.home-hero-video')) return false;

    let response;
    try { response = await win.fetch('/videos/hero/manifest.json', { cache: 'no-cache' }); }
    catch { return false; }
    if (!response.ok) return false;
    let manifest;
    try { manifest = await response.json(); }
    catch { return false; }
    const valid = (manifest.videos || []).filter(item =>
      localAsset(item.src, 'mp4') && localAsset(item.poster, '(?:jpg|jpeg|webp)'));
    const item = chooseVideo(valid, options.rng || Math.random);
    if (!item) return false;

    const video = doc.createElement('video');
    video.className = 'home-hero-video';
    video.autoplay = true;
    video.muted = true;
    video.defaultMuted = true;
    video.loop = true;
    video.playsInline = true;
    video.setAttribute('autoplay', '');
    video.setAttribute('muted', '');
    video.setAttribute('loop', '');
    video.setAttribute('playsinline', '');
    video.setAttribute('webkit-playsinline', '');
    video.setAttribute('preload', 'metadata');
    video.setAttribute('aria-hidden', 'true');
    video.setAttribute('poster', item.poster);
    video.setAttribute('src', item.src);

    const credit = doc.createElement('a');
    credit.className = 'home-hero-coverr-credit';
    credit.href = 'https://coverr.co/';
    credit.target = '_blank';
    credit.rel = 'noopener noreferrer';
    credit.setAttribute('aria-label', 'Video via Coverr');
    const logo = doc.createElement('img');
    logo.src = '/img/coverr-logo-white.svg';
    logo.alt = 'Coverr';
    credit.append(logo);
    const fallback = () => {
      video.pause();
      video.removeAttribute('src');
      video.load?.();
      video.remove();
      credit.remove();
      header.classList.remove('hero-video-active');
    };
    video.addEventListener('error', fallback, { once: true });
    header.prepend(video);
    header.append(credit);
    header.classList.add('hero-video-active');

    const media = win.matchMedia?.('(prefers-reduced-motion: reduce)');
    media?.addEventListener?.('change', event => { if (event.matches) fallback(); });
    try {
      const attempt = video.play?.();
      if (attempt?.catch) attempt.catch(fallback);
    } catch { fallback(); }
    return true;
  }

  return { chooseVideo, mountHeroVideo };
});
