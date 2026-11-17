# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

京津冀城际高铁批次：京张高铁（含崇礼铁路太子城支线）+ 京津城际。

事实依据（公开资料）：
- 京张高铁：2019-12-30 开通，北京北—张家口 174km，设计 350km/h，
  中国首条智能高铁；八达岭长城站埋深 102 米——世界最深高铁站。
- 崇礼铁路：下花园北—太子城支线，服务 2022 冬奥崇礼赛区。
- 京津城际：2008-08-01 开通，中国首条 350km/h 高速铁路，北京南—天津 120km。

站点坐标为公开地图级示意值（非测绘级）；八达岭长城站埋深 102 米为公开
资料实测值（非算法生成），以 depthSource 标注来源。
"""
import io, json

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))

if any(c['id'] == 'jjj-hsr' for c in d['cities']):
    # 幂等：先移除旧条目再重新插入（数据修正后可重复执行）
    d['cities'] = [c for c in d['cities'] if c['id'] != 'jjj-hsr']

# ---------- 京张高铁主线（10 站） ----------
jz_main = {
    'id': 'jz-hsr',
    'name': '京张高铁',
    'color': '#4A90D9',
    'from': '北京北', 'to': '张家口',
    'lengthKm': 174,
    'opened': 2019,
    'stations': [
        {'name': '北京北', 'lng': 116.3547, 'lat': 39.9411, 'type': 'underground', 'depth': 10,
         'transfer': ['2', '4', '13'],
         'note': '京张高铁起点 · 西直门综合交通枢纽（地下站）',
         'depthSource': '京张高铁公开资料：北京北站为地下站'},
        {'name': '清河', 'lng': 116.3377, 'lat': 40.0328, 'type': 'underground', 'depth': 14,
         'transfer': ['13', '昌平线'],
         'note': '与地铁 13 号线 / 昌平线换乘 · 京张场设于地下',
         'depthSource': '京张高铁公开资料：清河站京张场设于地下'},
        {'name': '沙河', 'lng': 116.2966, 'lat': 40.0902, 'type': 'ground', 'depth': 0, 'transfer': []},
        {'name': '昌平', 'lng': 116.2311, 'lat': 40.2159, 'type': 'ground', 'depth': 0, 'transfer': []},
        {'name': '八达岭长城', 'lng': 116.0201, 'lat': 40.3598, 'type': 'underground', 'depth': 102,
         'transfer': [],
         'note': '世界最深高铁站——埋深 102 米，隐于新八达岭隧道山体中（公开资料实测值）',
         'depthSource': '京张高铁公开资料：八达岭长城站埋深 102 米（世界最深高铁站）'},
        {'name': '东花园北', 'lng': 115.5883, 'lat': 40.3252, 'type': 'ground', 'depth': 0, 'transfer': []},
        {'name': '怀来', 'lng': 115.5210, 'lat': 40.4056, 'type': 'ground', 'depth': 0, 'transfer': []},
        {'name': '下花园北', 'lng': 115.4347, 'lat': 40.4667, 'type': 'ground', 'depth': 0,
         'transfer': ['京张高铁太子城支线'], 'note': '崇礼铁路（太子城支线）分岔枢纽'},
        {'name': '宣化北', 'lng': 115.0936, 'lat': 40.5565, 'type': 'ground', 'depth': 0, 'transfer': []},
        {'name': '张家口', 'lng': 114.8859, 'lat': 40.7668, 'type': 'ground', 'depth': 0, 'transfer': []},
    ],
}

# ---------- 崇礼铁路（太子城支线，冬奥专线） ----------
jz_tzc = {
    'id': 'jz-tzc',
    'name': '太子城支线',
    'color': '#8B5CF6',
    'from': '下花园北', 'to': '太子城',
    'opened': 2019,
    'stations': [
        {'name': '下花园北', 'lng': 115.4347, 'lat': 40.4667, 'type': 'ground', 'depth': 0,
         'transfer': ['京张高铁'], 'note': '崇礼铁路自京张高铁下花园北站引出'},
        {'name': '太子城', 'lng': 115.4197, 'lat': 40.8657, 'type': 'ground', 'depth': 0,
         'transfer': [], 'note': '2022 冬奥崇礼赛区门户车站（冬奥专线终点）'},
    ],
}

# ---------- 京津城际（中国首条 350km/h 高铁，4 站） ----------
jt_hsr = {
    'id': 'jt-hsr',
    'name': '京津城际',
    'color': '#C62828',
    'from': '北京南', 'to': '天津',
    'lengthKm': 120,
    'opened': 2008,
    'stations': [
        {'name': '北京南', 'lng': 116.3786, 'lat': 39.8652, 'type': 'ground', 'depth': 0,
         'transfer': ['4', '14'], 'note': '中国首条 350km/h 高速铁路的起点（2008-08-01）'},
        {'name': '亦庄', 'lng': 116.5005, 'lat': 39.7883, 'type': 'ground', 'depth': 0, 'transfer': []},
        {'name': '武清', 'lng': 117.0482, 'lat': 39.3823, 'type': 'ground', 'depth': 0, 'transfer': []},
        {'name': '天津', 'lng': 117.1952, 'lat': 39.1401, 'type': 'ground', 'depth': 0,
         'transfer': ['3', '9'], 'note': '30 分钟直达天津'},
    ],
}

city = {
    'id': 'jjj-hsr',
    'name': '京津冀 · 京张高铁 / 京津城际',
    'lines': [jz_main, jz_tzc, jt_hsr],
    'river': {
        'name': '官厅水库',
        'points': [
            [115.500, 40.280], [115.530, 40.308], [115.555, 40.325],
            [115.580, 40.335], [115.600, 40.345], [115.625, 40.352],
        ],
    },
    'note': '京张高铁 2019-12-30 开通——中国首条智能高铁（350km/h）；'
            '八达岭长城站埋深 102 米为公开资料实测值（世界最深高铁站，非算法生成）；'
            '站点坐标为公开地图级示意。崇礼铁路太子城支线服务 2022 冬奥赛区。',
}

# 插入位置：bridges 特殊条目之前（普通城市保持连续）
idx = next(i for i, c in enumerate(d['cities']) if c['id'] == 'bridges')
d['cities'].insert(idx, city)

io.open(p, 'w', encoding='utf-8').write(
    json.dumps(d, ensure_ascii=False, separators=(',', ':')))

n_st = sum(len(l.get('stations', [])) for l in city['lines'])
print(f'[add_jingzhang] 已插入 {city["name"]}：{len(city["lines"])} 线 / {n_st} 站（含八达岭长城站 -102m）')
