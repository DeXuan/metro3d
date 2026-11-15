# -*- coding: utf-8 -*-
import io, re

h = io.open('index.html', encoding='utf-8').read()
a = re.findall(r'<script type="module">(.*?)</script>', h, re.S)[1]
assert 'pinnedProfile' not in a, 'already patched'

# ---------- 1) 钉住状态 ----------
old = "let profileUserHide = false;"
assert a.count(old) == 1, 'K1'
a = a.replace(old, "let profileUserHide = false;\nlet pinnedProfile = null;   // 📌 钉住的对比线路（跨城市可对比埋深）")

# ---------- 2) drawProfile 支持对比层（钉住线淡色 + 当前线主色） ----------
old = "function drawProfile(line){\n  const cv = $('profile-canvas');"
assert a.count(old) == 1, 'K2'
a = a.replace(old, """function drawProfile(line){
  const cv = $('profile-canvas');
  const P = pinnedProfile;
  // 标题带对比说明
  $('pf-title').textContent = line.name + ' · 纵断面' +
    (P && P.line !== line ? `（对比：${P.label}）` : '');
  drawProfileLayer(cv, line, line.color || '#4FC2E8', false);
  if (P && P.line !== line) drawProfileLayer(cv, P.line, P.color, true);
}

function drawProfileLayer(cv, line, col, dim){
  const W = cv.width / Math.min(devicePixelRatio || 1, 2), H = cv.height / Math.min(devicePixelRatio || 1, 2);
  const ctx = cv.getContext('2d');""")
# 原 drawProfile 主体用局部 W/H/ctx——改造后保留主体但去掉重复声明
old = """  const W = cv.width / Math.min(devicePixelRatio || 1, 2), H = cv.height / Math.min(devicePixelRatio || 1, 2);
  const ctx = cv.getContext('2d');"""
# 上面的 replace 已把 drawProfileLayer 头接上了原主体的开头（W/H/ctx）——需要删除主体里的重复 W/ctx 声明
old_dup = """function drawProfileLayer(cv, line, col, dim){
  const W = cv.width / Math.min(devicePixelRatio || 1, 2), H = cv.height / Math.min(devicePixelRatio || 1, 2);
  const ctx = cv.getContext('2d');
  const W = cv.width / Math.min(devicePixelRatio || 1, 2), H = cv.height / Math.min(devicePixelRatio || 1, 2);
  const ctx = cv.getContext('2d');"""
if a.count(old_dup) == 1:
    a = a.replace(old_dup, """function drawProfileLayer(cv, line, col, dim){
  const W = cv.width / Math.min(devicePixelRatio || 1, 2), H = cv.height / Math.min(devicePixelRatio || 1, 2);
  const ctx = cv.getContext('2d');""")

h = h.replace(re.findall(r'<script type="module">(.*?)</script>', h, re.S)[1], a)
io.open('index.html', 'w', encoding='utf-8').write(h)
app = re.findall(r'<script type="module">(.*?)</script>', h, re.S)[1]
io.open('_c.mjs', 'w', encoding='utf-8').write(app)
print('profile compare stage 1')
