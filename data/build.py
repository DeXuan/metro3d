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
APP_JS = os.path.join(ROOT, 'src', 'app.js')
APP_MARK = '/*__APP_INLINE__*/'
APP_BEGIN = '/*__APP_BEGIN__*/'
APP_END = '/*__APP_END__*/'

def write_html(text):
    """统一以 LF 写出 index.html——本地/CI/服务器三端 md5 一致（OTA 校验基础）"""
    io.open(HTML, 'w', encoding='utf-8', newline='\n').write(text)

OTA_URL_DEFAULT = 'https://dexuan.github.io/metro3d/ota-manifest.js'

def load_blob():
    d = json.load(open(DATA, encoding='utf-8'))
    return json.dumps(d, ensure_ascii=False, separators=(',', ':'))

def load_app():
    """业务 JS 源文件（v2.2.0 起外置，构建时内联回单文件交付）"""
    return io.open(APP_JS, encoding='utf-8').read()

def inline_app():
    """把 src/app.js 整段回填到 index.html 的标记区（幂等：每次全量替换）

    标记协议（首次拆分后 index.html 内保留）：
        /*__APP_BEGIN__*/  ...构建时被 src/app.js 整体替换...  /*__APP_END__*/
    源码是唯一事实源，产物不会与源码漂移。
    """
    h = io.open(HTML, encoding='utf-8').read()
    app = load_app().strip("\n")
    if APP_BEGIN in h and APP_END in h:
        i0 = h.index(APP_BEGIN) + len(APP_BEGIN)
        i1 = h.index(APP_END, i0)
        h2 = h[:i0] + "\n" + app + "\n" + h[i1:]
    elif APP_MARK in h:
        h2 = h.replace(APP_MARK, "\n" + APP_BEGIN + "\n" + app + "\n" + APP_END + "\n", 1)
    else:
        return h                      # 未拆分形态（历史版本）
    if h2 != h:
        write_html(h2)
    return h2

def check_app(h=None):
    """校验 src/app.js 与 index.html 内联结果逐字节一致（标记协议）"""
    h = h or io.open(HTML, encoding='utf-8').read()
    if APP_BEGIN not in h or APP_END not in h:
        if APP_MARK in h:
            print('[build] index.html 仍是哨兵态——请运行 python data/build.py')
            return False
        return True                    # 未拆分形态
    i0 = h.index(APP_BEGIN) + len(APP_BEGIN)
    i1 = h.index(APP_END, i0)
    # 归一化：占位符注入 + 去除每行行尾空白与整体边缘空白
    # （跨平台写读可能带入行尾空格/CR，JS 语义无关，避免误报）
    def norm(t):
        t = apply_placeholders(t)
        return '\n'.join(line.rstrip() for line in t.split('\n')).strip()
    embedded = norm(h[i0:i1])
    app = norm(load_app())
    if embedded != app:
        print('[build] src/app.js 与 index.html 内联内容不一致（%d vs %d 字符）——请运行 python data/build.py'
              % (len(embedded), len(app)))
        return False
    return True

def inline(blob):
    h = io.open(HTML, encoding='utf-8').read()
    i0 = h.index('const METRO_DATA = ')
    i1 = h.index(';\n', h.index('"cities"', i0))
    write_html(h[:i0] + 'const METRO_DATA = ' + blob + h[i1:])

def check(blob):
    h = io.open(HTML, encoding='utf-8').read()
    i0 = h.index('const METRO_DATA = ')
    i1 = h.index(';\n', h.index('"cities"', i0))
    inline_blob = h[i0 + len('const METRO_DATA = '):i1]
    if inline_blob != blob:
        print('[build] 数据不一致：index.html 内联数据与 data/metro_all.json 不同步')
        print('        请运行: python data/build.py')
        return False
    if '__APP_VER__' in h:
        print('[build] 占位符 __APP_VER__ 未替换——请运行 python data/build.py')
        ok = False
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
        write_html(h2)
        print('[build] 版本徽章同步为 v' + ver)

def apply_placeholders(text, ver=None):
    """构建期占位符注入：__APP_VER__ / __OTA_URL__（幂等）"""
    if ver is None:
        cl = io.open(os.path.join(ROOT, 'CHANGELOG.md'), encoding='utf-8').read()
        m = re.search(r'^## \[(\d+\.\d+\.\d+)\]', cl, re.M)
        ver = ('v' + m.group(1)) if m else 'v0.0.0'
    elif not ver.startswith('v'):
        ver = 'v' + ver
    ota = os.environ.get('METRO3D_OTA_URL', OTA_URL_DEFAULT)
    # ver 需带 v 前缀；正则整词替换兼容 v__APP_VER__ / __APP_VER__ 两种写法
    return re.sub(r'v?__APP_VER__', ver, text).replace('__OTA_URL__', ota)

def sync_ota():
    """生成 OTA 发布清单：version.json（节点脚本用）+ ota-manifest.js（页面端用）"""
    import hashlib
    from datetime import date
    cl = io.open(os.path.join(ROOT, 'CHANGELOG.md'), encoding='utf-8').read()
    m = re.search(r'^## \[(\d+\.\d+\.\d+)\] — (\d{4}-\d{2}-\d{2})', cl, re.M)
    ver = 'v' + m.group(1) if m else 'v0.0.0'
    released = m.group(2) if m else date.today().isoformat()
    h = io.open(HTML, encoding='utf-8').read()
    h = apply_placeholders(h, ver)
    write_html(h)
    md5 = hashlib.md5(h.encode('utf-8')).hexdigest()
    size_kb = len(h.encode('utf-8')) // 1024
    data = {'version': ver, 'released': released, 'hash': md5,
            'pagesUrl': 'https://dexuan.github.io/metro3d/', 'sizeKb': size_kb}
    io.open(os.path.join(ROOT, 'version.json'), 'w', encoding='utf-8').write(
        json.dumps(data, ensure_ascii=False, indent=2))
    io.open(os.path.join(ROOT, 'ota-manifest.js'), 'w', encoding='utf-8').write(
        '/* metro3d OTA 清单 —— 由 data/build.py 自动生成，勿手改 */\n'
        'window.__OTA_MANIFEST = ' + json.dumps(data, ensure_ascii=False) + ';\n')
    print('[build] OTA 清单已生成：%s · md5 %s…' % (ver, md5[:10]))

if __name__ == '__main__':
    blob = load_blob()
    if '--check' in sys.argv:
        ok_app = check_app()
        sys.exit(0 if (check(blob) and ok_app) else 1)
    # v2.2.0：先回填业务 JS（src/app.js），再内联数据，最后同步徽章
    inline_app()
    inline(blob)
    sync_version()
    sync_ota()
    ok = check(blob) and check_app()
    print('[build] 数据已内联 (%d KB) + 业务 JS src/app.js 已内联；语法校验: %s'
          % (len(blob) // 1024, '通过' if ok else '失败'))
    sys.exit(0 if ok else 1)
