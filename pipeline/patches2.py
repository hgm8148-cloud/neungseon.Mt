"""build_site.py 가 쓰는 추가 바꿔 끼우기 (2026-11-03 요청)
- 계절 문구 빼기, 오프닝 = 그 산의 실제 능선 실루엣, 산 이름 누르면 저장 + 산 고르기,
- 걸음마다 화면 떨림 줄이기, 산별 식생·바위·눈(biome)
"""
import base64, json, math
import numpy as np

EXTRA_ROWS = [
    *[], 
    ['산길을 한 걸음씩, 함께 오르다', 'One step at a time, up the trail together', '山道を一歩ずつ、いっしょに登る', '一步一步，一起走上山路'],
    ['지금까지 걸은 기록을 저장했어요', 'Your progress so far is saved', 'ここまでの記録を保存しました', '已保存目前的进度'],
    ['다른 산 고르기 (기록은 저장돼요)', 'Choose another mountain (progress is saved)', '別の山を選ぶ（記録は保存されます）', '选择其他山（进度会保存）'],
]

# ---------- 산별 식생·지형 (게임 높이 = 실제 해발 - BASE) ----------
PRESETS = {
    'autumn':  dict(pine=1, sp={}, dens=1, flat=0, leaf=1, grass=0, bare=0),
    'conifer': dict(pine=2.6, sp={'mapleRed': .45, 'mapleOrange': .5, 'yellow': .7, 'birch': 1.4}, dens=.95, flat=0, leaf=.6, grass=.05, bare=0),
    'highland': dict(pine=1.8, sp={'mapleRed': .5, 'oak': 1.2, 'bare': 2}, dens=.8, flat=0, leaf=.7, grass=.15, bare=0),
    'larch':   dict(pine=1.6, sp={'yellow': 3, 'oakGold': 2, 'mapleRed': .1, 'mapleOrange': .2, 'birch': 1.5}, dens=.75, flat=.2, leaf=.3, grass=.1, bare=.05),
    'sierra':  dict(pine=5, sp={'mapleRed': .05, 'mapleOrange': .1, 'oak': .3, 'yellow': .4}, dens=.55, flat=.35, leaf=.15, grass=0, bare=.1),
    'granite-pine': dict(pine=7, sp={'mapleRed': .4, 'mapleOrange': .4}, dens=.85, flat=.25, leaf=.4, grass=0, bare=0),
    'lenga':   dict(pine=.05, sp={'mapleRed': 1.8, 'oakGold': 2.2, 'yellow': 1.4, 'oak': .4}, dens=.8, flat=.15, leaf=.8, grass=.1, bare=0),
    'alpine':  dict(pine=0, sp={}, dens=0, flat=.9, leaf=0, grass=.25, bare=.22),
    'volcanic': dict(pine=0, sp={}, dens=0, flat=.95, leaf=0, grass=.1, bare=.3),
}


def bio_for(m, meta):
    b = m.get('biome') or {}
    if m.get('legacy') or not b:
        return dict(tt=775, r0=700, r1=790, pt=790, snow=1e9, **PRESETS['autumn'])
    base = meta['BASE']
    tl = b.get('treeline', 1e5); rk = b.get('rockline', tl - 75)
    o = dict(PRESETS[b.get('preset', 'autumn')])
    o.update(tt=round(tl - base), r0=round(rk - base), r1=round(rk - base + 90),
             pt=round(b.get('plantline', tl + 250) - base), snow=round(b['snow'] - base) if b.get('snow') else 1e9)
    for k in ('dens', 'pine', 'grass', 'bare', 'leaf', 'flat'):
        if k in b: o[k] = b[k]
    return o


