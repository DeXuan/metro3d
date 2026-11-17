# -*- coding: utf-8 -*-
"""香港坐标精确化 v2：OpenCC 繁简转换 + 中文名提取 + 距离消歧（报告模式）"""
import io, json, math, re
from opencc import OpenCC

cc = OpenCC('t2s')
osm = json.load(open('hk_osm2.json', encoding='utf-8'))
d = json.load(open('data/metro_all.json', encoding='utf-8'))
hk = next(c for c in d['cities'] if c['id'] == 'xianggang')

def norm(name):
    """OSM name → 简体中文名（提取第一段连续汉字，去尾「站」）"""
    m = re.search(r'[\u4e00-\u9fff]+(?:站)?', name.replace('\u200e', ''))
    if not m: return ''
    return cc.convert(m.group(0)).removesuffix('站')

nodes = []
for e in osm.get('elements', []):
    t = e.get('tags', {})
    cn = norm(t.get('name', ''))
    if cn:
        lat = e.get('lat') or (e.get('center') or {}).get('lat')
        lon = e.get('lon') or (e.get('center') or {}).get('lon')
        if lat is None: continue
        nodes.append({'name': cn, 'lat': lat, 'lon': lon})

def dist(a, b):
    return math.hypot((a[0]-b[0])*111320*math.cos(math.radians((a[1]+b[1])/2)), (a[1]-b[1])*110540)

matched, missed = 0, []
for l in hk['lines']:
    for s in l['stations']:
        cand = [n for n in nodes if n['name'] == s['name']]
        if not cand:
            missed.append((l['name'], s['name'], '无同名'))
            continue
        cand.sort(key=lambda n: dist((s['lng'], s['lat']), (n['lon'], n['lat'])))
        best = cand[0]
        dd = dist((s['lng'], s['lat']), (best['lon'], best['lat']))
        if dd > 2500:
            missed.append((l['name'], s['name'], f'最近 {dd:.0f}m'))
            continue
        matched += 1
        print(f"  {l['name']:5s} {s['name']:6s} 旧({s['lng']:.4f},{s['lat']:.4f}) -> 新({best['lon']:.5f},{best['lat']:.5f}) d={dd:.0f}m")

total = sum(len(l['stations']) for l in hk['lines'])
print(f'\n匹配成功: {matched}/{total}  未匹配: {len(missed)}')
for m in missed: print('  ✗', m)