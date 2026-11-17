# -*- coding: utf-8 -*-
"""香港坐标精确化：OSM Overpass 数据 → 匹配 → 更新（先出报告，不直接写）"""
import io, json, math

osm = json.load(open('hk_osm.json', encoding='utf-8'))
d = json.load(open('data/metro_all.json', encoding='utf-8'))
hk = next(c for c in d['cities'] if c['id'] == 'xianggang')

# 繁→简（覆盖港铁站名用字）
T2S = str.maketrans('環灣匯綫調景嶺觀塘將軍澳油塘坑口寶琳坑尾門恆安馬鞍山烏溪沙大圍車公廟顯徑紅磡旺角東奧運南昌荔景欣澳東涌迪士尼陰澳機場博覽館錦上路元朗朗屏天水圍屯門兆康柴灣杏花邨筲箕灣太古側魚涌北角炮台山上環金鐘中環香港九龍塘石硖尾深水埗長沙灣荔枝角美孚葵興葵芳荃灣大窩口佐敦油麻地何文田樂富黃大仙鑽石山彩虹九龍灣牛頭角藍田將軍澳綫西門罩裙涌綫北角調',
                    '环湾汇线调景岭观塘将军澳油塘坑口宝琳坑尾门恒安马鞍山乌溪沙大围车公庙显径红磡旺角东奥运南昌荔景欣澳东涌迪士尼阴澳机场博览馆锦上路元朗朗屏天水围屯门兆康柴湾杏花村筲箕湾太古侧鱼涌北角炮台山上环金钟中环香港九龙塘石硖尾深水埗长沙湾荔枝角美孚葵兴葵芳荃湾大窝口佐敦油麻地何文田乐富黄大仙钻石山彩虹九龙湾牛头角蓝田将军澳线西门罩裙涌线北角调')
def s2s(name): return name.translate(T2S)

# OSM 索引
nodes = []
for e in osm.get('elements', []):
    t = e.get('tags', {})
    nm = t.get('name', '')
    if nm:
        nodes.append({'name': s2s(nm), 'lat': e['lat'], 'lon': e['lon'], 'en': t.get('name:en', '')})

def dist(a, b):
    return math.hypot((a[0]-b[0])*111320*math.cos(math.radians((a[1]+b[1])/2)), (a[1]-b[1])*110540)

# 匹配：同名且距旧坐标 < 2.5km
report, matched, missed = [], 0, []
for l in hk['lines']:
    for s in l['stations']:
        cand = [n for n in nodes if n['name'] == s['name']]
        if not cand:
            missed.append((l['name'], s['name'], 'OSM 无同名'))
            continue
        cand.sort(key=lambda n: dist((s['lng'], s['lat']), (n['lon'], n['lat'])))
        best = cand[0]
        dd = dist((s['lng'], s['lat']), (best['lon'], best['lat']))
        if dd > 2500:
            missed.append((l['name'], s['name'], f'最近同名 {dd:.0f}m 超阈值'))
            continue
        matched += 1
        report.append(f"{l['name']:6s} {s['name']:6s} 旧({s['lng']:.4f},{s['lat']:.4f}) -> 新({best['lon']:.5f},{best['lat']:.5f}) d={dd:.0f}m")

print(f'匹配成功: {matched} / 总站: {sum(len(l["stations"]) for l in hk["lines"])}')
print('未匹配:')
for m in missed: print('  -', m)
print('样例前 12 条:')
for r in report[:12]: print('  ', r)