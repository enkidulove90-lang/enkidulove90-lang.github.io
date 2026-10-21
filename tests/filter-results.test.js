const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');

test('homepage exposes a Butterfly-style domain, year, and venue filter above the first article', () => {
  const script = fs.readFileSync(path.join(root, 'source/js/multidim-filter.js'), 'utf8');
  const css = fs.readFileSync(path.join(root, 'source/css/filter.css'), 'utf8');

  assert.match(script, /function buildHomeToolbar/);
  assert.match(script, /md-home-filter/);
  assert.match(script, /data-home-dim="domain"/);
  assert.match(script, /data-home-dim="year"/);
  assert.match(script, /data-home-dim="venue"/);
  assert.match(script, /insertBefore\(toolbar,\s*originalList\)/);
  assert.match(css, /\.md-home-filter/);
});

test('Butterfly author card uses the requested local avatar asset', () => {
  const config = fs.readFileSync(path.join(root, '_config.butterfly.yml'), 'utf8');
  const avatar = path.join(root, 'source/img/avatar-kurisu.jpg');
  assert.match(config, /avatar:[\s\S]*img:\s*\/img\/avatar-kurisu\.jpg/);
  assert.equal(fs.existsSync(avatar), true);
});

function createElement(registry) {
  const element = {
    className: '',
    innerHTML: '',
    isConnected: false,
    style: {},
    onclick: null,
    listeners: {},
    parentNode: null,
    addEventListener(type, handler) {
      this.listeners[type] = handler;
    },
    remove() {
      this.isConnected = false;
      registry.delete(this.id);
    }
  };

  Object.defineProperty(element, 'id', {
    get() { return this._id || ''; },
    set(value) {
      this._id = value;
      if (value) registry.set(value, this);
    }
  });

  return element;
}

async function runSubSelection(attributes, posts, interaction = 'sub') {
  const registry = new Map();
  const main = createElement(registry);
  const originalList = createElement(registry);
  originalList.id = 'recent-posts';
  originalList.isConnected = true;
  originalList.parentNode = main;
  main.firstChild = originalList;
  main.insertBefore = function insertBefore(node) {
    node.isConnected = true;
    node.parentNode = this;
    registry.set(node.id, node);
  };

  const aside = createElement(registry);
  aside.id = 'aside-content';
  aside.firstChild = null;
  aside.querySelector = () => null;
  aside.insertBefore = function insertBefore(node) {
    node.isConnected = true;
    node.parentNode = this;
    registry.set(node.id, node);
  };

  const siteTitle = createElement(registry);
  siteTitle.id = 'site-title';
  siteTitle.textContent = '企业论文';

  const document = {
    readyState: 'complete',
    getElementById(id) { return registry.get(id) || null; },
    querySelector() { return null; },
    createElement() { return createElement(registry); }
  };
  const context = {
    document,
    location: { search: '' },
    URLSearchParams,
    fetch: async () => ({ ok: true, json: async () => ({ posts }) }),
    console
  };

  const script = fs.readFileSync(path.join(root, 'source/js/multidim-filter.js'), 'utf8');
  vm.runInNewContext(script, context);
  await new Promise(resolve => setImmediate(resolve));
  await new Promise(resolve => setImmediate(resolve));

  const active = new Set();
  const group = {
    getAttribute(name) {
      if (name === 'data-group') return attributes['data-val'] || '';
      if (name === 'data-leaf-dim') return attributes['data-dim'] || '';
      if (name === 'data-leaf-val') return attributes['data-val'] || '';
      return null;
    },
    classList: {
      contains(name) { return active.has(name); },
      add(name) { active.add(name); },
      remove(name) { active.delete(name); },
      toggle(name) { active.has(name) ? active.delete(name) : active.add(name); }
    },
    querySelectorAll() { return []; }
  };
  const sub = {
    parentNode: { parentNode: { querySelectorAll() { return [sub]; } } },
    closest(selector) {
      if (interaction === 'leaf' && selector === '.md-group-head') return { parentNode: group };
      return interaction === 'sub' && selector === '.md-sub' ? this : null;
    },
    getAttribute(name) { return attributes[name] || null; },
    classList: {
      contains(name) { return active.has(name); },
      add(name) { active.add(name); },
      remove(name) { active.delete(name); }
    }
  };

  registry.get('md-filter').listeners.click({ target: sub });
  return {
    html: registry.get('md-results').innerHTML,
    title: siteTitle.textContent
  };
}

