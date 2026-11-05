"""함께 걷기: 다른 사람 걸음을 끊김 없이 (2026-11-05 승연)

- 예전: 위치가 1.2초마다 오는데, 받자마자 0.4초 만에 따라붙고 멈춰서 '세 걸음 걷고 멈추기'처럼 보였어요.
- 이제: 받은 위치를 시간과 함께 쌓아 두고, 약 한 번 받는 간격만큼 늦춰서 그 사이를 고르게 이어 걸어요.
  오래 서 있다가 다시 걷기 시작하면 한 간격 전에 출발한 것으로 이어서 갑자기 미끄러지지 않게.
  30m 넘게 한 번에 바뀌면(순간이동) 바로 그 자리로.
"""

MP_JS = r'''
// ---------- 함께 걷기 보간 (pipeline/mp_patch.py) ----------
function mpSample(a){ const now = performance.now(), B = a.buf || (a.buf = []), L = B[B.length - 1];
  if(L && L.x === a.tx && L.z === a.tz) return;
  if(L){ const dt = now - L.t; if(Math.hypot(a.tx - L.x, a.tz - L.z) > 30){ B.length = 0; a.x = a.tx; a.z = a.tz; }
    else { a.gap = a.gap ? a.gap*0.7 + Math.min(2500, Math.max(150, dt))*0.3 : Math.min(2500, Math.max(150, dt));
      if(dt > a.gap*1.6) B.push({ t: now - a.gap, x: L.x, z: L.z }); } }
  B.push({ t: now, x: a.tx, z: a.tz }); while(B.length > 10) B.shift(); }
function mpPos(a){ const B = a.buf; if(!B || !B.length) return [a.tx, a.tz];
  const D = Math.min(1800, (a.gap || 1200)*1.15 + 80), rt = performance.now() - D;
  if(rt <= B[0].t) return [B[0].x, B[0].z];
  for(let i = B.length - 1; i > 0; i--){ const p = B[i-1], q = B[i]; if(rt >= p.t){ if(rt >= q.t) return [q.x, q.z]; const k = (rt - p.t)/Math.max(1, q.t - p.t); return [p.x + (q.x - p.x)*k, p.z + (q.z - p.z)*k]; } }
  return [B[B.length-1].x, B[B.length-1].z]; }
window.__mp = { mpSample, mpPos };
'''


def patch_mp(P, m):
    P.rep("function updateRemotes(dt){", MP_JS + "function updateRemotes(dt){", 1)
    P.rep("a.tf = num(pr.f); a.moving = pr.m===1;", "a.tf = num(pr.f); mpSample(a); a.moving = pr.m===1;", 1)
    P.rep("    a.x += (a.tx-a.x)*Math.min(1,dt*6); a.z += (a.tz-a.z)*Math.min(1,dt*6);",
          "    { const [ix, iz] = mpPos(a); a.x += (ix - a.x)*Math.min(1, dt*12); a.z += (iz - a.z)*Math.min(1, dt*12); }", 1)
    # 걷는 모습: 받은 '걷는 중' 표시 대신 실제로 움직이는지로 (보간 중에도 다리가 자연스럽게)
    P.rep("animHiker(a.h, a.phase, a.moving?Math.min(1,sp/2):0, a.sit, a.waveT);",
          "animHiker(a.h, a.phase, (a.moving || sp > 0.25) ? Math.min(1, sp/2) : 0, a.sit, a.waveT);", 1)
