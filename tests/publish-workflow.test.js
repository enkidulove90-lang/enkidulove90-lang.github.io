const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const workflowPath = path.resolve(__dirname, '../.github/workflows/publish.yml');

test('publish workflow reports repository-dispatch completion to the intake gateway', () => {
  const yaml = fs.readFileSync(workflowPath, 'utf8');

  assert.match(yaml, /PAPER_INTAKE_CALLBACK_URL/);
  assert.match(yaml, /PAPER_INTAKE_CALLBACK_TOKEN/);
  assert.match(yaml, /github\.event\.client_payload\.job_id/);
  assert.match(yaml, /\/v1\/publications\/callback/);
  assert.match(yaml, /\\"ok\\":\$OK/);
  assert.match(yaml, /PAPER_INTAKE_API_BASE:\s*\$\{\{\s*secrets\.PAPER_INTAKE_API_BASE\s*\}\}/);
});

test('publish callback runs even after a failed deployment and retries transient delivery errors', () => {
  const yaml = fs.readFileSync(workflowPath, 'utf8');

  assert.match(yaml, /if:\s*\$\{\{\s*always\(\)/);
  assert.match(yaml, /job\.status/);
  assert.match(yaml, /--retry\s+3/);
  assert.match(yaml, /Authorization:\s*Bearer\s+\$CALLBACK_TOKEN/);
});

test('repository dispatch syncs only its Notion page and persists the incremental mirror', () => {
  const yaml = fs.readFileSync(workflowPath, 'utf8');

  assert.match(yaml, /NOTION_PAGE_ID:\s*\$\{\{\s*github\.event\.client_payload\.notion_page_id\s*\}\}/);
  assert.match(yaml, /tools\/\.notion_state\.json/);
  assert.match(yaml, /git push origin HEAD:source/);
  assert.match(yaml, /rebuild_site\(\)/);
  assert.match(yaml, /public\/article\/\$TARGET_SLUG\/index\.html/);
});
