# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

文化 POI 第四批：广州（沙面/陈家祠/石室圣心大教堂）、天津（五大道/古文化街）、
哈尔滨（索菲亚教堂/中央大街/防洪纪念塔）、青岛（栈桥/八大关/天主教堂）。
坐标为公开资料级示意值。
"""
import io, json

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}

by['guangzhou'].setdefault('landmarks', []).extend([
    {'name': '沙面岛', 'lng': 113.241, 'lat': 23.110, 'h': 20,
     'type': 'castle', 'color': '#d8c8a8', 'desc': '欧陆建筑群 · 租界史迹'},
    {'name': '陈家祠', 'lng': 113.253, 'lat': 23.125, 'h': 18,
     'type': 'ancient', 'color': '#c94f4f', 'desc': '岭南建筑艺术明珠'},
    {'name': '石室圣心大教堂', 'lng': 113.261, 'lat': 23.114, 'h': 36,
     'type': 'castle', 'color': '#8a97a8', 'desc': '远东巴黎圣母院'},
])

by['tianjin'].setdefault('landmarks', []).extend([
    {'name': '五大道', 'lng': 117.198, 'lat': 39.110, 'h': 18,
     'type': 'castle', 'color': '#d8c8a8', 'desc': '万国建筑博览会'},
    {'name': '古文化街', 'lng': 117.184, 'lat': 39.146, 'h': 15,
     'type': 'ancient', 'color': '#c94f4f', 'desc': '津味民俗 · 天后宫'},
])

by['haerbin'].setdefault('landmarks', []).extend([
    {'name': '索菲亚教堂', 'lng': 126.638, 'lat': 45.780, 'h': 53,
     'type': 'castle', 'color': '#8a6a4a', 'desc': '远东最大东正教堂'},
    {'name': '中央大街', 'lng': 126.625, 'lat': 45.780, 'h': 15,
     'type': 'ancient', 'color': '#d8c8a8', 'desc': '百年面包石路 · 欧式风情'},
    {'name': '防洪纪念塔', 'lng': 126.622, 'lat': 45.795, 'h': 22,
     'type': 'tower', 'color': '#c94f4f', 'desc': '松花江畔 · 斯大林公园'},
])

by['qingdao'].setdefault('landmarks', []).extend([
    {'name': '栈桥回澜阁', 'lng': 120.319, 'lat': 36.058, 'h': 20,
     'type': 'pavilion', 'color': '#c9a86a', 'desc': '青岛百年地标'},
    {'name': '八大关', 'lng': 120.345, 'lat': 36.053, 'h': 15,
     'type': 'castle', 'color': '#d8c8a8', 'desc': '万国建筑 · 花石楼'},
    {'name': '浙江路天主教堂', 'lng': 120.318, 'lat': 36.068, 'h': 56,
     'type': 'castle', 'color': '#8a97a8', 'desc': '哥特式双塔'},
])

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('POI 第四批：广州+3 / 天津+2 / 哈尔滨+3 / 青岛+3')