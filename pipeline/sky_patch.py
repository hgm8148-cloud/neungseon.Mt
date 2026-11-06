"""하늘: 승연 님 하늘 사진으로 맞춘 일출·오전·오후·일몰·심야 5단계 + 사진 밤하늘 (2026-11-03)

- 낮 하늘: 물리 산란(Sky 셰이더) 위에 사진에서 뽑은 천정→지평선 색 띠를 밝기는 그대로 두고 색만 입혀요.
  일출 konevi·21028723(겨울 아침), 오전 mustafa·beholz, 오후 bartroman·hias, 일몰 alberto·leolo·tom.
  계절(봄 황사빛·여름 습한 연무·가을 깊은 파랑·겨울 파스텔)과 기후(고산일수록 짙은 파랑)를 더해요.
- 밤하늘: lanius 님 은하수 사진으로 만든 온하늘 별지도(make_sky.py), 지평선 쪽 별빛 붉어짐·흐려짐,
  초록빛 대기광 띠, 해 진 쪽 박명(bru-no-heaven 사진의 주황→라일락→남색), 산마다 다른 도시 불빛.
  어두운 오지 산(에베레스트·킬리만자로·파타고니아 등)일수록 별이 더 많이 보여요. 밝은 달이 뜨면 별이 옅어져요.
- 달: Pexels 보름달 사진.
- 시간 버튼: 실시간 → 일출 → 오전 → 오후 → 일몰 → 심야 (관리자 줄도 같이).
"""
import json

SKY_ROWS = [
    ['일출', 'Sunrise', '日の出', '日出'], ['오전', 'Morning', '午前', '上午'], ['오후', 'Afternoon', '午後', '下午'],
    ['일몰', 'Sunset', '日の入り', '日落'], ['심야', 'Late night', '深夜', '深夜'], ['실시간', 'Live', 'リアルタイム', '实时'],
    ['🕐 일출', '🕐 Sunrise', '🕐 日の出', '🕐 日出'], ['🕐 오전', '🕐 Morning', '🕐 午前', '🕐 上午'], ['🕐 오후', '🕐 Afternoon', '🕐 午後', '🕐 下午'],
    ['🕐 일몰', '🕐 Sunset', '🕐 日の入り', '🕐 日落'], ['🕐 심야', '🕐 Late night', '🕐 深夜', '🕐 深夜'],
]

# 사진에서 뽑은 색 (zen, up, mid, low, hor, sun쪽 지평선) — sRGB
PAL = {
    'sunrise':   ['#3c5a96', '#7f9cc8', '#cbb9c6', '#f1d0aa', '#ffd9a0', '#ffb466'],
    'morning':   ['#2f6cc4', '#4f86d6', '#79a3e2', '#a5c2e8', '#cfdde8', '#fff3dc'],
    'afternoon': ['#0b58a0', '#1c6aaa', '#2f80bb', '#5d9bc6', '#b0c7d2', '#fff0d2'],
    'sunset':    ['#2a4886', '#5f6b9e', '#b68c9c', '#f2a86c', '#ffbe6a', '#ff8a40'],
}
SEASON_TINT = {   # 지평선 쪽(low·hor)과 천정 쪽(zen·up)에 섞는 색과 양, 탁도 더하기
    'spring': dict(low='#e2d8c2', lowK=0.22, turb=1.6),
    'summer': dict(low='#d4d9da', lowK=0.3, zen='#2a73b8', zenK=0.15, turb=2.6),
    'autumn': dict(zen='#0a4fa6', zenK=0.3, turb=-1.2),
    'winter': dict(low='#f2e6e6', lowK=0.28, zen='#4a7cc0', zenK=0.15, turb=-1.6),
}
ALPINE = {'alps': 1, 'fixed': 1, 'patagonia': 0.8, 'sierra': 0.7, 'nz': 0.6, 'kr-high': 0.35, 'jp': 0.4}
# 도시 불빛: 게임 좌표 방향 (x=동, z=남) · 색 세기
CITY = {
    'bukhansan': ([0.18, 1.0], 1.0), 'hallasan': ([0.0, -1.0], 0.6), 'fuji': ([1.0, -0.35], 0.7), 'montblanc': ([0.0, -1.0], 0.45),
    'mudeungsan': ([-0.7, -0.7], 0.8), 'naejangsan': ([-0.2, -1.0], 0.45), 'wolchulsan': ([-1.0, 0.1], 0.45),
}
DARK = {'everest': 1.45, 'kilimanjaro': 1.4, 'torresdelpaine': 1.45, 'tongariro': 1.35, 'halfdome': 1.25, 'trecime': 1.25, 'matterhorn': 1.3}

