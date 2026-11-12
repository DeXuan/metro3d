/* =====================================================================
 * 城市地铁地下三维视图 · 多线路版
 * 渲染层完全由 METRO_DATA 驱动：城市 → 线路(含支线) → 站点
 * 扩展：向 cities[].lines 添加线路对象即可，渲染逻辑无需改动
 * ===================================================================== */

/* ---------------- 数据（由 generate 脚本注入） ---------------- */
const METRO_DATA = __METRO_DATA__;

/* ---------------- 常量与状态 ---------------- */
const H_SCALE = 0.01;            // 1 场景单位 = 100 米
let V_SCALE = 2.0;               // 垂直比例 2.0 单位/米（≈200× 夸张）
const MAX_DEPTH_M = 30;

const state = {
  cityId: METRO_DATA.cities[0].id,
  focusLineId: '__all__',        // '__all__' 或线路 id
  depthColor: false,
  labels: true,
  strata: true,
  selectedIdx: -1,
  focusIdx: -1,                  // 当前 focus 线路在线路数组中的下标
  flyTo: null,
  cruise: null,
  intro: null,
};

/* 深度 → 颜色 */
const DEPTH_STOPS = [[0,'#2FD8A9'],[8,'#37C4F2'],[16,'#6F8CFF'],[22,'#A86BFF'],[30,'#FF6A4D']];
const ELEVATED_COLOR = '#FFC44D';
function depthColor(elevM){
  if (elevM > 0.4) return new THREE.Color(ELEVATED_COLOR);
  const d = Math.max(0, Math.min(MAX_DEPTH_M, -elevM));
  for (let i = 1; i < DEPTH_STOPS.length; i++){
    if (d <= DEPTH_STOPS[i][0]){
      const [d0,c0] = DEPTH_STOPS[i-1], [d1,c1] = DEPTH_STOPS[i];
      return new THREE.Color(c0).lerp(new THREE.Color(c1), (d-d0)/(d1-d0));
    }
  }
  return new THREE.Color(DEPTH_STOPS.at(-1)[1]);
}
function stElev(st){ return st.type === 'elevated' ? st.height : (st.type === 'ground' ? 0 : -st.depth); }

/* ---------------- 场景基础 ---------------- */
const canvas = document.getElementById('c');
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
} catch (e) {
  document.getElementById('load-error').style.display = 'block';
  document.getElementById('load-msg').textContent = '当前环境不支持 WebGL，无法渲染三维视图。';
  throw e;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.setClearColor(0x060c16);

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x081020, 0.00055);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.5, 6000);
const controls = new window.OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI * 0.52;
controls.autoRotate = true;
controls.autoRotateSpeed = -0.35;

scene.add(new THREE.AmbientLight(0x88aacc, 1.0));
const dirLight = new THREE.DirectionalLight(0xffffff, 1.4);
dirLight.position.set(120, 260, 160);
scene.add(dirLight);

/* ---------------- 运行时对象 ---------------- */
let world = null;   // { allLines:[...线对象...], focusIdx, group(整个线网容器), bbox, center, size }

function project(lng, lat, origin){
  const x = (lng - origin.lng) * 111320 * Math.cos(origin.lat * Math.PI/180);
  const z = -(lat - origin.lat) * 110540;
  return new THREE.Vector3(x * H_SCALE, 0, z * H_SCALE);
}

/* ---------- 文字标注 ---------- */
function makeLabel(main, sub, subColor){
  const dpr = 2, W = 300, H = 96;
  const cv = document.createElement('canvas');
  cv.width = W*dpr; cv.height = H*dpr;
  const ctx = cv.getContext('2d');
  ctx.scale(dpr, dpr);
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = '600 30px "PingFang SC","Microsoft YaHei",sans-serif';
  ctx.lineWidth = 5; ctx.strokeStyle = 'rgba(3,8,16,.85)';
  ctx.strokeText(main, W/2, 30);
  ctx.fillStyle = '#f0f7ff'; ctx.fillText(main, W/2, 30);
  if (sub){
    ctx.font = '500 22px "PingFang SC","Microsoft YaHei",sans-serif';
    ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(3,8,16,.85)';
    ctx.strokeText(sub, W/2, 66);
    ctx.fillStyle = subColor; ctx.fillText(sub, W/2, 66);
  }
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }));
  sp.scale.set(16.5, 5.3, 1);
  return sp;
}

