"""로딩 화면 두 가지 (2026-11-04, 승연 님 요청)

1) 처음 들어올 때(산 고르기 화면이 뜨는 경우): 북한산 사진 대신 '능선' 고유의 브랜드 화면
   - 새벽 하늘이 밝아지고, 겹겹의 능선이 천천히 흐르고, 한 줄 능선이 그려지며 '능선' 글자가 떠올라요.
   - 아래로 산 이름들이 천천히 흘러가요 (산을 더하면 저절로 늘어나요). 숫자로 산 개수를 못박는 표현은 쓰지 않아요.
2) 산을 골라 들어갈 때: 그 산 사진 + 실제 탐방로 고도 그래프 위를 등산객 점이 걸어 올라가요.
   - 예전엔 SVG 선을 메인 스레드로 그려서, 지형을 만드는 동안 화면이 뚝뚝 끊겼어요.
   - 이제 움직이는 것은 모두 transform/opacity(합성 스레드)라 무거운 계산 중에도 부드럽게 움직여요.
   - 로딩 단계도 5번 → 14번으로 잘게 나눠 진행이 자연스럽게 이어져요.
"""
import json, math, glob, os
import numpy as np
from patches2 import _grid, _samp

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- 번역 (ko, en, ja, zh, de, fr, it, es, ne, sw) ----------
LOADER_FIX = [
    ['실제 지형을 본떠 만든 명산 산길', 'Mountain trails modeled on real terrain', '実際の地形をもとに作った名山の山道', '参照真实地形打造的名山步道', 'Bergwege nach dem Vorbild echter Landschaften', 'Des sentiers de montagne inspirés du relief réel', 'Sentieri di montagna ispirati al terreno reale', 'Senderos de montaña inspirados en el terreno real', 'वास्तविक भू-भागबाट प्रेरित हिमाली पदमार्ग', 'Njia za milima zilizoigwa kutoka ardhi halisi'],
    ['실제 지형을 본떠 만든 산길을 골라 보세요', 'Pick a trail modeled on real terrain', '実際の地形をもとに作った山道を選んでください', '选择一条参照真实地形打造的步道', 'Wähle einen Weg nach dem Vorbild echter Landschaft', 'Choisissez un sentier inspiré du relief réel', 'Scegli un sentiero ispirato al terreno reale', 'Elige un sendero inspirado en el terreno real', 'वास्तविक भू-भागबाट प्रेरित पदमार्ग छान्नुहोस्', 'Chagua njia iliyoigwa kutoka ardhi halisi'],
    ['km · 실제 고도 데이터를 본떠 만든 지형', 'km · terrain modeled on real elevation data', 'km・実際の標高データをもとに作った地形', '公里 · 参照真实海拔数据打造的地形', 'km · Gelände nach echten Höhendaten modelliert', 'km · relief modelé d’après des données d’altitude réelles', 'km · terreno modellato su dati di quota reali', 'km · terreno modelado a partir de datos de altitud reales', 'km · वास्तविक उचाइ तथ्याङ्कबाट बनाइएको भू-भाग', 'km · ardhi iliyoigwa kutoka data halisi ya mwinuko'],
    ['국내 명산', 'Korea', '韓国の名山', '韩国名山', 'Korea', 'Corée', 'Corea', 'Corea', 'कोरिया', 'Korea'],
    ['해외 명산', 'World', '世界の名山', '世界名山', 'Welt', 'Monde', 'Mondo', 'Mundo', 'विश्व', 'Dunia'],
    ['여유 있는 산행', 'An unhurried hike', 'ゆったりとした山歩き', '从容的山行', 'Eine gemächliche Wanderung', 'Une randonnée sans hâte', 'Un’escursione senza fretta', 'Una caminata sin prisas', 'फुर्सदको पदयात्रा', 'Matembezi ya taratibu mlimani'],
    ['오늘의 산행', "Today's hike", '今日の山歩き', '今天的山行', 'Heutige Wanderung', 'La randonnée du jour', 'L’escursione di oggi', 'La caminata de hoy', 'आजको पदयात्रा', 'Matembezi ya leo'],
    ['정상', 'Summit', '山頂', '山顶', 'Gipfel', 'Sommet', 'Vetta', 'Cumbre', 'शिखर', 'Kilele'],
    ['들머리', 'Trailhead', '登山口', '登山口', 'Ausgangspunkt', 'Départ', 'Partenza', 'Inicio del sendero', 'सुरुवात बिन्दु', 'Mwanzo wa njia'],
    ['편도', 'One way', '片道', '单程', 'Einfach', 'Aller simple', 'Solo andata', 'Solo ida', 'एकतर्फी', 'Njia moja'],
    ['바위와 자갈길을 다듬는 중', 'Smoothing the rocks and gravel path', '岩と砂利道を整えています', '正在整理岩石与碎石路', 'Felsen und Geröllpfad werden geglättet', 'On aplanit les rochers et le chemin de gravier', 'Sistemiamo rocce e sentiero di ghiaia', 'Alisando las rocas y el sendero de grava', 'चट्टान र गिट्टीको बाटो मिलाउँदै', 'Tunasawazisha miamba na njia ya changarawe'],
    ['숲을 심는 중', 'Planting the forest', '森を植えています', '正在种植森林', 'Der Wald wird gepflanzt', 'On plante la forêt', 'Piantiamo il bosco', 'Plantando el bosque', 'जङ्गल रोप्दै', 'Tunapanda msitu'],
    ['산의 결을 빚는 중', 'Shaping the folds of the mountain', '山のひだを形づくっています', '正在塑造山的纹理', 'Die Falten des Berges werden geformt', 'On façonne le relief de la montagne', 'Modelliamo le pieghe della montagna', 'Modelando el relieve de la montaña', 'पहाडको बनोट कुँद्दै', 'Tunaunda umbo la mlima'],
    ['바위와 흙의 결을 고르는 중', 'Choosing the textures of rock and soil', '岩と土の質感を選んでいます', '正在挑选岩石与泥土的质感', 'Fels- und Erdtexturen werden gewählt', 'On choisit les textures de roche et de terre', 'Scegliamo le trame di roccia e terra', 'Eligiendo las texturas de roca y tierra', 'चट्टान र माटोको बुनोट छान्दै', 'Tunachagua maumbile ya miamba na udongo'],
    ['구름바다를 띄우는 중', 'Floating the sea of clouds', '雲海を浮かべています', '正在铺开云海', 'Das Wolkenmeer wird ausgebreitet', 'On fait flotter la mer de nuages', 'Facciamo galleggiare il mare di nuvole', 'Haciendo flotar el mar de nubes', 'बादलको समुद्र फैलाउँदै', 'Tunaelea bahari ya mawingu'],
    ['돌계단을 놓는 중', 'Laying the stone steps', '石段を据えています', '正在铺设石阶', 'Die Steinstufen werden gelegt', 'On pose les marches de pierre', 'Posiamo i gradini di pietra', 'Colocando los escalones de piedra', 'ढुङ्गाका खुड्किला राख्दै', 'Tunaweka ngazi za mawe'],
    ['정상 야영장을 꾸리는 중', 'Setting up the summit campsite', '山頂キャンプ場を整えています', '正在布置山顶营地', 'Der Gipfelzeltplatz wird eingerichtet', 'On installe le bivouac du sommet', 'Allestiamo il campo in vetta', 'Preparando el campamento de la cumbre', 'शिखर शिविर मिलाउँदै', 'Tunaandaa kambi ya kileleni'],
    ['배낭을 챙기는 중', 'Packing your backpack', 'リュックを詰めています', '正在收拾背包', 'Der Rucksack wird gepackt', 'On prépare le sac à dos', 'Prepariamo lo zaino', 'Preparando la mochila', 'झोला तयार पार्दै', 'Tunafunga mkoba wako'],
    ['산새를 깨우는 중', 'Waking the mountain birds', '山の鳥を起こしています', '正在唤醒山鸟', 'Die Bergvögel werden geweckt', 'On réveille les oiseaux de la montagne', 'Svegliamo gli uccelli di montagna', 'Despertando a los pájaros del monte', 'पहाडका चराहरू ब्युँझाउँदै', 'Tunaamsha ndege wa mlimani'],
    ['하늘에 해와 별을 거는 중', 'Hanging the sun and stars in the sky', '空に太陽と星を掛けています', '正在把太阳和星星挂上天空', 'Sonne und Sterne werden an den Himmel gehängt', 'On accroche le soleil et les étoiles au ciel', 'Appendiamo il sole e le stelle al cielo', 'Colgando el sol y las estrellas en el cielo', 'आकाशमा घाम र तारा झुण्ड्याउँदै', 'Tunatundika jua na nyota angani'],
]

