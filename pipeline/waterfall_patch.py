"""경유지 폭포 (2026-11-05 승연: 설악산 '설악폭포'에 도착했는데 폭포가 안 보여요)

mountains/<id>.json 경유지에 "feature": "waterfall" 을 달면 그 경유지 옆에 폭포를 세워요.
- 탐방로에서 오르막 쪽으로 비켜난 화강암 벼랑 + 위에서 쏟아지는 물줄기(흐르는 물결) + 아래 소(물웅덩이)·물보라·물안개
- 계곡 물소리 계산(STREAM)에 넣어서 가까이 가면 물소리가 커져요
- 탐방로·숨은 길은 막지 않아요 (벼랑은 길에서 11m, 소는 길에서 5m 넘게)
"""
import json

WF_JS = r'''
// ---------- 경유지 폭포 (pipeline/waterfall_patch.py) ----------
for(const wi of __WFS__){ const W = WPS[wi]; if(!W) continue; try{
  const i = W.i, p = trail[i], a0 = trail[Math.max(0, i-5)], a1 = trail[Math.min(trail.length-1, i+5)];
  let tx = a1.x - a0.x, tz = a1.z - a0.z; const tl = Math.hypot(tx, tz) || 1; tx /= tl; tz /= tl; const nx = -tz, nz = tx;
  // 길 옆 두 쪽 가운데 길 높이와 비슷한 쪽(앞이 언덕에 가리지 않는 쪽)에 세워요
  const hp = heightAt(p.x, p.z), dif = s => { let m = 0; for(const d of [4, 7, 10, 13]) m = Math.max(m, heightAt(p.x + nx*d*s, p.z + nz*d*s) - hp); return m; };
  const sd = dif(1) <= dif(-1) ? 1 : -1;
  const cx = p.x + nx*sd*12, cz = p.z + nz*sd*12, face = Math.atan2(-nx*sd, -nz*sd);   // 벼랑이 탐방로를 바라봐요
  const g0 = Math.max(heightAt(cx, cz), hp) - 0.4, H = 11;
  const G = new THREE.Group(); G.position.set(cx, g0, cz); G.rotation.y = face; scene.add(G);
  const rockM = new THREE.MeshStandardMaterial({ map: TEX.granite, color: 0xb9b2a6, roughness: 0.92 });
  let rs = 4127; const rnd = () => (rs = (rs * 16807) % 2147483647) / 2147483647;
  const boulder = (w, h, d, x, y, z) => { const g = new THREE.IcosahedronGeometry(1, 2), P = g.attributes.position;
    for(let k = 0; k < P.count; k++){ const vx = P.getX(k), vy = P.getY(k), vz = P.getZ(k), n = 1 + (rnd() - 0.5)*0.22; P.setXYZ(k, vx*n, vy*n, vz*n); }
    g.computeVertexNormals(); const m = new THREE.Mesh(g, rockM); m.scale.set(w, h, d); m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; G.add(m); return m; };
  // 벼랑: 가운데가 살짝 파인 두 덩이 + 위 턱 + 아래 받침 (물줄기가 가운데 홈으로 떨어져요)
  boulder(2.8, H*0.6, 2.2, -3.7, H*0.5, -2.0); boulder(2.9, H*0.56, 2.3, 3.8, H*0.46, -1.9);
  boulder(4.8, 1.6, 1.8, 0, H + 0.5, -2.4); boulder(2.4, H*0.55, 1.2, 0, H*0.5, -3.0);
  boulder(1.6, 1.0, 1.4, -3.2, 0.4, 2.6); boulder(1.2, 0.8, 1.1, 3.0, 0.3, 2.9); boulder(0.9, 0.6, 0.9, -1.8, 0.2, 4.2);
  // 물줄기: 세로 물결 무늬가 아래로 흘러요 (두 겹, 속도 다르게)
  const wc = document.createElement('canvas'); wc.width = 64; wc.height = 256; const x = wc.getContext('2d');
  x.fillStyle = 'rgba(210,232,240,0.55)'; x.fillRect(0, 0, 64, 256);
  for(let k = 0; k < 90; k++){ const X = rnd()*64, Y = rnd()*256, L = 20 + rnd()*70; x.strokeStyle = `rgba(255,255,255,${0.35 + rnd()*0.5})`; x.lineWidth = 0.8 + rnd()*2.2; x.beginPath(); x.moveTo(X, Y); x.lineTo(X + (rnd()-0.5)*2, Y + L); x.stroke(); }
  const mk = (sp, w, z, op) => { const t = new THREE.CanvasTexture(wc); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1.5, 2.2); t.colorSpace = THREE.SRGBColorSpace;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, H + 0.6, 1, 1), new THREE.MeshBasicMaterial({ map: t, transparent: true, opacity: op, depthWrite: false, side: THREE.DoubleSide, fog: true }));
    m.position.set(0, H/2 + 0.1, z); G.add(m); m.onBeforeRender = () => { t.offset.y = (performance.now()/1000 * sp) % 1; }; return m; };
  mk(1.35, 2.1, -1.55, 0.95); mk(0.95, 2.7, -1.4, 0.5);
  // 소(물웅덩이)
  const pool = new THREE.Mesh(new THREE.CircleGeometry(3.4, 32), new THREE.MeshStandardMaterial({ color: 0x3f6f78, roughness: 0.12, metalness: 0.1, transparent: true, opacity: 0.88 }));
  pool.rotation.x = -Math.PI/2; pool.position.set(0, 0.18, 1.2); pool.receiveShadow = true; G.add(pool);
  // 물보라·물안개
  const sc = document.createElement('canvas'); sc.width = sc.height = 64; const y = sc.getContext('2d'), gr = y.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,0.9)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); y.fillStyle = gr; y.fillRect(0, 0, 64, 64);
  const st0 = new THREE.CanvasTexture(sc), puffs = [];
  for(let k = 0; k < 9; k++){ const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: st0, transparent: true, depthWrite: false, opacity: 0.5 })); s.userData.ph = rnd()*6.28; s.userData.k = k; G.add(s); puffs.push(s); }
  pool.onBeforeRender = () => { const t = performance.now()/1000; for(const s of puffs){ const k = s.userData.k, f = (t*0.35 + s.userData.ph) % 1; const big = k > 5;
      s.position.set(Math.sin(s.userData.ph*3)*1.2, 0.4 + f*(big ? 3.5 : 1.4), -0.4 + f*(big ? 1.8 : 0.8)); const sz = (big ? 2.4 : 1.3) * (0.6 + f); s.scale.set(sz, sz*0.8, 1); s.material.opacity = (big ? 0.22 : 0.55) * (1 - f); } };
  G.updateMatrixWorld(true);
  // 물소리: 계곡 물줄기 점으로 넣어요
  if(typeof STREAM !== 'undefined'){ const v = new THREE.Vector3(); for(const q of [[0, 0.2, 1.6], [0, H*0.5, -1], [0, H, -1.2]]){ v.set(q[0], q[1], q[2]); G.localToWorld(v); STREAM.push({ x: v.x, z: v.z, h: v.y, foam: 1 }); } }
  // 벼랑·소 자리의 나무·풀은 치워요
  { const M = new THREE.Matrix4(), Z = new THREE.Matrix4().makeScale(0, 0, 0), v = new THREE.Vector3(), pc = new THREE.Vector3(0, 0, 1.6); G.localToWorld(pc);
    scene.traverse(o => { if(!o.isInstancedMesh || o.parent === G) return; let ch = false; for(let k = 0; k < o.count; k++){ o.getMatrixAt(k, M); v.setFromMatrixPosition(M);
      if(Math.hypot(v.x - cx, v.z - cz) < 7.5 || Math.hypot(v.x - pc.x, v.z - pc.z) < 4.5){ o.setMatrixAt(k, Z); ch = true; } } if(ch) o.instanceMatrix.needsUpdate = true; }); }
  window.__falls = (window.__falls || []).concat([{ wi, x: cx, z: cz, side: sd }]);
}catch(e){ console.warn('waterfall', e); } }
'''


def patch_waterfall(P, m):
    wfs = [k for k, w in enumerate(m.get('waypoints', [])) if w.get('feature') == 'waterfall']
    if not wfs: return
    P.rep("window.__game = {", WF_JS.replace('__WFS__', json.dumps(wfs)) + "window.__game = {", 1)
