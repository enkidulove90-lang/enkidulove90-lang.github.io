'use strict';

function normalizeApiBase(value) {
  const fallback = 'http://127.0.0.1:8787';
  const candidate = String(value || fallback).trim().replace(/\/+$/, '');
  try {
    const parsed = new URL(candidate);
    if (!['http:', 'https:'].includes(parsed.protocol)) return fallback;
    return parsed.origin + parsed.pathname.replace(/\/+$/, '');
  } catch {
    return fallback;
  }
}

function buildPublicConfig(env = process.env) {
  return {
    apiBase: normalizeApiBase(env.PAPER_INTAKE_API_BASE),
    pdfUploadEnabled: String(env.PAPER_INTAKE_PDF_ENABLED || '').toLowerCase() === 'true'
  };
}

if (typeof hexo !== 'undefined') {
  hexo.extend.generator.register('paper_intake_config', () => ({
    path: 'paper-intake-config.json',
    data: JSON.stringify(buildPublicConfig()),
    layout: false
  }));
}

module.exports = { buildPublicConfig, normalizeApiBase };
