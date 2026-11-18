# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: core.spec.js >> E7 星图俯冲：点击上海星点 → 退出星图并切到上海
- Location: tests\core.spec.js:200:1

# Error details

```
Error: expect(received).toContain(expected) // indexOf

Expected substring: "上海"
Received string:    "北京（27线/527站）"
```

# Page snapshot

```yaml
- main [ref=e2]:
  - generic "全国星图：方向键选择城市，Enter 进入，Esc 退出" [active] [ref=e3]
  - generic [ref=e4]:
    - heading [level=1] [ref=e5]:
      - text: 城市地铁 · 地下三维视图
      - button "⤴" [ref=e8] [cursor=pointer]
    - generic [ref=e9]:
      - combobox "选择城市" [ref=e10]:
        - option "北京（27线/527站）" [selected]
        - option "上海（24线/536站）"
        - option "广州（23线/418站）"
        - option "成都（18线/476站）"
        - option "重庆（16线/345站）"
        - option "杭州（16线/394站）"
        - option "深圳（16线/432站）"
        - option "南京（15线/303站）"
        - option "天津（14线/275站）"
        - option "武汉（13线/351站）"
        - option "郑州（13线/285站）"
        - option "西安（12线/285站）"
        - option "香港（10线/121站）"
        - option "合肥（9线/225站）"
        - option "宁波（9线/210站）"
        - option "苏州（9线/275站）"
        - option "青岛（8线/195站）"
        - option "长春（8线/168站）"
        - option "大连（7线/108站）"
        - option "济南（7线/123站）"
        - option "昆明（7线/128站）"
        - option "长沙（7线/170站）"
        - option "福州（6线/119站）"
        - option "沈阳（6线/159站）"
        - option "南宁（5线/106站）"
        - option "厦门（5线/102站）"
        - option "台北（5线/118站）"
        - option "无锡（5线/97站）"
        - option "佛山（4线/106站）"
        - option "贵阳（4线/99站）"
        - option "南昌（4线/122站）"
        - option "徐州（4线/76站）"
        - option "哈尔滨（3线/78站）"
        - option "京津冀 · 京张高铁 / 京津城际（3线/16站）"
        - option "绍兴（3线/43站）"
        - option "石家庄（3线/63站）"
        - option "常州（2线/44站）"
        - option "东莞（2线/40站）"
        - option "高雄（2线/42站）"
        - option "呼和浩特（2线/44站）"
        - option "金华（2线/30站）"
        - option "兰州（2线/29站）"
        - option "洛阳（2线/34站）"
        - option "南通（2线/45站）"
        - option "太原（2线/47站）"
        - option "温州（2线/38站）"
        - option "乌鲁木齐（2线/23站）"
        - option "芜湖（2线/36站）"
        - option "澳门（1线/13站）"
        - option "滁州（1线/10站）"
        - option "台中（1线/14站）"
        - option "台州（1线/15站）"
        - option "桃园（1线/22站）"
        - option "中国超级桥梁（11桥）"
      - combobox "选择线路" [ref=e11]:
        - option "全部线路 · 网络总览" [selected]
        - option "S1线 · 苹果园—石厂"
        - option "1号线八通线 · 苹果园—环球度假区"
        - option "2号线 · 环线"
        - option "3号线 · 东四十条—东坝北"
        - option "4号线大兴线 · 天宫院—安河桥北"
        - option "5号线 · 宋家庄—天通苑北"
        - option "6号线 · 潞阳—金安桥"
        - option "7号线 · 环球度假区—北京西站"
        - option "8号线 · 瀛海—朱辛庄"
        - option "9号线 · 郭公庄—国家图书馆"
        - option "10号线 · 环线"
        - option "11号线 · 模式口—新首钢"
        - option "12号线 · 东坝北—四季青桥"
        - option "13号线 · 西直门—东直门"
        - option "14号线 · 善各庄—张郭庄"
        - option "15号线 · 俸伯—清华东路西口"
        - option "16号线 · 北安河—宛平城"
        - option "17号线 · 嘉会湖—未来科学城北"
        - option "18号线 · 马连洼—天通苑东"
        - option "19号线 · 新宫—牡丹园"
        - option "昌平线 · 昌平西山口—蓟门桥"
        - option "大兴机场线 · 草桥—大兴机场"
        - option "房山线 · 阎村东—东管头南"
        - option "首都机场线 · 3号航站楼—北新桥"
        - option "西郊线 · 巴沟—香山"
        - option "燕房线 · 阎村东—燕山"
        - option "亦庄线 · 宋家庄—亦庄火车站"
        - option "更多线路 · 敬请期待" [disabled]
    - textbox "🔍 搜索站点 / 线路 / 大桥" [ref=e13]
    - generic [ref=e14]: 上海轨道交通线网 · 24 条线路 · 536 座车站全线地下埋深示意 0~35.9 m · 点击线路可聚焦查看
    - generic [ref=e15]:
      - generic [ref=e16]:
        - button "1号线" [ref=e17] [cursor=pointer]
        - button "2号线" [ref=e20] [cursor=pointer]
        - button "3号线" [ref=e23] [cursor=pointer]
        - button "4号线" [ref=e26] [cursor=pointer]
        - button "5号线" [ref=e29] [cursor=pointer]
        - button "6号线" [ref=e32] [cursor=pointer]
        - button "7号线" [ref=e35] [cursor=pointer]
        - button "8号线" [ref=e38] [cursor=pointer]
        - button "9号线" [ref=e41] [cursor=pointer]
        - button "10号线" [ref=e44] [cursor=pointer]
        - button "11号线" [ref=e47] [cursor=pointer]
        - button "12号线" [ref=e50] [cursor=pointer]
        - button "13号线" [ref=e53] [cursor=pointer]
        - button "14号线" [ref=e56] [cursor=pointer]
        - button "15号线" [ref=e59] [cursor=pointer]
        - button "16号线" [ref=e62] [cursor=pointer]
        - button "17号线" [ref=e65] [cursor=pointer]
        - button "18号线" [ref=e68] [cursor=pointer]
        - button "机场联络线" [ref=e71] [cursor=pointer]
        - button "浦江线" [ref=e74] [cursor=pointer]
        - button "磁浮线" [ref=e77] [cursor=pointer]
      - generic [ref=e80]: 高架段
      - generic [ref=e82]: 换乘站
      - generic [ref=e84]: ◆ 地标建筑 7 座（名称+高度标注）
  - generic [ref=e85]:
    - navigation "本文目录" [ref=e86]:
      - group [ref=e87]:
        - generic "▸ 本文目录 5 节" [ref=e88] [cursor=pointer]:
          - text: ▸ 本文目录
          - generic [ref=e89]: 5 节
        - list [ref=e90]:
          - listitem [ref=e91]:
            - link "视图控制" [ref=e92] [cursor=pointer]:
              - /url: "#v2sec-1"
          - listitem [ref=e93]:
            - link "城市对比✕" [ref=e94] [cursor=pointer]:
              - /url: "#v2sec-2"
          - listitem [ref=e95]:
            - link "站点 · 深度›" [ref=e96] [cursor=pointer]:
              - /url: "#list-title"
          - listitem [ref=e97]:
            - link "站名" [ref=e98] [cursor=pointer]:
              - /url: "#ic-name"
          - listitem [ref=e99]:
            - link "欢迎使用 · 三维立体地铁视图" [ref=e100] [cursor=pointer]:
              - /url: "#v2sec-5"
    - heading "视图控制" [level=2] [ref=e101]
    - generic [ref=e102]:
      - generic [ref=e103]: 垂直夸张
      - slider [ref=e104]: "200"
      - generic [ref=e105]: 200×
    - generic [ref=e106]:
      - button "深度着色" [ref=e107] [cursor=pointer]
      - button "站点标注" [ref=e108] [cursor=pointer]
      - button "地层参考面" [ref=e109] [cursor=pointer]
      - button "🚆 列车" [ref=e110] [cursor=pointer]
      - button "⏱ 年代" [ref=e111] [cursor=pointer]
      - button "📈 剖面" [ref=e112] [cursor=pointer]
      - button "⚖ 对比" [ref=e113] [cursor=pointer]
      - button "🗂 图层" [ref=e114] [cursor=pointer]
      - button "📷 截图" [ref=e115] [cursor=pointer]
      - button "🎬 录制" [ref=e116] [cursor=pointer]
      - button "🏆 深度之最" [ref=e117] [cursor=pointer]
      - button "🗺 全国" [ref=e118] [cursor=pointer]
      - button "⬇ GLB" [ref=e119] [cursor=pointer]
      - button "⛶ 全屏" [ref=e120] [cursor=pointer]
      - button "🔌 屏保" [ref=e121] [cursor=pointer]
      - button "📍 标注" [ref=e122] [cursor=pointer]
      - button "🌙 深色" [ref=e123] [cursor=pointer]
      - button "🌃 夜景" [ref=e124] [cursor=pointer]
      - button "重置视角" [ref=e125] [cursor=pointer]
      - button "▶ 沿线巡航" [ref=e126] [cursor=pointer]
  - text: ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶ ▶
  - status [ref=e127]
  - button "☰ 536" [ref=e128] [cursor=pointer]:
    - generic [ref=e129]: ☰
    - generic [ref=e130]: "536"
  - generic "罗盘：N=正北 · 点击回正北" [ref=e131] [cursor=pointer]:
    - generic [ref=e132]:
      - generic [ref=e133]: "N"
      - generic [ref=e134]: W
      - generic [ref=e135]: E
      - generic [ref=e136]: S
    - generic [ref=e138]: 0°
  - generic: 拖拽旋转 · 滚轮缩放 · 点击站点/列车查看详情 · / 搜索 · R 复位 · T 列车 · 📷 截图 · ⛶ 全屏 · Esc 关闭面板
  - generic: v2.1.0 · 数据快照 2026-11 · 53 城 / 377 线 / 8180 站 · 车站埋深为依据公开资料整理的近似示意值 · 站点坐标源自 OpenStreetMap线路走向与深度以官方资料为准
  - generic: 正在加载 3D 引擎与线路数据…
```

