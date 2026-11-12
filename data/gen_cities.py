# -*- coding: utf-8 -*-
"""解析高德地铁数据（北京/南京/郑州/洛阳）→ 统一线路格式 other_cities.json
字段：id/name/color/loop/from/to/lengthKm/stations[{name,lng,lat,type,depth|height,transfer}]
深度为示意值；高架/地面按线路结构知识标注。
"""
import json, math, hashlib, collections

SRC = {
 'beijing':  ('北京', 'bj'),
 'nanjing':  ('南京', 'nj'),
 'zhengzhou':('郑州', 'zz'),
 'luoyang':  ('洛阳', 'ly'),
}

def jitter(name, base, spread=2.0):
    h = int(hashlib.md5(name.encode('utf-8')).hexdigest()[:6], 16)
    return round(base + ((h % 1000)/1000 - .5) * 2 * spread, 1)

# ---------------- 结构知识：高架/地面站 ----------------
# 键：线路名（高德 ln）
ELEV = {
 # 北京
 '13号线': {'e': 'ALL_EXCEPT', 'except': {'西直门'}},
 'S1线': {'e': 'ALL'},
 '西郊线': {'g': 'ALL'},
 '首都机场线': {'e': {'T2航站楼', 'T3航站楼'}, 'u': {'东直门', '三元桥'}},
 '大兴机场线': {'e': {'大兴机场'}, 'u': {'草桥', '大兴新城'}},
 '房山线': {'e': 'ALL_EXCEPT', 'except': {'郭公庄'}},
 '燕房线': {'e': 'ALL'},
 '亦庄线': {'e': {'荣昌东街','同济南路','经海路','次渠南','次渠','亦庄火车站'}},
 '昌平线': {'e': {'西二旗','生命科学园','朱辛庄','巩华城','沙河','沙河高教园','南邵','北邵洼','昌平东关','昌平','十三陵景区','昌平西山口'}},
 # 南京
 '1号线': {'g': {'小行'}},
 'S1号线(机场线)': {'e': 'ALL_EXCEPT', 'except': {'南京南站'}},
 'S2号线(宁马线)': {'e': 'ALL_EXCEPT', 'except': {'西善桥'}},
 'S3号线(宁和线)': {'e': 'ALL_EXCEPT', 'except': {'南京南站'}},
 'S6号线(宁句线)': {'e': 'ALL_EXCEPT', 'except': {'马群'}},
 'S7号线(宁溧线)': {'e': 'ALL_EXCEPT', 'except': {'空港新城江宁'}},
 'S8号线(宁天线)': {'e': 'ALL_EXCEPT', 'except': {'泰山新村'}},
 'S9号线(宁高线)': {'e': 'ALL_EXCEPT', 'except': {'翔宇路南'}},
 # 郑州
 '城郊线': {'e': 'ALL_EXCEPT', 'except': {'南四环'}},
 '郑许线': {'e': 'ALL'},
 # 洛阳（全地下）
}

# 各线路一般埋深基准（米）
BASE = {
 # 北京
 '1号线八通线': 11, '2号线': 10, '3号线': 18, '4号线大兴线': 14, '5号线': 14,
 '6号线': 16, '7号线': 16, '8号线': 16, '9号线': 14, '10号线': 15, '11号线': 18,
 '12号线': 18, '13号线': 12, '14号线': 16, '15号线': 17, '16号线': 18, '17号线': 18,
 '18号线': 20, '19号线': 20, '昌平线': 14, '大兴机场线': 18, '房山线': 12,
 '首都机场线': 15, '西郊线': 6, '燕房线': 10, 'S1线': 9, '亦庄线': 14,
 # 南京
 '1号线': 14, '2号线': 14, '3号线': 16, '4号线': 16, '5号线': 18, '6号线': 18,
 '7号线': 18, '10号线': 15, 'S1号线(机场线)': 11, 'S2号线(宁马线)': 10,
 'S3号线(宁和线)': 10, 'S6号线(宁句线)': 10, 'S7号线(宁溧线)': 9,
 'S8号线(宁天线)': 9, 'S9号线(宁高线)': 9,
 # 郑州
 '1号线': 14, '2号线': 14, '3号线': 15, '4号线': 15, '5号线': 15, '6号线': 16,
 '7号线': 17, '8号线': 17, '10号线': 17, '12号线': 18, '14号线': 16,
 '城郊线': 9, '郑许线': 8,
 # 洛阳
 '洛阳1号线': 13, '洛阳2号线': 13,
}

