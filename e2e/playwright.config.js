// @ts-check
/**
 * Metro 3D · Playwright E2E 配置
 *
 * 默认 baseURL 指向仓库自带的 index.html（file:// 协议，离线可跑，无需服务器）。
 * 覆盖为线上站点：
 *   BASE=https://xn--888-vw3e05fxyzc07e.cn:9006/web/metro3d/ npx playwright test
 *
 * locale 固定 zh-CN：用例断言使用中文 UI 文案（城市名 / 按钮 / 统计串），
 * 而应用会按 navigator.language 切换 UI 语言。
 */
const path = require('path');
const { pathToFileURL } = require('url');
const { defineConfig } = require('playwright/test');

const LOCAL_INDEX = pathToFileURL(path.resolve(__dirname, '..', 'index.html')).href;

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: process.env.BASE || LOCAL_INDEX,
    locale: 'zh-CN',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      // 桌面：E1–E11 核心用例
      name: 'chromium',
      grepInvert: /E12/,
      use: { browserName: 'chromium', viewport: { width: 1440, height: 900 } },
    },
    {
      // 移动端：仅 E12 冒烟（Chromium 内核 + 移动视口）
      name: 'mobile',
      grep: /E12/,
      use: {
        browserName: 'chromium',
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
        deviceScaleFactor: 3,
      },
    },
  ],
});