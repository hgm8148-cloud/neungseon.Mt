"""계절 날씨 + 게임 중 계절 바꾸기 (2026-11-03)

- 예전: 사계절 내내 낙엽이 쉬지 않고 떨어졌어요.
- 이제: 봄 꽃잎 · 여름 소나기 · 가을 낙엽 · 겨울 눈이 산행 중 가끔, 무작위로 찾아와요.
  첫 번째는 1~2분 뒤, 그다음은 2~5분 간격, 한 번에 45~100초. 20분 산행이면 서너 번쯤.
  소나기·눈이 올 때는 하늘이 회색으로 흐려지고, 햇빛·별빛이 약해지고, 안개가 짙어져요. 비는 빗소리도.
- 오른쪽 위 도구에 '계절' 버튼: 봄·여름·가을·겨울을 바로 고르면, 지금 자리를 저장하고 산을 새로 그린 뒤 그 자리에서 이어 걸어요.
"""

WX_ROWS = [
    ['봄바람에 꽃잎이 흩날려요 🌸', 'Petals drift on the spring breeze 🌸', '春風に花びらが舞っています 🌸', '春风吹落片片花瓣 🌸'],
    ['소나기가 지나가요 · 하늘이 잠시 흐려져요 🌧', 'A passing shower · the sky clouds over for a while 🌧', 'にわか雨です · 空がしばらく曇ります 🌧', '一阵阵雨经过 · 天空暂时阴了下来 🌧'],
    ['바람에 낙엽이 흩날려요 🍂', 'Leaves swirl in the wind 🍂', '風に落ち葉が舞っています 🍂', '落叶随风飞舞 🍂'],
    ['눈발이 날리기 시작해요 ❄', 'Snowflakes begin to fall ❄', '雪がちらつき始めました ❄', '开始飘雪了 ❄'],
    ['비가 그쳤어요 · 하늘이 다시 개요', 'The rain has stopped · the sky is clearing', '雨がやみました · 空が晴れてきます', '雨停了 · 天空又放晴了'],
    ['눈이 그쳤어요', 'The snow has stopped', '雪がやみました', '雪停了'],
    ['계절 바꾸기', 'Change season', '季節を変える', '更换季节'],
    ['이 자리에서 계절을 바꿔요 · 산을 새로 그린 뒤 이어서 걸어요', 'Change the season here · the mountain is redrawn and you continue from this spot', 'ここで季節を変えます · 山を描き直してから続きを歩きます', '在此更换季节 · 重新绘制山景后从这里继续'],
    ['계절이 바뀌었어요 · 이어서 걸어요', 'The season has changed · keep walking', '季節が変わりました · 続きを歩きましょう', '季节已更换 · 继续前行'],
]

