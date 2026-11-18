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
        # v2.2.0：先做类型守卫再比较——历史上 '2019' 字符串会让本行 TypeError 崩溃，
        # 校验器自身崩溃比数据缺陷更糟（CI 会误报为脚本错误而非数据错误）
        _op = l.get('opened')
        if _op is not None and (not isinstance(_op, int) or isinstance(_op, bool)):
            issues.append(f"{c['name']}/{l['name']}: opened 必须是整数（实际 {type(_op).__name__} {_op!r}）")
        elif _op is not None and not (1900 <= _op <= 2030):
            issues.append(f"{c['name']}/{l['name']}: opened 年份异常 {_op}")
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

# ---- v2.2.0 类型 schema 校验 ----
# 背景：历史上 opened 曾被写成字符串 '2019'，导致 check_data 自身比较时
# TypeError 崩溃、应用侧排序也异常。这里对关键字段做显式类型/枚举断言，
# 让数据问题在 CI 阶段暴露，而不是运行时。
CHANNEL_LIKE = {'id', 'name', 'color', 'from', 'to'}
STATION_TYPES = {'underground', 'elevated', 'ground'}
for c in d['cities']:
    if not isinstance(c.get('id'), str) or not c['id'].strip():
        issues.append(f"{c.get('name', '?')}: city.id 必须是非空字符串")
    if c.get('kind') not in (None, 'bridges'):
        issues.append(f"{c.get('name', '?')}: city.kind 取值异常 {c.get('kind')!r}")
    for key in ('lines', 'bridges'):
        v = c.get(key)
        if v is not None and not isinstance(v, list):
            issues.append(f"{c.get('name', '?')}: {key} 必须是数组（实际 {type(v).__name__}）")
    for li, l in enumerate(c.get('lines') or []):
        where = f"{c.get('name', '?')}/line[{li}]"
        if not isinstance(l.get('id'), str) or not l['id'].strip():
            issues.append(f"{where}: 线路 id 必须是非空字符串")
        if not isinstance(l.get('name'), str) or not l['name'].strip():
            issues.append(f"{where}: 线路 name 必须是非空字符串")
        col = l.get('color')
        if not isinstance(col, str) or not (col.startswith('#') and len(col) in (4, 7)):
            issues.append(f"{where}: color 必须是 #hex（实际 {col!r}）")
        if 'opened' in l and l['opened'] is not None:
            if not isinstance(l['opened'], int) or isinstance(l['opened'], bool):
                issues.append(f"{where}: opened 必须是整数（实际 {type(l['opened']).__name__} {l['opened']!r}）")
            elif not (1900 <= l['opened'] <= 2030):
                issues.append(f"{where}: opened 年份超出范围 {l['opened']}")
        if 'lengthKm' in l and not isinstance(l.get('lengthKm'), (int, float)):
            issues.append(f"{where}: lengthKm 必须是数字（实际 {type(l.get('lengthKm')).__name__}）")
        sts = l.get('stations')
        if not isinstance(sts, list) or not sts:
            issues.append(f"{where}: stations 必须是非空数组")
            continue
        for si, st in enumerate(sts):
            sw = f"{where}/st[{si}] {st.get('name', '?')}"
            if not isinstance(st.get('name'), str) or not st['name'].strip():
                issues.append(f"{sw}: 站名必须是非空字符串")
            if st.get('type') not in STATION_TYPES:
                issues.append(f"{sw}: type 必须是 {sorted(STATION_TYPES)} 之一（实际 {st.get('type')!r}）")
            for axis in ('lng', 'lat'):
                val = st.get(axis)
                if not isinstance(val, (int, float)) or isinstance(val, bool):
                    issues.append(f"{sw}: {axis} 必须是数字（实际 {type(val).__name__}）")
            if st.get('depth') is not None and not isinstance(st['depth'], (int, float)):
                issues.append(f"{sw}: depth 必须是数字（实际 {type(st.get('depth')).__name__}）")
            if st.get('height') is not None and not isinstance(st['height'], (int, float)):
                issues.append(f"{sw}: height 必须是数字（实际 {type(st.get('height')).__name__}）")
            tr = st.get('transfer')
            if tr is not None and not isinstance(tr, list):
                issues.append(f"{sw}: transfer 必须是数组（实际 {type(tr).__name__}）")
    # 桥梁字段
    for bi, b in enumerate(c.get('bridges') or []):
        bw = f"{c.get('name', '?')}/bridge[{bi}]"
        if not isinstance(b.get('name'), str) or not b['name'].strip():
            issues.append(f"{bw}: 桥名必须是非空字符串")
        if not isinstance(b.get('points'), list) or len(b['points']) < 2:
            issues.append(f"{bw}: points 至少 2 个点")
        if b.get('year') is not None and not isinstance(b.get('year'), int):
            issues.append(f"{bw}: year 必须是整数（实际 {type(b.get('year')).__name__}）")

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
