# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

免责声明：本脚本生成的数据仅供可视化演示与学习参考，禁止用于工程、施工、
测绘、导航或军事等专业用途。生成的埋深为示意值（非实测数据）。
详见 README「数据精度与使用限制」。

补全换乘关系：按"同名站被多条线路共用"推导换乘

规则：
  1) 站名完全一致 + 出现在 ≥2 条不同线路 → 互为换乘
  2) 站名相近（含括注差异，如 "新郑机场A" vs "新郑机场"）→ 归一化后匹配
  3) 排除：跨城同名（不同城市不互通）、同城但距离过远（>1.2km，防同名异地）
  4) 保留已有 transfer 的人工数据，只补空缺
"""
import json, re, math, collections

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))

def norm(name):
    """归一化站名：去括注、去空格、去书名号等"""
    s = re.sub(r'[（(].*?[)）]', '', name)
    s = s.replace('・', '·').replace(' ', '').strip()
    return s

def dist_m(a, b):
    return math.hypot((a['lng'] - b['lng']) * 111320 * math.cos(math.radians((a['lat']+b['lat'])/2)),
                      (a['lat'] - b['lat']) * 110540)

def line_token(lname):
    """线路名 → 用于显示的短标签"""
    n = lname.replace('支线', '')
    m = re.match(r'^([A-Za-z]?\d+)', n)
    if m:
        tok = m.group(1)
        if re.match(r'^\d+$', tok):
            return tok
        return n
    # 中文线路名（如 机场联络线、杭海城际、宁滁线）
    return n

total_added = 0
report = []

for c in d['cities']:
    if not c.get('lines'):
        continue
    # 1) 建立"归一化站名 → [(line, station)]"索引
    idx = collections.defaultdict(list)
    for l in c['lines']:
        for s in l['stations']:
            idx[norm(s['name'])].append((l, s))

    # 2) 同城跨线同名站 → 互为换乘
    added_here = 0
    for key, group in idx.items():
        line_names = {l['name'] for l, s in group}
        if len(line_names) < 2:
            continue
        # 位置一致性检查（同名但相距太远 → 不是同一站）
        for l, s in group:
            # 与其它线路的近距离同名站
            others = [lnobj['name'] for lnobj, st in group
                      if lnobj['name'] != l['name'] and dist_m(s, st) < 1200]
            if not others:
                continue
            toks = sorted({line_token(x) for x in others})
            cur = s.get('transfer') or []
            cur_set = set(cur)
            merged = sorted(cur_set | set(toks))
            if len(merged) != len(cur):
                s['transfer'] = merged
                added_here += len(merged) - len(cur)
    if added_here:
        report.append((c['name'], added_here))
        total_added += added_here

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

print('补全站次:', total_added)
for name, n in sorted(report, key=lambda x: -x[1]):
    print(f'  {name}: +{n}')

# 复检
print()
print('补全后统计:')
for c in d['cities']:
    if not c.get('lines'): continue
    tot = sum(len(l['stations']) for l in c['lines'])
    tr = sum(1 for l in c['lines'] for s in l['stations'] if s.get('transfer'))
    if c['name'] in ('香港', '台北', '杭州', '昆明', '上海', '成都', '高雄'):
        print(f"  {c['name']}: {tr}/{tot} 站有换乘")

# 漏标复检
still = 0
for c in d['cities']:
    if not c.get('lines'): continue
    idx = collections.defaultdict(list)
    for l in c['lines']:
        for s in l['stations']:
            idx[norm(s['name'])].append((l, s))
    for key, group in idx.items():
        lns = {l['name'] for l, s in group}
        if len(lns) < 2: continue
        for l, s in group:
            if not s.get('transfer'):
                # 检查是否真有近距离同名
                if any(o[0]['name'] != l['name'] and dist_m(s, o[1]) < 1200 for o in group):
                    still += 1
print()
print('仍漏标:', still)