/* ---------- 黄浦江 ---------- */
const RIVER_LINE = [
  [121.4890,31.1550],[121.4920,31.1800],[121.4952,31.2030],[121.4995,31.2180],
  [121.5035,31.2330],[121.5085,31.2520],[121.5150,31.2720],[121.5235,31.2930],[121.5350,31.3150]
];
function buildRiver(origin){
  const kx = 111320 * Math.cos(origin.lat*Math.PI/180) * H_SCALE;
  const kz = 110540 * H_SCALE;
  const ctr = RIVER_LINE.map(([lng,lat]) => new THREE.Vector3((lng-origin.lng)*kx, 0.06, -(lat-origin.lat)*kz));
  const w = 0.0032 * 111320 * Math.cos(origin.lat*Math.PI/180) * H_SCALE;
  const verts = [], idx = [];
  ctr.forEach((p,i) => {
    const a = ctr[Math.max(0,i-1)], b = ctr[Math.min(ctr.length-1,i+1)];
    const dir = new THREE.Vector3().subVectors(b,a).normalize();
    const n = new THREE.Vector3(-dir.z,0,dir.x);
    verts.push(p.clone().addScaledVector(n,-w), p.clone().addScaledVector(n,w));
  });
  for (let i = 0; i < ctr.length-1; i++){
    const l = i*2, r = i*2+1;
    idx.push(l, l+2, r, r, l+2, r+2);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(verts.flatMap(v=>[v.x,v.y,v.z]), 3));
  g.setIndex(idx);
  const mesh = new THREE.Mesh(g, new THREE.MeshBasicMaterial({
    color: 0x1c5a8f, transparent: true, opacity: 0.62, depthWrite: false, side: THREE.DoubleSide }));
  mesh.renderOrder = 1;
  return mesh;
}

/* ---------- 城市天际线（InstancedMesh） ---------- */
function mulberry32(a){ return function(){
  a |= 0; a = a + 0x6D2B79F5 | 0;
  let t = Math.imul(a ^ a>>>15, 1|a);
  t = t + Math.imul(t ^ t>>>7, 61|t) ^ t;
  return ((t ^ t>>>14)>>>0) / 4294967296; }; }
