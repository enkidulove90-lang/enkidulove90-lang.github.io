'use strict';

const TARGET_SLUG = 'paper-2610.05432';
const TARGET_SOURCE = '_posts/paper-2610.05432.md';

function isTargetPost(data) {
  if (!data) return false;
  if (data.slug === TARGET_SLUG || data.source === TARGET_SOURCE) return true;
  const slug = String(data.slug || '').trim();
  const source = String(data.source || '').replace(/\\/g, '/');
  return /^paper-\d{4}\.\d{4,5}$/.test(slug)
    || /(?:^|\/)paper-\d{4}\.\d{4,5}\.md$/.test(source);
}

function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function escapeInlineMath(value) {
  return escapeHtml(value)
    .replace(/_/g, '&#95;')
    .replace(/\*/g, '&#42;');
}

function protectMath(markdown) {
  const displays = [];
  const inlines = [];
  const protectDisplay = (_match, formula) => {
    const token = `@@OPTICALREC_DISPLAY_${displays.length}@@`;
    displays.push(`<div class="math-display">\\[${escapeHtml(formula.trim())}\\]</div>`);
    return token;
  };
  const protectInline = (_match, prefix, formula) => {
    const token = `@@OPTICALREC_INLINE_${inlines.length}@@`;
    inlines.push(
      `${prefix}<span class="math-inline">$${escapeInlineMath(formula)}$</span>`
    );
    return token;
  };

  let protectedMarkdown = String(markdown)
    .replace(/\$\$([\s\S]*?)\$\$/g, protectDisplay)
    .replace(/\\\[([\s\S]*?)\\\]/g, protectDisplay);

  protectedMarkdown = protectedMarkdown.replace(
    /(^|[^$])\$(?!\$)([^\n$]+?)\$(?!\$)/g,
    protectInline
  ).replace(/(^|[^\\])\\\(([\s\S]*?)\\\)/g, protectInline);

  const withDisplays = displays.reduce(
    (content, display, index) => content.replace(`@@OPTICALREC_DISPLAY_${index}@@`, display),
    protectedMarkdown
  );
  return inlines.reduce(
    (content, inline, index) => content.replace(`@@OPTICALREC_INLINE_${index}@@`, inline),
    withDisplays
  );
}

if (typeof hexo !== 'undefined') {
  hexo.extend.filter.register('before_post_render', data => {
    if (isTargetPost(data)) data.content = protectMath(data.content);
    return data;
  });
}

module.exports = { isTargetPost, protectMath };
