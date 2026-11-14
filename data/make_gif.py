# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— README 首屏动图生成
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

把 docs/screenshots 下的截图合成 Ken Burns 式动图（缓慢推拉 + 交叉溶解）。
用法：python data/make_gif.py   → 输出 docs/screenshots/hero.gif
"""
import io, os
from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'docs', 'screenshots')
OUT = os.path.join(SRC, 'hero.gif')

W, H = 640, 341          # 输出尺寸
PER_SHOT = 1.0           # 每图秒数
FPS = 7
ZOOM = 0.10              # 最大推近比例
DISSOLVE = 4             # 交叉溶解帧数

SHOTS = [
    ('overview-shanghai.jpg', '53 城地铁线网 · 真实经纬度投影'),
    ('hzmb-water.png',        '超级桥梁 · 港珠澳大桥'),
    ('wuhan-hsr-cross.png',   '全国高铁网络 · 银白干线'),
    ('luoyang-panorama.png',  '洛阳 · 邙山古墓群 / 城市地形'),
    ('beipanjiang-valley.png','跨山谷桥 · 北盘江大桥'),
    ('zhengzhou-hub.png',     '郑州 · 米字高铁枢纽'),
]

def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    nw, nh = int(im.width * s) + 1, int(im.height * s) + 1
    im = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2; y = (nh - h) // 2
    return im.crop((x, y, x + w, y + h))

def kenburns(im, f):
    """f: 0..1，从全幅缓慢推近 + 微移"""
    zoom = 1.0 + ZOOM * f
    iw, ih = im.size
    cw, ch = int(iw / zoom), int(ih / zoom)
    dx = int((iw - cw) * f * 0.6)
    dy = int((ih - ch) * f * 0.4)
    win = im.crop((dx, dy, dx + cw, dy + ch))
    return win.resize((W, H), Image.LANCZOS)

def label(im, text):
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    d.rectangle([12, H - 40, 12 + 10 * len(text) + 16, H - 12], fill=(8, 18, 34))
    d.text((22, H - 34), text, fill=(220, 234, 247))
    return im

frames = []
for k, (fn, cap) in enumerate(SHOTS):
    path = os.path.join(SRC, fn)
    if not os.path.exists(path):
        print('跳过缺失素材:', fn); continue
    im = Image.open(path).convert('RGB')
    im = cover(im, 1600, 900)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    n = int(PER_SHOT * FPS)
    for f in range(n):
        fr = kenburns(im, f / max(1, n - 1))
        fr = label(fr, cap)
        if frames and f < DISSOLVE:                       # 交叉溶解
            a = f / DISSOLVE
            fr = Image.blend(frames[-1], fr, a)
        frames.append(fr)
    if k == 0:                                            # 首尾定格，循环更顺
        frames = [frames[0]] * 3 + frames
frames += [frames[-1]] * 3

print('总帧数:', len(frames))
qframes = [f.convert('P', palette=Image.ADAPTIVE, colors=64) for f in frames]
qframes[0].save(OUT, save_all=True, append_images=qframes[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print('输出:', OUT, '%.2f MB' % (os.path.getsize(OUT) / 1048576))