function buildBuildings(origin){
  const seeds = [
    [121.4323,31.1975,1.0],[121.4650,31.2090,.7],[121.4860,31.2210,.8],
    [121.5080,31.2330,1.0],[121.5226,31.2306,.9],[121.5450,31.2330,.55],
    [121.3950,31.1720,.6],[121.3500,31.1580,.35],[121.2600,31.1200,.2],
    [121.2280,31.0300,.2],[121.5530,31.2650,.4],[121.6230,31.2200,.35],
    [121.6150,31.2500,.3],[121.3100,31.1960,.4],[121.1510,31.2900,.15],
    [121.0750,31.1030,.1],[121.5900,31.1550,.35],[121.2240,31.1180,.18],
  ];
  const rng = mulberry32(20261112);
  const items = [];
  seeds.forEach(([lng,lat,w]) => {
    const n = Math.round(w * 46);
    for (let i = 0; i < n; i++){
      const plng = lng + (rng()-.5)*.014*(0.4+rng());
      const plat = lat + (rng()-.5)*.011*(0.4+rng());
      let nearRiver = false;
      for (const [rl,ra] of RIVER_LINE){
        if (Math.hypot(plng-rl, (plat-ra)*1.25) < .0032){ nearRiver = true; break; }
      }
      if (nearRiver) continue;
      const tall = rng()*rng();
      items.push([plng, plat, 10 + tall*190*(w>=.9?1.35:1), 35+rng()*85]);
    }
  });
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

/* ---------- 构建整网 ---------- */
const grouped = new THREE.Group();       // 常驻：环境（地面/江/建筑/地层参考面）
let lineGroups = [];                     // 每条线路一个 Group
let allMarkers = [], allLabels = [];
const globalLabelInfo = [];              // 与 allLabels 一一对应 {lineIdx, stIdx}

function lineObjKey(l){ return l.branchOf ? l.branchOf + '|' + l.id : l.id; }

function buildWorld(doFit = true){
  if (world){ scene.remove(world.root); disposeObj(world.root); }
  allMarkers = []; allLabels = [];

  const city = METRO_DATA.cities.find(c => c.id === state.cityId);
  const lines = city.lines;

  // 全市投影原点 = 所有站坐标的质心
  let sLng = 0, sLat = 0, n = 0;
  lines.forEach(l => l.stations.forEach(s => { sLng += s.lng; sLat += s.lat; n++; }));
  const origin = { lng: sLng/n, lat: sLat/n };

  const root = new THREE.Group();
  // —— 环境层 ——
  {
    let minLng=Infinity, minLat=Infinity, maxLng=-Infinity, maxLat=-Infinity;
    lines.forEach(l => l.stations.forEach(s => {
      minLng=Math.min(minLng,s.lng); maxLng=Math.max(maxLng,s.lng);
      minLat=Math.min(minLat,s.lat); maxLat=Math.max(maxLat,s.lat);
    }));
    const pad = (maxLng-minLng)*0.02;
    const pMin = project(minLng-pad, minLat-pad, origin);
    const pMax = project(maxLng+pad, maxLat+pad, origin);
    const cx = (pMin.x+pMax.x)/2, cz = (pMin.z+pMax.z)/2;
    const sx = pMax.x-pMin.x, sz = pMax.z-pMin.z;

    const ground = new THREE.Mesh(new THREE.PlaneGeometry(sx+140, sz+140),
      new THREE.MeshBasicMaterial({ color: 0x0d1c30, transparent: true, opacity: .5, side: THREE.DoubleSide, depthWrite: false }));
    ground.rotation.x = -Math.PI/2; ground.position.set(cx,0,cz); ground.renderOrder = 2;
    grouped.add(ground);

    const grid = new THREE.GridHelper(Math.max(sx,sz)+160, 96, 0x1d3a5c, 0x112640);
    grid.material.transparent = true; grid.material.opacity = .5;
    grid.position.set(cx, 0.02, cz);
    grouped.add(grid);

    grouped.add(buildRiver(origin));

    world = { city, lines, origin, root, grouped, center: new THREE.Vector3(cx,0,cz),
      size: Math.max(sx,sz) };
    root.add(grouped);
  }

  // —— 各线路对象 ——
  lineGroups = lines.map((line, li) => {
    const lg = makeLineGroup(line, li, origin);
    if (lg) root.add(lg.group);
    return lg;
  });

  // 地层参考面（全市，-10/-20/-30m）
  const strataGroup = new THREE.Group();
  [[10,0x1d4a3a],[20,0x1d3a58],[30,0x3a2450]].forEach(([d,c]) => {
    const pm = new THREE.Mesh(new THREE.PlaneGeometry(world.size+220, world.size+220),
      new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: .07, side: THREE.DoubleSide, depthWrite: false }));
    pm.rotation.x = -Math.PI/2;
    pm.position.set(world.center.x, -d*V_SCALE, world.center.z);
    pm.renderOrder = 3;
    strataGroup.add(pm);
    const lb = makeLabel('', `−${d} m`, '#6d8aa5');
    lb.scale.set(9, 3.6, 1);
    lb.position.set(world.center.x - world.size/2 - 14, -d*V_SCALE, world.center.z + world.size/2 + 8);
    strataGroup.add(lb);
  });
  strataGroup.visible = state.strata;
  grouped.add(strataGroup);

  // 聚焦线路高亮/淡化其余
  applyFocus();

  scene.add(root);
  world.root = root;
  world.strataGroup = strataGroup;
  if (doFit) fitAll();
  buildUIList();
  updateStats();
  updateLegend();
}

