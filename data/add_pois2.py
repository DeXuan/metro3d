# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

文化 POI 扩城：西安 / 北京 / 重庆 / 苏州（追加式，不动已有条目）。
坐标为公开资料级示意值。
"""
import io, json, math

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}

def ellipse(cx, cy, ra, rb, n=10):
    return [[round(cx + ra * math.cos(2 * math.pi * k / n), 6),
             round(cy + rb * math.sin(2 * math.pi * k / n), 6)] for k in range(n)]

# ---------- 西安 ----------
by['xian'].setdefault('landmarks', []).extend([
    {'name': '小雁塔', 'lng': 108.924, 'lat': 34.240, 'h': 43,
     'type': 'pagoda', 'color': '#d8b878', 'desc': '荐福寺 · 唐代密檐塔'},
    {'name': '大明宫丹凤门', 'lng': 108.948, 'lat': 34.288, 'h': 32,
     'type': 'gate', 'color': '#c9a86a', 'desc': '大明宫遗址 · 帝国正门'},
    {'name': '永宁门', 'lng': 108.940, 'lat': 34.252, 'h': 28,
     'type': 'gate', 'color': '#b8a078', 'desc': '明城墙正南门'},
])

# ---------- 北京 ----------
by['beijing'].setdefault('landmarks', []).extend([
    {'name': '天安门', 'lng': 116.398, 'lat': 39.903, 'h': 34,
     'type': 'gate', 'color': '#c94f4f', 'desc': '中华人民共和国象征'},
    {'name': '天坛祈年殿', 'lng': 116.410, 'lat': 39.882, 'h': 38,
     'type': 'pavilion', 'color': '#4a7ac0', 'desc': '三重檐 · 明清祭天之所'},
    {'name': '故宫午门', 'lng': 116.394, 'lat': 39.913, 'h': 38,
     'type': 'gate', 'color': '#c94f4f', 'desc': '紫禁城正门'},
    {'name': '中央电视塔', 'lng': 116.302, 'lat': 39.911, 'h': 405,
     'type': 'tower', 'color': '#9fc8e8', 'desc': '405m · 西三环'},
])

# ---------- 重庆 ----------
by['chongqing'].setdefault('landmarks', []).extend([
    {'name': '洪崖洞', 'lng': 106.577, 'lat': 29.562, 'h': 75,
     'type': 'castle', 'color': '#e8a845', 'desc': '吊脚楼群 · 山城夜景'},
    {'name': '解放碑', 'lng': 106.552, 'lat': 29.559, 'h': 27,
     'type': 'tower', 'color': '#c94f4f', 'desc': '抗战胜利纪功碑'},
])

# ---------- 苏州：北寺塔 / 拙政园 + 金鸡湖 ----------
by['suzhou'].setdefault('landmarks', []).extend([
    {'name': '北寺塔', 'lng': 120.620, 'lat': 31.329, 'h': 76,
     'type': 'pagoda', 'color': '#d8b878', 'desc': '报恩寺塔 · 吴中第一名刹'},
    {'name': '拙政园', 'lng': 120.627, 'lat': 31.325, 'h': 12,
     'type': 'pavilion', 'color': '#8fc89a', 'desc': '中国四大名园之首'},
])
by['suzhou']['lakes'] = [{
    'name': '金鸡湖', 'desc': '工业园区 · 中国最大城市内湖之一',
    'points': ellipse(120.685, 31.305, 0.030, 0.023, 12),
}]

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('POI 扩城完成：西安+3 / 北京+4 / 重庆+2 / 苏州+2+金鸡湖')
