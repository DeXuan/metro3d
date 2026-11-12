# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

免责声明：本脚本生成的数据仅供可视化演示与学习参考，禁止用于工程、施工、
测绘、导航或军事等专业用途。生成的埋深为示意值（非实测数据）。
详见 README「数据精度与使用限制」。

补丁：build_v2/render.py 的 DIY_ARTICLES —— 修纵断面卡片链接 bug + 新增全国地铁3D卡片
"""
import io, sys

p = "/opt/aihot-v2/build_v2/render.py"
s = io.open(p, encoding="utf-8").read()

old_card = '''    "chip": "数据可视化",
    "name": "上海轨道交通 · 隧道纵断面工程图",
    "url": "/web/metro3d/",'''

new_card = '''    "chip": "3D可视化",
    "name": "全国地铁线路三维立体视图",
    "url": "/web/metro3d/",
    "desc": "上海 / 北京 / 南京 / 郑州 / 洛阳 五城地铁全网 3D 地下隧道：真实经纬度投影 + 官方线路色，管线随埋深起伏、高架段拱出地面，黄浦江/长江水系参考；城市与线路下拉切换，全网叠加显示，支持沿线巡航与深度着色",
    "priority": 2
  },
  {
    "chip": "数据可视化",
    "name": "上海轨道交通 · 隧道纵断面工程图",
    "url": "/web/metro-3d/",'''

if "全国地铁线路三维立体视图" not in s:
    assert old_card in s, "old card not found"
    s = s.replace(old_card, new_card, 1)
    io.open(p, "w", encoding="utf-8").write(s)
    print("PATCHED: new card added, old link fixed")
else:
    print("ALREADY PATCHED")

# 校验
s2 = io.open(p, encoding="utf-8").read()
print("check new card:", "全国地铁线路三维立体视图" in s2)
print("check old link fixed:", "/web/metro-3d/" in s2)
print("check no stray metro3d left for old card:", s2.count('"url": "/web/metro3d/"') == 1)