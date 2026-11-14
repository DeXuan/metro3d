#!/usr/bin/env bash
# ============================================================
# 一键部署（静态托管）
# 用法：
#   DEPLOY_HOST=user@your-server DEPLOY_DIR=/var/www/yoursite ./deploy.sh
# 或复制 .env.example 为 .env 并填写后 source .env
# 说明：上传前自动备份远端旧版
# ============================================================
set -euo pipefail

HOST="${DEPLOY_HOST:?请设置 DEPLOY_HOST（如 user@server.example.com）}"
REMOTE_DIR="${DEPLOY_DIR:?请设置 DEPLOY_DIR（如 /var/www/metro3d）}"
PUBLIC_URL="${PUBLIC_URL:-}"
LOCAL_FILE="index.html"

if [[ ! -f "$LOCAL_FILE" ]]; then
  echo "[错误] 找不到 $LOCAL_FILE，请在本项目目录下执行" >&2
  exit 1
fi

echo "==> [1/3] 确保远端目录存在"
ssh "$HOST" "mkdir -p $REMOTE_DIR"

echo "==> [2/3] 备份远端旧版"
ssh "$HOST" "cp -f $REMOTE_DIR/index.html $REMOTE_DIR/index.html.bak-\$(date +%Y%m%d-%H%M%S) 2>/dev/null || true"

echo "==> [3/3] 上传 index.html ($(du -h $LOCAL_FILE | cut -f1)) + PWA 资源"
scp "$LOCAL_FILE" "$HOST:$REMOTE_DIR/"
scp manifest.json sw.js "$HOST:$REMOTE_DIR/" 2>/dev/null || true
ssh "$HOST" "mkdir -p $REMOTE_DIR/icons"
scp icons/icon-192.png icons/icon-512.png "$HOST:$REMOTE_DIR/icons/" 2>/dev/null || true

echo "✅ 部署完成"
if [[ -n "$PUBLIC_URL" ]]; then
  echo "   访问地址: $PUBLIC_URL"
  ssh "$HOST" "curl -skI '$PUBLIC_URL' | head -1 || true"
fi
