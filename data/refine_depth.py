# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

免责声明：本脚本生成的数据仅供可视化演示与学习参考，禁止用于工程、施工、
测绘、导航或军事等专业用途。生成的埋深为示意值（非实测数据）。
详见 README「数据精度与使用限制」。

深度精修：让所有城市呈现合理的埋深起伏

规律：
  1) 换乘站加深（换乘通道/多层站台）
  2) 靠近水体（河流/海湾）的站加深（越江/临江段常深埋）
  3) 线路首末站略浅（端头常为浅埋或高架接驳）
  4) 城市基准深度按线龄：老线浅、新线深
  5) 手工城市（台北/桃园/高雄/澳门）按真实线路特征逐线基准 + 站级变化
"""
import json, math, hashlib

p = 'data/metro_all.json'
d = json.load(open(p, encoding='utf-8'))

def h01(name, salt=''):
    return int(hashlib.md5((name + salt).encode('utf-8')).hexdigest()[:6], 16) / 0xFFFFFF

# ---------- 手工城市：逐线基准深度（按真实工程特征） ----------
MANUAL_BASE = {
 # 台北：板南线浅（B1-B2，16-20m）、淡水信义线深（跨淡水河/台北盆地，20-30m）、
 #       松山新店线中等、中和新芦线深（跨河+台地）、文湖线高架为主（保留少量地下）
 '板南线': (15, 4.5),
 '淡水信义线': (22, 6.0),
 '松山新店线': (18, 4.0),
 '中和新芦线': (24, 5.5),
 '文湖线': (13, 3.0),
 # 桃园机场捷运：台北段深（市区地下 25-30m），机场段浅
 '机场捷运': (20, 7.0),
 # 高雄：红线浅（12-18m），橘线中等（15-22m，跨爱河）
 '红线': (15, 4.0),
 '橘线': (18, 4.5),
 # 澳门氹仔线：全高架为主，少量地下
 '氹仔线': (10, 2.5),
}

lines_by_name = {}
for c in d['cities']:
    for l in c.get('lines', []):
        lines_by_name.setdefault(l['name'], []).append((c, l))

# ---------- 城市水体位置（用于"近水加深"） ----------
def river_dist(city, lng, lat):
    """返回站点到该城河流中心线的最近距离（度）"""
    rv = city.get('river')
    if not rv or not rv.get('points'):
        return 999
    best = 999
    for pt in rv['points']:
        dd = math.hypot(lng - pt[0], (lat - pt[1]) * 0.8)
        if dd < best: best = dd
    return best

stats = []
for c in d['cities']:
    if not c.get('lines'):
        continue
    lines = c['lines']
    for l in lines:
        sts = l['stations']
        # 线路基准
        if l['name'] in MANUAL_BASE and c['id'] in ('taibei', 'taoyuan', 'gaoxiong', 'aomen'):
            base, spread = MANUAL_BASE[l['name']]
        else:
            deps = [s['depth'] for s in sts if s['type'] == 'underground' and s.get('depth')]
            if not deps:
                continue
            base = sum(deps) / len(deps)
            spread = max(2.5, (max(deps) - min(deps)) * 0.9)
        n = len(sts)
        for i, s in enumerate(sts):
            if s['type'] != 'underground':
                continue
            # 1) 站级确定性抖动（幅度更大，体现地质/施工差异）
            v = base + (h01(s['name'], l['id']) - 0.5) * 2 * spread
            # 2) 换乘站加深 3~6m（多层站台/换乘通道）
            if s.get('transfer'):
                v += 2.5 + h01(s['name'], 'tr') * 4.0
            # 3) 近水加深（越江/滨江段常深埋，最多 +7m）
            rd = river_dist(c, s['lng'], s['lat'])
            if rd < 0.020:
                v += (1 - rd / 0.020) * 7.0
            # 4) 首末站略浅（端头常接高架/地面）
            if i == 0 or i == n - 1:
                v -= 2.0 + h01(s['name'], 'end') * 1.5
            # 5) 轻轨/高架主导线路不做地下深埋
            if '云轨' in l['name'] or '单轨' in l['name']:
                v = min(v, 12)
            s['depth'] = round(max(6.0, min(42.0, v)), 1)

    # 统计
    deps = [s['depth'] for l in lines for s in l['stations'] if s['type'] == 'underground']
    if len(deps) >= 3:
        stats.append((c['name'], len(deps), min(deps), max(deps), round(max(deps) - min(deps), 1)))

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
stats.sort(key=lambda r: r[4])
print('埋深极差最小 8 城:')
for r in stats[:8]:
    print(f'  {r[0]:<6} {r[1]:>4}站  {r[2]:>5.1f}~{r[3]:>5.1f}  极差{r[4]:>5.1f}m')
print('埋深极差最大 4 城:')
for r in stats[-4:]:
    print(f'  {r[0]:<6} {r[1]:>4}站  {r[2]:>5.1f}~{r[3]:>5.1f}  极差{r[4]:>5.1f}m')
print('\n台北示例（板南线前 8 站深度）:')
tp = next(c for c in d['cities'] if c['id'] == 'taibei')
ban = next(l for l in tp['lines'] if l['name'] == '板南线')
print(' ', [(s['name'], s['depth']) for s in ban['stations'][:8]])
print('\n台中/滁州（手工新增）:')
for cid in ('taizhong', 'chuzhou'):
    c = next((x for x in d['cities'] if x['id'] == cid), None)
    if c:
        deps = [s['depth'] for l in c['lines'] for s in l['stations'] if s['type'] == 'underground']
        print(f'  {c["name"]}: {deps[:8]}')