# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

洛阳高铁轨迹：郑西高铁（徐兰客运专线郑州—西安段，2010 年开通）。
走行为公开地图级示意值——东自偃师方向入境，经洛阳龙门站（与地铁 2 号线
换乘），向西经宜阳北、新安方向出境；全程行经洛河以南、龙门山前台地。
"""
import io, json

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}
ly = by['luoyang']

def densify(points, step=0.006):
    out = [points[0]]
    for a, b in zip(points, points[1:]):
        dd = ((b[0]-a[0])**2 + (b[1]-a[1])**2) ** 0.5
        n = max(1, int(dd/step))
        for i in range(1, n + 1):
            t = i / n
            out.append([round(a[0] + (b[0]-a[0])*t, 6), round(a[1] + (b[1]-a[1])*t, 6)])
    return out

ly['railways'] = [{
  'name': '郑西高铁',
  'desc': '徐兰客运专线 · 2010 年开通 · 时速 350km/h',
  'type': 'hsr',
  'color': '#E8ECF2',
  'year': 2010,
  'points': densify([
    [112.78, 34.655], [112.70, 34.638], [112.62, 34.618], [112.55, 34.600],
    [112.50, 34.593], [112.463, 34.590], [112.42, 34.588], [112.36, 34.592],
    [112.29, 34.610], [112.21, 34.648],
  ]),
  'stations': [
    {'name': '洛阳龙门', 'lng': 112.463, 'lat': 34.590, 'note': '↔ 地铁2号线 龙门高铁站'},
  ],
}]

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('郑西高铁已写入：', len(ly['railways'][0]['points']), '个加密点')
