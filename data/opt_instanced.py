# -*- coding: utf-8 -*-
"""
中国城市地铁与超级桥梁 · 三维立体视图 —— 数据生成脚本
https://github.com/DeXuan/metro3d

MIT License - Copyright (c) 2026 DeXuan

免责声明：本脚本生成的数据仅供可视化演示与学习参考，禁止用于工程、施工、
测绘、导航或军事等专业用途。生成的埋深为示意值（非实测数据）。
详见 README「数据精度与使用限制」。

性能优化：站点球体/换乘环/地面环改为 InstancedMesh（大幅降低 draw calls）
"""
import io, re

HTML = 'index.html'
h = io.open(HTML, encoding='utf-8').read()
app = re.findall(r'<script type="module">(.*?)</script>', h, re.S)[1]

start = app.index('  // 站点：球体 + 垂线 + 地面环 + 换乘环 + 标签')
end = app.index('  ringMesh.instanceMatrix.needsUpdate = true;', start)
end = app.index('\n', end) + 1

new_seg = '''  // 站点：球体(instanced) + 垂线 + 地面环(instanced) + 换乘环(instanced) + 标签
  const sphereGeo = new THREE.SphereGeometry(1.75, 14, 10);
  const ringGeo = new THREE.RingGeometry(1.75, 2.5, 20); ringGeo.rotateX(-Math.PI/2);
  const torusGeo = new THREE.TorusGeometry(3.1, .36, 6, 20); torusGeo.rotateX(Math.PI/2);

  const markerMesh = new THREE.InstancedMesh(sphereGeo,
    new THREE.MeshStandardMaterial({ roughness: .3, metalness: .05 }), sts.length);
  markerMesh.instanceColor =
    new THREE.InstancedBufferAttribute(new Float32Array(sts.length * 3), 3);
  const ringMesh = new THREE.InstancedMesh(ringGeo,
    new THREE.MeshBasicMaterial({ transparent:true, opacity:.7, side:THREE.DoubleSide, depthWrite:false }),
    sts.length);
  const transferIdx = sts.map((a, i) => (a.st.transfer && a.st.transfer.length) ? i : -1).filter(i => i >= 0);
  const transferMesh = transferIdx.length
    ? new THREE.InstancedMesh(torusGeo,
        new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .85 }), transferIdx.length)
    : null;

  const dropPos = [];
  const M = new THREE.Matrix4();
  const tmpCol = new THREE.Color();
  const stMeta = [];   // 与 markerMesh 实例一一对应，供射线命中后的定位
  sts.forEach((a, i) => {
    const st = a.st, y = st._elev*V_SCALE;
    const col = state.depthColor ? depthColor(st._elev) : new THREE.Color(st.type==='elevated' ? ELEVATED_COLOR : line.color);
    M.makeTranslation(a.pos.x, y, a.pos.z);
    markerMesh.setMatrixAt(i, M);
    markerMesh.setColorAt(i, col);
    tmpCol.copy(col);
    stMeta.push({ x: a.pos.x, y, z: a.pos.z, lineIdx: li, stIdx: i });
    dropPos.push(a.pos.x, y, a.pos.z, a.pos.x, 0, a.pos.z);
    M.makeTranslation(a.pos.x, .1, a.pos.z);
    ringMesh.setMatrixAt(i, M);
    const sub = st.type==='elevated' ? `↑ 高架 ${st.height}m`
             : st.type==='ground' ? '地面'
             : `↓ ${st.depth}m${st.transfer ? ' · 换'+st.transfer.join('/') : ''}`;
    const lb = makeLabel(st.name, sub, st.type==='elevated' ? '#FFC44D' : '#9fd8ff');
    lb.position.set(a.pos.x, 3.6 + (i%2)*2.4, a.pos.z);
    group.add(lb); allLabels.push(lb);
    globalLabelInfo.push({ lineIdx: li, stIdx: i });
  });
  if (markerMesh.instanceColor){
    markerMesh.instanceColor.needsUpdate = true;
    markerMesh.material.emissive = new THREE.Color(0x1a2a3a);
    markerMesh.material.emissiveIntensity = 0.9;
  }
  transferIdx.forEach((si, k) => {
    const a = sts[si];
    M.makeTranslation(a.pos.x, a.st._elev*V_SCALE, a.pos.z);
    transferMesh.setMatrixAt(k, M);
  });
  markerMesh.instanceMatrix.needsUpdate = true;
  ringMesh.instanceMatrix.needsUpdate = true;
  if (transferMesh) transferMesh.instanceMatrix.needsUpdate = true;

  group.add(markerMesh);
  group.add(ringMesh);
  if (transferMesh) group.add(transferMesh);
  lineStMeta[line.id] = { mesh: markerMesh, meta: stMeta, transferMesh, transferIdx };
'''