# 로딩 중간중간 쉬어 가며 화면을 그릴 틈 (맨 위 수준 구역 머리말 바로 앞)
STEPS = [
    ('// ---------- fine terrain ----------', '산의 결을 빚는 중', 0.14),
    ('// ---------- procedural textures (사실적 질감) ----------', '바위와 흙의 결을 고르는 중', 0.2),
    ('// ---------- 먼 산 풍경: 숲 무리, 겹겹이 옅어지는 능선, 운해 ----------', '구름바다를 띄우는 중', 0.56),
    ('// ---------- 오르막 구간:', '돌계단을 놓는 중', 0.62),
    ('// ---------- 정상 야영장:', '정상 야영장을 꾸리는 중', 0.68),
    ('// ---------- 아바타 ----------', '배낭을 챙기는 중', 0.74),
    ('// ---------- 소리:', '산새를 깨우는 중', 0.8),
    ('// ---------- 루프 ----------', '하늘에 해와 별을 거는 중', 0.92),
]


def L(d, l):
    return d.get(l) or d.get('en') or d['ko']


def loader_rows(m):
    rows = []
    for k in ('area', 'peak', 'course'):
        if m.get(k): rows.append([L(m[k], l) for l in ('ko', 'en', 'ja', 'zh')])
    return rows


