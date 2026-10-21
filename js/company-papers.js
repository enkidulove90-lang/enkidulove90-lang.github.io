(function (root, factory) {
  'use strict';
  // /map_data.json is shared through the one-hour MapDataCache.
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && root.document) api.boot(root.document, root);
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  function companySlug(value) {
    return String(value || 'company')
      .trim()
      .toLowerCase()
      .normalize('NFKD')
      .replace(/[^a-z0-9\u4e00-\u9fff]+/g, '-')
      .replace(/^-+|-+$/g, '') || 'company';
  }

  function computeVirtualRange(options) {
    var rowHeight = Math.max(1, Number(options.rowHeight) || 1);
    var itemCount = Math.max(0, Number(options.itemCount) || 0);
    var overscan = Math.max(0, Number(options.overscan) || 0);
    var scrollTop = Math.max(0, Number(options.scrollTop) || 0);
    var viewportHeight = Math.max(0, Number(options.viewportHeight) || 0);
    var start = Math.max(0, Math.floor(scrollTop / rowHeight) - overscan);
    var end = Math.min(itemCount, Math.ceil((scrollTop + viewportHeight) / rowHeight) + overscan);
    return { start: start, end: end };
  }

  function element(document, tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function groupKey(value) {
    return String(value || '未命名企业').trim();
  }

  function collectCompanies(payload) {
    var companies = new Map();
    (payload.places || []).filter(function (place) {
      return place.location_type === 'company';
    }).forEach(function (place) {
      (place.papers || []).forEach(function (paper) {
        var name = groupKey(paper.location_label || (place.institution && place.institution.name) || place.name);
        var institution = (place.institutions || []).find(function (item) {
          return groupKey(item.name) === name;
        });
        if (!companies.has(name)) {
          companies.set(name, {
            name: name,
            city: place.city === 'Virtual' ? '坐标待补充' : (place.city || place.name),
            description: (institution && institution.description) || place.description || '',
            images: Array.from(new Set([].concat(place.city_images || [], place.image || []).filter(Boolean))),
            papers: []
          });
        }
        companies.get(name).papers.push(paper);
      });
    });
    return Array.from(companies.values()).map(function (company) {
      company.papers.sort(function (a, b) { return String(b.date).localeCompare(String(a.date)); });
      return company;
    });
  }

  function paperMatches(paper, query) {
    if (!query) return true;
    return [paper.title, paper.description, paper.venue_name, paper.date]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .indexOf(query.toLowerCase()) !== -1;
  }

  function createPaperCard(document, paper, company, index) {
    var article = element(document, 'article', 'map-catalog__paper-card');
    var cover = element(document, 'a', 'map-catalog__paper-cover');
    var image = element(document, 'img');
    var body = element(document, 'div', 'map-catalog__paper-body');
    var title = element(document, 'a', 'map-catalog__paper-title', paper.title);
    var meta = element(document, 'p', 'map-catalog__paper-meta',
      [paper.date, paper.venue_name, company.city].filter(Boolean).join(' · '));
    var description = element(document, 'p', 'map-catalog__paper-description',
      paper.description || '这篇文章从问题背景、方法设计与实验结果三个层面整理这项工作。');
    var images = company.images || [];

    cover.href = paper.url;
    cover.setAttribute('aria-label', paper.title);
    image.dataset.src = images.length ? images[index % images.length] : '';
    image.alt = company.city + '城市图景';
    image.loading = 'lazy';
    image.decoding = 'async';
    title.href = paper.url;
    cover.appendChild(image);
    body.append(title, meta, description);
    article.append(cover, body);
    return article;
  }

  function boot(document, window) {
    var root = document.querySelector('[data-company-papers]');
    if (!root) return;

    var params = new URLSearchParams(window.location.search);
    var requestedCompany = params.get('company') || '';
    var titleRoot = root.querySelector('[data-company-paper-title]');
    var summaryRoot = root.querySelector('[data-company-paper-summary]');
    var searchRoot = root.querySelector('[data-company-paper-search]');
    var viewport = root.querySelector('[data-company-paper-viewport]');
    var spacer = root.querySelector('[data-company-paper-spacer]');
    var itemsRoot = root.querySelector('[data-company-paper-items]');
    var emptyRoot = root.querySelector('[data-company-paper-empty]');
    var overscan = 3;
    var allPapers = [];
    var filteredPapers = [];
    var company = null;
    var scheduled = false;

    function rowHeight() {
      return window.matchMedia && window.matchMedia('(max-width: 520px)').matches ? 180 : 226;
    }

    function renderVirtualRows() {
      scheduled = false;
      var height = rowHeight();
      var range = computeVirtualRange({
        scrollTop: viewport.scrollTop,
        viewportHeight: viewport.clientHeight,
        rowHeight: height,
        itemCount: filteredPapers.length,
        overscan: overscan
      });
      var fragment = document.createDocumentFragment();
      spacer.style.height = (filteredPapers.length * height) + 'px';
      itemsRoot.replaceChildren();
      for (var index = range.start; index < range.end; index += 1) {
        var row = element(document, 'div', 'company-paper-virtual__row');
        row.setAttribute('role', 'listitem');
        row.style.height = height + 'px';
        row.style.transform = 'translateY(' + (index * height) + 'px)';
        row.appendChild(createPaperCard(document, filteredPapers[index], company, index));
        fragment.appendChild(row);
      }
      itemsRoot.appendChild(fragment);
      window.MapDataCache.observeImages(itemsRoot);
      emptyRoot.hidden = filteredPapers.length !== 0;
      viewport.hidden = filteredPapers.length === 0;
    }

    function scheduleRender() {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(renderVirtualRows);
    }

    function applySearch() {
      var query = searchRoot.value.trim();
      filteredPapers = allPapers.filter(function (paper) { return paperMatches(paper, query); });
      viewport.scrollTop = 0;
      summaryRoot.textContent = company.name + ' · ' + filteredPapers.length + ' 篇论文' +
        (company.description ? ' · ' + company.description : '');
      scheduleRender();
    }

    viewport.addEventListener('scroll', scheduleRender, { passive: true });
    searchRoot.addEventListener('input', applySearch);
    window.addEventListener('resize', scheduleRender, { passive: true });

    window.MapDataCache.load()
      .then(function (payload) {
        company = collectCompanies(payload).find(function (candidate) {
          return companySlug(candidate.name) === requestedCompany;
        });
        if (!company) {
          titleRoot.textContent = '没有找到该企业';
          summaryRoot.textContent = '请返回企业目录重新选择。';
          searchRoot.disabled = true;
          viewport.hidden = true;
          emptyRoot.hidden = false;
          return;
        }
        titleRoot.textContent = company.name + ' 的论文';
        allPapers = company.papers;
        filteredPapers = allPapers.slice();
        summaryRoot.textContent = company.city + ' · ' + allPapers.length + ' 篇论文' +
          (company.description ? ' · ' + company.description : '');
        renderVirtualRows();
      })
      .catch(function () {
        titleRoot.textContent = '企业论文暂时无法读取';
        summaryRoot.textContent = '数据请求失败，请稍后刷新重试。';
        viewport.hidden = true;
        emptyRoot.hidden = false;
      });
  }

  return {
    companySlug: companySlug,
    computeVirtualRange: computeVirtualRange,
    boot: boot
  };
});
