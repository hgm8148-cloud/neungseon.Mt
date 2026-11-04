"""3D 정상과 역동적인 산길 (mountains/<id>.json 의 "relief").

  "relief": {
    "xex": 1.3,                       # 산세 강조 (build_site 에서 VEX 에 곱해요)
    "crags": {"zone": 700, "n": 240, "h": [8, 26], "w": [3, 7], "color": "#cfc8bc", "ridge": 1.2},
    "bridge": {"wp": 1, "len": 52, "depth": 26, "color": "#b4332a"}
  }

- crags: 정상 둘레 능선(주변보다 볼록한 곳)에 화강암 기암 봉우리를 무리 지어 세워요.
  탐방로에서 9m 안, 정상 야영장 안에는 세우지 않아요(길을 막지 않게).
- bridge: 지정한 지점 가까이에서 양 끝 높이가 비슷한 구간을 골라 협곡을 파고, 붉은 철 구름다리를 놓아요.
  다리 위에서는 발 높이를 다리 바닥에 맞춰요.
"""
import json

PRE_JS = r"""
// ---------- 구름다리 구간: 다리 위는 평평하게 (pipeline/relief_patch.py) ----------
const RELIEF = __CFG__;
const BRIDGE = (() => { const B = RELIEF.bridge; if(!B || !WPS[B.wp]) return null;
  const L = B.len|0, c0 = WPS[B.wp].i; let best = null;
  for(let c = Math.max(L, c0 - 70); c <= Math.min(trail.length - 1 - L, c0 + 70); c++){
    const a = trail[c - (L>>1)], b = trail[c + (L>>1)]; if(!a || !b) continue;
    const sc = Math.abs(a.h - b.h) + Math.abs(c - c0)*0.02; if(!best || sc < best.sc) best = {sc, i0:c - (L>>1), i1:c + (L>>1)}; }
  if(!best) return null; const ha = trail[best.i0].h, hb = trail[best.i1].h;
  for(let i = best.i0; i <= best.i1; i++){ const f = (i - best.i0)/(best.i1 - best.i0); trail[i].h = ha + (hb - ha)*f; }
  return { i0:best.i0, i1:best.i1, depth:B.depth || 24, color:B.color || '#b4332a' }; })();
"""

CARVE_JS = r"""
// ---------- 구름다리 아래 협곡 파기 (pipeline/relief_patch.py) ----------
if(BRIDGE){ const {i0, i1, depth} = BRIDGE, n = i1 - i0; let x0 = 1e9, x1 = -1e9, z0 = 1e9, z1 = -1e9;
  for(let i = i0; i <= i1; i++){ const p = trail[i]; x0 = Math.min(x0, p.x); x1 = Math.max(x1, p.x); z0 = Math.min(z0, p.z); z1 = Math.max(z1, p.z); }
  const pad = 90, sst = (a, b, v) => { const t = Math.min(1, Math.max(0, (v - a)/(b - a))); return t*t*(3 - 2*t); };
  const ta = trail[i0], tb = trail[i1], ux = (tb.x - ta.x)/Math.hypot(tb.x - ta.x, tb.z - ta.z), uz = (tb.z - ta.z)/Math.hypot(tb.x - ta.x, tb.z - ta.z), Lb = Math.hypot(tb.x - ta.x, tb.z - ta.z);
  for(let j = 0; j < M; j++){ const z = -HALF + j*FC; if(z < z0 - pad || z > z1 + pad) continue;
    for(let i = 0; i < M; i++){ const x = -HALF + i*FC; if(x < x0 - pad || x > x1 + pad) continue;
      const al = ((x - ta.x)*ux + (z - ta.z)*uz)/Lb, lat = Math.abs(-(x - ta.x)*uz + (z - ta.z)*ux);
      if(al < -0.1 || al > 1.1) continue;
      const along = sst(0.02, 0.2, al) * (1 - sst(0.8, 0.98, al)), side = 1 - sst(35, 85, lat);
      const k = along*side; if(k <= 0) continue;
      const deck = ta.h + (tb.h - ta.h)*Math.min(1, Math.max(0, al)), jag = (vnoise(x/9, z/9) - 0.5)*5;
      const floor = deck - depth*(0.75 + 0.25*side) + jag;
      fineH[j*M + i] = Math.min(fineH[j*M + i], fineH[j*M + i]*(1 - k) + floor*k); } } }
"""

