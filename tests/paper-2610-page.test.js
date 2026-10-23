const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const Hexo = require('hexo');
const { JSDOM } = require('jsdom');

const root = path.resolve(__dirname, '..');
const scriptPath = path.join(root, 'source/js/paper-2610.05432.js');
const cssPath = path.join(root, 'source/css/paper-2610.05432.css');

function loadScript(pathname) {
  const appended = [];
  const listeners = {};
  const body = {
    classes: new Set(),
    classList: {
      add(value) { body.classes.add(value); },
      remove(value) { body.classes.delete(value); }
    }
  };
  const nodes = new Map();
  const document = {
    body,
    head: { appendChild(node) { appended.push(node); if (node.id) nodes.set(node.id, node); } },
    createElement(tagName) { return { tagName, id: '', rel: '', href: '', src: '', async: false, onload: null, onerror: null }; },
    getElementById(id) { return nodes.get(id) || null; },
    addEventListener(name, callback) { listeners[name] = callback; }
  };
  const window = { document, location: { pathname } };
  const context = { window, document, module: { exports: {} }, exports: {} };
  vm.runInNewContext(fs.readFileSync(scriptPath, 'utf8'), context, { filename: scriptPath });
  return { api: context.module.exports, appended, body, window, listeners };
}

test('route guard matches canonical paper article routes after URL normalization', () => {
  const { api } = loadScript('/control/');
  assert.equal(api.isTargetUrl('/article/paper-2610.05432/'), true);
  assert.equal(api.isTargetUrl('/article/paper-2610.05432?view=1#method'), true);
  assert.equal(api.isTargetUrl('/article/paper-2610.05432///'), true);
  assert.equal(api.isTargetUrl('/article/paper-2608.17316/'), true);
  assert.equal(api.isTargetUrl('/article/paper-2610.05432-extra/'), false);
  assert.equal(api.isTargetUrl('/article/control/'), false);
});

test('target route adds its class, stylesheet, and MathJax exactly once', () => {
  const page = loadScript('/article/paper-2610.05432/');
  page.api.applyTargetEnhancements();
  page.api.applyTargetEnhancements();

  assert.equal(page.body.classes.has('paper-2610-05432'), true);
  assert.equal(page.appended.filter(node => node.id === 'paper-2610-05432-css').length, 1);
  assert.equal(page.appended.filter(node => node.id === 'paper-2610-05432-mathjax').length, 1);
  const loader = page.appended.find(node => node.id === 'paper-2610-05432-mathjax');
  assert.equal(loader.src, '/js/vendor/mathjax/tex-svg.js');
  assert.equal(typeof loader.onload, 'function');
  assert.equal(typeof loader.onerror, 'function');
  assert.deepEqual(
    JSON.parse(JSON.stringify(page.window.MathJax.tex.inlineMath)),
    [['$', '$'], ['\\(', '\\)']]
  );
  assert.deepEqual(
    JSON.parse(JSON.stringify(page.window.MathJax.tex.displayMath)),
    [['$$', '$$'], ['\\[', '\\]']]
  );
});

test('MathJax is re-typeset after the self-hosted loader finishes', async () => {
  const page = loadScript('/article/paper-2610.05432/');
  const loader = page.appended.find(node => node.id === 'paper-2610-05432-mathjax');
  let calls = 0;
  page.window.MathJax.typesetPromise = elements => {
    calls += 1;
    assert.equal(elements[0], page.window.document.body);
    return Promise.resolve();
  };

  loader.onload();
  await Promise.resolve();

  assert.equal(calls, 1);
});

test('MathJax load failure becomes visible instead of silently leaving raw formulas', () => {
  const page = loadScript('/article/paper-2610.05432/');
  const loader = page.appended.find(node => node.id === 'paper-2610-05432-mathjax');

  loader.onerror();

  assert.equal(page.body.classes.has('paper-math-load-failed'), true);
});

test('target route re-typesets the complete article when MathJax is already loaded', async () => {
  const page = loadScript('/article/paper-2610.05432/');
  let calls = 0;
  page.window.MathJax = {
    typesetPromise(elements) {
      calls += 1;
      assert.equal(elements.length, 1);
      assert.equal(elements[0], page.window.document.body);
      return Promise.resolve();
    }
  };

  page.api.applyTargetEnhancements();
  await Promise.resolve();

  assert.equal(calls, 1);
});

