"""멀미 없는 카메라 + 바위·통나무·돌계단 위로 걷기 (2026-11-03)

카메라
- 예전: 카메라가 아바타 위치를 그대로 바라보고(lookAt), 높이는 걸음·계단마다 따라 출렁였어요. 자동 걷기는 다섯 점 앞을 보고 방향을 틀어 좌우로 살짝 지그재그.
- 이제: 카메라가 바라보는 점을 스프링처럼 부드럽게 따라가요 (가로 0.3초, 높이 0.6초). 1인칭 걸음 흔들림은 뺐어요.
  자동 걷기는 이동 방향도 부드럽게 돌아요.
지형지물
- 예전: 바위·물가 바위·노두·쓰러진 통나무·돌계단을 지나가면 아바타가 그 속에 묻혔어요.
- 이제: 무릎 높이(0.9m)까지는 위로 올라서 넘어가고, 그보다 높은 바위는 막혀서 옆으로 미끄러지듯 비켜 가요.
"""

# 3인칭 카메라와 아바타 사이를 '실제로 가리는' 나무·큰 바위만, 그루 단위로 반투명하게(점묘 디더) 흐려요.
# - 카메라에서 아바타를 잇는 선보다 낮은 풀·작은 바위·덤불은 건드리지 않아요 (아바타가 지우며 걷는 느낌 없애기)
# - 선에서 멀어질수록 점점 덜 흐려져서 툭 사라지지 않아요. 카메라 바로 앞을 막는 것만 완전히 숨겨요
# - 지형은 절대 자르지 않아요
VEG_JS = r"""
  { const VU = window.__vegU || (window.__vegU = { uCutOn:{value:0}, uCamP:{value:new THREE.Vector3()}, uAvP:{value:new THREE.Vector3()} });
    VU.uCutOn.value = (!st.fp && st.dist > 4) ? 1 : 0; VU.uCamP.value.copy(camera.position); VU.uAvP.value.set(st.x, heightAt(st.x, st.z) + 1.0, st.z);
    if(camera.near !== 0.3){ camera.near = 0.3; camera.updateProjectionMatrix(); }
    const tn = performance.now(); if(!(tn < (st.cutT || 0))){ st.cutT = tn + 2000; scene.traverse(o => { if(!o.isInstancedMesh) return;
      if(!o.geometry.boundingBox) o.geometry.computeBoundingBox(); const bb = o.geometry.boundingBox, top = bb.max.y, rad = Math.max(Math.abs(bb.min.x), bb.max.x, Math.abs(bb.min.z), bb.max.z);
      for(const m of (Array.isArray(o.material) ? o.material : [o.material])){ if(!m || m.isShaderMaterial) continue;
        if(m.__cut){ m.__topU.value = Math.max(m.__topU.value, top); m.__radU.value = Math.max(m.__radU.value, rad); continue; }
        m.__cut = 1; m.__topU = {value: top}; m.__radU = {value: rad}; const pb = m.onBeforeCompile, pk = m.customProgramCacheKey;
        m.onBeforeCompile = function(sh, r){ if(pb) pb.call(this, sh, r); if(!sh.vertexShader.includes('#include <project_vertex>') || !sh.fragmentShader.includes('#include <clipping_planes_fragment>')) return;
          Object.assign(sh.uniforms, VU, { uTopY: this.__topU, uRadXZ: this.__radU });
          sh.vertexShader = 'uniform float uCutOn, uTopY, uRadXZ; uniform vec3 uCamP, uAvP; varying float vCut;\n' + sh.vertexShader.replace('#include <project_vertex>', `#include <project_vertex>
  vCut = 0.0;
  if(uCutOn > 0.5){
  #ifdef USE_INSTANCING
    mat4 IM = modelMatrix * instanceMatrix;
  #else
    mat4 IM = modelMatrix;
  #endif
    vec3 ip = (IM * vec4(0.0, 0.0, 0.0, 1.0)).xyz; float sy = length(IM[1].xyz), sxz = length(IM[0].xyz);
    float top = ip.y + uTopY * sy, rr = uRadXZ * sxz + 0.4;
    vec2 dd = ip.xz - uCamP.xz, sg = uAvP.xz - uCamP.xz; float sl = max(0.01, dot(sg, sg)); float tt = clamp(dot(dd, sg)/sl, 0.0, 1.0); float lt = length(dd - sg*tt);
    float ly = mix(uCamP.y, uAvP.y, tt);
    float occ = (1.0 - smoothstep(rr, rr + 2.0, lt)) * smoothstep(ly - 0.6, ly + 0.4, top) * (1.0 - smoothstep(0.86, 0.97, tt)) * step(0.0001, tt);
    vec3 cp = vec3(dd.x, clamp(uCamP.y, ip.y, top) - uCamP.y, dd.y); float nr = 1.0 - smoothstep(rr + 0.6, rr + 2.6, length(cp));
    vCut = max(occ * 0.82, nr);
  }`);
          sh.fragmentShader = 'varying float vCut;\n' + sh.fragmentShader.replace('#include <clipping_planes_fragment>', `#include <clipping_planes_fragment>
  if(vCut > 0.01){ vec2 q = mod(floor(gl_FragCoord.xy), 4.0); const float B[16] = float[16](0.,8.,2.,10.,12.,4.,14.,6.,3.,11.,1.,9.,15.,7.,13.,5.); float th = (B[int(q.y*4.0 + q.x)] + 0.5) / 16.0; if(vCut > 0.995 || th < vCut) discard; }`); };
        m.customProgramCacheKey = function(){ return (pk ? pk.call(this) : '') + '|vegcut3'; }; m.needsUpdate = true; } }); } }"""

