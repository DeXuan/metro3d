# metro3d 节点 OTA 一键更新（Windows PowerShell 版）
# 用法：
#   .\deploy-ota.bat                         单次检查（有更新时交互确认）
#   .\deploy-ota.bat --yes                   直接部署
#   .\deploy-ota.bat --watch --interval 30   常驻轮询
#   .\deploy-ota.bat --deploy-dir D:\site   目标目录
#   .\deploy-ota.bat --notify "powershell -c ..."   通知钩子（env: NEW_VERSION/RELEASED/HASH）
param(
  [switch]$Yes, [switch]$Watch, [int]$Interval = 30,
  [string]$Manifest = "https://dexuan.github.io/metro3d/version.json",
  [string]$DeployDir = ".", [string]$Notify = ""
)

function Log($m){ Write-Host ("[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) }
function VerNum($v){ return [int](($v -replace '[^0-9]', '') + '0') }

function Get-LocalVersion {
  $vj = Join-Path $DeployDir "version.json"
  if (Test-Path $vj) { return (Get-Content $vj -Raw | ConvertFrom-Json).version }
  $html = Join-Path $DeployDir "index.html"
  if (Test-Path $html) {
    $m = Select-String -Path $html -Pattern "const __APP_VERSION = '([^']+)'" | Select-Object -First 1
    if ($m) { return $m.Matches[0].Groups[1].Value }
  }
  return $null
}

function Invoke-Deploy($ver, $hash, $base) {
  $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("metro3d-ota-" + [guid]::NewGuid().ToString('N'))
  New-Item -ItemType Directory -Path $tmp -Force | Out-Null
  $files = @("index.html","version.json","ota-manifest.js","manifest.json","sw.js",
             "icons/icon-192.png","icons/icon-512.png","icons/icon-maskable-512.png")
  Log "下载 $ver ..."
  foreach ($f in $files) {
    $dst = Join-Path $tmp $f
    New-Item -ItemType Directory -Path (Split-Path $dst) -Force | Out-Null
    try { Invoke-WebRequest -Uri "$base/$f" -OutFile $dst -UseBasicParsing -TimeoutSec 90 }
    catch { Remove-Item $tmp -Recurse -Force; throw "下载失败: $base/$f" }
  }
  # 完整性校验
  $got = (Get-FileHash (Join-Path $tmp "index.html") -Algorithm MD5).Hash.ToLower()
  if ($got -ne $hash.ToLower()) {
    Remove-Item $tmp -Recurse -Force
    Write-Error "哈希校验失败 (期望 $($hash.Substring(0,12))... 实得 $($got.Substring(0,12))...)，拒绝部署"
    exit 2
  }
  Log "哈希校验通过 ($($hash.Substring(0,12))...)"
  # 备份 + 部署
  $idx = Join-Path $DeployDir "index.html"
  if (Test-Path $idx) {
    Copy-Item $idx (Join-Path $DeployDir ("index.html.bak-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))) -Force
  }
  foreach ($f in $files) {
    $dst = Join-Path $DeployDir $f
    New-Item -ItemType Directory -Path (Split-Path $dst) -Force | Out-Null
    Copy-Item (Join-Path $tmp $f) $dst -Force
  }
  Remove-Item $tmp -Recurse -Force
  Log "OK 部署完成: $ver -> $DeployDir"
}

function Check-Once {
  try { $mf = Invoke-RestMethod -Uri $Manifest -UseBasicParsing -TimeoutSec 30 }
  catch { Log "清单不可达：$Manifest（离线或地址错误）"; return }
  if (-not $mf.version -or -not $mf.hash -or -not $mf.pagesUrl) { Log "清单字段不完整，跳过"; return }
  $lver = Get-LocalVersion
  Log "本地 $(if($lver){$lver}else{'未知'}) · 远端 $($mf.version) ($($mf.released))"
  if ($lver -and (VerNum $mf.version) -le (VerNum $lver)) { Log "已是最新版本，无需更新"; return }
  Log "🆕 发现新版本: $(if($lver){$lver}else{'无'}) -> $($mf.version)"
  if ($Notify) {
    $env:NEW_VERSION = $mf.version; $env:RELEASED = $mf.released; $env:HASH = $mf.hash
    cmd /c $Notify
  }
  if ($Yes) { Invoke-Deploy $mf.version $mf.hash $mf.pagesUrl }
  else {
    $ans = Read-Host "是否立即部署 $($mf.version)? [y/N]"
    if ($ans -match '^[Yy]') { Invoke-Deploy $mf.version $mf.hash $mf.pagesUrl } else { Log "已跳过" }
  }
}

if ($Watch) {
  Log "OTA 守护启动：每 $Interval 分钟检查一次（Ctrl-C 退出）"
  while ($true) { Check-Once; Start-Sleep -Seconds ($Interval * 60) }
} else { Check-Once }