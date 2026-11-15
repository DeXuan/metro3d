# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

河流流向修正：river.points 数组顺序 = 流光移动方向，须与真实水系流向一致
（起点 = 上游，终点 = 下游）。核对依据为公开地理资料。
海湾类水体（湾/港/海峡）不设流向，渲染层自动关闭流光。
"""
import io, json

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}

# 数组反向的城市（数据顺序与真实流向相反）
FLIP = ['shanghai', 'changsha', 'shenyang', 'changchun', 'nanchang',
        'jinhua', 'wuhu', 'dongguan', 'taibei', 'gaoxiong']

n = 0
for cid in FLIP:
    c = by.get(cid)
    if c and c.get('river') and c['river'].get('points'):
        c['river']['points'] = c['river']['points'][::-1]
        n += 1

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('已翻转 %d 条河流方向：%s' % (n, '、'.join(by[c]['name'] for c in FLIP if by[c].get('river'))))
