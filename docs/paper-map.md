# 论文足迹地图维护说明

## 当前设计

地图使用 Leaflet 与 OpenTopoMap 彩色地形底图，海洋、植被和地形具有天然色彩，不再依赖 CSS 滤镜。站点坐标统一为 WGS-84；CARTO Key 在构建期注入，源码不保存真实 Key，并作为 OpenTopoMap 不可用时的首级回退，随后才回退到 OpenStreetMap 标准底图。构建期只读取本地字典和已缓存图片；无法确认的位置不会落到默认点，仍保留在生成数据的 `unlocated` 清单中，但不占用地图初始界面。

当前 93 篇文章中有 92 篇论文；其中 57 篇具有可信实体坐标，35 篇保留在 `unlocated` 审计清单，显式虚拟论文为 0。第一作者机构补全脚本已从论文公开链接和本地 MinerU 文本中核验出 43 条机构记录。主导航仍使用 60% 准入规则；当前可定位样本覆盖率为 98.28%。

## CARTO Key

- 本地：复制 `.env.example` 为 `.env.local`，填写只允许 `localhost`、`127.0.0.1` 与 `*.localhost` 的本地开发 Key。`.env.local` 已被 Git 忽略。
- 线上：在 GitHub Actions Secrets 中添加 `CARTO_API_KEY`，使用只允许 `enkidulove90-lang.github.io` 的独立线上 Key。
- `scripts/map_carto_config.js` 每次构建生成 `/js/map-carto-config.js`，浏览器只会收到当前构建环境对应的一个 Key。
- 页面始终保留 OpenStreetMap 与 CARTO 署名；Key 被拒绝或瓦片服务失败时自动切换到 OSM。

## Notion 字段

- `location_type`：`Venue`、`Affiliation`、`Publisher` 或 `Virtual`。
- `venue_city`：实体会议举办城市。
- `affil_city`：作者机构城市，可为多个值。
- `corresponding_city`：主位置缺失时的可靠回退城市。
- `affiliation_name`：学校、企业或出版机构名称。
- `venue_name`：会议、期刊或平台名称。

这些字段由 `tools/notion_sync.py` 原样写入 Front-matter。

`tools/location_dict.json` 还维护地图展示字段：城市级 `hover_text`、`city_images`，以及机构级 `inst_desc`。图片元数据来自 Wikimedia Commons API，坐标缺失时由 Nominatim 查询；浏览器只读取已经下载到 `source/images/map/` 的本地图片。构建脚本用源 URL、Commons 文件标题和本地文件 SHA-256 三层去重，列表页再保证同一屏论文卡片不复用图片。每次刷新会避开该论文在本会话上一次使用的图片。

在线论文使用规范化 arXiv ID 作为固定身份键；同一 ID 的不同版本、链接写法或重复文章只生成一条记录。

## 解析优先级

1. `Affiliation` 先用 `affiliation_name` 命中 `tools/location_dict.json` 的别名和坐标。
2. `Venue` 使用 `venue_city`；`Publisher` 使用出版机构字典。
3. 仍未命中时回退 `corresponding_city`。
4. `Virtual` 使用显式虚拟点；它不会冒充实体会场。
5. 无可靠坐标时进入 `unlocated`，绝不使用北京或 `(0,0)` 作为物理兜底。

## 新地点维护

先在 `tools/location_dict.json` 增加机构正式名、别名、类型、城市和 WGS-84 坐标。已知机构完全离线解析，不访问外部服务。

只有本地调研新增地点时才运行：

```powershell
python tools/build_places.py --resolve-missing
```

该开关会以单线程、至少 1.1 秒间隔请求 Nominatim，并使用带站点标识的 User-Agent。确认结果后应把坐标固化进字典；GitHub Actions 只运行无网络补全的 `python tools/build_places.py`，避免周期性批量请求公共服务。

城市图片保存在 `source/images/map/`，浏览器不直接请求 Wikimedia。完成数据更新后运行：

```powershell
python tools/build_places.py
npm test
npm run test:python
npm run clean
npm run build
```

生成的 `/map_data.json` 包含 `places`、`papers`、`unlocated`、`links` 与覆盖元数据。

## 前端交互

- 初始界面：只有彩色地形世界地图和右侧无底板的透明竖排图例。
- 标记：透明背景的语义图标，不使用圆形黑底或蓝色描边；同城同类型机构合并为一个点。
- 悬停：复用一个全局卡片，展示城市图与短文案；离开标记后延迟关闭，进入卡片会取消关闭，点击卡片可打开城市详情。
- 轮播：详情图每 1 秒切换，打开新城市或关闭详情时都会先清理旧定时器。
- 点击标记：右侧滑出本地城市轮播图、宋体城市标题、机构简介与按时间排序的论文列表；打开新地点或关闭面板时会清理旧轮播定时器。
- 点击地图空白：立即收起详情面板，恢复纯地图状态。
- 五类图例：高校与科研院所、企业研究机构、出版与学术组织、线上会议和会议举办地均链接到独立列表页；列表以机构/会议 ID 分组，再逐行展示城市图、正式标题、元数据和文章真实简介。
- 全库映射：有可信坐标的论文显示在实体地点；其余论文只进入 `unlocated` 审计清单，不生成虚拟节点，也不伪造学校、会议或城市坐标。
- 左侧导航：`论文足迹` 由主题配置静态生成，不再依赖异步覆盖率脚本。
- 海量点位：超过 100 个 Marker 时自动启用 `Leaflet.markercluster` 分块聚合。
- 未定位：继续保存在静态数据中，不伪造坐标，也不在初始地图上展开长列表。
