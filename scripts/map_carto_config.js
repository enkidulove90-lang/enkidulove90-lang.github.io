const fs = require('node:fs');
const path = require('node:path');

function readLocalEnv(filePath) {
  if (!fs.existsSync(filePath)) return {};
  return fs.readFileSync(filePath, 'utf8').split(/\r?\n/).reduce((values, line) => {
    const match = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
    if (!match || match[1].startsWith('#')) return values;
    values[match[1]] = match[2].replace(/^(['"])(.*)\1$/, '$2');
    return values;
  }, {});
}

hexo.extend.generator.register('map-carto-config', function () {
  const localEnv = readLocalEnv(path.join(hexo.base_dir, '.env.local'));
  const cartoApiKey = process.env.CARTO_API_KEY || localEnv.CARTO_API_KEY || '';
  const config = JSON.stringify({ cartoApiKey }).replace(/</g, '\\u003c');

  return {
    path: 'js/map-carto-config.js',
    data: `window.__PAPER_MAP_CONFIG__ = Object.freeze(${config});\n`
  };
});
