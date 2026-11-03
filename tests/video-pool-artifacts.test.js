const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');
const test = require('node:test');

const root = path.resolve(__dirname, '..');

test('committed hero pool has five to eight valid local clips within its total byte budget', () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'source/videos/hero/manifest.json'), 'utf8'));
  assert.ok(manifest.videos.length >= 5 && manifest.videos.length <= 8);
  let total = 0;
  for (const item of manifest.videos) {
    assert.match(item.src, /^\/videos\/hero\/[a-z0-9-]+\.mp4$/);
    assert.match(item.poster, /^\/videos\/hero\/[a-z0-9-]+\.webp$/);
    const video = fs.readFileSync(path.join(root, 'source', item.src.slice(1)));
    const poster = fs.readFileSync(path.join(root, 'source', item.poster.slice(1)));
    assert.equal(video.toString('ascii', 4, 8), 'ftyp');
    assert.equal(poster.toString('ascii', 0, 4), 'RIFF');
    assert.equal(video.length, item.bytes);
    assert.equal(poster.length, item.poster_bytes);
    assert.equal(crypto.createHash('sha256').update(video).digest('hex'), item.sha256);
    assert.ok(video.length <= 8 * 1024 * 1024);
    total += video.length + poster.length;
  }
  assert.ok(total <= 40 * 1024 * 1024);
  assert.equal(JSON.stringify(manifest).includes('token='), false);
  assert.equal(JSON.stringify(manifest).includes('api.coverr.co'), false);
});

test('private original-video cache is not tracked by Git', () => {
  const tracked = execFileSync('git', ['ls-files', 'data/videos'], { cwd: root, encoding: 'utf8' });
  assert.equal(tracked.trim(), '');
});
