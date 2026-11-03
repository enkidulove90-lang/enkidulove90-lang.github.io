const assert = require('node:assert/strict');
const test = require('node:test');
const { JSDOM } = require('jsdom');
const hero = require('../source/js/home-hero-video');

function page({ mobile = false, reduced = false, fetcher, rng = () => 0 } = {}) {
  const dom = new JSDOM('<!doctype html><html><body><header id="page-header" class="full_page"><div id="site-info">Research</div></header></body></html>', { url: 'https://example.test/' });
  const { window } = dom;
  window.HTMLMediaElement.prototype.play = async () => {};
  window.HTMLMediaElement.prototype.pause = () => {};
  window.HTMLMediaElement.prototype.load = () => {};
  Object.defineProperty(window, 'innerWidth', { value: mobile ? 390 : 1280 });
  window.matchMedia = query => ({ matches: reduced && query.includes('reduce'), addEventListener() {} });
  window.fetch = fetcher || (async () => ({ ok: true, json: async () => ({ videos: [{ src: '/videos/hero/one.mp4', poster: '/videos/hero/one.jpg' }, { src: '/videos/hero/two.mp4', poster: '/videos/hero/two.jpg' }] }) }));
  return { dom, window, rng };
}

test('U5 random selection accepts a singleton and produces distinct valid results for different RNG values', () => {
  const one = [{ src: '/videos/hero/one.mp4' }];
  assert.equal(hero.chooseVideo(one, () => 0.9), one[0]);
  const many = [{ src: 'a' }, { src: 'b' }, { src: 'c' }];
  assert.equal(hero.chooseVideo(many, () => 0).src, 'a');
  assert.equal(hero.chooseVideo(many, () => 0.99).src, 'c');
});

test('I1 desktop homepage creates a muted inline autoplay loop with poster', async () => {
  const { window, rng } = page();
  await hero.mountHeroVideo(window, { rng });
  const video = window.document.querySelector('#page-header video');
  assert.ok(video);
  assert.equal(video.autoplay, true);
  assert.equal(video.muted, true);
  assert.equal(video.loop, true);
  assert.equal(video.playsInline, true);
  assert.equal(video.getAttribute('poster'), '/videos/hero/one.jpg');
  assert.equal(video.getAttribute('src'), '/videos/hero/one.mp4');
  assert.equal(window.document.querySelector('.home-hero-coverr-credit img')?.getAttribute('src'), '/img/coverr-logo-white.svg');
});

test('I2 video error restores visible original header background without removing layout', async () => {
  const { window, rng } = page();
  await hero.mountHeroVideo(window, { rng });
  const header = window.document.querySelector('#page-header');
  const video = header.querySelector('video');
  video.dispatchEvent(new window.Event('error'));
  assert.equal(header.querySelector('video'), null);
  assert.ok(header.querySelector('#site-info'));
  assert.equal(header.classList.contains('hero-video-active'), false);
});

test('I3 reduced motion skips manifest and never sets a video source', async () => {
  let calls = 0;
  const { window, rng } = page({ reduced: true, fetcher: async () => { calls++; throw Error('not expected'); } });
  await hero.mountHeroVideo(window, { rng });
  assert.equal(calls, 0);
  assert.equal(window.document.querySelector('video'), null);
});

test('I4 mobile width skips manifest and full MP4', async () => {
  let calls = 0;
  const { window, rng } = page({ mobile: true, fetcher: async () => { calls++; throw Error('not expected'); } });
  await hero.mountHeroVideo(window, { rng });
  assert.equal(calls, 0);
  assert.equal(window.document.querySelector('video'), null);
});

test('runtime ignores non-local manifest URLs and keeps fallback', async () => {
  const { window, rng } = page({ fetcher: async () => ({ ok: true, json: async () => ({ videos: [{ src: 'https://cdn.coverr.co/secret.mp4', poster: '/videos/hero/one.jpg' }] }) }) });
  await hero.mountHeroVideo(window, { rng });
  assert.equal(window.document.querySelector('video'), null);
});

test('autoplay rejection restores the static header image', async () => {
  const { window, rng } = page();
  window.HTMLMediaElement.prototype.play = async () => { throw new Error('NotAllowedError'); };
  await hero.mountHeroVideo(window, { rng });
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.equal(window.document.querySelector('#page-header video'), null);
});