const _dropPos = [];
function makeLineGroup(line, li, origin){
  const sts = line.stations.map((s,j) => {
    s._i = j; s._elev = stElev(s);
    return { st: s, pos: project(s.lng, s.lat, origin) };
  });
  const pts = sts.map(a => new THREE.Vector3(a.pos.x, a.st._elev*V_SCALE, a.pos.z));
  const group = new THREE.Group();

  // 管线
  const tubular = Math.max(140, Math.min(720, sts.length*16));
  const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal');
  const tubeGeo = new THREE.TubeGeometry(curve, tubular, 1.25, 10, false);
  group.userData.curve = curve;

  if (state.depthColor){
    const anchorUs = [];
    const NS = 900, sample = [];
    for (let i=0;i<=NS;i++) sample.push(curve.getPointAt(i/NS));
    sts.forEach(a => {
      let best=0, bd=Infinity;
      sample.forEach((p,j) => { const dd=p.distanceToSquared(pts[a.st._i]); if (dd<bd){bd=dd;best=j;} });
      anchorUs.push(best/NS);
    });
    const colors = new Float32Array(tubeGeo.attributes.position.count*3);
    const ringVerts = 11;
    const c = new THREE.Color();
    for (let v=0; v<tubeGeo.attributes.position.count; v++){
      const u = Math.min(1, Math.floor(v/ringVerts)/tubular);
      let e = sts[0].st._elev;
      for (let i=1; i<anchorUs.length; i++){
        if (u <= anchorUs[i] || i === anchorUs.length-1){
          const span = anchorUs[i]-anchorUs[i-1];
          e = sts[i-1].st._elev + (sts[i].st._elev-sts[i-1].st._elev)*(span>0?(u-anchorUs[i-1])/span:0);
          break;
        }
      }
      c.copy(depthColor(e));
      colors[v*3]=c.r; colors[v*3+1]=c.g; colors[v*3+2]=c.b;
    }
    tubeGeo.setAttribute('color', new THREE.BufferAttribute(colors,3));
    group.add(new THREE.Mesh(tubeGeo, new THREE.MeshStandardMaterial({
      vertexColors: true, roughness:.35, metalness:.15, emissive:0x223344, emissiveIntensity:.6 })));
  } else {
    const col = new THREE.Color(line.color);
    group.add(new THREE.Mesh(tubeGeo, new THREE.MeshStandardMaterial({
      color: col, roughness:.35, metalness:.15, emissive: col.clone().multiplyScalar(.38) })));
  }

  // 地面投影参考线
  const flat = pts.map(p => new THREE.Vector3(p.x, 0.25, p.z));
  group.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(flat,false,'centripetal'), Math.max(200, sts.length*8), 0.3, 6, false),
    new THREE.MeshBasicMaterial({ color: new THREE.Color(line.color), transparent: true, opacity: .25 })));

  // 站点：球体 + 垂线 + 地面环 + 换乘环 + 标签
  const sphereGeo = new THREE.SphereGeometry(1.75, 18, 12);
  const ringGeo = new THREE.RingGeometry(1.75, 2.5, 22); ringGeo.rotateX(-Math.PI/2);
  const ringMesh = new THREE.InstancedMesh(ringGeo,
    new THREE.MeshBasicMaterial({ transparent:true, opacity:.7, side:THREE.DoubleSide, depthWrite:false }),
    sts.length);
  const dropPos = [];
  sts.forEach((a, i) => {
    const st = a.st, y = st._elev*V_SCALE;
    const col = state.depthColor ? depthColor(st._elev) : new THREE.Color(st.type==='elevated' ? ELEVATED_COLOR : line.color);
    const marker = new THREE.Mesh(sphereGeo, new THREE.MeshStandardMaterial({
      color: col, emissive: col.clone().multiplyScalar(.5), roughness: .3 }));
    marker.position.set(a.pos.x, y, a.pos.z);
    marker.userData = { lineIdx: li, stIdx: i, lineId: line.id };
    group.add(marker); allMarkers.push(marker);
    dropPos.push(a.pos.x, y, a.pos.z, a.pos.x, 0, a.pos.z);
    const M = new THREE.Matrix4(); M.makeTranslation(a.pos.x, .1, a.pos.z);
    ringMesh.setMatrixAt(i, M);
    if (st.transfer && st.transfer.length){
      const tr = new THREE.Mesh(new THREE.TorusGeometry(3.1, .36, 8, 26),
        new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .85 }));
      tr.rotation.x = Math.PI/2; tr.position.set(a.pos.x, y, a.pos.z);
      group.add(tr);
    }
    const sub = st.type==='elevated' ? `↑ 高架 ${st.height}m`
             : st.type==='ground' ? '地面'
             : `↓ ${st.depth}m${st.transfer ? ' · 换'+st.transfer.join('/') : ''}`;
    const lb = makeLabel(st.name, sub, st.type==='elevated' ? '#FFC44D' : '#9fd8ff');
    lb.position.set(a.pos.x, 3.6 + (i%2)*2.4, a.pos.z);
    group.add(lb); allLabels.push(lb);
    globalLabelInfo.push({ lineIdx: li, stIdx: i });
  });
  ringMesh.instanceMatrix.needsUpdate = true;
  group.add(ringMesh);
  const dropGeo = new THREE.BufferGeometry();
  dropGeo.setAttribute('position', new THREE.Float32BufferAttribute(dropPos, 3));
  group.add(new THREE.LineSegments(dropGeo, new THREE.LineBasicMaterial({ color: 0x7fb8d8, transparent:true, opacity:.4 })));

  const bbox = new THREE.Box3().setFromPoints(pts);
  return { line, li, group, bbox, markers: group.children.filter(c => c.userData && c.userData.lineIdx === li),
           center: bbox.getCenter(new THREE.Vector3()), size: Math.max(bbox.max.x-bbox.min.x, bbox.max.z-bbox.min.z) };
}

