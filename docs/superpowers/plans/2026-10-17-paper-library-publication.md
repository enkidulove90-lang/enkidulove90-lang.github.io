# Paper Library Publication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an audited, idempotent pipeline that converts the 49 unpublished PDFs into evidence-backed Notion articles and stable Hexo pages with high-resolution figures and conditionally attached source PDFs.

**Architecture:** A manifest builder inventories PDFs, summaries, MinerU assets and existing posts by arXiv ID, then a quality gate assigns each paper to ready, summarize, parse, quarantine, or published. Separate article, Notion, and sync adapters keep content generation testable without network credentials; external writes occur only after a dry run and a one-paper canary.

**Tech Stack:** Python 3.12, `requests`, PyMuPDF, Pillow, MinerU CLI, Notion REST API `2026-03-11`, Hexo/Node.js tests.

**Spec:** `docs/superpowers/specs/2026-10-17-paper-library-publication.md`

## Global Constraints

- Treat arXiv ID as the unique idempotency key across PDF, parsed assets, summaries, Notion pages and Hexo posts.
- Never re-import the deleted mismatch IDs `2504.00678` or `2505.00556`.
- Publish only claims, figures and numeric results traceable to the source PDF, MinerU Markdown, metadata API or official repository.
- Use `status=Invisible` until every article passes the quality gate; only then promote to `Published`.
- Do not commit, push, merge or trigger GitHub Pages without explicit user approval.
- Do not expose Notion tokens in logs, manifests, generated Markdown or test fixtures.

## Review Focus

- A summary whose arXiv ID exists but title differs from the parsed paper must be routed to summary regeneration, not treated as ready.
- A paper with no ablation, benchmark or official GitHub repository must state that absence without inventing content or links.
- MinerU image hashes, captions and PDF page crops must resolve to the same Figure/Table number before publication.
- Retry after an interrupted Notion upload must update/reuse the same arXiv page and must not duplicate file blocks; existing articles without a source-file reference must not gain one.
- PDFs larger than 20 MiB must use multipart upload while smaller files use single-part upload.

---

### Task 1: Audited publication manifest

**Files:**
- Create: `tools/paper_inventory.py`
- Create: `tools/paper_exclusions.json`
- Create: `tests/test_paper_inventory.py`
- Generate: `tools/paper_publication_manifest.json`

**Interfaces:**
- Consumes: `build_manifest(papers_dir: Path, summaries_dir: Path, parsed_dir: Path, posts_dir: Path, exclusions_path: Path) -> list[PaperRecord]`
- Produces: `PaperRecord` with `arxiv_id`, paths, title fingerprints, `on_site`, `quality_state`, and reasons.

- [ ] **Step 1: Write failing inventory tests** for complete 74-PDF coverage, 49 unpublished IDs, duplicate rejection, deleted-ID exclusion, title mismatch regeneration, and stable JSON ordering.
- [ ] **Step 2: Run `python -m unittest tests.test_paper_inventory -v`** and verify the new tests fail because the module is absent.
- [ ] **Step 3: Implement the manifest builder and CLI** with states `published`, `ready`, `needs_summary`, and `needs_parse`; seed the two removed IDs in `paper_exclusions.json` so they cannot be reintroduced accidentally.
- [ ] **Step 4: Generate the manifest and rerun the test**; expect 74 total, 25 published, 20 reliable-summary candidates, 22 parsed papers needing a reliable summary, and 7 without parsed Markdown.
- [ ] **Step 5: Commit** `feat: add audited paper publication manifest`.

### Task 2: MinerU and figure asset adapter

**Files:**
- Create: `tools/mineru_adapter.py`
- Modify: `tools/paper_digest.py`
- Modify: `tools/crop_pdf_layout.py`
- Create: `tests/test_mineru_adapter.py`

**Interfaces:**
- Consumes: `prepare_assets(record: PaperRecord, output_root: Path, run_mineru: bool) -> ParsedPaper`
- Produces: `ParsedPaper` with normalized Markdown, ordered sections, figure-caption-page mappings, image dimensions and provenance.

- [ ] **Step 1: Write failing tests** for existing MinerU discovery, missing-command reporting, caption matching, vector crop fallback, HD threshold, and the 7-paper parse queue.
- [ ] **Step 2: Run `python -m unittest tests.test_mineru_adapter -v`** and verify failure before implementation.
- [ ] **Step 3: Implement discovery and normalization** without invoking MinerU unless `--run-mineru` is supplied; preserve source paths and hashes.
- [ ] **Step 4: Add figure validation and crop fallback** using PDF page number, caption number and minimum `1280px` width or `720px` height.
- [ ] **Step 5: Run the tests and a no-network dry run**; expect 21 missing-summary papers to reuse existing Markdown and exactly 7 papers to request MinerU.
- [ ] **Step 6: Commit** `feat: normalize MinerU paper assets`.

### Task 3: Evidence-backed article builder and quality gate

**Files:**
- Create: `tools/paper_article.py`
- Modify: `tools/paper_article_template.md`
- Create: `tests/test_paper_article.py`

**Interfaces:**
- Consumes: `build_article(record: PaperRecord, parsed: ParsedPaper, summary_path: Path | None) -> ArticleDraft`
- Produces: `ArticleDraft` containing front matter, required sections, local images/PDF links, citations, source spans and `validation_errors`.

