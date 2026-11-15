# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

补充洛阳北郊机场（LYA）：无轨道交通直达，地面交通接驳。
坐标为公开地图级示意值。
"""
import io, json

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
ly = next(c for c in d['cities'] if c['id'] == 'luoyang')

ly['airports'] = [{
    'name': '北郊国际机场', 'iata': 'LYA',
    'lng': 112.452, 'lat': 34.745,
    'note': '邙山之上 · 地面交通接驳',
}]

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('洛阳北郊机场已写入')
