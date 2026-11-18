/**
 * V1–V4 视觉回归（v2.4.0）
 *
 * 设计取舍：3D WebGL 跨平台像素差异巨大，PNG 字节哈希/逐像素 diff 会在 CI 假阳性。
 * 这里做「语义级视觉断言」：把页面截图回传浏览器、用 createImageBitmap 解码后统计颜色多样性，
 * 判断「画布确实渲染出内容 + 两种主题下星图都可见」——能抓住「整屏空白/全白/全黑」这类真实回归，
 * 又不受软件渲染的抗锯齿差异影响。
 */
const { test, expect } = require('playwright/test');

const URL = process.env.BASE || undefined;

async function boot(page, query = '') {
  await page.goto(query, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => {
    const el = document.getElementById('loading');
    return typeof window.__diag === 'function' && el && el.classList.contains('hide');
  }, null, { timeout: 25_000 });
  const welcome = page.getByRole('button', { name: /开始探索/ });
  if (await welcome.count()) { try { await welcome.first().click({ timeout: 4_000 }); } catch {} }
}

/** 截图 → 回传浏览器解码 → 统计颜色多样性与平均亮度 */
async function screenDiversity(page, clip) {
  const buf = await page.screenshot(clip ? { clip } : undefined);
  const b64 = buf.toString('base64');
  return page.evaluate(async (b64) => {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    const bmp = await createImageBitmap(new Blob([bytes], { type: 'image/png' }));
    const cv = document.createElement('canvas');
    cv.width = 120; cv.height = 75;
    const ctx = cv.getContext('2d');
    ctx.drawImage(bmp, 0, 0, cv.width, cv.height);
    const d = ctx.getImageData(0, 0, cv.width, cv.height).data;
    const colors = new Set();
    let lum = 0, n = 0;
    for (let i = 0; i < d.length; i += 4) {
      colors.add(`${d[i] >> 4},${d[i+1] >> 4},${d[i+2] >> 4}`);
      lum += d[i] * 0.299 + d[i+1] * 0.587 + d[i+2] * 0.114;
      n++;
    }
    bmp.close && bmp.close();
    return { uniqueColors: colors.size, avgLum: lum / n };
  }, b64);
}

// 只采样画布中部区域，避免被 UI 面板颜色主导统计
const CENTER_CLIP = { x: 320, y: 150, width: 800, height: 560 };

test('V1 城市模式渲染健康：画布有内容且控制区可见', async ({ page }) => {
  await boot(page);
  await page.waitForTimeout(1500);
  const div = await screenDiversity(page, CENTER_CLIP);
  expect(div.uniqueColors, '城市模式画布应有颜色多样性（不是空图）').toBeGreaterThan(10);
  await expect(page.locator('#panel-title')).toBeVisible();
  await expect(page.locator('#sel-city')).toBeVisible();
  await expect(page.locator('#btn-nation')).toBeVisible();
});

test('V2 星图暗色主题：可见、有内容、时间轴就位', async ({ page }) => {
  await boot(page, (URL || '') + '?nation=1');
  await page.waitForTimeout(2500);
  expect(await page.evaluate(() => window.__diag().nation)).toBe(true);
  const div = await screenDiversity(page, CENTER_CLIP);
  expect(div.uniqueColors, '星图画布应有颜色多样性').toBeGreaterThan(8);
  await expect(page.locator('#nation-time')).toBeVisible();
  await expect(page.locator('#nt-stat')).toContainText(/城 ·/);
});

test('V3 星图浅色主题：光晕不失效（颜色多样性保持）', async ({ page }) => {
  await boot(page, (URL || '') + '?nation=1');
  await page.waitForTimeout(2000);
  await page.evaluate(() => { const b = document.getElementById('btn-theme'); if (b) b.click(); });
  await page.waitForTimeout(1200);
  const div = await screenDiversity(page, CENTER_CLIP);
  expect(div.uniqueColors, '浅色主题星图仍应有内容（光晕失效时颜色多样性骤降）').toBeGreaterThan(8);
  expect(await page.evaluate(() => window.__diag().nation)).toBe(true);
  await expect(page.locator('#nation-time')).toBeVisible();
});

test('V4 移动端星图：全图适配且底部控件不被时间轴遮挡', async ({ page }) => {
  await boot(page, (URL || '') + '?nation=1');
  await page.waitForTimeout(2500);
  expect(await page.evaluate(() => window.__diag().nation)).toBe(true);
  const inView = await page.evaluate(() => {
    return ['shanghai', 'beijing', 'chengdu', 'wulumuqi'].map(id => {
      const p = window.__nationScreen(id);
      return p && p[0] >= 0 && p[0] <= innerWidth && p[1] >= 0 && p[1] <= innerHeight;
    });
  });
  expect(inView.every(Boolean), '移动端 4 个代表城市都应在视口内').toBe(true);
  const overlap = await page.evaluate(() => {
    const t = document.getElementById('nation-time').getBoundingClientRect();
    return ['btn-ctrl-toggle', 'btn-list-toggle'].map(id => {
      const el = document.getElementById(id);
      if (!el || getComputedStyle(el).display === 'none') return false;
      const r = el.getBoundingClientRect();
      return !(r.right < t.left || r.left > t.right || r.bottom < t.top || r.top > t.bottom);
    }).some(Boolean);
  });
  expect(overlap, '移动端时间轴不应遮挡底部浮钮').toBe(false);
});