GRADE_GLSL = r'''
	{ float ge = max(direction.y, 0.0);
	  vec3 T = mix(gHor, gLow, smoothstep(0.0, 0.07, ge)); T = mix(T, gMid, smoothstep(0.05, 0.22, ge)); T = mix(T, gUp, smoothstep(0.18, 0.5, ge)); T = mix(T, gZen, smoothstep(0.45, 0.95, ge));
	  float sk = pow(max(dot(normalize(direction.xz + 1e-5), normalize(vSunDirection.xz + 1e-5)), 0.0), 3.0)*(1.0 - smoothstep(0.0, 0.35, ge));
	  T = mix(T, gSun, sk*0.75);
	  float lr = dot(retColor, vec3(0.2126, 0.7152, 0.0722)), lt = dot(T, vec3(0.2126, 0.7152, 0.0722));
	  retColor = mix(retColor, T*(lr/max(lt, 1e-4)), gAmt*(1.0 - sundisk)); }
	gl_FragColor = vec4( retColor, 1.0 );'''

SKY_JS = r'''
// ---------- 사진 색 하늘 (pipeline/sky_patch.py) ----------
const SKYX = __SKYX__;
const SKYG = (()=>{
  const C = h => new THREE.Color(h), P = {}; for(const k in SKYX.pal) P[k] = SKYX.pal[k].map(C);
  let seasonDone = false, turb = 0;
  function season(){ if(seasonDone) return; seasonDone = true; let S = null; try{ S = SKYX.tint[SEASON]; }catch(e){}
    const alp = SKYX.alpine, deep = C('#0a3f8f');
    for(const k in P){ const p = P[k];
      if(alp){ p[0].lerp(deep, 0.35*alp); p[1].lerp(deep, 0.2*alp); if(k === 'morning' || k === 'afternoon') p[4].lerp(C('#c4d6e6'), 0.3*alp); }
      if(S){ if(S.low){ p[3].lerp(C(S.low), S.lowK*0.6); p[4].lerp(C(S.low), S.lowK); } if(S.zen && (k === 'morning' || k === 'afternoon')){ p[0].lerp(C(S.zen), S.zenK); p[1].lerp(C(S.zen), S.zenK*0.7); } } }
    turb = (S ? S.turb : 0) - 2.2*alp; }
  const out = [0,1,2,3,4,5].map(() => new THREE.Color()), tmp = new THREE.Color(), cloudR = C('#ffc89a'), cloudS = C('#ff9e6e'), sunR = C('#ffb870'), sunS = C('#ff9850');
  const fog = new THREE.Color();
  return { out, fog, get turb(){ return turb; }, amt:0,
    update(s, dir){ season(); const ss = THREE.MathUtils.smoothstep;
      const m = ss(dir.x, -0.15, 0.15), gw = 1 - ss(s, 0.06, 0.32);   // m: 오전 쪽, gw: 해가 낮을수록 일출·일몰 색
      for(let i=0;i<6;i++){ tmp.copy(P.afternoon[i]).lerp(P.morning[i], m); out[i].copy(P.sunset[i]).lerp(P.sunrise[i], m).lerp(tmp, 1 - gw); }
      this.amt = (0.5 + 0.22*gw) * SKYX.amt * ss(s, -0.14, 0.0);
      const u = sky.material.uniforms; ['gZen','gUp','gMid','gLow','gHor','gSun'].forEach((k,i)=>u[k].value.copy(out[i])); u.gAmt.value = this.amt;
      fog.copy(out[4]).lerp(out[3], 0.35);
      SKYC.cloudG.copy(cloudS).lerp(cloudR, m); SKYC.sunG.copy(sunS).lerp(sunR, m); SKYC.fogG.copy(out[4]).lerp(out[5], 0.3); }
  };
})();
window.__setTime = (mode) => { SKY.override = null; SKY.mode = mode; SKY.h = targetHour(); };
window.__cam = (pitch, yaw) => { st.pitch = pitch; if(yaw != null) st.yaw = yaw; };
'''