def patch_biome(P, bio):
    P.rep('const D = JSON.parse(', 'const BIO = ' + json.dumps(bio) + ';\nconst D = JSON.parse(', 1)
    # 바닥 색·바위 섞기
    P.rep('if(h > 700) rock = Math.max(rock, THREE.MathUtils.smoothstep(700, 790, h) * THREE.MathUtils.smoothstep(0.97,0.85,ny));',
          'if(h > BIO.r0) rock = Math.max(rock, THREE.MathUtils.smoothstep(BIO.r0, BIO.r1, h) * Math.max(BIO.flat, THREE.MathUtils.smoothstep(0.97,0.85,ny)));', 1)
    P.rep('if(h > 700) rock = Math.max(rock, THREE.MathUtils.smoothstep(h, 700, 790));',
          'if(h > BIO.r0) rock = Math.max(rock, THREE.MathUtils.smoothstep(h, BIO.r0, BIO.r1));', 1)
    # 먼 산 색 (+ 눈)
    P.rep('if(h > 520) o.lerp(TOON_PAL[1], THREE.MathUtils.smoothstep(h,520,700)*0.4);',
          'if(h > BIO.r0-180) o.lerp(TOON_PAL[1], THREE.MathUtils.smoothstep(h,BIO.r0-180,BIO.r0)*0.4);', 1)
    P.rep('h>760 ? THREE.MathUtils.smoothstep(h,760,820) : 0);',
          'h>BIO.tt-15 ? THREE.MathUtils.smoothstep(h,BIO.tt-15,BIO.tt+45) : 0);', 1)
    P.rep('  if(rock > 0.35) o.copy(vnoise(x/120,z/120) > 0.5 ? TOON_ROCK : TOON_ROCK2);\n  return o;',
          '  if(rock > 0.35) o.copy(vnoise(x/120,z/120) > 0.5 ? TOON_ROCK : TOON_ROCK2);\n'
          '  if(h > BIO.snow - 120){ const s = THREE.MathUtils.smoothstep(h + (vnoise(x/300,z/300)-0.5)*160, BIO.snow-120, BIO.snow+80) * (0.55 + 0.45*THREE.MathUtils.smoothstep(ny, 0.55, 0.8)); if(s > 0) o.lerp(SNOW_C, Math.min(1, s)); }\n  return o;', 1)
    P.rep('function toonColor(x,z,h,ny,o){', 'const SNOW_C = new THREE.Color(0xeef2f7);\nfunction toonColor(x,z,h,ny,o){', 1)
    # 나무
    P.rep('if(rnd() < pPine) return \'pine\';', 'if(rnd() < pPine*BIO.pine) return \'pine\';', 1)
    P.rep('let tot=0; for(const k in w) tot+=w[k];', 'for(const k in w) w[k] *= (BIO.sp[k] ?? 1); let tot=0; for(const k in w) tot+=w[k];', 1)
    P.rep('if(sl > 0.8 || h > 775) continue;', 'if(sl > 0.8 || h > BIO.tt || rnd() > BIO.dens) continue;', 1)
    P.rep('if(h > 620 && rnd() < (h-620)/150) continue;', 'if(h > BIO.tt-155 && rnd() < (h-BIO.tt+155)/150) continue;', 1)
    P.rep('const shrink = 1 - Math.max(0,(h-520)/650);', 'const shrink = 1 - Math.max(0,(h-BIO.tt+255)/650);', 1)
    # 풀·덤불
    P.rep('const h = heightAt(x,z); if(slopeAt(x,z) > 0.85 || h > 790) continue;', 'const h = heightAt(x,z); if(slopeAt(x,z) > 0.85 || h > BIO.pt) continue;', 1)
    P.rep("let best='grass', bv=-9;", "zones.grass += BIO.grass; zones.reed += BIO.grass*0.8; if(BIO.dens < 0.05){ zones.bushRed -= 0.5; zones.bushOak -= 0.4; zones.fern -= 0.5; }\n    let best='grass', bv=-9;", 1)
    P.rep('if(bv < 0.62) continue;', 'if(bv < 0.62 + BIO.bare) continue;', 1)
    # 통나무·중경 숲·바위 노두·낙엽 더미
    P.rep('heightAt(x,z)>780) continue;', 'heightAt(x,z)>BIO.tt || rnd() > BIO.dens) continue;', 1)
    P.rep('if(h > 760 || sl > 1.0) continue;', 'if(h > BIO.tt-15 || sl > 1.0 || rnd() > BIO.dens) continue;', 1)
    P.rep('if(h > 640 && rnd() < (h-640)/140) continue;', 'if(h > BIO.tt-135 && rnd() < (h-BIO.tt+135)/140) continue;', 1)
    P.rep('THREE.MathUtils.smoothstep(h, 520, 700)) * (0.4', 'THREE.MathUtils.smoothstep(h, BIO.r0-180, BIO.r0)) * (0.4', 1)
    P.rep('const h = heightAt(x,z); if(h > 780 || slopeAt(x,z) > 0.7) continue;', 'const h = heightAt(x,z); if(h > BIO.tt || rnd() > BIO.leaf || slopeAt(x,z) > 0.7) continue;', 1)
    # 발소리
    P.rep("(hh > 700 || stairAt[nt.i] > 0) ? 'rock' : 'dirt'", "(hh > BIO.r0 || stairAt[nt.i] > 0) ? 'rock' : 'dirt'", 1)


# ---------- 걸음마다 화면 떨림 ----------
def patch_shake(P):
    if 'st.camY' in P.t: return            # 템플릿 v26부터 원본에 들어 있음
    P.rep('const yC = st.sitting ? hiker.position.y + 0.28 : y;',
          'const yRaw = st.sitting ? hiker.position.y + 0.28 : y;\n'
          '  if(st.camY == null || dt === 0 || Math.abs(yRaw - st.camY) > 3) st.camY = yRaw; else st.camY += (yRaw - st.camY) * Math.min(1, dt*5);   // 카메라 높이는 부드럽게 따라가요 (걸음마다 떨리지 않게)\n'
          '  const yC = st.camY;', 1)
    P.rep('const bob = Math.sin(st.phase*2)*(0.035+Math.max(0,grade)*0.06)', 'const bob = 0.4*Math.sin(st.phase*2)*(0.035+Math.max(0,grade)*0.06)', 1)


