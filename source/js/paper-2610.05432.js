(function bootstrapOpticalRec(root, factory) {
  const api = factory(root);
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (!root || !root.document) return;
  api.applyTargetEnhancements();
  root.document.addEventListener('pjax:complete', api.applyTargetEnhancements);
})(typeof window === 'undefined' ? null : window, function createOpticalRecEnhancer(root) {
  const TARGET_PATH = '/article/paper-2610.05432';
  const BODY_CLASS = 'paper-2610-05432';

  function normalizePath(value) {
    const withoutQuery = String(value || '').split(/[?#]/, 1)[0];
    const normalized = withoutQuery.replace(/\/+$/, '');
    return normalized || '/';
  }

  function isTargetUrl(value) {
    return normalizePath(value) === TARGET_PATH;
  }

  function appendOnce(document, id, tagName, attributes) {
    if (document.getElementById(id)) return;
    const node = document.createElement(tagName);
    node.id = id;
    Object.assign(node, attributes);
    document.head.appendChild(node);
  }

  function applyTargetEnhancements() {
    if (!root || !root.document || !root.document.body) return false;
    const { document } = root;
    document.body.classList.remove(BODY_CLASS);
    if (!isTargetUrl(root.location.pathname)) return false;

    document.body.classList.add(BODY_CLASS);
    appendOnce(document, 'paper-2610-05432-css', 'link', {
      rel: 'stylesheet',
      href: '/css/paper-2610.05432.css'
    });
    root.MathJax = root.MathJax || {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true
      },
      options: {
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
      }
    };
    appendOnce(document, 'paper-2610-05432-mathjax', 'script', {
      async: true,
      src: 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'
    });
    if (typeof root.MathJax.typesetPromise === 'function') {
      Promise.resolve(root.MathJax.typesetPromise([document.body])).catch(function ignoreTypesetFailure() {});
    }
    return true;
  }

  return { applyTargetEnhancements, isTargetUrl, normalizePath };
});
