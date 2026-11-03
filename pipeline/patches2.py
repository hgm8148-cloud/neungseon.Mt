"""build_site.py 가 쓰는 추가 바꿔 끼우기 (2026-11-03 요청)
- 계절 문구 빼기, 오프닝 = 그 산의 실제 능선 실루엣, 산 이름 누르면 저장 + 산 고르기,
- 걸음마다 화면 떨림 줄이기, 산별 식생·바위·눈(biome)
"""
import base64, json, math
import numpy as np

EXTRA_ROWS = [
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
            if v is not None: return M['H0'] + (v - M['H0']) * M['VEX'] if g is Nn else v
        return 0.0
    sx, sz = data['trail'][-1]; tx_, tz_ = data['trail'][0]
    vx, vz = tx_ - sx, tz_ - sz; L = math.hypot(vx, vz) or 1; vx, vz = vx / L, vz / L
    D = max(3800, L + 1600)
    cx, cz = sx + vx * D, sz + vz * D
    camh = h(cx, cz) + 80
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
    if b.get('snow'):
        snow = f'<path d="{path(ld["front"])}" fill="#fff" opacity=".9" clip-path="url(#c{i})"/>'
        clip = f'<clipPath id="c{i}"><rect x="0" y="0" width="1600" height="{ld["peakY"]+60:.0f}"/></clipPath>'
    else:
        clip = ''
    return (f'<svg viewBox="0 {top:.0f} 1600 {900-top:.0f}" preserveAspectRatio="xMidYMax slice" aria-hidden="true">'
            f'<defs><linearGradient id="g{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{s2}"/><stop offset=".6" stop-color="{s1}"/><stop offset="1" stop-color="{s0}"/></linearGradient>{clip}</defs>'
            f'<rect y="0" width="1600" height="900" fill="url(#g{i})"/><circle cx="{ld["peakX"]-260}" cy="{ld["peakY"]-40:.0f}" r="70" fill="{sun}" opacity=".85"/>'
            + ''.join(f'<path d="{path(ys)}" fill="{lay[k]}"/>' for k, ys in enumerate(ld['layers']))
            + f'<path d="{path(ld["front"])}" fill="{fr}"/>{snow}</svg>')