# ---------- 산 이름 누르면 저장 + 산 고르기 ----------
BRAND_CSS = '''
#brand .mtName{cursor:pointer;pointer-events:auto;border-bottom:1px dashed rgba(244,239,230,.45);padding-bottom:1px}
#brand .mtName:hover{color:#fff;border-bottom-color:#fff}
body.touch #brand > span.mtName{display:inline;font-size:12px}
.mtSaved{margin:-4px 0 8px;font-size:13px;color:var(--moss)}
'''


def patch_brand(P, m):
    P.rep('<b>능선</b><span class="sep"></span><span>', '<b>능선</b><span class="sep"></span><span class="mtName" role="button" tabindex="0" title="다른 산 고르기 (기록은 저장돼요)">', 1)
    P.rep('function clearHike(){', 'window.__saveHike = () => { saveHike(); return st.started && !st.finished ? (st.walked||0) : null; };\nfunction clearHike(){', 1)


# ---------- 오프닝: 이 산의 실제 능선 실루엣 ----------
def _grid(d, sc):
    N = d['N']; return np.frombuffer(base64.b64decode(d['h']), '<u2').astype(float).reshape(N, N) / sc, N, d['size']


def _samp(G, N, S, x, z):
    c = S / (N - 1); gx = (x + S / 2) / c; gz = (z + S / 2) / c
    if gx < 0 or gz < 0 or gx > N - 1.001 or gz > N - 1.001: return None
    i, j = int(gx), int(gz); u, w = gx - i, gz - j
    return (G[j, i] * (1 - u) + G[j, i + 1] * u) * (1 - w) + (G[j + 1, i] * (1 - u) + G[j + 1, i + 1] * u) * w


_SKY = {}


def skyline(data):
    k = data['meta']['id']
    if k not in _SKY: _SKY[k] = _skyline(data)
    return _SKY[k]


def _skyline(data):
    M = data['meta']; F = _grid(data['far'], 2); U = _grid(data['ultra'], 1); Nn = _grid(data, 10)
    def h(x, z):
        for g in (Nn, F, U):
            v = _samp(*g, x, z)
            if v is not None: return M['H0'] + (v - M['H0']) * M['VEX'] if g is Nn else (v - M['BASE'] if M.get('farReal') else v)
        return 0.0
    sx, sz = data['trail'][-1]; tx_, tz_ = data['trail'][0]
    vx, vz = tx_ - sx, tz_ - sz; L = math.hypot(vx, vz) or 1; vx, vz = vx / L, vz / L
    D = max(3800, L + 1600)
    cx, cz = sx + vx * D, sz + vz * D
    SK = M.get('skyline') or {}                  # 산 설정 "skyline": 골짜기 코스(남체)처럼 둘레 벽이 높을 때
    camh = h(cx, cz) + SK.get('up', 80)
    yaw = math.atan2(sx - cx, sz - cz)          # 정상 쪽
    W, FOV = 1600, math.radians(62); f = (W / 2) / math.tan(FOV / 2)
    off = math.atan((1080 - W / 2) / f)          # 정상을 화면 오른쪽(1080px)에
    bands = [(D + 9000, 23000), (D + 4500, D + 9000), (D + 1400, D + 4500), (D * 0.55, D + 1400)]
    cols = list(range(0, W + 1, 16))
    E = np.full((len(bands), len(cols)), -0.3)
    for ci, px in enumerate(cols):
        a = yaw + off - math.atan((px - W / 2) / f)
        dx, dz = math.sin(a), math.cos(a)
        r = 250.0
        while r < 23000:
            e = math.atan2(h(cx + dx * r, cz + dz * r) - camh - r * r / (2 * 6371000) * 0.87, r)
            for bi, (r0, r1) in enumerate(bands):
                if r0 <= r < r1 and e > E[bi, ci]: E[bi, ci] = e
            r *= 1.012
    T = np.tan(E)
    fr = T[-1]
    lo_c, hi_c = 55, 80                                   # 정상 근처 열 (1080px 둘레)
    pk = lo_c + int(np.argmax(fr[lo_c:hi_c + 1]))
    top = max(float(fr[pk]), float(T[:-1].max()) * 0.0 + float(fr[pk]))
    if SK.get('fit') == 'all': top = max(top, float(T.max()))   # 가장 높은 둘레 산까지 화면에 담기
    low = float(np.percentile(fr, 8))
    # 정상 → y 300, 앞 능선의 낮은 곳 → y 800 이 되도록 맞춰요 (산이 화면을 꽉 채우지 않고 하늘이 넉넉하게)
    B = (800 - 300) / max(1e-4, top - low); A = 300 + B * top
    Y = np.clip(A - B * T, 120, 900)
    peakX = pk * 16; peakY = float(Y[-1][pk])
    return dict(step=16, layers=[[round(v, 1) for v in Y[i]] for i in range(len(bands) - 1)], front=[round(v, 1) for v in Y[-1]],
                peakX=peakX, peakY=round(peakY, 1))