ROCK_JS = r'''
// ---------- 바위·통나무·돌계단 충돌 (pipeline/camera_patch.py) ----------
// 야영장 안·탐방로 위의 바위는 치워요 (앉을 자리·텐트·길과 겹치지 않게)
{ const M = new THREE.Matrix4(), Z = new THREE.Matrix4().makeScale(0,0,0), v = new THREE.Vector3();
  scene.traverse(o => { if(!o.isInstancedMesh || o.geometry.type !== 'IcosahedronGeometry') return; let ch = false;
    const R0 = (o.geometry.parameters && o.geometry.parameters.radius) || 1;
    for(let n=0;n<o.count;n++){ o.getMatrixAt(n, M); v.setFromMatrixPosition(M); if(Math.hypot(v.x-CAMP.x, v.z-CAMP.z) < 8.5){ o.setMatrixAt(n, Z); ch = true; continue; }
      // 탐방로 위·바로 옆 바위도 치워요 (물가 바위 줄이 길을 가로막아 제자리걸음 하던 문제)
      const e = M.elements, rr = R0*Math.max(Math.hypot(e[0], e[1], e[2]), Math.hypot(e[8], e[9], e[10])), nt = nearTrail(v.x, v.z, 2);
      if(nt.i >= 0 && nt.d < rr + 0.6){ o.setMatrixAt(n, Z); ch = true; } }
    if(ch) o.instanceMatrix.needsUpdate = true; }); }
ROCKC = (()=>{
  const ok = im => { const g = im.geometry, t = g.type, p = g.parameters || {};
    return t === 'IcosahedronGeometry' || t === 'BoxGeometry' || (t === 'CylinderGeometry' && (p.radiusBottom||0) >= 0.1); };
  const list = [], G = new Map(), C = 4, key = (i, j) => i*100003 + j, M4 = new THREE.Matrix4();
  scene.traverse(o => { if(!o.isInstancedMesh || !ok(o) || o === window.__skipRock) return; o.updateMatrixWorld(true);
    const ZERO_M = new THREE.Matrix4().makeScale(0,0,0);
    const tmp = new THREE.Mesh(o.geometry); tmp.matrixAutoUpdate = false; if(!o.geometry.boundingBox) o.geometry.computeBoundingBox(); const bb = o.geometry.boundingBox;
    for(let n = 0; n < o.count; n++){ o.getMatrixAt(n, M4); M4.premultiply(o.matrixWorld); const e = M4.elements;
      const hx = Math.hypot(e[0], e[4], e[8]) * Math.max(Math.abs(bb.min.x), Math.abs(bb.max.x), Math.abs(bb.min.y), Math.abs(bb.max.y), Math.abs(bb.min.z), Math.abs(bb.max.z));
      // 가로 반경: 열벡터들의 x·z 성분으로 감싼 상자
      const rx = (Math.abs(e[0]) + Math.abs(e[4]) + Math.abs(e[8])) * 1.0, rz = (Math.abs(e[2]) + Math.abs(e[6]) + Math.abs(e[10])) * 1.0, ry = (Math.abs(e[1]) + Math.abs(e[5]) + Math.abs(e[9]));
      const r = { x:e[12], y:e[13], z:e[14], rx:rx*Math.max(Math.abs(bb.min.x),bb.max.x), rz:rz*Math.max(Math.abs(bb.min.z),bb.max.z), top:e[13] + ry*Math.max(Math.abs(bb.min.y),bb.max.y), m:M4.clone(), mesh:tmp };
      if(r.top < heightAt(r.x, r.z) + 0.12) continue;   // 땅속에 잠긴 것
      // 탐방로를 가로막는 키 큰 바위는 치워요 (황산 등에서 길 위 바위에 막혀 제자리걸음 하던 문제)
      if(o.geometry.type !== 'CylinderGeometry' && o.geometry.type !== 'BoxGeometry' && r.top - heightAt(r.x, r.z) > 0.9){ const nt = nearTrail(r.x, r.z, 2);
        if(nt.i >= 0 && nt.d < Math.max(r.rx, r.rz) + 1.0){ o.setMatrixAt(n, ZERO_M); o.instanceMatrix.needsUpdate = true; continue; } }
      list.push(r); const i0 = Math.floor((r.x - r.rx)/C), i1 = Math.floor((r.x + r.rx)/C), j0 = Math.floor((r.z - r.rz)/C), j1 = Math.floor((r.z + r.rz)/C);
      for(let i = i0; i <= i1; i++) for(let j = j0; j <= j1; j++){ const k = key(i, j); let a = G.get(k); if(!a) G.set(k, a = []); a.push(r); } } });
  const ray = new THREE.Raycaster(), down = new THREE.Vector3(0, -1, 0), o = new THREE.Vector3(), hits = [];
  // (x,z) 에서 지형지물 윗면 높이 (없으면 -Infinity)
  const surf = (x, z) => { const a = G.get(key(Math.floor(x/C), Math.floor(z/C))); if(!a) return -Infinity; let best = -Infinity;
    for(const r of a){ if(Math.abs(x - r.x) > r.rx || Math.abs(z - r.z) > r.rz || r.top < best) continue;
      r.mesh.matrixWorld.copy(r.m); o.set(x, r.top + 1, z); ray.set(o, down); ray.far = r.top + 2 - (heightAt(x, z) - 1); hits.length = 0; r.mesh.raycast(ray, hits);
      for(const h of hits) if(h.point.y > best) best = h.point.y; }
    return best; };
  const STEP = 0.9, FOOT = 0.18;
  return {
    n: list.length, list,
    // 올라설 수 있는 높이면 그 위에 서요
    // 탐방로 위(가운데서 2.4m 안)에서는 더 높은 바위도 타고 올라 넘어가요
    top(x, z, gy){ let y = -Infinity; for(const [a, b] of [[0,0],[FOOT,0],[-FOOT,0],[0,FOOT],[0,-FOOT]]){ const s = surf(x+a, z+b); if(s > y) y = s; } const lim = nearTrail(x, z, 1).d < 2.4 ? 3.2 : STEP; return y - gy <= lim ? y : -Infinity; },
    // 너무 높은 바위면 막혀요
    blocked(x, z){ if(nearTrail(x, z, 1).d < 2.4) return false;   // 탐방로 위는 절대 막히지 않아요
      const g = heightAt(x, z); for(const [a, b] of [[0,0],[0.22,0],[-0.22,0],[0,0.22],[0,-0.22]]){ if(surf(x+a, z+b) - g > STEP) return true; } return false; },
  };
})(); window.__ROCKC = ROCKC;
'''