def profile(m, data, n=90):
    M = data['meta']; H0 = M.get('H0', 272); VEX = M.get('VEX', 1.058); base = M.get('BASE', 0)
    G = _grid(data, 10); tr = data['trail']
    d = [0.0]
    for a, b in zip(tr[:-1], tr[1:]): d.append(d[-1] + math.dist(a, b))
    tot = d[-1] or 1
    out = []
    for i in range(n + 1):
        s = tot * i / n; k = int(np.searchsorted(d, s)); k = min(max(k, 1), len(tr) - 1)
        t = (s - d[k - 1]) / max(1e-6, d[k] - d[k - 1]); x = tr[k - 1][0] + (tr[k][0] - tr[k - 1][0]) * t; z = tr[k - 1][1] + (tr[k][1] - tr[k - 1][1]) * t
        v = _samp(*G, x, z)
        out.append(H0 + (v - H0) * VEX + base if v is not None else (out[-1] if out else 0))
    # 살짝 매끈하게
    a = np.array(out); a = np.convolve(np.pad(a, 2, mode='edge'), np.ones(5) / 5, mode='valid')
    return [round(float(v)) for v in a], tot


def ridges_svg(seed, W=2400, H=900):
    """브랜드 화면용 겹 능선 (화면보다 넓게 그려 옆으로 천천히 흘러가게)"""
    rnd = np.random.default_rng(seed)
    L_ = [(560, 90, '#3b3f66', .0025), (620, 110, '#2e3256', .0034), (690, 120, '#222644', .0042), (770, 110, '#171a31', .0055)]
    out = []
    for i, (y, a, c, f) in enumerate(L_):
        ph = rnd.random(3) * 10
        pts = []
        for x in range(0, W + 1, 24):
            n = math.sin(x * f + ph[0]) * .5 + math.sin(x * f * 2.3 + ph[1]) * .28 + math.sin(x * f * 5.1 + ph[2]) * .12
            pts.append(f'L{x} {y - (n + .4) * a:.0f}')
        out.append((f'M0 {H} ' + ' '.join(pts) + f' L{W} {H} Z', c, i))
    return out


