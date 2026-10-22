const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const Hexo = require('hexo');

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
    createElement(tagName) { return { tagName, id: '', rel: '', href: '', src: '', async: false }; },
    getElementById(id) { return nodes.get(id) || null; },
    addEventListener(name, callback) { listeners[name] = callback; }
  };
  const window = { document, location: { pathname } };
  const context = { window, document, module: { exports: {} }, exports: {} };
  vm.runInNewContext(fs.readFileSync(scriptPath, 'utf8'), context, { filename: scriptPath });
  return { api: context.module.exports, appended, body, window, listeners };
}

test('route guard matches only the OpticalRec article after URL normalization', () => {
  const { api } = loadScript('/control/');
  assert.equal(api.isTargetUrl('/article/paper-2610.05432/'), true);
  assert.equal(api.isTargetUrl('/article/paper-2610.05432?view=1#method'), true);
  assert.equal(api.isTargetUrl('/article/paper-2610.05432///'), true);
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
  assert.deepEqual(
    JSON.parse(JSON.stringify(page.window.MathJax.tex.inlineMath)),
    [['$', '$']]
  );
  assert.deepEqual(
    JSON.parse(JSON.stringify(page.window.MathJax.tex.displayMath)),
    [['$$', '$$']]
  );
});

test('control route receives neither target class nor target-only assets', () => {
  const page = loadScript('/article/paper-2608.17316/');
  page.api.applyTargetEnhancements();

  assert.equal(page.body.classes.has('paper-2610-05432'), false);
  assert.equal(page.appended.length, 0);
  assert.equal(page.window.MathJax, undefined);
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

  assert.match(config, /<script defer src="\/js\/paper-2610\.05432\.js"><\/script>/);
  assert.match(script, /inlineMath:\s*\[\['\$', '\$'\]\]/);
  assert.match(script, /displayMath:\s*\[\['\$\$', '\$\$'\]\]/);
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
