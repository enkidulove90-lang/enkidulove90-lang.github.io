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
  assert.match(yaml, /TRACE_ID:\s*\$\{\{\s*github\.event\.client_payload\.trace_id\s*\}\}/);
  assert.match(yaml, /\/v1\/publications\/callback/);
  assert.match(yaml, /\\"ok\\":\$OK/);
  assert.match(yaml, /\\"trace_id\\":\\"\$TRACE_ID\\"/);
  assert.match(yaml, /\\"workflow_run_id\\":\\"\$GITHUB_RUN_ID\\"/);
  assert.match(yaml, /\\"run_url\\":\\"\$RUN_URL\\"/);
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
  assert.match(yaml, /force_orphan:\s*false/);
});

test('source mirror is committed only after the build has passed', () => {
  const yaml = fs.readFileSync(workflowPath, 'utf8');
  const build = yaml.indexOf('name: Build');
  const persist = yaml.indexOf('name: Persist incremental Notion mirror');

  assert.ok(build >= 0, 'Build step must exist');
  assert.ok(persist > build, 'Notion mirror must not be pushed before build validation');
});

test('deployment is gated by tests and followed by public smoke checks', () => {
  const yaml = fs.readFileSync(workflowPath, 'utf8');
  const gate = yaml.indexOf('name: Quality gate');
  const publish = yaml.indexOf('name: Publish to main');
  const smoke = yaml.indexOf('name: Post-deploy smoke test');
  assert.ok(gate >= 0 && gate < publish);
  assert.ok(smoke > publish);
  assert.match(yaml, /npm test/);
  assert.match(yaml, /post_deploy_smoke\.py/);
});
