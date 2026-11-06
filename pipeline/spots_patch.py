"""길 위 명소 (2026-11-06 승연 '제안해준 곳으로 진행해줘')

mountains/<id>.json 경유지에 "spot": {"type": ..., ...} 을 달면 그 경유지 근처에 실제 명소를 단순한 3D로 다시 만들어요.
(사진을 붙인 게 아니라 실제 모양을 본떠 만든 것이에요. 탐방로·숨은 길은 막지 않아요.)

type
- railing   : 쇠기둥·쇠줄 난간 + 매끈한 화강암 너럭바위 (북한산 위문~백운대)
- blade     : 칼날처럼 솟은 큰 바위 (지리산 칼바위)
- columns   : 육각 돌기둥 (mode wall = 병풍처럼 늘어선 절벽, stand = 따로 선 돌기둥 무리) (무등산 입석대·서석대, 한라산 병풍바위)
- pavilion  : 연못 + 육각 정자 + 작은 다리 (내장산 우화정)
- yews      : 오래된 주목 군락 + 하얀 고사목 (소백산·태백산)
- seracs    : 빙하 얼음 탑 + 빙하 호수 (에베레스트 쿰부)
- huts      : 돌담을 두른 작은 산장 줄 (후지산 7·8합목)
- icewall   : 층진 빙벽 (킬리만자로)
- chapel    : 호수 + 하얀 예배당 (마터호른 슈바르츠제)
- lake      : 산이 비치는 작은 호수 (몽블랑 락 데 슈제르)
- stairs    : 화강암을 깎은 돌계단 (하프돔 서브돔)
- pine      : 바위 위에서 가지를 길게 뻗은 소나무 (황산 영객송)
- boulders  : 큰 바윗덩이 비탈 (토레스 델 파이네)
공통 옵션: at (경유지에서 탐방로 점 몇 개 앞/뒤), D (탐방로에서 떨어진 거리 m), side (1/-1, 없으면 낮은 쪽)
"""
import json