WX_JS = r'''
// ---------- 계절 날씨: 봄 꽃잎 · 여름 소나기 · 가을 낙엽 · 겨울 눈이 가끔 (pipeline/weather_patch.py) ----------
const WX = (()=>{
  let S = 'autumn'; try{ S = SEASON; }catch(e){}
  const kind = ({spring:'petal', summer:'rain', autumn:'leaf', winter:'snow', fixed:'snow'})[S] || 'leaf';
  const MSG = { petal:'봄바람에 꽃잎이 흩날려요 🌸', rain:'소나기가 지나가요 · 하늘이 잠시 흐려져요 🌧', leaf:'바람에 낙엽이 흩날려요 🍂', snow:'눈발이 날리기 시작해요 ❄' };
  const END = { rain:'비가 그쳤어요 · 하늘이 다시 개요', snow:'눈이 그쳤어요' };
  const W = { kind, amt:0, target:0, next:55 + Math.random()*70, left:0, cw:0, count:0 };
  // 꽃잎: 잎 모양 대신 꽃잎 그림, 분홍·흰빛
  if(kind === 'petal'){
    const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'); x.translate(64,64);
    const gr = x.createRadialGradient(0,10,4,0,0,56); gr.addColorStop(0,'#fff'); gr.addColorStop(1,'#f4f0f2'); x.fillStyle = gr;
    x.beginPath(); x.moveTo(0,52); x.bezierCurveTo(44,30,40,-34,12,-50); x.quadraticCurveTo(0,-38,-12,-50); x.bezierCurveTo(-40,-34,-44,30,0,52); x.fill();
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; const pc = [0xf6c6d4, 0xf9dbe4, 0xf1b3c6, 0xfde9ef, 0xf5c0cf];
    leafMeshes.forEach((m,k) => { m.material.map = t; m.material.needsUpdate = true; for(let j=0;j<m.count;j++) m.setColorAt(j, new THREE.Color(pc[(j+k*2)%pc.length])); m.instanceColor.needsUpdate = true; });
    for(const v of leafVel) v.sc *= 0.55;
  }
  // 소나기: 비스듬히 떨어지는 빗줄기
  let rain = null, snow = null;
  if(kind === 'rain'){ const N = 1500, pos = new Float32Array(N*6), sp = new Float32Array(N);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const m = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color:0xc4ceda, transparent:true, opacity:0, depthWrite:false }));
    m.frustumCulled = false; m.visible = false; scene.add(m); for(let i=0;i<N;i++){ sp[i] = 15 + Math.random()*7; pos[i*6+1] = -1e5; } rain = { m, pos, sp, N }; }
  // 눈: 천천히 흔들리며 내려오는 눈송이
  if(kind === 'snow'){ const N = 1700, pos = new Float32Array(N*3), ph = new Float32Array(N);
    const c = document.createElement('canvas'); c.width = c.height = 32; const x = c.getContext('2d'); const gr = x.createRadialGradient(16,16,0,16,16,16);
    gr.addColorStop(0,'rgba(255,255,255,1)'); gr.addColorStop(0.45,'rgba(255,255,255,.75)'); gr.addColorStop(1,'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(0,0,32,32);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const m = new THREE.Points(g, new THREE.PointsMaterial({ size:0.13, map:new THREE.CanvasTexture(c), transparent:true, opacity:0, depthWrite:false, color:0xffffff }));
    m.frustumCulled = false; m.visible = false; scene.add(m); for(let i=0;i<N;i++){ ph[i] = Math.random()*100; pos[i*3+1] = -1e5; } snow = { m, pos, ph, N }; }
  const zero = new THREE.Matrix4().makeScale(0,0,0);
  W.start = (quiet) => { W.target = 1; W.left = 45 + Math.random()*55; W.count++; if(!quiet) toast(MSG[kind], 4); };
  W.update = (dt, started, y) => {
    if(started){ if(W.target > 0){ W.left -= dt; if(W.left <= 0){ W.target = 0; W.next = 120 + Math.random()*180; if(END[kind]) setTimeout(() => toast(END[kind], 3), 5000); } }
      else { W.next -= dt; if(W.next <= 0) W.start(); } }
    W.amt += (W.target - W.amt)*Math.min(1, dt*(W.target > W.amt ? 0.3 : 0.18)); if(W.amt < 0.002 && !W.target) W.amt = 0;
    W.cw = (kind === 'rain' ? 0.92 : kind === 'snow' ? 0.72 : 0)*THREE.MathUtils.smoothstep(W.amt, 0.0, 0.8);
    const cx = camera.position.x, cy = camera.position.y, cz = camera.position.z;
    // 잎·꽃잎
    const leafy = kind === 'leaf' || kind === 'petal', n = leafy ? Math.round(leafCount*W.amt) : 0;
    for(const m of leafMeshes) m.visible = n > 0;
    if(n > 0){ const lp = leafPos;
      for(let i=0;i<leafCount;i++){
        if(i >= n){ leafMeshes[i%LEAF_KINDS].setMatrixAt((i/LEAF_KINDS)|0, zero); continue; }
        const v = leafVel[i];
        if(!leavesInit || Math.abs(lp[i*3]-st.x)>25 || Math.abs(lp[i*3+2]-st.z)>25 || lp[i*3+1] < heightAt(lp[i*3],lp[i*3+2])){
          lp[i*3]=st.x+(rnd()-0.5)*50; lp[i*3+2]=st.z+(rnd()-0.5)*50; lp[i*3+1]=heightAt(lp[i*3],lp[i*3+2])+4+rnd()*14; }
        const sw = kind === 'petal' ? 0.6 : 1;
        v.ph += dt*2; lp[i*3] += (Math.sin(v.ph)*0.6 + 0.4)*dt; lp[i*3+2] += Math.cos(v.ph*0.7)*0.4*dt; lp[i*3+1] -= v.sp*sw*(0.75+0.35*Math.sin(v.ph*1.3))*dt;
        leafObj.position.set(lp[i*3],lp[i*3+1],lp[i*3+2]); leafObj.rotation.set(v.rx+v.ph*v.spin*0.5, v.ry+v.ph*0.3, Math.sin(v.ph)*0.9); leafObj.scale.setScalar(v.sc); leafObj.updateMatrix();
        leafMeshes[i%LEAF_KINDS].setMatrixAt((i/LEAF_KINDS)|0, leafObj.matrix); }
      leavesInit = true; for(const m of leafMeshes) m.instanceMatrix.needsUpdate = true; }
    if(rain){ const on = W.amt > 0.01; rain.m.visible = on; rain.m.material.opacity = 0.42*W.amt;
      if(window.__rainG) window.__rainG.gain.value = 0.2*W.amt;
      if(on){ const P = rain.pos, act = Math.round(rain.N*W.amt);
        for(let i=0;i<rain.N;i++){ const k = i*6;
          if(i >= act){ P[k+1] = P[k+4] = -1e5; continue; }
          let x = P[k], yy = P[k+1], z = P[k+2];
          if(yy < cy - 7 || Math.abs(x - cx) > 20 || Math.abs(z - cz) > 20){ x = cx + (Math.random()-0.5)*40; z = cz + (Math.random()-0.5)*40; yy = cy + 4 + Math.random()*12; }
          const d = rain.sp[i]*dt; yy -= d; x += d*0.12;
          P[k] = x; P[k+1] = yy; P[k+2] = z; P[k+3] = x - 0.08; P[k+4] = yy + 0.75; P[k+5] = z; }
        rain.m.geometry.attributes.position.needsUpdate = true; } }
    if(snow){ const on = W.amt > 0.01; snow.m.visible = on; snow.m.material.opacity = 0.95*W.amt;
      if(on){ const P = snow.pos, act = Math.round(snow.N*W.amt), t = performance.now()/1000;
        for(let i=0;i<snow.N;i++){ const k = i*3;
          if(i >= act){ P[k+1] = -1e5; continue; }
          let x = P[k], yy = P[k+1], z = P[k+2];
          if(yy < cy - 6 || Math.abs(x - cx) > 22 || Math.abs(z - cz) > 22){ x = cx + (Math.random()-0.5)*44; z = cz + (Math.random()-0.5)*44; yy = cy + 2 + Math.random()*12; }
          const ph = snow.ph[i]; yy -= (0.8 + (ph % 1)*0.7)*dt; x += (Math.sin(t*0.8 + ph)*0.35 + 0.15)*dt; z += Math.cos(t*0.6 + ph*1.3)*0.3*dt;
          P[k] = x; P[k+1] = yy; P[k+2] = z; }
        snow.m.geometry.attributes.position.needsUpdate = true; } }
  };
  // 흐린 하늘: 비·눈이 올 때 (updateSky 끝에서)
  const gZ = new THREE.Color(0x7c8590), gH = new THREE.Color(0xa7aeb5), gS = new THREE.Color(0xb6babe), gF = new THREE.Color(0x9ba3ab), gC = new THREE.Color(0x8e959d), gN = new THREE.Color(0x1a1e26);
  W.sky = () => { const c = W.cw; if(c < 0.001) return; const u = sky.material.uniforms;
    u.gZen.value.lerp(gZ, c*0.9); u.gUp.value.lerp(gZ, c*0.85); u.gMid.value.lerp(gH, c*0.85); u.gLow.value.lerp(gH, c*0.85); u.gHor.value.lerp(gH, c*0.85); u.gSun.value.lerp(gS, c*0.9);
    u.gAmt.value = Math.max(u.gAmt.value, c*0.92*SKY.day); u.gOver.value = c;
    scene.fog.color.lerp(_cl.copy(gN).lerp(gF, SKY.day), c*0.75);
    sun.intensity *= 1 - 0.62*c; hemi.intensity *= 1 - 0.08*c; renderer.toneMappingExposure *= 1 - 0.1*c;
    GLARE.material.opacity *= 1 - c;
    _cl.copy(gN).lerp(gC, SKY.day); for(const m of SKY_CLOUDS){ m.opacity = Math.min(1, m.opacity + c*0.45); m.color.lerp(_cl, c*0.7); }
    STARS.material.uniforms.op.value *= 1 - c; TWINKLE.material.uniforms.op.value *= 1 - c; MOON.mat.uniforms.op.value *= 1 - 0.9*c; MOON.glow.material.opacity *= 1 - c;
    for(const sh of SHAFTS) sh.m.material.opacity *= 1 - c; };
  window.__weather = () => { W.start(); W.amt = Math.max(W.amt, 0.6); };
  return W;
})();
'''