STARS_FS_OLD = '''vec3 col = texture2D(map, uv).rgb; float l = dot(col, vec3(0.3,0.59,0.11)); col = max(mix(vec3(l), col, 1.55), 0.0);
        col = pow(col, vec3(2.3))*0.95; gl_FragColor = vec4(col*op*hz, 1.0); }'''
STARS_FS_NEW = '''vec3 col = texture2D(map, uv).rgb; col = col*col*(0.45 + 0.55*col)*1.7;          // 사진 은하수: 감마를 풀어 별빛만 또렷이
        float ext = smoothstep(-0.02, 0.4, d.y); col *= mix(vec3(1.0, 0.7, 0.48), vec3(1.0), ext);   // 지평선 쪽은 공기층에 붉어지고 흐려져요
        gl_FragColor = vec4(col*op*hz*(0.3 + 0.7*ext)*gain, 1.0); }'''

GLOW_OLD = '''vec3 col = vec3(0.010, 0.018, 0.046)*(1.0 - 0.4*e) + vec3(0.028, 0.042, 0.075)*exp(-e*7.0);
        float seoul = pow(max(dot(hz, normalize(vec2(0.18, 1.0))), 0.0), 2.0); col += vec3(0.12, 0.07, 0.036)*seoul*exp(-e*9.0);'''
GLOW_NEW = '''vec3 col = mix(vec3(0.024, 0.034, 0.062), vec3(0.005, 0.009, 0.024), pow(e, 0.5));   // 지평선 남회색 → 천정 짙은 남색 (manuel·bru-no 사진)
        col += vec3(0.016, 0.028, 0.018)*exp(-pow((e - 0.1)/0.06, 2.0));                          // 옅은 초록 대기광 띠 (은하수 사진들)
        float city = pow(max(dot(hz, normalize(cityDir)), 0.0), 2.0); col += cityCol*(city*exp(-e*10.0) + 0.06*exp(-e*16.0));'''
GLOW_TAIL_OLD = 'col *= night*smoothstep(-0.08, 0.02, d.y);'
GLOW_TAIL_NEW = '''col *= night*smoothstep(-0.08, 0.02, d.y);
        if(twi > 0.001){ float sa = max(dot(hz, normalize(sunDir.xz + vec2(1e-5))), 0.0), tk = twi*(0.3 + 0.7*sa*sa);   // 박명: 해 진 쪽 주황 → 라일락 → 남색
          col += tk*(vec3(0.62, 0.21, 0.07)*exp(-e*20.0) + vec3(0.2, 0.13, 0.2)*exp(-e*6.5) + vec3(0.04, 0.06, 0.11)*exp(-e*2.2))*smoothstep(-0.06, 0.02, d.y); }'''


