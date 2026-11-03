#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const os = require('node:os');
const { spawn } = require('node:child_process');

const API_URL = 'https://api.coverr.co/videos';
const DEFAULTS = Object.freeze({
  minWidth: 1920, minHeight: 1080, minDuration: 3, maxDuration: 12,
  minItems: 5, maxItems: 8, maxVideoBytes: 8 * 1024 * 1024,
  maxPoolBytes: 40 * 1024 * 1024, maxSourceBytes: 80 * 1024 * 1024,
  maxPosterSourceBytes: 8 * 1024 * 1024, maxPosterBytes: 500 * 1024
});

function extractDownloadUrl(item) {
  const raw = item?.urls?.mp4_download || item?.urls?.mp4;
  if (typeof raw !== 'string') return null;
  try {
    const url = new URL(raw);
    return url.protocol === 'https:' ? url.href : null;
  } catch { return null; }
}

function selectVideos(items, options = {}) {
  const settings = { ...DEFAULTS, ...options };
  if (!Array.isArray(items)) return [];
  const seen = new Set();
  return items.filter(item => {
    const id = String(item?.id || '');
    const width = Number(item?.max_width);
    const height = Number(item?.max_height);
    const duration = Number(item?.duration);
    const aspect = width / height;
    const good = id && !seen.has(id) && extractDownloadUrl(item) &&
      width >= settings.minWidth && height >= settings.minHeight &&
      aspect >= 1.7 && aspect <= 1.85 &&
      duration >= settings.minDuration && duration <= settings.maxDuration &&
      typeof item.poster === 'string' && item.poster.startsWith('https://');
    if (good) seen.add(id);
    return Boolean(good);
  });
}

function safePublicUrl(value) {
  return typeof value === 'string' && /^\/videos\/hero\/[a-z0-9-]+\.(?:mp4|jpg|jpeg|webp)$/.test(value);
}

function orderCurated(items, ids) {
  const indexed = new Map(items.map(item => [String(item.id), item]));
  return ids.map(id => indexed.get(String(id))).filter(Boolean);
}

async function fetchBounded(fetcher, url, maxBytes) {
  const response = await fetcher(url, { redirect: 'follow', signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`Asset HTTP ${response.status}`);
  const length = Number(response.headers?.get?.('content-length'));
  if (Number.isFinite(length) && length > maxBytes) throw new Error('Asset exceeds byte limit');
  let buffer;
  if (response.body?.getReader) {
    const reader = response.body.getReader();
    const chunks = [];
    let size = 0;
    try {
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        size += value.byteLength;
        if (size > maxBytes) throw new Error('Asset exceeds byte limit');
        chunks.push(Buffer.from(value));
      }
    } finally { await reader.cancel().catch(() => {}); }
    buffer = Buffer.concat(chunks);
  } else {
    buffer = Buffer.from(await response.arrayBuffer());
  }
  if (!buffer.length || buffer.length > maxBytes) throw new Error('Asset exceeds byte limit');
  return buffer;
}

function validMp4(bytes) {
  return bytes.length > 12 && bytes.toString('ascii', 4, 8) === 'ftyp';
}

function ffmpegPath() {
  if (process.env.FFMPEG_PATH) return process.env.FFMPEG_PATH;
  try { return require('ffmpeg-static'); }
  catch { return 'ffmpeg'; }
}

async function transcodePoster(bytes) {
  const dir = await fs.promises.mkdtemp(path.join(os.tmpdir(), 'coverr-poster-'));
  const input = path.join(dir, 'input.png');
  const output = path.join(dir, 'output.webp');
  try {
    await fs.promises.writeFile(input, bytes);
    await new Promise((resolve, reject) => {
      const child = spawn(ffmpegPath(), ['-hide_banner', '-loglevel', 'error', '-y', '-i', input,
        '-frames:v', '1', '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease', '-q:v', '70', output],
      { windowsHide: true, stdio: 'ignore' });
      child.once('error', reject);
      child.once('close', code => code === 0 ? resolve() : reject(new Error('FFmpeg poster conversion failed')));
    });
    return await fs.promises.readFile(output);
  } finally {
    await fs.promises.unlink(input).catch(() => {});
    await fs.promises.unlink(output).catch(() => {});
    await fs.promises.rmdir(dir).catch(() => {});
  }
}

