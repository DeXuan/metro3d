# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

城市文化 POI：龙门石窟（grotto 类型）/ 静安寺 / 灵隐寺（landmarks）、
玄武湖 / 西湖 / 伊河（lakes 湖泊多边形）、中山陵 / 明孝陵（南京 tombs）。
坐标为公开资料级示意值。
"""
import io, json, math

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}

def ellipse(cx, cy, ra, rb, n=10):
    return [[round(cx + ra * math.cos(2 * math.pi * k / n), 6),
             round(cy + rb * math.sin(2 * math.pi * k / n), 6)] for k in range(n)]

# ---------- 洛阳：龙门石窟（grotto）+ 伊河 ----------
ly = by['luoyang']
ly.setdefault('landmarks', []).append({
    'name': '龙门石窟', 'lng': 112.472, 'lat': 34.556, 'h': 60,
    'type': 'grotto', 'color': '#c9a86a',
    'desc': '世界文化遗产 · 北魏至唐造像 10 万余尊'})
ly['lakes'] = [{
    'name': '伊河', 'desc': '龙门山前',
    'points': [[112.474, 34.542], [112.481, 34.542], [112.485, 34.561],
               [112.481, 34.578], [112.474, 34.578], [112.470, 34.561]],
}]

# ---------- 上海：静安寺（金顶） ----------
by['shanghai'].setdefault('landmarks', []).append({
    'name': '静安寺', 'lng': 121.445, 'lat': 31.223, 'h': 36,
    'type': 'pagoda', 'color': '#E8B44A',
    'desc': '静安寺 · 金顶 · 2/7 号线'})

# ---------- 南京：玄武湖 + 中山陵 / 明孝陵 ----------
nj = by['nanjing']
nj['lakes'] = [{
    'name': '玄武湖', 'desc': '江南城内湖 · 皇家园林',
    'points': ellipse(118.807, 32.075, 0.016, 0.010, 10),
}]
nj['tombs'] = {
  'name': '钟山陵墓群',
  'desc': '中山陵 · 明孝陵（世界文化遗产）',
  'intro': '紫金山（钟山）南麓集中山陵、明孝陵、灵谷寺于一体，为"民国建筑与明代皇家陵寝"的叠加区。明孝陵 2003 年列入世界文化遗产，中山陵为中国近代建筑史上第一陵。',
  'items': [
    {'name': '中山陵 · 孙中山', 'era': '民国 · 1929 年奉安', 'role': '名人',
     'lng': 118.847, 'lat': 32.063, 'moundD': 325, 'moundH': 73, 'kind': 'mausoleum',
     'level': '全国重点文物保护单位',
     'intro': '孙中山先生陵寝。1926 年动工、1929 年奉安，祭堂与墓室沿紫金山南坡逐级抬升，392 级台阶寓意当时三亿九千二百万国民。平面呈"自由钟"形，建筑师吕彦直设计，为中国近代建筑史上第一陵。'},
    {'name': '明孝陵 · 明太祖朱元璋', 'era': '明 · 公元 1398 年', 'role': '帝王',
     'lng': 118.838, 'lat': 32.055, 'moundD': 90, 'moundH': 25,
     'level': '世界文化遗产 · 全国重点文物保护单位',
     'intro': '明太祖朱元璋与马皇后合葬陵寝，"明清皇家第一陵"。首创"前朝后寝"格局，神道石像生依山势蜿蜒曲折，2003 年列入世界文化遗产（明清皇家陵寝），其规制为明十三陵所沿用。宝顶之下即地宫。'},
  ],
}

# ---------- 杭州：西湖 + 灵隐寺 ----------
hz = by['hangzhou']
hz['lakes'] = [{
    'name': '西湖', 'desc': '世界文化遗产 · 三面云山一面城',
    'points': ellipse(120.143, 30.248, 0.011, 0.0095, 10),
}]
hz.setdefault('landmarks', []).append({
    'name': '灵隐寺', 'lng': 120.097, 'lat': 30.241, 'h': 28,
    'type': 'pavilion', 'color': '#d8b878',
    'desc': '东晋古刹 · 飞来峰'})

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('POI 已写入：龙门石窟+伊河 / 静安寺 / 玄武湖+中山陵+明孝陵 / 西湖+灵隐寺')