LD_JS = r'''  const LD = __LD__, LCOL = ['#7a7699','#5d5c82','#43456a'];
  const layers = LD.layers.map((ys,i)=>({ys, c:LCOL[i], d:[.1,.3,.5][i]}));
  layers.forEach((L,i)=>{ let d=`M0 900`; L.ys.forEach((y,k)=>{ d+=` L${k*LD.step} ${y}`; }); d+=` L${W} 900 Z`;
    const p=document.createElementNS('http://www.w3.org/2000/svg','path'); p.setAttribute('d',d); p.setAttribute('fill',L.c); p.setAttribute('class','ridge'); p.style.animationDelay=(L.d)+'s'; R.appendChild(p);
    if(i===1||i===2){ const my = Math.min(...L.ys.slice(10,90)) + 60; const m=document.createElementNS('http://www.w3.org/2000/svg','rect'); m.setAttribute('x',-200); m.setAttribute('y',my); m.setAttribute('width',W+400); m.setAttribute('height',38); m.setAttribute('rx',19); m.setAttribute('fill','url(#ldMist)'); m.setAttribute('filter','url(#ldBlur)'); m.setAttribute('class','mist'+(i===2?' b':'')); R.appendChild(m); } });
  // 맨 앞 능선: 실제 지형에서 잘라 온 이 산의 실루엣, 오른쪽 봉우리가 정상
  const peakX=LD.peakX, peakY=LD.peakY, pts=LD.front.map((y,k)=>[k*LD.step, y]);
  const front=document.createElementNS('http://www.w3.org/2000/svg','path'); front.setAttribute('d','M0 900 '+pts.map(p=>`L${p[0]} ${p[1].toFixed(1)}`).join(' ')+` L${W} 900 Z`); front.setAttribute('fill','#191d30'); front.setAttribute('class','ridge'); front.style.animationDelay='.9s'; R.appendChild(front);
'''


def patch_opening(P, data):
    import re
    ld = skyline(data)
    js = LD_JS.replace('__LD__', json.dumps(ld))
    t2, n = re.subn(r"  const layers=\[\{y:520.*?R\.appendChild\(front\);\n", lambda _: js, P.t, count=1, flags=re.S)
    if n != 1: raise SystemExit('[opening] 오프닝 능선 코드를 못 찾았어요')
    P.t = t2
    # 웅장하게: 해를 봉우리 뒤로, 빛을 더 크게
    P.rep('<g class="glow"><circle cx="1060" cy="560" r="420"', f'<g class="glow"><circle cx="{ld["peakX"]-40}" cy="{max(200, ld["peakY"]-10)}" r="520"', 1)
    P.rep('<g class="sun"><circle cx="1060" cy="560" r="46"', f'<g class="sun"><circle cx="{ld["peakX"]-40}" cy="{max(200, ld["peakY"]+30)}" r="46"', 1)


SEA_JS = "const SEA_C = new THREE.Color(0x5f86a6), SEA_C2 = new THREE.Color(0x7aa0bd);\n"


def patch_geo(P, m, data):
    """먼 풍경 = 실제 주변 지리: 먼 산 높이를 실제 해발로 받아 BASE만 빼고, 바다는 바다색으로."""
    if not P.t.count('ALT0 ='):
        P.rep('const H0 = 272, VEX = 1.058;', 'const H0 = 272, VEX = 1.058, ALT0 = 0;', 1)
    if data['meta'].get('farReal'):
        P.rep('decode(F.h, 2)', 'decode(F.h, 2).map(v => v - ALT0)')
        P.rep('decode(U.h, 1)', 'decode(U.h, 1).map(v => v - ALT0)')
    P.rep('if(hm > 85 || hm < 3) continue;', 'if(hm + ALT0 > 85 || hm + ALT0 < 3) continue;', 1)
    P.rep('function toonColor(x,z,h,ny,o){', SEA_JS + 'function toonColor(x,z,h,ny,o){\n  if(h + ALT0 < 1.5 && ny > 0.97){ o.copy(SEA_C).lerp(SEA_C2, vnoise(x/1400, z/1400)*0.6); return o; }   // 바다', 1)


def patch_common(P, m, data):
    # 계절 문구 빼기
    P.rep('<p class="ldTag">가을 산길을 한 걸음씩, 함께 오르다</p>', '<p class="ldTag">산길을 한 걸음씩, 함께 오르다</p>', 1)
    P.rep('가을, 북한산 백운대에 함께 오르다', '북한산 백운대에 함께 오르다', need=False)
    P.rep(' 가을 산길을 걷는', ' 산길을 걷는', need=False)
    P.rep('"가을 산길을 한 걸음씩.', '"산길을 한 걸음씩.', need=False)
    patch_opening(P, data)
    patch_shake(P)
    patch_brand(P, m)
    P.rep('</style>', BRAND_CSS + '</style>', 1)
    patch_biome(P, bio_for(m, data['meta']))
    patch_season(P, m, data['meta'])
    patch_geo(P, m, data)


