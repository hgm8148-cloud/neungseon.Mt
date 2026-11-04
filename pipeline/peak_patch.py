"""정상 실루엣 (2026-11-04)

산길을 오르며 정상 쪽을 올려다보면, 가까운 비탈 너머로 그 산의 대표 모습(후지산의 원뿔, 마터호른의 뿔…)이
보이게 해요. 탐방로·지형은 그대로 두고, 하늘에 걸린 '먼 정상 그림'만 더해요.

- 산 설정 `peakArt`: profile(실루엣 점, x 0~1 · y 0~1), aspect(가로/세로), ang(보이는 높이, 도),
  rock/rock2/forest(색), snow(계절별 눈 덮인 비율, 위에서부터), streak(눈 골 줄무늬 세기), haze(먼 공기 흐림).
- 실루엣은 Drive 대표 사진을 보고 따서 만들어요(사진 픽셀은 쓰지 않아요 → 계절·시간에 맞게 색이 바뀌어요).
- 보이는 자리: 내 위치에서 정상 쪽 방향, 가까운 능선(지형) 바로 뒤. 앞의 지형·나무가 가리면 가려져요.
- 정상에 가까워지면(탐방로 82%→92%) 서서히 사라져서, 진짜 정상에 서면 겹쳐 보이지 않아요.
"""
import json

