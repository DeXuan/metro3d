# -*- coding: utf-8 -*-
"""三项改进：①深链+分享面板 ②河流逐字标注 ③移动端顶部面板折叠"""
import io, re

HTML = 'index.html'
h = io.open(HTML, encoding='utf-8').read()

# ============ 1) CSS ============
extra_css = """
  /* ---------- 分享按钮 / 折叠按钮 ---------- */
  #panel-title h1{ position:relative; }
  .h1-tools{ margin-left:auto; display:flex; gap:4px; }
  .h1-btn{
    background:rgba(20,40,66,.7); border:1px solid var(--panel-border); color:var(--text-dim);
    border-radius:7px; width:26px; height:24px; font-size:12px; cursor:pointer; line-height:1;
    display:flex; align-items:center; justify-content:center; transition:all .15s; padding:0;
  }
  .h1-btn:hover{ color:var(--accent); border-color:rgba(79,194,232,.55); }
  #btn-title-toggle{ display:none; }

  /* ---------- 分享面板 ---------- */
  #share-panel{
    display:none; position:fixed; z-index:30; right:14px; top:14px; width:300px;
    max-width:calc(100vw - 28px);
  }
  #share-panel.show{ display:block; }
  .sh-head{ display:flex; align-items:center; margin-bottom:10px; }
  .sh-head b{ font-size:13px; flex:1; }
  .sh-head button{ background:none; border:0; color:var(--text-dim); font-size:14px; cursor:pointer; padding:2px 6px; }
  .sh-link{ display:flex; gap:6px; }
  .sh-link input{
    flex:1; min-width:0; background:rgba(12,26,44,.9); border:1px solid var(--panel-border);
    border-radius:7px; color:var(--text); font-size:11px; padding:6px 8px; outline:none;
  }
  .sh-link button{
    background:rgba(79,194,232,.16); border:1px solid rgba(79,194,232,.5); color:var(--accent);
    border-radius:7px; font-size:11px; padding:0 10px; cursor:pointer; white-space:nowrap;
  }
  .sh-qr{ margin-top:10px; text-align:center; }
  .sh-qr img{ width:150px; height:150px; border-radius:10px; background:#0a1626; border:1px solid var(--panel-border); }
  .sh-btns{ display:flex; gap:6px; margin-top:10px; }
  .sh-btns button{
    flex:1; background:rgba(20,40,66,.75); border:1px solid var(--panel-border); border-radius:7px;
    color:var(--text); font-size:11px; padding:7px 2px; cursor:pointer; transition:all .15s;
  }
  .sh-btns button:hover{ border-color:rgba(79,194,232,.55); color:var(--accent); }
  .sh-tip{ margin-top:8px; font-size:10.5px; color:var(--text-dim); line-height:1.55; min-height:14px; }

  /* ---------- 移动端：顶部面板折叠 ---------- */
  @media (max-width: 860px){
    #panel-title{ padding:8px 10px; transition:max-height .25s ease; }
    #panel-title h1{ font-size:13px; gap:6px; }
    #panel-title h1 .dot{ width:8px; height:8px; }
    #panel-title .sel-row{ margin-top:7px; }
    #panel-title.collapsed #stat-line,
    #panel-title.collapsed #legend{ display:none; }
    #btn-title-toggle{ display:flex; }
    #share-panel{ left:14px; right:14px; top:auto; bottom:76px; width:auto; }
  }
"""
h = h.replace('</style>', extra_css + '</style>', 1)

# ============ 2) HTML ============
old_h1 = '''  <h1><span class="dot"></span>城市地铁 · 地下三维视图</h1>'''
assert old_h1 in h
h = h.replace(old_h1, '''  <h1><span class="dot"></span>城市地铁 · 地下三维视图
    <span class="h1-tools">
      <button class="h1-btn" id="btn-share" title="分享当前视图">⤴</button>
      <button class="h1-btn" id="btn-title-toggle" title="展开/收起详情">▾</button>
    </span>
  </h1>''')

