(function paperIntakeModule(factory) {
  const exported = factory();
  if (typeof module === 'object' && module.exports) module.exports = exported;
  if (typeof window !== 'undefined') {
    window.PaperIntake = exported;
    const start = () => exported.bootPaperIntake(window).catch(error => {
      console.warn('[paper-intake] unable to start', error);
    });
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
    else start();
  }
})(function createPaperIntakeModule() {
  'use strict';

  const SESSION_KEY = 'paper-intake-session';
  const TERMINAL = new Set(['published', 'failed', 'cancelled']);
  const STATUS_LABELS = {
    queued: '等待处理',
    processing: '处理中',
    publishing: '正在发布',
    published: '处理完成',
    failed: '未发布',
    cancelled: '已关闭'
  };
  const STAGES = [
    ['received', '等待领取'],
    ['validate_input', '校验论文'],
    ['resolve_metadata', '读取元数据'],
    ['download_pdf', '下载 PDF'],
    ['mineru_parse', '解析论文'],
    ['deepseek_generate', '生成文章'],
    ['classify', '自动分类'],
    ['quality_check', '质量校验'],
    ['write_notion_published', '写入 Notion'],
    ['publishing', '发布网站'],
    ['published', '发布完成']
  ];
  const STAGE_LABELS = Object.fromEntries(STAGES);

  function mapJobGroup(job) {
    return TERMINAL.has(String(job && job.status || '').toLowerCase()) ? 'completed' : 'processing';
  }

  function normalizeJob(raw) {
    return {
      id: String(raw.id || raw.job_id || ''),
      paperId: String(raw.paperId || raw.paper_id || ''),
      title: String(raw.title || '').trim(),
      status: String(raw.status || 'queued').toLowerCase(),
      stage: String(raw.stage || ''),
      retryable: Boolean(raw.retryable),
      attempt: Number(raw.attempt || 0),
      errorCode: String(raw.errorCode || raw.error_code || ''),
      errorMessage: String(raw.errorMessage || raw.error_message || ''),
      createdAt: String(raw.createdAt || raw.created_at || ''),
      updatedAt: String(raw.updatedAt || raw.updated_at || ''),
      siteUrl: String(raw.siteUrl || raw.site_url || '')
    };
  }

  function createPaperIntakeApi(options) {
    const apiBase = String(options.apiBase || '').replace(/\/+$/, '');
    const win = options.window;
    const fetchImpl = options.fetch || win.fetch.bind(win);

    function token() {
      return win.localStorage.getItem(SESSION_KEY)
        || win.sessionStorage.getItem(SESSION_KEY)
        || '';
    }

    function clearToken() {
      win.localStorage.removeItem(SESSION_KEY);
      win.sessionStorage.removeItem(SESSION_KEY);
    }

    function expiresSoon(value) {
      try {
        const payload = value.split('.')[0].replace(/-/g, '+').replace(/_/g, '/');
        const claims = JSON.parse(win.atob(payload));
        return Number(claims.exp || 0) * 1000 - Date.now() <= 5 * 60 * 1000;
      } catch { return false; }
    }

    async function refreshSessionIfNeeded() {
      const current = token();
      if (!current || !expiresSoon(current)) return;
      const response = await fetchImpl(`${apiBase}/v1/session/refresh`, {
        method: 'POST', headers: { Authorization: `Bearer ${current}` }
      });
      let payload = {};
      try { payload = await response.json(); } catch { /* handled below */ }
      if (!response.ok || !payload.token) {
        if (response.status === 401) clearToken();
        throw Object.assign(new Error(payload.message || '授权续期失败，请重新登录。'), payload);
      }
      win.localStorage.setItem(SESSION_KEY, payload.token);
    }

    async function request(path, init = {}, authenticated = true) {
      if (authenticated && path !== '/v1/session/refresh') await refreshSessionIfNeeded();
      const headers = new win.Headers(init.headers || {});
      if (authenticated) {
        const current = token();
        if (!current) throw Object.assign(new Error('请先使用 GitHub 登录。'), { code: 'authentication_required' });
        headers.set('Authorization', `Bearer ${current}`);
      }
      const response = await fetchImpl(`${apiBase}${path}`, { ...init, headers });
      let payload = {};
      try { payload = await response.json(); } catch { /* non-JSON gateway response */ }
      if (!response.ok) {
        if (response.status === 401) {
          clearToken();
          win.dispatchEvent(new win.CustomEvent('paper-intake:unauthorized'));
        }
        throw Object.assign(new Error(payload.message || `请求失败（${response.status}）`), payload);
      }
      return payload;
    }

    return {
      apiBase,
      hasSession: () => Boolean(token()),
      clearSession: clearToken,
      refreshSessionIfNeeded,
      loginUrl: returnOrigin => `${apiBase}/v1/session/start?return_origin=${encodeURIComponent(returnOrigin)}`,
      async exchangeCode(code) {
        const payload = await request('/v1/session/exchange', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ code })
        }, false);
        const sessionToken = payload.token || payload.access_token;
        if (!sessionToken) throw new Error('登录成功，但服务端没有返回会话凭据。');
        win.localStorage.setItem(SESSION_KEY, sessionToken);
        win.sessionStorage.removeItem(SESSION_KEY);
        return payload;
      },
      async submitUrl(url) {
        return request('/v1/intake/url', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ url })
        });
      },
      async submitPdf(file) {
        return request('/v1/intake/pdf', {
          method: 'POST',
          headers: { 'content-type': 'application/pdf' },
          body: file
        });
      },
      async listJobs() {
        const payload = await request('/v1/jobs');
        return Array.isArray(payload.jobs) ? payload.jobs.map(normalizeJob) : [];
      },
      jobLog: id => request(`/v1/jobs/${encodeURIComponent(id)}/log`),
      retry: id => request(`/v1/jobs/${encodeURIComponent(id)}/retry`, { method: 'POST' })
    };
  }

  function element(doc, tag, className, text) {
    const node = doc.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function freshPublicationUrl(siteUrl, updatedAt, baseUrl) {
    try {
      const target = new URL(siteUrl, baseUrl);
      target.searchParams.set('build', updatedAt || String(Date.now()));
      return target.href;
    } catch {
      return siteUrl;
    }
  }

  function icon(doc, className) {
    const node = element(doc, 'i', className);
    node.setAttribute('aria-hidden', 'true');
    return node;
  }

  function appendNavigationEntries(doc, openModal) {
    const containers = doc.querySelectorAll('#menus .menus_items, #sidebar-menus .menus_items');
    const entries = [];
    containers.forEach(container => {
      if (container.querySelector('.paper-intake-entry')) return;
      const link = element(doc, 'a', 'site-page paper-intake-entry');
      link.href = '#paper-intake';
      link.setAttribute('role', 'button');
      link.append(icon(doc, 'fas fa-file-arrow-up fa-fw'));
      link.append(doc.createTextNode(' 收录论文'));
      link.addEventListener('click', event => {
        event.preventDefault();
        openModal();
      });
      container.append(link);
      entries.push(link);
    });
    return entries;
  }

  function buildModal(doc, pdfUploadEnabled) {
    const overlay = element(doc, 'div', 'paper-intake-modal');
    overlay.id = 'paper-intake-modal';
    overlay.setAttribute('aria-hidden', 'true');
    overlay.innerHTML = `
      <section class="paper-intake-dialog" role="dialog" aria-modal="true" aria-labelledby="paper-intake-title">
        <button class="paper-intake-close" type="button" data-action="close-modal" aria-label="关闭">×</button>
        <p class="paper-intake-kicker">论文收录</p>
        <h2 id="paper-intake-title">收录一篇论文</h2>
        <p class="paper-intake-lead">提交链接或 PDF。系统会自动解析、撰写、分类并发布到本站。</p>
        <div class="paper-intake-auth">
          <span class="paper-intake-auth-dot" aria-hidden="true"></span>
          <span data-auth-label>尚未登录</span>
          <button type="button" class="paper-intake-text-button" data-action="login">GitHub 登录</button>
        </div>
        <div class="paper-intake-tabs" role="tablist" aria-label="提交方式">
          <button type="button" role="tab" aria-selected="true" data-mode="url">论文链接</button>
          <button type="button" role="tab" aria-selected="false" data-mode="pdf">PDF 文件</button>
        </div>
        <form class="paper-intake-form" data-form="url">
          <label for="paper-intake-url">公开论文链接</label>
          <div class="paper-intake-field-row">
            <input id="paper-intake-url" name="paper_url" type="url" required placeholder="https://arxiv.org/abs/…">
            <button type="submit" class="paper-intake-primary">开始收录</button>
          </div>
          <p class="paper-intake-hint">支持 arXiv、DOI 与公开 HTTPS 论文页；重复论文不会再次入库。</p>
        </form>
        <form class="paper-intake-form" data-form="pdf" hidden>
          <label class="paper-intake-drop" for="paper-intake-pdf">
            <input id="paper-intake-pdf" name="paper_pdf" type="file" accept="application/pdf,.pdf" required>
            <span class="paper-intake-drop-mark">PDF</span>
            <strong>选择本地论文</strong>
            <small>单个文件不超过 50 MB</small>
          </label>
          <button type="submit" class="paper-intake-primary">上传并开始收录</button>
        </form>
        <p class="paper-intake-notice" data-notice role="status" aria-live="polite"></p>
      </section>`;
    doc.body.append(overlay);
    if (!pdfUploadEnabled) {
      overlay.querySelector('.paper-intake-lead').textContent = '提交公开论文链接。系统会自动解析、撰写、分类并发布到本站。';
      overlay.querySelector('[data-mode="pdf"]').hidden = true;
      overlay.querySelector('[data-form="pdf"]').hidden = true;
    }
    return overlay;
  }

  function buildDrawer(doc) {
    const shell = element(doc, 'aside', 'paper-task-drawer');
    shell.id = 'paper-task-drawer';
    shell.dataset.state = 'closed';
    shell.setAttribute('aria-label', '论文处理任务');
    shell.innerHTML = `
      <button class="paper-task-tab" type="button" aria-expanded="false" aria-controls="paper-task-panel">
        <span class="paper-task-tab-icon">↟</span><span>任务</span><b data-task-count>0</b>
      </button>
      <div class="paper-task-panel" id="paper-task-panel">
        <header class="paper-task-header">
          <div><p>收录进度</p><h2>论文处理任务</h2></div>
          <button type="button" data-action="close-drawer" aria-label="收起任务抽屉">×</button>
        </header>
        <div class="paper-task-login" data-task-login>
          <p>仅站点所有者可查看任务。</p>
          <button type="button" data-action="login">使用 GitHub 登录</button>
        </div>
        <div class="paper-task-groups" data-task-groups hidden>
          <section><h3><span>处理中</span><b data-processing-count>0</b></h3><div data-processing></div></section>
          <section><h3><span>处理完成</span><b data-completed-count>0</b></h3><div data-completed></div></section>
        </div>
      </div>`;
    doc.body.append(shell);
    return shell;
  }

  function mountPaperIntake(options) {
    const win = options.window;
    const doc = options.document;
    const api = options.api;
    const hoverCloseDelay = Number(options.hoverCloseDelay == null ? 320 : options.hoverCloseDelay);
    const downloadText = options.downloadText || ((name, text) => {
      const blob = new win.Blob([text], { type: 'application/json;charset=utf-8' });
      const url = win.URL.createObjectURL(blob);
      const link = doc.createElement('a');
      link.href = url;
      link.download = name;
      link.click();
      win.URL.revokeObjectURL(url);
    });
    const modal = buildModal(doc, options.pdfUploadEnabled === true);
    const drawer = buildDrawer(doc);
    const tab = drawer.querySelector('.paper-task-tab');
    const panel = drawer.querySelector('.paper-task-panel');
    const processing = drawer.querySelector('[data-processing]');
    const completed = drawer.querySelector('[data-completed]');
    const notice = modal.querySelector('[data-notice]');
    let closeTimer = null;
    let pollTimer = null;
    let destroyed = false;
    const unauthorizedHandler = () => {
      syncAuth();
      const toast = element(doc, 'div', 'paper-intake-toast is-error', '授权已过期，请重新点击 GitHub 登录');
      toast.setAttribute('role', 'alert');
      doc.body.appendChild(toast);
      win.setTimeout(() => toast.remove(), 5000);
    };
    win.addEventListener('paper-intake:unauthorized', unauthorizedHandler);

    function setDrawerState(state) {
      drawer.dataset.state = state;
      tab.setAttribute('aria-expanded', state === 'closed' ? 'false' : 'true');
    }

    function cancelClose() {
      if (closeTimer != null) win.clearTimeout(closeTimer);
      closeTimer = null;
    }

    function scheduleClose() {
      cancelClose();
      if (drawer.dataset.state === 'locked') return;
      closeTimer = win.setTimeout(() => setDrawerState('closed'), hoverCloseDelay);
    }

    function openModal() {
      modal.setAttribute('aria-hidden', 'false');
      syncAuth();
      win.setTimeout(() => modal.querySelector('input:not([hidden])')?.focus(), 0);
    }

    function closeModal() {
      modal.setAttribute('aria-hidden', 'true');
      notice.textContent = '';
    }

    function syncAuth() {
      const loggedIn = Boolean(api.hasSession && api.hasSession());
      modal.querySelector('[data-auth-label]').textContent = loggedIn ? 'GitHub 身份已验证' : '尚未登录';
      modal.querySelector('.paper-intake-auth').classList.toggle('is-authenticated', loggedIn);
      drawer.querySelector('[data-task-login]').hidden = loggedIn;
      drawer.querySelector('[data-task-groups]').hidden = !loggedIn;
    }

    function login() {
      if (!api.loginUrl) return;
      win.open(api.loginUrl(win.location.origin), 'paper-intake-login', 'popup,width=560,height=720');
    }

    function jobCard(job) {
      const card = element(doc, 'article', `paper-task-card is-${job.status}`);
      const top = element(doc, 'div', 'paper-task-card-top');
      const heading = element(doc, 'h4', '', job.title || `论文 ${job.paperId.slice(0, 8) || job.id.slice(0, 8)}`);
      const menuWrap = element(doc, 'div', 'paper-task-menu');
      const menuButton = element(doc, 'button', 'paper-task-menu-button', '•••');
      menuButton.type = 'button';
      menuButton.dataset.action = 'task-menu';
      menuButton.setAttribute('aria-label', '任务操作');
      menuButton.setAttribute('aria-expanded', 'false');
      const menu = element(doc, 'div', 'paper-task-menu-popover');
      menu.hidden = true;
      const exportButton = element(doc, 'button', '', '导出日志');
      exportButton.type = 'button';
      exportButton.dataset.action = 'export-log';
      menuButton.addEventListener('click', event => {
        event.stopPropagation();
        menu.hidden = !menu.hidden;
        menuButton.setAttribute('aria-expanded', String(!menu.hidden));
      });
      exportButton.addEventListener('click', async event => {
        event.stopPropagation();
        exportButton.disabled = true;
        try {
          const payload = api.jobLog ? await api.jobLog(job.id) : { job, events: [] };
          downloadText(`paper-task-${job.id}.json`, JSON.stringify(payload, null, 2));
          menu.hidden = true;
          menuButton.setAttribute('aria-expanded', 'false');
        } catch (error) {
          exportButton.textContent = error.message || '导出失败';
        } finally { exportButton.disabled = false; }
      });
      menu.append(exportButton);
      menuWrap.append(menuButton, menu);
      top.append(heading, menuWrap);
      const meta = element(doc, 'p', 'paper-task-card-meta');
      const status = element(doc, 'span', 'paper-task-status', STATUS_LABELS[job.status] || job.status);
      meta.append(status);
      if (job.updatedAt) {
        const time = element(doc, 'time', '', new Date(job.updatedAt).toLocaleString('zh-CN', { hour12: false }));
        time.dateTime = job.updatedAt;
        meta.append(time);
      }
      card.append(top, meta);
      const stageIndex = Math.max(0, STAGES.findIndex(([name]) => name === job.stage));
      const stageLabel = STAGE_LABELS[job.stage] || (job.status === 'queued' ? '等待领取' : '处理中');
      const terminalProgress = job.status === 'published' ? 100 : null;
      const progressValue = terminalProgress == null
        ? Math.max(4, Math.round((stageIndex / (STAGES.length - 1)) * 100))
        : terminalProgress;
      const progress = element(doc, 'div', 'paper-task-progress');
      const progressLabel = element(doc, 'div', 'paper-task-progress-label');
      progressLabel.append(element(doc, 'span', '', stageLabel), element(doc, 'b', '', `${progressValue}%`));
      const track = element(doc, 'div', 'paper-task-progress-track');
      track.setAttribute('role', 'progressbar');
      track.setAttribute('aria-label', stageLabel);
      track.setAttribute('aria-valuemin', '0');
      track.setAttribute('aria-valuemax', '100');
      track.setAttribute('aria-valuenow', String(progressValue));
      const fill = element(doc, 'span', 'paper-task-progress-fill');
      fill.style.width = `${progressValue}%`;
      track.append(fill);
      progress.append(progressLabel, track);
      card.append(progress);
      if (job.errorMessage) card.append(element(doc, 'p', 'paper-task-error', job.errorMessage));
      const actions = element(doc, 'div', 'paper-task-actions');
      if (job.siteUrl && job.status === 'published') {
        const link = element(doc, 'a', '', '阅读文章');
        link.href = freshPublicationUrl(job.siteUrl, job.updatedAt, win.location.href);
        actions.append(link);
      }
      if (job.status === 'failed' && job.retryable) {
        const retry = element(doc, 'button', '', '重新处理');
        retry.type = 'button';
        retry.dataset.action = 'retry';
        retry.addEventListener('click', async () => {
          retry.disabled = true;
          try { await api.retry(job.id); await refreshJobs(); }
          catch (error) { retry.disabled = false; retry.textContent = error.message || '重试失败'; }
        });
        actions.append(retry);
      }
      if (actions.childNodes.length) card.append(actions);
      return card;
    }

    function renderJobs(rawJobs) {
      const jobs = rawJobs.map(normalizeJob);
      const active = jobs.filter(job => mapJobGroup(job) === 'processing');
      const done = jobs.filter(job => mapJobGroup(job) === 'completed');
      processing.replaceChildren(...active.map(jobCard));
      completed.replaceChildren(...done.map(jobCard));
      if (!active.length) processing.append(element(doc, 'p', 'paper-task-empty', '当前没有正在处理的任务。'));
      if (!done.length) completed.append(element(doc, 'p', 'paper-task-empty', '完成记录会保留在这里。'));
      drawer.querySelector('[data-processing-count]').textContent = String(active.length);
      drawer.querySelector('[data-completed-count]').textContent = String(done.length);
      drawer.querySelector('[data-task-count]').textContent = String(active.length);
      drawer.classList.toggle('has-active-jobs', active.length > 0);
      if (pollTimer != null) win.clearTimeout(pollTimer);
      if (active.length && !destroyed) pollTimer = win.setTimeout(refreshJobs, 10000);
      return jobs;
    }

    async function refreshJobs() {
      syncAuth();
      if (!api.hasSession || !api.hasSession()) return [];
      try { return renderJobs(await api.listJobs()); }
      catch (error) {
        if (error.code === 'authentication_required' || error.code === 'invalid_session') syncAuth();
        return [];
      }
    }

    const navigationEntries = appendNavigationEntries(doc, openModal);
    tab.addEventListener('mouseenter', () => {
      cancelClose();
      if (drawer.dataset.state === 'closed') setDrawerState('peek');
    });
    drawer.addEventListener('mouseenter', cancelClose);
    drawer.addEventListener('mouseleave', scheduleClose);
    tab.addEventListener('click', event => {
      event.stopPropagation();
      setDrawerState(drawer.dataset.state === 'locked' ? 'closed' : 'locked');
      if (drawer.dataset.state === 'locked') refreshJobs();
    });
    panel.addEventListener('click', event => event.stopPropagation());
    doc.addEventListener('click', () => setDrawerState('closed'));
    drawer.querySelector('[data-action="close-drawer"]').addEventListener('click', () => setDrawerState('closed'));
    drawer.querySelectorAll('[data-action="login"]').forEach(button => button.addEventListener('click', login));
    modal.querySelector('[data-action="login"]').addEventListener('click', login);
    modal.querySelector('[data-action="close-modal"]').addEventListener('click', closeModal);
    modal.addEventListener('click', event => { if (event.target === modal) closeModal(); });
    modal.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => {
      const mode = button.dataset.mode;
      modal.querySelectorAll('[data-mode]').forEach(item => item.setAttribute('aria-selected', String(item === button)));
      modal.querySelectorAll('[data-form]').forEach(form => { form.hidden = form.dataset.form !== mode; });
      notice.textContent = '';
    }));

    modal.querySelector('[data-form="url"]').addEventListener('submit', async event => {
      event.preventDefault();
      if (!api.hasSession || !api.hasSession()) { login(); return; }
      const submit = event.currentTarget.querySelector('[type="submit"]');
      submit.disabled = true;
      notice.textContent = '正在提交论文链接…';
      try {
        const input = event.currentTarget.elements.paper_url;
        const result = await api.submitUrl(input.value);
        closeModal();
        setDrawerState('locked');
        await refreshJobs();
      } catch (error) { notice.textContent = error.message || '提交失败，请稍后重试。'; }
      finally { submit.disabled = false; }
    });

    modal.querySelector('[data-form="pdf"]').addEventListener('submit', async event => {
      event.preventDefault();
      if (!api.hasSession || !api.hasSession()) { login(); return; }
      const file = event.currentTarget.elements.paper_pdf.files[0];
      if (!file) return;
      const submit = event.currentTarget.querySelector('[type="submit"]');
      submit.disabled = true;
      notice.textContent = '正在上传 PDF…';
      try {
        const result = await api.submitPdf(file);
        closeModal();
        setDrawerState('locked');
        await refreshJobs();
      } catch (error) { notice.textContent = error.message || '上传失败，请稍后重试。'; }
      finally { submit.disabled = false; }
    });

    const messageHandler = async event => {
      let expectedOrigin;
      try { expectedOrigin = new URL(api.apiBase).origin; } catch { return; }
      if (event.origin !== expectedOrigin) return;
      if (!event.data || event.data.type !== 'paper-intake-login' || typeof event.data.code !== 'string') return;
      try {
        await api.exchangeCode(event.data.code);
        syncAuth();
        notice.textContent = 'GitHub 身份验证成功。';
        await refreshJobs();
      } catch (error) { notice.textContent = error.message || '登录失败。'; }
    };
    win.addEventListener('message', messageHandler);
    syncAuth();
    refreshJobs();

    return {
      modal, drawer, tab, processing, completed, navigationEntries,
      openModal, closeModal, renderJobs, refreshJobs,
      destroy() {
        destroyed = true;
        cancelClose();
        if (pollTimer != null) win.clearTimeout(pollTimer);
        win.removeEventListener('message', messageHandler);
        win.removeEventListener('paper-intake:unauthorized', unauthorizedHandler);
        navigationEntries.forEach(node => node.remove());
        modal.remove();
        drawer.remove();
      }
    };
  }

  async function bootPaperIntake(win) {
    if (win.document.getElementById('paper-intake-modal')) return null;
    const response = await win.fetch('/paper-intake-config.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('论文收录配置加载失败。');
    const config = await response.json();
    const api = createPaperIntakeApi({ apiBase: config.apiBase, window: win });
    return mountPaperIntake({
      window: win,
      document: win.document,
      api,
      pdfUploadEnabled: config.pdfUploadEnabled === true
    });
  }

  return {
    SESSION_KEY,
    bootPaperIntake,
    createPaperIntakeApi,
    freshPublicationUrl,
    mapJobGroup,
    mountPaperIntake,
    normalizeJob
  };
});
