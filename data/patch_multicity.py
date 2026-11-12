# -*- coding: utf-8 -*-
"""多城市补丁（干净版）：五城数据 + 环线 + 城市名 + 河流/建筑群 + 滑块节流"""
import io, json, re

HTML = 'index.html'
h = io.open(HTML, encoding='utf-8').read()
app = re.findall(r'<script type="module">(.*?)</script>', h, re.S)[1]
orig_len = len(app)
steps = []

def rep(old, new, tag):
    global app
    assert old in app, 'MISS: ' + tag
    app = app.replace(old, new)
    steps.append(tag)

# ---------- 1) METRO_DATA ----------
metro = json.load(open('../_data4/metro_all.json', encoding='utf-8'))
blob = json.dumps(metro, ensure_ascii=False, separators=(',', ':'))
i0 = app.index('const METRO_DATA = ')
i1 = app.index(';\n', app.index('"cities"', i0))
app = app[:i0] + 'const METRO_DATA = ' + blob + app[i1:]
steps.append('METRO_DATA')

# ---------- 2) 环线闭合 ----------
rep("const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal');",
    "const curve = new THREE.CatmullRomCurve3(pts, !!line.loop, 'centripetal');", 'curve-loop')
rep("new THREE.TubeGeometry(new THREE.CatmullRomCurve3(flat,false,'centripetal')",
    "new THREE.TubeGeometry(new THREE.CatmullRomCurve3(flat,!!line.loop,'centripetal')", 'flat-loop')

# ---------- 3) 统计城市名 ----------
rep("<b>上海轨道交通线网</b> · ${w.lines.length} 条线路 · ${totalSt} 座车站",
    "<b>${w.city.name}轨道交通线网</b> · ${w.lines.length} 条线路 · ${totalSt} 座车站", 'stats-city')

# ---------- 4) 环线显示 ----------
rep("opts.push(`<option value=\"${lineObjKey(l)}\">${l.name} · ${l.from}—${l.to}</option>`);",
    "opts.push(`<option value=\"${lineObjKey(l)}\">${l.name} · ${l.loop ? '环线' : l.from + '—' + l.to}</option>`);", 'sel-loop')
rep("""    ? `<b>${focus.name}</b> · ${focus.from} ↔ ${focus.to} · 约 ${focus.lengthKm} km<br>` +""",
    """    ? `<b>${focus.name}</b> · ${focus.loop ? '环线' : focus.from + ' ↔ ' + focus.to} · 约 ${focus.lengthKm} km<br>` +""", 'stat-loop')

# ---------- 5) 滑块节流 ----------
rep("""$('vscale').addEventListener('input', e => {
  const v = +e.target.value;
  $('vscale-val').textContent = v + '×';
  V_SCALE = v * H_SCALE;
  rebuild(true);
});""",
"""let vscaleTimer = null;
$('vscale').addEventListener('input', e => {
  const v = +e.target.value;
  $('vscale-val').textContent = v + '×';
  V_SCALE = v * H_SCALE;
  clearTimeout(vscaleTimer);
  vscaleTimer = setTimeout(() => rebuild(true), 160);
});""", 'vscale-throttle')

# ---------- 6) buildBuildings 重写：沿线生成 ----------
start = app.index('function buildBuildings(origin){')
end = app.index('\n/* ---------- 构建整网 ---------- */')
new_fn = """function buildBuildings(origin, lines){
  const rng = mulberry32(20261112);
  const items = [];
  lines.forEach(l => l.stations.forEach(s => {
    if (rng() > 0.5) return;
    const n = 1 + Math.floor(rng() * 3);
    for (let i = 0; i < n; i++){
      const plng = s.lng + (rng() - .5) * .0075;
      const plat = s.lat + (rng() - .5) * .0060;
      const tall = rng() * rng();
      items.push([plng, plat, 10 + tall * 150, 30 + rng() * 75]);
    }
  }));
  if (!items.length) return new THREE.Group();
  const geo = new THREE.BoxGeometry(1,1,1); geo.translate(0,.5,0);
  const mat = new THREE.MeshStandardMaterial({ color: 0x2f4f74, roughness: .85, metalness: .1,
    emissive: 0x12294a, emissiveIntensity: 1.0 });
  const mesh = new THREE.InstancedMesh(geo, mat, items.length);
  const M = new THREE.Matrix4();
  items.forEach(([lng,lat,hM,fM],i) => {
    const p = project(lng,lat,origin);
    M.makeScale(fM*H_SCALE, hM*H_SCALE*6.5, fM*H_SCALE);
    M.setPosition(p.x, 0, p.z);
    mesh.setMatrixAt(i, M);
  });
  mesh.instanceMatrix.needsUpdate = true;
  return mesh;
}
"""
app = app[:start] + new_fn + app[end:]
steps.append('buildings-fn')

# ---------- 7) 河流按城市 + 建筑群调用 ----------
rep("""const RIVER_LINE = [
  [121.4890,31.1550],[121.4920,31.1800],[121.4952,31.2030],[121.4995,31.2180],
  [121.5035,31.2330],[121.5085,31.2520],[121.5150,31.2720],[121.5235,31.2930],[121.5350,31.3150]
];
function buildRiver(origin){""",
"""function buildRiver(origin, city){
  const cfg = city && city.river;
  if (!cfg || !cfg.points || cfg.points.length < 2) return null;
  const widthM = cfg.widthM || 500;""", 'river-fn')

rep("const w = 0.0032 * 111320 * Math.cos(origin.lat*Math.PI/180) * H_SCALE;",
    "const wScene = (widthM / 2) * H_SCALE;", 'river-width')
rep("verts.push(p.clone().addScaledVector(n,-w), p.clone().addScaledVector(n,w));",
    "verts.push(p.clone().addScaledVector(n,-wScene), p.clone().addScaledVector(n,wScene));", 'river-verts')
rep("grouped.add(buildRiver(origin));",
    "const river = buildRiver(origin, city);\n    if (river) grouped.add(river);\n    grouped.add(buildBuildings(origin, lines));", 'river-call+buildings')

# ---------- 写回 ----------
prefix = h[:h.rindex('<script type="module">')]
suffix = h[h.rindex('</script>') + len('</script>'):]
out = prefix + '<script type="module">' + app + '</script>' + suffix
io.open(HTML, 'w', encoding='utf-8').write(out)
print('OK steps:', steps)
print('size:', len(out), '| city beijing:', '"beijing"' in out)
scripts = re.findall(r'<script type="module">(.*?)</script>', out, re.S)
for i, s in enumerate(scripts):
    io.open('_chk%d.mjs' % i, 'w', encoding='utf-8').write(s)
print('scripts:', len(scripts))