function applyFocus(){
  if (!world) return;
  const focus = state.focusLineId;
  lineGroups.forEach(lg => {
    const isFocus = focus === '__all__' || lineObjKey(lg.line) === focus ||
                    (lg.line.branchOf && lg.line.branchOf === focus);
    lg.dim = !isFocus;
    lg.group.traverse(o => {
      const mats = o.material ? (Array.isArray(o.material) ? o.material : [o.material]) : [];
      mats.forEach(mm => {
        if (mm && typeof mm.opacity === 'number'){
          if (mm.userData._baseOp === undefined) mm.userData._baseOp = mm.opacity;
          const base = mm.userData._baseOp;
          mm.transparent = true;
          mm.opacity = base * (lg.dim ? 0.14 : 1);
          void o;
        }
      });
    });
  });
  state.focusIdx = focus === '__all__' ? -1 : world.lines.findIndex(l => lineObjKey(l) === focus);
}

function disposeObj(root){
  root.traverse(o => {
    if (o.geometry) o.geometry.dispose();
    if (o.material){
      (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => { if (m.map) m.map.dispose(); if (!m.userData._shared) m.dispose(); });
    }
  });
}

/* ---------------- 相机适配 ---------------- */
function fitAll(instant){
  const w = world;
  let target = w.center.clone(), size = w.size;
  if (state.focusIdx >= 0){
    const lg = lineGroups[state.focusIdx];
    if (lg){ target = lg.center.clone(); size = lg.size; }
  }
  target.y = -V_SCALE * 9;
  const dist = size * 0.85;
  const dir = new THREE.Vector3(0.15, 0.55, 0.95).normalize();
  const camPos = target.clone().addScaledVector(dir, dist);
  controls.target.copy(target);
  if (instant){
    camera.position.copy(camPos);
    camera.near = Math.max(0.1, dist/500); camera.far = dist*30;
    camera.updateProjectionMatrix();
    controls.minDistance = size*0.04; controls.maxDistance = size*3;
    controls.update();
  } else {
    state.flyTo = { from: camera.position.clone(), to: camPos, fromT: controls.target.clone(), toT: target, t: 0 };
  }
}

/* ---------------- UI ---------------- */
const $ = id => document.getElementById(id);

function populateSelectors(){
  const city = METRO_DATA.cities.find(c => c.id === state.cityId);
  const selCity = $('sel-city'), selLine = $('sel-line');
  selCity.innerHTML = METRO_DATA.cities.map(c => `<option value="${c.id}">${c.name}（${c.lines.length}条线路）</option>`).join('') +
    '<option disabled>更多城市 · 敬请期待</option>';
  const opts = ['<option value="__all__">全部线路 · 网络总览</option>'];
  city.lines.forEach(l => {
    opts.push(`<option value="${lineObjKey(l)}">${l.name} · ${l.from}—${l.to}</option>`);
  });
  selLine.innerHTML = opts.join('') + '<option disabled>更多线路 · 敬请期待</option>';
  selCity.value = state.cityId;
  selLine.value = state.focusLineId;
}

function updateStats(){
  const w = world;
  const totalSt = w.lines.reduce((a,l) => a + l.stations.length, 0);
  const focus = state.focusIdx >= 0 ? w.lines[state.focusIdx] : null;
  $('stat-line').innerHTML = focus
    ? `<b>${focus.name}</b> · ${focus.from} ↔ ${focus.to} · 约 ${focus.lengthKm} km<br>` +
      `${focus.stations.length} 站 · 线路色 <span style="color:${focus.color}">■</span>（深度为示意值）`
    : `<b>上海轨道交通线网</b> · ${w.lines.length} 条线路 · ${totalSt} 座车站<br>` +
      `全线地下埋深示意 0~${MAX_DEPTH_M} m · 点击线路可聚焦查看`;
  $('btn-list-toggle').textContent = `站点 ${totalSt}`;
}

