# -*- coding: utf-8 -*-
"""黄浦江等水系参考层增强：
- 江面加宽加亮、岸线描边
- 沿江中线发光参考轨迹
- 河名标注（沿江多处）
- 支持 cfg.branches 多支流/多江段
"""
import io, re, json

HTML = 'index.html'
h = io.open(HTML, encoding='utf-8').read()
app = re.findall(r'<script type="module">(.*?)</script>', h, re.S)[1]

start = app.index('function buildRiver(origin, city){')
end = app.index('/* ---------- 城市天际线')

new_fn = '''function buildRiver(origin, city){
  const cfg = city && city.river;
  if (!cfg || !cfg.points || cfg.points.length < 2) return null;

  const kx = 111320 * Math.cos(origin.lat*Math.PI/180) * H_SCALE;
  const kz = 110540 * H_SCALE;
  const grp = new THREE.Group();
  const name = cfg.name || '河流';

  // 逐条水系（主线 + 可选支流）
  const segs = [{ pts: cfg.points, w: cfg.widthM || 500, n: name }]
    .concat((cfg.branches || []).map(b => ({ pts: b.points, w: b.widthM || 300, n: b.name || '' })));

  segs.forEach(seg => {
    if (!seg.pts || seg.pts.length < 2) return;
    const ctr = seg.pts.map(([lng,lat]) =>
      new THREE.Vector3((lng-origin.lng)*kx, 0.06, -(lat-origin.lat)*kz));
    // 平滑：加密采样，让轨迹更自然
    const curve = new THREE.CatmullRomCurve3(ctr, false, 'centripetal');
    const N = Math.max(40, ctr.length * 6);
    const pts = [];
    for (let i = 0; i <= N; i++) pts.push(curve.getPointAt(i / N));
    const wScene = (seg.w / 2) * H_SCALE;

    // 1) 江面（带状三角面）
    const verts = [], idx = [];
    pts.forEach((p, i) => {
      const a = pts[Math.max(0, i-1)], b = pts[Math.min(pts.length-1, i+1)];
      const dir = new THREE.Vector3().subVectors(b, a).normalize();
      const n = new THREE.Vector3(-dir.z, 0, dir.x);
      verts.push(p.clone().addScaledVector(n, -wScene), p.clone().addScaledVector(n, wScene));
    });
    for (let i = 0; i < pts.length - 1; i++){
      const l = i*2, r = i*2+1;
      idx.push(l, l+2, r, r, l+2, r+2);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(verts.flatMap(v=>[v.x,v.y,v.z]), 3));
    g.setIndex(idx);
    const water = new THREE.Mesh(g, new THREE.MeshBasicMaterial({
      color: cfg.color || 0x1d6494, transparent: true, opacity: 0.72,
      depthWrite: false, side: THREE.DoubleSide }));
    water.renderOrder = 1;
    grp.add(water);

    // 2) 岸线描边（两侧轮廓）
    [-1, 1].forEach(side => {
      const edge = [];
      pts.forEach((p, i) => {
        const a = pts[Math.max(0, i-1)], b = pts[Math.min(pts.length-1, i+1)];
        const dir = new THREE.Vector3().subVectors(b, a).normalize();
        const n = new THREE.Vector3(-dir.z, 0, dir.x);
        edge.push(p.clone().addScaledVector(n, side * wScene).setY(0.12));
      });
      const eg = new THREE.BufferGeometry().setFromPoints(
        edge.flatMap((p, i) => (i < edge.length - 1 ? [p, edge[i+1]] : [])));
      grp.add(new THREE.LineSegments(eg, new THREE.LineBasicMaterial({
        color: cfg.edgeColor || 0x4d9fd0, transparent: true, opacity: 0.55 })));
    });

    // 3) 中线发光参考轨迹
    const cg = new THREE.BufferGeometry().setFromPoints(
      pts.flatMap((p, i) => (i < pts.length - 1 ? [p.clone().setY(0.18), pts[i+1].clone().setY(0.18)] : [])
    ));
    grp.add(new THREE.LineSegments(cg, new THREE.LineBasicMaterial({
      color: cfg.centerColor || 0x8fd8ff, transparent: true, opacity: 0.5 })));

    // 4) 河名标注（沿江均匀放 2~3 处）
    if (seg.n){
      const nLabels = seg.n.length > 0 ? Math.min(3, Math.max(2, Math.round(pts.length / 40))) : 0;
      for (let k = 1; k <= nLabels; k++){
        const u = k / (nLabels + 1);
        const p = curve.getPointAt(u);
        const lb = makeLabel(seg.n, '', '#bfe4ff');
        lb.scale.set(13, 4.2, 1);
        lb.position.set(p.x, 1.2, p.z);
        grp.add(lb);
      }
    }
  });

  groupLabelLayer(grp);
  return grp;
}

/* 河流标注需在标签 LOD 之外常显，单独标记 */
function groupLabelLayer(grp){
  grp.traverse(o => { if (o.isSprite) o.userData.alwaysVisible = true; });
}

'''

