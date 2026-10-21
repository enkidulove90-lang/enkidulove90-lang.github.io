/**
 * 多维过滤器：领域 / 年份 / 出版类型 三个正交维度，前端无刷新交叉筛选。
 *
 * 数据源：/filter-index.json（由 scripts/filter_index.js 生成，含全站文章）
 * 交互  ：侧栏卡片 = Tabs（三个维度）+ 手风琴（一级 → 二级）
 *          点击条件 → 在正文列表位置自渲染结果（不依赖当前页是否列出全部文章）
 *
 * 为什么自渲染结果而不是隐藏原 DOM：过滤器要在**任何页面**都能用，而首页只列出
 * 分页的前若干篇、归档页是时间线布局、文章页没有列表——只有自渲染才能保证
 * 「点条件 → 看到命中的全部文章」这条路径在任何页面上都成立。
 */
(function () {
  'use strict';

  var state = { domain: '', year: '', month: '', venueType: '', venue: '', heading: '' };
  var INDEX = [];
  var MOUNTED = false;
  var ORIGINAL_TITLE = '';

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    fetch('/filter-index.json', { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (d) {
        INDEX = (d && d.posts) || [];
        if (!INDEX.length) return;
        buildCard();
        buildHomeToolbar();
        applyFromQuery();
      })
      .catch(function () { /* 索引不可用时静默降级，不影响站点其它功能 */ });
  });

  /* ------------------------------------------------------------------ 聚合 */

  function agg() {
    var domains = {}, years = {}, vtypes = {}, venues = {};
    INDEX.forEach(function (p) {
      var d1 = p.cats[0] || '未分类';
      var d2 = p.cats[1] || '';
      (domains[d1] = domains[d1] || { n: 0, subs: {} });
      domains[d1].n++;
      if (d2) domains[d1].subs[d2] = (domains[d1].subs[d2] || 0) + 1;

      var y = p.year || String(p.date).slice(0, 4);
      var m = p.month || String(p.date).slice(5, 7);
      (years[y] = years[y] || { n: 0, months: {} });
      years[y].n++;
      years[y].months[m] = (years[y].months[m] || 0) + 1;

      var vt = p.venue_type || '未标注';
      (vtypes[vt] = vtypes[vt] || { n: 0, subs: {} });
      vtypes[vt].n++;
      var vn = p.venue_name || vt;
      vtypes[vt].subs[vn] = (vtypes[vt].subs[vn] || 0) + 1;

      if (p.venue_name) venues[p.venue_name] = (venues[p.venue_name] || 0) + 1;
    });
    return { domains: domains, years: years, vtypes: vtypes };
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function sortedEntries(obj, byKey) {
    var arr = Object.keys(obj).map(function (k) { return [k, obj[k]]; });
    arr.sort(byKey === 'name'
      ? function (a, b) { return String(a[0]).localeCompare(String(b[0]), 'zh'); }
      : function (a, b) { return (b[1].n || b[1]) - (a[1].n || a[1]) || String(a[0]).localeCompare(String(b[0])); });
    return arr;
  }

  function monthLabel(m) {
    var n = parseInt(m, 10);
    return isNaN(n) ? m : (n + ' 月');
  }

  /* ------------------------------------------------------------- 渲染卡片 */

  function groupHtml(name, count, subs, dim) {
    var subHtml = subs.map(function (kv) {
      var value = kv.length > 2 ? kv[2] : kv[0];
      var month = kv.length > 3 ? ' data-month="' + esc(kv[3]) + '"' : '';
      return '<div class="md-sub" data-dim="' + dim + '" data-val="' + esc(value) +
        '" data-parent="' + esc(name) + '"' + month + '><span class="md-sub-name">' +
        esc(kv[0]) + '</span><span class="md-count">' + kv[1] + '</span></div>';
    }).join('');
    var leaf = !subHtml;
    return '<div class="md-group' + (leaf ? ' is-leaf' : '') + '" data-group="' + esc(name) + '"' +
      (leaf ? ' data-leaf-dim="' + esc(dim) + '" data-leaf-val="' + esc(name) + '"' : '') + '>' +
      '<div class="md-group-head"><span class="md-caret">' + (leaf ? '•' : '▶') + '</span>' +
      '<span class="md-group-name">' + esc(name) + '</span>' +
      '<span class="md-count">' + count + '</span></div>' +
      (subHtml ? '<div class="md-sub-wrap">' + subHtml + '</div>' : '') +
      '</div>';
  }

  function buildCard() {
    var aside = document.getElementById('aside-content');
    if (!aside) return;
    var a = agg();

    var domainHtml = sortedEntries(a.domains).map(function (kv) {
      var subs = sortedEntries(kv[1].subs, 'count').map(function (s) { return [s[0], s[1]]; });
      return groupHtml(kv[0], kv[1].n, subs, 'domain');
    }).join('');

    var yearHtml = sortedEntries(a.years, 'name').reverse().map(function (kv) {
      var months = sortedEntries(kv[1].months, 'name').reverse().map(function (s) {
        return [monthLabel(s[0]), s[1], kv[0], s[0]];
      });
      return groupHtml(kv[0], kv[1].n, months, 'year');
    }).join('');

    var venueHtml = sortedEntries(a.vtypes).map(function (kv) {
      var subs = sortedEntries(kv[1].subs, 'count').map(function (s) { return [s[0], s[1]]; });
      return groupHtml(kv[0], kv[1].n, subs, 'venueType');
    }).join('');

    var card = document.createElement('div');
    card.className = 'card-widget md-filter';
    card.id = 'md-filter';
    card.innerHTML =
      '<div class="md-tabs">' +
      '<div class="md-tab is-active" data-tab="domain">按领域</div>' +
      '<div class="md-tab" data-tab="year">按年份</div>' +
      '<div class="md-tab" data-tab="venueType">按出版类型</div>' +
      '</div>' +
      '<div class="md-panel is-active" data-panel="domain">' + domainHtml + '</div>' +
      '<div class="md-panel" data-panel="year">' + yearHtml + '</div>' +
      '<div class="md-panel" data-panel="venueType">' + venueHtml + '</div>';

    var old = aside.querySelector('.card-categories');
    if (old) old.parentNode.replaceChild(card, old);
    else aside.insertBefore(card, aside.firstChild);

    card.addEventListener('click', onClick);
    MOUNTED = true;
  }

  function optionHtml(value, label) {
    return '<option value="' + esc(value) + '">' + esc(label || value) + '</option>';
  }

  function uniqueValues(getter) {
    var values = {};
    INDEX.forEach(function (post) {
      var value = getter(post);
      if (value) values[value] = true;
    });
    return Object.keys(values).sort(function (a, b) { return String(a).localeCompare(String(b), 'zh'); });
  }

  function buildHomeToolbar() {
    if (!location.pathname || location.pathname !== '/') return;
    var originalList = document.getElementById('recent-posts');
    if (!originalList || !originalList.parentNode || document.getElementById('md-home-filter')) return;
    var domains = uniqueValues(function (post) { return post.cats[0] || '未分类'; });
    var years = uniqueValues(function (post) { return String(post.year || String(post.date).slice(0, 4)); }).reverse();
    var venues = uniqueValues(function (post) { return post.venue_name || ''; });
    var toolbar = document.createElement('section');
    toolbar.id = 'md-home-filter';
    toolbar.className = 'md-home-filter card-widget';
    toolbar.setAttribute('aria-label', '文章筛选');
    toolbar.innerHTML =
      '<div class="md-home-filter__intro"><strong>筛选文章</strong><span>从领域、年份与刊物快速找到论文</span></div>' +
      '<label><span>领域</span><select data-home-dim="domain"><option value="">全部领域</option>' + domains.map(function (v) { return optionHtml(v); }).join('') + '</select></label>' +
      '<label><span>年份</span><select data-home-dim="year"><option value="">全部年份</option>' + years.map(function (v) { return optionHtml(v); }).join('') + '</select></label>' +
      '<label><span>刊物</span><select data-home-dim="venue"><option value="">全部刊物</option>' + venues.map(function (v) { return optionHtml(v); }).join('') + '</select></label>' +
      '<button type="button" data-home-clear="1">重置</button>';
    // #content-inner 是 Butterfly 的横向 Flex 容器。筛选栏必须留在文章列中，
    // 否则会成为与 #recent-posts、侧栏并列的第三列并挤压论文卡片。
    originalList.insertBefore(toolbar, originalList.firstChild);
    toolbar.addEventListener('change', function (event) {
      var dim = event.target.getAttribute && event.target.getAttribute('data-home-dim');
      if (!dim) return;
      state[dim] = event.target.value || '';
      if (dim === 'venue') {
        var sample = INDEX.find(function (post) { return post.venue_name === state.venue; });
        state.venueType = sample ? (sample.venue_type || '未标注') : '';
      }
      state.month = '';
      state.heading = state[dim];
      syncCard();
      render();
    });
    toolbar.addEventListener('click', function (event) {
      if (!(event.target.getAttribute && event.target.getAttribute('data-home-clear'))) return;
      state = { domain: '', year: '', month: '', venueType: '', venue: '', heading: '' };
      syncCard();
      syncHomeToolbar();
      render();
    });
  }

  function syncHomeToolbar() {
    var toolbar = document.getElementById('md-home-filter');
    if (!toolbar || !toolbar.querySelectorAll) return;
    toolbar.querySelectorAll('[data-home-dim]').forEach(function (select) {
      select.value = state[select.getAttribute('data-home-dim')] || '';
    });
  }

  function onClick(e) {
    var tab = e.target.closest ? e.target.closest('.md-tab') : null;
    if (tab) { switchTab(tab); return; }

    var head = e.target.closest ? e.target.closest('.md-group-head') : null;
    if (head) {
      var group = head.parentNode;
      var leafDim = group.getAttribute('data-leaf-dim');
      if (leafDim) {
        var leafValue = group.getAttribute('data-leaf-val') || group.getAttribute('data-group') || '';
        var leafActive = group.classList.contains('is-active');
        group.classList[leafActive ? 'remove' : 'add']('is-active');
        state[leafDim] = leafActive ? '' : leafValue;
        state.heading = leafActive ? '' : leafValue;
        render();
      } else {
        group.classList.toggle('is-open');
      }
      return;
    }

    var sub = e.target.closest ? e.target.closest('.md-sub') : null;
    if (sub) {
      var dim = sub.getAttribute('data-dim');
      var val = sub.getAttribute('data-val');
      var parent = sub.getAttribute('data-parent') || '';
      var month = sub.getAttribute('data-month') || '';
      var wasActive = sub.classList.contains('is-active');
      sub.parentNode.parentNode.querySelectorAll('.md-sub.is-active').forEach(function (n) { n.classList.remove('is-active'); });
      if (wasActive) {
        if (dim === 'venueType') { state.venueType = ''; state.venue = ''; }
        else if (dim === 'year') { state.year = ''; state.month = ''; }
        else state[dim] = '';
        state.heading = '';
      } else {
        sub.classList.add('is-active');
        if (dim === 'venueType') { state.venueType = parent || val; state.venue = val; state.heading = val; }
        else if (dim === 'year') {
          state.year = val;
          state.month = month;
          state.heading = val + (month ? ' 年 ' + monthLabel(month) : ' 年');
        } else { state[dim] = val; state.heading = val; }
      }
      render();
    }
  }

  function switchTab(tab) {
    var key = tab.getAttribute('data-tab');
    var card = tab.closest('.md-filter');
    card.querySelectorAll('.md-tab').forEach(function (t) { t.classList.toggle('is-active', t === tab); });
    card.querySelectorAll('.md-panel').forEach(function (p) {
      p.classList.toggle('is-active', p.getAttribute('data-panel') === key);
    });
  }

  /* -------------------------------------------------------------- 筛选逻辑 */

  function match(p) {
    if (state.domain && p.cats.indexOf(state.domain) < 0) return false;
    if (state.year && String(p.year || String(p.date).slice(0, 4)) !== state.year) return false;
    if (state.month && String(p.month || String(p.date).slice(5, 7)) !== state.month) return false;
    if (state.venueType && (p.venue_type || '未标注') !== state.venueType) return false;
    if (state.venue && p.venue_name !== state.venue) return false;
    return true;
  }

  function activeCount() {
    return (state.domain ? 1 : 0) + (state.year ? 1 : 0) + (state.venueType ? 1 : 0) + (state.venue ? 1 : 0);
  }

  function barHtml(n) {
    var chips = '';
    if (state.domain) chips += chip('领域', state.domain, 'domain');
    if (state.year) chips += chip('年份', state.year + (state.month ? '-' + state.month : ''), 'year');
    if (state.venueType) chips += chip('类型', state.venueType, 'venueType');
    if (state.venue) chips += chip('出处', state.venue, 'venue');
    return '<span>筛选结果 <b class="md-hint">' + n + ' 篇</b></span>' + chips +
      '<span class="md-clear" data-clear="1">清除筛选</span>';
  }

  function chip(label, val, dim) {
    return '<span class="md-chip">' + esc(label) + '：<b>' + esc(val) + '</b>' +
      '<i data-remove="' + dim + '">✕</i></span>';
  }

  function itemHtml(p) {
    var cats = p.cats.slice(0, 2).map(function (c, index) {
      var path = p.cats.slice(0, index + 1).map(encodeURIComponent).join('/');
      return '<a href="/categories/' + path + '/" class="post-meta-categories">' + esc(c) + '</a>';
    }).join(', ');
    var meta = [p.year, p.venue_name,
      '<span class="post-meta-date-created">' + esc(p.date) + '</span>'].filter(Boolean).join(' · ');
    var cover = p.cover
      ? '<div class="post_cover left"><a href="' + esc(p.url) + '" title="' + esc(p.title) + '">' +
        '<img class="post-bg" src="' + esc(p.cover) + '" alt="' + esc(p.title) + '" loading="lazy"></a></div>'
      : '';
    var infoClass = cover ? 'recent-post-info' : 'recent-post-info no-cover';
    var excerpt = p.excerpt ? '<div class="content">' + esc(p.excerpt) + '</div>' : '';
    return '<div class="recent-post-item">' + cover +
      '<div class="' + infoClass + '">' +
      '<a class="article-title" href="' + esc(p.url) + '" title="' + esc(p.title) + '">' + esc(p.title) + '</a>' +
      '<div class="article-meta-wrap">' + cats + ' · ' + meta + '</div>' +
      excerpt +
      '</div></div>';
  }

  function fallbackHeading() {
    if (state.venue) return state.venue;
    if (state.year) return state.year + (state.month ? ' 年 ' + monthLabel(state.month) : ' 年');
    if (state.domain) return state.domain;
    if (state.venueType) return state.venueType;
    return '';
  }

  function updateHeading() {
    var title = document.getElementById('site-title');
    if (!title) return;
    if (!ORIGINAL_TITLE) ORIGINAL_TITLE = title.textContent || '';
    title.textContent = activeCount() ? (state.heading || fallbackHeading()) : ORIGINAL_TITLE;
  }

  function mount(main, bar, list, anchor) {
    if (!bar.isConnected) main.insertBefore(bar, anchor ? anchor.nextSibling : main.firstChild);
    if (!list.isConnected) main.insertBefore(list, bar.nextSibling);
  }

  function host() {
    // 把筛选结果放到当前正文组件的同级位置，避免插入 #content-inner 后破坏主题布局。
    var original = document.getElementById('recent-posts') ||
      document.getElementById('archive') ||
      document.getElementById('category') ||
      document.getElementById('tag') ||
      document.getElementById('post') ||
      document.getElementById('page');
    var homeToolbar = document.getElementById('md-home-filter');
    if (original && original.id === 'recent-posts' && homeToolbar && homeToolbar.parentNode === original) {
      return { main: original, list: original, anchor: homeToolbar, embedded: true };
    }
    if (original && original.parentNode) return { main: original.parentNode, list: original, embedded: false };
    return null;
  }

  function render() {
    if (!INDEX.length) return;
    var h = host();
    if (!h) return;

    var bar = document.getElementById('md-active-bar');
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'md-active-bar';
      bar.className = 'md-active-bar';
    }
    var list = document.getElementById('md-results');
    if (!list) {
      list = document.createElement('div');
      list.id = 'md-results';
      list.className = 'recent-posts md-results';
    }

    updateHeading();
    if (activeCount() === 0) {
      // 恢复原状
      if (bar.isConnected) bar.remove();
      if (list.isConnected) list.remove();
      if (h.list) {
        h.list.style.display = '';
        if (h.list.classList) h.list.classList.remove('md-filtering');
      }
      return;
    }

    var hits = INDEX.filter(match);
    bar.className = 'md-active-bar is-on';
    bar.innerHTML = barHtml(hits.length);
    list.innerHTML = hits.length
      ? hits.map(itemHtml).join('')
      : '<div class="md-empty">没有符合当前条件的文章，试试放宽条件。</div>';

    mount(h.main, bar, list, h.anchor);
    if (h.list) {
      if (h.embedded && h.list.classList) h.list.classList.add('md-filtering');
      else h.list.style.display = 'none';
    }

    bar.onclick = function (e) {
      var rm = e.target.getAttribute && e.target.getAttribute('data-remove');
      if (rm) {
        if (rm === 'venueType') { state.venueType = ''; state.venue = ''; } else state[rm] = '';
        if (rm === 'year') state.month = '';
        state.heading = '';
        syncCard(); render();
        return;
      }
      if (e.target.getAttribute && e.target.getAttribute('data-clear')) {
        state = { domain: '', year: '', month: '', venueType: '', venue: '', heading: '' };
        syncCard(); render();
      }
    };
  }

  function syncCard() {
    var card = document.getElementById('md-filter');
    if (!card) return;
    card.querySelectorAll('.md-sub').forEach(function (n) {
      var dim = n.getAttribute('data-dim'), val = n.getAttribute('data-val');
      var parent = n.getAttribute('data-parent') || '';
      var month = n.getAttribute('data-month') || '';
      var on = (dim === 'domain' && state.domain === val) ||
               (dim === 'year' && state.year === val && state.month === month) ||
               (dim === 'venueType' && state.venueType === parent && state.venue === val);
      n.classList.toggle('is-active', !!on);
    });
    card.querySelectorAll('.md-group[data-leaf-dim]').forEach(function (n) {
      var dim = n.getAttribute('data-leaf-dim');
      n.classList.toggle('is-active', state[dim] === n.getAttribute('data-leaf-val'));
    });
    syncHomeToolbar();
  }

  /** 支持从 URL 带入条件：/archives/?f_domain=推荐系统&f_year=2026 */
  function applyFromQuery() {
    var q = new URLSearchParams(location.search);
    var any = false;
    ['domain', 'year', 'month', 'venueType', 'venue'].forEach(function (k) {
      var v = q.get('f_' + k);
      if (v) { state[k] = v; state.heading = v; any = true; }
    });
    if (!any) return;
    syncCard();
    render();
  }
})();