function updateLegend(){
  const w = world;
  const grad = `linear-gradient(90deg, ${DEPTH_STOPS.map(([d,c])=>`${c} ${d/MAX_DEPTH_M*100}%`).join(',')})`;
  let html = '';
  if (state.depthColor){
    html = `<div class="lg-row"><span class="lg-grad" style="background:${grad}"></span><span>埋深着色（全网络）</span></div>
      <div class="lg-num"><span>0m</span><span>浅</span><span>${MAX_DEPTH_M}m 深</span></div>
      <div class="lg-row"><span class="lg-chip" style="background:${ELEVATED_COLOR}"></span>高架段</div>`;
  } else {
    const focus = state.focusIdx >= 0 ? w.lines[state.focusIdx] : null;
    const shown = focus ? [focus] : w.lines.filter(l => !l.branchOf);
    html = `<div class="lg-grid">${shown.map(l =>
      `<button class="lg-chip-btn" data-id="${lineObjKey(l)}" title="${l.name}"><i style="background:${l.color}"></i><span>${l.name.replace('（市域）','')}${l.branchOf?'支':''}</span></button>`).join('')}</div>`;
    html += `<div class="lg-row"><span class="lg-chip" style="background:${ELEVATED_COLOR}"></span>高架段</div>
      <div class="lg-row"><span class="lg-ring"></span>换乘站</div>`;
  }
  $('legend').innerHTML = html;
  $('legend').querySelectorAll('.lg-chip-btn').forEach(b => {
    b.addEventListener('click', () => {
      state.focusLineId = b.dataset.id;
      $('sel-line').value = state.focusLineId;
      rebuild();
    });
  });
}

function buildUIList(){
  const box = $('st-list');
  box.innerHTML = '';
  const w = world;
  const focus = state.focusIdx >= 0 ? [w.lines[state.focusIdx]] : w.lines;
  focus.forEach(line => {
    const gHead = document.createElement('button');
    gHead.className = 'grp-head';
    gHead.innerHTML = `<i style="background:${line.color}"></i><span>${line.name} · ${line.stations.length}站</span><b>${line.from}—${line.to}</b>`;
    if (state.focusIdx >= 0){
      gHead.classList.add('open');
      const b = document.createElement('div');
      b.className = 'grp-body'; b.dataset.g = lineObjKey(line);
      line.stations.forEach((st,j) => {
        const row = document.createElement('button');
        row.className = 'st-row'; row.dataset.idx = j; row.dataset.line = lineObjKey(line);
        const dTxt = st.type==='elevated' ? `↑${st.height}m` : st.type==='ground' ? '地面' : `−${st.depth}m`;
        const dCol = '#' + (state.depthColor ? depthColor(st._elev) : new THREE.Color(line.color)).getHexString();
        row.innerHTML = `<span class="st-idx">${String(j+1).padStart(2,'0')}</span>
          <span class="st-name">${st.name}</span>
          ${st.transfer && !state.depthColor ? `<span class="st-tr">换 ${st.transfer.join('/')}</span>` : ''}
          <span class="st-depth" style="color:${dCol}">${dTxt}</span>`;
        row.addEventListener('click', () => focusStation(line, j));
        b.appendChild(row);
      });
      box.appendChild(gHead);
      box.appendChild(b);
      return;
    }
    gHead.addEventListener('click', () => {
      const body = box.querySelector(`.grp-body[data-g="${lineObjKey(line)}"]`);
      if (body){ body.style.display = body.style.display === 'none' ? '' : 'none';
        gHead.classList.toggle('open', body.style.display !== 'none'); }
      else {
        const b = document.createElement('div');
        b.className = 'grp-body'; b.dataset.g = lineObjKey(line);
        line.stations.forEach((st,j) => {
          const row = document.createElement('button');
          row.className = 'st-row'; row.dataset.idx = j; row.dataset.line = lineObjKey(line);
          const dTxt = st.type==='elevated' ? `↑${st.height}m` : st.type==='ground' ? '地面' : `−${st.depth}m`;
          const dCol = '#' + (state.depthColor ? depthColor(st._elev) : new THREE.Color(line.color)).getHexString();
          row.innerHTML = `<span class="st-idx">${String(j+1).padStart(2,'0')}</span>
            <span class="st-name">${st.name}</span>
            ${st.transfer && !state.depthColor ? `<span class="st-tr">换 ${st.transfer.join('/')}</span>` : ''}
            <span class="st-depth" style="color:${dCol}">${dTxt}</span>`;
          row.addEventListener('click', () => focusStation(state.focusIdx >= 0 ? line : chooseLineByStation(line,j), j));
          b.appendChild(row);
        });
        gHead.parentNode.insertBefore(b, gHead.nextSibling);
        gHead.classList.add('open');
      }
    });
    box.appendChild(gHead);
  });
}

/* 全部模式下点击某站 → 该站所在线路对象 */
function chooseLineByStation(line, idx){ return line; }

