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
                issues.append(f"{c['name']}/{s['name']}: 深度异常 {s.get('depth')}")
            if s['type'] == 'elevated' and not (3 <= (s.get('height') or 0) <= 40):
                issues.append(f"{c['name']}/{s['name']}: 高度异常 {s.get('height')}")

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
