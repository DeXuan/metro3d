# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— HTML/资源结构体检
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

检查项：重复 id / JS 孤儿引用 / 未定义 CSS 变量 / 必需 meta / PWA 资源 /
版本徽章与 CHANGELOG 同步 / 无障碍（按钮标签、reduced-motion）。
有问题以非零码退出（CI 用）。
"""
import io, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
issues = []

h = io.open(HTML, encoding='utf-8').read()
a = re.findall(r'<script type="module">(.*?)</script>', h, re.S)[1]

# ---- 1. 重复 id ----
ids = re.findall(r'id="([^"]+)"', h)
dup = [k for k, v in collections.Counter(ids).items() if v > 1]
if dup: issues.append(f'重复 id: {dup}')

# ---- 2. JS 孤儿引用 ----
refs = set(re.findall(r"\$\('([\w-]+)'\)", a)) | set(re.findall(r'getElementById\([\'"]([\w-]+)[\'"]\)', a))
dynamic = {'tomb-card','tc-name','tc-era','tc-chips','tc-intro','tc-close','tomb-canvas','perf-toast',
           'train-card','tcn-line','tcn-name','tcn-dir','tcn-seg','tcn-pos','tcn-fill','tcn-close'}
orph = sorted(r for r in refs if r not in set(ids) and r not in dynamic)
if orph: issues.append(f'JS 孤儿引用: {orph}')

# ---- 3. CSS 变量 ----
defined = set(re.findall(r'--([\w-]+)\s*:', h))
used = set(re.findall(r'var\(--([\w-]+)[,)]', h))
miss = sorted(u for u in used if u not in defined)
if miss: issues.append(f'未定义 CSS 变量: {miss}')

# ---- 4. 必需 meta ----
for key, pat in {
    'og:title': r'property="og:title"', 'og:image(绝对)': r'property="og:image"\s+content="https?://',
    'og:url': r'property="og:url"', 'twitter:card': r'name="twitter:card"',
    'theme-color': r'name="theme-color"', 'manifest': r'rel="manifest"', 'favicon': r'rel="icon"',
    'html lang': r'<html[^>]+lang=',
}.items():
    if not re.search(pat, h): issues.append(f'缺 meta: {key}')

# ---- 5. PWA 资源 ----
for f in ['manifest.json', 'sw.js', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/icon-maskable-512.png']:
    if not os.path.exists(os.path.join(ROOT, f)): issues.append(f'缺 PWA 资源: {f}')
mf = io.open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8').read()
if 'maskable' not in mf: issues.append('manifest 缺 maskable 图标')

# ---- 6. 版本徽章 vs CHANGELOG ----
cl = io.open(os.path.join(ROOT, 'CHANGELOG.md'), encoding='utf-8').read()
mv = re.search(r'^## \[(\d+\.\d+\.\d+)\]', cl, re.M)
mb = re.search(r'id="app-ver"[^>]*>([^<]+)<', h)
if mv and mb and mb.group(1) != 'v' + mv.group(1):
    issues.append(f"版本徽章 {mb.group(1)} ≠ CHANGELOG v{mv.group(1)}（运行 python data/build.py 同步）")

# ---- 7. 无障碍 ----
if 'prefers-reduced-motion' not in h: issues.append('未支持 prefers-reduced-motion')
icon_only = []
for m in re.finditer(r'<button([^>]*)>([^<]*)</button>', h):
    attrs, text = m.group(1), m.group(2).strip()
    sym_only = bool(text) and not re.search(r'[0-9A-Za-z一-鿿]', text)
    if len(text) <= 2 and sym_only and 'title=' not in attrs and 'aria-label=' not in attrs:
        icon_only.append(text)
if icon_only: issues.append(f'图标按钮缺 aria-label: {icon_only}')

print(f'[check_html] index.html {os.path.getsize(HTML)//1024} KB · 检查项 7 类')
if issues:
    print('发现问题 %d 处：' % len(issues))
    for i in issues: print('  -', i)
    sys.exit(1)
print('未发现问题 ✓')