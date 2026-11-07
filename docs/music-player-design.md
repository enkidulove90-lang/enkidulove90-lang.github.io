# 悬浮音乐控件：接入设计与风险分析

> 版本：v1.0（2026-11-07）
> 形态：Butterfly 主题悬浮音符控件，纯本地 5 首随机播放
> 范围：`source/css/music-player.css` + `source/js/music-player.js` + `source/icons/logo-keyboard-music.svg` + `source/audio/`（待放入 mp3）+ `_config.butterfly.yml inject`

---

## 一、接入架构：两层解耦

```text
┌─ 前端（全部确定性逻辑，零 API 依赖）─────────────┐
│ 随机选歌 Math.random() → currentIndex            │
│ 上一首/暂停/下一首 → <audio> 本地文件循环滚动     │
│ 事件日志 → localStorage JSONL ring buffer        │
└──────────────────────────────────────────────────┘
         （在线模式仅作预留，当前不实现）
```

**核心决策：随机是纯前端逻辑**。页面每次刷新随机选起始曲目（`(Math.random() * n) | 0`），上一首/下一首用 `(index ± 1 + n) % n` 循环滚动。这保证了：即使未来加在线模式，API 也只负责"mid 换临时直链"，随机与播放控制永远不依赖外部服务——API 失效只影响在线曲目，本地播放零损失。

**接入点**：沿用仓库已有的 `_config.butterfly.yml → inject.head/bottom` 机制（与 left-nav/filter 等自定义资源同一通道），**不改主题文件**——主题升级时零冲突，这是维护成本最低的挂载方式。

| 注入 | 内容 |
|---|---|
| `inject.head` | `<link rel="stylesheet" href="/css/music-player.css">` |
| `inject.bottom` | `<script defer src="/js/music-player.js?v=20261107"></script>`（defer：不阻塞渲染；`?v=` 沿用仓库缓存刷新惯例） |

**全站生效**：inject 注入的是全站布局，所有页面都有悬浮控件；`Audio` 对象在首次点击时才创建（`preload="none"`），打开页面**零音频流量**。

## 二、日志系统设计（详细日志的接入）

### 2.1 事件流契约

每条日志一行 JSONL，字段固定：

```json
{"ts":"2026-11-07T13:00:00.000Z","event":"play","index":2,"track":"歌曲 3","detail":{"src":"/audio/song3.mp3"}}
```

| event | 触发点 | detail |
|---|---|---|
| `init` | 控件挂载完成 | `start_index`（本次随机起点）、`total` |
| `play` | 开始播放某曲目 | `src` |
| `play_rejected` | autoplay 被浏览器拦截 | 错误名（NotAllowedError 等） |
| `pause` | 用户暂停 | — |
| `ended` | 自然播完 | 触发自动下一首 |
| `next` / `prev` | 手动切歌 | — |
| `error` | 音频加载失败 | `src`（文件缺失/路径错） |

### 2.2 存储与出口

- **存储**：`localStorage["mp_logs_v1"]`，ring buffer 上限 200 行（防爆容量），写入失败静默降级（隐私模式/配额满不影响播放）。
- **查看**：控制台 `window.__musicPlayerLogs()` 返回数组。
- **导出**：`window.__musicPlayerDumpLogs()` 下载 `music-player-logs.jsonl`，可与后端日志体系（如 paper_intake 的 `logs --error-code`）对齐做离线分析。
- **明确不做网络上报**：站点是纯静态 GitHub Pages，没有接收端；上报会引入隐私与合规成本，收益为零。这是有意的设计边界，不是缺陷。

### 2.3 为什么不用 sessionStorage

播放历史是低频排障数据而非会话状态，localStorage 跨会话保留才能回答"昨天那首歌加载失败是什么时候"这类问题；代价是用户清理浏览器数据时日志丢失——可接受（见风险 R6）。

## 三、风险清单

| 编号 | 风险 | 表现 | 对策/现状 |
|---|---|---|---|
| R1 | **autoplay 政策** | 无用户手势时 `audio.play()` 被拒 | 已内置：不自动播放，首次点击音符启动；`play_rejected` 事件可观测拦截率 |
| R2 | **音频文件未就绪** | `source/audio/` 目前为空，点击播放报错 | 已内置：`error` 事件 → 面板红字提示具体路径 + 日志；放入 `song1..song5.mp3` 即恢复 |
| R3 | **音频体积入库** | 5 首 mp3 ≈ 20–50MB 直接进 git，仓库历史进一步膨胀（该仓库已有大文件史） | 建议 128k 码率（每首 ~3–4MB）；若将来超 50 首，迁移到 LFS 或 CDN，控件只需改 `PLAYLIST` 的 `src` |
| R4 | **移动端无 hover** | 面板无法弹出 | 已内置：`@media (hover: none)` 面板常驻小尺寸显示在图标上方，点击音符 = 播放/暂停 |
| R5 | **file:// 协议限制** | 双击本地 html 音频不加载 | 预览用 `hexo server`（站点本来就经 hexo 构建部署，线上无此问题） |
| R6 | **日志丢失** | 隐私模式/用户清缓存 → localStorage 清空 | 接受：日志定位为"排障辅助"而非审计数据；需要持久化时再评估上报方案 |
| R7 | **图标体积** | logo-keyboard-music.svg 52KB（512×512 全路径插画） | 一次性加载 + 浏览器缓存，可接受；追求极致可再导出 64px 精简版（<5KB） |
| R8 | **z-index 冲突** | 与主题其他 fixed 元素（回到顶部等）重叠 | 取 9999 高位；右上角 20px 定位与 butterfly 默认元素错开，如遇遮挡调 `.mp-widget` 即可 |
| R9 | **缓存不刷新** | 改了 JS 用户端不生效 | `?v=20261107` 版本参数，改动后递增（仓库既有惯例） |
| R10 | **多标签页同时播放** | 两个标签各开一个 Audio 叠音 | 未处理（个人使用影响小）；如需，用 BroadcastChannel 抢占式暂停，改动约 15 行 |

## 四、后续扩展路径（预留，未实现）

- **在线模式**：`PLAYLIST` 项加 `mid` 字段 + `MODE` 开关；API 调用必须走自建代理（Cookie 永不进前端代码），且**仅限本机自用，不部署公网**。日志体系天然覆盖：只需在换链失败时加 `url_fetch_error` 事件。
- **歌词/封面**：`PLAYLIST` 加 `lrc`/`cover` 字段，面板扩展，日志加 `lrc_missing`。
- **与后端日志体系合流**：`__musicPlayerDumpLogs()` 导出的 JSONL 格式与 development-process.md 的日志规范同构（ts/event/detail 三段），必要时可写一个 `logs --source music` 类命令统一查询。

## 五、验证清单

- [x] `inject` 注入后全站页面含控件 DOM
- [x] 刷新页面随机起始（init 日志可查 `start_index`）
- [x] hover 面板平滑出现，`pointer-events` 隐藏态不误触
- [x] 上一首/下一首循环滚动不越界
- [ ] 放入 5 个 mp3 后完整播放一轮（待音频文件就绪）
- [ ] `hexo server` 本地预览 + 移动端模拟器检查 hover:none 分支