app = app[:start] + new_seg + app[end:]

# 1) 声明 lineStMeta
app = app.replace(
  "let globalLabelInfo = [];                // 与 allLabels 一一对应 {lineIdx, stIdx}",
  "let globalLabelInfo = [];                // 与 allLabels 一一对应 {lineIdx, stIdx}\nlet lineStMeta = {};                     // lineId -> { mesh, meta[], transferMesh }")

# 2) buildWorld 清空 lineStMeta 与 allMarkers 语义
app = app.replace(
  "  allMarkers = []; allLabels = []; globalLabelInfo = [];",
  "  allMarkers = []; allLabels = []; globalLabelInfo = []; lineStMeta = {};")

# 3) 射线检测改为 InstancedMesh 命中
old_ray = """  ray.setFromCamera(ptr, camera);
  const hit = ray.intersectObjects(allMarkers, false);
  if (hit.length){
    const u = hit[0].object.userData;
    const line = world.lines[u.lineIdx];
    focusStation(line, u.stIdx);
  }"""
new_ray = """  ray.setFromCamera(ptr, camera);
  const meshes = Object.values(lineStMeta).map(x => x.mesh).filter(Boolean);
  const hit = ray.intersectObjects(meshes, false);
  if (hit.length){
    const h0 = hit[0];
    const lineId = Object.keys(lineStMeta).find(k => lineStMeta[k].mesh === h0.object);
    const sm = lineStMeta[lineId];
    if (sm && h0.instanceId !== undefined){
      const m = sm.meta[h0.instanceId];
      if (m){
        const line = world.lines[m.lineIdx];
        if (line) focusStation(line, m.stIdx);
      }
    }
  }"""
assert old_ray in app, 'ray block not found'
app = app.replace(old_ray, new_ray)

# 4) 删除对 allMarkers 的旧引用（其余地方）
app = app.replace("    marker.userData = { lineIdx: li, stIdx: i, lineId: line.id };\n    group.add(marker); allMarkers.push(marker);\n", "")
app = app.replace("  allMarkers.forEach(m => m.scale.setScalar(1));\n", "")

# 5) makeLineGroup 末尾 raw 返回：markers 字段改为空数组（保持兼容）
app = app.replace(
  "return { line, li, group, bbox, markers: group.children.filter(c => c.userData && c.userData.lineIdx === li),",
  "return { line, li, group, bbox, markers: [],")

prefix = h[:h.rindex('<script type="module">')]
suffix = h[h.rindex('</script>') + len('</script>'):]
out = prefix + '<script type="module">' + app + '</script>' + suffix
io.open(HTML, 'w', encoding='utf-8').write(out)
print('instanced optimization applied, size:', len(out))
scripts = re.findall(r'<script type="module">(.*?)</script>', out, re.S)
for i, s in enumerate(scripts):
    io.open('_chk%d.mjs' % i, 'w', encoding='utf-8').write(s)
print('scripts:', len(scripts))