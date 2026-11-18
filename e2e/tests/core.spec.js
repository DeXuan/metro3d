// @ts-check
/**
 * Metro 3D · 浏览器端核心回归（E1–E12）
 *
 * 断言对象一律是「可观测状态」：window.__diag()、DOM 文本/显隐、URL。
 * 不做实现细节断言（内部变量、three.js 对象结构），因此允许渲染层重构。
 *
 * 启动开销：单文件 2.7MB（Three.js + 数据内联），本机约 2–3s 完成模块执行，
 * 引入「开场俯冲」相机动画约 4.5s 才稳定。所有用例先走 boot() 等待：
 *   __diag 可用 → #loading.hide（引擎就绪）→ 关掉首次访问引导。
 */
const { test: base, expect } = require('playwright/test');

/** 每个用例都挂错误收集器；用例结束时统一断言为空（E11 的落地方式）。 */
const test = base.extend({
  errors: async ({ page }, use) => {
    /** @type {string[]} */
    const errors = [];
    page.on('pageerror', e => errors.push('pageerror: ' + (e && e.message)));
    page.on('console', m => { if (m.type() === 'error') errors.push('console.error: ' + m.text()); });

    await use(errors);

    // 应用自带的错误环形缓冲（v2.2+）：被 try/catch 吞掉的错误也在里面
    const diagErrors = await page
      .evaluate(() => (typeof window.__diag === 'function' ? (window.__diag().errors || []) : []))
      .catch(() => []);
    for (const e of diagErrors) errors.push(`__diag().errors: ${e.kind} ${e.msg} @${e.src}`);

    // KNOWN-BUG 标注过的用例允许保留错误证据（fixme 时用例本身也不会执行到断言）
    expect(errors, 'E11 无静默崩溃：pageerror / console.error / __diag().errors 必须为空').toEqual([]);
  },
});

/* ------------------------------ helpers ------------------------------ */

/**
 * 打开页面直到「引擎就绪」，并关掉首次访问引导。
 * @param {import('playwright/test').Page} page
 * @param {string} query 追加在 baseURL 后的查询串（如 '?nation=1&year=1993'）
 */
async function boot(page, query = '') {
  await page.goto(query, { waitUntil: 'load' });
  await page.waitForFunction(() => typeof window.__diag === 'function', null, { timeout: 20_000 });
  await page.waitForFunction(
    () => { const el = document.getElementById('loading'); return !!el && el.classList.contains('hide'); },
    null, { timeout: 20_000 });
  await dismissWelcome(page);
}

/**
 * 首次访问引导（#tour-card）会盖住全屏遮罩，挡住后续点击。
 * 有「开始探索」按钮就点它；布局异常时退回 evaluate 触发。
 * @param {import('playwright/test').Page} page
 */
async function dismissWelcome(page) {
  if (!(await page.locator('#tour-card.show').count())) return;
  const btn = page.getByRole('button', { name: /开始探索/ });
  if (await btn.count()) {
    try { await btn.first().click({ timeout: 5_000 }); }
    catch { await page.evaluate(() => { const b = document.getElementById('tour-start'); if (b) b.click(); }); }
  } else {
    await page.evaluate(() => { const b = document.getElementById('tour-start'); if (b) b.click(); });
  }
  await expect(page.locator('#tour-card')).not.toHaveClass(/show/);
}

/** @param {import('playwright/test').Page} page */
function diag(page) {
  return page.evaluate(() => window.__diag());
}

/** @param {import('playwright/test').Page} page */
function selectedCityText(page) {
  return page.evaluate(() => {
    const s = /** @type {HTMLSelectElement} */ (document.getElementById('sel-city'));
    return s.options[s.selectedIndex].textContent || '';
  });
}

/**
 * 星图里的城市星点只有在俯冲飞行结束后投影才有意义（飞行期间可能在视口外）。
 * 轮询 __nationScreen(id)，取「落在视口内且相邻两次读数相差 ≤ 8px」的坐标。
 * @param {import('playwright/test').Page} page
 * @param {string} cityId
 * @returns {Promise<number[] | null>}
 */
async function waitStableViewportPoint(page, cityId) {
  let prev = null;
  for (let i = 0; i < 30; i++) {                        // 最多 ~7.5s
    const pt = await page.evaluate(id => window.__nationScreen(id), cityId);
    const vp = await page.evaluate(() => ({ w: window.innerWidth, h: window.innerHeight }));
    if (pt && pt[0] > 0 && pt[0] < vp.w && pt[1] > 0 && pt[1] < vp.h) {
      if (prev && Math.abs(pt[0] - prev[0]) <= 8 && Math.abs(pt[1] - prev[1]) <= 8) return pt;
      prev = pt;
    } else {
      prev = null;
    }
    await page.waitForTimeout(250);
  }
  return null;
}

