const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');

const { selectVideos, extractDownloadUrl, writePool, safePublicUrl, orderCurated } = require('../tools/coverr_video_pool');

const video = (id, overrides = {}) => ({
  id, title: `Landscape ${id}`, duration: 8, max_width: 1920, max_height: 1080,
  aspect_ratio: '16:9', poster: `https://cdn.coverr.co/${id}.jpg`,
  urls: { mp4_download: `https://cdn.coverr.co/${id}.mp4?token=secret`, mp4: `https://cdn.coverr.co/${id}-alt.mp4` },
  ...overrides
});

test('U1 download URL prefers tracked mp4_download and rejects missing video URLs', () => {
  assert.equal(extractDownloadUrl(video('one')), 'https://cdn.coverr.co/one.mp4?token=secret');
  assert.equal(extractDownloadUrl(video('two', { urls: { mp4: 'https://cdn.coverr.co/two.mp4' } })), 'https://cdn.coverr.co/two.mp4');
  assert.equal(extractDownloadUrl(video('three', { urls: {} })), null);
});

test('U2 and U3 only select landscape HD clips in the short-loop duration range', () => {
  const selected = selectVideos([
    video('good'), video('narrow', { max_width: 1280 }),
    video('portrait', { max_width: 1080, max_height: 1920, aspect_ratio: '9:16' }),
    video('long', { duration: 20 }), video('short', { duration: 2 }),
    video('missing', { urls: {} })
  ], { minWidth: 1920, minHeight: 1080, minDuration: 3, maxDuration: 12 });
  assert.deepEqual(selected.map(item => item.id), ['good']);
});

test('U4 successful pool writes only local paths and every manifest asset exists', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'coverr-pool-'));
  try {
    const mp4 = Buffer.from('0000ftypisomvideo-bytes');
    const poster = Buffer.from('poster-bytes');
    const fetcher = async (url) => ({ ok: true, status: 200, headers: new Map([['content-length', String(url.endsWith('.jpg') ? poster.length : mp4.length)]]), arrayBuffer: async () => (url.endsWith('.jpg') ? poster : mp4) });
    const manifest = await writePool([video('one')], { root, fetcher, minItems: 1, maxItems: 1, maxVideoBytes: 1024, maxPoolBytes: 1024, convertPoster: async () => Buffer.from('RIFF0000WEBPposter') });
    assert.equal(manifest.videos.length, 1);
    const entry = manifest.videos[0];
    assert.match(entry.src, /^\/videos\/hero\/[a-z0-9-]+\.mp4$/);
    assert.match(entry.poster, /^\/videos\/hero\/[a-z0-9-]+\.webp$/);
    assert.equal(entry.width, 1920);
    assert.equal(entry.height, 1080);
    assert.equal(entry.duration, 8);
    assert.equal(fs.existsSync(path.join(root, entry.src.slice(1))), true);
    assert.equal(fs.existsSync(path.join(root, entry.poster.slice(1))), true);
    assert.equal(JSON.stringify(manifest).includes('token=secret'), false);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('video pool rejects oversized files without publishing a partial manifest', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'coverr-pool-'));
  try {
    const fetcher = async () => ({ ok: true, status: 200, headers: new Map([['content-length', '999999']]), arrayBuffer: async () => Buffer.alloc(999999) });
    await assert.rejects(writePool([video('one')], { root, fetcher, minItems: 1, maxItems: 1, maxVideoBytes: 100, maxPoolBytes: 100 }));
    assert.equal(fs.existsSync(path.join(root, 'videos/hero/manifest.json')), false);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('manifest path validation rejects remote and traversal paths', () => {
  assert.equal(safePublicUrl('/videos/hero/clip.mp4'), true);
  assert.equal(safePublicUrl('https://api.coverr.co/videos'), false);
  assert.equal(safePublicUrl('/videos/hero/../secret.mp4'), false);
});

test('curation excludes unapproved popular results and preserves editorial order', () => {
  const result = orderCurated([video('car'), video('mountain'), video('city')], ['city', 'mountain']);
  assert.deepEqual(result.map(item => item.id), ['city', 'mountain']);
});

test('successful refresh removes orphaned public video left by a prior run', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'coverr-prune-'));
  try {
    const dir = path.join(root, 'videos', 'hero');
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'orphan.mp4'), 'orphan');
    const mp4 = Buffer.from('0000ftypisomvideo-bytes');
    const fetcher = async () => ({ ok: true, status: 200, headers: new Map(), arrayBuffer: async () => mp4 });
    await writePool([video('one')], { root, fetcher, minItems: 1, maxItems: 1, maxVideoBytes: 1024, maxPoolBytes: 1024, convertPoster: async () => Buffer.from('RIFF0000WEBPposter') });
    assert.equal(fs.existsSync(path.join(dir, 'orphan.mp4')), false);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('oversized high-resolution source is locally transcoded before entering the bounded public pool', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'coverr-transcode-'));
  try {
    const source = Buffer.concat([Buffer.from('0000ftypisom'), Buffer.alloc(150)]);
    const compressed = Buffer.from('0000ftypisomcompressed');
    const fetcher = async () => ({ ok: true, status: 200, headers: new Map(), arrayBuffer: async () => source });
    const manifest = await writePool([video('one')], {
      root, fetcher, minItems: 1, maxItems: 1, maxVideoBytes: 100, maxSourceBytes: 1000,
      maxPoolBytes: 100, transcode: async bytes => { assert.equal(bytes.length, source.length); return compressed; },
      convertPoster: async () => Buffer.from('RIFF0000WEBPposter')
    });
    assert.equal(manifest.videos[0].bytes, compressed.length);
    assert.equal(manifest.videos[0].width, 1280);
    assert.equal(manifest.videos[0].height, 720);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('poster conversion keeps the local WebP small and counts it against total pool bytes', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'coverr-poster-'));
  try {
    const mp4 = Buffer.from('0000ftypisomvideo-bytes');
    const rawPoster = Buffer.alloc(2 * 1024 * 1024, 1);
    const fetcher = async url => ({ ok: true, status: 200, headers: new Map(), arrayBuffer: async () => url.endsWith('.jpg') ? rawPoster : mp4 });
    const manifest = await writePool([video('one')], {
      root, fetcher, minItems: 1, maxItems: 1, maxVideoBytes: 1024, maxPoolBytes: 1024,
      convertPoster: async bytes => { assert.equal(bytes.length, rawPoster.length); return Buffer.from('RIFF0000WEBPposter'); }
    });
    assert.match(manifest.videos[0].poster, /\.webp$/);
    assert.equal(manifest.videos[0].poster_bytes, 18);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('private cache retains only the current approved video IDs after a successful refresh', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'coverr-cache-'));
  try {
    const cacheDir = path.join(root, 'data', 'videos', 'coverr-hero');
    fs.mkdirSync(cacheDir, { recursive: true });
    fs.writeFileSync(path.join(cacheDir, 'old.mp4'), 'obsolete');
    const mp4 = Buffer.from('0000ftypisomvideo-bytes');
    const fetcher = async () => ({ ok: true, status: 200, headers: new Map(), arrayBuffer: async () => mp4 });
    await writePool([video('one')], { root, cacheDir, fetcher, minItems: 1, maxItems: 1, maxVideoBytes: 1024, maxPoolBytes: 1024, convertPoster: async () => Buffer.from('RIFF0000WEBPposter') });
    assert.deepEqual(fs.readdirSync(cacheDir), ['one.mp4']);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
