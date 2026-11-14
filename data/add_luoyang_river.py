# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

补齐洛阳市洛河水系（此前清理错误数据时被整体移除）。
河道中心线为示意值（公开地图级精度），2 号线"牡丹桥—文博园"区间
为公开报道的下穿洛河隧道段（2021 年贯通，首条下穿洛河地铁隧道）。
"""
import io, json

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}
ly = by.get('luoyang')
assert ly, 'luoyang city not found'

def densify(points, step=0.005):
    out = [points[0]]
    for a, b in zip(points, points[1:]):
        dd = ((b[0]-a[0])**2 + (b[1]-a[1])**2) ** 0.5
        n = max(1, int(dd/step))
        for i in range(1, n + 1):
            t = i / n
            out.append([round(a[0] + (b[0]-a[0])*t, 6), round(a[1] + (b[1]-a[1])*t, 6)])
    return out

# 洛河：自西向东横贯洛阳市区南部，2 号线牡丹桥—文博园区间下穿（≈34.652N）
ly['river'] = {
  'name': '洛河',
  'points': densify([
    [112.330, 34.672], [112.365, 34.665], [112.395, 34.658], [112.420, 34.654],
    [112.443, 34.652], [112.468, 34.645], [112.492, 34.635], [112.518, 34.624],
    [112.545, 34.612], [112.580, 34.607], [112.605, 34.606],
  ]),
  'widthM': 350, 'startWidthM': 300, 'endWidthM': 450,
  'color': 1728394, 'edgeColor': 5875928, 'centerColor': 10477823,
  'crossings': [
    {'line': '2号线', 'from': '牡丹桥', 'to': '文博园', 'label': '2号线越洛河（隧道）'},
  ],
}

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('洛河水系已写入：', len(ly['river']['points']), '个加密点')
