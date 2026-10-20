# 论文足迹地图设计规范

## 目标

以可信位置为原则展示论文与真实世界的联系。地图使用静态生成的数据、本地图片与 WGS-84 坐标；缺失地理信息的论文保持可阅读，但不显示虚假点位。

## 数据流

1. `tools/notion_sync.py` 同步位置语义与城市字段。
2. `tools/build_places.py` 先查 `tools/location_dict.json`，仅在维护者显式传入 `--resolve-missing` 时使用 Nominatim；图片下载到本站并缓存。
3. `source/_data/places.json` 保存地点、论文关系和无法解析的记录。
4. `scripts/map_data.js` 生成单一的 `/map_data.json`，同时给出已定位与未定位论文。
5. `/map/` 使用 Leaflet + CARTO Voyager 原生彩色底图，构建期注入当前环境的 CARTO Key，失败时回退到 OpenStreetMap。初始状态只显示地图和不透明白色图例；悬停复用单例图文卡片，点击标记时右侧滑出城市轮播图、机构简介与论文列表，点击地图空白时收起。

## 数据约束

- `places` 每项必须有稳定 `id`、`name`、`wgs84`、站内 `image` 与 `description`。
- 坐标数组顺序统一为 `[longitude, latitude]`；交给 Leaflet 时再转为 `[latitude, longitude]`。
- `assignments` 记录 `paper_id`、`place_id`、位置语义、显示标签和来源。
- `unlocated` 明确保留无法可靠定位的论文，禁止默认城市和 `(0,0)` 物理兜底。

## 服务边界

- 自动构建只消费本地字典和缓存，不周期性查询公共地理编码服务。
- Nominatim 补全是本地、显式、限速的维护动作；结果审核后固化到字典。
- 浏览器只请求瓦片服务和本站资源；本地与线上分别使用受 Referer 限制的 CARTO Key，源码不保存真实 Key。
- 城市图构建期下载到本站，前端不直接访问 Wikimedia API。

## 验收

- 海外机构能通过本地别名表命中机构级 WGS-84 坐标。
- 未定位论文保留在静态数据中，不出现在地图上，也不占用初始界面。
- 图标透明无圆底，悬停放大；点击后才滑出图文面板，点击地图空白即关闭。
- 页面源码不含真实 Key；构建产物只包含当前环境对应的受限 CARTO Key。
- 低于准入阈值时导航门控仍生效。
