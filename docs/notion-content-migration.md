# 网站内容迁移到 Notion

本迁移只处理网站的正式内容资产：文章正文、摘要、论文插图和地图/城市图片。PDF、MinerU 中间产物、缓存、工作流状态与测试输出不上传。

## 安全边界

- 默认命令只生成清单，不访问或修改 Notion。
- 只有显式添加 `--write` 才会写入 Notion。
- 文章按 `slug` 幂等更新，不重复创建同一篇文章。
- 图片按 SHA-256 去重。
- 未嵌入文章的图片分组保存到 `Invisible` 状态的资产页。
- 超过 Notion 基础版 5 MiB 限制的栅格图，会在 `.notion-migration-cache/` 生成压缩上传副本；原图保持不变。
- 本地文件不会被删除。只有审计报告全部通过并由人工确认后，才能另行设计清理步骤。

## 本地执行

在被 Git 忽略的 `.env.local` 中配置：

```dotenv
NOTION_TOKEN=secret_xxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

先生成清单：

```powershell
python tools/notion_content_migration.py
```

确认 `reports/notion-content-migration.json` 后执行写入：

```powershell
python tools/notion_content_migration.py --write
python tools/notion_content_audit.py
```

审计会从 Notion 回读 Markdown，重新下载每张已上传图片，并比较正文与 SHA-256。只有审计退出码为 0，才代表本批次全部对应。

## GitHub Actions 执行

仓库 Secrets 已配置时，可在 Actions 中手动运行 `Migrate site content to Notion`：

1. 第一次保持 `write=false`，下载并查看清单 artifact。
2. 确认运行所用分支已经包含全部本地文章与图片。
3. 再运行 `write=true`；任务会迁移后立即执行云端回读审计。
4. 下载 `notion-content-migration-report`，保留迁移与审计报告。

GitHub Secrets 无法被下载回本机，这是平台的安全设计。因此，本地未提交内容只能使用本机 `.env.local` 迁移；GitHub Actions 只能看到已经提交并推送到所选分支的内容。
