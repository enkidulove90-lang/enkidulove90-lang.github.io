/**
 * 生成 /filter-index.json —— 供侧栏「多维过滤器」组件做无刷新交叉筛选。
 *
 * 输出结构：
 *   { posts: [ { title, url, date, year, venue_type, venue_name, cats, tags,
 *                cover, excerpt } ] }
 *
 * 说明：本文件放在仓库根的 scripts/ 下，Hexo 启动时会自动作为插件加载
 *      （⚠️ 该目录只能放 .js，混入 .py 会导致 "Script load failed"）。
 */
hexo.extend.generator.register('filter_index', function (locals) {
  var coverConfig = (hexo.theme && hexo.theme.config && hexo.theme.config.cover) || {};
  var defaultCovers = Array.isArray(coverConfig.default_cover)
    ? coverConfig.default_cover.filter(Boolean)
    : (coverConfig.default_cover ? [coverConfig.default_cover] : []);

  function plainText(html) {
    return String(html || '')
      .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, ' ')
      .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
      .replace(/&nbsp;/gi, ' ')
      .replace(/&amp;/gi, '&')
      .replace(/&lt;/gi, '<')
      .replace(/&gt;/gi, '>')
      .replace(/&quot;/gi, '"')
      .replace(/&#39;|&apos;/gi, "'")
      .replace(/\s+/g, ' ')
      .trim();
  }

  function excerptFor(p) {
    var text = plainText(p.excerpt || p.content || '');
    return text.length > 180 ? text.slice(0, 177).trim() + '…' : text;
  }

  var posts = locals.posts.sort('-date').map(function (p, index) {
    var cats = [];
    var tags = [];
    try { cats = (p.categories && p.categories.toArray ? p.categories.toArray() : []).map(function (c) { return c.name; }); } catch (e) {}
    try { tags = (p.tags && p.tags.toArray ? p.tags.toArray() : []).map(function (t) { return t.name; }); } catch (e) {}
    return {
      title: p.title || '',
      url: '/' + String(p.path || '').replace(/^\//, ''),
      date: p.date ? p.date.format('YYYY-MM-DD') : '',
      year: p.year ? String(p.year) : (p.date ? p.date.format('YYYY') : ''),
      venue_type: p.venue_type || '',
      venue_name: p.venue_name || '',
      cats: cats,
      tags: tags,
      cover: p.cover || p.index_img || (defaultCovers.length ? defaultCovers[index % defaultCovers.length] : ''),
      excerpt: excerptFor(p)
    };
  });
  return {
    path: 'filter-index.json',
    data: JSON.stringify({ generated: new Date().toISOString(), count: posts.length, posts: posts })
  };
});
