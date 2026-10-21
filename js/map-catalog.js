(function () {
  'use strict';

  var root = document.querySelector('[data-map-catalog]');
  if (!root) return;
  var type = root.getAttribute('data-map-catalog');
  var groupsRoot = root.querySelector('.map-catalog__groups');
  var countRoot = root.querySelector('[data-map-catalog-count]');
  var refreshSeed = Date.now() + Math.floor(Math.random() * 1000000);
  var usedImages = new Set();

  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function groupKey(value) {
    return String(value || '未命名位置').trim();
  }

  function collectGroups(payload) {
    var groups = new Map();
    payload.places.filter(function (place) {
      return place.location_type === type;
    }).forEach(function (place) {
      (place.papers || []).forEach(function (paper) {
        var name = groupKey(paper.location_label || place.name);
        var institution = (place.institutions || []).find(function (item) {
          return groupKey(item.name) === name;
        });
        if (!groups.has(name)) {
          groups.set(name, {
            name: name,
            city: place.city === 'Virtual' ? '坐标待补充' : (place.city || place.name),
            description: (institution && institution.description) || place.description || '',
            images: Array.from(new Set([].concat(place.city_images || [], place.image || []).filter(Boolean))),
            papers: []
          });
        }
        groups.get(name).papers.push(paper);
      });
    });
    return Array.from(groups.values()).sort(function (a, b) {
      return b.papers.length - a.papers.length || a.name.localeCompare(b.name);
    });
  }

  function stringHash(value) {
    return String(value).split('').reduce(function (hash, character) {
      return ((hash << 5) - hash + character.charCodeAt(0)) | 0;
    }, refreshSeed);
  }

  function chooseUniqueImage(images, paper) {
    if (!images.length) return '';
    var storageKey = 'map-catalog-image:' + (paper.id || paper.url || paper.title);
    var previous = sessionStorage.getItem(storageKey);
    var start = Math.abs(stringHash(paper.id || paper.url || paper.title)) % images.length;
    for (var index = 0; index < images.length; index += 1) {
      var candidate = images[(start + index) % images.length];
      if (candidate !== previous && !usedImages.has(candidate)) {
        usedImages.add(candidate);
        sessionStorage.setItem(storageKey, candidate);
        return candidate;
      }
    }
    for (var fallbackIndex = 0; fallbackIndex < images.length; fallbackIndex += 1) {
      var fallback = images[(start + fallbackIndex) % images.length];
      if (fallback !== previous) {
        sessionStorage.setItem(storageKey, fallback);
        return fallback;
      }
    }
    sessionStorage.setItem(storageKey, images[start]);
    return images[start];
  }

  function paperCard(paper, group) {
    var article = element('article', 'map-catalog__paper-card');
    var link = element('a', 'map-catalog__paper-cover');
    var image = element('img');
    var body = element('div', 'map-catalog__paper-body');
    var title = element('a', 'map-catalog__paper-title', paper.title);
    var meta = element('p', 'map-catalog__paper-meta',
      [paper.date, paper.venue_name, group.city].filter(Boolean).join(' · '));
    var description = element('p', 'map-catalog__paper-description',
      paper.description || '这篇文章从问题背景、方法设计与实验结果三个层面整理这项工作。');
    link.href = paper.url;
    link.setAttribute('aria-label', paper.title);
    image.src = chooseUniqueImage(group.images, paper);
    image.alt = group.city + '城市图景';
    image.loading = 'lazy';
    image.decoding = 'async';
    title.href = paper.url;
    link.appendChild(image);
    body.append(title, meta, description);
    article.append(link, body);
    return article;
  }

  function institutionSection(group) {
    var section = element('section', 'map-catalog__institution');
    var header = element('header', 'map-catalog__institution-head');
    var identity = element('div');
    var title = element('h2', null, group.name);
    var meta = element('p', null, group.city + ' · ' + group.papers.length + ' 篇');
    var papers = element('div', 'map-catalog__papers');
    identity.append(title, meta);
    header.appendChild(identity);
    section.id = 'institution-' + group.name.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fff]+/g, '-');
    group.papers.sort(function (a, b) { return b.date.localeCompare(a.date); })
      .forEach(function (paper) { papers.appendChild(paperCard(paper, group)); });
    section.append(header, papers);
    return section;
  }

  function companySection(group, index) {
    var section = element('section', 'map-catalog__institution map-catalog__company');
    var card = element('button', 'map-catalog__company-card');
    var cover = element('span', 'map-catalog__company-cover');
    var image = element('img');
    var body = element('span', 'map-catalog__company-body');
    var eyebrow = element('span', 'map-catalog__company-meta', group.city + ' · ' + group.papers.length + ' 篇论文');
    var title = element('strong', 'map-catalog__company-title', group.name);
    var description = element('span', 'map-catalog__company-description',
      group.description || '该企业研究团队持续参与推荐系统、机器学习与智能信息服务研究。');
    var lead = group.papers[0];
    var leadSummary = lead && lead.description
      ? lead.description.slice(0, 120) + (lead.description.length > 120 ? '…' : '')
      : '';
    var featured = element('span', 'map-catalog__company-featured',
      lead ? '代表论文：' + lead.title + (leadSummary ? ' — ' + leadSummary : '') : '查看企业论文');
    var action = element('span', 'map-catalog__company-action', '展开论文列表 ↓');
    var papers = element('div', 'map-catalog__company-papers map-catalog__papers');
    var panelId = 'company-papers-' + index;

    image.src = group.images[0] || '';
    image.alt = group.name + '相关城市与机构图景';
    image.loading = 'lazy';
    image.decoding = 'async';
    cover.appendChild(image);
    body.append(eyebrow, title, description, featured, action);
    card.type = 'button';
    card.setAttribute('aria-expanded', 'false');
    card.setAttribute('aria-controls', panelId);
    card.append(cover, body);
    papers.id = panelId;
    papers.hidden = true;
    group.papers.sort(function (a, b) { return b.date.localeCompare(a.date); })
      .forEach(function (paper) { papers.appendChild(paperCard(paper, group)); });
    card.addEventListener('click', function () {
      var willOpen = card.getAttribute('aria-expanded') !== 'true';
      groupsRoot.querySelectorAll('.map-catalog__company-card[aria-expanded="true"]').forEach(function (openCard) {
        openCard.setAttribute('aria-expanded', 'false');
        openCard.closest('.map-catalog__company').classList.remove('is-open');
        var openPanel = document.getElementById(openCard.getAttribute('aria-controls'));
        if (openPanel) openPanel.hidden = true;
      });
      card.setAttribute('aria-expanded', String(willOpen));
      section.classList.toggle('is-open', willOpen);
      papers.hidden = !willOpen;
      action.textContent = willOpen ? '收起论文列表 ↑' : '展开论文列表 ↓';
    });
    section.append(card, papers);
    return section;
  }

  fetch('/map_data.json', { cache: 'default' })
    .then(function (response) {
      if (!response.ok) throw new Error('map catalog request failed');
      return response.json();
    })
    .then(function (payload) {
      var groups = collectGroups(payload);
      var paperCount = groups.reduce(function (sum, group) { return sum + group.papers.length; }, 0);
      countRoot.textContent = groups.length + ' 个分组 · ' + paperCount + ' 篇论文';
      groupsRoot.replaceChildren();
      if (!groups.length) {
        groupsRoot.appendChild(element('p', 'map-catalog__empty', '这一类暂时还没有可展示的论文。'));
        return;
      }
      groupsRoot.classList.toggle('map-catalog__company-grid', type === 'company');
      groups.forEach(function (group, index) {
        groupsRoot.appendChild(type === 'company' ? companySection(group, index) : institutionSection(group));
      });
    })
    .catch(function () {
      groupsRoot.replaceChildren(element('p', 'map-catalog__empty', '列表数据暂时没有加载成功，请刷新后重试。'));
    });
})();
