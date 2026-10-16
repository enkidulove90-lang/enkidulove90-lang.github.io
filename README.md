# enkidulove90-lang.github.io · source 分支

个人「推荐系统内容分享库」站点。**内容在 Notion 写，本仓库只存 Hexo 源码与自动同步的 Markdown。**

## 架构

```
Notion 数据库（写文章）
   │  GitHub Actions 每 30 分钟（或手动 / webhook 触发）
   ▼
tools/notion_sync.py   Notion → source/_posts/*.md（增量，图片下载进 source/images/）
   ▼
hexo generate            生成静态页到 public/
   ▼
peaceiris/actions-gh-pages  强推到 main 分支
   ▼
GitHub Pages             https://enkidulove90-lang.github.io（从 main 根发布）
```

## 分支说明

- `source`（本分支）：Hexo 源码、`_config.yml`、`tools/notion_sync.py`、workflow、旧站内容 `source/legacy/`
- `main`：**只放构建产物**，由 Actions 全量覆盖，不要手改

## 配置 Secrets（Settings → Secrets and variables → Actions）

| Secret | 说明 |
|---|---|
| `NOTION_TOKEN` | internal integration token（`ntn_` 开头），需在 Notion 目标库 `... → Connections` 里把本 integration 连上 |
| `NOTION_DATABASE_ID` | 内容数据库 ID（库页面 URL 中 32 位十六进制段） |

## Notion 数据库字段（必填）

`title`(title) · `status`(select: **Published**/Invisible) · `type`(select: **Post**) · `slug`(rich_text，可空自动生成) · `summary`(rich_text，可空) · `date`(date) · `category`(select) · `tags`(multi_select) · `arxiv_id`(rich_text，论文条目的幂等键)

论文批量导入默认只做 dry-run。新建论文文章明确附带本地源 PDF 时，才把 PDF 上传到对应 Notion 页面；已有文章如果原本没有源文件块，不会自动回填。Notion 文件上传使用 API `2026-03-11`，大于 20 MiB 的文件自动走 multipart。

> 若你的 `status` 字段是 checkbox 而非 select，改 `tools/notion_sync.py` 里 `pq` 的过滤器。

## 旧内容

旧站（2025/2026 论文页、music/movies/travel 等）原样保留在 `source/legacy/`，构建时直接拷入 `public/legacy/`，不经渲染。导航里「旧站存档」指向 `/legacy/`。注意：`legacy/2026` 内部链接仍是旧站相对路径，深层页面互链可能失效，属预期行为。

## 本地预览

```bash
npm install
export NOTION_TOKEN=... NOTION_DATABASE_ID=...   # 可选，不填则只构建已有文章
python tools/notion_sync.py
npx hexo server
```

## 手动触发发布

GitHub 仓库页 → Actions → "Build & Publish" → Run workflow。