CSS = r'''
/* ---------- 로딩 화면 (pipeline/loader_patch.py) ---------- */
#loading .ld2{display:none}
#loading.mBrand .ld2.brand, #loading.mMtn .ld2.mtn{display:block}
#loading.mBrand > .scene, #loading.mBrand > .copy, #loading.mBrand > .ldPhoto, #loading.mBrand > .ldCredit{display:none !important}
#loading.mBrand::before{display:none !important}
#loading.mMtn > .scene, #loading.mMtn > .copy{display:none !important}
#loading .ld2{position:absolute;inset:0;overflow:hidden}
@keyframes ld2Fade{from{opacity:0}to{opacity:1}}
@keyframes ld2Up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
/* 브랜드 */
#loading.mBrand{background:#141833}
.ld2.brand .bSky{position:absolute;inset:0;background:linear-gradient(180deg,#0f1430 0%,#252a55 38%,#5b4b78 62%,#c98a78 82%,#f2c08a 100%)}
.ld2.brand .bDawn{position:absolute;inset:0;background:linear-gradient(180deg,#1d2a5c 0%,#4f6aa8 40%,#e7a88a 72%,#ffd9a3 100%);opacity:0;animation:ld2Fade 9s 1s ease-in-out forwards;will-change:opacity}
.ld2.brand .bSun{position:absolute;left:50%;top:68%;width:44vmin;height:44vmin;margin:-22vmin 0 0 -22vmin;border-radius:50%;
  background:radial-gradient(circle,#fff3d6 0 9%,rgba(255,222,170,.75) 13%,rgba(255,196,140,.28) 34%,rgba(255,170,120,0) 68%);transform:translateY(16vmin);animation:bSun 10s .3s cubic-bezier(.25,.1,.25,1) forwards;will-change:transform}
@keyframes bSun{to{transform:translateY(0)}}
.ld2.brand .bR{position:absolute;left:0;bottom:0;width:150%;height:100%;will-change:transform}
.ld2.brand .bR.r0{animation:bDrift 60s linear infinite alternate}
.ld2.brand .bR.r1{animation:bDrift 46s linear infinite alternate-reverse}
.ld2.brand .bR.r2{animation:bDrift 34s linear infinite alternate}
.ld2.brand .bR.r3{animation:bDrift 26s linear infinite alternate-reverse}
@keyframes bDrift{from{transform:translateX(0)}to{transform:translateX(-30%)}}
.ld2.brand .bMist{position:absolute;left:-30%;width:160%;height:16vh;border-radius:50%;background:radial-gradient(ellipse at center,rgba(255,236,214,.34),rgba(255,236,214,0) 70%);will-change:transform;filter:blur(2px)}
.ld2.brand .bMist.m1{top:62%;animation:bMist 22s ease-in-out infinite alternate}
.ld2.brand .bMist.m2{top:72%;opacity:.8;animation:bMist 30s ease-in-out infinite alternate-reverse}
@keyframes bMist{from{transform:translateX(-6%)}to{transform:translateX(8%)}}
.ld2.brand .bBirds{position:absolute;left:0;top:34%;width:100%;height:60px;animation:bFly 26s 2s linear infinite;will-change:transform;opacity:.75}
.ld2.brand .bBirds i{position:absolute;width:14px;height:6px;border-top:2px solid #1d2140;border-radius:50% 50% 0 0;animation:bFlap 1.1s ease-in-out infinite}
.ld2.brand .bBirds i:nth-child(1){left:0;top:10px}.ld2.brand .bBirds i:nth-child(2){left:22px;top:0;animation-delay:.3s;transform:scale(.8)}.ld2.brand .bBirds i:nth-child(3){left:40px;top:16px;animation-delay:.6s;transform:scale(.7)}
@keyframes bFly{from{transform:translate(-80px,20px)}to{transform:translate(110vw,-30px)}}
@keyframes bFlap{50%{transform:scaleY(.4)}}
.ld2.brand .bLogo{position:absolute;left:0;right:0;top:19vh;text-align:center;padding:0 16px}
.ld2.brand .bKick{font-family:var(--body);font-size:12.5px;letter-spacing:.32em;color:rgba(255,240,222,.72);opacity:0;animation:ld2Up 1.2s .4s ease forwards}
.ld2.brand .bLineWrap{position:relative;width:min(420px,78vw);height:52px;margin:18px auto 0;opacity:0;animation:ld2Up 1.8s .8s ease forwards}
.ld2.brand .bLineWrap svg{display:block;width:100%;height:100%;overflow:visible}
.ld2.brand h2{margin:2px 0 0;font-family:var(--display);font-weight:700;font-size:clamp(52px,10vw,92px);letter-spacing:.42em;padding-left:.42em;color:#fff6e8;text-shadow:0 4px 34px rgba(255,190,130,.45);opacity:0;animation:ld2Up 1.6s 1.4s ease forwards}
.ld2.brand .bTag{margin:12px 0 0;font-family:var(--display);font-size:16px;letter-spacing:.3em;color:rgba(255,240,222,.88);opacity:0;animation:ld2Up 1.4s 2.1s ease forwards}
.ld2.brand .bTick{position:absolute;left:0;right:0;bottom:15vh;overflow:hidden;opacity:0;animation:ld2Fade 1.6s 2.6s ease forwards;-webkit-mask-image:linear-gradient(90deg,transparent,#000 18%,#000 82%,transparent);mask-image:linear-gradient(90deg,transparent,#000 18%,#000 82%,transparent)}
.ld2.brand .bTrack{display:flex;width:max-content;animation:bTick 70s linear infinite;will-change:transform}
.ld2.brand .bTrack span{font-family:var(--display);font-size:14px;letter-spacing:.14em;color:rgba(255,244,230,.7);white-space:nowrap;padding:0 14px}
.ld2.brand .bTrack span.dot{padding:0;width:4px;height:4px;border-radius:50%;background:rgba(255,214,160,.55);align-self:center}
@keyframes bTick{to{transform:translateX(-50%)}}
#loading.mBrand > .status{bottom:7vh}
#loading.mBrand #ldAlt{display:none}
.ld2 .bar{position:absolute;left:50%;bottom:calc(7vh - 14px);width:min(220px,60vw);height:2px;transform:translateX(-50%);background:rgba(255,240,222,.18);border-radius:2px;overflow:hidden}
.ld2 .bar i{position:absolute;inset:0;background:linear-gradient(90deg,#ffd9a6,#fff1dc);transform-origin:0 50%;transform:scaleX(.02);transition:transform 2.4s cubic-bezier(.2,.7,.3,1);will-change:transform}
/* 산 입장 */
#loading.mMtn .ldPhoto{animation:ld2Ken 30s cubic-bezier(.3,0,.25,1) forwards !important;will-change:transform,opacity;transition:opacity 1.8s ease}
@keyframes ld2Ken{from{transform:scale(1.14) translate(-1.6%,1.2%)}to{transform:scale(1.02) translate(0,0)}}
#loading.mMtn::before{background:linear-gradient(180deg,rgba(10,14,28,.62) 0%,rgba(10,14,28,.1) 30%,rgba(10,14,28,.05) 50%,rgba(10,14,28,.78) 100%) !important}
.ld2.mtn{z-index:3}
.ld2.mtn .mMist{position:absolute;left:-40%;width:180%;height:30vh;background:radial-gradient(ellipse at center,rgba(255,255,255,.2),rgba(255,255,255,0) 66%);will-change:transform}
.ld2.mtn .mMist.a{top:44%;animation:bMist 24s ease-in-out infinite alternate}
.ld2.mtn .mMist.b{top:58%;animation:bMist 33s ease-in-out infinite alternate-reverse;opacity:.7}
.ld2.mtn .mBeam{position:absolute;inset:-20%;background:linear-gradient(115deg,rgba(255,236,200,0) 35%,rgba(255,236,200,.16) 48%,rgba(255,236,200,0) 60%);opacity:0;animation:mBeam 9s 1.2s ease-in-out infinite alternate;will-change:opacity,transform}
@keyframes mBeam{from{opacity:0;transform:translateX(-4%)}to{opacity:1;transform:translateX(4%)}}
.ld2.mtn .mCopy{position:absolute;left:0;right:0;top:13vh;text-align:center;padding:0 16px;color:#fff6ea;text-shadow:0 2px 20px rgba(0,0,0,.45)}
.ld2.mtn .mKick{font-family:var(--body);font-size:12.5px;letter-spacing:.3em;opacity:0;animation:ld2Up 1s .2s ease forwards;color:rgba(255,240,224,.82)}
.ld2.mtn .mKick b{font-weight:700;letter-spacing:.36em;color:#ffd9a6;margin-right:.6em}
.ld2.mtn h2{margin:12px 0 0;font-family:var(--display);font-weight:700;font-size:clamp(40px,8.4vw,80px);letter-spacing:.14em;opacity:0;animation:ld2Up 1.4s .45s ease forwards}
.ld2.mtn .mSub{margin-top:10px;font-family:var(--display);font-size:clamp(15px,2.2vw,19px);letter-spacing:.1em;opacity:0;animation:ld2Up 1.2s .8s ease forwards}
.ld2.mtn .mSub b{font-weight:700;color:#ffe0b0;margin-left:.4em}
.ld2.mtn .mVista{margin:14px auto 0;max-width:560px;font-family:var(--display);font-size:14.5px;line-height:1.6;color:rgba(255,244,230,.88);opacity:0;animation:ld2Up 1.2s 1.2s ease forwards}
.ld2.mtn .mPanel{position:absolute;left:50%;bottom:calc(7vh + 34px);width:min(560px,calc(100% - 32px));transform:translateX(-50%);padding:14px 16px 12px;border-radius:18px;background:rgba(14,18,32,.38);border:1px solid rgba(255,255,255,.14);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);opacity:0;animation:ld2Fade 1.2s 1s ease forwards}
.ld2.mtn .pfHead{display:flex;justify-content:space-between;align-items:baseline;font-family:var(--body);font-size:12px;color:rgba(255,244,230,.8);letter-spacing:.04em;gap:8px}
.ld2.mtn .pfHead b{font-weight:700;color:#fff2de;font-variant-numeric:tabular-nums;margin-left:4px}
.ld2.mtn .pfHead .mid{text-align:center;flex:1;opacity:.85;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ld2.mtn .pf{position:relative;height:70px;margin-top:8px}
.ld2.mtn .pf svg{position:absolute;inset:0;width:100%;height:100%}
.ld2.mtn .pfMask{position:absolute;inset:0;-webkit-mask-size:100% 100%;mask-size:100% 100%;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat}
.ld2.mtn .pfFill{position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,214,160,.85),rgba(255,214,160,.25));transform-origin:0 50%;transform:scaleX(.02);transition:transform 2.4s cubic-bezier(.2,.7,.3,1);will-change:transform}
.ld2.mtn .pfRun{position:absolute;left:0;top:0;width:100%;height:100%;transform:translateX(2%);transition:transform 2.4s cubic-bezier(.2,.7,.3,1);will-change:transform;pointer-events:none}
.ld2.mtn .pfDot{position:absolute;left:-7px;top:-7px;width:14px;height:14px;border-radius:50%;background:#fff3de;box-shadow:0 0 0 5px rgba(255,217,166,.28),0 0 18px rgba(255,217,166,.8);transition:transform 2.4s cubic-bezier(.2,.7,.3,1);will-change:transform}
.ld2.mtn .pfFlag{position:absolute;right:-2px;top:-20px;width:2px;height:20px;background:#fff1dc}
.ld2.mtn .pfFlag::after{content:'';position:absolute;left:2px;top:0;border-left:13px solid #ff9f5a;border-top:4px solid transparent;border-bottom:4px solid transparent}
#loading.mMtn > .status{bottom:7vh;z-index:4}
html:not([lang=ko]) .ld2.brand h2{letter-spacing:.1em;padding-left:.1em;font-size:clamp(40px,11vw,88px)}
html:not([lang=ko]) .ld2.brand .bKick, html:not([lang=ko]) .ld2.brand .bTag{letter-spacing:.12em}
html:not([lang=ko]) .ld2.mtn h2{letter-spacing:.04em}
@media (max-width:480px){.ld2.mtn .pfHead .mid{display:none}}
@media (max-height:620px){.ld2.mtn .mVista{display:none} .ld2.mtn .mCopy{top:8vh}}
@media (prefers-reduced-motion:reduce){.ld2 *{animation-duration:.01s !important;animation-iteration-count:1 !important}}
'''