app = app[:start] + new_fn + app[end:]

# 标签 LOD 跳过水系常显标注
old_lod = """      lb.visible = false;
      if (!state.labels) return;"""
assert old_lod in app, 'lod block not found'
app = app.replace(old_lod, """      if (lb.userData.alwaysVisible){ lb.visible = true; return; }
      lb.visible = false;
      if (!state.labels) return;""")

# 水系开关：并入「地层参考面」按钮语义 → 改为水元素也受控于该按钮？保持常显更符合"参考"
print('buildRiver rewritten')

io.open(HTML, 'w', encoding='utf-8').write(
    h[:h.rindex('<script type="module">')] + '<script type="module">' + app + '</script>' +
    h[h.rindex('</script>') + len('</script>'):])

# ---------- 数据层：升级河流配置 ----------
dpath = 'data/metro_all.json'
data = json.load(open(dpath, encoding='utf-8'))

def densify(points, step=0.006):
    """线性插值加密河道点，让曲线更平滑"""
    out = [points[0]]
    for a, b in zip(points, points[1:]):
        d = ((b[0]-a[0])**2 + (b[1]-a[1])**2) ** 0.5
        n = max(1, int(d / step))
        for i in range(1, n + 1):
            t = i / n
            out.append([round(a[0] + (b[0]-a[0])*t, 6), round(a[1] + (b[1]-a[1])*t, 6)])
    return out

# 黄浦江：更完整的轨迹（吴淞口 → 徐浦大桥 → 闵行），含弯道
huangpu = [
    # 吴淞口（长江口）向南
    [121.5090, 31.4080], [121.5060, 31.3920], [121.4990, 31.3760], [121.4950, 31.3620],
    [121.5020, 31.3480], [121.5150, 31.3340], [121.5250, 31.3200], [121.5290, 31.3030],
    [121.5210, 31.2880], [121.5130, 31.2760], [121.5080, 31.2640], [121.5060, 31.2520],
    [121.5030, 31.2400], [121.4990, 31.2280], [121.4960, 31.2170], [121.4945, 31.2070],
    [121.4930, 31.1960], [121.4910, 31.1850], [121.4880, 31.1750], [121.4830, 31.1660],
    [121.4770, 31.1580], [121.4700, 31.1510], [121.4620, 31.1460], [121.4530, 31.1420],
    [121.4440, 31.1380], [121.4350, 31.1330], [121.4260, 31.1280], [121.4170, 31.1230],
    [121.4080, 31.1170], [121.4000, 31.1100], [121.3930, 31.1020], [121.3860, 31.0930],
]
sh = next(c for c in data['cities'] if c['id'] == 'shanghai')
sh['river'] = {
    'name': '黄浦江',
    'points': densify(huangpu, 0.004),
    'widthM': 480,
    'color': 0x1d6494,
    'edgeColor': 0x4d9fd0,
    'centerColor': 0x8fd8ff,
    'branches': [
        {'name': '苏州河', 'widthM': 90,
         'points': densify([[121.4180, 31.2450], [121.4300, 31.2430], [121.4420, 31.2440],
                            [121.4540, 31.2430], [121.4660, 31.2420], [121.4770, 31.2450],
                            [121.4870, 31.2430], [121.4960, 31.2380]], 0.004)}
    ]
}

# 南京长江：加宽 + 名称
nj = next(c for c in data['cities'] if c['id'] == 'nanjing')
nj['river'] = {
    'name': '长江',
    'points': densify([[118.6300, 32.0800], [118.6800, 32.1100], [118.7300, 32.1400],
                       [118.7800, 32.1600], [118.8300, 32.1900], [118.8900, 32.2200],
                       [118.9600, 32.2500], [119.0200, 32.2700]], 0.006),
    'widthM': 1600,
    'color': 0x1a5f8a,
    'edgeColor': 0x59a8d8,
    'centerColor': 0x9fe0ff,
}
data['cities'] = [sh] + [c for c in data['cities'] if c['id'] != 'shanghai']
json.dump(data, open(dpath, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

# ---------- 注入新数据 ----------
h2 = io.open(HTML, encoding='utf-8').read()
blob = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
i0 = h2.index('const METRO_DATA = ')
i1 = h2.index(';\n', h2.index('"cities"', i0))
h2 = h2[:i0] + 'const METRO_DATA = ' + blob + h2[i1:]
io.open(HTML, 'w', encoding='utf-8').write(h2)

print('data upgraded: huangpu pts =', len(sh['river']['points']))
scripts = re.findall(r'<script type="module">(.*?)</script>', h2, re.S)
for i, s in enumerate(scripts):
    io.open('_chk%d.mjs' % i, 'w', encoding='utf-8').write(s)
print('scripts:', len(scripts))