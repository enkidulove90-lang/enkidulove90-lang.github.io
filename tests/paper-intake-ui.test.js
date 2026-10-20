const assert = require('node:assert/strict');
const test = require('node:test');
const { JSDOM } = require('jsdom');

const {
  createPaperIntakeApi,
  mapJobGroup,
  mountPaperIntake
} = require('../source/js/paper-intake');
const { buildPublicConfig } = require('../scripts/paper_intake_config');

function createDom() {
  return new JSDOM(`<!doctype html><html><body>
    <nav id="menus"><div class="menus_items"></div></nav>
    <aside id="sidebar-menus"><div class="menus_items"></div></aside>
  </body></html>`, {
    url: 'https://enkidulove90-lang.github.io/'
  });
}

test('public config exposes only the gateway base URL', () => {
  const config = buildPublicConfig({
    PAPER_INTAKE_API_BASE: 'https://papers-api.example.workers.dev',
    NOTION_TOKEN: 'must-not-leak',
    WORKER_MACHINE_TOKEN: 'must-not-leak-either'
  });

  assert.deepEqual(config, {
    apiBase: 'https://papers-api.example.workers.dev',
    pdfUploadEnabled: false
  });
  assert.doesNotMatch(JSON.stringify(config), /token|secret|must-not-leak/i);
});

test('job grouping keeps failed work in completed and published work out of processing', () => {
  assert.equal(mapJobGroup({ status: 'processing' }), 'processing');
  assert.equal(mapJobGroup({ status: 'published' }), 'completed');
  assert.equal(mapJobGroup({ status: 'failed' }), 'completed');
  assert.equal(mapJobGroup({ status: 'cancelled' }), 'completed');
});

test('drawer starts closed, peeks on hover, locks on click and closes outside', async () => {
  const dom = createDom();
  const app = mountPaperIntake({
    window: dom.window,
    document: dom.window.document,
    api: { listJobs: async () => [] },
    hoverCloseDelay: 5
  });

  assert.equal(app.drawer.dataset.state, 'closed');
  app.tab.dispatchEvent(new dom.window.MouseEvent('mouseenter', { bubbles: true }));
  assert.equal(app.drawer.dataset.state, 'peek');
  app.tab.click();
  assert.equal(app.drawer.dataset.state, 'locked');
  dom.window.document.body.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  assert.equal(app.drawer.dataset.state, 'closed');

  app.destroy();
});

test('navigation entry opens one modal with URL and PDF submission modes', () => {
  const dom = createDom();
  const app = mountPaperIntake({
    window: dom.window,
    document: dom.window.document,
    api: { listJobs: async () => [] },
    pdfUploadEnabled: true
  });

  const entries = dom.window.document.querySelectorAll('.paper-intake-entry');
  assert.equal(entries.length, 2);
  entries[0].click();
  assert.equal(app.modal.getAttribute('aria-hidden'), 'false');
  assert.ok(app.modal.querySelector('input[name="paper_url"]'));
  assert.ok(app.modal.querySelector('input[name="paper_pdf"][type="file"]'));

  app.destroy();
});

test('URL-only deployment hides the unavailable PDF submission mode', () => {
  const dom = createDom();
  const app = mountPaperIntake({
    window: dom.window,
    document: dom.window.document,
    api: { listJobs: async () => [] },
    pdfUploadEnabled: false
  });

  assert.equal(app.modal.querySelector('[data-mode="pdf"]').hidden, true);
  assert.equal(app.modal.querySelector('[data-form="pdf"]').hidden, true);
  assert.match(app.modal.querySelector('.paper-intake-lead').textContent, /链接/);
  assert.doesNotMatch(app.modal.querySelector('.paper-intake-lead').textContent, /PDF/);

  app.destroy();
});

test('failed cards say unpublished and expose retry', async () => {
  const dom = createDom();
  let retried = '';
  const app = mountPaperIntake({
    window: dom.window,
    document: dom.window.document,
    api: {
      hasSession: () => true,
      listJobs: async () => [{ id: 'job-7', title: 'A failed paper', status: 'failed', retryable: true }],
      retry: async id => { retried = id; }
    }
  });

  await app.refreshJobs();
  assert.match(app.completed.textContent, /未发布/);
  const retry = app.completed.querySelector('[data-action="retry"]');
  assert.ok(retry);
  retry.click();
  await new Promise(resolve => dom.window.setTimeout(resolve, 0));
  assert.equal(retried, 'job-7');

  app.destroy();
});

test('published article links bypass the pre-build browser cache', () => {
  const dom = createDom();
  const app = mountPaperIntake({
    window: dom.window,
    document: dom.window.document,
    api: { hasSession: () => true, listJobs: async () => [] }
  });

  app.renderJobs([{
    id: 'job-published',
    status: 'published',
    siteUrl: 'https://enkidulove90-lang.github.io/article/paper-2509.06002/',
    updatedAt: '2026-10-20T08:56:00Z'
  }]);

  const link = app.completed.querySelector('a');
  assert.ok(link);
  assert.equal(link.href, 'https://enkidulove90-lang.github.io/article/paper-2509.06002/?build=2026-10-20T08%3A56%3A00Z');
  app.destroy();
});

test('API stores owner bearer only in sessionStorage', async () => {
  const dom = createDom();
  const calls = [];
  const fetch = async (url, options) => {
    calls.push({ url, options });
    return { ok: true, json: async () => ({ access_token: 'session-token' }) };
  };
  const api = createPaperIntakeApi({
    apiBase: 'https://papers-api.example.workers.dev',
    window: dom.window,
    fetch
  });

  await api.exchangeCode('one-time-code');
  assert.equal(dom.window.sessionStorage.getItem('paper-intake-session'), 'session-token');
  assert.equal(dom.window.localStorage.getItem('paper-intake-session'), null);
  await api.listJobs();
  assert.equal(calls[1].options.headers.get('Authorization'), 'Bearer session-token');
});

test('login message is accepted only from the configured gateway origin', async () => {
  const dom = createDom();
  const codes = [];
  const api = {
    apiBase: 'https://papers-api.example.workers.dev',
    hasSession: () => false,
    exchangeCode: async code => { codes.push(code); },
    listJobs: async () => []
  };
  const app = mountPaperIntake({ window: dom.window, document: dom.window.document, api });

  dom.window.dispatchEvent(new dom.window.MessageEvent('message', {
    origin: 'https://evil.example', data: { type: 'paper-intake-login', code: 'bad' }
  }));
  dom.window.dispatchEvent(new dom.window.MessageEvent('message', {
    origin: 'https://papers-api.example.workers.dev', data: { type: 'paper-intake-login', code: 'good' }
  }));
  await new Promise(resolve => dom.window.setTimeout(resolve, 0));
  assert.deepEqual(codes, ['good']);

  app.destroy();
});
