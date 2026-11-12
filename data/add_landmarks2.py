# -*- coding: utf-8 -*-
"""补齐 14 城地标 + 苏州水系"""
import json

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}

LANDMARKS = {
 'xianggang': [
   {'name': '环球贸易广场', 'lng': 114.1605, 'lat': 22.3033, 'h': 484, 'type': 'taper', 'color': '#9fc8e8', 'desc': 'ICC · 484m'},
   {'name': '国际金融中心二期', 'lng': 114.1590, 'lat': 22.2850, 'h': 415, 'type': 'taper', 'color': '#8fc4e8', 'desc': 'IFC · 415m'},
   {'name': '中银大厦', 'lng': 114.1610, 'lat': 22.2795, 'h': 367, 'type': 'taper', 'color': '#c8d8e8', 'desc': '贝聿铭设计'},
   {'name': '香港摩天轮', 'lng': 114.1680, 'lat': 22.2840, 'h': 60, 'type': 'wheel', 'color': '#e8a86a', 'desc': '中环海滨'},
 ],
 'taibei': [
   {'name': '台北101', 'lng': 121.5645, 'lat': 25.0339, 'h': 508, 'type': 'pagoda', 'color': '#8fc4e8', 'desc': '508m · 曾为世界第一高楼'},
   {'name': '台北小巨蛋', 'lng': 121.5530, 'lat': 25.0500, 'h': 45, 'type': 'pavilion', 'color': '#c8d8e8', 'desc': '多功能体育馆'},
 ],
 'tianjin': [
   {'name': '天津周大福金融中心', 'lng': 117.6900, 'lat': 39.0050, 'h': 530, 'type': 'taper', 'color': '#9fc8e8', 'desc': '530m · 天津第一高楼'},
   {'name': '天津之眼', 'lng': 117.1830, 'lat': 39.1520, 'h': 120, 'type': 'wheel', 'color': '#e86a9a', 'desc': '永乐桥摩天轮'},
   {'name': '天津劝业场', 'lng': 117.1980, 'lat': 39.1300, 'h': 30, 'type': 'ancient', 'color': '#d8b878', 'desc': '百年商厦'},
 ],
 'shenyang': [
   {'name': '沈阳茂业中心', 'lng': 123.4330, 'lat': 41.8080, 'h': 310, 'type': 'tower', 'color': '#9fc8e8', 'desc': '青年大街'},
   {'name': '沈阳故宫', 'lng': 123.4560, 'lat': 41.7960, 'h': 20, 'type': 'ancient', 'color': '#d8b878', 'desc': '清初皇宫'},
 ],
 'dalian': [
   {'name': '大连星海广场', 'lng': 121.5860, 'lat': 38.8890, 'h': 25, 'type': 'wheel', 'color': '#e8c8a8', 'desc': '亚洲最大城市广场'},
   {'name': '大连裕景中心', 'lng': 121.6100, 'lat': 38.9140, 'h': 383, 'type': 'taper', 'color': '#9fc8e8', 'desc': '383m'},
 ],
 'changchun': [
   {'name': '长春国际金融中心', 'lng': 125.3200, 'lat': 43.8700, 'h': 226, 'type': 'tower', 'color': '#9fc8e8', 'desc': '226m'},
   {'name': '伪满皇宫', 'lng': 125.3200, 'lat': 43.9090, 'h': 18, 'type': 'ancient', 'color': '#d8b878', 'desc': '溥仪宫廷遗址'},
 ],
 'jinan': [
   {'name': '济南绿地普利中心', 'lng': 117.0000, 'lat': 36.6700, 'h': 303, 'type': 'taper', 'color': '#9fc8e8', 'desc': '303m'},
   {'name': '趵突泉', 'lng': 117.0100, 'lat': 36.6640, 'h': 12, 'type': 'ancient', 'color': '#9fd3f0', 'desc': '天下第一泉'},
 ],
 'ningbo': [
   {'name': '宁波中心大厦', 'lng': 121.6060, 'lat': 29.8800, 'h': 409, 'type': 'taper', 'color': '#9fc8e8', 'desc': '409m'},
   {'name': '天一阁', 'lng': 121.5390, 'lat': 29.8770, 'h': 15, 'type': 'ancient', 'color': '#d8b878', 'desc': '中国最古老藏书楼'},
 ],
 'hefei': [
   {'name': '合肥恒大中心', 'lng': 117.2890, 'lat': 31.7420, 'h': 518, 'type': 'taper', 'color': '#9fc8e8', 'desc': '518m（在建）'},
   {'name': '合肥大剧院', 'lng': 117.2350, 'lat': 31.8220, 'h': 40, 'type': 'pavilion', 'color': '#c8d8e8', 'desc': '天鹅湖畔'},
 ],
 'fuzhou': [
   {'name': '福州世茂国际中心', 'lng': 119.3020, 'lat': 26.0800, 'h': 300, 'type': 'taper', 'color': '#9fc8e8', 'desc': '300m'},
   {'name': '三坊七巷', 'lng': 119.2950, 'lat': 26.0800, 'h': 12, 'type': 'ancient', 'color': '#d8b878', 'desc': '明清古建筑群'},
 ],
 'xiamen': [
   {'name': '厦门世茂海峡大厦', 'lng': 118.1110, 'lat': 24.4420, 'h': 300, 'type': 'taper', 'color': '#9fd3f0', 'desc': '双子塔 · 300m'},
   {'name': '日光岩', 'lng': 118.0670, 'lat': 24.4460, 'h': 92, 'type': 'ancient', 'color': '#d8b878', 'desc': '鼓浪屿'},
 ],
 'nanning': [
   {'name': '南宁华润东写字楼', 'lng': 108.3900, 'lat': 22.8150, 'h': 445, 'type': 'taper', 'color': '#9fc8e8', 'desc': '445m · 广西第一高楼'},
   {'name': '南宁国际会展中心', 'lng': 108.3680, 'lat': 22.8180, 'h': 60, 'type': 'pavilion', 'color': '#c8d8e8', 'desc': '朱槿花造型'},
 ],
 'kunming': [
   {'name': '昆明春之眼', 'lng': 102.7180, 'lat': 25.0380, 'h': 407, 'type': 'tower', 'color': '#9fc8e8', 'desc': '407m（在建）'},
   {'name': '金马碧鸡坊', 'lng': 102.7100, 'lat': 25.0330, 'h': 14, 'type': 'ancient', 'color': '#d8b878', 'desc': '明代牌坊'},
 ],
 'wuxi': [
   {'name': '无锡国金中心', 'lng': 120.3050, 'lat': 31.5750, 'h': 339, 'type': 'taper', 'color': '#9fc8e8', 'desc': '339m'},
   {'name': '无锡灵山大佛', 'lng': 120.0950, 'lat': 31.4350, 'h': 88, 'type': 'ancient', 'color': '#d8b878', 'desc': '88m 青铜立像'},
 ],
}