# ---------- 산 고르기 카드 그림: 실제 능선 실루엣 ----------
SKIES = {
    'kr':    ('#fde7c8', '#f7c59a', '#9fb7d8', ['#b7bfd8', '#8f9cc0', '#6b7aa6'], '#3d4a6e', '#fff4dc'),
    'snow':  ('#e8f3ff', '#bcd9f2', '#7fa9d6', ['#c7d6ea', '#9fb6d6', '#7590ba'], '#3b4f78', '#ffffff'),
    'warm':  ('#ffe9cf', '#ffc79a', '#e59a7a', ['#d9b2a4', '#b98f8a', '#8f6c74'], '#4e3d4c', '#fff1d6'),
    'green': ('#eaf6e7', '#c6e3c9', '#8cbcae', ['#b2cfc4', '#89b0a6', '#628d86'], '#2f4f4c', '#fffbe8'),
}


def thumb_svg(m, data):
    ld = skyline(data)
    b = (m.get('biome') or {})
    key = 'kr' if m['region'] == 'kr' else ('snow' if b.get('snow') else ('warm' if b.get('preset') in ('volcanic', 'lenga') else 'green'))
    s0, s1, s2, lay, fr, sun = SKIES[key]
    i = m['id']
    def path(ys):
        return 'M0 900 ' + ' '.join(f'L{k*16} {y:.0f}' for k, y in enumerate(ys)) + ' L1600 900 Z'
    top = max(140, min(min(ld['front']), *(min(l) for l in ld['layers'])) - 110)
    snow = ''
    snowY = min(ld['front']) + 90 if (m.get('skyline') or {}).get('fit') == 'all' else ld['peakY']   # 골짜기 코스는 높은 산꼭대기만 눈
    if b.get('snow'):
        snow = f'<path d="{path(ld["front"])}" fill="#fff" opacity=".9" clip-path="url(#c{i})"/>'
        clip = f'<clipPath id="c{i}"><rect x="0" y="0" width="1600" height="{snowY+60:.0f}"/></clipPath>'
    else:
        clip = ''
    return (f'<svg viewBox="0 {top:.0f} 1600 {900-top:.0f}" preserveAspectRatio="xMidYMax slice" aria-hidden="true">'
            f'<defs><linearGradient id="g{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{s2}"/><stop offset=".6" stop-color="{s1}"/><stop offset="1" stop-color="{s0}"/></linearGradient>{clip}</defs>'
            f'<rect y="0" width="1600" height="900" fill="url(#g{i})"/><circle cx="{ld["peakX"]-260}" cy="{ld["peakY"]-40:.0f}" r="70" fill="{sun}" opacity=".85"/>'
            + ''.join(f'<path d="{path(ys)}" fill="{lay[k]}"/>' for k, ys in enumerate(ld['layers']))
            + f'<path d="{path(ld["front"])}" fill="{fr}"/>{snow}</svg>')


# ---------- 계절 고르기 (봄·여름·가을·겨울) ----------
SEASON_ROWS = [
    ['계절', 'Season', '季節', '季节'], ['봄', 'Spring', '春', '春'], ['여름', 'Summer', '夏', '夏'], ['가을', 'Autumn', '秋', '秋'], ['겨울', 'Winter', '冬', '冬'],
    ['이 산은 일 년 내내 눈과 바위의 계절이에요', 'This mountain stays in its season of snow and rock all year', 'この山は一年中、雪と岩の季節です', '这座山一年四季都是冰雪与岩石'],
    ['바꾸면 산을 새로 그려요', 'Changing it redraws the mountain', '変えると山を描き直します', '更改后会重新绘制山景'],
]

