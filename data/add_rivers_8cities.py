# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

补齐 8 城水系（此前清理错误数据时被整体移除的城市）：
大连湾 / 汾河 / 京杭大运河(常州) / 故黄河(徐州) / 青弋江 / 浙东运河(绍兴) / 义乌江 / 清流河
河道中心线为公开地图级示意值；过河区间依据公开报道与站间坐标推断。
"""
import io, json

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}

def densify(points, step=0.005):
    out = [points[0]]
    for a, b in zip(points, points[1:]):
        dd = ((b[0]-a[0])**2 + (b[1]-a[1])**2) ** 0.5
        n = max(1, int(dd/step))
        for i in range(1, n + 1):
            t = i / n
            out.append([round(a[0] + (b[0]-a[0])*t, 6), round(a[1] + (b[1]-a[1])*t, 6)])
    return out

RIVERS = {
 'dalian': {   # 5 号线梭鱼湾南—大连站下穿大连湾（2023 年开通的海底隧道段）
   'name': '大连湾', 'widthM': 1500, 'startWidthM': 1800, 'endWidthM': 2500,
   'points': [[121.600, 38.948], [121.645, 38.946], [121.680, 38.950], [121.720, 38.960], [121.760, 38.972]],
   'crossings': [{'line': '5号线', 'from': '梭鱼湾南', 'to': '大连站', 'label': '5号线越大连湾（海底隧道）'}],
 },
 'taiyuan': {  # 汾河自北向南穿城，1 号线太原理工大学—桃园路下穿
   'name': '汾河', 'widthM': 300, 'startWidthM': 280, 'endWidthM': 380,
   'points': [[112.548, 37.920], [112.545, 37.890], [112.540, 37.870], [112.536, 37.858], [112.532, 37.830], [112.528, 37.800], [112.524, 37.770], [112.520, 37.745]],
   'crossings': [{'line': '1号线', 'from': '太原理工大学', 'to': '桃园路', 'label': '1号线越汾河（隧道）'}],
 },
 'changzhou': {  # 京杭大运河东西向，1 号线文化宫—同济桥过河
   'name': '京杭大运河', 'widthM': 150, 'startWidthM': 160, 'endWidthM': 180,
   'points': [[119.885, 31.806], [119.905, 31.798], [119.925, 31.789], [119.945, 31.780], [119.965, 31.774], [119.990, 31.766], [120.020, 31.757], [120.050, 31.752]],
   'crossings': [{'line': '1号线', 'from': '文化宫', 'to': '同济桥', 'label': '1号线越京杭运河（隧道）'}],
 },
 'xuzhou': {   # 故黄河南北向穿城，1 号线民主北路—徐州火车站过河
   'name': '故黄河', 'widthM': 120, 'startWidthM': 130, 'endWidthM': 150,
   'points': [[117.185, 34.320], [117.188, 34.295], [117.190, 34.275], [117.193, 34.262], [117.197, 34.240], [117.203, 34.215], [117.210, 34.190]],
   'crossings': [{'line': '1号线', 'from': '民主北路', 'to': '徐州火车站', 'label': '1号线越故黄河（隧道）'}],
 },
 'wuhu': {     # 青弋江自西向东汇入长江，1 号线（单轨高架）鸠兹广场—环城北路过河
   'name': '青弋江', 'widthM': 180, 'startWidthM': 200, 'endWidthM': 260,
   'points': [[118.365, 31.328], [118.385, 31.326], [118.410, 31.320], [118.440, 31.312], [118.470, 31.305]],
   'crossings': [{'line': '1号线', 'from': '鸠兹广场', 'to': '环城北路', 'label': '1号线越青弋江（桥梁）'}],
 },
 'shaoxing': { # 浙东运河（杭甬运河）东西向，1 号线火车站—城市广场过河
   'name': '浙东运河', 'widthM': 120, 'startWidthM': 130, 'endWidthM': 150,
   'points': [[120.400, 30.095], [120.450, 30.070], [120.500, 30.045], [120.545, 30.025], [120.582, 30.010], [120.620, 29.998], [120.670, 29.988]],
   'crossings': [{'line': '1号线', 'from': '火车站', 'to': '城市广场', 'label': '1号线越浙东运河（隧道）'}],
 },
 'jinhua': {   # 义乌江（东阳江）沿金义走廊，作为地理参考（无跨河区间）
   'name': '义乌江', 'widthM': 150, 'startWidthM': 160, 'endWidthM': 200,
   'points': [[119.640, 29.092], [119.700, 29.110], [119.760, 29.150], [119.820, 29.190], [119.900, 29.240], [119.980, 29.280], [120.050, 29.308], [120.120, 29.325], [120.200, 29.295]],
   'crossings': [],
 },
 'chuzhou': {  # 清流河东西向穿城北，宁滁线大王郢—苏滁商务中心过河
   'name': '清流河', 'widthM': 130, 'startWidthM': 140, 'endWidthM': 180,
   'points': [[118.300, 32.300], [118.350, 32.295], [118.400, 32.288], [118.470, 32.270], [118.520, 32.262]],
   'crossings': [{'line': '宁滁线', 'from': '大王郢', 'to': '苏滁商务中心', 'label': '宁滁线越清流河（桥梁）'}],
 },
}

COLORS = {'color': 1728394, 'edgeColor': 5875928, 'centerColor': 10477823}
n = 0
for cid, r in RIVERS.items():
    c = by.get(cid)
    assert c, f'{cid} not found'
    c['river'] = {
      'name': r['name'],
      'points': densify(r['points']),
      'widthM': r['widthM'], 'startWidthM': r['startWidthM'], 'endWidthM': r['endWidthM'],
      **COLORS,
      'crossings': r['crossings'],
    }
    n += 1

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('补齐水系城市:', n)
print('水系覆盖:', sum(1 for c in d['cities'] if c.get('river')), '/', len(d['cities']))
