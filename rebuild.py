# -*- coding: utf-8 -*-
"""从损坏文件抢救 lib 块 + 重建完整 HTML 骨架 + 注入新 app/数据，生成最终 index.html"""
import io, json, re

# 1) 从损坏文件提取 lib 模块脚本（第一个 module script 完整块）
damaged = io.open('index.html', encoding='utf-8').read()
lib_start = damaged.index('<script type="module">')
lib_end = damaged.index('</script>', lib_start) + len('</script>')
lib_block = damaged[lib_start:lib_end]
assert 'window.OrbitControls' in lib_block and 'window.THREE' in lib_block
print('lib recovered:', len(lib_block), 'chars')

# 2) 提取 head（到 </style> 为止，损坏文件中 head 完整）
head_end = damaged.index('</style>') + len('</style>')
head = damaged[:head_end]
assert 'lg-chip-btn' in head  # extra_css 已包含
print('head recovered:', len(head), 'chars')

# 3) 新 app 脚本（数据已注入的模板）
json_data = json.load(open('data/sh_lines.json', encoding='utf-8'))
metro = {'cities': [{'id': 'shanghai', 'name': '上海', 'lines': json_data}]}
blob = json.dumps(metro, ensure_ascii=False, separators=(',', ':'))
app_tpl = io.open('data/app_template.js', encoding='utf-8').read()
app = app_tpl.replace('__METRO_DATA__', blob)
assert '__METRO_DATA__' not in app

# 4) 全新 body 骨架（与原设计一致：面板/列表/信息卡/提示/加载）
body = open('data/body_skeleton.html', encoding='utf-8').read()

out = head + '\n</head>\n' + body + '\n\n' + lib_block + '\n\n<script type="module">' + app + '</script>\n</body>\n</html>'
io.open('index.html', 'w', encoding='utf-8').write(out)
print('final assembled:', len(out), 'bytes; loading present:', 'id="loading"' in out)