SEASON_JS = r'''
const SEASONS_OK = __SEASONS__;
let SEASON = 'autumn'; try{ const s = localStorage.getItem('neungseon.season.__ID__'); if(SEASONS_OK.includes(s)) SEASON = s; }catch(e){}
if(!SEASONS_OK.length) SEASON = 'fixed';
const SZ = ({
  spring: { green:.42, snow:0, grass:[[[120,160,70],[140,176,84],[104,146,60],[96,136,58]],[[110,150,66],[130,166,78],[96,138,56],[88,128,52]]], bushRed:[[96,140,64],[112,156,74],[84,128,58]], bushOak:[[120,160,80],[136,176,92],[104,146,70]], toon:[0x5d8a3e,0x7aa34a,0x9cbc5a,0xc6d27a,0xe9b7c8,0x86ad55,0x5f8d44],
    leaf:[[236,176,196],[244,206,216],[226,150,176],[150,186,96],[126,170,80],[180,206,120]],
    pals:[[[232,170,192],[244,200,212],[220,150,178],[250,220,228]],[[150,190,96],[170,206,112],[130,176,84],[190,214,130]],[[96,140,70],[80,124,60],[112,156,80],[70,110,54]],[[176,204,110],[156,190,96],[196,216,130],[136,176,86]],[[226,160,186],[150,190,100],[206,130,166],[120,170,90]]],
    floor:[0x4a4a28,0x5e6a2e,0x4f5a2a],
    sp:{ mapleRed:[[232,166,188],[244,198,212],[218,140,172],[250,222,230],[204,120,156],[236,184,200]], mapleOrange:[[150,190,96],[170,206,112],[130,176,84],[190,214,130],[118,160,76],[160,196,104]],
         oak:[[120,160,80],[136,176,92],[104,146,70],[150,186,100],[96,136,66],[128,168,86]], oakGold:[[166,200,104],[186,214,120],[150,188,92],[176,206,112],[200,220,140],[140,180,90]],
         yellow:[[196,214,120],[214,226,140],[176,200,106],[160,190,96],[220,230,150],[150,184,90]], birch:[[176,206,112],[196,220,130],[160,194,100],[150,186,96],[206,226,144]],
         green:[[96,140,64],[112,156,74],[84,128,58],[126,166,82],[104,148,70],[92,136,62]], bare:[[150,186,100],[130,170,86]] } },
  summer: { green:.62, snow:0, grass:[[[84,124,52],[100,140,60],[70,110,44],[64,100,40]],[[78,118,48],[94,134,58],[66,104,42],[58,94,38]]], bushRed:[[52,92,40],[64,106,48],[44,82,36]], bushOak:[[64,104,44],[76,116,50],[54,92,38]], toon:[0x2f5a2a,0x3f6e30,0x4f7c36,0x5f8a3e,0x3a6630,0x2a5026,0x467038],
    leaf:[[96,130,60],[80,116,52],[120,150,70],[70,100,46],[110,120,60],[90,96,50]],
    pals:[[[52,96,44],[64,110,52],[44,84,38],[76,120,58]],[[70,116,52],[84,130,60],[60,104,46],[96,140,66]],[[40,74,36],[32,62,30],[50,86,42],[28,52,26]],[[84,124,56],[70,110,50],[96,136,64],[60,98,44]],[[60,106,48],[48,92,40],[74,120,56],[40,80,36]]],
    floor:[0x3a3e22,0x4a5428,0x3e4824],
    sp:{ mapleRed:[[60,112,48],[74,126,56],[50,98,42],[86,136,62],[44,88,38],[68,118,52]], mapleOrange:[[70,120,52],[84,134,60],[60,108,46],[96,144,66],[54,98,42],[78,128,56]],
         oak:[[64,104,44],[76,116,50],[54,92,38],[88,126,56],[48,84,36],[70,110,48]], oakGold:[[80,124,54],[94,138,62],[70,112,48],[86,130,58],[104,146,68],[64,104,46]],
         yellow:[[90,136,60],[104,148,68],[80,124,54],[72,114,50],[110,152,72],[66,108,46]], birch:[[96,140,64],[110,152,72],[84,128,58],[76,120,54],[120,160,80]],
         green:[[48,86,36],[58,98,42],[40,76,32],[66,106,46],[52,92,38],[44,80,34]], bare:[[70,110,50],[60,100,44]] } },
  winter: { green:0, snow:.82, grass:[[[196,186,160],[214,206,184],[176,166,140],[226,226,222]],[[190,180,156],[210,202,180],[170,160,136],[222,222,218]]], bushRed:[[120,90,70],[100,76,60],[226,232,238]], bushOak:[[130,104,80],[110,90,70],[228,234,240]], toon:[0xdfe5ec,0xc9d2dc,0xb7c2cf,0xe9eef3,0xd3dbe4,0xa9b6c4,0xc1cbd6],
    leaf:[[226,232,238],[210,218,226],[150,130,110],[236,240,244],[190,196,204],[170,150,128]],
    pals:[[[120,104,92],[230,236,242],[100,90,80],[214,222,230]],[[220,228,236],[110,96,84],[236,240,246],[130,116,100]],[[40,62,44],[226,232,238],[34,54,38],[210,218,226]],[[132,116,100],[226,232,238],[112,100,88],[240,244,248]],[[228,234,240],[118,104,92],[212,220,228],[96,86,76]]],
    floor:[0xd8dee6,0xe6ebf0,0xcfd6df], bareAll:true,
    sp:{} },
})[SEASON] || { green:0, snow:0 };
const seasonGLSL = () => `lit = mix(lit, lit.g*vec3(0.62,1.0,0.5) + vec3(0.03,0.06,0.0), ${(SZ.green||0).toFixed(2)}); lit = mix(lit, vec3(0.9,0.93,0.97)*(0.86+0.14*lit.g), ${(SZ.snow||0).toFixed(2)});`;
'''

SEASON_UI_CSS = '''
.seasonRow{display:flex;gap:6px;flex-wrap:wrap;margin:2px 0 4px}
.seasonRow button{padding:7px 14px;border-radius:999px;border:1px solid var(--paperLine);background:transparent;color:var(--ink);font-size:14px;cursor:pointer}
.seasonRow button.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.seasonNote{font-size:12px;opacity:.7;margin:0 0 6px}
'''


