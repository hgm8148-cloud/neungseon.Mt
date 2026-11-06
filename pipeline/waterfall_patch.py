"""경유지 폭포 (2026-11-05 승연: 설악산 '설악폭포'에 도착했는데 폭포가 안 보여요)

mountains/<id>.json 경유지에 "feature": "waterfall" 을 달면 그 경유지 옆에 폭포를 세워요.
- 탐방로에서 오르막 쪽으로 비켜난 화강암 벼랑 + 위에서 쏟아지는 물줄기(흐르는 물결) + 아래 소(물웅덩이)·물보라·물안개
- 계곡 물소리 계산(STREAM)에 넣어서 가까이 가면 물소리가 커져요
- 탐방로·숨은 길은 막지 않아요 (벼랑은 길에서 11m, 소는 길에서 5m 넘게)
"""
import json

WF_JS = r"""
// ---------- 경유지 폭포 (pipeline/waterfall_patch.py) ----------
// 2026-11-06 승연 '너무 조악하고 깨져 보여, 더 크고 웅장하게': 높이 약 2배, 매끈한 바위 벼랑(틈 없음), 휘어 떨어지는 물줄기, 2단 낙차, 소·물보라·물안개
for(const wi0 of __WFS__){ const [wi, WO] = Array.isArray(wi0) ? wi0 : [wi0, {}], SC = WO.scale || 1; const W = WPS[wi]; if(!W) continue; try{
  const i = Math.max(1, Math.min(trail.length - 2, W.i + (WO.at || 0))), p = trail[i], a0 = trail[Math.max(0, i-6)], a1 = trail[Math.min(trail.length-1, i+6)];
  let tx = a1.x - a0.x, tz = a1.z - a0.z; const tl = Math.hypot(tx, tz) || 1; tx /= tl; tz /= tl; const nx = -tz, nz = tx;
  const hp = heightAt(p.x, p.z), dif = s => { let m = 0; for(const d of [5, 9, 13, 17]) m = Math.max(m, heightAt(p.x + nx*d*s, p.z + nz*d*s) - hp); return m; };
  const sd = WO.side || (dif(1) <= dif(-1) ? 1 : -1), D = (WO.D || 19*Math.max(0.55, SC));
  const cx = p.x + nx*sd*D, cz = p.z + nz*sd*D, face = Math.atan2(-nx*sd, -nz*sd);   // 벼랑이 탐방로를 바라봐요
  const G = new THREE.Group(); G.rotation.y = face; G.position.set(cx, 0, cz); G.scale.setScalar(SC); G.updateMatrixWorld(true);
  const wpt = (lx, lz) => { const v = new THREE.Vector3(lx, 0, lz); G.localToWorld(v); return v; };
  // 소 높이: 소 둘레 땅 높이의 가운데값 (비탈에서 너무 뜨거나 묻히지 않게)
  const PZ = 4.2, PR = 5.2; const rim = []; for(let k = 0; k < 16; k++){ const an = k/16*6.283, v = wpt(Math.cos(an)*PR, PZ + Math.sin(an)*PR); rim.push(heightAt(v.x, v.z)); }
  rim.sort((u, v) => u - v); const L = Math.max(rim[8], hp - 1.5) + 0.25*SC, H = 24, H1 = 15;   // H1: 위 폭포가 떨어지는 턱
  G.position.y = L; G.updateMatrixWorld(true); scene.add(G);
  let rs = 4127; const rnd = () => (rs = (rs * 16807) % 2147483647) / 2147483647;
  const tones = (WO.tones || [0xb7b0a4, 0xa9a397, 0xc2bbae, 0x9c978d]).map(c => new THREE.MeshStandardMaterial({ map: TEX.granite, color: c, roughness: 0.9 }));
  // 매끈한 바위: 꼭짓점을 위치로 정한 물결로만 밀어서 면 사이 틈이 생기지 않아요
  const rockGeo = []; for(let k = 0; k < 4; k++){ const g = new THREE.SphereGeometry(1, 22, 14), P = g.attributes.position, a = 1.3 + k*0.4, s1 = k*1.7, s2 = k*2.3 + 1;
    for(let j = 0; j < P.count; j++){ const x = P.getX(j), y = P.getY(j), z = P.getZ(j);
      let n = 1 + 0.13*Math.sin(x*a*2.1 + s1)*Math.cos(z*a*1.7 + s2) + 0.08*Math.sin(y*a*3.3 + z*2.2 + s1) + 0.05*Math.sin((x + y)*6.1 + s2);
      const fl = y > 0.55 ? 0.55 + (y - 0.55)*0.35 : y;   // 윗면은 판판하게 (층진 화강암)
      P.setXYZ(j, x*n, fl*n, z*n); }
    g.computeVertexNormals(); rockGeo.push(g); }
  const near = (lx, lz, r) => { const v = wpt(lx, lz); return nearTrail(v.x, v.z, 30).d < r*SC + 2.5; };
  const boulder = (w, h, d, x, y, z, ry) => { if(near(x, z, Math.max(w, d))) return null; const m = new THREE.Mesh(rockGeo[(rnd()*4)|0], tones[(rnd()*4)|0]); m.scale.set(w, h, d); m.position.set(x, y, z); m.rotation.y = ry ?? rnd()*6.28; m.castShadow = m.receiveShadow = true; G.add(m); return m; };
  // 벼랑: 가운데 홈(물길) 양옆으로 층층이 쌓인 큰 바위, 아래는 땅속까지 묻어요
  for(const s of [-1, 1]){
    for(let lv = 0; lv < 6; lv++){ const y = -3 + lv*4.6, k = 1 - lv*0.06;
      boulder(4.2*k, 3.4, 3.4, s*(4.2 + rnd()*0.8), y, -2.6 + rnd()*0.6);
      boulder(4.6*k, 3.8, 3.8, s*(9.2 + rnd()*1.2), y - 1.5 - lv*0.3, -3.6 + rnd()*0.8);
      if(lv < 4) boulder(3.6, 3.2, 3.4, s*(13.5 + rnd()), y - 3 - lv*0.6, -4.6); } }
  for(let lv = 0; lv < 6; lv++) boulder(3.2, 3.0, 2.2, (rnd() - 0.5)*0.8, -2 + lv*4.4, -5.0);   // 물이 미끄러지는 뒷벽
  boulder(4.0, 1.4, 2.6, 0, H1 - 0.9, -1.6, 0);          // 위 폭포가 부딪는 중간 턱
  boulder(6.5, 1.8, 3.6, 0, H + 0.2, -4.6, 0);           // 꼭대기 턱
  boulder(5.5, 2.4, 3.8, -6, H + 0.6, -6.5); boulder(5.5, 2.4, 3.8, 6, H + 0.4, -6.8);
  // 소 둘레 돌 (아래쪽 비탈에서 소가 떠 보이지 않게 둑처럼)
  for(let k = 0; k < 18; k++){ const an = k/18*6.283 + rnd()*0.15; if(Math.sin(an) < -0.55) continue; const r = PR + 0.6 + rnd()*0.8, v = wpt(Math.cos(an)*r, PZ + Math.sin(an)*r), gy = heightAt(v.x, v.z) - L;
    const sz = 0.9 + rnd()*1.1, top = Math.max(0.5, -gy + 0.6); boulder(sz*1.3, Math.max(sz, top), sz, Math.cos(an)*r, Math.min(gy, 0) + top*0.35, PZ + Math.sin(an)*r); }
  // 물줄기 무늬: 가장자리는 부드럽게 사라져요
  const wtex = (w, h, n, base) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d');
    x.fillStyle = base; x.fillRect(0, 0, w, h);
    for(let k = 0; k < n; k++){ const X = rnd()*w, Y = rnd()*h, Lh = 30 + rnd()*140; const dark = rnd() < 0.25;
      x.strokeStyle = dark ? `rgba(120,150,165,${0.15 + rnd()*0.25})` : `rgba(255,255,255,${0.3 + rnd()*0.6})`; x.lineWidth = 0.6 + rnd()*2.6; x.beginPath(); x.moveTo(X, Y); x.bezierCurveTo(X + (rnd()-0.5)*3, Y + Lh*0.3, X + (rnd()-0.5)*3, Y + Lh*0.7, X + (rnd()-0.5)*2, Y + Lh); x.stroke();
      if(Y + Lh > h){ x.beginPath(); x.moveTo(X, Y - h); x.lineTo(X, Y + Lh - h); x.stroke(); } }
    x.globalCompositeOperation = 'destination-in'; const g = x.createLinearGradient(0, 0, w, 0); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.16, 'rgba(0,0,0,1)'); g.addColorStop(0.84, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)'); x.fillStyle = g; x.fillRect(0, 0, w, h);
    const t = new THREE.CanvasTexture(c); t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; return t; };
  const sheets = [];
  // 휘어 떨어지는 물줄기: 턱에서 앞으로 튀어나왔다가 아래로 (z = a·√낙차), 아래로 갈수록 넓어져요
  const fall = (top, bot, z0, w0, w1, out, sp, op, rep) => { const h = top - bot, g = new THREE.PlaneGeometry(1, 1, 6, 30), P = g.attributes.position;
    for(let j = 0; j < P.count; j++){ const u = P.getX(j), t = 0.5 - P.getY(j); const wv = w0 + (w1 - w0)*t;
      P.setXYZ(j, u*wv + Math.sin(t*9 + u*3)*0.12, top - t*h, z0 + out*Math.sqrt(t) + 0.15*Math.sin(u*5 + t*4)); }
    g.computeVertexNormals(); const tx2 = wtex(128, 512, 260, 'rgba(214,234,242,0.78)'); tx2.repeat.set(1, rep);
    const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ map: tx2, transparent: true, opacity: op, depthWrite: false, side: THREE.DoubleSide, fog: true }));
    G.add(m); sheets.push([tx2, sp, m.material]); return m; };
  fall(H + 0.9, H1 - 0.2, -2.6, 2.6, 3.4, 1.2, 1.25, 0.95, 1.6); fall(H + 0.9, H1 - 0.2, -2.4, 3.4, 4.4, 1.35, 0.9, 0.45, 1.2);
  fall(H1 + 0.1, 0.1, -1.1, 3.6, 5.0, 1.6, 1.35, 0.95, 1.4); fall(H1 + 0.1, 0.1, -0.9, 4.6, 6.0, 1.8, 0.95, 0.42, 1.1);
  fall(H*0.62, 0.1, -2.9, 0.7, 1.0, 0.5, 1.1, 0.6, 1.0).position.x = -2.3;   // 옆으로 흐르는 가는 물줄기
  // 꼭대기 물길 (뒤에서 흘러와 턱으로)
  { const t = wtex(64, 256, 80, 'rgba(160,200,212,0.85)'); t.repeat.set(1, 1); const m = new THREE.Mesh(new THREE.PlaneGeometry(3, 6), new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false, fog: true }));
    m.rotation.x = -Math.PI/2 + 0.12; m.position.set(0, H + 1.1, -5.2); G.add(m); sheets.push([t, 0.6, m.material]); }
  // 소(물웅덩이) + 퍼지는 물결
  const pool = new THREE.Mesh(new THREE.CircleGeometry(PR, 40), new THREE.MeshStandardMaterial({ color: 0x1f4d52, roughness: 0.22, metalness: 0.0, transparent: true, opacity: 0.9 }));
  pool.rotation.x = -Math.PI/2; pool.position.set(0, 0, PZ); pool.receiveShadow = true; G.add(pool);
  const rc = document.createElement('canvas'); rc.width = rc.height = 256; { const x = rc.getContext('2d'); x.translate(128, 128);
    for(let k = 0; k < 7; k++){ x.strokeStyle = `rgba(255,255,255,${0.5 - k*0.06})`; x.lineWidth = 3 - k*0.3; x.beginPath(); x.arc(0, 0, 14 + k*16 + rnd()*5, 0, 6.283); x.stroke(); } }
  const rt = new THREE.CanvasTexture(rc), rings = [];
  for(let k = 0; k < 3; k++){ const m = new THREE.Mesh(new THREE.CircleGeometry(1, 32), new THREE.MeshBasicMaterial({ map: rt, transparent: true, depthWrite: false, opacity: 0.4 })); m.rotation.x = -Math.PI/2; m.position.set(0, 0.03 + k*0.01, 0.9); G.add(m); rings.push(m); }
  const lit = [];   // 빛을 받지 않는 물·물보라는 밤엔 어둡게
  // 물보라·물안개
  const sc = document.createElement('canvas'); sc.width = sc.height = 64; const y = sc.getContext('2d'), gr = y.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,0.95)'); gr.addColorStop(0.5, 'rgba(255,255,255,0.4)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); y.fillStyle = gr; y.fillRect(0, 0, 64, 64);
  const st0 = new THREE.CanvasTexture(sc), puffs = [];
  const puff = (k, kind) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: st0, transparent: true, depthWrite: false, opacity: 0.5, fog: true })); s.userData = { ph: rnd(), k, kind, x: (rnd() - 0.5) }; G.add(s); puffs.push(s); };
  for(let k = 0; k < 16; k++) puff(k, 0); for(let k = 0; k < 8; k++) puff(k, 1); for(let k = 0; k < 6; k++) puff(k, 2);
  pool.onBeforeRender = () => { const t = performance.now()/1000;
    const lum = typeof SKY !== 'undefined' && SKY.night != null ? 0.2 + 0.8*(1 - SKY.night) : 1;
    for(const [tx2, sp, mt] of sheets){ tx2.offset.y = (t*sp) % 1; mt.color.setScalar(lum); }
    for(const m of rings) m.material.color.setScalar(lum); for(const s of puffs) s.material.color.setScalar(lum);
    rings.forEach((m, k) => { const f = (t*0.25 + k/3) % 1, r = 1.2 + f*4.2; m.scale.set(r, r, 1); m.material.opacity = 0.45*(1 - f); });
    for(const s of puffs){ const u = s.userData, f = (t*(u.kind === 2 ? 0.12 : 0.4) + u.ph) % 1; let sz;
      if(u.kind === 0){ s.position.set(u.x*5, 0.3 + f*2.2, 0.5 + f*1.6); sz = (1.4 + f*1.8); s.material.opacity = 0.6*(1 - f); }        // 떨어지는 곳 물보라
      else if(u.kind === 1){ s.position.set(u.x*3.6, H1 + 0.3 + f*1.4, -0.5 + f*0.8); sz = 1 + f*1.4; s.material.opacity = 0.45*(1 - f); }   // 중간 턱 물보라
      else { s.position.set(u.x*8, 1 + f*9, 1.5 + f*4); sz = 4 + f*6; s.material.opacity = 0.2*(1 - f)*Math.min(1, f*4); }               // 피어오르는 물안개
      s.scale.set(sz, sz*0.85, 1); } };
  G.updateMatrixWorld(true);
  // 물소리
  if(typeof STREAM !== 'undefined'){ const v = new THREE.Vector3(); for(const q of [[0, 0.3, PZ], [0, H1, -1], [0, H, -2.5], [0, 0.3, 0.5]]){ v.set(q[0], q[1], q[2]); G.localToWorld(v); STREAM.push({ x: v.x, z: v.z, h: v.y, foam: 1 }); } }
  // 벼랑·소 자리의 나무·풀은 치워요
  { const M = new THREE.Matrix4(), Z = new THREE.Matrix4().makeScale(0, 0, 0), v = new THREE.Vector3(), inv = new THREE.Matrix4().copy(G.matrixWorld).invert();
    scene.traverse(o => { if(!o.isInstancedMesh || o.parent === G) return; let ch = false; for(let k = 0; k < o.count; k++){ o.getMatrixAt(k, M); v.setFromMatrixPosition(M); v.applyMatrix4(inv);
      if((Math.abs(v.x) < 17 && v.z > -10 && v.z < 1.5) || Math.hypot(v.x, v.z - PZ) < PR + 2.5){ o.setMatrixAt(k, Z); ch = true; } } if(ch) o.instanceMatrix.needsUpdate = true; }); }
  window.__falls = (window.__falls || []).concat([{ wi, x: cx, z: cz, side: sd, L, H }]);
}catch(e){ console.warn('waterfall', e); } }
"""


def patch_waterfall(P, m):
    wfs = []
    for k, w in enumerate(m.get('waypoints', [])):
        f = w.get('feature')
        if f == 'waterfall': wfs.append(k)
        elif isinstance(f, dict) and f.get('type') == 'waterfall': wfs.append([k, {a: b for a, b in f.items() if a != 'type'}])
    if not wfs: return
    P.rep("window.__game = {", WF_JS.replace('__WFS__', json.dumps(wfs)) + "window.__game = {", 1)