test('filtered results render a visible Butterfly card with cover and excerpt', async () => {
  const registry = new Map();
  const main = createElement(registry);
  const originalList = createElement(registry);
  originalList.id = 'recent-posts';
  originalList.isConnected = true;
  originalList.parentNode = main;

  main.firstChild = originalList;
  main.insertBefore = function insertBefore(node) {
    node.isConnected = true;
    node.parentNode = this;
    registry.set(node.id, node);
  };

  const document = {
    readyState: 'complete',
    getElementById(id) { return registry.get(id) || null; },
    querySelector() { return null; },
    createElement() { return createElement(registry); }
  };

  const fixture = {
    title: 'A recommender systems paper',
    url: '/papers/recommender-paper/',
    date: '2026-10-16',
    year: '2026',
    venue_type: '会议',
    venue_name: 'RecSys',
    cats: ['推荐系统'],
    tags: ['论文速读'],
    cover: 'https://images.example/recsys.webp',
    excerpt: 'A concise explanation of the paper contribution.'
  };

  const context = {
    document,
    location: { search: '?f_year=2026' },
    URLSearchParams,
    fetch: async () => ({ ok: true, json: async () => ({ posts: [fixture] }) }),
    console
  };

  const script = fs.readFileSync(path.join(root, 'source/js/multidim-filter.js'), 'utf8');
  vm.runInNewContext(script, context);
  await new Promise(resolve => setImmediate(resolve));
  await new Promise(resolve => setImmediate(resolve));

  const results = registry.get('md-results');
  const bar = registry.get('md-active-bar');
  assert.ok(results, 'filter results should be mounted');
  assert.match(results.innerHTML, /class="post_cover/);
  assert.match(results.innerHTML, /src="https:\/\/images\.example\/recsys\.webp"/);
  assert.match(results.innerHTML, /class="content"/);
  assert.match(results.innerHTML, /A concise explanation of the paper contribution\./);
  assert.match(bar.className, /\bis-on\b/);
  assert.equal(originalList.style.display, 'none');
});

test('filter index supplies cover and plain-text excerpt for every post', () => {
  let generator;
  const context = {
    hexo: {
      theme: {
        config: {
          cover: {
            default_cover: [
              'https://images.example/default-1.webp',
              'https://images.example/default-2.webp'
            ]
          }
        }
      },
      extend: {
        generator: {
          register(name, fn) {
            assert.equal(name, 'filter_index');
            generator = fn;
          }
        }
      }
    }
  };

  const script = fs.readFileSync(path.join(root, 'scripts/filter_index.js'), 'utf8');
  vm.runInNewContext(script, context);

  const post = {
    title: 'Rendered paper',
    path: 'papers/rendered-paper/',
    content: '<p>Useful <strong>plain text</strong> summary.</p><a href="https://arxiv.org/abs/2508.04247">paper</a>',
    date: { format(pattern) { return pattern === 'YYYY' ? '2026' : '2026-10-16'; } },
    categories: { toArray() { return [{ name: '推荐系统' }]; } },
    tags: { toArray() { return [{ name: '论文速读' }]; } }
  };
  const locals = { posts: { sort() { return [post]; } } };
  const output = JSON.parse(generator(locals).data);

  assert.equal(output.posts[0].cover, 'https://images.example/default-1.webp');
  assert.equal(output.posts[0].excerpt, 'Useful plain text summary. paper');
  assert.equal(output.posts[0].month, '08', 'paper month should come from its arXiv identity, not the October intake date');
});

test('selecting a venue keeps its type and filters by the concrete venue', async () => {
  const base = {
    date: '2026-10-16', year: '2026', cats: ['推荐系统'], tags: [],
    cover: 'https://images.example/cover.webp', excerpt: 'Summary'
  };
  const { html, title } = await runSubSelection(
    { 'data-dim': 'venueType', 'data-val': 'RecSys', 'data-parent': '会议' },
    [
      { ...base, title: 'RecSys paper', url: '/recsys/', venue_type: '会议', venue_name: 'RecSys' },
      { ...base, title: 'Journal paper', url: '/journal/', venue_type: '期刊', venue_name: 'TOIS' }
    ]
  );

  assert.match(html, /RecSys paper/);
  assert.doesNotMatch(html, /Journal paper/);
  assert.equal(title, 'RecSys');
});

test('selecting a month keeps both year and month constraints', async () => {
  const base = {
    year: '2026', cats: ['推荐系统'], tags: [], venue_type: '会议', venue_name: 'RecSys',
    cover: 'https://images.example/cover.webp', excerpt: 'Summary'
  };
  const { html, title } = await runSubSelection(
    { 'data-dim': 'year', 'data-val': '2026', 'data-month': '07' },
    [
      { ...base, title: 'July paper', url: '/july/', date: '2026-07-15' },
      { ...base, title: 'June paper', url: '/june/', date: '2026-06-20' }
    ]
  );

  assert.match(html, /July paper/);
  assert.doesNotMatch(html, /June paper/);
  assert.equal(title, '2026 年 7 月');
});

test('a domain without children is a selectable leaf instead of an empty accordion', async () => {
  const base = {
    date: '2026-10-16', year: '2026', month: '10', tags: [], venue_type: '随笔', venue_name: '站内随笔',
    cover: 'https://images.example/cover.webp', excerpt: 'Summary'
  };
  const { html, title } = await runSubSelection(
    { 'data-dim': 'domain', 'data-val': '随笔' },
    [
      { ...base, title: 'Hello Rec', url: '/hello-rec/', cats: ['随笔'] },
      { ...base, title: 'A paper', url: '/paper/', cats: ['推荐系统'] }
    ],
    'leaf'
  );

  assert.match(html, /Hello Rec/);
  assert.doesNotMatch(html, /A paper/);
  assert.equal(title, '随笔');
});

test('filter assets are versioned so GitHub Pages does not reuse stale behavior', () => {
  const config = fs.readFileSync(path.join(root, '_config.butterfly.yml'), 'utf8');
  assert.match(config, /filter\.css\?v=[a-z0-9-]+/i);
  assert.match(config, /multidim-filter\.js\?v=[a-z0-9-]+/i);
});

test('desktop pointer navigation is a retractable left-edge drawer', () => {
  const css = fs.readFileSync(path.join(root, 'source/css/left-nav.css'), 'utf8');

  assert.match(css, /@media\s*\(hover:\s*hover\)\s*and\s*\(pointer:\s*fine\)/);
  assert.match(css, /translateX\(calc\(-100%\s*\+\s*var\(--drawer-peek\)\)\)/);
  assert.match(css, /#sidebar:hover\s+#sidebar-menus/);
  assert.match(css, /#sidebar:focus-within\s+#sidebar-menus/);
  assert.match(css, /transition:\s*transform/);
  assert.match(css, /--drawer-peek:\s*54px/);
  assert.match(css, /--drawer-paper:\s*rgba\(255,\s*253,\s*248,\s*0\.78\)/);
  assert.match(css, /font-size:\s*clamp\(36px,\s*2\.8vw,\s*42px\)/);
  assert.match(css, /#sidebar-menus\.open::after\s*\{[^}]*opacity:\s*0/s);
  assert.match(css, /background:\s*rgba\(255,\s*255,\s*255,\s*0\.46\)\s*!important/);
  assert.match(css, /#body-wrap\s*\{[^}]*margin-left:\s*0/s);
  assert.doesNotMatch(css, /margin-left:\s*var\(--/);
});
