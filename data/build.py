# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 构建脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

把 data/metro_all.json 内联进 index.html（唯一运行产物），并做语法自检。

用法：
  python data/build.py            # 重新内联数据到 index.html
  python data/build.py --check    # 校验：内联数据与 JSON 一致 + JS 语法通过（CI 用）
"""
import io, json, re, subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
DATA = os.path.join(ROOT, 'data', 'metro_all.json')

def load_blob():
    d = json.load(open(DATA, encoding='utf-8'))
    return json.dumps(d, ensure_ascii=False, separators=(',', ':'))

def inline(blob):
    h = io.open(HTML, encoding='utf-8').read()
    i0 = h.index('const METRO_DATA = ')
    i1 = h.index(';\n', h.index('"cities"', i0))
    io.open(HTML, 'w', encoding='utf-8').write(h[:i0] + 'const METRO_DATA = ' + blob + h[i1:])

def check(blob):
    h = io.open(HTML, encoding='utf-8').read()
    i0 = h.index('const METRO_DATA = ')
    i1 = h.index(';\n', h.index('"cities"', i0))
    inline_blob = h[i0 + len('const METRO_DATA = '):i1]
    if inline_blob != blob:
        print('[build] 数据不一致：index.html 内联数据与 data/metro_all.json 不同步')
        print('        请运行: python data/build.py')
        return False
    mods = re.findall(r'<script type="module">(.*?)</script>', h, re.S)
    ok = True
    for k, s in enumerate(mods):
        tmp = os.path.join(ROOT, f'_ci_check_{k}.mjs')
        io.open(tmp, 'w', encoding='utf-8').write(s)
        r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
        os.remove(tmp)
        if r.returncode != 0:
            print(f'[build] 模块脚本 {k} 语法错误:\n{r.stderr[:600]}')
            ok = False
    return ok

def sync_version():
    """从 CHANGELOG 最新版本号同步页脚版本徽章（发版流程自动，不再手改）"""
    cl = io.open(os.path.join(ROOT, 'CHANGELOG.md'), encoding='utf-8').read()
    m = re.search(r'^## \[(\d+\.\d+\.\d+)\]', cl, re.M)
    if not m: return
    ver = m.group(1)
    h = io.open(HTML, encoding='utf-8').read()
    h2 = re.sub(r'(id="app-ver"[^>]*>)[^<]*(</b>)', r'\g<1>v' + ver + r'\g<2>', h)
    if h2 != h:
        io.open(HTML, 'w', encoding='utf-8').write(h2)
        print('[build] 版本徽章同步为 v' + ver)

if __name__ == '__main__':
    blob = load_blob()
    if '--check' in sys.argv:
        sys.exit(0 if check(blob) else 1)
    inline(blob)
    sync_version()
    ok = check(blob)
    print('[build] 数据已内联 (%d KB)；语法校验: %s' % (len(blob) // 1024, '通过' if ok else '失败'))
    sys.exit(0 if ok else 1)