def patch_camera(P, m):
    # --- 지형지물 ---
    P.rep("function standY(x, z, ni){\n  let y = heightAt(x, z); const r = 0.26;",
          "let ROCKC = null;\nfunction standY(x, z, ni){\n  let y = heightAt(x, z); const r = 0.26;", 1)
    P.rep("  return y;\n}\n// trail ribbon (흙길)", "  if(ROCKC){ const ry = ROCKC.top(x, z, y); if(ry > y) y = ry - 0.01; }\n  return y;\n}\n// trail ribbon (흙길)", 1)
    P.rep("window.__game = {", ROCK_JS + "window.__game = {", 1)
    P.rep("      if(Math.abs(nx)<HALF-8 && Math.abs(nz)<HALF-8){ st.walked += Math.hypot(nx-st.x, nz-st.z); st.x=nx; st.z=nz; }",
          "      let ax = nx, az = nz;   // 높은 바위는 옆으로 비켜 가요\n"
          "      if(ROCKC && ROCKC.blocked(ax, az) && !ROCKC.blocked(st.x, st.z)){ if(!ROCKC.blocked(ax, st.z)) az = st.z; else if(!ROCKC.blocked(st.x, az)) ax = st.x; else { ax = st.x; az = st.z; } }\n"
          "      // 자동 걷기는 탐방로 가운데에서 1.1m 안쪽으로만 (길가 밧줄 난간·울타리를 넘지 않게)\n"
          "      if(st.auto && !st.goal && !forward && !strafe && !st.inSummit){ const q = nearTrail(ax, az, 1); if(q.i >= 0 && q.d > 1.1){ const c = trail[q.i], kq = 1.1/q.d; ax = c.x + (ax - c.x)*kq; az = c.z + (az - c.z)*kq; } }\n"
          "      if(Math.abs(ax)<HALF-8 && Math.abs(az)<HALF-8){ st.walked += Math.hypot(ax-st.x, az-st.z); st.x=ax; st.z=az; }", 1)
    # 돌계단 높이는 이제 실제 계단 돌 위에 서서 정해져요 → 걸음마다 넣던 계단 들썩임은 빼요
    P.rep("(onTrail ? stairAt[nt.i]*0.5*(1 - Math.cos(2*st.phase))*0.5 : 0)", "0", 1)

    # --- 자동 걷기 방향을 부드럽게 ---
    P.rep("if(joy.id !== null && Math.hypot(joy.x, joy.y) > 0.18){ forward = -joy.y; strafe = joy.x; joySprint = Math.hypot(joy.x, joy.y) > 0.97; st.goal = null; }",
          "if(joy.id !== null && Math.hypot(joy.x, joy.y) > 0.18){ forward = -joy.y; strafe = joy.x; joySprint = Math.hypot(joy.x, joy.y) > 0.97; st.goal = null; if(st.auto){ st.auto = false; refreshWalk(); } }", 1)
    P.rep("    const ml = Math.hypot(mx,mz)||1; mx/=ml; mz/=ml;\n",
          "    const ml = Math.hypot(mx,mz)||1; mx/=ml; mz/=ml;\n"
          "    if(st.auto && !st.goal && !forward && !strafe){ if(!st.md) st.md = { x:mx, z:mz }; const kk = Math.min(1, dt*3.5); st.md.x += (mx-st.md.x)*kk; st.md.z += (mz-st.md.z)*kk; const l2 = Math.hypot(st.md.x, st.md.z)||1; mx = st.md.x/l2; mz = st.md.z/l2; } else st.md = null;\n", 1)
    P.rep("if(nt.d < 2.5) j = Math.min(trail.length-1, nt.i + 5);", "if(nt.d < 2.5) j = Math.min(trail.length-1, nt.i + Math.max(3, Math.round(8 - nt.d*4)));", 1)
    P.rep("if(nt.d < 2.5) j = Math.max(0, nt.i - 5);", "if(nt.d < 2.5) j = Math.max(0, nt.i - Math.max(3, Math.round(8 - nt.d*4)));", 1)

    # --- 카메라: 바라보는 점을 스프링처럼 ---
    P.rep("  if(st.camY == null || dt === 0 || Math.abs(yRaw - st.camY) > 3) st.camY = yRaw; else st.camY += (yRaw - st.camY) * Math.min(1, dt*5);\n  const yC = st.camY;",
          "  { const F = st.cf || (st.cf = { x:st.x, y:yRaw, z:st.z, vx:0, vy:0, vz:0 });\n"
          "    const sd = (c, v, tg, T) => { const w = 2/T, x = w*dt, e = 1/(1 + x + 0.48*x*x + 0.235*x*x*x), ch = c - tg, tmp = (v + w*ch)*dt; return [tg + (ch + tmp)*e, (v - w*tmp)*e]; };\n"
          "    if(dt === 0 || !st.camInit || Math.hypot(st.x - F.x, st.z - F.z) > 6 || Math.abs(yRaw - F.y) > 4){ F.x = st.x; F.y = yRaw; F.z = st.z; F.vx = F.vy = F.vz = 0; }\n"
          "    else { [F.x, F.vx] = sd(F.x, F.vx, st.x, 0.3); [F.z, F.vz] = sd(F.z, F.vz, st.z, 0.3); [F.y, F.vy] = sd(F.y, F.vy, yRaw, st.sitting ? 0.35 : 0.6); }\n"
          "    st.camY = F.y; }\n"
          "  const yC = st.camY, fX = st.cf.x, fZ = st.cf.z;", 1)
    P.rep("    const bob = 0.22*Math.sin(st.phase*2)*(0.035+Math.max(0,grade)*0.06)*Math.min(1,Math.max(speed,0.6)/2);\n    camPos.set(st.x, yC + (st.sitting?1.0:1.45) + bob, st.z);",
          "    camPos.set(fX, yC + (st.sitting?1.0:1.45), fZ);   // 1인칭: 걸음 흔들림 없이", 1)
    P.rep("    camLook.set(st.x - Math.sin(st.yaw)*Math.cos(p)*10, camPos.y - Math.sin(p)*10, st.z - Math.cos(st.yaw)*Math.cos(p)*10);",
          "    camLook.set(fX - Math.sin(st.yaw)*Math.cos(p)*10, camPos.y - Math.sin(p)*10, fZ - Math.cos(st.yaw)*Math.cos(p)*10);", 1)
    P.rep("    camLook.set(st.x, yC+1.1 + Math.tan(Math.min(1.35, lookUp*1.45))*st.dist, st.z);\n    camPos.set(st.x + Math.sin(st.yaw)*cy*st.dist, yC + 1.1 + sy*st.dist, st.z + Math.cos(st.yaw)*cy*st.dist);\n    const g = heightAt(camPos.x, camPos.z) + 0.8; if(camPos.y < g) camPos.y = g;\n    if(dt===0 || !st.camInit){ camera.position.copy(camPos); st.camInit = true; } else camera.position.lerp(camPos, Math.min(1, dt*8));",
          "    camLook.set(fX, yC+1.1 + Math.tan(Math.min(1.35, lookUp*1.45))*st.dist, fZ);\n"
          "    camPos.set(fX + Math.sin(st.yaw)*cy*st.dist, yC + 1.1 + sy*st.dist, fZ + Math.cos(st.yaw)*cy*st.dist);\n"
          "    { const need = Math.max(0, heightAt(camPos.x, camPos.z) + 0.8 - camPos.y); let los = 0;\n"
          "      // 드론처럼 멀리 뺀 카메라: 아바타와 카메라 사이를 언덕이 가리면 카메라를 그만큼 위로 (시야 확보)\n"
          "      if(st.dist > 9){ const ly = camLook.y, cy0 = camPos.y + need; let want = cy0; for(let t = 0.2; t < 0.99; t += 0.08){ const x = camLook.x + (camPos.x - camLook.x)*t, z = camLook.z + (camPos.z - camLook.z)*t, g = heightAt(x, z) + 1.6; if(ly + (want - ly)*t < g) want = ly + (g - ly)/t; } los = Math.min(want - cy0, st.dist*0.9); }\n"
          "      const tgt = need + los; st.lift = (dt === 0 || !st.camInit || st.lift == null) ? tgt : st.lift + (tgt - st.lift)*Math.min(1, dt*(tgt > st.lift ? 4 : 1.2)); camPos.y += Math.max(st.lift, need - 0.35); }   // 땅 밑으로 안 들어가게, 그러나 출렁이지 않게\n"
          "    if(dt===0 || !st.camInit){ camera.position.copy(camPos); st.camInit = true; } else camera.position.lerp(camPos, Math.min(1, dt*14));", 1)
    # 드론 시점: 카메라 바로 앞 나무·바위·풀만 잘라내요 (지형은 그대로 두어 땅 밑 빈 공간이 보이지 않게)
    # 드론 시점: 카메라와 아바타 사이, 카메라 바로 아래 나무·바위는 '그루 단위'로 통째로 숨겨요
    # (조각으로 잘라내면 화면 아래쪽 나무가 찢어져 보여서, 지형은 절대 자르지 않아요)
    P.rep("\n  camera.lookAt(camLook);", "\n  camera.lookAt(camLook);" + VEG_JS, 1)