async function transcodeVideo(bytes) {
  const ffmpeg = ffmpegPath();
  const dir = await fs.promises.mkdtemp(path.join(os.tmpdir(), 'coverr-transcode-'));
  const input = path.join(dir, 'input.mp4');
  const output = path.join(dir, 'output.mp4');
  try {
    await fs.promises.writeFile(input, bytes);
    await new Promise((resolve, reject) => {
      const args = ['-hide_banner', '-loglevel', 'error', '-y', '-i', input,
        '-t', '12', '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2',
        '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '30', '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart', output];
      const child = spawn(ffmpeg, args, { windowsHide: true, stdio: 'ignore' });
      child.once('error', reject);
      child.once('close', code => code === 0 ? resolve() : reject(new Error('FFmpeg transcoding failed')));
    });
    return await fs.promises.readFile(output);
  } finally {
    await fs.promises.unlink(input).catch(() => {});
    await fs.promises.unlink(output).catch(() => {});
    await fs.promises.rmdir(dir).catch(() => {});
  }
}

async function writePool(candidates, options = {}) {
  const settings = { ...DEFAULTS, ...options };
  const root = path.resolve(settings.root || path.join(__dirname, '..', 'source'));
  const fetcher = settings.fetcher || fetch;
  const output = path.join(root, 'videos', 'hero');
  const cacheDir = settings.cacheDir ? path.resolve(settings.cacheDir) : null;
  await fs.promises.mkdir(output, { recursive: true });
  if (cacheDir) await fs.promises.mkdir(cacheDir, { recursive: true });
  const chosen = selectVideos(candidates, settings);
  const videos = [];
  let poolBytes = 0;
  for (const item of chosen) {
    if (videos.length >= settings.maxItems) break;
    const id = String(item.id).toLowerCase().replace(/[^a-z0-9-]/g, '-').slice(0, 64);
    if (!id) continue;
    try {
      const source = await fetchBounded(fetcher, extractDownloadUrl(item), settings.maxSourceBytes);
      if (!validMp4(source)) throw new Error('Asset is not MP4');
      const resized = source.length > settings.maxVideoBytes;
      const mp4 = resized ? await (settings.transcode || transcodeVideo)(source) : source;
      if (!validMp4(mp4) || mp4.length > settings.maxVideoBytes) throw new Error('Transcoded MP4 exceeds byte limit');
      if (poolBytes + mp4.length > settings.maxPoolBytes) continue;
      const posterUrl = new URL(item.poster);
      const posterSource = await fetchBounded(fetcher, posterUrl.href, settings.maxPosterSourceBytes);
      const poster = await (settings.convertPoster || transcodePoster)(posterSource);
      if (poster.toString('ascii', 0, 4) !== 'RIFF' || poster.toString('ascii', 8, 12) !== 'WEBP' || poster.length > settings.maxPosterBytes) {
        throw new Error('Poster conversion exceeds byte limit');
      }
      if (poolBytes + mp4.length + poster.length > settings.maxPoolBytes) continue;
      const filename = `${id}.mp4`;
      const posterName = `${id}.webp`;
      await fs.promises.writeFile(path.join(output, `${filename}.tmp`), mp4);
      await fs.promises.rename(path.join(output, `${filename}.tmp`), path.join(output, filename));
      await fs.promises.writeFile(path.join(output, `${posterName}.tmp`), poster);
      await fs.promises.rename(path.join(output, `${posterName}.tmp`), path.join(output, posterName));
      if (cacheDir) await fs.promises.copyFile(path.join(output, filename), path.join(cacheDir, filename));
      poolBytes += mp4.length + poster.length;
      videos.push({
        id, title: String(item.title || '').slice(0, 120),
        src: `/videos/hero/${filename}`, poster: `/videos/hero/${posterName}`,
        width: resized ? 1280 : Number(item.max_width), height: resized ? 720 : Number(item.max_height), duration: Number(item.duration),
        bytes: mp4.length, poster_bytes: poster.length,
        sha256: crypto.createHash('sha256').update(mp4).digest('hex'),
        attribution: 'Coverr'
      });
    } catch (error) {
      // Signed download URLs and response bodies must never enter build output or logs.
      if (settings.onSkip) settings.onSkip({ id, reason: /limit|FFmpeg|MP4|HTTP/.test(error.message) ? error.message : 'download_or_transcode_failed' });
    }
  }
  if (videos.length < settings.minItems) {
    throw new Error(`Only ${videos.length} valid clips; need ${settings.minItems}. Previous manifest was left untouched.`);
  }
  const manifest = { schema_version: 1, generated_at: new Date().toISOString(), videos };
  const temp = path.join(output, 'manifest.json.tmp');
  await fs.promises.writeFile(temp, JSON.stringify(manifest, null, 2) + '\n');
  await fs.promises.rename(temp, path.join(output, 'manifest.json'));
  const active = new Set(videos.flatMap(item => [path.basename(item.src), path.basename(item.poster)]));
  for (const entry of await fs.promises.readdir(output)) {
    if (/^[a-z0-9-]+\.(?:mp4|jpe?g|webp)$/.test(entry) && !active.has(entry)) {
      await fs.promises.unlink(path.join(output, entry));
    }
  }
  if (cacheDir && path.basename(cacheDir) === 'coverr-hero') {
    const activeVideos = new Set(videos.map(item => path.basename(item.src)));
    for (const entry of await fs.promises.readdir(cacheDir)) {
      if (/^[a-z0-9-]+\.mp4$/.test(entry) && !activeVideos.has(entry)) {
        await fs.promises.unlink(path.join(cacheDir, entry));
      }
    }
  }
  return manifest;
}

function readEnvFile(filename) {
  if (!filename) return {};
  const result = {};
  for (const line of fs.readFileSync(filename, 'utf8').split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Z][A-Z0-9_]*)\s*=\s*(.*)\s*$/);
    if (match) result[match[1]] = match[2].replace(/^['"]|['"]$/g, '');
  }
  return result;
}