# 分享面板 HTML（插在 info-card 之后）
old_ic = '''<button id="btn-list-float" title="展开站点列表">'''
assert old_ic in h
share_html = '''<div id="share-panel" class="panel">
  <div class="sh-head"><b>分享当前视图</b><button id="sh-close">✕</button></div>
  <div class="sh-link"><input id="sh-url" readonly><button id="sh-copy">复制链接</button></div>
  <div class="sh-qr"><img id="sh-qr-img" alt="扫码打开" referrerpolicy="no-referrer"></div>
  <div class="sh-btns">
    <button data-sh="weibo">微博</button>
    <button data-sh="wechat">微信/朋友圈</button>
    <button data-sh="xhs">小红书</button>
  </div>
  <div class="sh-tip" id="sh-tip">链接会带上当前城市与线路。</div>
</div>

<button id="btn-list-float" title="展开站点列表">'''
h = h.replace(old_ic, share_html, 1)

# ============ 3) JS：深链 + 分享 + 折叠 ============
anchor = """populateSelectors();
rebuild();
setListCollapsed(true);"""
assert anchor in h
new_boot = """/* ---------------- 深链：?city=shanghai&line=sh-9 ---------------- */
(function applyDeepLink(){
  try {
    const qp = new URLSearchParams(location.search);
    const cid = qp.get('city');
    if (cid && METRO_DATA.cities.some(c => c.id === cid)) state.cityId = cid;
    const ln = qp.get('line');
    if (ln) state.focusLineId = ln;
  } catch(e){}
})();

function syncUrl(){
  try {
    const u = new URL(location.href);
    if (state.cityId) u.searchParams.set('city', state.cityId);
    if (state.focusLineId && state.focusLineId !== '__all__') u.searchParams.set('line', state.focusLineId);
    else u.searchParams.delete('line');
    if (u.search !== location.search) history.replaceState(null, '', u.toString());
  } catch(e){}
}

populateSelectors();
rebuild();
setListCollapsed(true);
// 移动端：顶部详情默认折叠，给 3D 视图让出空间
if (window.matchMedia('(max-width: 860px)').matches){
  document.getElementById('panel-title').classList.add('collapsed');
}

/* ---------------- 分享面板 ---------------- */
(function sharePanel(){
  const panel = document.getElementById('share-panel');
  const urlInput = document.getElementById('sh-url');
  const qrImg = document.getElementById('sh-qr-img');
  const tip = document.getElementById('sh-tip');
  const sync = () => {
    const url = location.href;
    urlInput.value = url;
    qrImg.src = 'https://api.qrserver.com/v1/create-qr-code/?size=220x220&margin=8&data=' + encodeURIComponent(url);
    qrImg.onerror = () => { qrImg.style.display = 'none'; };
  };
  document.getElementById('btn-share').addEventListener('click', () => {
    sync();
    panel.classList.add('show');
    $('panel-ctrl').classList.remove('show');
    $('panel-list').classList.remove('show');
  });
  document.getElementById('sh-close').addEventListener('click', () => panel.classList.remove('show'));
  document.getElementById('sh-copy').addEventListener('click', async () => {
    const url = location.href;
    let ok = false;
    try { await navigator.clipboard.writeText(url); ok = true; } catch(e){}
    if (!ok){
      urlInput.select();
      try { ok = document.execCommand('copy'); } catch(e){}
    }
    tip.textContent = ok ? '✅ 链接已复制，可粘贴到微信 / 小红书' : '复制失败，请长按输入框手动复制';
  });
  panel.querySelectorAll('.sh-btns button').forEach(btn => {
    btn.addEventListener('click', async () => {
      const type = btn.dataset.sh;
      const url = location.href;
      const title = '城市地铁与超级桥梁 · 三维立体视图';
      if (type === 'weibo'){
        window.open('https://service.weibo.com/share/share.php?url=' + encodeURIComponent(url) +
          '&title=' + encodeURIComponent(title), '_blank', 'noopener');
      } else if (type === 'wechat'){
        try { await navigator.clipboard.writeText(url); } catch(e){}
        tip.textContent = '微信/朋友圈：链接已复制。粘贴到微信聊天或朋友圈即可（微信内分享卡片需公众号授权，当前为链接形式）。';
      } else {
        try { await navigator.clipboard.writeText(url); } catch(e){}
        tip.textContent = '小红书：链接已复制。小红书暂不支持网页直接分享，粘贴到笔记里的「添加链接」即可。';
      }
    });
  });
})();

/* ---------------- 移动端顶部面板折叠 ---------------- */
document.getElementById('btn-title-toggle').addEventListener('click', () => {
  const el = document.getElementById('panel-title');
  el.classList.toggle('collapsed');
  el.querySelector('#btn-title-toggle').textContent = el.classList.contains('collapsed') ? '▾' : '▴';
});"""
h = h.replace(anchor, new_boot, 1)