CLIMATES = {
    # 봄꽃·여름꽃 색, 겨울 눈 양(0~1), 계절별 설선(실제 해발 m), 상고대
    'kr':   dict(spring=dict(flower=[[214,82,150],[232,120,180],[196,60,130],[240,160,200],[226,100,160]], flowerAmt=.35), summer=dict(flower=[[236,150,60],[250,190,90],[220,120,50]], flowerAmt=.08), winter=dict(snowAmt=.8)),
    'kr-south': dict(spring=dict(flower=[[214,82,150],[232,120,180],[196,60,130],[240,160,200]], flowerAmt=.3), winter=dict(snowAmt=.4)),
    'kr-high': dict(spring=dict(flower=[[214,82,150],[232,120,180],[196,60,130],[240,160,200]], flowerAmt=.45), summer=dict(flower=[[236,150,60],[250,196,80],[230,230,236]], flowerAmt=.12), winter=dict(snowAmt=.92, rime=1)),
    'jp':   dict(spring=dict(snowline=2700), summer=dict(snowline=9000, flower=[[240,220,90],[236,236,240],[200,120,200]], flowerAmt=.06), autumn=dict(snowline=3500), winter=dict(snowAmt=.95, snowline=1600)),
    'alps': dict(spring=dict(snowline=2200, flower=[[250,250,250],[240,214,70]], flowerAmt=.1, notCherry=1), summer=dict(snowline=3300, flower=[[80,110,220],[244,214,70],[246,246,246],[206,90,170],[220,60,60]], flowerAmt=.35, notCherry=1), winter=dict(snowAmt=.97, snowline=900)),
    'sierra': dict(spring=dict(notCherry=1, flower=[[150,110,220],[244,200,70]], flowerAmt=.12), summer=dict(notCherry=1, grassDry=1), winter=dict(snowAmt=.7, snowline=1900)),
    'cn':   dict(spring=dict(flower=[[214,82,150],[240,240,244]], flowerAmt=.2), winter=dict(snowAmt=.5, rime=1)),
    'patagonia': dict(spring=dict(notCherry=1, snowline=1100), summer=dict(notCherry=1, flower=[[246,222,80],[246,246,246],[214,60,60]], flowerAmt=.15, snowline=1500), autumn=dict(snowline=1300), winter=dict(snowAmt=.85, snowline=500)),
    'nz':   dict(spring=dict(notCherry=1, snowline=1650, flower=[[246,246,246]], flowerAmt=.12), summer=dict(notCherry=1, snowline=2500, flower=[[246,246,246],[240,214,90]], flowerAmt=.18), autumn=dict(snowline=2200), winter=dict(snowAmt=.9, snowline=1150)),
    'fixed': dict(),
}


def climate_js(m, meta):
    c = CLIMATES[m.get('climate', 'kr')]; base = meta['BASE']; out = {}
    for s, d in c.items():
        d = dict(d)
        if 'snowline' in d: d['snowline'] = round(d['snowline'] - base)
        out[s] = d
    return out


