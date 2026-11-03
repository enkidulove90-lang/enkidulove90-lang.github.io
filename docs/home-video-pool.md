# 首页本地视频池：构建与验收

范围：仅 Butterfly 首页 `#page-header.full_page`。文章卡片、分类筛选、地图和文章页不读取视频池。普通站点构建不访问 Coverr；人工低频运行 `npm run videos:refresh -- --env-file <本机 .env 路径>` 才会访问 API。密钥只在 Node 进程内通过 `Authorization` 头使用，不写入网页、manifest 或日志。

## 更新流程

1. 在 `tools/coverr_hero_selection.json` 审核、固定 5–10 个 Coverr 视频 ID。不要使用“热门列表直接入池”。
2. 确保本机有 FFmpeg，可通过 `FFMPEG_PATH` 指定；执行 `npm run videos:refresh -- --env-file <本机 .env 路径>`。
3. 脚本只接受 16:9、源分辨率至少 1920×1080、3–12 秒的视频。源 MP4 超过 8 MiB 时构建时转为无音轨 1280×720 H.264；封面转为本地 WebP。输出最多 8 个 MP4，至少 5 个，单条不超过 8 MiB，视频和封面合计不超过 40 MiB。未达到 5 条时保留旧 manifest。
4. 私有下载副本保存在被 Git 忽略的 `data/videos/coverr-hero/`；用于 GitHub Pages 的精选文件位于 `source/videos/hero/`。`source/videos/hero/manifest.json` 只含本地路径、尺寸、时长、字节数、哈希与来源标记。
5. 执行 `npm test` 和 `npm run build`，检查 `git status`，确认 `.env`、`data/videos/`、大体积原件未进入提交。当前 Key 曾在聊天中明文出现；本次经用户授权用于真实验证，发布后应尽快在 Coverr 后台轮换，不应写入仓库或网页产物。

Coverr 官方 [API 文档](https://api.coverr.co/docs/videos/) 说明了 `mp4_download` 和签名 URL；本地池只保存媒体字节，不发布这些 URL。[署名要求](https://api.coverr.co/docs) 是可点击的 Coverr logo，页面使用本地官方白色 logo 链接到 Coverr。

## 2026-11-04 验收记录

| 项目 | 方法 | 结果 |
| --- | --- | --- |
| U1–U5、转码、体积、路径、清理 | `npm test` 的 Node 单测 | 通过 |
| I1–I5、播放拒绝 | JSDOM 注入桌面/窄屏/减少动态效果/坏 URL | 通过 |
| 完整站点回归 | `npm test` | 98 passed, 0 failed |
| Hexo 构建 | `hexo generate --silent` | 通过；输出 6 MP4 + 6 WebP |
| 文件完整性 | `tests/video-pool-artifacts.test.js` 重新读盘计算 SHA-256、大小与格式 | 通过；总计 36,564,745 字节 |
| 桌面 Chrome | 本地 Hexo + Chrome CDP，1280×800、普通动态效果 | `readyState=4`、`paused=false`、`currentTime=2.97s`；本地 MP4 和官方 logo 可见 |
| 手机/减少动态效果 | JSDOM + Chrome 默认小视口、减少动态效果 | 不请求 manifest、不设置 MP4 `src`；保留 Butterfly 原 WebP 背景 |
| 本地静态降级 | Chrome CDP，390px + `prefers-reduced-motion: reduce` | 无视频节点；背景 URL 为本地 `/img/home-hero-fallback.webp` |
| iOS Safari 真机 | 当前 Windows 环境不可执行 | 待真机验证；不宣称已通过 |

视觉证据：[桌面播放](../evidence/home-hero-desktop.png)、[窄屏静态降级](../evidence/home-hero-static-fallback.png)。原 Butterfly 首页 WebP 已固定为本地 `source/img/home-hero-fallback.webp`；视频失败、播放被阻止或动态效果减少时退回这张静态背景，断网时也不依赖 Picsum。移动端默认不拉取完整 MP4。

## 未覆盖风险

- 本地 Chrome/Hexo 已验证自动播放，但 iOS Safari 行内播放与 GitHub Pages CDN 的 Range/缓存行为需要上线前后分别验证。
- Coverr 视频的使用应符合其 API 的非转售/非商业条款；若站点用途变化，需重新核对授权。
- 这不是一个自动按时抓取任务。手工刷新便于审核画面与控制 Demo API 的 50 次/小时配额；若未来增加调度，必须保留人工准入清单和失败时不替换旧 manifest 的规则。