function focusStation(lineObj, idx){
  const st = lineObj.stations[idx];
  state.focusLineId = lineObjKey(lineObj);
  $('sel-line').value = state.focusLineId;
  state.selectedIdx = idx;
  state.selectedLine = lineObj.id;
  rebuild(true);
  const lg = lineGroups.find(g => g.line === lineObj);
  const pos = project(st.lng, st.lat, world.origin);
  const size = lg ? lg.size : world.size;
  const target = new THREE.Vector3(pos.x, st._elev*V_SCALE*0.5, pos.z);
  const camPos = target.clone().add(new THREE.Vector3(size*0.06, size*0.055, size*0.075));
  state.flyTo = { from: camera.position.clone(), to: camPos, fromT: controls.target.clone(), toT: target, t: 0 };
  showInfoCard(lineObj, idx);
}

function showInfoCard(line, i){
  const st = line.stations[i];
  $('ic-idx').textContent = String(i+1).padStart(2,'0');
  $('ic-name').textContent = st.name + '站';
  const chips = [`<span class="chip ${st.type==='elevated'?'e':st.type==='ground'?'u':'u'}">${st.type==='elevated'?'高架车站':st.type==='ground'?'地面车站':'地下车站'}</span>`,
                 `<span class="chip t" style="border-color:${line.color};color:${line.color}">${line.name}</span>`];
  if (st.transfer) chips.push(`<span class="chip t">换乘 ${st.transfer.map(t=>/^[0-9]+$/.test(t)?t+'号线':t).join(' · ')}</span>`);
  $('ic-chips').innerHTML = chips.join('');
  if (st.type==='elevated'){
    $('ic-depth').innerHTML = `轨面高 <b>+${st.height}</b> m（高架段）`;
  } else {
    const pct = Math.round(st.depth / MAX_DEPTH_M * 100);
    $('ic-depth').innerHTML = `站台埋深 <b>−${st.depth}</b> m
      <div class="ic-bar"><i style="width:${pct}%;background:#${depthColor(st._elev).getHexString()}"></i></div>`;
  }
  $('ic-note').textContent = st.note || (st.transfer ? '换乘站' : '');
  $('info-card').classList.add('show');
}

/* ---------------- 交互 ---------------- */
const ray = new THREE.Raycaster();
const ptr = new THREE.Vector2();
let downXY = null;
canvas.addEventListener('pointerdown', e => {
  downXY = [e.clientX, e.clientY];
  controls.autoRotate = false;
  stopCruise();
});
canvas.addEventListener('pointerup', e => {
  if (!downXY) return;
  const moved = Math.hypot(e.clientX-downXY[0], e.clientY-downXY[1]);
  downXY = null;
  if (moved > 7) return;
  ptr.x = (e.clientX/innerWidth)*2-1;
  ptr.y = -(e.clientY/innerHeight)*2+1;
  ray.setFromCamera(ptr, camera);
  const hit = ray.intersectObjects(allMarkers, false);
  if (hit.length){
    const u = hit[0].object.userData;
    const line = world.lines[u.lineIdx];
    focusStation(line, u.stIdx);
  }
});
canvas.addEventListener('wheel', () => { controls.autoRotate = false; stopCruise(); }, { passive: true });

$('sel-city').addEventListener('change', e => {
  const c = METRO_DATA.cities.find(x => x.id === e.target.value);
  state.cityId = c.id; state.focusLineId = '__all__';
  populateSelectors(); rebuild();
});
$('sel-line').addEventListener('change', e => {
  state.focusLineId = e.target.value;
  rebuild();
});

function rebuild(keepCamera){
  stopCruise();
  buildWorld(!keepCamera);
}

$('vscale').addEventListener('input', e => {
  const v = +e.target.value;
  $('vscale-val').textContent = v + '×';
  V_SCALE = v * H_SCALE;
  rebuild(true);
});
$('btn-depth-color').addEventListener('click', e => {
  state.depthColor = !state.depthColor;
  e.currentTarget.classList.toggle('on', state.depthColor);
  rebuild(true);
});
$('btn-labels').addEventListener('click', e => {
  state.labels = !state.labels;
  e.currentTarget.classList.toggle('on', state.labels);
  allLabels.forEach(l => l.visible = false);
});
$('btn-strata').addEventListener('click', e => {
  state.strata = !state.strata;
  e.currentTarget.classList.toggle('on', state.strata);
  world.strataGroup.visible = state.strata;
});
$('btn-reset').addEventListener('click', () => {
  stopCruise();
  fitAll(false);
  $('info-card').classList.remove('show');
  state.selectedIdx = -1;
});
$('ic-close').addEventListener('click', () => $('info-card').classList.remove('show'));
$('btn-list-toggle').addEventListener('click', () => {
  $('panel-list').classList.toggle('show');
  $('panel-ctrl').classList.remove('show');
});
$('btn-ctrl-toggle').addEventListener('click', () => {
  $('panel-ctrl').classList.toggle('show');
  $('panel-list').classList.remove('show');
});