SCENE_JS = r"""
// ---------- 기암 봉우리 + 구름다리 (pipeline/relief_patch.py) ----------
{ const RC = RELIEF, rnd = (() => { let s = 7331; return () => (s = (s*16807) % 2147483647)/2147483647; })();
  const SUM = trail[trail.length - 1];
  // 기암 봉우리: 둥근 머리 + 세로 절리 + 가로 마디를 가진 화강암 기둥 원형 6개를 돌려 써요
  if(RC.crags){ const C = RC.crags, protos = [];
    for(let k = 0; k < 6; k++){ const g = new THREE.CylinderGeometry(1, 1, 1, 14, 14, false); g.translate(0, 0.5, 0);
      const P = g.attributes.position, col = [], sd = k*17.3 + 3, lean = (rnd() - 0.5)*0.25, ribs = 5 + (k % 3)*2, tip = 0.62 + rnd()*0.2;
      for(let v = 0; v < P.count; v++){ let x = P.getX(v), y = P.getY(v), z = P.getZ(v); const a = Math.atan2(z, x), r0 = Math.hypot(x, z);
        let r = 1 + 0.16*Math.sin(a*2 + sd) + 0.1*Math.sin(a*3.3 + sd*1.7 + y*3) + 0.07*Math.sin(y*9 + a*2 + sd);
        const groove = Math.pow(Math.abs(Math.sin(a*ribs*0.5 + sd + y*0.6)), 10); r *= 1 - 0.13*groove;
        const joint = Math.pow(Math.abs(Math.sin(y*Math.PI*3.2 + sd)), 18); r *= 1 - 0.035*joint;
        if(y > tip){ const f = (y - tip)/(1 - tip); r *= Math.sqrt(Math.max(0, 1 - f*f*0.96)); }
        r *= 1 - 0.18*y;
        x = (r0 > 1e-4 ? x/r0 : 0)*r*r0; z = (r0 > 1e-4 ? z/r0 : 0)*r*r0; x += lean*y*y;
        P.setXYZ(v, x, y, z);
        const sh = (0.74 + 0.26*Math.min(1, y*1.6)) * (1 - 0.35*groove) * (1 - 0.08*joint); col.push(sh, sh, sh); }
      g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.computeVertexNormals(); protos.push(g); }
    const tex = TEX.granite.clone(); tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.repeat.set(2, 3); tex.needsUpdate = true;
    const mat = new THREE.MeshStandardMaterial({ color:new THREE.Color(C.color || '#cfc8bc'), map:tex, vertexColors:true, roughness:0.96, metalness:0 });
    if(SZ && SZ.snow){ mat.color.lerp(new THREE.Color(0xf2f4f7), 0.25); }
    const items = protos.map(() => []), R = C.zone || 700, step = C.step || 15, hr = C.h || [8, 24], wr = C.w || [3, 7];
    const ring = (x, z, d) => (heightAt(x + d, z) + heightAt(x - d, z) + heightAt(x, z + d) + heightAt(x, z - d))/4;
    // 후보를 영역 전체에서 모아 점수 순으로 골라요 (정상 가까이·능선 위일수록 먼저)
    const cand = [];
    for(let gz = SUM.z - R; gz <= SUM.z + R; gz += step) for(let gx = SUM.x - R; gx <= SUM.x + R; gx += step){
      const x = gx + (rnd() - 0.5)*step, z = gz + (rnd() - 0.5)*step, ds = Math.hypot(x - SUM.x, z - SUM.z);
      if(ds > R || ds < SUMMIT_R + 12 || Math.abs(x) > HALF - 30 || Math.abs(z) > HALF - 30) continue;
      const h = heightAt(x, z), ridge = h - ring(x, z, 32), near = 1 - ds/R;
      const hf = (h - trail[0].h)/Math.max(1, SUM.h - trail[0].h);
      const sc = ridge/(C.ridge || 1.2)*0.5 + near*0.8 + hf*0.6 + rnd()*0.5;
      if(ridge < -1.5 || hf < (C.minH || 0.35)) continue;
      cand.push({x, z, sc, ridge, near}); }
    cand.sort((p, q) => q.sc - p.sc);
    let placed = 0;
    for(const cd of cand){ if(placed >= (C.n || 240)) break; const {x, z, ridge, near} = cd;
      if(nearTrail(x, z, 1).d < 10) continue;
      if(BRIDGE){ const nb = nearTrail(x, z, 1); if(nb.i >= BRIDGE.i0 - 10 && nb.i <= BRIDGE.i1 + 10 && nb.d < 40) continue; }
      const kk = 2 + (rnd()*4|0), big = Math.min(1.25, 0.65 + near*0.5 + Math.max(0, ridge)/14);
      for(let c = 0; c < kk; c++){ const ox = x + (rnd() - 0.5)*9, oz = z + (rnd() - 0.5)*9; if(nearTrail(ox, oz, 1).d < 9) continue;
        const ht = (hr[0] + (hr[1] - hr[0])*rnd()*rnd()) * big * (c === 0 ? 1 : 0.55 + rnd()*0.4), w = wr[0] + (wr[1] - wr[0])*rnd();
        const base = Math.min(heightAt(ox + w, oz), heightAt(ox - w, oz), heightAt(ox, oz + w), heightAt(ox, oz - w)) - 1.5;
        const m4 = new THREE.Matrix4().compose(new THREE.Vector3(ox, base, oz), new THREE.Quaternion().setFromEuler(new THREE.Euler((rnd() - 0.5)*0.12, rnd()*6.28, (rnd() - 0.5)*0.12)), new THREE.Vector3(w, ht + 1.5, w*(0.7 + rnd()*0.5)));
        items[(rnd()*protos.length)|0].push(m4); }
      placed++; }
    protos.forEach((g, k) => { if(!items[k].length) return; const im = new THREE.InstancedMesh(g, mat, items[k].length); items[k].forEach((m4, i) => im.setMatrixAt(i, m4));
      im.castShadow = true; im.receiveShadow = true; im.frustumCulled = false; scene.add(im); });
    window.__crags = placed; }
  // 구름다리: 붉은 철 트러스 + 철망 바닥 + 난간
  if(BRIDGE){ const {i0, i1} = BRIDGE, red = new THREE.MeshStandardMaterial({ color:new THREE.Color(BRIDGE.color), roughness:0.55, metalness:0.35 });
    const grate = new THREE.MeshStandardMaterial({ color:0x5d5a55, roughness:0.8, metalness:0.4 }), G = new THREE.Group();
    const a = trail[i0], b = trail[i1], len = Math.hypot(b.x - a.x, b.z - a.z), yaw = Math.atan2(b.x - a.x, b.z - a.z), slope = Math.atan2(b.h - a.h, len);
    const W = 1.7, mk = (geo, m, x, y, z) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = true; G.add(o); return o; };
    mk(new THREE.BoxGeometry(W, 0.12, len + 2), grate, 0, -0.06, 0);
    for(const s of [-1, 1]){ mk(new THREE.BoxGeometry(0.16, 0.5, len + 2), red, s*W/2, -0.3, 0);   // 옆 거더
      mk(new THREE.CylinderGeometry(0.045, 0.045, len + 2, 8).rotateX(Math.PI/2), red, s*W/2, 1.15, 0);   // 손잡이
      mk(new THREE.CylinderGeometry(0.03, 0.03, len + 2, 6).rotateX(Math.PI/2), red, s*W/2, 0.6, 0);
      for(let t = -len/2 - 1; t <= len/2 + 1.01; t += 2){ mk(new THREE.BoxGeometry(0.07, 1.2, 0.07), red, s*W/2, 0.55, t); } }
    // 아래 트러스: 아치형 하현재 + 사선 부재
    const arch = t => -0.6 - 2.4*(1 - Math.pow(2*t/len, 2));
    for(const s of [-1, 1]){ let prev = null; for(let k = 0; k <= 16; k++){ const t = -len/2 + len*k/16, y = arch(t), p = new THREE.Vector3(s*W/2, y, t);
        if(prev){ const d = p.clone().sub(prev), seg = mk(new THREE.CylinderGeometry(0.09, 0.09, d.length(), 6), red, (p.x + prev.x)/2, (p.y + prev.y)/2, (p.z + prev.z)/2); seg.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize());
          const q = new THREE.Vector3(s*W/2, -0.5, k % 2 ? prev.z : p.z), r2 = (k % 2 ? p : prev), d2 = r2.clone().sub(q), dg = mk(new THREE.CylinderGeometry(0.05, 0.05, d2.length(), 5), red, (q.x + r2.x)/2, (q.y + r2.y)/2, (q.z + r2.z)/2); dg.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d2.normalize()); }
        prev = p; } }
    G.rotation.order = 'YXZ'; G.rotation.y = yaw; G.rotation.x = -slope; G.position.set((a.x + b.x)/2, (a.h + b.h)/2 + 0.18, (a.z + b.z)/2); scene.add(G);
    window.__deckY = (x, z, ni) => { if(ni == null || ni < i0 - 1 || ni > i1 + 1) return null; const p = trail[Math.min(i1, Math.max(i0, ni))]; if(Math.hypot(x - p.x, z - p.z) > W/2 + 0.2) return null; return p.h + 0.18; };
    window.__bridge = BRIDGE; }
}
"""