PEAK_JS = r'''
// ---------- 정상 실루엣: 올려다보면 이 산의 대표 모습 (pipeline/peak_patch.py) ----------
{ const CFG = __CFG__;
  const N = 256, prof = new Uint8Array(N * 4); let smax = 0;
  const P = CFG.profile; const at = u => { for(let k = 1; k < P.length; k++){ if(u <= P[k][0]){ const a = P[k-1], b = P[k], t = (u - a[0]) / Math.max(1e-6, b[0] - a[0]); const s = t*t*(3 - 2*t); return a[1] + (b[1] - a[1]) * (CFG.smooth ? s : t); } } return P[P.length-1][1]; };
  for(let i = 0; i < N; i++){ const y = Math.max(0, Math.min(1, at(i / (N - 1)))); smax = Math.max(smax, y); prof[i*4] = Math.round(y * 255); prof[i*4+3] = 255; }
  const tex = new THREE.DataTexture(prof, N, 1, THREE.RGBAFormat); tex.magFilter = THREE.LinearFilter; tex.minFilter = THREE.LinearFilter; tex.needsUpdate = true;
  const SN = CFG.snow || {}; const snowAmt = (SN[SEASON] != null ? SN[SEASON] : SN.all != null ? SN.all : 0);
  const C = c => new THREE.Color(c);
  const mat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, fog: false, toneMapped: false,
    uniforms: { uProf: {value: tex}, uRock: {value: C(CFG.rock || '#5d5048')}, uRock2: {value: C(CFG.rock2 || CFG.rock || '#77685c')}, uForest: {value: C((CFG.forestBy && CFG.forestBy[SEASON]) || CFG.forest || CFG.rock2 || CFG.rock || '#4a5a40')},
      uForestTop: {value: CFG.forestTop != null ? CFG.forestTop : (CFG.forest ? 0.32 : -1)}, uSnow: {value: snowAmt}, uStreak: {value: CFG.streak != null ? CFG.streak : 1}, uFog: {value: new THREE.Color(0xc8d4e2)},
      uHaze: {value: CFG.haze != null ? CFG.haze : 0.32}, uDay: {value: 1}, uSunX: {value: 0.5}, uSunCol: {value: new THREE.Color(0xffffff)}, uA: {value: 1}, uMax: {value: smax} },
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `precision highp float; varying vec2 vUv; uniform sampler2D uProf; uniform vec3 uRock, uRock2, uForest, uFog, uSunCol; uniform float uForestTop, uSnow, uStreak, uHaze, uDay, uSunX, uA, uMax;
      float h2(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f); return mix(mix(h2(i), h2(i+vec2(1,0)), f.x), mix(h2(i+vec2(0,1)), h2(i+vec2(1,1)), f.x), f.y); }
      float fb(vec2 p){ float s = 0.0, a = 0.5; for(int i = 0; i < 5; i++){ s += a*vn(p); p *= 2.03; a *= 0.5; } return s; }
      void main(){
        float s = texture2D(uProf, vec2(vUv.x, 0.5)).r, v = vUv.y;
        float edge = 1.0 - smoothstep(s - 0.006, s + 0.002, v); if(edge <= 0.001) discard;
        float sl = texture2D(uProf, vec2(vUv.x + 0.004, 0.5)).r - texture2D(uProf, vec2(vUv.x - 0.004, 0.5)).r;   // 실루엣 기울기 → 산 사면 방향
        float h = v / max(uMax, 0.05);                       // 0 아래 ~ 1 정상
        float depth = clamp((s - v) / max(s, 0.05), 0.0, 1.0);   // 능선에서 얼마나 아래인지
        // 골짜기 줄무늬: 능선에서 아래로 흘러내리는 무늬
        float gx = vUv.x * 46.0 + fb(vec2(vUv.x * 9.0, v * 3.0)) * 2.5;
        float gully = fb(vec2(gx, v * 5.0));
        float ridgeL = 0.80 + 0.30 * (gully - 0.5) * 1.6;
        // 사면 밝기: 해가 오는 쪽 사면은 밝게
        float side = clamp(-sl * 22.0, -1.0, 1.0); float lit = 0.80 + 0.22 * side * uSunX;
        vec3 rock = mix(uRock, uRock2, smoothstep(0.25, 0.75, fb(vec2(vUv.x * 14.0, v * 6.0))));
        vec3 col = rock;
        if(uForestTop > 0.0){ float f = 1.0 - smoothstep(uForestTop - 0.08, uForestTop + 0.06 + (gully - 0.5) * 0.12, h); col = mix(col, uForest * (0.85 + 0.3 * vn(vec2(vUv.x * 120.0, v * 60.0))), f); }
        col *= ridgeL * lit;
        // 눈: 정상에서부터 uSnow 만큼, 골을 따라 손가락처럼 흘러내려요
        float line = 1.0 - uSnow + (gully - 0.5) * 0.12 * uStreak;
        // 정상에서 방사형으로 흘러내리는 눈 골: 정상(가운데)에서 퍼지는 각도를 따라 가는 줄
        float ang = (vUv.x - 0.5) / max(1.05 - h, 0.08);
        float wob = fb(vec2(vUv.x * 7.0, v * 2.0)) * 1.6;
        float rib = 1.0 - abs(2.0 * fract(ang * 15.0 + wob) - 1.0);
        float rib2 = 1.0 - abs(2.0 * fract(ang * 9.0 + wob * 1.3 + 0.37) - 1.0);
        float fingers = pow(rib, 4.0) * 0.26 * uStreak * smoothstep(0.0, 0.2, uSnow);
        float snow = uSnow > 0.001 ? smoothstep(line - 0.02, line + 0.02, h + fingers) : 0.0;
        snow *= 1.0 - smoothstep(0.86, 0.97, rib2) * 0.75 * smoothstep(0.92, 0.55, h) * uStreak * step(uSnow, 0.7);   // 눈 사이로 드러난 바위 줄기
        vec3 sc = vec3(0.93, 0.95, 0.98) * (0.84 + 0.18 * side * uSunX) * (0.90 + 0.10 * rib);
        col = mix(col, sc, snow);
        // 빛: 낮·밤, 노을 색
        col *= mix(vec3(0.20, 0.24, 0.36), uSunCol, uDay);
        // 먼 공기: 아래쪽일수록 더 흐리게
        float haze = clamp(uHaze + (1.0 - h) * 0.14, 0.0, 0.92);
        col = mix(col, uFog, haze);
        float a = edge * smoothstep(0.0, 0.22, v) * uA;
        gl_FragColor = vec4(col, a);
        #include <colorspace_fragment>
      }` });
  const geo = new THREE.PlaneGeometry(1, 1); geo.translate(0, 0.5, 0);
  const mesh = new THREE.Mesh(geo, mat); mesh.frustumCulled = false; mesh.renderOrder = -0.5; scene.add(mesh); window.__PEAK = mesh;
  const SUM = trail[trail.length - 1], D = 8600, ANG = (CFG.ang || 12) * Math.PI / 180, ASP = CFG.aspect || 3;
  let sky = 0, prog = 0, tick = 0;
  const _v = new THREE.Vector3(), _d = new THREE.Vector3();
  window.__peakUpdate = () => {
    const cp = camera.position, az = Math.atan2(SUM.x - cp.x, SUM.z - cp.z), dx = Math.sin(az), dz = Math.cos(az);
    if((tick++ % 20) === 0){   // 가까운 지형이 정상 쪽에서 몇 도까지 올라와 있는지
      let m = -0.2; for(let t = 30; t < 2600; t += t < 400 ? 25 : 60){ const x = cp.x + dx*t, z = cp.z + dz*t; if(Math.abs(x) > HALF - 4 || Math.abs(z) > HALF - 4) break; const a = Math.atan2(heightAt(x, z) - cp.y, t); if(a > m) m = a; }
      sky = m; const nt = nearTrail(st.x, st.z, 2); if(nt.i >= 0) prog = nt.i / (trail.length - 1); }
    const base = sky - 0.012, top = base + ANG, y0 = cp.y + Math.tan(base) * D, y1 = cp.y + Math.tan(top) * D, hgt = y1 - y0;
    mesh.position.set(cp.x + dx*D, y0, cp.z + dz*D); mesh.scale.set(hgt * ASP, hgt, 1); mesh.rotation.set(0, az + Math.PI, 0);
    const U = mat.uniforms, fade = 1 - Math.min(1, Math.max(0, (prog - 0.82) / 0.10));
    U.uA.value = fade; mesh.visible = fade > 0.01 && !st.inSummit;
    if(mesh.visible){ const S = window.SKY || {}; U.uDay.value = S.day != null ? Math.max(0.05, S.day) : 1; U.uFog.value.copy(scene.fog.color);
      _d.copy(sun.position).sub(sun.target.position).normalize(); _v.set(Math.cos(az), 0, -Math.sin(az));   // 화면 오른쪽 방향
      U.uSunX.value = THREE.MathUtils.clamp(_d.x * _v.x + _d.z * _v.z, -1, 1) * -1;
      U.uSunCol.value.copy(sun.color).lerp(new THREE.Color(1, 1, 1), 0.55); }
  };
}
'''


