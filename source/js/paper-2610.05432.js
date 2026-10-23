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
    return /^\/article\/paper-\d{4}\.\d{4,5}$/.test(normalizePath(value));
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

    if (normalizePath(root.location.pathname) === TARGET_PATH) {
      document.body.classList.add(BODY_CLASS);
      appendOnce(document, 'paper-2610-05432-css', 'link', {
        rel: 'stylesheet',
        href: '/css/paper-2610.05432.css'
      });
    }
    root.MathJax = root.MathJax || {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        macros: {
          bm: ['\\boldsymbol{#1}', 1]
        },
        processEscapes: true
      },
      options: {
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
      }
    };
    appendOnce(document, 'paper-2610-05432-mathjax', 'script', {
      async: true,
      src: '/js/vendor/mathjax/tex-svg.js',
      onload: function typesetOpticalRecAfterLoad() {
        if (root.MathJax && typeof root.MathJax.typesetPromise === 'function') {
          Promise.resolve(root.MathJax.typesetPromise([document.body])).catch(
            function markTypesetFailure() {
              document.body.classList.add('paper-math-typeset-failed');
            }
          );
        }
      },
      onerror: function markMathLoaderFailure() {
        document.body.classList.add('paper-math-load-failed');
      }
    });
    if (typeof root.MathJax.typesetPromise === 'function') {
      Promise.resolve(root.MathJax.typesetPromise([document.body])).catch(function ignoreTypesetFailure() {});
    }
    return true;
  }

  return { applyTargetEnhancements, isTargetUrl, normalizePath };
});