def sky_x(m):
    mid, cl = m.get('base', m['id']), m.get('climate', 'kr')
    cdir, ck = CITY.get(mid, ([0, 1], 0.0)) if m.get('cityLights', True) else ([0, 1], 0.0)
    base = [0.12, 0.07, 0.036]
    return dict(pal=PAL, tint=SEASON_TINT, alpine=ALPINE.get(cl, 0), amt=1.0,
                city=dict(dir=cdir, col=[round(c * ck + 0.006, 4) for c in base]),
                star=DARK.get(mid, 0.8 if ck >= 0.9 else 1.0 if ck > 0 else 1.15))


def patch_sky(P, m):
    X = sky_x(m)
    # 사진 은하수·달 (페이지 옆 photos/sky/ 파일로)
    P.sub(r"const STARS_URL = '[^']*';", "const STARS_URL = 'photos/sky/milkyway.jpg';")
    P.sub(r"const MOON_URL = '[^']*';", "const MOON_URL = 'photos/sky/moon.jpg';")
    # Sky 셰이더에 사진 색 입히기
    P.rep("const sky = new Sky(); sky.scale.setScalar(25000);",
          "const sky = new Sky(); sky.scale.setScalar(25000);\n"
          "{ const U = sky.material.uniforms; for(const k of ['gZen','gUp','gMid','gLow','gHor','gSun']) U[k] = { value:new THREE.Color() }; U.gAmt = { value:0 };\n"
          "  sky.material.fragmentShader = sky.material.fragmentShader.replace('uniform vec3 up;', 'uniform vec3 up; uniform vec3 gZen, gUp, gMid, gLow, gHor, gSun; uniform float gAmt;')"
          ".replace('gl_FragColor = vec4( retColor, 1.0 );', " + json.dumps(GRADE_GLSL) + "); }", 1)
    P.rep("const _cl = new THREE.Color(); const RIDGES = [];", "const _cl = new THREE.Color(); const RIDGES = [];" + SKY_JS.replace('__SKYX__', json.dumps(X)), 1)
    # 5단계 시간
    P.rep("const TIME_PRESETS = { real:null, dawn:6.55, day:12.5, dusk:17.55, night:22.5 };",
          "const TIME_PRESETS = { real:null, dawn:6.55, morning:9.5, day:14.5, afternoon:14.5, dusk:17.55, night:23.5 };\n"
          "function deepNightHour(){ const doy = dayOfYear(); let best = 0, by = 9; for(let h = 0; h < 24; h += 0.1){ const y = sunAtHour(h, doy).y; if(y < by){ by = y; best = h; } } return (best - 1 + 24) % 24; }", 1)
    P.rep("if(SKY.mode === 'dusk') return hourAtSun(0.07, false);",
          "if(SKY.mode === 'dusk') return hourAtSun(0.07, false); if(SKY.mode === 'morning') return hourAtSun(0.5, true); if(SKY.mode === 'afternoon' || SKY.mode === 'day') return hourAtSun(0.55, false); if(SKY.mode === 'night') return deepNightHour();", 1)
    P.rep('<button data-ad="tDawn">해 뜰 녘</button><button data-ad="tDay">한낮</button><button data-ad="tDusk">해 질 녘</button><button data-ad="tNight">밤</button>',
          '<button data-ad="tDawn">일출</button><button data-ad="tMorning">오전</button><button data-ad="tDay">오후</button><button data-ad="tDusk">일몰</button><button data-ad="tNight">심야</button>', 1)
    P.rep("case 'tDay': SKY.override = null; SKY.mode = 'day'; SKY.h = targetHour(); break;",
          "case 'tMorning': SKY.override = null; SKY.mode = 'morning'; SKY.h = targetHour(); break;\n    case 'tDay': SKY.override = null; SKY.mode = 'afternoon'; SKY.h = targetHour(); break;", 1)
    P.rep("const order = ['real','dawn','day','dusk','night'], label = { real:'지금 시각 그대로', dawn:'해 뜰 무렵', day:'한낮', dusk:'해 질 녘', night:'별이 뜬 밤' };",
          "const order = ['real','dawn','morning','afternoon','dusk','night'], label = { real:'지금 시각 그대로', dawn:'일출', morning:'오전', afternoon:'오후', day:'오후', dusk:'일몰', night:'심야' };", 1)
    # updateSky: 사진 색·탁도·안개
    P.rep("SKY.day = day; SKY.night = night; SKY.gold = gold; SKY.sunAmt = sunAmt;",
          "SKY.day = day; SKY.night = night; SKY.gold = gold; SKY.sunAmt = sunAmt; SKYG.update(s, dir);", 1)
    P.rep("u.mieCoefficient.value = 0.005 + gold*0.004;",
          "u.mieCoefficient.value = 0.005 + gold*0.004; u.turbidity.value = Math.max(1.5, u.turbidity.value + SKYG.turb*(1 - gold*0.5));", 1)
    P.rep("scene.fog.color.copy(SKYC.fogN).lerp(SKYC.fogD, day).lerp(SKYC.fogG, gold*0.55);",
          "scene.fog.color.copy(SKYC.fogN).lerp(SKYC.fogD, day).lerp(SKYC.fogG, gold*0.55); scene.fog.color.lerp(SKYG.fog, 0.4*day*(1 - gold*0.6));", 1)
    # 사진 별지도 셰이더
    P.rep("uniforms:{ map:{value:null}, op:{value:0}, rot:{value:0} }", "uniforms:{ map:{value:null}, op:{value:0}, rot:{value:0}, gain:{value:1} }", 1)
    P.rep("uniform sampler2D map; uniform float op, rot; varying vec3 vD;", "uniform sampler2D map; uniform float op, rot, gain; varying vec3 vD;", 1)
    P.rep(STARS_FS_OLD, STARS_FS_NEW, 1)
    P.rep("STARS.material.uniforms.op.value = night;", f"STARS.material.uniforms.op.value = night; STARS.material.uniforms.gain.value = {X['star']}*(1 - 0.55*MOON.amt);", 1)
    P.rep("TWINKLE.material.uniforms.op.value = night;", f"TWINKLE.material.uniforms.op.value = night*{min(1.0, X['star']):.2f}*(1 - 0.6*MOON.amt);", 1)
    # 밤하늘 빛: 대기광·박명·산마다 다른 도시 불빛
    P.rep("uniforms:{ night:{value:0}, aur:{value:0}, time:{value:0}, moonDir:{value:new THREE.Vector3(0,1,0)}, moonAmt:{value:0} }",
          "uniforms:{ night:{value:0}, aur:{value:0}, time:{value:0}, moonDir:{value:new THREE.Vector3(0,1,0)}, moonAmt:{value:0}, twi:{value:0}, sunDir:{value:new THREE.Vector3(0,-1,0)}, "
          f"cityDir:{{value:new THREE.Vector2({X['city']['dir'][0]}, {X['city']['dir'][1]})}}, cityCol:{{value:new THREE.Vector3({', '.join(map(str, X['city']['col']))})}} }}", 1)
    P.rep("uniform float night, aur, time, moonAmt; uniform vec3 moonDir; varying vec3 vD;",
          "uniform float night, aur, time, moonAmt, twi; uniform vec3 moonDir, sunDir, cityCol; uniform vec2 cityDir; varying vec3 vD;", 1)
    P.rep(GLOW_OLD, GLOW_NEW, 1)
    P.rep(GLOW_TAIL_OLD, GLOW_TAIL_NEW, 1)
    P.rep("NIGHTGLOW.visible = night > 0.01; const NU = NIGHTGLOW.material.uniforms; NU.night.value = night;",
          "NIGHTGLOW.visible = night > 0.01; const NU = NIGHTGLOW.material.uniforms; NU.night.value = night; NU.sunDir.value.copy(dir); NU.twi.value = ss(-s, 0.035, 0.085)*(1 - ss(-s, 0.1, 0.31));", 1)
