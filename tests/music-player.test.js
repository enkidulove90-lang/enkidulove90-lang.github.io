const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const { JSDOM } = require('jsdom');

const siteRoot = path.resolve(__dirname, '..');
const read = relativePath => fs.readFileSync(path.join(siteRoot, relativePath), 'utf8');

test('internal navigation keeps the music player document alive through Butterfly PJAX', () => {
  const config = read('_config.butterfly.yml');
  assert.match(config, /^pjax:\s*\r?\n\s+enable:\s*true\s*$/m);
});

test('the hover hit area bridges the trigger-to-panel gap', () => {
  const css = read('source/css/music-player.css');
  assert.match(css, /\.mp-widget\s*\{[^}]*padding-bottom:\s*8px;/s);
  assert.match(css, /\.mp-panel\s*\{[^}]*top:\s*calc\(100%\s*-\s*8px\);[^}]*margin-top:\s*8px;/s);
});

test('details expands the full playlist and selecting a song switches playback', () => {
  const dom = new JSDOM('<!doctype html><html><body></body></html>', {
    url: 'https://example.test/',
    runScripts: 'outside-only',
  });
  const played = [];

  class FakeAudio {
    constructor() {
      this.src = '';
      this.paused = true;
      this.currentTime = 0;
      this.volume = 1;
      this.listeners = new Map();
    }

    addEventListener(type, listener) {
      this.listeners.set(type, listener);
    }

    play() {
      this.paused = false;
      played.push(this.src);
      return Promise.resolve();
    }

    pause() {
      this.paused = true;
    }
  }

  dom.window.Audio = FakeAudio;
  vm.runInContext(read('source/js/music-player.js'), dom.getInternalVMContext());
  dom.window.document.dispatchEvent(new dom.window.Event('DOMContentLoaded'));

  const details = dom.window.document.querySelector('[data-act="details"]');
  const list = dom.window.document.querySelector('.mp-playlist');
  assert.ok(details, 'details control should be present');
  assert.ok(list.hidden, 'playlist should start collapsed');

  details.click();
  assert.equal(details.getAttribute('aria-expanded'), 'true');
  assert.equal(list.hidden, false);
  assert.equal(list.querySelectorAll('[data-playlist-index]').length, 6);

  list.querySelector('[data-playlist-index="5"]').click();
  assert.match(dom.window.document.querySelector('.mp-track').textContent, /下个，路口，见/);
  assert.match(played.at(-1), /\/audio\/song6\.mp3$/);
});
