'use strict';

const TARGET_SLUG = 'paper-2610.05432';
const TARGET_SOURCE = '_posts/paper-2610.05432.md';

function isTargetPost(data) {
  return Boolean(data && (data.slug === TARGET_SLUG || data.source === TARGET_SOURCE));
}

function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function protectMath(markdown) {
  const displays = [];
  let protectedMarkdown = String(markdown).replace(/\$\$([\s\S]*?)\$\$/g, (_match, formula) => {
    const token = `@@OPTICALREC_DISPLAY_${displays.length}@@`;
    displays.push(`<div class="math-display">\\[${escapeHtml(formula.trim())}\\]</div>`);
    return token;
  });

  protectedMarkdown = protectedMarkdown.replace(
    /(^|[^$])\$(?!\$)([^\n$]+?)\$(?!\$)/g,
    (_match, prefix, formula) => (
      `${prefix}<span class="math-inline">\\(${escapeHtml(formula)}\\)</span>`
    )
  );

  return displays.reduce(
    (content, display, index) => content.replace(`@@OPTICALREC_DISPLAY_${index}@@`, display),
    protectedMarkdown
  );
}

if (typeof hexo !== 'undefined') {
  hexo.extend.filter.register('before_post_render', data => {
    if (isTargetPost(data)) data.content = protectMath(data.content);
    return data;
  });
}

module.exports = { isTargetPost, protectMath };