def brand_html(mts):
    rs = ''.join(f'<svg class="bR r{i}" viewBox="0 0 2400 900" preserveAspectRatio="xMinYMax slice"><path d="{d}" fill="{c}"/></svg>' for d, c, i in ridges_svg(11))
    order = sorted(mts, key=lambda x: (x['region'] != 'kr', x.get('order', 99)))
    names = ''.join(f'<span>{x["area"]["ko"]}</span><span class="dot"></span>' for x in order)
    line = ('<svg viewBox="0 0 420 52" preserveAspectRatio="none"><path d="M0 46 C40 44 60 30 92 28 S140 40 168 30 S206 6 232 8 S262 30 290 26 S330 12 356 20 S396 40 420 38" '
            'fill="none" stroke="#ffd9a6" stroke-width="2.2" stroke-linecap="round"/><circle cx="232" cy="8" r="3.2" fill="#fff1dc"/></svg>')
    return (f'<div class="ld2 brand" aria-hidden="false"><div class="bSky"></div><div class="bDawn"></div><div class="bSun"></div>{rs}'
            '<div class="bMist m1"></div><div class="bMist m2"></div><div class="bBirds"><i></i><i></i><i></i></div>'
            f'<div class="bLogo"><div class="bKick">실제 지형을 본떠 만든 명산 산길</div><div class="bLineWrap">{line}</div><h2>능선</h2><p class="bTag">여유 있는 산행</p></div>'
            f'<div class="bTick"><div class="bTrack">{names}{names}</div></div><div class="bar"><i></i></div></div>')


