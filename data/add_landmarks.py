# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

免责声明：本脚本生成的数据仅供可视化演示与学习参考，禁止用于工程、施工、
测绘、导航或军事等专业用途。生成的埋深为示意值（非实测数据）。
详见 README「数据精度与使用限制」。

为各城市添加地标建筑数据（真实经纬度 + 高度 + 造型类型）
"""
import json

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))
by = {c['id']: c for c in d['cities']}

# 造型类型：
#  tv_tower   电视塔（球体串塔）        : 东方明珠
#  twist      扭转超高层                 : 上海中心
#  opener     开瓶器（顶部洞口）         : 环球金融中心
#  pagoda     阶梯塔楼                   : 金茂大厦 / 台北101 式
#  pavilion   斗拱倒锥（世博会中国馆）   : 中华艺术宫
#  castle     城堡（塔群+尖顶）          : 迪士尼
#  tower      通用超高层                 : 平安/紫峰/IFS 等
#  gate       门形双塔                   : 苏州东方之门
#  corn       椭圆塔                     : 郑州大玉米
#  ancient    仿古建筑（钟楼/大雁塔式）  : 西安钟楼、大雁塔、洛阳应天门
#  wheel      摩天轮                     : 天津之眼式（暂无）
LANDMARKS = {
 'shanghai': [
   {'name': '东方明珠', 'lng': 121.4998, 'lat': 31.2397, 'h': 468, 'type': 'tv_tower',
    'color': '#e86a9a', 'desc': '468m · 上海地标'},
   {'name': '上海中心大厦', 'lng': 121.5057, 'lat': 31.2354, 'h': 632, 'type': 'twist',
    'color': '#9fd3f0', 'desc': '632m · 中国第一高楼'},
   {'name': '环球金融中心', 'lng': 121.5052, 'lat': 31.2347, 'h': 492, 'type': 'opener',
    'color': '#8fc4e8', 'desc': '492m · 开瓶器'},
   {'name': '金茂大厦', 'lng': 121.5066, 'lat': 31.2347, 'h': 421, 'type': 'pagoda',
    'color': '#b8d8f0', 'desc': '421m · 塔楼'},
   {'name': '中华艺术宫', 'lng': 121.4926, 'lat': 31.1856, 'h': 63, 'type': 'pavilion',
    'color': '#e05a4a', 'desc': '世博会中国馆 · 斗拱'},
   {'name': '迪士尼城堡', 'lng': 121.6590, 'lat': 31.1470, 'h': 60, 'type': 'castle',
    'color': '#e8c8a8', 'desc': '奇幻童话城堡'},
 ],
 'beijing': [
   {'name': '中国尊', 'lng': 116.4605, 'lat': 39.9130, 'h': 528, 'type': 'twist',
    'color': '#9fc8e8', 'desc': '528m · 北京第一高楼'},
   {'name': '央视总部', 'lng': 116.4578, 'lat': 39.9154, 'h': 234, 'type': 'opener',
    'color': '#8ab8d8', 'desc': '大裤衩'},
   {'name': '鸟巢', 'lng': 116.3967, 'lat': 39.9929, 'h': 68, 'type': 'pavilion',
    'color': '#d8d0b8', 'desc': '国家体育场'},
 ],
 'guangzhou': [
   {'name': '广州塔', 'lng': 113.3245, 'lat': 23.1066, 'h': 600, 'type': 'tv_tower',
    'color': '#c86ae8', 'desc': '600m · 小蛮腰'},
   {'name': '广州西塔', 'lng': 113.3213, 'lat': 23.1180, 'h': 440, 'type': 'tower',
    'color': '#9fd3f0', 'desc': 'IFC · 440m'},
   {'name': '广州东塔', 'lng': 113.3252, 'lat': 23.1184, 'h': 530, 'type': 'taper',
    'color': '#8fc4e8', 'desc': '周大福中心 · 530m'},
 ],
 'shenzhen': [
   {'name': '平安金融中心', 'lng': 114.0505, 'lat': 22.5344, 'h': 599, 'type': 'taper',
    'color': '#9fc8e8', 'desc': '599m · 深圳第一高楼'},
   {'name': '平安信用卡大厦', 'lng': 114.0480, 'lat': 22.5330, 'h': 300, 'type': 'tower',
    'color': '#8fc4e8', 'desc': '300m'},
 ],
 'chongqing': [
   {'name': '来福士广场', 'lng': 106.5870, 'lat': 29.5660, 'h': 354, 'type': 'tower',
    'color': '#9fd3f0', 'desc': '354m · 朝天门'},
   {'name': '环球金融中心', 'lng': 106.5533, 'lat': 29.5613, 'h': 339, 'type': 'tower',
    'color': '#8fc4e8', 'desc': '339m · 江北嘴'},
 ],
 'hongkong': [
   {'name': '中银大厦', 'lng': 114.1610, 'lat': 22.2795, 'h': 367, 'type': 'taper',
    'color': '#c8d8e8', 'desc': '367m · 贝聿铭设计'},
   {'name': '国际金融中心二期', 'lng': 114.1590, 'lat': 22.2850, 'h': 415, 'type': 'taper',
    'color': '#9fc8e8', 'desc': 'IFC · 415m'},
   {'name': '环球贸易广场', 'lng': 114.1605, 'lat': 22.3033, 'h': 484, 'type': 'taper',
    'color': '#8fc4e8', 'desc': 'ICC · 484m'},
 ],
 'wuhan': [
   {'name': '绿地中心', 'lng': 114.3540, 'lat': 30.5560, 'h': 475, 'type': 'taper',
    'color': '#9fc8e8', 'desc': '475m · 武汉第一高楼'},
   {'name': '黄鹤楼', 'lng': 114.3020, 'lat': 30.5455, 'h': 52, 'type': 'ancient',
    'color': '#d8b878', 'desc': '江南名楼'},
 ],
 'nanjing': [
   {'name': '紫峰大厦', 'lng': 118.7770, 'lat': 32.0620, 'h': 450, 'type': 'taper',
    'color': '#9fc8e8', 'desc': '450m · 南京第一高楼'},
   {'name': '南京眼', 'lng': 118.7300, 'lat': 32.0330, 'h': 100, 'type': 'gate',
    'color': '#c8d8e8', 'desc': '青奥步行桥'},
 ],
 'hangzhou': [
   {'name': '杭州之门', 'lng': 120.2450, 'lat': 30.2400, 'h': 310, 'type': 'gate',
    'color': '#9fd3f0', 'desc': '310m · 双塔'},
   {'name': '雷峰塔', 'lng': 120.1490, 'lat': 30.2320, 'h': 71, 'type': 'ancient',
    'color': '#d8b878', 'desc': '西湖十景'},
 ],
 'chengdu': [
   {'name': '天府熊猫塔', 'lng': 104.1180, 'lat': 30.6680, 'h': 339, 'type': 'tv_tower',
    'color': '#e8a86a', 'desc': '339m · 西部明珠'},
   {'name': '环球中心', 'lng': 104.0630, 'lat': 30.5700, 'h': 100, 'type': 'pavilion',
    'color': '#9fd3f0', 'desc': '新世纪环球中心'},
 ],
 'xian': [
   {'name': '钟楼', 'lng': 108.9420, 'lat': 34.2610, 'h': 36, 'type': 'ancient',
    'color': '#d8b878', 'desc': '明代 · 西安地标'},
   {'name': '大雁塔', 'lng': 108.9640, 'lat': 34.2180, 'h': 64, 'type': 'ancient',
    'color': '#c8a878', 'desc': '唐代 · 大慈恩寺'},
 ],
 'qingdao': [
   {'name': '五月的风', 'lng': 120.3830, 'lat': 36.0590, 'h': 30, 'type': 'wheel',
    'color': '#e05a4a', 'desc': '五四广场雕塑'},
 ],
 'changsha': [
   {'name': '长沙 IFS 国金中心', 'lng': 112.9770, 'lat': 28.1930, 'h': 452, 'type': 'taper',
    'color': '#9fc8e8', 'desc': '452m · 长沙第一高楼'},
   {'name': '橘子洲青年毛泽东像', 'lng': 112.9640, 'lat': 28.1920, 'h': 32, 'type': 'ancient',
    'color': '#d8b878', 'desc': '橘子洲头'},
 ],
 'suzhou': [
   {'name': '东方之门', 'lng': 120.7350, 'lat': 31.3150, 'h': 302, 'type': 'gate',
    'color': '#9fd3f0', 'desc': '302m · 门形双塔'},
   {'name': '虎丘塔', 'lng': 120.5730, 'lat': 31.3260, 'h': 47, 'type': 'ancient',
    'color': '#c8a878', 'desc': '云岩寺塔 · 斜塔'},
 ],
 'zhengzhou': [
   {'name': '千禧广场', 'lng': 113.7370, 'lat': 34.7630, 'h': 280, 'type': 'corn',
    'color': '#e8d06a', 'desc': '280m · 大玉米'},
   {'name': '郑州会展中心', 'lng': 113.7300, 'lat': 34.7640, 'h': 60, 'type': 'pavilion',
    'color': '#9fc8e8', 'desc': '郑东新区'},
 ],
 'luoyang': [
   {'name': '应天门', 'lng': 112.4595, 'lat': 34.6670, 'h': 60, 'type': 'ancient',
    'color': '#d8b878', 'desc': '隋唐洛阳城 · 遗址复建'},
 ],
}

n = 0
for cid, items in LANDMARKS.items():
    c = by.get(cid)
    if not c: continue
    c['landmarks'] = items
    n += len(items)

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('landmarks added:', n, 'to', len(LANDMARKS), 'cities')
for cid in LANDMARKS:
    print(' ', cid, len(LANDMARKS[cid]))