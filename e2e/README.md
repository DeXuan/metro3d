# Metro 3D · 浏览器端 E2E 回归套件

针对单文件 3D 应用（`index.html`：Three.js 内联 + `METRO_DATA` 内联，约 2.7 MB）的
真实浏览器端回归测试。断言只依赖**可观测状态**——`window.__diag()`、DOM 文本与显隐、URL——
不触摸内部变量或 three.js 对象结构，因此渲染层重构不会误伤用例。

## 用例分组

- `core.spec.js`（E1–E12）：功能回归，桌面 + 移动双项目。
- `visual.spec.js`（V1–V4）：**语义级视觉回归**——截图回传浏览器解码后统计颜色多样性，
  判断「城市/星图确实渲染出内容、浅色主题光晕不失效、移动端全图适配且控件不被遮挡」。
  刻意不做 PNG 字节哈希/逐像素 diff：WebGL 在 CI 软件渲染与本地 GPU 间抗锯齿差异大，
  字节级对比会制造大量假阳性。V1–V4 判定的是**语义可见性**，能抓住整屏空白/全白/全黑这类真实回归。
  运行：`npx playwright test visual.spec.js`

## 快速开始

```bash
cd e2e
npm ci                                  # 或 npm install
npx playwright install chromium         # 首次需要（CI 用 --with-deps）

npm test                                # 离线跑仓库自带的 index.html（file://）
npm run test:headed                     # 带界面调试
```

默认 `baseURL` 是仓库根目录 `index.html` 的 `file://` 绝对路径，**无需任何本地服务器**。

### 指向线上站点

```bash
# Git Bash / macOS / Linux
BASE=https://xn--888-vw3e05fxyzc07e.cn:9006/web/metro3d/ npx playwright test

# PowerShell
$env:BASE='https://xn--888-vw3e05fxyzc07e.cn:9006/web/metro3d/'; npx playwright test

# CMD
set BASE=https://xn--888-vw3e05fxyzc07e.cn:9006/web/metro3d/ && npx playwright test
```

线上站点启用了 Service Worker，第二次导航可能命中缓存；排查「线上像旧版」时，
在 DevTools 里 Unregister service worker 再测，或直接用离线模式验证当前代码。

### 只跑某些用例

```bash
npx playwright test -g "E5"             # 单条
npx playwright test --project=chromium  # 只跑桌面（E1–E11）
npx playwright test --project=mobile    # 只跑移动端（E12）
```

## 两个 project

| project | 视口 | 覆盖用例 |
|---|---|---|
| `chromium` | 1440×900 桌面 | E1–E11（核心功能） |
| `mobile` | 390×844，`isMobile` + touch | E12（移动端冒烟） |

用例标题里带 `E12` 的只在 mobile 跑，其余只在 chromium 跑（配置里用 `grep` / `grepInvert` 切分）。

## 用例清单与守护目标

| 用例 | 操作 | 断言 | 守护什么 |
|---|---|---|---|
| **E1 启动** | 加载页面 | `#app-ver` 以 `v` 开头；`__diag()` 含 `reduce`/`autoRotate`/`renders` 且 `renders > 0`；无 pageerror | 引擎/数据内联没坏、诊断钩子契约没变 |
| **E2 城市切换** | `#sel-city` → `beijing` | `#stat-line` 含「北京」，下拉值同步；仍为城市模式 | 切城后线网统计真的重算，不残留上一城 |
| **E3 搜索** | 输入「八达岭」→ 点首个 `.sr` | 结果 ≥1；约 0.6s 后 `#info-card.show` 且含「102」 | 搜索索引、跨城飞行、信息卡埋深渲染 |
| **E4 深度之最** | 点 `#btn-deeptop` → 点首行 | 面板 `.show`，≥10 行；首行含「八达岭」「-102」；点击后城市切到「京张」且信息卡显示 | 全国深埋榜 TOP20 计算 + 跨城直达复用 `searchGo` |
| **E5 星图** | 点 `#btn-nation` | `__diag().nation === true`；`#nation-time.show`；`#nt-stat` 匹配 `53 城 · 377 线 · 8180 站`；URL 含 `nation=1` | 星图进入、总统计口径、深链写入 |
| **E6 星图时间轴** | 滑杆设 1971 / 2010 | 统计分别为 `1 城 · 1 线 · 36 站` / `17 城 · 67 线 · 1493 站`；`nationYear` 跟随 | 按建成年份分桶的 55 年生长史与真实统计口径 |
| **E7 星图俯冲** | 先进北京 → 进星图 → 点上海星点 | 约 3s 后 `nation === false`，下拉含「上海」 | 星点 raycast 命中、俯冲→重建→开场扫入一条龙、下拉与 `state.cityId` 同步 |
| **E8 Esc 退出** | 星图内按 Escape | `nation === false`，`#nation-time` 隐藏 | 键盘退出路径与控件收尾（不留残影） |
| **E9 深链** | `?nation=1&year=1993`，等 8s | `nation === true`，时间轴控件可见 | 深链进星图 + 自动播放到 2026 不被 `syncUrl` 抹掉 |
| **E10 渲染健康** | 城市模式等 3s | `renders` 增长，`paused === false` | 渲染循环没死（空闲降帧可以，但不能停帧或误判暂停） |
| **E11 无静默崩溃** | 切城 → 搜索 → 深埋榜开合 → 星图进出 | 本次会话 `pageerror` / `console.error` / `__diag().errors` 全为空 | try/catch 吞掉的异常也要留证据，防「界面正常但功能已死」 |
| **E12 移动端冒烟** | 移动视口加载 → 关引导 → 展开视图面板 → 进星图 | 无横向溢出（`scrollWidth ≤ innerWidth + 2`）；`#btn-nation` 可点；`nation === true` | 移动端布局溢出、面板折叠后仍能进星图 |

## 关于等待

单文件应用启动要跑约 2.7 MB 内联脚本（Three.js + 8180 站数据），本机冷启动 2–4s，
再叠加「开场俯冲」相机动画约 4.5s 才稳定。因此：

- `boot()` 等的是 **`__diag()` 可用 + `#loading.hide`**（应用自己就绪的信号），
  而不是固定 sleep；随后关掉首次访问引导（`#tour-card` 会盖住全屏遮罩挡点击）。
- 能用 `page.waitForFunction` 轮询状态的（info-card 出现、`nation` 翻转）就轮询，
  不用固定 sleep。
- 用例里保留的固定等待只有两处是**产品行为本身决定的**：
  E4 的 2.5s（跨城飞行 + 信息卡）与 E9 的 8s（`year=1993` 深链自动播放到 2026 约 6s）。
- 星图俯冲（E7）不能直接拿 `__nationScreen()` 的第一次读数就点：进入星图时相机还在飞行，
  星点投影可能落在视口外。`waitStableViewportPoint()` 会轮询到「落在视口内且相邻两次读数
  相差 ≤ 8px」才返回坐标。

## 已知缺陷（如需登记，用这套写法）

如果用例暴露了应用的真实缺陷，**不要改应用**，用下面写法让套件保持绿色并留下证据：

```js
test('E13 xxx', async ({ page }) => {
  // KNOWN-BUG: 描述 + 实际 vs 期望
  test.fixme(true, 'KNOWN-BUG: ...');
  ...
});
```

## CI

`.github/workflows/ci.yml` 的 `e2e` job：跑完 3 项静态检查（`data/build.py --check`、
`data/check_data.py`、`data/check_html.py`）之后，`npm ci` + `playwright install --with-deps
chromium` + `npx playwright test`。失败时上传 `e2e/test-results` 作为 artifact。