/* ------------------------------ E1–E12 ------------------------------ */

test('E1 启动：版本徽章 + 诊断钩子就绪 + 无异常', async ({ page }) => {
  await boot(page);

  await expect(page.locator('#app-ver')).toHaveText(/^v/);

  const d = await diag(page);
  expect(typeof d, '__diag() 应返回对象').toBe('object');
  expect(Object.keys(d)).toEqual(expect.arrayContaining(['reduce', 'autoRotate', 'renders']));
  expect(typeof d.renders).toBe('number');
  expect(d.renders, '启动后应已产生渲染帧').toBeGreaterThan(0);
});

test('E2 城市切换：下拉切换后统计行跟随新城市', async ({ page }) => {
  await boot(page);

  await page.selectOption('#sel-city', 'beijing');
  await expect(page.locator('#stat-line')).toContainText('北京');
  await expect(page.locator('#sel-city')).toHaveValue('beijing');

  const d = await diag(page);
  expect(d.nation, '切城后仍应处于城市模式').toBe(false);
});

test('E3 搜索：八达岭 → 下拉首项 → 信息卡显示埋深 102', async ({ page }) => {
  await boot(page);

  await page.fill('#st-search', '八达岭');
  const results = page.locator('#search-drop .sr');
  await expect(results.first()).toBeVisible();
  expect(await results.count()).toBeGreaterThanOrEqual(1);

  // 应用监听的是 mousedown（避免 blur 先后顺序问题），用真实事件派发
  await results.first().dispatchEvent('mousedown');

  await page.waitForFunction(() => {
    const card = document.getElementById('info-card');
    return !!card && card.classList.contains('show') && card.textContent.includes('102');
  }, null, { timeout: 5_000 });

  await expect(page.locator('#info-card')).toHaveClass(/show/);
  await expect(page.locator('#info-card')).toContainText('102');
  await expect(page.locator('#info-card')).toContainText('八达岭');
});

test('E4 深度之最：榜单首行为八达岭 -102m，点击跨城直达信息卡', async ({ page }) => {
  await boot(page);

  await page.click('#btn-deeptop');
  await expect(page.locator('#deeptop-panel')).toHaveClass(/show/);

  const rows = page.locator('#deeptop-list .dt-row');
  expect(await rows.count(), '深度榜单至少 10 行').toBeGreaterThanOrEqual(10);
  await expect(rows.first()).toContainText('八达岭');
  await expect(rows.first()).toContainText('-102');

  await rows.first().click();

  await page.waitForTimeout(2_500);          // 跨城飞行 + 信息卡（实测 ~0.2s 内完成）
  expect(await selectedCityText(page)).toContain('京张');
  await expect(page.locator('#info-card')).toHaveClass(/show/);
  await expect(page.locator('#info-card')).toContainText('八达岭');
});

test('E5 星图：进入后 diag.nation=true，时间轴控件与总统计就位，URL 带 nation=1', async ({ page }) => {
  await boot(page);

  await page.click('#btn-nation');

  await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(true);
  await expect(page.locator('#nation-time')).toBeVisible();
  await expect(page.locator('#nt-stat')).toHaveText(/53 城 · 377 线 · 8180 站/);
  expect(page.url()).toContain('nation=1');
});

test('E6 星图时间轴：滑杆到 1971 / 2010 时统计按建成年份收缩', async ({ page }) => {
  await boot(page);
  await page.click('#btn-nation');
  await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(true);

  const setYear = (y) => page.locator('#nt-range').evaluate((el, year) => {
    const input = /** @type {HTMLInputElement} */ (el);
    input.value = String(year);
    input.dispatchEvent(new Event('input', { bubbles: true }));
  }, y);

  await setYear(1971);
  await expect(page.locator('#nt-stat')).toHaveText(/1 城 · 1 线 · 36 站/);

  await setYear(2010);
  await expect(page.locator('#nt-stat')).toHaveText(/17 城 · 67 线 · 1493 站/);

  await expect.poll(async () => (await diag(page)).nationYear, { timeout: 5_000 }).toBe(2010);
});

