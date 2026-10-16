# 定期检索并更新一篇论文

这份文档用于周期性地从学术网站发现候选论文，并且每个周期只向当前内容库加入一篇经过核验的论文。推荐采用“自动提醒或采集候选，人工确认一篇，流水线负责解析与发布”的方式，避免把标题相似、无高清图或摘要不可靠的论文自动发布到网站。

## 建议频率

- 每天：只收集候选，不发布。
- 每周一次：从候选中选择一篇，完成解析、中文摘要和图片核验后发布。
- 重要会议截稿或放榜期：临时提高到每 2～3 天一次。

一次运行最多发布一篇。上一篇仍处于 `needs_parse`、`needs_summary` 或图片校验失败状态时，不开始下一篇。

## 检索来源及用途

| 来源 | 用途 | 核验重点 |
|---|---|---|
| [arXiv](https://arxiv.org/) / [arXiv API](https://info.arxiv.org/help/api/index.html) | 发现最新预印本，下载 PDF 与 LaTeX 源码 | arXiv ID、版本日期、源码中的原始图片 |
| [Semantic Scholar Academic Graph API](https://api.semanticscholar.org/api-docs/) | 按关键词补充检索，查看引用关系和开放 PDF | DOI、arXiv ID、`openAccessPdf`、是否为同一篇论文 |
| [DBLP Search API](https://dblp.org/faq/How%2Bto%2Buse%2Bthe%2Bdblp%2Bsearch%2BAPI.html) | 确认计算机领域会议或期刊元数据 | venue、年份、作者、DOI |
| [OpenReview API](https://docs.openreview.net/getting-started/using-the-api) | 跟踪 ICLR、NeurIPS、ICML 等采用 OpenReview 的投稿 | 论文版本、会议、公开状态；评审意见不能当作论文结论 |
| [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | 用 DOI 补全出版社、期刊和日期信息 | DOI、出版类型、正式发表日期 |
| ACM Digital Library、IEEE Xplore、会议官网 | 最后确认正式版本和出版信息 | 不绕过付费墙；只保存有权使用的 PDF 和图片 |

推荐关键词轮换使用：`recommender systems`、`sequential recommendation`、`multimodal recommendation`、`LLM recommendation`、`retrieval augmented generation`、`agentic recommender`、`cold start recommendation`。同时关注 `cs.IR`、`cs.LG`、`cs.AI`、`cs.CL`、`cs.CV`，但不要仅凭分类决定是否入库。

## 每周期操作流程

### 1. 建立候选清单

记录每个候选的标题、arXiv ID、DOI、作者、日期、来源页面、PDF、代码仓库和一句入选理由。候选必须满足：

1. 与推荐系统、检索、LLM/Agent 或当前网站已有专题直接相关；
2. 能取得可靠摘要或完整正文；
3. 至少能取得一张与图注匹配的高清论文原图；
4. 不是站内已有文章，也不在排除名单中；
5. GitHub 链接来自论文、作者主页或仓库本身，不能用名称猜测。

### 2. 去重和排除

主键优先级为 `arXiv ID > DOI > 规范化标题`。先检查：

```powershell
rg "2601.12345|10\.1234/example" source/_posts tools/paper_exclusions.json
```

还要检查 Notion 数据库的 `arxiv_id` 字段。`tools/paper_exclusions.json` 中的 ID 不得重新导入，除非先人工确认并明确修改排除原因。

### 3. 保存 PDF 和解析结果

把合法取得的 PDF 放入：

```text
D:/recommendation-system-learning/data/papers/<arxiv-id>_<short-title>.pdf
```

优先从 arXiv LaTeX 源码提取原图：

```powershell
python tools/arxiv_source_figures.py `
  --ids 2601.12345 `
  --output-root .paper-work `
  --report reports/arxiv-source-2601.12345.json
```

如果没有源码或源码图片不可用，再用 MinerU 解析 PDF，并把 Markdown、layout JSON 和图片保存在：

```text
D:/recommendation-system-learning/data/parsed/<arxiv-id>_<short-title>/
```

图片选择顺序为：arXiv 源码原图、MinerU 原图、layout 裁图、PDF 图注裁图。不要使用网页截图代替论文原图。图片至少满足一个边长达到高清阈值，并且必须有可对应的原始图注。

### 4. 生成并审核中文摘要

摘要文件放入：

```text
D:/recommendation-system-learning/data/summaries/<arxiv-id>_<中文标题>_summary.md
```

固定栏目为：

```markdown
# 中文标题

**英文标题**: Original English Title

## 主要贡献
## 方法论
## 创新点
## 数据集与实验设置
## 实验条件
## 实验结果
## 总结
```

如果用 DeepSeek 生成初稿，输入必须来自 MinerU 正文或 arXiv LaTeX 源码。发布前人工核对数字、数据集、基线、消融结论、GitHub 链接和每张图的解释。英文模型名、数据集名和指标可以保留，正文解释应为中文。

### 5. 先执行只读检查

生成清单：

```powershell
python tools/paper_inventory.py `
  --library-root D:/recommendation-system-learning `
  --output reports/paper-publication-manifest.json
```

只检查目标论文，不写网站或 Notion：

```powershell
python tools/publish_paper_library.py `
  --ids 2601.12345 `
  --batch all `
  --report reports/paper-2601.12345-dry-run.json
```

报告必须满足：`selected_count = 1`、`blocked_count = 0`、`figure_count >= 1`，并且 `errors` 为空。

### 6. 写入网站

确认 dry-run 后才生成文章、复制图片和 PDF：

```powershell
python tools/publish_paper_library.py `
  --ids 2601.12345 `
  --batch all `
  --materialize `
  --report reports/paper-2601.12345-materialized.json
```

只有确实需要让 Notion 管理这篇新文章时，才增加 `--write-notion`；审核完成并准备公开时再增加 `--promote`。新文章附带本地源 PDF 时可以上传 PDF，已有文章原本没有源文件块时不自动回填。

### 7. 发布前验证

```powershell
python -m unittest discover -s tests -v
npm test
npm run build
npm run server -- --port 4322
```

在 `http://127.0.0.1:4322/article/paper-<arxiv-id>/` 检查：

- 标题、导语和主体解释为中文；
- 方法图与实验图都显示，浏览器中 `naturalWidth` 和 `naturalHeight` 不为 0；
- 数据集、基线、Benchmark、消融和总结没有互相错位；
- arXiv、GitHub、PDF 链接能访问；
- 页面中没有内部工作流说明、生成提示词或未经原文支持的数字。

### 8. 提交和发布

只提交本篇文章、对应图片/PDF以及确有必要的工具改动，不提交 `.paper-work`、临时报告或解析缓存。

```powershell
git add -- source/_posts/paper-2601.12345.md `
  source/images/papers/2601.12345 `
  source/papers/2601.12345.pdf
git commit -m "content: publish paper 2601.12345"
git push origin HEAD:source
gh workflow run publish.yml --ref source
```

发布结束后检查文章页、全部论文图片和 PDF 均返回 HTTP 200。

## 如何做到“每隔一段时间”

当前 `.github/workflows/publish.yml` 每 30 分钟执行的是 Notion 同步和 Hexo 发布，不会搜索或选择论文。不要把未经审核的检索结果直接接到这个工作流。

推荐的定时方式是：

1. 用 GitHub Actions、Windows 任务计划程序或 Codex 定时任务，每天生成候选清单；
2. 当候选清单有新内容时通知人工选择一篇；
3. 选择后按本文件的步骤执行单篇 dry-run、解析和发布；
4. 记录 `last_checked_at`、已见 arXiv ID/DOI 和失败原因，下次只处理增量。

如果以后实现自动发现脚本，建议接口固定为：一次最多输出一篇、默认只写候选 JSON、不下载受限内容、不写 Notion、不提交 Git。只有显式传入发布参数并通过全部质量门禁后，才允许进入 `publish_paper_library.py`。

## 失败处理

- 没有可靠摘要：保持 `needs_summary`，本周期不发布。
- 没有解析 Markdown：保持 `needs_parse`，先运行 MinerU。
- 没有高清图或图注无法对应：阻断发布，不用封面图冒充论文图。
- 标题与解析正文不匹配：重新下载正确 PDF 或重做摘要。
- 站内已有同 ID：只在明确需要修订时使用 `--refresh-existing --ids <id>`。
- 构建失败：不要推送生成产物；修复后重新运行全部测试和 Hexo 构建。

整个流程的原则是：检索可以自动化，选择与事实核验必须保守，发布永远只发生在单篇论文通过全部门禁之后。