SPOT_JS = r"""
// ---------- 길 위 명소 (pipeline/spots_patch.py) ----------
{ const SPOTS = __SPOTS__;
  let rs = 7919; const rnd = () => (rs = (rs * 16807) % 2147483647) / 2147483647, R = (a, b) => a + rnd()*(b - a);
  const V3 = THREE.Vector3;
  const rockGeo = []; for(let k = 0; k < 4; k++){ const g = new THREE.SphereGeometry(1, 20, 12), P = g.attributes.position, a = 1.3 + k*0.4, s1 = k*1.7, s2 = k*2.3 + 1;
    for(let j = 0; j < P.count; j++){ const x = P.getX(j), y = P.getY(j), z = P.getZ(j);
      const n = 1 + 0.13*Math.sin(x*a*2.1 + s1)*Math.cos(z*a*1.7 + s2) + 0.08*Math.sin(y*a*3.3 + z*2.2 + s1) + 0.05*Math.sin((x + y)*6.1 + s2);
      const fl = y > 0.55 ? 0.55 + (y - 0.55)*0.35 : y; P.setXYZ(j, x*n, fl*n, z*n); }
    g.computeVertexNormals(); rockGeo.push(g); }
  const MC = {}; const mat = (c, o) => { const k = c + JSON.stringify(o || {}); return MC[k] || (MC[k] = new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.9 }, o || {}))); };
  const rockM = c => mat(c, { map: TEX.granite });
  const trailD = (x, z) => { const r = nearTrail(x, z, 2); return r.i < 0 ? 1e9 : r.d; };
  const sideD = (x, z) => { try{ return window.__SIDE && window.__SIDE.on && !window.__SIDE.following ? (window.__SIDE.on(x, z) ? 0 : 1e9) : 1e9; }catch(_){ return 1e9; } };
  const free = (x, z, r) => trailD(x, z) > r + 2.2;
  // 탐방로 i 지점 기준 틀: 로컬 x = 길 방향, z = 길에서 멀어지는 쪽
  const frame = (i, D, side) => { i = Math.max(1, Math.min(trail.length - 2, i)); const p = trail[i], a0 = trail[Math.max(0, i - 6)], a1 = trail[Math.min(trail.length - 1, i + 6)];
    let tx = a1.x - a0.x, tz = a1.z - a0.z; const tl = Math.hypot(tx, tz) || 1; tx /= tl; tz /= tl; const nx = -tz, nz = tx, hp = heightAt(p.x, p.z);
    if(!side){ const dif = s => { let m = 0; for(const d of [D*0.4, D*0.7, D]) m = Math.max(m, heightAt(p.x + nx*d*s, p.z + nz*d*s) - hp); return m; }; side = dif(1) <= dif(-1) ? 1 : -1; }
    const cx = p.x + nx*side*D, cz = p.z + nz*side*D;
    const G = new THREE.Group(); G.position.set(cx, heightAt(cx, cz), cz); G.rotation.y = Math.atan2(nx*side, nz*side); G.updateMatrixWorld(true); scene.add(G);
    const w = (lx, lz) => { const v = new V3(lx, 0, lz); G.localToWorld(v); return v; };
    return { G, i, side, p, w, gy: (lx, lz) => { const v = w(lx, lz); return heightAt(v.x, v.z) - G.position.y; }, ok: (lx, lz, r) => { const v = w(lx, lz); return free(v.x, v.z, r); } };
  };
  const add = (G, geo, m, x, y, z, s, ry) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); if(s) (typeof s === 'number' ? o.scale.setScalar(s) : o.scale.set(s[0], s[1], s[2])); if(ry) o.rotation.y = ry; o.castShadow = o.receiveShadow = true; G.add(o); return o; };
  const rock = (F, w, h, d, x, z, c, sink) => { if(!F.ok(x, z, Math.max(w, d))) return null; return add(F.G, rockGeo[(rnd()*4)|0], rockM(c), x, F.gy(x, z) + h*(sink ?? 0.35), z, [w, h, d], rnd()*6.28); };
  // 명소 자리의 나무·풀 치우기 (로컬 판정 함수)
  const clear = (G, inside) => { const M = new THREE.Matrix4(), Z = new THREE.Matrix4().makeScale(0, 0, 0), v = new V3(), inv = new THREE.Matrix4().copy(G.matrixWorld).invert();
    scene.traverse(o => { if(!o.isInstancedMesh || o.parent === G) return; let ch = false; for(let k = 0; k < o.count; k++){ o.getMatrixAt(k, M); v.setFromMatrixPosition(M); v.applyMatrix4(inv); if(inside(v.x, v.z)){ o.setMatrixAt(k, Z); ch = true; } } if(ch) o.instanceMatrix.needsUpdate = true; }); };
  const water = (G, r, x, z, y, c, o) => { const m = new THREE.Mesh(new THREE.CircleGeometry(r, 48), new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.08, metalness: 0.15, transparent: true, opacity: 0.93 }, o || {}))); m.rotation.x = -Math.PI/2; m.position.set(x, y, z); m.receiveShadow = true; G.add(m); return m; };
  const lakeLevel = (F, r, x, z) => { const h = []; for(let k = 0; k < 20; k++){ const an = k/20*6.283; h.push(F.gy(x + Math.cos(an)*r, z + Math.sin(an)*r)); } h.sort((a, b) => a - b); return h[Math.floor(h.length*0.35)] + 0.15; };
  const shore = (F, r, x, z, y, c, n) => { for(let k = 0; k < n; k++){ const an = k/n*6.283 + rnd()*0.2, rr = r + R(0.2, 1.2), px = x + Math.cos(an)*rr, pz = z + Math.sin(an)*rr, g = F.gy(px, pz); const sz = R(0.6, 1.6), top = Math.max(sz*0.6, y - g + 0.5);
      if(F.ok(px, pz, sz)) add(F.G, rockGeo[(rnd()*4)|0], rockM(c), px, Math.min(g, y) + top*0.3, pz, [sz*1.3, Math.max(sz, top), sz], rnd()*6.28); } };
  const tube = (pts, r0, r1, seg) => { const c = new THREE.CatmullRomCurve3(pts), g = new THREE.TubeGeometry(c, seg || 16, 1, 7, false), P = g.attributes.position, N = (seg || 16) + 1;
    // 굵기: 아래 r0 → 위 r1
    const C = new V3(), tmp = new V3(); for(let s = 0; s < N; s++){ c.getPointAt(s/(N - 1), C); const rr = r0 + (r1 - r0)*s/(N - 1); for(let j = 0; j <= 7; j++){ const k = s*8 + j; tmp.fromBufferAttribute(P, k).sub(C).multiplyScalar(rr).add(C); P.setXYZ(k, tmp.x, tmp.y, tmp.z); } }
    g.computeVertexNormals(); return g; };
  const needle = () => { const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'); x.fillStyle = '#1d3320'; x.fillRect(0, 0, 128, 128);
    for(let k = 0; k < 900; k++){ const X = rnd()*128, Y = rnd()*128, a = rnd()*6.28, L = 3 + rnd()*6; x.strokeStyle = ['#2f5a33', '#3d6b3c', '#14261a', '#4a7a45'][(rnd()*4)|0]; x.lineWidth = 1 + rnd(); x.beginPath(); x.moveTo(X, Y); x.lineTo(X + Math.cos(a)*L, Y + Math.sin(a)*L); x.stroke(); }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(3, 3); t.colorSpace = THREE.SRGBColorSpace; return t; };
  const B = {
    railing(W, S){ const i0 = W.i + (S.from ?? -40), i1 = Math.min(trail.length - 20, S.to === 'end' ? 1e9 : W.i + (S.to ?? 60)); const G = new THREE.Group(); scene.add(G); const F0 = { G };
      const postM = mat(0x3b3d40, { metalness: 0.6, roughness: 0.4 }), postG = new THREE.CylinderGeometry(0.045, 0.055, 1.15, 8), tops = [];
      for(let i = i0; i <= i1; i += 2){ const a = trail[Math.max(0, i - 2)], b = trail[i + 2], p = trail[i]; let tx = b.x - a.x, tz = b.z - a.z; const l = Math.hypot(tx, tz) || 1; tx /= l; tz /= l;
        const x = p.x - tz*1.15, z = p.z + tx*1.15, y = heightAt(x, z); add(G, postG, postM, x, y + 0.5, z); tops.push(new V3(x, y + 1.05, z)); }
      const chM = mat(0x55585c, { metalness: 0.7, roughness: 0.35 });
      for(let k = 0; k + 1 < tops.length; k++){ const a = tops[k], b = tops[k + 1], m = a.clone().lerp(b, 0.5); m.y -= 0.12; G.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.QuadraticBezierCurve3(a, m, b), 6, 0.018, 5, false), chM)); }
      // 너럭바위: 길 양옆에 낮고 넓은 화강암
      for(let i = i0; i <= i1; i += 7){ const p = trail[i]; for(const s of [-1, 1]){ const a = trail[Math.max(0, i - 2)], b = trail[i + 2]; let tx = b.x - a.x, tz = b.z - a.z; const l = Math.hypot(tx, tz) || 1; tx /= l; tz /= l;
          const d = R(2.6, 5), x = p.x - tz*s*d, z = p.z + tx*s*d; if(!free(x, z, 0.4)) continue; const w = R(1.4, 2.6); add(G, rockGeo[(rnd()*4)|0], rockM(0xd8d2c6), x, heightAt(x, z) - 0.15, z, [w, R(0.35, 0.7), w*R(0.7, 1.1)], rnd()*6.28); } }
      return { x: trail[W.i].x, z: trail[W.i].z }; },
    blade(W, S){ const F = frame(W.i + (S.at || 0), S.D || 12, S.side); const G = F.G, c = S.color ? parseInt(S.color.slice(1), 16) : 0x9d978c;
      const h = S.h || 14; add(G, rockGeo[1], rockM(c), 0, h*0.42, 0, [1.3, h*0.55, 3.2], 0.15).rotation.z = 0.12;
      add(G, rockGeo[2], rockM(c), 1.6, h*0.3, 0.8, [1.0, h*0.38, 2.4], -0.2).rotation.z = -0.1;
      for(let k = 0; k < 8; k++) rock(F, R(1, 2.4), R(0.7, 1.6), R(1, 2.2), R(-5, 5), R(-4, 4), c);
      clear(G, (x, z) => Math.hypot(x, z) < 6.5); return F.w(0, 0); },
    columns(W, S){ const F = frame(W.i + (S.at || 0), S.D || 22, S.side); const G = F.G, c = S.color ? parseInt(S.color.slice(1), 16) : 0x837c71;
      const m = mat(c, { map: TEX.granite, roughness: 0.88 }), H = S.h || 14, n = S.n || 26, wall = S.mode !== 'stand';
      // 돌기둥 원형: 육각 단면 + 가로 마디(절리)가 살짝 어긋나요
      const colGeo = []; for(let k = 0; k < 4; k++){ const g = new THREE.CylinderGeometry(1, 1, 1, 6, 10), P = g.attributes.position; g.translate(0, 0.5, 0);
        for(let j = 0; j < P.count; j++){ const y = P.getY(j), seg = Math.floor(y*10), sh = 0.06*Math.sin(seg*2.3 + k*1.7), n2 = 1 + sh + 0.04*Math.sin(Math.atan2(P.getZ(j), P.getX(j))*3 + seg);
          P.setX(j, P.getX(j)*n2 + 0.03*Math.sin(seg*1.1 + k)); P.setZ(j, P.getZ(j)*n2); if(y > 0.99) P.setY(j, 1 + 0.08*Math.sin(P.getX(j)*3 + k)); }
        g.computeVertexNormals(); colGeo.push(g); }
      const rows = wall ? (S.rows || 3) : 1;
      for(let row = 0; row < rows; row++) for(let k = 0; k < n; k++){ let x, z, h; const r = R(0.9, 1.6);
        if(wall){ x = (k - n/2)*(S.mode === 'spires' ? 3.2 : 2.3) + R(-0.4, 0.4) + row*1.1; z = -row*2.6 + R(-0.5, 0.5) + Math.abs(x)*0.06; h = H*(0.5 + 0.25*Math.sin(k*0.55 + row) + 0.35*rnd())*(1 + row*0.25); }
        else { if(row) break; const an = R(-1.3, 1.3), rr = R(2, 10); x = Math.sin(an)*rr; z = Math.cos(an)*rr*0.7 - 3; h = H*R(0.5, 1); }
        if(!F.ok(x, z, r)) continue; const g0 = F.gy(x, z) - 2;
        if(S.mode === 'spires'){ const w = R(1.8, 3.2); add(G, rockGeo[(rnd()*4)|0], m, x, g0 + h*0.5, z, [w, h*0.62, w*R(0.8, 1.15)], rnd()*6); continue; }
        const o = add(G, colGeo[(rnd()*4)|0], m, x, g0, z, [r, h + 2, r*R(0.85, 1.1)], rnd()*6);
        o.rotation.z = R(-0.035, 0.035); o.rotation.x = R(-0.035, 0.035); }
      for(let k = 0; k < 12; k++) rock(F, R(0.6, 1.4), R(0.4, 0.8), R(0.6, 1.4), R(-n*0.6, n*0.6), R(1.5, 5), c);   // 무너진 돌기둥 조각
      clear(G, (x, z) => Math.abs(x) < n*0.85 + 2 && z > -4 && z < 7); return F.w(0, 0); },
    pavilion(W, S){ const F = frame(W.i + (S.at || 0), S.D || 20, S.side); const G = F.G, PR = 9; const L = lakeLevel(F, PR, 0, 0);
      water(G, PR, 0, 0, L, 0x2f4f3c, { roughness: 0.06 }); shore(F, PR, 0, 0, L, 0x8f897d, 26);
      const P = new THREE.Group(); P.position.set(0, L, 0); G.add(P); const wood = mat(0x7e2f22, { roughness: 0.7 }), tile = mat(0x3d4044, { roughness: 0.75 }), floor = mat(0x6b5440);
      add(P, new THREE.CylinderGeometry(2.9, 2.9, 0.35, 6), floor, 0, 0.6, 0); add(P, new THREE.CylinderGeometry(2.6, 2.8, 0.8, 6), mat(0x8f897d, { map: TEX.granite }), 0, 0.1, 0);
      for(let k = 0; k < 6; k++){ const an = k/6*6.283; add(P, new THREE.CylinderGeometry(0.13, 0.15, 2.6, 8), wood, Math.cos(an)*2.4, 2.05, Math.sin(an)*2.4); }
      add(P, new THREE.CylinderGeometry(2.7, 2.7, 0.25, 6), wood, 0, 3.4, 0);
      const roof = new THREE.ConeGeometry(3.9, 1.9, 6, 1, true), rp = roof.attributes.position; for(let j = 0; j < rp.count; j++){ const y = rp.getY(j); if(y < 0){ const x = rp.getX(j), z = rp.getZ(j); rp.setY(j, y + 0.35*Math.hypot(x, z)/3.9); } } roof.computeVertexNormals();   // 처마 끝이 살짝 들려요
      const rf = add(P, roof, mat(0x3d4044, { roughness: 0.75, side: THREE.DoubleSide }), 0, 4.45, 0); add(P, new THREE.SphereGeometry(0.22, 10, 8), tile, 0, 5.45, 0);
      // 다리: 연못가 → 정자
      add(G, new THREE.BoxGeometry(1.4, 0.18, PR - 2.6), floor, 0, L + 0.55, -(PR + 2.6)/2 + 0.2);
      clear(G, (x, z) => Math.hypot(x, z) < PR + 2.5); return F.w(0, 0); },
    yews(W, S){ const i0 = W.i + (S.from ?? -40), i1 = Math.min(trail.length - 2, W.i + (S.to ?? 20)), G = new THREE.Group(); scene.add(G);
      const bark = mat(0x6e3a26, { roughness: 0.95 }), dead = mat(0xd9d3c7, { roughness: 0.9 }), leaf = new THREE.MeshStandardMaterial({ map: needle(), color: 0x9fb39a, roughness: 0.95 }), leaf2 = new THREE.MeshStandardMaterial({ map: needle(), color: 0x7f9a7c, roughness: 0.95 }), lg = new THREE.IcosahedronGeometry(1, 2);
      const clump = (x, y, z, r) => { for(let q = 0; q < 7; q++) add(G, lg, rnd() < 0.5 ? leaf : leaf2, x + R(-r, r), y + R(-r*0.3, r*0.5), z + R(-r, r), [R(0.45, 0.8)*r, R(0.35, 0.55)*r, R(0.45, 0.8)*r]); };
      const n = S.n || 12, snag = S.snags ?? 0.3; let made = 0, first = null;
      for(let t = 0; t < n*4 && made < n; t++){ const i = Math.floor(R(i0, i1)), p = trail[i], a = trail[Math.max(0, i - 2)], b = trail[Math.min(trail.length - 1, i + 2)]; let tx = b.x - a.x, tz = b.z - a.z; const l = Math.hypot(tx, tz) || 1; tx /= l; tz /= l;
        const s = rnd() < 0.5 ? -1 : 1, d = R(4.5, 14), x = p.x - tz*s*d, z = p.z + tx*s*d; if(!free(x, z, 2)) continue; made++; if(!first) first = { x, z };
        const y = heightAt(x, z), h = R(2.8, 4.6), lean = R(-0.9, 0.9), isDead = rnd() < snag, pts = [];
        for(let k = 0; k <= 4; k++){ const f = k/4; pts.push(new V3(x + Math.sin(f*2.2 + lean)*0.6*f + lean*f, y - 0.3 + f*h, z + Math.cos(f*1.7)*0.5*f)); }
        const tr = new THREE.Mesh(tube(pts, R(0.32, 0.55), 0.12, 14), isDead ? dead : bark); tr.castShadow = true; G.add(tr);
        for(let k = 0; k < 3; k++){ const f = R(0.45, 0.85), st0 = pts[Math.round(f*4)], dir = R(0, 6.28), L2 = R(1.2, 2.6);
          const br = new THREE.Mesh(tube([st0, new V3(st0.x + Math.cos(dir)*L2*0.6, st0.y + R(0.2, 0.8), st0.z + Math.sin(dir)*L2*0.6), new V3(st0.x + Math.cos(dir)*L2, st0.y + R(0.4, 1.2), st0.z + Math.sin(dir)*L2)], 0.12, 0.04, 6), isDead ? dead : bark); br.castShadow = true; G.add(br);
          if(!isDead) clump(st0.x + Math.cos(dir)*L2, st0.y + 0.6, st0.z + Math.sin(dir)*L2, R(1.1, 1.5)); }
        if(!isDead) clump(pts[4].x, pts[4].y + 0.2, pts[4].z, R(1.3, 1.8)); }
      return first || { x: trail[W.i].x, z: trail[W.i].z }; },
    seracs(W, S){ const F = frame(W.i + (S.at || 0), S.D || 30, S.side); const G = F.G, ice = mat(0xa9d0de, { roughness: 0.3, metalness: 0.05, emissive: 0x0e2a38, emissiveIntensity: 0.3, flatShading: true }), ice2 = mat(0xdcecf2, { roughness: 0.4, flatShading: true });
      const ig = []; for(let k = 0; k < 3; k++){ const g = new THREE.IcosahedronGeometry(1, 1), P = g.attributes.position; for(let j = 0; j < P.count; j++){ const x = P.getX(j), y = P.getY(j), z = P.getZ(j), n = 1 + 0.2*Math.sin(x*3 + k)*Math.cos(z*2.7 + y*2 + k); P.setXYZ(j, x*n, y*n, z*n); } g.computeVertexNormals(); ig.push(g); }
      for(let k = 0; k < (S.n || 26); k++){ const x = R(-30, 30), z = R(-6, 16), h = R(4, 14), w = R(1.6, 4); if(!F.ok(x, z, w)) continue; add(G, ig[k % 3], k % 3 ? ice : ice2, x, F.gy(x, z) + h*0.45, z, [w, h, w*R(0.6, 1.1)], rnd()*6).rotation.z = R(-0.15, 0.15); }
      const L = lakeLevel(F, 7, 0, -9); if(F.ok(0, -9, 7)) water(G, 7, 0, -9, L, 0x5aa5ad, { roughness: 0.05 });
      clear(G, (x, z) => Math.abs(x) < 33 && z > -16 && z < 19); return F.w(0, 0); },
    huts(W, S){ const G = new THREE.Group(); scene.add(G); const wall = mat(0x8a6446, { roughness: 0.85 }), win = mat(0x2e3a44, { roughness: 0.3, metalness: 0.3 }), trim = mat(0xe9e3d6), roofs = [mat(0x7a2e24, { roughness: 0.6, metalness: 0.2 }), mat(0x5e5a55, { roughness: 0.6, metalness: 0.2 })], stone = mat(0x9a9088, { map: TEX.granite }), sign = mat(0xf2ead8);
      const n = S.n || 3; let made = 0;
      for(let t = 0; t < 30 && made < n; t++){ const i = W.i + (S.at || 0) + (made - (n - 1)/2)*(S.gap || 14) + Math.round(R(-2, 2)); if(i < 2 || i > trail.length - 3) continue; const p = trail[i], a = trail[i - 2], b = trail[i + 2]; let tx = b.x - a.x, tz = b.z - a.z; const l = Math.hypot(tx, tz) || 1; tx /= l; tz /= l;
        const s = (S.side || 1)*((t % 2) ? -1 : 1), d = 6.5, x = p.x - tz*s*d, z = p.z + tx*s*d; if(!free(x, z, 3.2)) continue; made++;
        const y = heightAt(x, z), H = G.add(new THREE.Group()) && G.children[G.children.length - 1]; H.position.set(x, y, z); H.rotation.y = Math.atan2(-tz*s, tx*s) + Math.PI/2;
        add(H, new THREE.BoxGeometry(7, 3.6, 4.5), stone, 0, -1.4, 0);                 // 비탈을 받친 돌 기초
        add(H, new THREE.BoxGeometry(6.4, 2.6, 4), wall, 0, 1.6, 0);
        const r1 = add(H, new THREE.BoxGeometry(7, 0.18, 2.6), roofs[made % 2], 0, 3.25, 1.05); r1.rotation.x = 0.32; const r2 = add(H, new THREE.BoxGeometry(7, 0.18, 2.6), roofs[made % 2], 0, 3.25, -1.05); r2.rotation.x = -0.32;
        add(H, new THREE.BoxGeometry(2.4, 0.55, 0.08), sign, 0, 2.55, 2.05);           // 산장 간판
        for(const wx of [-2.2, 2.2]){ add(H, new THREE.BoxGeometry(1.1, 0.8, 0.06), win, wx, 1.7, 2.03); add(H, new THREE.BoxGeometry(1.3, 0.1, 0.1), trim, wx, 1.25, 2.05); }
        add(H, new THREE.BoxGeometry(1, 1.9, 0.06), mat(0x5a3b28), 0, 1.25, 2.03);
        add(H, new THREE.BoxGeometry(6.8, 0.9, 0.5), stone, 0, 0.1, 2.6);            // 앞 돌담
      }
      return { x: trail[W.i].x, z: trail[W.i].z }; },
    icewall(W, S){ const F = frame(W.i + (S.at || 0), S.D || 45, S.side); const G = F.G;
      const ic = document.createElement('canvas'); ic.width = 128; ic.height = 256; { const x = ic.getContext('2d'); const g = x.createLinearGradient(0, 0, 0, 256); g.addColorStop(0, '#f4fafc'); g.addColorStop(0.5, '#cfe4ec'); g.addColorStop(1, '#9fc3d2'); x.fillStyle = g; x.fillRect(0, 0, 128, 256);
        for(let k = 0; k < 70; k++){ const X = rnd()*128; x.strokeStyle = rnd() < 0.5 ? `rgba(90,140,165,${R(0.15, 0.4)})` : `rgba(255,255,255,${R(0.3, 0.7)})`; x.lineWidth = R(1, 5); x.beginPath(); x.moveTo(X, R(0, 60)); x.lineTo(X + R(-4, 4), 256); x.stroke(); }
 }
      const itx = new THREE.CanvasTexture(ic); itx.colorSpace = THREE.SRGBColorSpace; itx.wrapS = THREE.RepeatWrapping;
      const ice = new THREE.MeshStandardMaterial({ map: itx, roughness: 0.4, color: 0xb8d2dc }), dirty = mat(0x9aa4a6, { roughness: 0.7 });
      const Lw = S.len || 70, H = S.h || 18;
      for(let k = 0; k < 9; k++){ const x = -Lw/2 + (k + 0.5)*Lw/9, h = H*R(0.7, 1.05), g = new THREE.BoxGeometry(Lw/9 + 1, h, 10, 10, 8, 1), P = g.attributes.position;
        for(let j = 0; j < P.count; j++){ const px = P.getX(j), py = P.getY(j), pz = P.getZ(j); if(pz > 0) P.setZ(j, pz + 0.7*Math.sin(px*1.6 + k*2) + 0.35*Math.sin(py*0.9 + px)); if(py > 0) P.setY(j, py + 0.6*Math.sin(px*0.8 + k)); }
        g.computeVertexNormals(); const zz = R(-4, 4); if(!F.ok(x, zz, 5)) continue; add(G, g, ice, x, F.gy(x, zz) + h/2 - 2, zz, null, R(-0.15, 0.15)); add(G, new THREE.BoxGeometry(Lw/9 + 1.2, 1.2, 10.4), dirty, x, F.gy(x, 0) - 1.2, R(-1, 1)); }
      clear(G, (x, z) => Math.abs(x) < Lw/2 + 4 && Math.abs(z) < 9); return F.w(0, 0); },
    chapel(W, S){ const F = frame(W.i + (S.at || 0), S.D || 30, S.side); const G = F.G, PR = S.r || 14; const L = lakeLevel(F, PR, 0, 4);
      if(F.ok(0, 4, PR)) water(G, PR, 0, 4, L, 0x1f4a5a, { roughness: 0.05 }); shore(F, PR, 0, 4, L, 0x6d6660, 22);
      const C = new THREE.Group(), cz = -PR + 2.5, cy = F.gy(-6, cz); C.position.set(-6, cy, cz); C.rotation.y = 0.3; G.add(C); const white = mat(0xf1eee6, { roughness: 0.8 }), roof = mat(0x4a4c52, { roughness: 0.6 });
      add(C, new THREE.BoxGeometry(4.2, 6, 7), white, 0, 2.2, 0);
      const rg = new THREE.BoxGeometry(5, 0.22, 4.2); add(C, rg, roof, 0, 5.9, 1.55).rotation.x = 0.72; add(C, rg, roof, 0, 5.9, -1.55).rotation.x = -0.72;
      add(C, new THREE.BoxGeometry(1.6, 3, 1.6), white, 0, 6.6, 3); add(C, new THREE.ConeGeometry(1.25, 2.2, 4), roof, 0, 9.2, 3, null, Math.PI/4);
      add(C, new THREE.BoxGeometry(1.2, 2, 0.1), mat(0x5a3a26), 0, 0.9, 3.53);
      clear(G, (x, z) => Math.hypot(x, z - 4) < PR + 2 || Math.hypot(x + 6, z - cz) < 6); return F.w(0, 0); },
    lake(W, S){ const PR = S.r || 12; let best = null;
      for(const at of [-30, -15, 0, 15, 30]) for(const D of [18, 26, 36]) for(const sd of [1, -1]){ const i = W.i + at; if(i < 2 || i > trail.length - 3) continue; const p = trail[i], a = trail[i - 2], b = trail[i + 2]; let tx = b.x - a.x, tz = b.z - a.z; const l = Math.hypot(tx, tz) || 1; tx /= l; tz /= l;
        const x = p.x - tz*sd*D, z = p.z + tx*sd*D; if(!free(x, z, PR)) continue; let lo = 1e9, hi = -1e9; for(let k = 0; k < 12; k++){ const an = k/12*6.283, h = heightAt(x + Math.cos(an)*PR, z + Math.sin(an)*PR); lo = Math.min(lo, h); hi = Math.max(hi, h); }
        const sc = hi - lo + (heightAt(x, z) > p.h + 2 ? 30 : 0); if(!best || sc < best.sc) best = { sc, at, D, sd }; }
      const F = frame(W.i + (best ? best.at : 0), best ? best.D : 22, best ? best.sd : S.side); const G = F.G; const L = lakeLevel(F, PR, 0, 0);
      water(G, PR, 0, 0, L, 0x1d3c48, { roughness: 0.03, metalness: 0.35, opacity: 0.96 }); shore(F, PR, 0, 0, L, 0x77716a, 30);
      clear(G, (x, z) => Math.hypot(x, z) < PR + 2); return F.w(0, 0); },
    stairs(W, S){ const i0 = W.i + (S.from ?? -30), i1 = Math.min(trail.length - 3, W.i + (S.to ?? 10)), G = new THREE.Group(); scene.add(G); const m = rockM(0xcfc8ba), sg = new THREE.BoxGeometry(2.3, 0.45, 0.9);
      for(let i = Math.max(2, i0); i <= i1; i++){ const p = trail[i], a = trail[i - 1], b = trail[i + 1]; const o = add(G, sg, m, p.x, heightAt(p.x, p.z) - 0.12, p.z); o.rotation.y = Math.atan2(b.x - a.x, b.z - a.z); o.scale.x = R(0.9, 1.15); }
      for(let i = Math.max(2, i0); i <= i1; i += 3) for(const s of [-1, 1]){ const p = trail[i], a = trail[i - 1], b = trail[i + 1]; let tx = b.x - a.x, tz = b.z - a.z; const l = Math.hypot(tx, tz) || 1; tx /= l; tz /= l; const d = R(1.9, 3.2), x = p.x - tz*s*d, z = p.z + tx*s*d;
        add(G, rockGeo[(rnd()*4)|0], m, x, heightAt(x, z) + 0.1, z, [R(0.7, 1.4), R(0.5, 1.1), R(0.7, 1.3)], rnd()*6); }
      return { x: trail[W.i].x, z: trail[W.i].z }; },
    pine(W, S){ const F = frame(W.i + (S.at || 0), S.D || 7, S.side); const G = F.G, bark = mat(0x4e3b2e, { roughness: 0.95 }), leaf = mat(0x2a4a2c, { roughness: 0.95 });
      add(G, rockGeo[0], rockM(0xcfc9bd), 0, F.gy(0, 0) + 0.6, 0, [3.4, 2.2, 3]); add(G, rockGeo[2], rockM(0xcfc9bd), 2.4, F.gy(2.4, 1.2) + 0.4, 1.2, [2, 1.4, 1.8]);
      const y0 = F.gy(0, 0) + 2.2, tr = [new V3(0, y0 - 0.5, 0), new V3(0.2, y0 + 1.8, 0.3), new V3(-0.3, y0 + 3.6, 0.1), new V3(0.1, y0 + 5.2, -0.2)];
      G.add(new THREE.Mesh(tube(tr, 0.3, 0.12, 16), bark)).castShadow = true;
      // 손님을 맞듯 길 쪽으로 길게 뻗은 가지 (머리 위 3.8m 이상)
      const arm = [new V3(0, y0 + 2.6, 0), new V3(-0.4, y0 + 2.9, -2.2), new V3(-0.3, y0 + 3.0, -4.4), new V3(0.2, y0 + 3.3, -6.2)]; G.add(new THREE.Mesh(tube(arm, 0.22, 0.07, 14), bark)).castShadow = true;
      const pads = [[0.1, 5.5, -0.2, 2.2], [-0.6, 4.4, 0.8, 1.6], [0.7, 4.8, -0.6, 1.5], [-0.3, 3.4, -2.5, 1.5], [-0.2, 3.5, -4.5, 1.6], [0.2, 3.7, -6.3, 1.4], [0.8, 3.3, 1.2, 1.2]];
      const lg = new THREE.IcosahedronGeometry(1, 2), leaf2 = mat(0x203d24, { roughness: 0.95 });
      for(const [x, y, z, r] of pads) for(let q = 0; q < 9; q++){ const a = R(0, 6.28), d = R(0, r*0.8); add(G, lg, q % 2 ? leaf : leaf2, x + Math.cos(a)*d, y0 + y - 2.2 + R(0, 0.25), z + Math.sin(a)*d, [R(0.4, 0.6)*r, R(0.14, 0.22)*r + 0.12, R(0.4, 0.6)*r]); }
      clear(G, (x, z) => Math.hypot(x, z) < 4.5); return F.w(0, 0); },
    crater(W, S){ // 화구호: 정상 둘레에서 가장 낮은 곳을 찾아 물을 채워요 (백록담)
      const p = trail[Math.min(trail.length - 1, W.i)]; let lo = null;
      for(let r = 20; r <= (S.R || 420); r += 15) for(let a = 0; a < 6.283; a += 0.1){ const x = p.x + Math.cos(a)*r, z = p.z + Math.sin(a)*r, h = heightAt(x, z); let rim = 1e9;
        for(let b = 0; b < 6.283; b += 0.5) rim = Math.min(rim, heightAt(x + Math.cos(b)*130, z + Math.sin(b)*130));
        const dep = rim - h; if(!lo || dep > lo.dep) lo = { x, z, h, dep }; }
      if(!lo || lo.dep < 6) return { x: p.x, z: p.z };
      // 바닥으로 내려가며 가장 낮은 곳
      for(let it = 0; it < 40; it++){ let bx = lo.x, bz = lo.z, bh = lo.h; for(let a = 0; a < 6.283; a += 0.5){ const x = lo.x + Math.cos(a)*6, z = lo.z + Math.sin(a)*6, h = heightAt(x, z); if(h < bh){ bx = x; bz = z; bh = h; } } if(bh >= lo.h) break; lo.x = bx; lo.z = bz; lo.h = bh; }
      // 가장 낮은 곳 둘레로 조금씩 넓히며 물 높이를 넘는 벽까지
      const lvl = lo.h + (S.fill || 5); let rad = 10; for(; rad < 140; rad += 4){ let wet = 0; for(let a = 0; a < 6.283; a += 0.3) if(heightAt(lo.x + Math.cos(a)*rad, lo.z + Math.sin(a)*rad) < lvl) wet++; if(wet < 13) break; }
      const G = new THREE.Group(); G.position.set(lo.x, 0, lo.z); scene.add(G);
      const w = new THREE.Mesh(new THREE.CircleGeometry(rad + 6, 64), new THREE.MeshStandardMaterial({ color: 0x2b5a5c, roughness: 0.06, metalness: 0.2, transparent: true, opacity: 0.92 })); w.rotation.x = -Math.PI/2; w.position.y = lvl; G.add(w);
      window.__crater = { x: lo.x, z: lo.z, h: lo.h, dep: lo.dep, lvl, rad, sx: p.x, sz: p.z, sh: p.h };
      return { x: lo.x, z: lo.z }; },
    village(W, S){ // 산비탈 마을: 하얀 돌집 + 파랑·초록·빨강 지붕 (남체 바자르)
      const p = trail[Math.min(trail.length - 1, W.i)], G = new THREE.Group(); scene.add(G); const wall = mat(0xece7dc), stone = mat(0x8a8178, { map: TEX.granite }), roofs = [0x2f63a8, 0x3a8a4f, 0xa8382c, 0x5d6066].map(c => mat(c, { roughness: 0.55, metalness: 0.25 })), win = mat(0x3b2a20);
      let made = 0; for(let t = 0; t < 400 && made < (S.n || 34); t++){ const a = R(0, 6.283), r = R(18, S.R || 110), x = p.x + Math.cos(a)*r, z = p.z + Math.sin(a)*r; if(!free(x, z, 5)) continue;
        const w = R(5, 8), d = R(4, 6), h = R(3.2, 5.5), y0 = Math.min(heightAt(x - w/2, z), heightAt(x + w/2, z), heightAt(x, z - d/2), heightAt(x, z + d/2)), y1 = Math.max(heightAt(x - w/2, z), heightAt(x + w/2, z), heightAt(x, z - d/2), heightAt(x, z + d/2));
        if(y1 - y0 > 5) continue; made++; const H = new THREE.Group(); H.position.set(x, y0, z); H.rotation.y = Math.atan2(p.x - x, p.z - z) + R(-0.3, 0.3); G.add(H);
        add(H, new THREE.BoxGeometry(w, y1 - y0 + 0.6, d), stone, 0, (y1 - y0)/2 - 0.3, 0); const base = y1 - y0 + 0.3;
        add(H, new THREE.BoxGeometry(w, h, d), wall, 0, base + h/2, 0); const rm = roofs[(rnd()*4)|0];
        const rg = new THREE.BoxGeometry(w + 0.6, 0.16, d*0.62); add(H, rg, rm, 0, base + h + 0.55, d*0.25).rotation.x = 0.38; add(H, rg, rm, 0, base + h + 0.55, -d*0.25).rotation.x = -0.38;
        for(const sx of [-w/3, 0, w/3]) add(H, new THREE.BoxGeometry(0.7, 0.8, 0.05), win, sx, base + h*0.6, d/2 + 0.03); }
      return { x: p.x, z: p.z }; },
    boulders(W, S){ const i0 = W.i + (S.from ?? -70), i1 = Math.min(trail.length - 2, W.i + (S.to ?? 0)), G = new THREE.Group(); scene.add(G); const c = S.color ? parseInt(S.color.slice(1), 16) : 0xbdb6ab;
      for(let t = 0; t < (S.n || 70); t++){ const i = Math.max(2, Math.floor(R(i0, i1))), p = trail[i], a = trail[i - 1], b = trail[Math.min(trail.length - 1, i + 1)]; let tx = b.x - a.x, tz = b.z - a.z; const l = Math.hypot(tx, tz) || 1; tx /= l; tz /= l;
        const s = rnd() < 0.5 ? -1 : 1, w = R(1, 3.4), d = R(1.6, 9) + w, x = p.x - tz*s*d, z = p.z + tx*s*d; if(!free(x, z, w)) continue; add(G, rockGeo[(rnd()*4)|0], rockM(c), x, heightAt(x, z) + w*0.25, z, [w, w*R(0.6, 0.9), w*R(0.7, 1.1)], rnd()*6); }
      return { x: trail[W.i].x, z: trail[W.i].z }; },
  };
  window.__spots = [];
  for(const [wi, S] of SPOTS){ const W = WPS[wi]; if(!W || !B[S.type]) continue; try{ const at = B[S.type]({ i: W.i }, S); window.__spots.push({ wi, type: S.type, x: at.x, z: at.z }); }catch(e){ console.warn('spot', S.type, e); } }
}
"""


def patch_spots(P, m):
    spots = [[k, w['spot']] for k, w in enumerate(m.get('waypoints', [])) if isinstance(w.get('spot'), dict)]
    if not spots: return
    P.rep("window.__game = {", SPOT_JS.replace('__SPOTS__', json.dumps(spots, ensure_ascii=False)) + "window.__game = {", 1)