added = 0
for cid, items in LANDMARKS.items():
    c = by.get(cid)
    if c:
        c['landmarks'] = items
        added += len(items)

def densify(points, step=0.005):
    out = [points[0]]
    for a, b in zip(points, points[1:]):
        dd = ((b[0]-a[0])**2 + (b[1]-a[1])**2)**0.5
        n = max(1, int(dd/step))
        for i in range(1, n + 1):
            t = i / n
            out.append([round(a[0] + (b[0]-a[0])*t, 6), round(a[1] + (b[1]-a[1])*t, 6)])
    return out

sz = by.get('suzhou')
if sz:
    sz['river'] = {
      'name': '京杭大运河',
      'points': densify([[120.560, 31.330], [120.590, 31.315], [120.620, 31.300],
                         [120.660, 31.290], [120.700, 31.285], [120.740, 31.290]]),
      'widthM': 130, 'startWidthM': 140, 'endWidthM': 120,
      'color': 0x1d6494, 'edgeColor': 0x4d9fd0, 'centerColor': 0x8fd8ff,
    }

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('新增地标:', added, '座，涉及', len(LANDMARKS), '城')
print('地标覆盖:', sum(1 for c in d['cities'] if c.get('landmarks')), '/', len(d['cities']),
      '城, 共', sum(len(c.get('landmarks') or []) for c in d['cities']), '座')
print('水系覆盖:', sum(1 for c in d['cities'] if c.get('river')), '/', len(d['cities']))