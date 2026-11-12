# -*- coding: utf-8 -*-
"""桥梁主题 Step2：渲染实现（buildBridgeWorld / 桥体几何 / 列表 / 统计 / 聚焦）"""
import io, re

HTML = 'index.html'
h = io.open(HTML, encoding='utf-8').read()
app = re.findall(r'<script type="module">(.*?)</script>', h, re.S)[1]

# ============ 1) buildWorld 分派 ============
old = """  const city = METRO_DATA.cities.find(c => c.id === state.cityId);
  const lines = city.lines;"""
assert old in app
app = app.replace(old, """  const city = METRO_DATA.cities.find(c => c.id === state.cityId);
  // 桥梁主题：独立渲染分支
  if (city.kind === 'bridges') return buildBridgeWorld(city, doFit);
  const lines = city.lines;""")

# ============ 2) 插入桥梁渲染函数（在 buildWorld 之前） ============
anchor = "function buildWorld(doFit = true){"
assert anchor in app
bridge_code = '''/* ================================================================
 * 中国超级桥梁：三维效果渲染
 *   - 桥面（发光带）、桥塔、斜拉索 / 悬索主缆+吊索、山谷地形
 *   - 支持跨海 / 跨江 / 跨山谷三种类型
 * ================================================================ */
function buildBridgeWorld(city, doFit = true){
  const bridges = city.bridges;
  // 投影原点 = 所有桥控制点质心
  let sLng = 0, sLat = 0, n = 0;
  bridges.forEach(b => b.points.forEach(([lng, lat]) => { sLng += lng; sLat += lat; n++; }));
  const origin = { lng: sLng / n, lat: sLat / n };

  const root = new THREE.Group();
  const bridgeGroups = [];
  let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;

  bridges.forEach((b, bi) => {
    const grp = buildOneBridge(b, origin, bi);
    root.add(grp.group);
    bridgeGroups.push(grp);
    minX = Math.min(minX, grp.bbox.min.x); maxX = Math.max(maxX, grp.bbox.max.x);
    minZ = Math.min(minZ, grp.bbox.min.z); maxZ = Math.max(maxZ, grp.bbox.max.z);
  });

  const cx = (minX + maxX) / 2, cz = (minZ + maxZ) / 2;
  const size = Math.max(maxX - minX, maxZ - minZ);

  // 地面网格（全国尺度参考）
  const grid = new THREE.GridHelper(size + 200, 80, 0x1d3a5c, 0x112640);
  grid.material.transparent = true; grid.material.opacity = .35;
  grid.position.set(cx, -0.5, cz);
  grouped.add(grid);

  world = { city, lines: [], origin, root, grouped, center: new THREE.Vector3(cx, 0, cz),
    size, bridgeGroups, strataGroup: null, crossingGroup: null };
  lineGroups = [];
  state.focusIdx = -1;

  scene.add(root);
  world.root = root;
  if (doFit) fitAll();
  buildUIList();
  updateStats();
  updateLegend();
}

function buildOneBridge(b, origin, bi){
  const grp = new THREE.Group();
  const pts = b.points.map(([lng, lat]) => project(lng, lat, origin));
  const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal');
  const N = 140;
  const samples = [];
  for (let i = 0; i <= N; i++) samples.push(curve.getPointAt(i / N));

  const deckY = b.deckH;
  const halfW = b.width / 2;
  const col = new THREE.Color(b.color);

  // ---- 桥面（发光带 + 两侧栏杆线） ----
  {
    const verts = [], idx = [];
    samples.forEach((p, i) => {
      const a = samples[Math.max(0, i - 1)], c = samples[Math.min(N, i + 1)];
      const dir = new THREE.Vector3().subVectors(c, a).normalize();
      const nrm = new THREE.Vector3(-dir.z, 0, dir.x);
      verts.push(p.clone().setY(deckY).addScaledVector(nrm, -halfW));
      verts.push(p.clone().setY(deckY).addScaledVector(nrm, halfW));
    });
    for (let i = 0; i < samples.length - 1; i++) {
      const l = i * 2, r = i * 2 + 1;
      idx.push(l, l + 2, r, r, l + 2, r + 2);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(verts.flatMap(v => [v.x, v.y, v.z]), 3));
    g.setIndex(idx);
    grp.add(new THREE.Mesh(g, new THREE.MeshStandardMaterial({
      color: col, emissive: col.clone().multiplyScalar(.55), emissiveIntensity: 1.0,
      roughness: .5, metalness: .2, side: THREE.DoubleSide })));
    // 桥面边缘发光
    [-1, 1].forEach(side => {
      const edge = [];
      samples.forEach((p, i) => {
        const a = samples[Math.max(0, i - 1)], c = samples[Math.min(N, i + 1)];
        const dir = new THREE.Vector3().subVectors(c, a).normalize();
        const nrm = new THREE.Vector3(-dir.z, 0, dir.x);
        edge.push(p.clone().setY(deckY + .25).addScaledVector(nrm, side * halfW));
      });
      const seg = edge.flatMap((p, i) => i < edge.length - 1 ? [p, edge[i + 1]] : []);
      const eg = new THREE.BufferGeometry().setFromPoints(seg);
      grp.add(new THREE.LineSegments(eg, new THREE.LineBasicMaterial({
        color: 0xffffff, transparent: true, opacity: .55 })));
    });
  }

  const towerMat = new THREE.MeshStandardMaterial({
    color: 0xd8e4f0, emissive: 0x35506e, emissiveIntensity: .8, roughness: .6 });
  const cableMat = new THREE.LineBasicMaterial({
    color: col.clone().lerp(new THREE.Color(0xffffff), .45), transparent: true, opacity: .85 });

  // ---- 桥塔 + 斜拉索 ----
  const towerTops = [];
  (b.towers || []).forEach(tRatio => {
    const p = curve.getPointAt(tRatio);
    const th = b.towerH;
    const tower = new THREE.Mesh(new THREE.BoxGeometry(halfW * 2.2, th, halfW * 1.4), towerMat);
    tower.position.set(p.x, deckY + th / 2, p.z);
    grp.add(tower);
    towerTops.push({ p, topY: deckY + th, ratio: tRatio });

    if (b.type === 'cable' || b.type === 'truss') {
      // 斜拉索：塔顶向两侧呈扇形展开
      [-1, 1].forEach(side => {
        for (let k = 1; k <= 9; k++) {
          const u = tRatio + side * k * 0.010;
          if (u <= 0 || u >= 1) continue;
          const anchor = curve.getPointAt(u);
          const seg = [new THREE.Vector3(p.x, deckY + th, p.z),
                       new THREE.Vector3(anchor.x, deckY + .4, anchor.z)];
          const g = new THREE.BufferGeometry().setFromPoints(seg);
          grp.add(new THREE.LineSegments(g, cableMat));
        }
      });
    }
  });

  // ---- 悬索：主缆 + 吊索 ----
  if (b.type === 'suspension' && towerTops.length >= 2){
    const [t1, t2] = towerTops;
    const sag = b.towerH * 0.42;
    const M = 40;
    const mainPts = [];
    for (let i = 0; i <= M; i++){
      const t = i / M;
      const x = t1.p.x + (t2.p.x - t1.p.x) * t;
      const z = t1.p.z + (t2.p.z - t1.p.z) * t;
      const y = t1.topY - sag * Math.sin(Math.PI * t);
      mainPts.push(new THREE.Vector3(x, y, z));
    }
    // 主缆（两侧各一条，略向桥面两侧偏移）
    [-1, 1].forEach(side => {
      const off = halfW * 0.95;
      const ptsOff = mainPts.map(p => new THREE.Vector3(p.x, p.y, p.z + side * off));
      const seg = ptsOff.flatMap((p, i) => i < ptsOff.length - 1 ? [p, ptsOff[i + 1]] : []);
      grp.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(seg),
        new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: .7 })));
      // 吊索
      for (let i = 1; i < M; i += 2){
        const cp = mainPts[i];
        const seg2 = [
          new THREE.Vector3(cp.x, cp.y, cp.z + side * off),
          new THREE.Vector3(cp.x, deckY + .4, cp.z + side * off),
        ];
        grp.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(seg2),
          new THREE.LineBasicMaterial({ color: col.clone().lerp(new THREE.Color(0xffffff), .3),
            transparent: true, opacity: .45 })));
      }
    });
  }

  // ---- 跨山谷：两侧山体 + 谷底 ----
  if (b.valley){
    const valleyMat = new THREE.MeshStandardMaterial({
      color: 0x1b3a2c, emissive: 0x0a1a12, emissiveIntensity: 1, roughness: .95 });
    const vd = b.valleyDepth || 50;
    const mid = curve.getPointAt(0.5);
    const dirX = samples[0].x < samples[N].x ? 1 : -1;
    const spanX = Math.abs(samples[0].x - samples[N].x) || 1;
    [-1, 1].forEach(side => {
      const sx = mid.x + side * spanX * 0.55;
      const hill = new THREE.Mesh(new THREE.ConeGeometry(spanX * 0.42, vd, 5), valleyMat);
      hill.position.set(sx, vd / 2 - 2, mid.z);
      grp.add(hill);
    });
    // 谷底河流
    const riverSeg = [new THREE.Vector3(mid.x - spanX * 0.6, 0.2, mid.z),
                      new THREE.Vector3(mid.x + spanX * 0.6, 0.2, mid.z)];
    grp.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(riverSeg),
      new THREE.LineBasicMaterial({ color: 0x5fa8d8, transparent: true, opacity: .7 })));
  }

  // ---- 桥名 + 关键数据标注 ----
  {
    const mid = curve.getPointAt(0.5);
    const labelTop = deckY + (b.towerH || 20) + 10;
    const lb = makeLabel(b.name, `${b.cat} · ${b.lenKm} km · ${b.type === 'suspension' ? '悬索桥' : b.type === 'cable' ? '斜拉桥' : '钢桁梁桥'}`, b.color);
    lb.position.set(mid.x, labelTop, mid.z);
    lb.scale.set(19, 6.1, 1);
    lb.userData.alwaysVisible = true;
    grp.add(lb);
    allLabels.push(lb);
    globalLabelInfo.push({ bridge: true });
  }

  const bbox = new THREE.Box3().setFromPoints(samples.map(p => p.clone().setY(deckY)));
  return { bridge: b, bi, group: grp, bbox, center: bbox.getCenter(new THREE.Vector3()),
           size: Math.max(bbox.max.x - bbox.min.x, bbox.max.z - bbox.min.z) };
}

function focusBridge(idx){
  if (!world || !world.bridgeGroups) return;
  const bg = world.bridgeGroups[idx];
  if (!bg) return;
  state.focusIdx = -1;
  const target = bg.center.clone();
  target.y = bg.bridge.deckH * 0.8;
  const dist = Math.max(bg.size * 1.15, 60);
  const dir = new THREE.Vector3(0.25, 0.55, 0.8).normalize();
  const camPos = target.clone().addScaledVector(dir, dist);
  state.flyTo = { from: camera.position.clone(), to: camPos,
    fromT: controls.target.clone(), toT: target, t: 0 };
  // 高亮选中桥
  world.bridgeGroups.forEach((g, i) => {
    g.group.traverse(o => {
      if (o.material && o.material.opacity !== undefined){
        if (o.material.userData._base === undefined) o.material.userData._base = o.material.opacity;
        o.material.opacity = i === idx ? o.material.userData._base : o.material.userData._base * 0.35;
      }
    });
  });
  // 更新下拉
  const sel = document.getElementById('sel-line');
  if (sel) sel.value = 'bridge-' + idx;
  // 信息卡
  const info = document.getElementById('info-card');
  document.getElementById('ic-idx').textContent = String(idx + 1).padStart(2, '0');
  document.getElementById('ic-name').textContent = bg.bridge.name;
  document.getElementById('ic-chips').innerHTML =
    `<span class="chip t" style="border-color:${bg.bridge.color};color:${bg.bridge.color}">${bg.bridge.cat}</span>` +
    `<span class="chip">${bg.bridge.type === 'suspension' ? '悬索桥' : bg.bridge.type === 'cable' ? '斜拉桥' : '钢桁梁桥'}</span>` +
    `<span class="chip">${bg.bridge.year} 年</span>`;
  document.getElementById('ic-depth').innerHTML =
    `全长 <b>${bg.bridge.lenKm}</b> km · 主跨 <b>${bg.bridge.mainSpanM}</b> m` +
    (bg.bridge.towerHm ? ` · 塔高 <b>${bg.bridge.towerHm}</b> m` : '');
  document.getElementById('ic-note').textContent = bg.bridge.desc || '';
  info.classList.add('show');
}

function buildWorld(doFit = true){'''
app = app.replace(anchor, bridge_code, 1)