def mtn_html(m, prof, tot):
    e = m['elev']; lo, hi = min(prof), max(max(prof), e)
    W, H = 1000, 140
    pad = (hi - lo) * 0.12 + 20
    ys = [H - 8 - (v - lo + pad * .3) / (hi - lo + pad) * (H - 16) for v in prof]
    xs = [i / (len(prof) - 1) * W for i in range(len(prof))]
    line = 'M' + ' L'.join(f'{x:.0f} {y:.1f}' for x, y in zip(xs, ys))
    area = line + f' L{W} {H} L0 {H} Z'
    mask = ("url('data:image/svg+xml;utf8," + f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="none"><path d="{area}" fill="white"/></svg>'
            .replace('<', '%3C').replace('>', '%3E').replace('#', '%23').replace('"', '%22') + "')")
    pts = [round(y / H, 4) for y in ys]
    course = m.get('course', {}).get('ko', '')
    return (f'<div class="ld2 mtn"><div class="mMist a"></div><div class="mMist b"></div><div class="mBeam"></div>'
            f'<div class="mCopy"><div class="mKick"><b>능선</b><span>오늘의 산행</span></div><h2>{m["area"]["ko"]}</h2>'
            f'<div class="mSub"><span>{m["peak"]["ko"]}</span><b>{e:,}m</b></div><p class="mVista">{m["vista"]["ko"]}</p></div>'
            f'<div class="mPanel"><div class="pfHead"><span><span>들머리</span><b>{prof[0]:,}m</b></span><span class="mid"><span>{course}</span> · <span>편도</span> {tot/1000:.1f} km</span><span><span>정상</span><b>{e:,}m</b></span></div>'
            f'<div class="pf"><svg viewBox="0 0 {W} {H}" preserveAspectRatio="none"><path d="{area}" fill="rgba(255,255,255,.1)"/></svg>'
            f'<div class="pfMask" style="-webkit-mask-image:{mask};mask-image:{mask}"><div class="pfFill"></div></div>'
            f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="none"><path d="{line}" fill="none" stroke="rgba(255,240,222,.85)" stroke-width="2.4" vector-effect="non-scaling-stroke"/></svg>'
            f'<div class="pfFlag" style="top:calc({pts[-1]*100:.1f}% - 20px)"></div><div class="pfRun"><div class="pfDot"></div></div></div></div>'
            f'<div class="bar" style="display:none"><i></i></div></div>'
            f'<script>window.__PF={json.dumps(pts)};</script>')


