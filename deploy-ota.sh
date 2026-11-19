#!/usr/bin/env bash
# ============================================================
# metro3d 节点 OTA 一键更新
# 拉取发布清单 → 比对本地版本 → 备份 → 下载 → MD5 校验 → 部署
#
# 用法：
#   ./deploy-ota.sh                                    单次检查（有更新时交互确认）
#   ./deploy-ota.sh --yes                              单次检查，直接部署（无人值守）
#   ./deploy-ota.sh --watch [--interval 30]            常驻轮询（默认每 30 分钟）
#   ./deploy-ota.sh --manifest <url>                   指定清单地址
#   ./deploy-ota.sh --deploy-dir <dir>                 目标目录（默认当前目录）
#   ./deploy-ota.sh --notify 'cmd'                     发现新版本时执行通知命令
#                                                      （env: NEW_VERSION RELEASED HASH）
#
# 依赖：curl、python3（解析 JSON 与计算 MD5）
# 退出码：0 成功/已最新；1 参数或运行错误；2 发现更新但校验失败（拒绝部署）
# ============================================================
set -uo pipefail

DEPLOY_DIR="${DEPLOY_DIR:-.}"
MANIFEST="${OTA_MANIFEST:-https://dexuan.github.io/metro3d/version.json}"
AUTO=0; WATCH=0; INTERVAL=30; NOTIFY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes|-y)        AUTO=1; shift;;
    --watch)         WATCH=1; shift;;
    --interval)      INTERVAL="${2:-30}"; shift 2;;
    --manifest)      MANIFEST="$2"; shift 2;;
    --deploy-dir)    DEPLOY_DIR="$2"; shift 2;;
    --notify)        NOTIFY="$2"; shift 2;;
    -h|--help)       sed -n '2,18p' "$0"; exit 0;;
    *) echo "[错误] 未知参数: $1" >&2; exit 1;;
  esac
done

log(){ echo "[$(date '+%F %T')] $*"; }
die(){ echo "[错误] $*" >&2; exit 1; }

command -v curl >/dev/null || die "需要 curl"
CURL_OPTS=(-sfL)
[[ "${METRO3D_NO_PROXY:-0}" == "1" ]] && CURL_OPTS+=(--noproxy '*')
command -v python3 >/dev/null || die "需要 python3"

jget(){ # jget <file> <key>
  python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get(sys.argv[2],""))' "$1" "$2"
}
local_version(){
  if [[ -f "$DEPLOY_DIR/version.json" ]]; then
    jget "$DEPLOY_DIR/version.json" version
  elif [[ -f "$DEPLOY_DIR/index.html" ]]; then
    grep -oE "const __APP_VERSION = '[^']+'" "$DEPLOY_DIR/index.html" | head -1 | sed "s/.*'\(.*\)'/\1/"
  else
    echo ""
  fi
}
ver_num(){ echo "$1" | tr -cd '0-9'; }   # v2.4.1 -> 241

download_and_deploy(){
  local ver="$1" hash="$2" base="$3"
  local tmp; tmp="$(mktemp -d)"
  log "下载 $ver 到临时目录…"
  local files=(index.html version.json ota-manifest.js manifest.json sw.js
               icons/icon-192.png icons/icon-512.png icons/icon-maskable-512.png)
  for f in "${files[@]}"; do
    mkdir -p "$tmp/$(dirname "$f")"
    curl "${CURL_OPTS[@]}" --max-time 90 "$base/$f" -o "$tmp/$f" || { rm -rf "$tmp"; die "下载失败: $base/$f"; }
  done
  # 完整性校验：下载的 index.html 必须与清单哈希一致
  local got
  got="$(python3 -c 'import hashlib,sys;print(hashlib.md5(open(sys.argv[1],"rb").read()).hexdigest())' "$tmp/index.html")"
  if [[ "$got" != "$hash" ]]; then
    rm -rf "$tmp"
    echo "[错误] 哈希校验失败（期望 ${hash:0:12}… 实得 ${got:0:12}…），拒绝部署" >&2
    exit 2
  fi
  log "哈希校验通过 (${hash:0:12}…)"
  # 备份 + 就地部署
  mkdir -p "$DEPLOY_DIR/icons"
  [[ -f "$DEPLOY_DIR/index.html" ]] && \
    cp -f "$DEPLOY_DIR/index.html" "$DEPLOY_DIR/index.html.bak-$(date +%Y%m%d-%H%M%S)"
  for f in "${files[@]}"; do
    mkdir -p "$DEPLOY_DIR/$(dirname "$f")"
    cp -f "$tmp/$f" "$DEPLOY_DIR/$f"
  done
  rm -rf "$tmp"
  log "✅ 部署完成：$ver → $DEPLOY_DIR"
}

check_once(){
  local mf; mf="$(mktemp)"
  if ! curl "${CURL_OPTS[@]}" --max-time 30 "$MANIFEST" -o "$mf"; then
    rm -f "$mf"; log "清单不可达：$MANIFEST（离线或地址错误）"; return 0
  fi
  local rver rhash rrel rbase
  rver="$(jget "$mf" version)"; rhash="$(jget "$mf" hash)"
  rrel="$(jget "$mf" released)";  rbase="$(jget "$mf" pagesUrl)"
  rm -f "$mf"
  [[ -n "$rver" && -n "$rhash" && -n "$rbase" ]] || { log "清单字段不完整，跳过"; return 0; }
  local lver; lver="$(local_version)"
  log "本地 ${lver:-未知} · 远端 $rver（$rrel）"
  if [[ -z "$lver" ]]; then
    log "本地无版本信息，按需部署最新版"
  elif (( $(ver_num "$rver") <= $(ver_num "$lver") )); then
    log "已是最新版本，无需更新"; return 0
  else
    log "🆕 发现新版本：$lver → $rver"
  fi
  if [[ -n "$NOTIFY" ]]; then
    NEW_VERSION="$rver" RELEASED="$rrel" HASH="$rhash" bash -c "$NOTIFY" || true
  fi
  if [[ $AUTO == 1 ]]; then
    download_and_deploy "$rver" "$rhash" "$rbase"
  else
    read -r -p "是否立即部署 $rver？[y/N] " ans
    [[ "$ans" =~ ^[Yy]$ ]] && download_and_deploy "$rver" "$rhash" "$rbase" || log "已跳过"
  fi
  return 0
}

if [[ $WATCH == 1 ]]; then
  trap 'log "OTA 守护进程退出"; exit 0' INT TERM
  log "OTA 守护启动：每 ${INTERVAL} 分钟检查一次（Ctrl-C 退出）"
  while true; do
    check_once || true
    sleep $((INTERVAL * 60))
  done
else
  check_once
fi