# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

免责声明：本脚本生成的数据仅供可视化演示与学习参考，禁止用于工程、施工、
测绘、导航或军事等专业用途。生成的埋深为示意值（非实测数据）。
详见 README「数据精度与使用限制」。

桥梁主题：数据注入 + 渲染实现（中国最高/最长跨江跨海跨山谷大桥）
"""
import io, re, json

HTML = 'index.html'
h = io.open(HTML, encoding='utf-8').read()

# ============ 1) 数据：桥梁城市 ============
bridges = {
  "id": "bridges", "name": "中国超级桥梁", "kind": "bridges",
  "bridges": [
    {"name": "港珠澳大桥", "en": "HZMB", "type": "cable", "cat": "跨海",
     "lenKm": 55, "mainSpanM": 458, "towerHm": 163, "year": 2018,
     "desc": "世界最长跨海大桥，桥岛隧集群工程", "color": "#00A6A6",
     "points": [[113.616,22.124],[113.700,22.190],[113.780,22.268],[113.900,22.286],[114.013,22.294]],
     "towers": [0.44,0.56], "towerH": 62, "deckH": 11, "width": 3.2},
    {"name": "深中通道", "en": "Shenzhen-Zhongshan Link", "type": "suspension", "cat": "跨海",
     "lenKm": 24, "mainSpanM": 1666, "towerHm": 270, "year": 2024,
     "desc": "世界最高海中悬索桥塔（270m），桥岛隧集群", "color": "#2E86DE",
     "points": [[113.630,22.550],[113.710,22.552],[113.790,22.550]],
     "towers": [0.38,0.62], "towerH": 74, "deckH": 13, "width": 3.0},
    {"name": "青岛胶州湾大桥", "en": "Jiaozhou Bay Bridge", "type": "cable", "cat": "跨海",
     "lenKm": 41.6, "mainSpanM": 260, "towerHm": 100, "year": 2011,
     "desc": "曾为世界最长跨海大桥", "color": "#E67E22",
     "points": [[120.130,36.020],[120.190,36.060],[120.255,36.093],[120.310,36.118],[120.380,36.140]],
     "towers": [0.32,0.52,0.72], "towerH": 40, "deckH": 9, "width": 3.0},
    {"name": "杭州湾跨海大桥", "en": "Hangzhou Bay Bridge", "type": "cable", "cat": "跨海",
     "lenKm": 36, "mainSpanM": 448, "towerHm": 187, "year": 2008,
     "desc": "首创海中平台，S 形曲线跨越杭州湾", "color": "#16A085",
     "points": [[121.140,30.280],[121.060,30.340],[120.980,30.395],[120.920,30.420]],
     "towers": [0.35,0.65], "towerH": 46, "deckH": 9, "width": 2.8},
    {"name": "平潭海峡公铁大桥", "en": "Pingtan Strait Bridge", "type": "cable", "cat": "跨海",
     "lenKm": 16.3, "mainSpanM": 532, "towerHm": 157, "year": 2020,
     "desc": "世界最长跨海公铁两用大桥，台风区建造", "color": "#8E44AD",
     "points": [[119.610,25.610],[119.680,25.575],[119.740,25.540],[119.790,25.500]],
     "towers": [0.4,0.6], "towerH": 34, "deckH": 10, "width": 2.4},
    {"name": "苏通大桥", "en": "Sutong Bridge", "type": "cable", "cat": "跨江",
     "lenKm": 8.2, "mainSpanM": 1088, "towerHm": 306, "year": 2008,
     "desc": "世界首座主跨超千米斜拉桥", "color": "#C0392B",
     "points": [[121.010,31.815],[120.998,31.795],[120.990,31.780]],
     "towers": [0.33,0.67], "towerH": 52, "deckH": 10, "width": 2.2},
    {"name": "五峰山长江大桥", "en": "Wufengshan Yangtze Bridge", "type": "suspension", "cat": "跨江",
     "lenKm": 6.4, "mainSpanM": 1092, "towerHm": 203, "year": 2021,
     "desc": "世界首座千米级公铁两用悬索桥", "color": "#D35400",
     "points": [[119.680,32.240],[119.700,32.255],[119.720,32.270]],
     "towers": [0.33,0.67], "towerH": 44, "deckH": 9, "width": 2.2},
    {"name": "南京长江大桥", "en": "Nanjing Yangtze River Bridge", "type": "truss", "cat": "跨江",
     "lenKm": 6.8, "mainSpanM": 160, "towerHm": 0, "year": 1968,
     "desc": "长江上第一座由中国自行设计建造的双层式公铁两用桥", "color": "#7F8C8D",
     "points": [[118.735,32.102],[118.740,32.110],[118.746,32.118]],
     "towers": [], "towerH": 18, "deckH": 8, "width": 2.0},
    {"name": "杨泗港长江大桥", "en": "Yangsigang Yangtze Bridge", "type": "suspension", "cat": "跨江",
     "lenKm": 4.1, "mainSpanM": 1700, "towerHm": 241, "year": 2019,
     "desc": "世界最大跨度双层公路悬索桥", "color": "#9B59B6",
     "points": [[114.268,30.535],[114.288,30.518],[114.305,30.505]],
     "towers": [0.32,0.68], "towerH": 40, "deckH": 9, "width": 2.2},
    {"name": "北盘江大桥", "en": "Beipanjiang Bridge", "type": "cable", "cat": "跨山谷",
     "lenKm": 1.34, "mainSpanM": 720, "towerHm": 269, "year": 2016,
     "desc": "世界最高桥：桥面距谷底 565 米", "color": "#27AE60", "valley": True, "valleyDepth": 60,
     "points": [[104.860,26.515],[104.875,26.525],[104.890,26.535]],
     "towers": [0.33,0.67], "towerH": 44, "deckH": 56, "width": 2.0},
    {"name": "矮寨大桥", "en": "Aizhai Bridge", "type": "suspension", "cat": "跨山谷",
     "lenKm": 1.18, "mainSpanM": 1176, "towerHm": 129, "year": 2012,
     "desc": "跨德夯大峡谷，桥面距谷底 355 米", "color": "#F39C12", "valley": True, "valleyDepth": 40,
     "points": [[109.595,28.325],[109.610,28.335],[109.625,28.345]],
     "towers": [0.32,0.68], "towerH": 34, "deckH": 36, "width": 2.0},
  ]
}

d = json.load(open('data/metro_all.json', encoding='utf-8'))
d['cities'] = [c for c in d['cities'] if c['id'] != 'bridges']
d['cities'].append(bridges)
json.dump(d, open('data/metro_all.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
blob = json.dumps(d, ensure_ascii=False, separators=(',', ':'))

app = re.findall(r'<script type="module">(.*?)</script>', h, re.S)[1]
i0 = app.index('const METRO_DATA = ')
i1 = app.index(';\n', app.index('"cities"', i0))
app = app[:i0] + 'const METRO_DATA = ' + blob + app[i1:]

# ============ 2) 城市下拉适配（桥梁城市无 lines） ============
old = """  selCity.innerHTML = METRO_DATA.cities.map(c => `<option value="${c.id}">${c.name}（${c.lines.length}条线路）</option>`).join('') +
    '<option disabled>更多城市 · 敬请期待</option>';"""
assert old in app
app = app.replace(old, """  selCity.innerHTML = METRO_DATA.cities.map(c => {
    const cnt = c.lines ? `${c.lines.length}条线路` : (c.bridges ? `${c.bridges.length}座大桥` : '');
    return `<option value="${c.id}">${c.name}（${cnt}）</option>`;
  }).join('') + '<option disabled>更多城市 · 敬请期待</option>';""")

# ============ 3) populateSelectors 线路下拉适配 ============
old2 = """  const opts = ['<option value="__all__">全部线路 · 网络总览</option>'];
  city.lines.forEach(l => {
    opts.push(`<option value="${lineObjKey(l)}">${l.name} · ${l.loop ? '环线' : l.from + '—' + l.to}</option>`);
  });"""
assert old2 in app
app = app.replace(old2, """  const opts = [];
  if (city.kind === 'bridges'){
    opts.push('<option value="__all__">全部大桥 · 全国总览</option>');
    city.bridges.forEach((b, i) => opts.push(`<option value="bridge-${i}">${b.name} · ${b.cat} ${b.lenKm}km</option>`));
  } else {
    opts.push('<option value="__all__">全部线路 · 网络总览</option>');
    city.lines.forEach(l => {
      opts.push(`<option value="${lineObjKey(l)}">${l.name} · ${l.loop ? '环线' : l.from + '—' + l.to}</option>`);
    });
  }""")

print('bridge data + selectors patched')
io.open('index.html', 'w', encoding='utf-8').write(
    h[:h.rindex('<script type="module">')] + '<script type="module">' + app + '</script>' +
    h[h.rindex('</script>') + len('</script>'):])
print('step 1 done')