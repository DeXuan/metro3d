# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

交通枢纽图层：城市可设为地铁/轨道交通/城际铁路直达的机场（通用 airports 字段）。
坐标为公开地图级示意值，IATA 码为标准三字码。
"""
import io, json

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}

AIRPORTS = {
 'beijing':    [{'name': '首都国际机场T3', 'iata': 'PEK', 'lng': 116.610, 'lat': 40.052, 'note': '首都机场线'},
                {'name': '大兴国际机场', 'iata': 'PKX', 'lng': 116.412, 'lat': 39.513, 'note': '大兴机场线'}],
 'shanghai':   [{'name': '虹桥国际机场', 'iata': 'SHA', 'lng': 121.336, 'lat': 31.199, 'note': '2/10/17号线'},
                {'name': '浦东国际机场', 'iata': 'PVG', 'lng': 121.806, 'lat': 31.144, 'note': '2号线 · 磁浮'}],
 'guangzhou':  [{'name': '白云国际机场', 'iata': 'CAN', 'lng': 113.300, 'lat': 23.392, 'note': '3号线北延'}],
 'shenzhen':   [{'name': '宝安国际机场', 'iata': 'SZX', 'lng': 113.811, 'lat': 22.639, 'note': '11号线'}],
 'chengdu':    [{'name': '双流国际机场', 'iata': 'CTU', 'lng': 103.952, 'lat': 30.578, 'note': '10号线'},
                {'name': '天府国际机场', 'iata': 'TFU', 'lng': 104.441, 'lat': 30.313, 'note': '18号线'}],
 'chongqing':  [{'name': '江北国际机场', 'iata': 'CKG', 'lng': 106.641, 'lat': 29.720, 'note': '3/10号线'}],
 'hangzhou':   [{'name': '萧山国际机场', 'iata': 'HGH', 'lng': 120.434, 'lat': 30.236, 'note': '1/7/19号线'}],
 'nanjing':    [{'name': '禄口国际机场', 'iata': 'NKG', 'lng': 118.864, 'lat': 31.740, 'note': 'S1机场线'}],
 'zhengzhou':  [{'name': '新郑国际机场', 'iata': 'CGO', 'lng': 113.841, 'lat': 34.527, 'note': '城郊线'}],
 'wuhan':      [{'name': '天河国际机场', 'iata': 'WUH', 'lng': 114.219, 'lat': 30.784, 'note': '2号线'}],
 'changsha':   [{'name': '黄花国际机场', 'iata': 'CSX', 'lng': 113.220, 'lat': 28.189, 'note': '6号线'}],
 'xian':       [{'name': '咸阳国际机场', 'iata': 'XIY', 'lng': 108.752, 'lat': 34.447, 'note': '14号线'}],
 'kunming':    [{'name': '长水国际机场', 'iata': 'KMG', 'lng': 102.929, 'lat': 25.101, 'note': '6号线'}],
 'shenyang':   [{'name': '桃仙国际机场', 'iata': 'SHE', 'lng': 123.482, 'lat': 41.638, 'note': '2号线支线'}],
 'dalian':     [{'name': '周水子国际机场', 'iata': 'DLC', 'lng': 121.539, 'lat': 38.968, 'note': '2号线'}],
 'qingdao':    [{'name': '胶东国际机场', 'iata': 'TAO', 'lng': 120.083, 'lat': 36.372, 'note': '8号线'}],
 'tianjin':    [{'name': '滨海国际机场', 'iata': 'TSN', 'lng': 117.353, 'lat': 39.124, 'note': '2号线'}],
 'wulumuqi':   [{'name': '地窝堡国际机场', 'iata': 'URC', 'lng': 87.474, 'lat': 43.907, 'note': '1号线'}],
 'lanzhou':    [{'name': '中川国际机场', 'iata': 'LHW', 'lng': 103.723, 'lat': 36.515, 'note': '中川城际'}],
 'taiyuan':    [{'name': '武宿国际机场', 'iata': 'TYN', 'lng': 112.627, 'lat': 37.751, 'note': '1号线'}],
 'huhehaote':  [{'name': '白塔国际机场', 'iata': 'HET', 'lng': 111.817, 'lat': 40.849, 'note': '机场线'}],
 'xuzhou':     [{'name': '观音国际机场', 'iata': 'XUZ', 'lng': 117.543, 'lat': 34.050, 'note': 'S1线'}],
 'aidermoot':  [],  # 占位防错
}
del AIRPORTS['aidermoot']

n = 0
for cid, ap in AIRPORTS.items():
    c = by.get(cid)
    if c and ap:
        c['airports'] = ap
        n += len(ap)

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('机场枢纽写入:', n, '座 /', len(AIRPORTS), '城')