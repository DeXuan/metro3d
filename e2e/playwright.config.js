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
  // 单文件应用（Three.js + 数据内联 ≈2.7MB）每个 page 都是一次全量解析 + WebGL 初始化。
  // 并行上下文会互相抢 CPU 反而更慢，串行跑总耗时更低也更稳定。
  workers: 1,
  fullyParallel: false,
  reporter: 'list',
  // 期望断言默认 5s；WebGL 页面在 CI 上主线程很忙，给到 8s 降低偶发抖动
  expect: { timeout: 8_000 },
  use: {
    baseURL: process.env.BASE || LOCAL_INDEX,
    locale: 'zh-CN',
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