def patch_season(P, m, meta):
    ok = m.get('seasons', ['spring', 'summer', 'autumn', 'winter'])
    P.rep('const BIO = ', SEASON_JS.replace('__SEASONS__', json.dumps(ok)).replace('__ID__', m['id'])
          + 'const SZX = ' + json.dumps(climate_js(m, meta)) + ';\nObject.assign(SZ, SZX[SEASON] || {});\n'
          + 'if(SZ.notCherry && SZ.sp && SZ.sp.mapleOrange) SZ.sp = Object.assign({}, SZ.sp, {mapleRed: SZ.sp.mapleOrange});\n'
          + 'if(SZ.snowAmt != null) SZ.snow = SZ.snowAmt;\n'
          + "if(SZ.rime){ SZ.bareAll = false; SZ.sp = {}; for(const k of ['mapleRed','mapleOrange','oak','oakGold','yellow','birch','green','bare']) SZ.sp[k] = [[236,240,246],[222,230,240],[248,250,253],[210,220,232],[240,244,250]]; }\n"
          + 'const BIO = ', 1)
    P.rep('const D = JSON.parse(', 'if(SZ.snowline != null) BIO.snow = SZ.snowline;\nconst D = JSON.parse(', 1)
    # 풀·덤불·꽃
    P.rep("strokes(220, v? [[150,130,80],[170,150,96],[120,110,70],[100,96,62]] : [[176,144,70],[196,164,84],[150,120,56],[120,104,52]]",
          "strokes(220, SZ.grass ? SZ.grass[v ? 1 : 0] : v? [[150,130,80],[170,150,96],[120,110,70],[100,96,62]] : [[176,144,70],[196,164,84],[150,120,56],[120,104,52]]", 1)
    P.rep("const pal = kind==='bushRed' ? [[160,38,28],[186,66,34],[138,30,26],[120,48,30],[200,90,40]] : kind==='bushOak' ? [[140,96,48],[160,112,54],[118,80,40],[176,128,60]]",
          "const pal = kind==='bushRed' ? (SZ.flower || SZ.bushRed || [[160,38,28],[186,66,34],[138,30,26],[120,48,30],[200,90,40]]) : kind==='bushOak' ? (SZ.bushOak || [[140,96,48],[160,112,54],[118,80,40],[176,128,60]])", 1)
    P.rep("zones.grass += BIO.grass;", "zones.grass += BIO.grass; zones.bushRed += (SZ.flowerAmt || 0);", 1)
    # 나무 색
    P.rep("  bare:       {pal:[[110,72,40],[96,64,36]], trunk:'#4a3a2e', bare:true}\n};",
          "  bare:       {pal:[[110,72,40],[96,64,36]], trunk:'#4a3a2e', bare:true}\n};\n"
          "if(SZ.sp) for(const k in SZ.sp) if(SPECIES[k]) SPECIES[k].pal = SZ.sp[k];\n"
          "if(SZ.bareAll) for(const k in SPECIES){ SPECIES[k].bare = true; SPECIES[k].pal = [[226,232,238],[214,222,230],[240,244,248],[150,136,120],[200,208,216]]; }   // 겨울: 남은 잎 대신 눈송이·마른 잎만 (단풍색 점 없음)", 1)
    P.rep("[[176,70,32],[150,52,28],[196,100,40],[120,60,30]] ];", "[[176,70,32],[150,52,28],[196,100,40],[120,60,30]] ];\n  if(SZ.pals) pals.splice(0, pals.length, ...SZ.pals);", 1)
    P.rep("const LEAF_COLS = [[150,52,30],[176,82,32],[190,120,45],[150,104,52],[112,72,40],[96,58,34],[168,140,70],[130,40,28]];",
          "const LEAF_COLS = [[150,52,30],[176,82,32],[190,120,45],[150,104,52],[112,72,40],[96,58,34],[168,140,70],[130,40,28]];\n"
          "if(SZ.leaf) LEAF_COLS.splice(0, LEAF_COLS.length, ...SZ.leaf);", 1)
    P.rep("const TOON_PAL = [0x3c6230, 0x5f7a32, 0xb08a2e, 0xd8822c, 0xcc4a22, 0xa42e1e, 0x467038].map(c=>new THREE.Color(c));",
          "const TOON_PAL = (SZ.toon || [0x3c6230, 0x5f7a32, 0xb08a2e, 0xd8822c, 0xcc4a22, 0xa42e1e, 0x467038]).map(c=>new THREE.Color(c));", 1)
    P.rep("  rock: new THREE.Color(0xa29d93), rockDark: new THREE.Color(0x7c776f), trail: new THREE.Color(0xb39a72)\n};",
          "  rock: new THREE.Color(0xa29d93), rockDark: new THREE.Color(0x7c776f), trail: new THREE.Color(0xb39a72)\n};\n"
          "if(SZ.floor){ C.floor1.setHex(SZ.floor[0]); C.floor2.setHex(SZ.floor[1]); C.floor3.setHex(SZ.floor[2]); }\n"
          "if(SZ.snow){ C.rock.lerp(new THREE.Color(0xe8edf2), SZ.snow*0.6); C.rockDark.lerp(new THREE.Color(0xc8d0da), SZ.snow*0.5); }", 1)
    # 바닥 질감 (낙엽 → 새싹·풀·눈)
    P.rep("        lit = mix(lit, mix(texture2D(tCanopy, vWP.xz/110.0).rgb, texture2D(tCanopy, vWP.zx/260.0 + 0.3).rgb, 0.4), cdist);",
          "        lit = mix(lit, mix(texture2D(tCanopy, vWP.xz/110.0).rgb, texture2D(tCanopy, vWP.zx/260.0 + 0.3).rgb, 0.4), cdist);\n        ${seasonGLSL()}", 1)
    P.rep("        vec3 alb = lit * vSplat.x + rk * vSplat.y + dt * vSplat.z;",
          "        rk = mix(rk, vec3(0.92,0.94,0.97), ${((SZ.snow||0)*0.45).toFixed(2)});\n        vec3 alb = lit * vSplat.x + rk * vSplat.y + dt * vSplat.z;", 1)
    # 시작 화면: 계절 고르기
    if ok:
        btns = ''.join(f'<button type="button" data-s="{s}">{dict(spring="봄", summer="여름", autumn="가을", winter="겨울")[s]}</button>' for s in ok)
        ui = f'<h2>계절</h2>\n    <div class="seasonRow" id="seasonRow">{btns}</div><p class="seasonNote">바꾸면 산을 새로 그려요</p>\n    '
    else:
        ui = '<h2>계절</h2>\n    <p class="seasonNote">이 산은 일 년 내내 눈과 바위의 계절이에요</p>\n    '
    P.rep('<h2>텐트 색 <small class="tentHint">', ui + '<h2>텐트 색 <small class="tentHint">', 1)
    P.rep('</body>', '''<script>
(function(){ const row = document.getElementById('seasonRow'); if(!row) return; const K = 'neungseon.season.%s';
  let cur = 'autumn'; try{ cur = localStorage.getItem(K) || 'autumn'; }catch(e){}
  row.querySelectorAll('button').forEach(b => { b.classList.toggle('on', b.dataset.s === cur);
    b.onclick = () => { if(b.dataset.s === cur) return; try{ localStorage.setItem(K, b.dataset.s); sessionStorage.setItem('neungseon.go', '%s'); }catch(e){} location.reload(); }; });
})();
</script>
</body>''' % (m['id'], m['id']), 1)
    P.rep('</style>', SEASON_UI_CSS + '</style>', 1)