GROUND_JS = r'''
// ---------- 이 산의 땅·바위 색 (pipeline/peak_patch.py · 산 설정 ground) ----------
{ const G = __G__; const rocks = window.__rocks;
  if(rocks && G.rockTint){ rocks.material.color.set(G.rockTint); if(rocks.material.map){ rocks.material.map = rocks.material.map.clone(); rocks.material.map.needsUpdate = true; } }
  if(rocks && G.shrinkAbove != null){ const M = new THREE.Matrix4(), p = new THREE.Vector3(), q = new THREE.Quaternion(), sc = new THREE.Vector3();
    for(let n = 0; n < rocks.count; n++){ rocks.getMatrixAt(n, M); M.decompose(p, q, sc); if(sc.x < 1e-4) continue; if(heightAt(p.x, p.z) > G.shrinkAbove){ const k = G.shrink || 0.4; sc.multiplyScalar(k); p.y = heightAt(p.x, p.z) + (p.y - heightAt(p.x, p.z)) * k; M.compose(p, q, sc); rocks.setMatrixAt(n, M); } }
    rocks.instanceMatrix.needsUpdate = true; }
}
'''


def patch_peak(P, m, meta):
    g = m.get('ground')
    if g:
        if g.get('rock'):
            P.rep("if(SZ.snow){ C.rock.lerp(", "C.rock.set(" + json.dumps(g['rock'][0]) + "); C.rockDark.set(" + json.dumps(g['rock'][1]) + ");\nif(SZ.snow){ C.rock.lerp(", 1)
        if g.get('rkTint'):   # 가까운 땅의 바위 질감 색 (후지산: 붉은 화산 자갈)
            t = g['rkTint']
            P.rep("        rk = mix(rk, vec3(0.92,0.94,0.97), ${", f"        rk *= vec3({t[0]:.3f}, {t[1]:.3f}, {t[2]:.3f});\n        rk = mix(rk, vec3(0.92,0.94,0.97), ${{", 1)
        gg = dict(g)
        if 'shrinkAbove' in gg:
            gg['shrinkAbove'] = gg['shrinkAbove'] - meta['BASE']
        P.rep("// ---------- 바위·통나무·돌계단 충돌", GROUND_JS.replace('__G__', json.dumps(gg)) + "// ---------- 바위·통나무·돌계단 충돌", 1)
    cfg = m.get('peakArt')
    if not cfg or m.get('relief'):   # 3D 정상(relief)을 쓰는 산은 하늘 그림을 쓰지 않아요
        return
    P.rep("window.__game = {", PEAK_JS.replace('__CFG__', json.dumps(cfg)) + "window.__game = {", 1)
    P.rep("\n  camera.lookAt(camLook);", "\n  camera.lookAt(camLook);\n  if(window.__peakUpdate) window.__peakUpdate();", 1)
