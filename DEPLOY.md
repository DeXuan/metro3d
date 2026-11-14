# 部署说明

本项目是**单文件静态站点**，任何静态托管都能部署。

## 一、最简单：直接用浏览器打开

双击 `index.html` 即可。完全离线，无外部请求。

## 二、本地服务器

```bash
python -m http.server 8000
# http://localhost:8000/
```

## 三、静态托管平台

把 `index.html` 上传即可：

- **GitHub Pages**：仓库 Settings → Pages → 选择分支根目录
- **Cloudflare Pages / Vercel / Netlify**：直接拖入或连 Git 仓库
- **对象存储（OSS/COS/S3）**：上传后开启静态网站托管
- **自建 Nginx**：见下方配置

## 四、自建 Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.example.com;

    root /var/www/metro3d;
    index index.html;

    charset utf-8;
    gzip on;
    gzip_types text/html;

    # 安全头
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header Referrer-Policy strict-origin-when-cross-origin;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

**性能提示**：`index.html` 原始 2.3MB，gzip 后约 490KB。务必开启 gzip 或 brotli。

## 五、一键部署脚本

```bash
# Linux / macOS / Git Bash
export DEPLOY_HOST=user@server.example.com
export DEPLOY_DIR=/var/www/metro3d
export PUBLIC_URL=https://your-domain.example.com/
./deploy.sh
```

```bat
REM Windows CMD
set DEPLOY_HOST=user@server.example.com
set DEPLOY_DIR=/var/www/metro3d
deploy.bat
```

脚本会：创建目录 → 备份远端旧版 → 上传 → 校验。

## 六、缓存策略

`index.html` 内容随版本变化，建议：

```nginx
location = /index.html {
    add_header Cache-Control "no-cache";
}
```

对 `poster/`、`docs/` 等静态资源可设长缓存。

## 常见问题

| 现象 | 处理 |
|---|---|
| 页面空白 | 检查浏览器控制台；确认 WebGL 可用；确认 gzip 未损坏文件 |
| 中文乱码 | 确保 HTTP 响应头 `Content-Type: text/html; charset=utf-8` |
| 加载慢 | 开启 gzip/brotli（体积可降至 ~490KB） |
| 移动端卡顿 | 降低「垂直夸张」或关闭「站点标注」 |


## 可选：隐私友好访问统计

本项目默认**零追踪**。如需了解访问量，推荐自托管 [umami](https://umami.is/)（开源、无 Cookie、GDPR 友好）：

1. 在服务器上以 Docker 运行 umami，接入任意数据库
2. 在 umami 后台创建网站，获得 `website-id`
3. 在 `index.html` 的 `</head>` 前加入：

```html
<script async defer data-website-id="你的ID" src="https://统计域名/umami.js"></script>
```

> 注意：这会引入一个外部请求，与"零外部依赖"卖点有取舍。建议仅在自建域名版本启用，GitHub Pages 版保持纯净。
