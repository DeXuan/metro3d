# -*- coding: utf-8 -*-
"""地标建筑渲染：模型工厂 + 接入 buildWorld"""
import io, re

HTML = 'index.html'
h = io.open(HTML, encoding='utf-8').read()
app = re.findall(r'<script type="module">(.*?)</script>', h, re.S)[1]

# ============ 1) 地标模型工厂（插在 buildWorld 之前） ============
anchor = "function buildBridgeWorld(city, doFit = true){"
assert anchor in app
landmark_code = '''/* ================================================================
 * 地标建筑：用组合几何体塑造可辨识的城市地标
 *   类型：tv_tower / twist / taper / opener / pagoda / pavilion /
 *          castle / tower / gate / corn / ancient / wheel
 * ================================================================ */
function makeLandmarkMesh(type, hH, wW, colorStr){
  const grp = new THREE.Group();
  const main = new THREE.Color(colorStr || '#9fd3f0');
  const glass = new THREE.MeshStandardMaterial({
    color: main, emissive: main.clone().multiplyScalar(0.35), emissiveIntensity: 1.0,
    roughness: 0.28, metalness: 0.55 });
  const accent = new THREE.MeshStandardMaterial({
    color: 0xffd166, emissive: 0x8a6420, emissiveIntensity: 1.2, roughness: .3, metalness: .4 });
  const stone = new THREE.MeshStandardMaterial({
    color: 0xc8b898, emissive: 0x3a3020, emissiveIntensity: .8, roughness: .9 });
  const W = Math.max(1.2, wW);

  if (type === 'tv_tower'){
    // 三根斜柱 + 三球串塔 + 天线
    for (let i = 0; i < 3; i++){
      const a = i * Math.PI * 2 / 3;
      const leg = new THREE.Mesh(new THREE.CylinderGeometry(W * 0.16, W * 0.30, hH * 0.55, 6), glass);
      leg.position.set(Math.cos(a) * W * 0.5, hH * 0.275, Math.sin(a) * W * 0.5);
      leg.rotation.z = Math.cos(a) * 0.16;
      leg.rotation.x = -Math.sin(a) * 0.16;
      grp.add(leg);
    }
    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(W * 0.10, W * 0.14, hH * 0.92, 8), glass);
    shaft.position.y = hH * 0.46; grp.add(shaft);
    const balls = [[0.52, 0.30], [0.72, 0.20], [0.88, 0.13]];  // [y 比例, 半径比例]
    balls.forEach(([ry, rr]) => {
      const b = new THREE.Mesh(new THREE.SphereGeometry(W * rr * 1.5, 14, 10),
        new THREE.MeshStandardMaterial({ color: 0xe86a9a, emissive: 0x7a2048, emissiveIntensity: 1.1,
          roughness: .35, metalness: .5 }));
      b.position.y = hH * ry; grp.add(b);
    });
    const ant = new THREE.Mesh(new THREE.CylinderGeometry(W * 0.04, W * 0.07, hH * 0.16, 6), accent);
    ant.position.y = hH * 0.96; grp.add(ant);
  } else if (type === 'twist'){
    // 扭转上升：多段方形逐层旋转 + 收分
    const N = 12;
    for (let i = 0; i < N; i++){
      const t = i / N;
      const side = W * (1 - t * 0.45);
      const seg = new THREE.Mesh(new THREE.BoxGeometry(side, hH / N * 1.02, side), glass);
      seg.position.y = hH * (t + 0.5 / N);
      seg.rotation.y = t * 0.9;
      grp.add(seg);
    }
    const tip = new THREE.Mesh(new THREE.ConeGeometry(W * 0.28, hH * 0.10, 8), glass);
    tip.position.y = hH * 1.03; grp.add(tip);
  } else if (type === 'taper'){
    // 收分塔楼（下宽上窄）+ 顶部锥
    const N = 7;
    for (let i = 0; i < N; i++){
      const t = i / N;
      const side = W * (1 - t * 0.62);
      const seg = new THREE.Mesh(new THREE.BoxGeometry(side, hH / N * 1.02, side), glass);
      seg.position.y = hH * (t + 0.5 / N);
      grp.add(seg);
    }
    const tip = new THREE.Mesh(new THREE.ConeGeometry(W * 0.19, hH * 0.09, 4), glass);
    tip.position.y = hH * 1.02; grp.add(tip);
  } else if (type === 'opener'){
    // 开瓶器：主楼 + 顶部两侧立柱 + 横梁（中间留洞）
    const body = new THREE.Mesh(new THREE.BoxGeometry(W, hH * 0.84, W * 0.7), glass);
    body.position.y = hH * 0.42; grp.add(body);
    [-1, 1].forEach(s => {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(W * 0.22, hH * 0.2, W * 0.6), glass);
      leg.position.set(s * W * 0.39, hH * 0.92, 0); grp.add(leg);
    });
    const bridge = new THREE.Mesh(new THREE.BoxGeometry(W, hH * 0.09, W * 0.6), glass);
    bridge.position.y = hH * 0.99; grp.add(bridge);
  } else if (type === 'pagoda'){
    // 阶梯塔楼（金茂式）
    const N = 6;
    for (let i = 0; i < N; i++){
      const t = i / N;
      const side = W * (1 - t * 0.55);
      const seg = new THREE.Mesh(new THREE.BoxGeometry(side, hH / N * 1.04, side), glass);
      seg.position.y = hH * (t + 0.5 / N) ;
      grp.add(seg);
    }
    const crown = new THREE.Mesh(new THREE.ConeGeometry(W * 0.2, hH * 0.12, 6), accent);
    crown.position.y = hH * 1.03; grp.add(crown);
  } else if (type === 'pavilion'){
    // 斗拱倒锥（世博中国馆 / 环球中心）
    const base = new THREE.Mesh(new THREE.CylinderGeometry(W * 0.55, W * 0.75, hH * 0.25, 6), glass);
    base.position.y = hH * 0.125; grp.add(base);
    const body = new THREE.Mesh(new THREE.ConeGeometry(W * 1.05, hH * 0.7, 4, 1, true), glass);
    body.rotation.y = Math.PI / 4;
    body.position.y = hH * 0.60; grp.add(body);
    const cap = new THREE.Mesh(new THREE.BoxGeometry(W * 0.7, hH * 0.08, W * 0.7), glass);
    cap.position.y = hH * 0.98; grp.add(cap);
  } else if (type === 'castle'){
    // 城堡：中心塔 + 四角塔楼 + 尖顶
    const keep = new THREE.Mesh(new THREE.CylinderGeometry(W * 0.5, W * 0.55, hH * 0.7, 10), stone);
    keep.position.y = hH * 0.35; grp.add(keep);
    const roof = new THREE.Mesh(new THREE.ConeGeometry(W * 0.58, hH * 0.35, 10), accent);
    roof.position.y = hH * 0.875; grp.add(roof);
    [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([sx, sz]) => {
      const tw = new THREE.Mesh(new THREE.CylinderGeometry(W * 0.18, W * 0.2, hH * 0.5, 8), stone);
      tw.position.set(sx * W * 0.62, hH * 0.25, sz * W * 0.62); grp.add(tw);
      const tr = new THREE.Mesh(new THREE.ConeGeometry(W * 0.24, hH * 0.22, 8), accent);
      tr.position.set(sx * W * 0.62, hH * 0.61, sz * W * 0.62); grp.add(tr);
    });
  } else if (type === 'gate'){
    // 门形双塔：两根斜柱 + 顶部连接
    [-1, 1].forEach(s => {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(W * 0.28, hH * 0.92, W * 0.5), glass);
      leg.position.set(s * W * 0.55, hH * 0.46, 0);
      leg.rotation.z = -s * 0.10;
      grp.add(leg);
    });
    const top = new THREE.Mesh(new THREE.BoxGeometry(W * 1.25, hH * 0.10, W * 0.5), glass);
    top.position.y = hH * 0.96; grp.add(top);
  } else if (type === 'corn'){
    // 椭圆塔（大玉米式）
    const body = new THREE.Mesh(new THREE.CylinderGeometry(W * 0.42, W * 0.55, hH * 0.9, 12), glass);
    body.position.y = hH * 0.45; grp.add(body);
    const top = new THREE.Mesh(new THREE.SphereGeometry(W * 0.44, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2), accent);
    top.position.y = hH * 0.9; grp.add(top);
  } else if (type === 'ancient'){
    // 仿古：台基 + 多层塔身 + 攒尖顶
    const base = new THREE.Mesh(new THREE.BoxGeometry(W * 1.6, hH * 0.16, W * 1.6), stone);
    base.position.y = hH * 0.08; grp.add(base);
    const body = new THREE.Mesh(new THREE.BoxGeometry(W * 1.1, hH * 0.5, W * 1.1), stone);
    body.position.y = hH * 0.41; grp.add(body);
    const roof1 = new THREE.Mesh(new THREE.ConeGeometry(W * 0.95, hH * 0.22, 4), accent);
    roof1.rotation.y = Math.PI / 4; roof1.position.y = hH * 0.77; grp.add(roof1);
    const roof2 = new THREE.Mesh(new THREE.ConeGeometry(W * 0.68, hH * 0.18, 4), accent);
    roof2.rotation.y = Math.PI / 4; roof2.position.y = hH * 0.92; grp.add(roof2);
    const fin = new THREE.Mesh(new THREE.SphereGeometry(W * 0.10, 8, 6), accent);
    fin.position.y = hH * 1.01; grp.add(fin);
  } else if (type === 'wheel'){
    // 环形雕塑（五月的风）
    const torus = new THREE.Mesh(new THREE.TorusGeometry(W * 0.75, W * 0.16, 10, 28),
      new THREE.MeshStandardMaterial({ color: main, emissive: main.clone().multiplyScalar(.4),
        emissiveIntensity: 1.1, roughness: .35, metalness: .45 }));
    torus.position.y = hH * 0.55; grp.add(torus);
    const base = new THREE.Mesh(new THREE.CylinderGeometry(W * 0.5, W * 0.7, hH * 0.12, 10), stone);
    base.position.y = hH * 0.06; grp.add(base);
  } else {
    // 通用高层：柱体 + 顶部装饰
    const body = new THREE.Mesh(new THREE.BoxGeometry(W, hH, W * 0.75), glass);
    body.position.y = hH * 0.5; grp.add(body);
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(W * 0.06, W * 0.4, hH * 0.06, 6), accent);
    cap.position.y = hH * 1.02; grp.add(cap);
  }
  return grp;
}

function buildCityLandmarks(city, origin){
  if (!city.landmarks || !city.landmarks.length) return null;
  const grp = new THREE.Group();
  // 地标真实高度 × 夸张倍率（线网尺度下才可见；与示意建筑群 3.2× 区分，用 8×）
  const K = 8.0;
  city.landmarks.forEach(lm => {
    const p = project(lm.lng, lm.lat, origin);
    const hH = Math.max(3, lm.h * H_SCALE * K);          // 世界高度
    const wW = Math.max(2.2, hH * 0.16);                 // 世界宽度（按高度推断）
    const mesh = makeLandmarkMesh(lm.type, hH, wW, lm.color);
    mesh.position.set(p.x, 0, p.z);
    mesh.userData.landmark = lm;
    grp.add(mesh);
    // 地面光环（标示位置）
    const ring = new THREE.Mesh(new THREE.RingGeometry(wW * 0.9, wW * 1.25, 24),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(lm.color || '#9fd3f0'),
        transparent: true, opacity: .5, side: THREE.DoubleSide, depthWrite: false }));
    ring.rotation.x = -Math.PI / 2;
    ring.position.set(p.x, 0.35, p.z);
    grp.add(ring);
    // 名称 + 高度标注
    const lb = makeLabel(lm.name, lm.desc || `${lm.h}m`, lm.color || '#9fd3f0');
    lb.position.set(p.x, hH + 4.5, p.z);
    lb.scale.set(17, 5.4, 1);
    lb.userData.alwaysVisible = true;
    grp.add(lb);
    allLabels.push(lb);
    globalLabelInfo.push({ landmark: true });
  });
  return grp;
}

function buildBridgeWorld(city, doFit = true){'''
app = app.replace(anchor, landmark_code, 1)

