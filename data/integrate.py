# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

免责声明：本脚本生成的数据仅供可视化演示与学习参考，禁止用于工程、施工、
测绘、导航或军事等专业用途。生成的埋深为示意值（非实测数据）。
详见 README「数据精度与使用限制」。

把 sh_lines.json 集成进 index.html：替换 METRO_DATA，并升级为多线路渲染版本。
"""
import io, json, re

JSON_PATH = 'sh_lines.json'
HTML_PATH = '../index.html'

data = json.load(open(JSON_PATH, encoding='utf-8'))
metro = {'cities': [{'id': 'shanghai', 'name': '上海', 'lines': data}]}
blob = json.dumps(metro, ensure_ascii=False, separators=(',', ':'))

html = io.open(HTML_PATH, encoding='utf-8').read()
app = re.findall(r'<script type="module">(.*?)</script>', html, re.S)[1]

# ============ 1) 替换 METRO_DATA ============
pat = re.compile(r"const METRO_DATA = \{.*?\n\};", re.S)
m = pat.search(app)
assert m, 'METRO_DATA block not found'
app = app[:m.start()] + 'const METRO_DATA = ' + blob + ';' + app[m.end():]

# ============ 2) 替换「锚点 + 全线路」构建逻辑 ============
old_render_block = """  /* — 管线（tube）+ 深度顶点色 — */"""
# 定位原「锚点构建」段：从 `// 投影原点 = 线路质心` 到 `/* — 管线` 之前
anchor_pat = re.compile(r"  // 投影原点 = 线路质心.*?/* — 管线", re.S)
# 保留：改写成每条线独立原点
assert anchor_pat.search(app), 'anchor block not found'
# 我们直接在 module 顶层替换 rebuildWorld 整体 —— 改为用锚点方式重构
print('anchor block found, size', len(anchor_pat.search(app).group(0)))

io.open('_stage1.js', 'w', encoding='utf-8').write(app)
print('METRO_DATA replaced, app size', len(app))