async function refresh() {
  const args = process.argv.slice(2);
  const envIndex = args.indexOf('--env-file');
  const envFile = envIndex >= 0 ? args[envIndex + 1] : null;
  const env = { ...readEnvFile(envFile), ...process.env };
  if (!env.COVERR_API_KEY) throw new Error('COVERR_API_KEY missing; use --env-file or environment variable');
  const selectedIds = require('./coverr_hero_selection.json');
  const items = [];
  for (const id of selectedIds) {
    const url = new URL(`${API_URL}/${encodeURIComponent(id)}`);
    const response = await fetch(url, { headers: { Authorization: `Bearer ${env.COVERR_API_KEY}` }, signal: AbortSignal.timeout(30000) });
    if (!response.ok) throw new Error(`Coverr API HTTP ${response.status}`);
    items.push(await response.json());
  }
  const curated = orderCurated(items, selectedIds);
  const root = path.join(__dirname, '..');
  const manifest = await writePool(curated, {
    root: path.join(root, 'source'), cacheDir: path.join(root, 'data', 'videos', 'coverr-hero'),
    onSkip: item => process.stderr.write(`Skipped ${item.id}: ${item.reason}\n`)
  });
  process.stdout.write(`Reviewed ${items.length}; eligible ${selectVideos(curated).length}; downloaded ${manifest.videos.length}; manifest source/videos/hero/manifest.json; pool bytes ${manifest.videos.reduce((sum, item) => sum + item.bytes + item.poster_bytes, 0)}\n`);
}

if (require.main === module) refresh().catch(error => {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
});

module.exports = { extractDownloadUrl, selectVideos, safePublicUrl, orderCurated, writePool, readEnvFile };