SEASON_POP_CSS = '''
#seasonPop{position:fixed;top:64px;right:12px;z-index:30;padding:12px 14px;border-radius:16px;max-width:280px}
#seasonPop p{margin:0 0 8px;font-size:12.5px;opacity:.8;line-height:1.45}
#seasonPop .seasonRow button{color:inherit;border-color:rgba(255,255,255,.35)}
#seasonPop .seasonRow button.on{background:#fff;color:#1d2230;border-color:#fff}
'''

LEAF_LOOP_START = "  const lp = leafPos;\n  for(let i=0;i<leafCount;i++){"
LEAF_LOOP_END = "  leavesInit = true; for(const m of leafMeshes) m.instanceMatrix.needsUpdate = true;\n"


def patch_weather(P, m):
    import re
    # 늘 떨어지던 낙엽 → 계절 날씨
    i = P.t.index(LEAF_LOOP_START); j = P.t.index(LEAF_LOOP_END, i) + len(LEAF_LOOP_END)
    P.t = P.t[:i] + "  WX.update(dt, st.started && !st.finished, y);\n" + P.t[j:]
    P.rep("let leavesInit = false;", "let leavesInit = false;" + WX_JS, 1)
    P.rep("for(const sh of SHAFTS){\n    sh.life -= dt;", "WX.sky();\n  for(const sh of SHAFTS){\n    sh.life -= dt;", 1)
    P.rep("const shaftK = sunAmt * forest * (SUN_DIR.y > 0.12 ? 1 : 0);", "const shaftK = sunAmt * forest * (SUN_DIR.y > 0.12 ? 1 : 0) * (1 - WX.cw);", 1)
    # 흐린 날 해 원반도 가려요
    P.rep("for(const k of ['gZen','gUp','gMid','gLow','gHor','gSun']) U[k] = { value:new THREE.Color() }; U.gAmt = { value:0 };",
          "for(const k of ['gZen','gUp','gMid','gLow','gHor','gSun']) U[k] = { value:new THREE.Color() }; U.gAmt = { value:0 }; U.gOver = { value:0 };", 1)
    P.rep("uniform float gAmt;", "uniform float gAmt, gOver;", 1)
    P.rep("gAmt*(1.0 - sundisk)); }", "gAmt*(1.0 - sundisk*(1.0 - gOver))); }", 1)
    P.rep("scene.fog.density = THREE.MathUtils.lerp(0.00031, 0.00013, THREE.MathUtils.clamp((y-300)/500,0,1));",
          "scene.fog.density = THREE.MathUtils.lerp(0.00031, 0.00013, THREE.MathUtils.clamp((y-300)/500,0,1)) * (1 + 2.4*WX.cw);", 1)
    # 빗소리
    P.rep("const brookF = filt('bandpass',750,0.55), brookG = gain(0.0); let brookT = 0;",
          "const rainG = gain(0.0); loop(whiteB, filt('highpass',700), filt('lowpass',5200), rainG).connect(master); window.__rainG = rainG;\n"
          "    const brookF = filt('bandpass',750,0.55), brookG = gain(0.0); let brookT = 0;", 1)
    # 게임 중 계절 바꾸기
    P.rep('<button class="ib" id="bOutfit"',
          '<button class="ib" id="bSeason" title="계절 바꾸기" aria-label="계절 바꾸기"><svg viewBox="0 0 24 24"><path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z"/><path d="M5 19c3-4 6-7 9.5-9.5"/></svg></button>\n    <button class="ib" id="bOutfit"', 1)
    P.rep('</style>', SEASON_POP_CSS + '</style>', 1)
    P.rep("const SEASONS_OK = ", "const SZ_RESUME = (()=>{ try{ const v = JSON.parse(sessionStorage.getItem('neungseon.szresume') || 'null'); sessionStorage.removeItem('neungseon.szresume'); return v && v.id === '%s' ? v : null; }catch(e){ return null; } })();\nconst SEASONS_OK = " % m['id'], 1)
    P.rep("|| (o.lastProg||0) < 25 ||", "|| ((o.lastProg||0) < 25 && !SZ_RESUME) ||", 1)
    names = dict(spring='봄', summer='여름', autumn='가을', winter='겨울')
    P.rep('<div id="flash"></div>', '<div id="seasonPop" class="glass" hidden><p>이 자리에서 계절을 바꿔요 · 산을 새로 그린 뒤 이어서 걸어요</p><div class="seasonRow" id="seasonRow2"></div></div>\n<div id="flash"></div>', 1)
    P.rep("$('loading').classList.add('out'); setTimeout(() => $('loading')?.remove(), 1700);",
          "$('loading').classList.add('out'); setTimeout(() => $('loading')?.remove(), 1700);\n"
          "{ // 계절 바꾸기 (게임 중)\n"
          "  const pop = $('seasonPop'), row = $('seasonRow2'), NM = " + repr(names).replace("'", '"') + ";\n"
          "  if(SEASONS_OK.length){ for(const s of SEASONS_OK){ const b = document.createElement('button'); b.type = 'button'; b.textContent = NM[s]; b.classList.toggle('on', s === SEASON);\n"
          "      b.onclick = () => { pop.hidden = true; if(s === SEASON) return; saveHike(); try{ localStorage.setItem('neungseon.season.%s', s); sessionStorage.setItem('neungseon.go', '%s'); sessionStorage.setItem('neungseon.szresume', JSON.stringify({ id:'%s', started: st.started && !st.finished, mode: SKY.mode })); }catch(e){} location.reload(); }; row.appendChild(b); } }\n"
          "  $('bSeason').onclick = (e) => { e.stopPropagation(); if(!SEASONS_OK.length){ toast('이 산은 일 년 내내 눈과 바위의 계절이에요', 3); return; } pop.hidden = !pop.hidden; };\n"
          "  addEventListener('pointerdown', e => { if(!pop.hidden && !pop.contains(e.target) && e.target.closest('#bSeason') == null) pop.hidden = true; });\n"
          "  if(SZ_RESUME){ if(SZ_RESUME.mode) SKY.mode = SZ_RESUME.mode; if(SZ_RESUME.started){ try{ window.MT_SELECT && window.MT_SELECT.close(); }catch(e){} beginHike(!!savedHike); setTimeout(() => toast('계절이 바뀌었어요 · 이어서 걸어요', 3), 3800); } }\n"
          "}" % (m['id'], m['id'], m['id']), 1)