# ============ 2) buildWorld 里接入（环境层建筑群之后） ============
old = "    const river = buildRiver(origin, city);\n    if (river) grouped.add(river);\n    grouped.add(buildBuildings(origin, lines));"
assert old in app
app = app.replace(old, "    const river = buildRiver(origin, city);\n    if (river) grouped.add(river);\n    grouped.add(buildBuildings(origin, lines));\n    const lms = buildCityLandmarks(city, origin);\n    if (lms) grouped.add(lms);")

# ============ 3) 标签 LOD：地标标签始终可见 ============
old2 = """      const u = globalLabelInfo[i];
      if (!u) return;
      const line = world.lines[u.lineIdx];"""
assert old2 in app
app = app.replace(old2, """      const u = globalLabelInfo[i];
      if (!u) return;
      if (u.landmark){ lb.visible = true; return; }   // 地标标签常显
      const line = world.lines[u.lineIdx];""")

# ============ 4) 图例加入地标说明 ============
old3 = """  $('legend').innerHTML = html;"""
assert old3 in app
app = app.replace(old3, """  if (world.city.landmarks && world.city.landmarks.length && !state.depthColor){
    html += `<div class="lg-row" style="font-size:10px;margin-top:4px">◆ 地标建筑 ${world.city.landmarks.length} 座（名称+高度标注）</div>`;
  }
  $('legend').innerHTML = html;""")

io.open('index.html', 'w', encoding='utf-8').write(
    h[:h.rindex('<script type="module">')] + '<script type="module">' + app + '</script>' +
    h[h.rindex('</script>') + len('</script>'):])
print('landmark rendering integrated')
scripts = re.findall(r'<script type="module">(.*?)</script>', io.open('index.html', encoding='utf-8').read(), re.S)
for i, s in enumerate(scripts):
    io.open('_chk%d.mjs' % i, 'w', encoding='utf-8').write(s)
print('scripts:', len(scripts))