# 已知换乘枢纽深度微调（城市-站名）
KD = {
 '北京': {'西直门': 20, '东直门': 20, '国贸': 22, '复兴门': 18, '建国门': 18,
          '西单': 20, '宣武门': 17, '北京站': 17, '北京南站': 20, '宋家庄': 17,
          '角门西': 16, '菜市口': 17, '磁器口': 15, '崇文门': 18, '雍和宫': 20,
          '望京': 22, '知春路': 15, '海淀黄庄': 17, '国家图书馆': 20, '白石桥南': 17,
          '六里桥': 17, '公主坟': 15, '军事博物馆': 15, '南锣鼓巷': 20, '东四': 22,
          '呼家楼': 20, '金台路': 18, '大望路': 17, '九龙山': 15, '十里河': 16,
          '蒲黄榆': 16, '珠市口': 18, '草桥': 16, '丰台站': 20, '丽泽商务区': 24,
          '北京西站': 20, '五道口': 15, '西土城': 18, '蓟门桥': 20, '北土城': 17},
 '南京': {'新街口': 22, '南京南站': 20, '鼓楼': 18, '珠江路': 16, '大行宫': 18,
          '鸡鸣寺': 16, '南京站': 17, '元通': 16, '安德门': 15, '金马路': 14,
          '马群': 15, '油坊桥': 15, '兴隆大街': 15, '奥体中心': 14, '莫愁湖': 16,
          '上海路': 17, '云南路': 18, '夫子庙': 17, '常府街': 16, '中胜': 14},
 '郑州': {'二七广场': 18, '郑州东站': 20, '郑州火车站': 17, '紫荆山': 17,
          '会展中心': 16, '燕庄': 15, '民航路': 15, '五一公园': 16, '绿城广场': 16,
          '医学院': 16, '桐柏路': 15, '碧沙岗': 15, '南五里堡': 15, '京广南路': 15,
          '市体育中心': 16, '关虎屯': 15, '黄河路': 15, '农业南路': 15},
 '洛阳': {'解放路': 16, '牡丹广场': 15, '王城公园': 15, '青年宫': 15},
}

def parse_latlon(s):
    lng, lat = s.split(',')
    return float(lng), float(lat)

def line_len_km(sts):
    tot = 0.0
    for a, b in zip(sts, sts[1:]):
        la1, lo1 = a['lat'], a['lng']
        la2, lo2 = b['lat'], b['lng']
        dy = (la2-la1) * 110.54
        dx = (lo2-lo1) * 111.32 * math.cos(math.radians((la1+la2)/2))
        tot += math.hypot(dx, dy)
    return round(tot, 1)

def truthy_set(v):
    return v if isinstance(v, set) else set()

out_cities = []
for key, (cn, prefix) in SRC.items():
    d = json.load(open(f'{key}.json', encoding='utf-8'))
    raw_lines = d['l']

    # 换乘聚合：poiid → 出现的线路名集合
    by_poi = collections.defaultdict(set)
    for l in raw_lines:
        for s in l.get('st', []):
            pid = s.get('poiid') or s.get('n')
            by_poi[pid].add(l['ln'])

    lines_out = []
    for li, l in enumerate(raw_lines):
        ln = l['ln']
        sts = l.get('st', [])
        if not sts:
            continue
        is_loop = str(l.get('lo', '0')) == '1'
        color = '#' + (l.get('cl') or '4FC2E8')
        cfg = ELEV.get(ln, {})
        stations = []
        for s in sts:
            name = s.get('n') or '未命名'
            lng, lat = parse_latlon(s['sl'])
            pid = s.get('poiid') or name
            tr = sorted(by_poi[pid] - {ln})
            # 结构判定
            e_all = cfg.get('e') == 'ALL'
            e_exc = cfg.get('e') == 'ALL_EXCEPT'
            e_set = truthy_set(cfg.get('e') if isinstance(cfg.get('e'), set) else None)
            g_all = cfg.get('g') == 'ALL'
            g_set = truthy_set(cfg.get('g') if isinstance(cfg.get('g'), set) else None)
            st_obj = {'name': name, 'lng': round(lng, 6), 'lat': round(lat, 6)}
            if g_all or name in g_set:
                st_obj.update({'type': 'ground', 'height': 0})
            elif e_all or name in e_set or (e_exc and name not in truthy_set(cfg.get('except'))):
                st_obj.update({'type': 'elevated', 'height': round(jitter(name, 10, 3), 1)})
            elif name in truthy_set(cfg.get('u')):
                st_obj.update({'type': 'underground',
                               'depth': KD.get(cn, {}).get(name, jitter(name, BASE.get(ln, 15), 2.5))})
            else:
                base = BASE.get(ln, 15)
                depth = KD.get(cn, {}).get(name)
                if depth is None:
                    depth = jitter(name, base, 2.5)
                    if tr:
                        depth = round(depth + 2.5, 1)
                st_obj.update({'type': 'underground', 'depth': depth})
            if tr:
                # 只保留相邻线路名，避免过长
                st_obj['transfer'] = tr[:6]
            stations.append(st_obj)

        from_name = stations[0]['name']
        to_name = stations[-1]['name']
        line_obj = {
            'id': f'{prefix}-{li+1}',
            'name': ln,
            'color': color,
            'from': from_name,
            'to': to_name,
            'lengthKm': line_len_km(stations),
            'stations': stations,
        }
        if is_loop:
            line_obj['loop'] = True
        lines_out.append(line_obj)

    total_st = sum(len(x['stations']) for x in lines_out)
    uniq = len({s['name'] + '|' + str(s['lat']) for x in lines_out for s in x['stations']})
    print(f'{cn}: {len(lines_out)} 线 / {total_st} 站次 / {uniq} 独立站 / 环线 {sum(1 for x in lines_out if x.get("loop"))}')
    out_cities.append({'id': key, 'name': cn, 'lines': lines_out})

json.dump(out_cities, open('other_cities.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
import os
print('json size:', os.path.getsize('other_cities.json'))