# Test source

```ts
  120 | 
  121 |   await page.selectOption('#sel-city', 'beijing');
  122 |   await expect(page.locator('#stat-line')).toContainText('北京');
  123 |   await expect(page.locator('#sel-city')).toHaveValue('beijing');
  124 | 
  125 |   const d = await diag(page);
  126 |   expect(d.nation, '切城后仍应处于城市模式').toBe(false);
  127 | });
  128 | 
  129 | test('E3 搜索：八达岭 → 下拉首项 → 信息卡显示埋深 102', async ({ page }) => {
  130 |   await boot(page);
  131 | 
  132 |   await page.fill('#st-search', '八达岭');
  133 |   const results = page.locator('#search-drop .sr');
  134 |   await expect(results.first()).toBeVisible();
  135 |   expect(await results.count()).toBeGreaterThanOrEqual(1);
  136 | 
  137 |   // 应用监听的是 mousedown（避免 blur 先后顺序问题），用真实事件派发
  138 |   await results.first().dispatchEvent('mousedown');
  139 | 
  140 |   await page.waitForFunction(() => {
  141 |     const card = document.getElementById('info-card');
  142 |     return !!card && card.classList.contains('show') && card.textContent.includes('102');
  143 |   }, null, { timeout: 5_000 });
  144 | 
  145 |   await expect(page.locator('#info-card')).toHaveClass(/show/);
  146 |   await expect(page.locator('#info-card')).toContainText('102');
  147 |   await expect(page.locator('#info-card')).toContainText('八达岭');
  148 | });
  149 | 
  150 | test('E4 深度之最：榜单首行为八达岭 -102m，点击跨城直达信息卡', async ({ page }) => {
  151 |   await boot(page);
  152 | 
  153 |   await page.click('#btn-deeptop');
  154 |   await expect(page.locator('#deeptop-panel')).toHaveClass(/show/);
  155 | 
  156 |   const rows = page.locator('#deeptop-list .dt-row');
  157 |   expect(await rows.count(), '深度榜单至少 10 行').toBeGreaterThanOrEqual(10);
  158 |   await expect(rows.first()).toContainText('八达岭');
  159 |   await expect(rows.first()).toContainText('-102');
  160 | 
  161 |   await rows.first().click();
  162 | 
  163 |   await page.waitForTimeout(2_500);          // 跨城飞行 + 信息卡（实测 ~0.2s 内完成）
  164 |   expect(await selectedCityText(page)).toContain('京张');
  165 |   await expect(page.locator('#info-card')).toHaveClass(/show/);
  166 |   await expect(page.locator('#info-card')).toContainText('八达岭');
  167 | });
  168 | 
  169 | test('E5 星图：进入后 diag.nation=true，时间轴控件与总统计就位，URL 带 nation=1', async ({ page }) => {
  170 |   await boot(page);
  171 | 
  172 |   await page.click('#btn-nation');
  173 | 
  174 |   await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(true);
  175 |   await expect(page.locator('#nation-time')).toBeVisible();
  176 |   await expect(page.locator('#nt-stat')).toHaveText(/53 城 · 377 线 · 8180 站/);
  177 |   expect(page.url()).toContain('nation=1');
  178 | });
  179 | 
  180 | test('E6 星图时间轴：滑杆到 1971 / 2010 时统计按建成年份收缩', async ({ page }) => {
  181 |   await boot(page);
  182 |   await page.click('#btn-nation');
  183 |   await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(true);
  184 | 
  185 |   const setYear = (y) => page.locator('#nt-range').evaluate((el, year) => {
  186 |     const input = /** @type {HTMLInputElement} */ (el);
  187 |     input.value = String(year);
  188 |     input.dispatchEvent(new Event('input', { bubbles: true }));
  189 |   }, y);
  190 | 
  191 |   await setYear(1971);
  192 |   await expect(page.locator('#nt-stat')).toHaveText(/1 城 · 1 线 · 36 站/);
  193 | 
  194 |   await setYear(2010);
  195 |   await expect(page.locator('#nt-stat')).toHaveText(/17 城 · 67 线 · 1493 站/);
  196 | 
  197 |   await expect.poll(async () => (await diag(page)).nationYear, { timeout: 5_000 }).toBe(2010);
  198 | });
  199 | 
  200 | test('E7 星图俯冲：点击上海星点 → 退出星图并切到上海', async ({ page }) => {
  201 |   await boot(page);
  202 | 
  203 |   // 先切到北京：否则「上海」可能是启动默认值，断言就没有证明力
  204 |   await page.selectOption('#sel-city', 'beijing');
  205 |   await expect(page.locator('#stat-line')).toContainText('北京');
  206 | 
  207 |   await page.click('#btn-nation');
  208 |   await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(true);
  209 | 
  210 |   // 俯冲飞行结束后星点投影才落在视口内；等它稳定再点
  211 |   const point = await waitStableViewportPoint(page, 'shanghai');
  212 |   expect(point, '上海星点应稳定落在视口内（__nationScreen 返回有效坐标）').not.toBeNull();
  213 |   if (!point) return;
  214 | 
  215 |   await page.mouse.click(point[0], point[1]);
  216 | 
  217 |   await page.waitForTimeout(3_000);          // 俯冲 1.15s + 城市场景重建 + 开场扫入
  218 |   await page.waitForFunction(() => window.__diag().nation === false, null, { timeout: 7_000 });
  219 | 
> 220 |   expect(await selectedCityText(page)).toContain('上海');
      |                                        ^ Error: expect(received).toContain(expected) // indexOf
  221 | });
  222 | 
  223 | test('E8 Esc：星图内按 Esc 退回城市模式并收起时间轴', async ({ page }) => {
  224 |   await boot(page);
  225 | 
  226 |   await page.click('#btn-nation');
  227 |   await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(true);
  228 | 
  229 |   // 键盘处理器会跳过 INPUT/SELECT/TEXTAREA 目标，先让焦点回到 body
  230 |   await page.evaluate(() => { const a = document.activeElement; if (a && a.blur) a.blur(); });
  231 |   await page.keyboard.press('Escape');
  232 | 
  233 |   await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(false);
  234 |   await expect(page.locator('#nation-time')).toBeHidden();
  235 | });
  236 | 
  237 | test('E9 深链：?nation=1&year=1993 直达星图并自动播放生长史', async ({ page }) => {
  238 |   await boot(page, '?nation=1&year=1993');
  239 | 
  240 |   await page.waitForTimeout(8_000);          // 1971→2026 自动播放约 6s，留出余量
  241 | 
  242 |   expect((await diag(page)).nation, '深链应直接进入星图').toBe(true);
  243 |   await expect(page.locator('#nation-time'), '时间轴控件应显示').toBeVisible();
  244 | });
  245 | 
  246 | test('E10 渲染健康：城市模式下渲染帧持续增长且未被暂停', async ({ page }) => {
  247 |   await boot(page);
  248 | 
  249 |   const before = await diag(page);
  250 |   expect(before.paused, 'headless 前台页面不应处于暂停态').toBe(false);
  251 | 
  252 |   await page.waitForTimeout(3_000);
  253 |   const after = await diag(page);
  254 | 
  255 |   expect(after.renders, `渲染帧应从 ${before.renders} 继续增长`).toBeGreaterThan(before.renders);
  256 |   expect(after.paused).toBe(false);
  257 | });
  258 | 
  259 | test('E11 无静默崩溃：多步交互全程零 pageerror / console.error / __diag().errors', async ({ page, errors }) => {
  260 |   await boot(page);
  261 | 
  262 |   // 覆盖主要交互路径：切城 → 搜索 → 深度榜开合 → 星图进出
  263 |   await page.selectOption('#sel-city', 'chengdu');
  264 |   await expect(page.locator('#stat-line')).toContainText('成都');
  265 | 
  266 |   await page.fill('#st-search', '天府广场');
  267 |   await expect(page.locator('#search-drop .sr').first()).toBeAttached();
  268 | 
  269 |   await page.click('#btn-deeptop');
  270 |   await expect(page.locator('#deeptop-panel')).toHaveClass(/show/);
  271 |   await page.click('#dt-close');
  272 |   await expect(page.locator('#deeptop-panel')).not.toHaveClass(/show/);
  273 | 
  274 |   await page.click('#btn-nation');
  275 |   await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(true);
  276 |   await page.evaluate(() => { const a = document.activeElement; if (a && a.blur) a.blur(); });
  277 |   await page.keyboard.press('Escape');
  278 |   await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(false);
  279 | 
  280 |   expect(errors, '交互过程中不应出现任何错误').toEqual([]);
  281 |   expect((await diag(page)).errors, '__diag().errors 环形缓冲应为空').toEqual([]);
  282 | });
  283 | 
  284 | test('E12 移动端冒烟：引导可关闭、无横向溢出、全国星图可进入', async ({ page }) => {
  285 |   await boot(page);
  286 | 
  287 |   // 引导层已关闭（boot 里按「开始探索」关掉）
  288 |   await expect(page.locator('#tour-card')).not.toHaveClass(/show/);
  289 | 
  290 |   const overflow = () => page.evaluate(() => ({
  291 |     sw: document.documentElement.scrollWidth,
  292 |     bsw: document.body.scrollWidth,
  293 |     iw: window.innerWidth,
  294 |   }));
  295 | 
  296 |   let m = await overflow();
  297 |   expect(m.sw, `document.scrollWidth ${m.sw} 不应超过视口 ${m.iw}`).toBeLessThanOrEqual(m.iw + 2);
  298 |   expect(Math.max(m.sw, m.bsw)).toBeLessThanOrEqual(m.iw + 2);
  299 | 
  300 |   // 移动端「视图」面板默认收起，展开后 #btn-nation 才可点（应用既有设计）
  301 |   if (!(await page.locator('#btn-nation').isVisible())) {
  302 |     await page.click('#btn-ctrl-toggle');
  303 |   }
  304 |   await expect(page.locator('#btn-nation')).toBeVisible();
  305 | 
  306 |   m = await overflow();
  307 |   expect(Math.max(m.sw, m.bsw), '展开控制面板后仍不应横向溢出').toBeLessThanOrEqual(m.iw + 2);
  308 | 
  309 |   await page.click('#btn-nation');
  310 |   await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(true);
  311 |   await expect(page.locator('#nation-time')).toBeVisible();
  312 | });
```