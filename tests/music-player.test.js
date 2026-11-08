const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

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
