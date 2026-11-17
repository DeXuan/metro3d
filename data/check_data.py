# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据质量自检
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

检查项：线路重名 / 线内站名重复 / 坐标越界 / 深度与高度异常 / opened 年份。
有问题时以非零码退出（CI 用）。
"""
import io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(io.open(os.path.join(ROOT, 'data', 'metro_all.json'), encoding='utf-8'))

issues = []
for c in d['cities']:
    names = [l['name'] for l in c.get('lines', [])]
    if len(names) != len(set(names)):
        issues.append(f"{c['name']}: 线路重名")
    for l in c.get('lines', []):
        sn = [s['name'] for s in l['stations']]
        if len(sn) != len(set(sn)):
            issues.append(f"{c['name']}/{l['name']}: 线内站名重复")
        if 'opened' in l and not (1900 <= l['opened'] <= 2030):
            issues.append(f"{c['name']}/{l['name']}: opened 年份异常 {l['opened']}")
        for s in l['stations']:
            if not (73 < s['lng'] < 136 and 3 < s['lat'] < 54):
                issues.append(f"{c['name']}/{s['name']}: 坐标越界")
            if s['type'] == 'underground' and not (5 <= (s.get('depth') or 0) <= 45):
                # 例外：公开资料实测的深埋站（如京张高铁八达岭长城站 102 米——
                # 世界最深高铁站），需 depthSource 标注来源方可放行
                ds_ok = isinstance(s.get('depthSource'), str) and s.get('depthSource').strip()
                if not ds_ok:
                    issues.append(f"{c['name']}/{s['name']}: 深度异常 {s.get('depth')}（>45m 需 depthSource 标注公开资料来源）")
            if s['type'] == 'elevated' and not (3 <= (s.get('height') or 0) <= 40):
                issues.append(f"{c['name']}/{s['name']}: 高度异常 {s.get('height')}")
            ds = s.get('depthSource')
            if ds is not None and not (isinstance(ds, str) and ds.strip()):
                issues.append(f"{c['name']}/{s['name']}: depthSource 需为非空字符串（URL 或文字说明）")

    # ---- 扩展字段：airports / railways / tombs / terrain / lakes ----
    for air in c.get('airports', []):
        if not (73 < air.get('lng', 0) < 136 and 3 < air.get('lat', 0) < 54):
            issues.append(f"{c['name']}/{air.get('name')}: 机场坐标越界")
        if not air.get('iata') or not air.get('note'):
            issues.append(f"{c['name']}/{air.get('name')}: 机场缺 iata/note")
    for r in c.get('railways', []):
        if not r.get('name') or len(r.get('points') or []) < 2:
            issues.append(f"{c['name']}: 铁路走廊缺 name/points")
            continue
        for x, y in r['points']:
            if not (73 < x < 136 and 3 < y < 54):
                issues.append(f"{c['name']}/{r['name']}: 走廊点越界"); break
        if r.get('year') and not (1900 <= r['year'] <= 2040):
            issues.append(f"{c['name']}/{r['name']}: year 异常 {r['year']}")
        if r.get('status') == 'building' and not r.get('year'):
            issues.append(f"{c['name']}/{r['name']}: 在建线路需标注预计开通年份")
    t = c.get('tombs')
    if t:
        for it in t.get('items', []):
            if not (73 < it.get('lng', 0) < 136 and 3 < it.get('lat', 0) < 54):
                issues.append(f"{c['name']}/{it.get('name')}: 墓葬坐标越界")
            if not it.get('era') or not it.get('intro'):
                issues.append(f"{c['name']}/{it.get('name')}: 墓葬缺 era/intro")
            if it.get('role') not in ('帝王', '名人'):
                issues.append(f"{c['name']}/{it.get('name')}: 墓葬 role 异常")
    for tr in [c['terrain']] if c.get('terrain') else []:
        for pk in tr.get('peaks') or []:
            if len(pk) != 4: issues.append(f"{c['name']}/{tr.get('name')}: peaks 字段数异常")
    for lk in c.get('lakes', []):
        if len(lk.get('points') or []) < 3:
            issues.append(f"{c['name']}/{lk.get('name')}: 湖泊点数不足")
    if c.get('climate') not in (None, 'snow'):
        issues.append(f"{c['name']}: climate 取值异常 {c.get('climate')}")

print('数据自检：城市 %d / 线路 %d / 站点 %d' % (
    len(d['cities']),
    sum(len(c.get('lines', [])) for c in d['cities']),
    sum(len(l['stations']) for c in d['cities'] for l in c.get('lines', []))))
if issues:
    print('发现问题 %d 处：' % len(issues))
    for i in issues[:30]:
        print('  -', i)
    sys.exit(1)
print('未发现问题 ✓')