- [ ] **Step 1: Write failing tests** for every required section, explicit “论文未报告”, figure explanations, numeric-source tracing, leak-word rejection, official-link format and incomplete-draft blocking.
- [ ] **Step 2: Run `python -m unittest tests.test_paper_article -v`** and verify failure.
- [ ] **Step 3: Implement the deterministic section extractor and renderer**; it may compress source text but must not invent unsupported claims.
- [ ] **Step 4: Implement `validate_article(draft: ArticleDraft) -> list[str]`** and copy only validated images/PDFs into `source/images/papers/<arxiv-id>/` and `source/papers/`.
- [ ] **Step 5: Build the PRISM fixture and one unpublished-paper fixture**; require zero validation errors and exact source-link rendering.
- [ ] **Step 6: Commit** `feat: build validated paper articles`.

### Task 4: Idempotent Notion publisher with file uploads

**Files:**
- Create: `tools/notion_publish.py`
- Create: `tests/test_notion_publish.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `publish_article(client: NotionClient, draft: ArticleDraft, database_id: str, publish: bool) -> PublishResult`
- Produces: one Notion page per arXiv ID, ordered article blocks, uploaded image/PDF blocks, and a dry-run report.

- [ ] **Step 1: Write mocked failing tests** for create, update, retry, no-token dry-run, block chunking, conditional source-PDF attachment, no backfill for existing articles, single-part PDF, multipart PDF and `Invisible`→`Published` promotion.
- [ ] **Step 2: Run `python -m unittest tests.test_notion_publish -v`** and verify failure.
- [ ] **Step 3: Implement the Notion client** against API version `2026-03-11`, querying by arXiv ID and never logging authorization headers.
- [ ] **Step 4: Implement image/PDF upload** only when a new article draft explicitly carries a source PDF, with single-part at `<=20 MiB`, multipart above `20 MiB`, and upload-state reuse after retry; never backfill existing articles lacking a file reference.
- [ ] **Step 5: Document required database property and connection changes** while retaining compatibility with existing fields.
- [ ] **Step 6: Run all mocked tests and a credential-free dry run**; expect zero external requests in dry-run mode.
- [ ] **Step 7: Commit** `feat: publish paper drafts to Notion`.

### Task 5: Notion-to-Hexo compatibility and orchestration

**Files:**
- Create: `tools/publish_paper_library.py`
- Modify: `tools/notion_sync.py`
- Modify: `.github/workflows/publish.yml`
- Create: `tests/test_paper_pipeline.py`

**Interfaces:**
- Consumes: manifest plus `--batch`, `--ids`, `--run-mineru`, `--write-notion`, and `--promote` CLI flags.
- Produces: resumable batch reports and Hexo Markdown whose image/PDF links remain stable after Notion sync.

- [ ] **Step 1: Write failing end-to-end fixture tests** for dry-run ordering, canary selection, resume state, Notion file blocks, stable local asset names and two consecutive identical runs.
- [ ] **Step 2: Run `python -m unittest tests.test_paper_pipeline -v`** and verify failure.
- [ ] **Step 3: Implement the orchestrator** with default dry-run and explicit external-write flags; refuse promotion when validation errors exist.
- [ ] **Step 4: Extend `notion_sync.py`** to preserve file/PDF blocks, alt text and arXiv ID without breaking existing pages.
- [ ] **Step 5: Add a manual workflow input** for audited publication batches; keep scheduled runs read-only from Notion to Hexo.
- [ ] **Step 6: Run Python tests, `npm test`, and `npm run build`**; expect all tests and Hexo generation to pass.
- [ ] **Step 7: Commit** `feat: orchestrate paper library publication`.

### Task 6: Controlled canary and batch publication

**Files:**
- Update: `tools/paper_publication_manifest.json`
- Generate: `reports/paper-publication-<timestamp>.json`
- Generate: `source/_posts/*.md`, `source/images/papers/**`, `source/papers/*.pdf`

**Interfaces:**
- Consumes: verified local pipeline plus Notion credentials with database access.
- Produces: 49 unique Notion/Hexo entries or explicit blocked records, never silent skips.

- [ ] **Step 1: Run the full dry run** and manually inspect the manifest, deleted-ID exclusions, source spans and asset sizes.
- [ ] **Step 2: Run PRISM as the single-page canary** with `status=Invisible`; verify Notion structure, image fidelity, PDF download and idempotent rerun.
- [ ] **Step 3: Promote the canary and sync back to Hexo**; verify the local article, image URLs and PDF URL return 200.
- [ ] **Step 4: Publish the 20 reliable-summary candidates in small batches** only after title and evidence gates pass.
- [ ] **Step 5: Generate and review drafts for the 22 papers lacking a reliable summary**; publish only zero-error drafts.
- [ ] **Step 6: Install/configure MinerU only with user-approved environment changes, parse the remaining 7 PDFs, then pass them through the same review gate.**
- [ ] **Step 7: Verify both deleted mismatch IDs remain absent** from the PDF catalog, Notion queue and generated site.
- [ ] **Step 8: Run final `npm test`, `npm run build`, link checks and count reconciliation**; expect 74 catalogued PDFs and 74 eligible site papers unless further mismatches are found.
- [ ] **Step 9: Ask for explicit approval before commit/push/Pages deployment**, then execute only the approved release action.
