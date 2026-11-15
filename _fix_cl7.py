# -*- coding: utf-8 -*-
import io
p = 'CHANGELOG.md'
c = io.open(p, encoding='utf-8').read()
if '## [1.4.7]' in c:
    print('already present')
else:
    anchor = '## [1.4.6] — 2026-11-15'
    assert c.count(anchor) == 1, 'anchor: %d' % c.count(anchor)
    add = '''## [1.4.7] — 2026-11-15

- **深链增强**：`&theme=night/light` 与 `&layers=tombs,railways,...` 参数——城市 / 线路 / 桥梁 / 年份 / 视角 / 主题 / 图层七维场景状态全部分享直达；URL 仅在非默认时写入保持简洁
- README 深链示例同步更新

'''
    c = c.replace(anchor, add + anchor, 1)
    io.open(p, 'w', encoding='utf-8').write(c)
    print('changelog 1.4.7 written')
