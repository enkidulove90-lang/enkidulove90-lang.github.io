# 论文库批量入站与 Notion 发布规范

## 目标

把 `D:\recommendation-system-learning\data\papers` 中尚未进入个人网页的规范 PDF，经过可靠性校验、MinerU 解析与文章结构化整理后，幂等写入现有 Notion 内容数据库，并由现有 Notion→Hexo→GitHub Pages 流程展示。

## 当前基线

- 规范 PDF：74 篇；当前网页已覆盖 25 篇，待处理 49 篇。
- 可靠性校验后，待处理论文中：20 篇有可靠摘要和 MinerU 解析稿；22 篇有解析稿但缺少可靠摘要；7 篇没有可用解析稿。
- 错配 ID `2504.00678`、`2505.00556` 的 PDF、解析稿、摘要和派生记录已经删除，不得重新进入发布清单。
- 当前解析资产：74 份正文 Markdown、2786 张图片。
- 本机未设置 `NOTION_TOKEN` / `NOTION_DATABASE_ID`，也没有可直接调用的 `mineru` 命令。

## 内容质量门槛

每篇文章必须包含：

1. 简介；
2. 论文方法；
3. 论文原图及逐图解释；
4. 模块创新点和创新内容；
5. 实验数据集选择；
6. 消融实验；
7. benchmark 结果和解释；
8. 总结；
9. References；
10. 论文链接、GitHub 链接（存在官方仓库时）和站内 PDF 链接。

所有结论和数字必须能追溯到 MinerU Markdown、原始 PDF、论文元数据或官方代码仓库。禁止发布内部项目比较、实验代号、研究笔记或无法由论文支撑的推断。没有某项实验时必须明确写“论文未报告”，不得补写。

## 图片与 PDF

- 优先使用 MinerU 输出的原图；矢量图或拼贴图缺失时，使用现有版面裁剪工具从原 PDF 以 200 DPI 或更高导出。
- 入选正文的图片至少满足宽度 1280px 或高度 720px；确无高分辨率原图时记录例外，不得通过单纯插值冒充高清原图。
- 图片必须与 Figure/Table 编号和图注匹配，并附中文解释。
- 新导入文章若明确附带本地源 PDF，则上传到对应 Notion 页面，并同步到站点 `source/papers/`；已有文章若原本未引用源文件，不做 PDF 回填。

## Notion 与发布行为

- 以 arXiv ID 作为幂等键；重复执行只能更新同一页面，不能产生重复条目。
- 首次写入使用 `status=Invisible`，通过完整性检查后才改为 `Published`。
- 复用现有字段：`title`、`status`、`type`、`slug`、`summary`、`date`、`category`、`tags`、`year`、`venue_type`、`venue_name`。
- 仅对需要附带源文件的新文章使用 Notion 当前文件上传 API；超过 20 MiB 的 PDF 使用 multipart 上传。
- 批次顺序：dry-run 清单 → PRISM 单篇 canary → 可靠摘要批次 → 新摘要批次 → 最终站点构建。
- 未经用户明确指示，不提交、推送或触发 GitHub Pages 发布。

## 验收

- 清单精确覆盖 74 篇 PDF，待处理集合为 49 篇且无重复 arXiv ID。
- 两个已删除错配 ID 永不重新进入可发布队列。
- 每篇发布稿通过必需章节、链接、图片尺寸、引用来源和泄漏词检查。
- Notion canary 可重复运行且只得到一个页面。
- Notion→Hexo 同步后，本地 `npm test` 与 `npm run build` 均通过，文章图片和 PDF 返回 200。
