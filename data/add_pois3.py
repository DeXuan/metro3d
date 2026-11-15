# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

文化 POI 第三批：武汉（东湖/古德寺/晴川阁）、成都（武侯祠/杜甫草堂/金沙遗址）、长沙（岳麓书院/爱晚亭/天心阁）+ 东湖/西湖楼外楼湖泊。
坐标为公开资料级示意值。
"""
import io, json, math

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}

def ellipse(cx, cy, ra, rb, n=10):
    return [[round(cx + ra * math.cos(2 * math.pi * k / n), 6),
             round(cy + rb * math.sin(2 * math.pi * k / n), 6)] for k in range(n)]

# ---------- 武汉 ----------
by['wuhan'].setdefault('landmarks', []).extend([
    {'name': '东湖绿道', 'lng': 114.390, 'lat': 30.555, 'h': 5,
     'type': 'pavilion', 'color': '#8fc89a', 'desc': '中国最大城中湖'},
    {'name': '古德寺', 'lng': 114.305, 'lat': 30.628, 'h': 30,
     'type': 'pagoda', 'color': '#c9a86a', 'desc': '混合欧亚建筑风格 · 全国重点文保'},
    {'name': '晴川阁', 'lng': 114.285, 'lat': 30.570, 'h': 25,
     'type': 'ancient', 'color': '#d8b878', 'desc': '长江南岸 · 晴川历历汉阳树'},
])
by['wuhan']['lakes'] = [{
    'name': '东湖', 'desc': '中国最大城中湖 · 湖光山色',
    'points': ellipse(114.380, 30.560, 0.028, 0.020, 12),
}]

# ---------- 成都 ----------
by['chengdu'].setdefault('landmarks', []).extend([
    {'name': '武侯祠', 'lng': 104.048, 'lat': 30.645, 'h': 15,
     'type': 'ancient', 'color': '#c94f4f', 'desc': '三国文化圣地 · 君臣合祀'},
    {'name': '杜甫草堂', 'lng': 104.027, 'lat': 30.661, 'h': 12,
     'type': 'pavilion', 'color': '#8fc89a', 'desc': '诗圣故居 · 茅屋听雨'},
    {'name': '金沙遗址', 'lng': 104.012, 'lat': 30.690, 'h': 18,
     'type': 'castle', 'color': '#e8a845', 'desc': '太阳神鸟 · 古蜀文明'},
])

# ---------- 长沙 ----------
by['changsha'].setdefault('landmarks', []).extend([
    {'name': '岳麓书院', 'lng': 112.940, 'lat': 28.188, 'h': 25,
     'type': 'ancient', 'color': '#d8b878', 'desc': '千年学府 · 惟楚有才'},
    {'name': '爱晚亭', 'lng': 112.938, 'lat': 28.183, 'h': 12,
     'type': 'pavilion', 'color': '#c96a4a', 'desc': '停车坐爱枫林晚'},
    {'name': '天心阁', 'lng': 112.978, 'lat': 28.190, 'h': 20,
     'type': 'castle', 'color': '#b8a078', 'desc': '古城地标 · 登阁览湘'},
])

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('POI 第三批完成：武汉+3+东湖 / 成都+3 / 长沙+3')