# rebuild 末尾同步 URL
old_rebuild = """  if (doFit) fitAll();
  buildUIList();
  updateStats();
  updateLegend();
}"""
if old_rebuild in h:
    h = h.replace(old_rebuild, """  if (doFit) fitAll();
  buildUIList();
  updateStats();
  updateLegend();
  syncUrl();
}""", 1)

# ============ 4) 河流逐字标注 ============
old_label = """    // 4) 河名标注（沿江均匀放 2~3 处）
    if (seg.n){
      const nLabels = seg.n.length > 0 ? Math.min(3, Math.max(2, Math.round(pts.length / 40))) : 0;
      for (let k = 1; k <= nLabels; k++){
        const u = k / (nLabels + 1);
        const p = curve.getPointAt(u);
        const lb = makeLabel(seg.n, '', '#bfe4ff');
        lb.scale.set(17, 5.4, 1);
        lb.position.set(p.x, 1.2, p.z);
        grp.add(lb);
      }
    }"""
assert old_label in h
new_label = """    // 4) 河名标注：逐字沿河道排布（参考地图河流注记），字距拉开、字号加大
    if (seg.n){
      const chars = [...seg.n];
      const longName = chars.length >= 4;              // 维多利亚港等长名
      const gapU = longName ? 0.020 : 0.030;           // 沿曲线的字距
      const centers = longName ? [0.42] : [0.30, 0.68]; // 长名单处，短名两处（地图习惯）
      centers.forEach(cu => {
        chars.forEach((ch, i) => {
          const u = cu + (i - (chars.length - 1) / 2) * gapU;
          const uu = Math.min(0.985, Math.max(0.015, u));
          const p = curve.getPointAt(uu);
          const lb = makeRiverChar(ch);
          lb.position.set(p.x, 1.6, p.z);
          grp.add(lb);
        });
      });
    }"""
h = h.replace(old_label, new_label, 1)

# 插入 makeRiverChar（在 makeLabel 之后）
old_mk = """function makeRiverChar(ch){"""
if old_mk not in h:
    anchor2 = "/* ---------- 黄浦江"
    assert anchor2 in h
    h = h.replace(anchor2, """/* ---------- 河流单字标注（大字号，逐字沿河排布） ---------- */
function makeRiverChar(ch){
  const dpr = 2, S = 128;
  const cv = document.createElement('canvas');
  cv.width = S * dpr; cv.height = S * dpr;
  const ctx = cv.getContext('2d');
  ctx.scale(dpr, dpr);
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = '600 96px "PingFang SC","Microsoft YaHei",sans-serif';
  ctx.lineWidth = 9; ctx.strokeStyle = 'rgba(3,12,24,.88)';
  ctx.strokeText(ch, S / 2, S / 2 + 4);
  ctx.fillStyle = '#d3ecff';
  ctx.fillText(ch, S / 2, S / 2 + 4);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({
    map: tex, transparent: true, depthTest: false, depthWrite: false }));
  sp.renderOrder = 900;
  sp.userData.alwaysVisible = true;
  sp.scale.set(13, 13, 1);
  return sp;
}

/* ---------- 黄浦江""", 1)

io.open(HTML, 'w', encoding='utf-8').write(h)
print('all three improvements applied, size:', len(h))
scripts = re.findall(r'<script type="module">(.*?)</script>', h, re.S)
for i, s in enumerate(scripts):
    io.open('_chk%d.mjs' % i, 'w', encoding='utf-8').write(s)
print('scripts:', len(scripts))