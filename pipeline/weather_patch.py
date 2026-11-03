"""계절 날씨 + 게임 중 계절 바꾸기 (2026-11-03)

- 예전: 사계절 내내 낙엽이 쉬지 않고 떨어졌어요.
- 이제: 봄 꽃잎 · 여름 소나기 · 가을 낙엽 · 겨울 눈이 산행 중 가끔, 무작위로 찾아와요.
  첫 번째는 1~2분 뒤, 그다음은 2~5분 간격, 한 번에 45~100초. 20분 산행이면 서너 번쯤.
  소나기·눈이 올 때는 하늘이 회색으로 흐려지고, 햇빛·별빛이 약해지고, 안개가 짙어져요. 비는 빗소리도.
- 오른쪽 위 도구에 '계절' 버튼: 봄·여름·가을·겨울을 바로 고르면, 지금 자리를 저장하고 산을 새로 그린 뒤 그 자리에서 이어 걸어요.
"""

WX_ROWS = [
    ['천둥 번개를 동반한 소나기예요 ⛈', 'A thundery shower is rolling in ⛈', '雷を伴うにわか雨です ⛈', '雷阵雨来了 ⛈'],
    ['별똥별이 연달아 떨어져요 ☄️ 하늘을 올려다보세요', 'Shooting stars, one after another ☄️ Look up!', '流れ星が次々と ☄️ 空を見上げて', '流星接连划过 ☄️ 抬头看看吧'],
    ['밤하늘에 오로라가 일렁여요 · 아주 드문 밤이에요', 'An aurora shimmers in the night sky · a very rare night', '夜空にオーロラが揺らめいています · とても珍しい夜です', '夜空中极光摇曳 · 非常难得的夜晚'],
    ['돌풍이 휘몰아쳐요 💨', 'A gust of wind sweeps through 💨', '突風が吹き抜けます 💨', '一阵狂风呼啸而过 💨'],
    ['천둥 번개를 멈췄어요', 'Thunder and lightning stopped', '雷を止めました', '已停止雷电'],
    ['멈췄어요', 'Stopped', '止めました', '已停止'],
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
// ---------- 날씨·하늘 효과: 꽃비·낙엽·소나기·눈·돌풍·천둥번개 + 밤의 별똥별·오로라 (pipeline/weather_patch.py) ----------
const WX = (()=>{
  let S = 'autumn'; try{ S = SEASON; }catch(e){}
  const MAIN = ({spring:'petal', summer:'rain', autumn:'leaf', winter:'snow', fixed:'snow'})[S] || 'leaf';
  const MSG = { petal:'봄바람에 꽃잎이 흩날려요 🌸', rain:'소나기가 지나가요 · 하늘이 잠시 흐려져요 🌧', leaf:'바람에 낙엽이 흩날려요 🍂', snow:'눈발이 날리기 시작해요 ❄' };
  const END = { rain:'비가 그쳤어요 · 하늘이 다시 개요', snow:'눈이 그쳤어요' };
  const KINDS = ['petal', 'leaf', 'rain', 'snow'];
  const E = {}; for(const k of KINDS) E[k] = { amt:0, target:0, left:0, admin:false, quiet:false };
  const W = { E, MAIN, cw:0, count:0, next:55 + Math.random()*70, gNext:70 + Math.random()*90, nNext:150 + Math.random()*150, storm:false, lNext:4, flashT:99, flashN:1, flash:0, g:{ amt:0, left:0, str:0 } };
  // 잎 ↔ 꽃잎: 같은 입자를 그림만 바꿔 써요
  const leafMaps = leafMeshes.map(m => m.material.map), leafCols = leafMeshes.map(m => m.instanceColor ? m.instanceColor.array.slice() : null), sc0 = leafVel.map(v => v.sc);
  const petalTex = (()=>{ const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'); x.translate(64,64);
    const gr = x.createRadialGradient(0,10,4,0,0,56); gr.addColorStop(0,'#fff'); gr.addColorStop(1,'#f4f0f2'); x.fillStyle = gr;
    x.beginPath(); x.moveTo(0,52); x.bezierCurveTo(44,30,40,-34,12,-50); x.quadraticCurveTo(0,-38,-12,-50); x.bezierCurveTo(-40,-34,-44,30,0,52); x.fill();
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
  const PC = [0xf6c6d4, 0xf9dbe4, 0xf1b3c6, 0xfde9ef, 0xf5c0cf].map(h => new THREE.Color(h));
  let leafMode = 'leaf';
  const setLeafMode = k => { if(leafMode === k) return; leafMode = k;
    leafMeshes.forEach((m, i) => { m.material.map = k === 'petal' ? petalTex : leafMaps[i]; m.material.needsUpdate = true;
      if(m.instanceColor){ if(k === 'petal') for(let j=0;j<m.count;j++) m.setColorAt(j, PC[(j+i*2)%PC.length]); else if(leafCols[i]) m.instanceColor.array.set(leafCols[i]); m.instanceColor.needsUpdate = true; } });
    leafVel.forEach((v, i) => { v.sc = sc0[i] * (k === 'petal' ? 0.55 : 1); }); };
  // 비: 비스듬히 떨어지는 빗줄기
  const rain = (()=>{ const N = 1500, pos = new Float32Array(N*6), sp = new Float32Array(N);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const m = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color:0xc4ceda, transparent:true, opacity:0, depthWrite:false }));
    m.frustumCulled = false; m.visible = false; scene.add(m); for(let i=0;i<N;i++){ sp[i] = 15 + Math.random()*7; pos[i*6+1] = -1e5; } return { m, pos, sp, N }; })();
  // 눈: 천천히 흔들리며 내려오는 눈송이
  const snow = (()=>{ const N = 1700, pos = new Float32Array(N*3), ph = new Float32Array(N);
    const c = document.createElement('canvas'); c.width = c.height = 32; const x = c.getContext('2d'); const gr = x.createRadialGradient(16,16,0,16,16,16);
    gr.addColorStop(0,'rgba(255,255,255,1)'); gr.addColorStop(0.45,'rgba(255,255,255,.75)'); gr.addColorStop(1,'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(0,0,32,32);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const m = new THREE.Points(g, new THREE.PointsMaterial({ size:0.13, map:new THREE.CanvasTexture(c), transparent:true, opacity:0, depthWrite:false, color:0xffffff }));
    m.frustumCulled = false; m.visible = false; scene.add(m); for(let i=0;i<N;i++){ ph[i] = Math.random()*100; pos[i*3+1] = -1e5; } return { m, pos, ph, N }; })();
  // 번개 줄기: 먼 하늘에 지그재그
  const bolt = (()=>{ const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(60*3), 3));
    const m = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color:0xf2f4ff, transparent:true, opacity:0, depthWrite:false, fog:false }));
    m.frustumCulled = false; m.visible = false; scene.add(m); return m; })();
  const makeBolt = () => { const P = bolt.geometry.attributes.position.array, a = Math.random()*6.28, d = 500 + Math.random()*500;
    let x = camera.position.x + Math.sin(a)*d, z = camera.position.z + Math.cos(a)*d, y = camera.position.y + 260 + Math.random()*80; const y0 = camera.position.y - 40; let n = 0;
    const seg = (x1,y1,z1,x2,y2,z2) => { if(n >= 60) return; P.set([x1,y1,z1,x2,y2,z2], n*3); n += 2; };
    while(y > y0 && n < 44){ const nx = x + (Math.random()-0.5)*40, ny = y - 18 - Math.random()*22, nz = z + (Math.random()-0.5)*40; seg(x,y,z,nx,ny,nz);
      if(Math.random() < 0.2){ seg(nx,ny,nz, nx + (Math.random()-0.5)*60, ny - 30, nz + (Math.random()-0.5)*60); } x = nx; y = ny; z = nz; }
    for(let i = n; i < 60; i++) P.set([x,y,z], i*3); bolt.geometry.attributes.position.needsUpdate = true; };
  const sfxOk = () => typeof sfx !== 'undefined' && sfx;
  W.start = (k, o = {}) => { const e = E[k]; if(!e) return;
    if(k === 'petal' || k === 'leaf'){ const other = E[k === 'petal' ? 'leaf' : 'petal']; other.target = 0; other.left = 0; other.amt = 0; setLeafMode(k); }
    e.target = o.amt || 1; e.left = o.dur || 45 + Math.random()*55; e.admin = !!o.admin; e.quiet = !!o.quiet; W.count++;
    if(k === 'rain' && o.storm){ W.storm = true; W.lNext = o.admin ? 2 : 6 + Math.random()*8; }
    if(!o.quiet) toast(k === 'rain' && o.storm ? '천둥 번개를 동반한 소나기예요 ⛈' : MSG[k], 4); };
  W.stop = k => { const e = E[k]; if(!e) return; e.target = 0; e.left = 0; e.admin = false; if(k === 'rain') W.storm = false; };
  W.gust = (len, str = 1) => { W.g.left = len; W.g.str = str; const s = sfxOk(); if(s && s.gust) s.gust(len + 1, 0.9 + str*0.5); };
  window.__wxGust = (len, str) => { W.g.left = Math.max(W.g.left, len); W.g.str = Math.max(W.g.left > 0 ? W.g.str : 0, str); };
  const strike = () => { W.flashT = 0; W.flashN = Math.random() < 0.55 ? 2 : 1; makeBolt(); const dist = Math.random(), s = sfxOk(); if(s && s.thunder) s.thunder(0.4 + dist*3.2, 1 - dist*0.55); };
  const active = k => E[k].target > 0;
  W.update = (dt, started, y) => {
    // 자연스럽게 찾아오는 날씨 (산행 중에만)
    if(started){
      if(!KINDS.some(active)){ W.next -= dt; if(W.next <= 0){ W.next = 120 + Math.random()*180; W.start(MAIN, { storm: MAIN === 'rain' && Math.random() < 0.45 }); } }
      W.gNext -= dt; if(W.gNext <= 0){ W.gNext = 70 + Math.random()*110; const len = 4 + Math.random()*3; W.gust(len, 0.6 + Math.random()*0.4);
        if((MAIN === 'leaf' || MAIN === 'petal') && !active('leaf') && !active('petal')) W.start(MAIN, { dur:len + 5, amt:0.45, quiet:true }); }
      if(SKY.night > 0.7){ W.nNext -= dt; if(W.nNext <= 0){ W.nNext = 240 + Math.random()*240;
        if(W.cw < 0.2 && !(SKY.shower > 0) && !(SKY.aurOn > 0)){ const r = Math.random(), AUR = __AUR__;
          if(r < 0.55){ SKY.shower = 14 + Math.random()*10; METEOR.force = 2; toast('별똥별이 연달아 떨어져요 ☄️ 하늘을 올려다보세요', 4); }
          else if(r < 0.55 + AUR){ SKY.aurOn = 100 + Math.random()*80; toast('밤하늘에 오로라가 일렁여요 · 아주 드문 밤이에요', 4.5); } } } }
    }
    for(const k of KINDS){ const e = E[k];
      if(e.target > 0){ e.left -= dt; if(e.left <= 0){ e.target = 0; e.admin = false; if(k === 'rain') W.storm = false; if(END[k] && !e.quiet) setTimeout(() => toast(END[k], 3), 5000); } }
      e.amt += (e.target - e.amt)*Math.min(1, dt*(e.target > e.amt ? 0.3 : 0.18)); if(e.amt < 0.002 && !e.target) e.amt = 0; }
    const g = W.g; g.left = Math.max(0, g.left - dt); g.amt += ((g.left > 0 ? g.str : 0) - g.amt)*Math.min(1, dt*(g.left > 0 ? 1.6 : 0.7));
    const ss = THREE.MathUtils.smoothstep;
    W.cw = Math.max((W.storm ? 1 : 0.92)*ss(E.rain.amt, 0, 0.8), 0.72*ss(E.snow.amt, 0, 0.8)); window.__WXcw = W.cw;
    // 천둥·번개
    if(W.storm && E.rain.amt > 0.45){ W.lNext -= dt; if(W.lNext <= 0){ W.lNext = 7 + Math.random()*15; strike(); } }
    W.flashT += dt; { const t = W.flashT; W.flash = t > 1 ? 0 : Math.exp(-t*16) + (W.flashN > 1 && t > 0.17 ? 0.85*Math.exp(-(t-0.17)*13) : 0); }
    bolt.visible = W.flash > 0.03; bolt.material.opacity = Math.min(1, W.flash*1.4);
    const cx = camera.position.x, cy = camera.position.y, cz = camera.position.z, wind = g.amt;
    // 잎·꽃잎
    const la = Math.max(E.leaf.amt, E.petal.amt), n = Math.round(leafCount*la);
    for(const m of leafMeshes) m.visible = n > 0;
    if(n > 0){ const lp = leafPos;
      for(let i=0;i<leafCount;i++){
        if(i >= n){ leafMeshes[i%LEAF_KINDS].setMatrixAt((i/LEAF_KINDS)|0, zero); continue; }
        const v = leafVel[i];
        if(!leavesInit || Math.abs(lp[i*3]-st.x)>25 || Math.abs(lp[i*3+2]-st.z)>25 || lp[i*3+1] < heightAt(lp[i*3],lp[i*3+2])){
          lp[i*3]=st.x+(rnd()-0.5)*50 - wind*12; lp[i*3+2]=st.z+(rnd()-0.5)*50; lp[i*3+1]=heightAt(lp[i*3],lp[i*3+2])+4+rnd()*14; }
        const sw = leafMode === 'petal' ? 0.6 : 1;
        v.ph += dt*(2 + wind*3); lp[i*3] += (Math.sin(v.ph)*0.6 + 0.4 + wind*5.5)*dt; lp[i*3+2] += (Math.cos(v.ph*0.7)*0.4 + wind*1.2)*dt; lp[i*3+1] -= v.sp*sw*(0.75+0.35*Math.sin(v.ph*1.3))*(1 - wind*0.45)*dt;
        leafObj.position.set(lp[i*3],lp[i*3+1],lp[i*3+2]); leafObj.rotation.set(v.rx+v.ph*v.spin*0.5, v.ry+v.ph*0.3, Math.sin(v.ph)*0.9); leafObj.scale.setScalar(v.sc); leafObj.updateMatrix();
        leafMeshes[i%LEAF_KINDS].setMatrixAt((i/LEAF_KINDS)|0, leafObj.matrix); }
      leavesInit = true; for(const m of leafMeshes) m.instanceMatrix.needsUpdate = true; }
    { const a = E.rain.amt, on = a > 0.01; rain.m.visible = on; rain.m.material.opacity = 0.42*a;
      if(window.__rainG) window.__rainG.gain.value = 0.2*a*(1 + wind*0.4);
      if(on){ const P = rain.pos, act = Math.round(rain.N*a), sl = 0.12 + wind*0.55;
        for(let i=0;i<rain.N;i++){ const k = i*6;
          if(i >= act){ P[k+1] = P[k+4] = -1e5; continue; }
          let x = P[k], yy = P[k+1], z = P[k+2];
          if(yy < cy - 7 || Math.abs(x - cx) > 20 || Math.abs(z - cz) > 20){ x = cx + (Math.random()-0.5)*40 - sl*8; z = cz + (Math.random()-0.5)*40; yy = cy + 4 + Math.random()*12; }
          const d = rain.sp[i]*dt; yy -= d; x += d*sl;
          P[k] = x; P[k+1] = yy; P[k+2] = z; P[k+3] = x - 0.62*sl; P[k+4] = yy + 0.75; P[k+5] = z; }
        rain.m.geometry.attributes.position.needsUpdate = true; } }
    { const a = E.snow.amt, on = a > 0.01; snow.m.visible = on; snow.m.material.opacity = 0.95*a;
      if(on){ const P = snow.pos, act = Math.round(snow.N*a), t = performance.now()/1000;
        for(let i=0;i<snow.N;i++){ const k = i*3;
          if(i >= act){ P[k+1] = -1e5; continue; }
          let x = P[k], yy = P[k+1], z = P[k+2];
          if(yy < cy - 6 || Math.abs(x - cx) > 22 || Math.abs(z - cz) > 22){ x = cx + (Math.random()-0.5)*44 - wind*10; z = cz + (Math.random()-0.5)*44; yy = cy + 2 + Math.random()*12; }
          const ph = snow.ph[i]; yy -= (0.8 + (ph % 1)*0.7)*dt; x += (Math.sin(t*0.8 + ph)*0.35 + 0.15 + wind*4)*dt; z += (Math.cos(t*0.6 + ph*1.3)*0.3 + wind*0.8)*dt;
          P[k] = x; P[k+1] = yy; P[k+2] = z; }
        snow.m.geometry.attributes.position.needsUpdate = true; } }
  };
  const zero = new THREE.Matrix4().makeScale(0,0,0);
  // 흐린 하늘(비·눈) + 번개 번쩍 (updateSky 끝에서)
  const gZ = new THREE.Color(0x7c8590), gH = new THREE.Color(0xa7aeb5), gS = new THREE.Color(0xb6babe), gF = new THREE.Color(0x9ba3ab), gC = new THREE.Color(0x8e959d), gN = new THREE.Color(0x1a1e26), gL = new THREE.Color(0xdfe3f5);
  W.sky = () => { const c = W.cw, u = sky.material.uniforms;
    if(c >= 0.001){
      u.gZen.value.lerp(gZ, c*0.9); u.gUp.value.lerp(gZ, c*0.85); u.gMid.value.lerp(gH, c*0.85); u.gLow.value.lerp(gH, c*0.85); u.gHor.value.lerp(gH, c*0.85); u.gSun.value.lerp(gS, c*0.9);
      u.gAmt.value = Math.max(u.gAmt.value, c*0.92*SKY.day); u.gOver.value = c;
      scene.fog.color.lerp(_cl.copy(gN).lerp(gF, SKY.day), c*0.75);
      sun.intensity *= 1 - 0.62*c; hemi.intensity *= 1 - 0.08*c; renderer.toneMappingExposure *= 1 - 0.1*c;
      GLARE.material.opacity *= 1 - c;
      _cl.copy(gN).lerp(gC, SKY.day); for(const m of SKY_CLOUDS){ m.opacity = Math.min(1, m.opacity + c*0.45); m.color.lerp(_cl, c*0.7); }
      STARS.material.uniforms.op.value *= 1 - c; TWINKLE.material.uniforms.op.value *= 1 - c; MOON.mat.uniforms.op.value *= 1 - 0.9*c; MOON.glow.material.opacity *= 1 - c;
      for(const sh of SHAFTS) sh.m.material.opacity *= 1 - c; }
    const f = W.flash; if(f > 0.01){ for(const k of ['gZen','gUp','gMid','gLow','gHor']) u[k].value.lerp(gL, f*0.8); u.gAmt.value = Math.max(u.gAmt.value, f*0.9);
      hemi.intensity += f*1.4; renderer.toneMappingExposure *= 1 + f*0.7; scene.fog.color.lerp(gL, f*0.5); for(const m of SKY_CLOUDS) m.color.lerp(gL, f*0.6); } };
  // 관리자: 효과를 바로 일으키거나 멈추기
  const ADK = { wxPetal:'petal', wxLeaf:'leaf', wxRain:'rain', wxSnow:'snow' };
  W.admin = a => {
    if(ADK[a]){ const k = ADK[a]; if(E[k].target > 0){ W.stop(k); toast('멈췄어요', 1.5); } else W.start(k, { dur:90, admin:true }); return; }
    if(a === 'wxGust'){ W.gust(6, 1.15); if(!active('leaf') && !active('petal') && !active('snow') && !active('rain')) W.start(MAIN === 'petal' ? 'petal' : 'leaf', { dur:11, amt:0.6, quiet:true }); toast('돌풍이 휘몰아쳐요 💨', 2.5); return; }
    if(a === 'wxStorm'){ if(W.storm){ W.stop('rain'); toast('천둥 번개를 멈췄어요', 1.5); } else W.start('rain', { dur:90, admin:true, storm:true }); return; }
  };
  W.adminOn = () => ({ wxPetal: active('petal'), wxLeaf: active('leaf'), wxRain: active('rain') && !W.storm, wxSnow: active('snow'), wxGust: W.g.left > 0, wxStorm: W.storm });
  W.stopAll = () => { for(const k of KINDS) W.stop(k); W.g.left = 0; };
  // 모두에게: 끝나는 시각(ms)으로 주고받아요
  W.evOut = now => { const o = {}; for(const k of KINDS) o[k] = E[k].target > 0 && E[k].admin ? Math.round(now + E[k].left*1000) : 0; o.storm = W.storm && E.rain.admin ? o.rain : 0; o.gust = W.g.left > 0 ? Math.round(now + W.g.left*1000) : 0; return o; };
  W.evIn = (wx, now) => { if(!wx || typeof wx !== 'object') return;
    for(const k of KINDS){ const left = (num(wx[k]) - now)/1000; if(left > 1){ if(!(E[k].target > 0 && E[k].admin)) W.start(k, { dur:left, admin:true, storm: k === 'rain' && num(wx.storm) > now }); else E[k].left = left; } else if(E[k].admin && E[k].target > 0) W.stop(k); }
    const gl = (num(wx.gust) - now)/1000; if(gl > 0.5 && !(W.g.left > 0)) W.gust(gl, 1.15); };
  window.__weather = (k) => { W.start(k || MAIN); E[k || MAIN].amt = Math.max(E[k || MAIN].amt, 0.6); };
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
    aur = '0.35' if m['id'] in ('torresdelpaine', 'tongariro') else '0.15'
    P.rep("let leavesInit = false;", "let leavesInit = false;" + WX_JS.replace('__AUR__', aur), 1)
    # 구름 낀 밤에는 별똥별이 저절로 떨어지지 않아요
    P.rep("if(night > 0.6 || MT.force > 0 || showering){ MT.next -= dt;", "if((night > 0.6 && (window.__WXcw||0) < 0.35) || MT.force > 0 || showering){ MT.next -= dt;", 1)
    # 관리자: 날씨 효과 버튼
    P.rep('<button data-ad="fxOff">효과 모두 끄기</button></div>',
          '<button data-ad="fxOff">효과 모두 끄기</button></div>\n'
          '  <div class="adSec">날씨 효과 <small>· 다시 누르면 멈춰요</small></div>\n'
          '  <div class="adRow"><button data-ad="wxPetal" data-tg>🌸 꽃비</button><button data-ad="wxLeaf" data-tg>🍂 낙엽</button><button data-ad="wxRain" data-tg>🌧 소나기</button><button data-ad="wxSnow" data-tg>❄ 눈</button><button data-ad="wxGust" data-tg>💨 돌풍</button><button data-ad="wxStorm" data-tg>⛈ 천둥·번개</button></div>', 1)
    P.rep("    case 'bots': adminBots(); break;", "    case 'wxPetal': case 'wxLeaf': case 'wxRain': case 'wxSnow': case 'wxGust': case 'wxStorm': WX.admin(a); break;\n    case 'bots': adminBots(); break;", 1)
    P.rep("if(['shower','aurora','moon','fxOff','notice'].includes(a)) sendGlobal();", "if(['shower','aurora','moon','fxOff','notice','wxPetal','wxLeaf','wxRain','wxSnow','wxGust','wxStorm'].includes(a)) sendGlobal();", 1)
    P.rep("case 'fxOff': SKY.outMsg = null;", "case 'fxOff': WX.stopAll(); SKY.outMsg = null;", 1)
    P.rep("bots: ADMIN_BOTS.length > 0, turbo: ADMIN_TURBO };", "bots: ADMIN_BOTS.length > 0, turbo: ADMIN_TURBO, ...WX.adminOn() };", 1)
    P.rep("msg: SKY.outMsg || null, t: Math.round(now) };", "msg: SKY.outMsg || null, wx: WX.evOut(now), t: Math.round(now) };", 1)
    P.rep("  SKY.shower = sh; METEOR.force = sh > 0 ? 3 : 0;", "  WX.evIn(ev.wx, now);\n  SKY.shower = sh; METEOR.force = sh > 0 ? 3 : 0;", 1)
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