JS = r'''<script>
// 로딩 화면 고르기 + 진행 표시 (pipeline/loader_patch.py) — 움직임은 transform만 써서 무거운 계산 중에도 부드럽게
(function(){ const root = document.getElementById('loading'); if(!root) return;
  let skip = /[?&]go=1/.test(location.search); try{ if(sessionStorage.getItem('neungseon.go') === '__ID__') skip = true; }catch(e){}
  root.classList.add(skip ? 'mMtn' : 'mBrand');
  const sel = skip ? '.ld2.mtn' : '.ld2.brand', box = root.querySelector(sel);
  const bar = box && box.querySelector('.bar i'), fill = box && box.querySelector('.pfFill'), run = box && box.querySelector('.pfRun'), dot = box && box.querySelector('.pfDot'), pf = box && box.querySelector('.pf');
  const P = window.__PF || [];
  const set = f => { f = Math.max(0.02, Math.min(1, f));
    if(bar) bar.style.transform = `scaleX(${f})`;
    if(fill) fill.style.transform = `scaleX(${f})`;
    if(run) run.style.transform = `translateX(${(f*100).toFixed(2)}%)`;
    if(dot && pf && P.length){ const k = f*(P.length-1), i = Math.min(P.length-2, Math.floor(k)), t = k - i, y = (P[i]*(1-t) + P[i+1]*t) * pf.clientHeight; dot.style.transform = `translateY(${y.toFixed(1)}px)`; } };
  const old = window.__ldProgress; window.__ldProgress = f => { try{ old && old(f); }catch(e){} set(f); };
  set(0.04);
})();
</script>
'''


