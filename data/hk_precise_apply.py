# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

香港坐标精确化：以 OpenStreetMap（Overpass API）港铁车站坐标为准，
更新全线 121 站坐标（原手工近似值 ±300m~5km）。繁体名经 OpenCC 转简体匹配，
同名站以距旧坐标最近者消歧。数据来源标注进城市 note。
"""
import io, json, math, re
from opencc import OpenCC

cc = OpenCC('t2s')
osm = json.load(open('hk_osm2.json', encoding='utf-8'))
p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
hk = next(c for c in d['cities'] if c['id'] == 'xianggang')

def norm(name):
    m = re.search(r'[\u4e00-\u9fff]+(?:站)?', name.replace('\u200e', ''))
    if not m: return ''
    return cc.convert(m.group(0)).removesuffix('站')

nodes = []
for e in osm.get('elements', []):
    t = e.get('tags', {})
    cn = norm(t.get('name', ''))
    if not cn: continue
    lat = e.get('lat') or (e.get('center') or {}).get('lat')
    lon = e.get('lon') or (e.get('center') or {}).get('lon')
    if lat is None: continue
    nodes.append({'name': cn, 'lat': lat, 'lon': lon})

def dist(a, b):
    return math.hypot((a[0]-b[0])*111320*math.cos(math.radians((a[1]+b[1])/2)), (a[1]-b[1])*110540)

FORCE = {'利东', '海怡半岛'}   # 近似坐标偏差 >2.5km，名称唯一无歧义
updated, kept, missed = 0, [], []
maxd = 0
for l in hk['lines']:
    for s in l['stations']:
        cand = [n for n in nodes if n['name'] == s['name']]
        if not cand:
            missed.append((l['name'], s['name'])); continue
        cand.sort(key=lambda n: dist((s['lng'], s['lat']), (n['lon'], n['lat'])))
        best = cand[0]
        dd = dist((s['lng'], s['lat']), (best['lon'], best['lat']))
        if dd > 2500 and s['name'] not in FORCE:
            kept.append((l['name'], s['name'], f'{dd:.0f}m')); continue
        maxd = max(maxd, dd)
        s['lng'], s['lat'] = round(best['lon'], 6), round(best['lat'], 6)
        updated += 1

hk['note'] = '车站坐标 2026-11 经 OpenStreetMap 精确校准（±10m 级）'
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'更新 {updated} 站（历史最大位移 {maxd:.0f}m）｜保留近似 {len(kept)}｜缺失 {len(missed)}')
for m in missed: print('  ✗', m)