# ============ 3) buildUIList 桥梁分支 ============
old3 = """function buildUIList(){
  const box = $('st-list');
  box.innerHTML = '';
  const w = world;"""
assert old3 in app
app = app.replace(old3, """function buildUIList(){
  const box = $('st-list');
  box.innerHTML = '';
  const w = world;
  // 桥梁主题：桥列表
  if (w.city.kind === 'bridges'){
    w.city.bridges.forEach((b, i) => {
      const row = document.createElement('button');
      row.className = 'st-row';
      row.innerHTML = `<span class="st-idx">${String(i+1).padStart(2,'0')}</span>
        <span class="st-name">${b.name}</span>
        <span class="st-tr">${b.cat}</span>
        <span class="st-depth" style="color:${b.color}">${b.lenKm}km</span>`;
      row.addEventListener('click', () => focusBridge(i));
      box.appendChild(row);
    });
    return;
  }""")

# ============ 4) updateStats / updateLegend 桥梁分支 ============
old4 = """function updateStats(){
  const w = world;"""
assert old4 in app
app = app.replace(old4, """function updateStats(){
  const w = world;
  if (w.city.kind === 'bridges'){
    const bs = w.city.bridges;
    const crossSea = bs.filter(b => b.cat === '跨海').length;
    const crossRiver = bs.filter(b => b.cat === '跨江').length;
    const crossValley = bs.filter(b => b.cat === '跨山谷').length;
    $('stat-line').innerHTML = `<b>中国超级桥梁</b> · ${bs.length} 座 · 跨海 ${crossSea} · 跨江 ${crossRiver} · 跨山谷 ${crossValley}<br>` +
      `点击桥梁查看三维效果与工程数据`;
    $('btn-list-toggle').textContent = `桥梁 ${bs.length}`;
    const fc = $('float-count'); if (fc) fc.textContent = bs.length;
    return;
  }""")

