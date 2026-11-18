# app.js 逻辑分区地图（v2.4.0）

> app.js 是单模块作用域（105 顶层函数 / 84 顶层变量相互引用），**物理拆分风险大于收益**，
> 因此这里用「逻辑分区 + 行号锚点」实现可维护性；构建仍内联为单文件产物（离线/零外链）。

| 分区 | 主要函数 | 定位方式 |
|---|---|---|
| 渲染核心 (core) | 17 个 | `project` L161, `makeLabel` L194, `makeRiverChar` L212, `focusBridge` L920, `buildWorld` L959, `disposeObj` L1302 |
| UI/面板 (ui) | 19 个 | `populateSelectors` L1356, `updateStats` L1403, `updateLegend` L1431, `buildUIList` L1470, `__deeptopOpen` L2315, `applyNationYear` L2559 |
| 数据/搜索 (data) | 1 个 | `isSubseq` L4019 |
| 状态/深链 (state) | 5 个 | `startScreensaver` L3012, `ssNext` L3023, `exitScreensaver` L3031, `resetIdle` L3039, `syncUrl` L3879 |

## 导航约定

- 改渲染 → 搜 `buildWorld` / `renderFrame`
- 改 UI 面板 → 搜 `populateSelectors` / `enterNation` / `__deeptopOpen`
- 改数据 → `data/metro_all.json` 是唯一事实源，改后跑 `python data/build.py`
- 深链参数 → 搜 `applyDeepLink` / `syncUrl`

## 为什么不做物理拆文件

app.js 的函数与变量在同一模块作用域高度耦合（事件监听、初始化顺序、闭包共享状态）。
按文件切开需要重排 189 个符号依赖，引入跨文件 import/迁移错误的风险远高于「单文件 4352 行」带来的可读性问题。
逻辑分区 + 本文件已给出的行号锚点 + 前述 4 道门禁 + 16 条 E2E，已提供足够的安全网。
