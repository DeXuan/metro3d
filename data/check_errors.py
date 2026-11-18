# -*- coding: utf-8 -*-
"""T4b: check_errors —— 静默失败门禁（仅审计自有业务代码，跳过第三方与门户补丁层）

范围：只扫描业务模块（`/* ---------------- 数据（由 generate 脚本注入）` 之后、
      到 `</script>` 结束前的自有代码），并排除 Three.js 内联段与 v2 门户补丁层。
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
h = io.open(HTML, encoding='utf-8').read()

def business_segment(src):
    """截取自有业务代码：从数据块注释起，到最后一个业务 </script> 前。"""
    start_marker = '/* ---------------- 数据（由 generate 脚本注入） ---------------- */'
    i = src.find(start_marker)
    if i < 0:
        return ''
    j = src.find('</script>', i)
    return src[i:j if j > 0 else len(src)]

biz = business_segment(h)
if not biz:
    print('[check_errors] 无法定位业务代码段'); sys.exit(1)

issues, warns = [], []
offset = h.find(biz)

empty_catch = re.compile(r'catch\s*(?:\(\s*[A-Za-z_$][\w$]*\s*\))?\s*\{\s*(?://[^\n]*\s*)?\}')
for m in empty_catch.finditer(biz):
    ln = h[:offset + m.start()].count('\n') + 1
    ctx = biz[max(0, m.start() - 120):m.start()]
    if '__recErr' in ctx:
        continue
    snippet = biz[max(0, m.start() - 50):m.end() + 8].replace('\n', ' ')
    issues.append(f'空 catch 吞异常（行 {ln}）: …{snippet.strip()[-64:]}')

catch_blocks = re.compile(r'catch\s*(?:\(\s*([A-Za-z_$][\w$]*)\s*\))?\s*\{([^{}]{0,200})\}', re.S)
for m in catch_blocks.finditer(biz):
    body = (m.group(2) or '').strip()
    if not body or '__recErr' in body or body.startswith('//'):
        continue
    ln = h[:offset + m.start()].count('\n') + 1
    if 'console.' in body:
        warns.append(f'catch 仅 console 未入错误缓冲（行 {ln}）')
    elif re.search(r'localStorage|clipboard|JSON\.parse|navigator\.', body):
        warns.append(f'catch 静默忽略 I/O 异常（行 {ln}）')

print(f'[check_errors] 业务代码 {len(biz)//1024} KB · 静默失败门禁')
if warns:
    print(f'提示 {len(warns)} 处（不阻断）：')
    for w in warns[:10]:
        print('  ~', w)
if issues:
    print(f'发现阻断问题 {len(issues)} 处：')
    for i in issues[:12]:
        print('  -', i)
    sys.exit(1)
# 收集器可能定义在业务段之前，故全文检索
if '__errbuf' not in h:
    print('  - 缺失全局错误环形缓冲 __errbuf（v2.2.0 起必须存在）')
    sys.exit(1)
if "__recErr" not in h:
    print('  - 缺失 __recErr 记录函数')
    sys.exit(1)
print('未发现静默吞错 ✓')