/* 沿线巡航（聚焦线路） */
function stopCruise(){
  if (state.cruise){
    state.cruise = null;
    $('btn-cruise').textContent = '▶ 沿线巡航';
    controls.enabled = true;
  }
}
$('btn-cruise').addEventListener('click', () => {
  if (state.cruise){ stopCruise(); return; }
  if (state.focusIdx < 0){
    state.focusLineId = world.lines[0].id; $('sel-line').value = state.focusLineId;
    rebuild(true);
  }
  const lg = lineGroups[state.focusIdx];
  if (!lg){ stopCruise(); return; }
  controls.enabled = false;
  controls.autoRotate = false;
  state.cruise = { u: 0, curve: lg.group.userData.curve };
  $('btn-cruise').textContent = '⏸ 停止巡航';
  $('info-card').classList.remove('show');
});

/* ---------------- 渲染循环 ---------------- */
const clock = new THREE.Clock();
let introT = -1;
let __lastRaf = 0;
function renderFrame(dtOverride){
  const dt = Math.min(dtOverride ?? clock.getDelta(), 0.05);

  // 标签 LOD：聚焦时显示聚焦线全部标签；总览时只显示重点（换乘/高架/深≥20/端点）
  if (world){
    const focus = state.focusIdx;
    allLabels.forEach((lb, i) => {
      lb.visible = false;
      if (!state.labels) return;
      const u = globalLabelInfo[i];
      const line = world.lines[u.lineIdx];
      const st = line.stations[u.stIdx];
      const isFocusLine = focus < 0 || u.lineIdx === focus;
      if (!isFocusLine) return;
      const major = st.transfer || st.type === 'elevated' || (st.depth || 0) >= 20 ||
                    u.stIdx === 0 || u.stIdx === line.stations.length - 1;
      if (focus < 0 && !major) return;
      lb.visible = true;
    });
  }

  if (introT >= 0){
    introT += dt / 1.6;
    const t = 1 - Math.pow(1 - Math.min(introT,1), 3);
    camera.position.lerpVectors(introFrom, introTo, t);
    if (introT >= 1){ introT = -1; controls.enabled = true; }
  } else if (state.flyTo){
    state.flyTo.t += dt / 1.1;
    const t = 1 - Math.pow(1 - Math.min(state.flyTo.t,1), 3);
    camera.position.lerpVectors(state.flyTo.from, state.flyTo.to, t);
    controls.target.lerpVectors(state.flyTo.fromT, state.flyTo.toT, t);
    if (state.flyTo.t >= 1) state.flyTo = null;
  } else if (state.cruise){
    state.cruise.u += dt * 0.021;
    const u = Math.min(state.cruise.u, 1);
    const p = state.cruise.curve.getPointAt(u);
    const ahead = state.cruise.curve.getPointAt(Math.min(u+0.018, 1));
    camera.position.set(p.x, p.y + 18, p.z + 32);
    camera.lookAt(ahead.x, ahead.y - 4, ahead.z);
    if (state.cruise.u >= 1) stopCruise();
  }

  if (introT < 0 && !state.flyTo && !state.cruise) controls.update();
  renderer.render(scene, camera);
}
function animate(){
  requestAnimationFrame(animate);
  __lastRaf = performance.now();
  renderFrame();
}

/* ---------------- 启动 ---------------- */
populateSelectors();
rebuild();

// 开场
let introFrom, introTo;
{
  const dir = new THREE.Vector3(0.15, 0.55, 0.95).normalize();
  introTo = camera.position.clone();
  introFrom = world.center.clone().addScaledVector(dir, world.size * 2.2);
  introFrom.y = world.size * 1.05;
  camera.position.copy(introFrom);
  controls.enabled = false;
  introT = 0;
}

addEventListener('resize', () => {
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

setTimeout(() => { $('hint').style.opacity = '0'; }, 9000);

animate();
setInterval(() => { if (performance.now() - __lastRaf > 300) renderFrame(); }, 120);
document.getElementById('loading').classList.add('hide');