old5 = """function updateLegend(){
  const w = world;"""
assert old5 in app
app = app.replace(old5, """function updateLegend(){
  const w = world;
  if (w.city.kind === 'bridges'){
    $('legend').innerHTML = `
      <div class="lg-row"><span class="lg-chip" style="background:#00A6A6"></span>斜拉桥 / 悬索桥 / 桁梁桥（按线路色区分）</div>
      <div class="lg-row"><span class="lg-chip" style="background:#FFC44D"></span>桥塔与主缆</div>
      <div class="lg-row" style="font-size:10px">点击列表或下拉选择单座桥梁查看特写</div>`;
    return;
  }""")

# ============ 5) 下拉值 'bridge-N' 处理 ============
old6 = """$('sel-line').addEventListener('change', e => {
  state.focusLineId = e.target.value;
  rebuild();
});"""
assert old6 in app
app = app.replace(old6, """$('sel-line').addEventListener('change', e => {
  const v = e.target.value;
  if (v.startsWith('bridge-')){
    state.focusLineId = '__all__';
    focusBridge(+v.split('-')[1]);
    return;
  }
  state.focusLineId = v;
  rebuild();
});""")

# ============ 6) 城市切换时清空选中状态 ============
old7 = """  const c = METRO_DATA.cities.find(x => x.id === e.target.value);
  state.cityId = c.id; state.focusLineId = '__all__';
  populateSelectors(); rebuild();"""
assert old7 in app
app = app.replace(old7, """  const c = METRO_DATA.cities.find(x => x.id === e.target.value);
  state.cityId = c.id; state.focusLineId = '__all__';
  document.getElementById('info-card').classList.remove('show');
  populateSelectors(); rebuild();""")

io.open('index.html', 'w', encoding='utf-8').write(
    h[:h.rindex('<script type="module">')] + '<script type="module">' + app + '</script>' +
    h[h.rindex('</script>') + len('</script>'):])
print('bridge rendering implemented')
scripts = re.findall(r'<script type="module">(.*?)</script>', io.open('index.html', encoding='utf-8').read(), re.S)
for i, s in enumerate(scripts):
    io.open('_chk%d.mjs' % i, 'w', encoding='utf-8').write(s)
print('scripts:', len(scripts))