def patch_honest(P):
    # 과장 없는 표현: 실제 지형을 '그대로' 옮긴 게 아니라 '본떠' 만든 것 (2026-11-04 승연 님)
    P.rep('<p>실제 고도 데이터로 만든 산길을 골라 보세요</p>', '<p>실제 지형을 본떠 만든 산길을 골라 보세요</p>', need=False)
    P.rep('km · 실제 고도 데이터로 만든 지형', 'km · 실제 고도 데이터를 본떠 만든 지형', need=False)
    for a,b in [('terrain built from real elevation data','terrain modeled on real elevation data'),('実際の標高データで作った地形','実際の標高データをもとに作った地形'),('用真实海拔数据制作的地形','参照真实海拔数据制作的地形')]:
        P.rep(a, b, need=False)
    P.rep('content="실제 고도 데이터로 만든 ', 'content="실제 지형을 본떠 만든 ', need=False)


def patch_loader(P, m, mts, data):
    patch_honest(P)
    P.rep('</style>', CSS + '</style>', 1)
    prof, tot = profile(m, data)
    P.rep('<div class="status"><span id="ldMsg">산길을 여는 중</span><b id="ldAlt">해발 0m</b></div>\n</div>\n',
          '<div class="status"><span id="ldMsg">산길을 여는 중</span><b id="ldAlt">해발 0m</b></div>\n'
          + brand_html(mts) + mtn_html(m, prof, tot) + '\n</div>\n', 1)
    # 진행 표시 감싸기: 오프닝 스크립트가 __ldProgress 를 만든 다음
    P.rep("  window.__ldProgress(0.02);\n", "  window.__ldProgress(0.02);\n", 1)
    i = P.t.index("  window.__ldProgress(0.02);\n"); j = P.t.index('</script>', i) + len('</script>\n')
    P.t = P.t[:j] + JS.replace('__ID__', m['id']) + P.t[j:]
    # 계절·식생에 맞는 문구 (나무 없는 산에 '단풍 숲'이 뜨던 것)
    P.rep("await ldStep('단풍 숲을 심는 중', 0.5);",
          "await ldStep(BIO.dens < 0.05 ? '바위와 자갈길을 다듬는 중' : SEASON === 'autumn' ? '단풍 숲을 심는 중' : '숲을 심는 중', 0.5);", 1)
    for head, msg, f in STEPS:
        k = P.t.find('\n' + head)
        if k < 0: print(f'  [loader] 단계 머리말 없음: {head[:30]}'); continue
        P.t = P.t[:k + 1] + f"await ldStep('{msg}', {f});\n" + P.t[k + 1:]