test('other paper routes receive MathJax but not OpticalRec-only styling', () => {
  const page = loadScript('/article/paper-2608.17316/');
  page.api.applyTargetEnhancements();

  assert.equal(page.body.classes.has('paper-2610-05432'), false);
  assert.equal(page.appended.some(node => node.id === 'paper-2610-05432-css'), false);
  assert.equal(page.appended.filter(node => node.id === 'paper-2610-05432-mathjax').length, 1);
  assert.ok(page.window.MathJax);
});

test('all typography selectors are target scoped with the requested font stacks', () => {
  const css = fs.readFileSync(cssPath, 'utf8');
  const selectors = css
    .split('}')
    .map(block => block.split('{', 1)[0].trim())
    .filter(Boolean);

  assert.ok(selectors.length >= 4);
  for (const group of selectors) {
    for (const selector of group.split(',')) {
      assert.match(selector.trim(), /^body\.paper-2610-05432\b/);
    }
  }
  assert.match(css, /SimHei/);
  assert.match(css, /Heiti SC/);
  assert.match(css, /SimSun/);
  assert.match(css, /Songti SC/);
  assert.match(css, /Times New Roman/);
  assert.doesNotMatch(css, /(^|})\s*\.post-content\s*\{/m);
});

test('the injected bootstrap is deferred and configures literal formula delimiters', () => {
  const config = fs.readFileSync(path.join(root, '_config.butterfly.yml'), 'utf8');
  const script = fs.readFileSync(scriptPath, 'utf8');

  assert.ok(config.includes('<script defer src="/js/paper-2610.05432.js?v=math-v4"></script>'));
  assert.ok(script.includes("inlineMath: [['$', '$'], ['\\\\(', '\\\\)']]"));
  assert.ok(script.includes("displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]"));
  assert.doesNotMatch(script, /cdn\.jsdelivr|cdnjs|unpkg/);
  assert.equal(fs.existsSync(path.join(root, 'source/js/vendor/mathjax/tex-svg.js')), true);
});