def patch_relief(P, m):
    R = m.get('relief')
    if not R:
        return
    P.rep("// ---------- fine terrain ----------", PRE_JS.replace('__CFG__', json.dumps(R)) + "// ---------- fine terrain ----------", 1)
    P.rep("function heightAt(x,z){", CARVE_JS + "function heightAt(x,z){", 1)
    P.rep("// ---------- 바위·통나무·돌계단 충돌", SCENE_JS + "// ---------- 바위·통나무·돌계단 충돌", 1)
    # 다리 위에서는 발을 다리 바닥에
    P.rep("  if(ROCKC){ const ry = ROCKC.top(x, z, y); if(ry > y) y = ry - 0.01; }\n  return y;",
          "  if(ROCKC){ const ry = ROCKC.top(x, z, y); if(ry > y) y = ry - 0.01; }\n  if(window.__deckY){ const dy = window.__deckY(x, z, ni); if(dy != null) y = dy; }\n  return y;", 1)


# 오르막에서는 시선을 앞쪽 비탈·정상 쪽으로 들어 올려요 (카메라가 아바타 발밑만 내려다보지 않게)
UPLOOK_JS = (
    "    if(!st.view && !st.camp){ const fx = -Math.sin(st.yaw), fz = -Math.cos(st.yaw); let rise = 0;\n"
    "      for(const d of [12, 24, 40]) rise = Math.max(rise, (heightAt(fX + fx*d, fZ + fz*d) - yC) * (20/(d+8)));\n"
    "      const want = Math.min(1, Math.max(0, rise - 1.5)/7) * (st.dist > 4 ? 1 : 0); st.upk = st.upk == null ? want : st.upk + (want - st.upk)*Math.min(1, dt*1.5);\n"
    "      if(st.upk > 0.01){ const k = st.upk; camLook.x += fx*st.dist*0.9*k; camLook.z += fz*st.dist*0.9*k; camLook.y += Math.min(st.dist*1.2, rise*0.45 + st.dist*0.45)*k; } }\n")


def patch_uplook(P):
    a = "    if(dt===0 || !st.camInit){ camera.position.copy(camPos); st.camInit = true; } else camera.position.lerp(camPos, Math.min(1, dt*14));"
    P.rep(a, UPLOOK_JS + a, 1)
