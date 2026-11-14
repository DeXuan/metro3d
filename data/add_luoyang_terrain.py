# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

洛阳邙山（崤山余脉）三维地形：城市北侧东西带状缓丘群。
峰高为相对市区的高差示意值（真实邙山海拔 250-450m，相对高差 150-250m）；
底半径按山体实际宽度（数公里）取值，渲染时与地标一致做 8× 高度夸张。
"""
import io, json

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}
ly = by['luoyang']

ly['terrain'] = {
  'name': '邙山',
  'desc': '崤山余脉 · 北邙',
  'peaks': [
    [112.365, 34.712, 180, 7],
    [112.405, 34.720, 220, 8],
    [112.445, 34.728, 260, 9],
    [112.485, 34.720, 220, 8],
    [112.525, 34.710, 180, 7],
    [112.560, 34.698, 140, 6],
  ],
}

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('邙山地形已写入：', len(ly['terrain']['peaks']), '座峰')