test('OpticalRec section headings use names without Chinese numeric prefixes', () => {
  const article = fs.readFileSync(path.join(root, 'source/_posts/paper-2610.05432.md'), 'utf8');

  assert.match(article, /^## 研究背景与问题$/m);
  assert.match(article, /^## 方法$/m);
  assert.match(article, /^## 实验$/m);
  assert.match(article, /^## 总结$/m);
  assert.doesNotMatch(article, /^##\s+[一二三四]、/m);
});

test('every listed OpticalRec reference has a clickable title and verified code is appended', () => {
  const article = fs.readFileSync(path.join(root, 'source/_posts/paper-2610.05432.md'), 'utf8');
  const references = article
    .split('## References', 2)[1]
    .replace(/<!--[\s\S]*?-->/g, '');
  assert.ok(references);
  const entries = references.split(/\r?\n/).filter(line => line.startsWith('- '));

  assert.equal(entries.length, 3);
  for (const entry of entries) {
    assert.match(entry, /\[[^\]]+\]\(https:\/\/(?:arxiv\.org\/abs\/|doi\.org\/)/);
  }
  assert.match(
    references,
    /Sink-token-aware pruning[^\n]+代码：\[https:\/\/github\.com\/rlqja1107\/SToP\]/i
  );
  assert.match(references, /\[OpticalRec: Unified Optical Vision-Language Representation/);
});

test('Hexo preserves inline and display formula delimiters for MathJax', async () => {
  const hexo = new Hexo(root, { silent: true });
  await hexo.init();
  try {
    const html = await hexo.render.render({
      text: 'inline $x_i$\n\n$$\\sum_i p_i$$',
      engine: 'md'
    });
    assert.match(html, /\$x_i\$/);
    assert.match(html, /\$\$\\sum_i p_i\$\$/);
  } finally {
    await hexo.exit();
  }
});

test('Hexo protects real OpticalRec formulas from Markdown emphasis parsing', async () => {
  const hexo = new Hexo(root, { silent: true });
  await hexo.init();
  try {
    const { protectMath } = require(path.join(root, 'scripts/opticalrec-math.js'));
    const content = protectMath([
        '$$',
        '\\mathbf{q}_i = f(\\mathbf{v}_i, \\mathbf{t}_i), \\quad \\mathbf{p}_u = \\mathcal{A}(\\{\\mathbf{q}_i\\}_{i\\in\\mathcal{N}_u})',
        '$$',
        '',
        '行内公式 $y_{ui}=\\langle \\mathbf{p}_u, \\mathbf{q}_i\\rangle$。'
      ].join('\n'));
    const html = await hexo.render.render({
      text: content,
      engine: 'md'
    });

    assert.doesNotMatch(html, /<em>/);
    assert.match(html, /class="math-display"/);
    assert.match(html, /class="math-inline"/);
    assert.match(html, /\\mathbf\{q\}_i/);
  } finally {
    await hexo.exit();
  }
});

test('Hexo protects every supported LaTeX delimiter across the OpticalRec article', async () => {
  const hexo = new Hexo(root, { silent: true });
  await hexo.init();
  try {
    const { protectMath } = require(path.join(root, 'scripts/opticalrec-math.js'));
    const content = protectMath([
      '美元行内 $x_i$。',
      '括号行内 \\(\\mathbf{q}_i \\to \\mathbf{z}_i\\)。',
      '',
      '$$\\sum_i p_i \\log p_i$$',
      '',
      '\\[I(\\mathbf{q}_i;\\mathbf{x}_i)=\\mathcal{I}_{\\mathrm{cross}}\\]'
    ].join('\n'));
    const html = await hexo.render.render({ text: content, engine: 'md' });

    assert.equal((html.match(/class="math-inline"/g) || []).length, 2);
    assert.equal((html.match(/class="math-display"/g) || []).length, 2);
    assert.doesNotMatch(html, /<em>/);
    assert.match(html, /\\mathbf\{q\}_i/);
    assert.match(html, /\\mathcal\{I\}_\{\\mathrm\{cross\}\}/);
  } finally {
    await hexo.exit();
  }
});

test('rendered inline formulas retain literal MathJax delimiters in the browser DOM', async () => {
  const hexo = new Hexo(root, { silent: true });
  await hexo.init();
  try {
    const { protectMath } = require(path.join(root, 'scripts/opticalrec-math.js'));
    const html = await hexo.render.render({
      text: protectMath('正文 $\\mathcal{I}_{\\mathrm{cross}}$。'),
      engine: 'md'
    });
    const document = new JSDOM(html).window.document;
    const inline = document.querySelector('.math-inline');

    assert.ok(inline);
    assert.match(inline.textContent, /^\$[\s\S]+\$$/);
  } finally {
    await hexo.exit();
  }
});

test('full Hexo post pipeline retains inline MathJax delimiters', async () => {
  const databaseRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'opticalrec-hexo-'));
  const hexo = new Hexo(root, { silent: true, output: databaseRoot });
  await hexo.init();
  try {
    await hexo.load();
    const post = hexo.locals.get('posts').findOne({ slug: 'paper-2610.05432' });
    const document = new JSDOM(post.content).window.document;
    const inlines = [...document.querySelectorAll('.math-inline')];

    assert.equal(inlines.length, 30);
    for (const inline of inlines) {
      assert.match(inline.textContent, /^\$[\s\S]+\$$/);
    }
    assert.equal(document.querySelectorAll('em .math-inline, .math-inline em').length, 0);
  } finally {
    await hexo.exit();
    fs.rmSync(databaseRoot, { recursive: true, force: true });
  }
});

test('math protection identifies the target during Hexo before-post rendering', () => {
  const { isTargetPost } = require(path.join(root, 'scripts/opticalrec-math.js'));

  assert.equal(isTargetPost({ source: '_posts/paper-2610.05432.md' }), true);
  assert.equal(isTargetPost({ slug: 'paper-2610.05432' }), true);
  assert.equal(isTargetPost({ source: '_posts/paper-2608.17316.md' }), true);
  assert.equal(isTargetPost({ slug: 'paper-not-an-id' }), false);
});
