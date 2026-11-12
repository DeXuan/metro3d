# -*- coding: utf-8 -*-
"""组装最终 index.html：lib(three内联) + 新多线路 app + 数据注入 + 新增 CSS"""
import io, json, re

json_data = json.load(open('sh_lines.json', encoding='utf-8'))
metro = {'cities': [{'id': 'shanghai', 'name': '上海', 'lines': json_data}]}
blob = json.dumps(metro, ensure_ascii=False, separators=(',', ':'))

html = io.open('../index.html', encoding='utf-8').read()
app_tpl = io.open('app_template.js', encoding='utf-8').read()

# 1) 抽取 lib 模块脚本（第一个 module script）
m = re.search(r'(<script type="module">.*?</script>)\n', html, re.S)
assert m, 'lib block not found'
lib_block = m.group(1)

# 2) 定位应用脚本块并替换
app_pat = re.compile(r'<script type="module">.*?</script>\n</body>', re.S)
assert app_pat.search(html), 'app block not found'

app = app_tpl.replace('__METRO_DATA__', blob)

# 3) 新增 CSS
extra_css = """
  /* ---------- 多线路图例 ---------- */
  .lg-grid{ display:flex; flex-wrap:wrap; gap:5px; margin-top:6px; }
  .lg-chip-btn{
    display:flex; align-items:center; gap:5px; background:rgba(20,40,66,.6);
    border:1px solid var(--panel-border); border-radius:12px; padding:3px 8px;
    color:var(--text-dim); font-size:10.5px; cursor:pointer; transition:all .15s;
  }
  .lg-chip-btn:hover{ color:var(--text); border-color:rgba(110,190,255,.5); }
  .lg-chip-btn i{ width:12px; height:5px; border-radius:3px; }
  .lg-chip-btn.active{ background:rgba(79,194,232,.18); color:var(--accent); border-color:rgba(79,194,232,.55); }

  /* ---------- 站点列表分组 ---------- */
  .grp-head{
    display:flex; align-items:center; gap:8px; width:100%; margin-top:4px;
    background:rgba(20,40,66,.45); border:0; border-radius:8px; padding:7px 8px;
    color:var(--text); font-size:12px; cursor:pointer; font-family:inherit; text-align:left;
  }
  .grp-head:hover{ background:rgba(79,194,232,.12); }
  .grp-head i{ width:14px; height:6px; border-radius:3px; flex:none; }
  .grp-head b{ color:var(--text-dim); font-weight:400; font-size:10.5px; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .grp-head::after{ content:'▶'; margin-left:auto; font-size:9px; color:var(--text-dim); transition:transform .2s; }
  .grp-head.open::after{ transform:rotate(90deg); }
  .grp-body{ padding-left:6px; }
"""
html = html.replace('</style>', extra_css + '</style>', 1)

# 4) 组装输出
out = html[:m.start()] + lib_block + '\n\n<script type="module">' + app + '</script>\n</body>\n</html>'
io.open('../index.html', 'w', encoding='utf-8').write(out)
print('assembled, total size', len(out))

# 语法检查辅助
scripts = re.findall(r'<script type="module">(.*?)</script>', out, re.S)
for i, s in enumerate(scripts):
    io.open('_chk%d.mjs' % i, 'w', encoding='utf-8').write(s)
print('scripts:', len(scripts))