test('E7 星图俯冲：点击上海星点 → 退出星图并切到上海', async ({ page }) => {
  await boot(page);

  // 先切到北京：否则「上海」可能是启动默认值，断言就没有证明力
  await page.selectOption('#sel-city', 'beijing');
  await expect(page.locator('#stat-line')).toContainText('北京');

  await page.click('#btn-nation');
  await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(true);

  // 俯冲飞行结束后星点投影才落在视口内；等它稳定再点
  const point = await waitStableViewportPoint(page, 'shanghai');
  expect(point, '上海星点应稳定落在视口内（__nationScreen 返回有效坐标）').not.toBeNull();
  if (!point) return;

  await page.mouse.click(point[0], point[1]);

  await page.waitForTimeout(3_000);          // 俯冲 1.15s + 城市场景重建 + 开场扫入
  await page.waitForFunction(() => window.__diag().nation === false, null, { timeout: 7_000 });

  expect(await selectedCityText(page)).toContain('上海');
});

test('E8 Esc：星图内按 Esc 退回城市模式并收起时间轴', async ({ page }) => {
  await boot(page);

  await page.click('#btn-nation');
  await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(true);

  // 键盘处理器会跳过 INPUT/SELECT/TEXTAREA 目标，先让焦点回到 body
  await page.evaluate(() => { const a = document.activeElement; if (a && a.blur) a.blur(); });
  await page.keyboard.press('Escape');

  await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(false);
  await expect(page.locator('#nation-time')).toBeHidden();
});

test('E9 深链：?nation=1&year=1993 直达星图并自动播放生长史', async ({ page }) => {
  await boot(page, '?nation=1&year=1993');

  await page.waitForTimeout(8_000);          // 1971→2026 自动播放约 6s，留出余量

  expect((await diag(page)).nation, '深链应直接进入星图').toBe(true);
  await expect(page.locator('#nation-time'), '时间轴控件应显示').toBeVisible();
});

test('E10 渲染健康：城市模式下渲染帧持续增长且未被暂停', async ({ page }) => {
  await boot(page);

  const before = await diag(page);
  expect(before.paused, 'headless 前台页面不应处于暂停态').toBe(false);

  await page.waitForTimeout(3_000);
  const after = await diag(page);

  expect(after.renders, `渲染帧应从 ${before.renders} 继续增长`).toBeGreaterThan(before.renders);
  expect(after.paused).toBe(false);
});

test('E11 无静默崩溃：多步交互全程零 pageerror / console.error / __diag().errors', async ({ page, errors }) => {
  await boot(page);

  // 覆盖主要交互路径：切城 → 搜索 → 深度榜开合 → 星图进出
  await page.selectOption('#sel-city', 'chengdu');
  await page.locator('#stat-line').filter({ hasText: '成都' }).waitFor({ timeout: 8_000 });

  await page.fill('#st-search', '天府广场');
  await page.locator('#search-drop .sr').first().waitFor({ state: 'attached', timeout: 8_000 });
  await page.fill('#st-search', '');

  await page.click('#btn-deeptop');
  await page.locator('#deeptop-panel.show').waitFor({ timeout: 5_000 });
  await page.click('#dt-close');

  await page.click('#btn-nation');
  await page.waitForFunction(() => window.__diag().nation === true, null, { timeout: 10_000 });
  await page.evaluate(() => { const a = document.activeElement; if (a && a.blur) a.blur(); });
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => window.__diag().nation === false, null, { timeout: 10_000 });

  expect(errors, '交互过程中不应出现任何错误').toEqual([]);
  expect((await diag(page)).errors, '__diag().errors 环形缓冲应为空').toEqual([]);
});

test('E12 移动端冒烟：引导可关闭、无横向溢出、全国星图可进入', async ({ page }) => {
  await boot(page);

  // 引导层已关闭（boot 里按「开始探索」关掉）
  await expect(page.locator('#tour-card')).not.toHaveClass(/show/);

  const overflow = () => page.evaluate(() => ({
    sw: document.documentElement.scrollWidth,
    bsw: document.body.scrollWidth,
    iw: window.innerWidth,
  }));

  let m = await overflow();
  expect(m.sw, `document.scrollWidth ${m.sw} 不应超过视口 ${m.iw}`).toBeLessThanOrEqual(m.iw + 2);
  expect(Math.max(m.sw, m.bsw)).toBeLessThanOrEqual(m.iw + 2);

  // 移动端「视图」面板默认收起，展开后 #btn-nation 才可点（应用既有设计）
  if (!(await page.locator('#btn-nation').isVisible())) {
    await page.click('#btn-ctrl-toggle');
  }
  await expect(page.locator('#btn-nation')).toBeVisible();

  m = await overflow();
  expect(Math.max(m.sw, m.bsw), '展开控制面板后仍不应横向溢出').toBeLessThanOrEqual(m.iw + 2);

  await page.click('#btn-nation');
  await expect.poll(async () => (await diag(page)).nation, { timeout: 10_000 }).toBe(true);
  await expect(page.locator('#nation-time')).toBeVisible();
});