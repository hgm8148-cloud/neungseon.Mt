"""PC(윈도우·맥)에 설치 (2026-11-04)

- 크롬·엣지: '💻 PC에 설치' → 브라우저 설치 창 → 바탕화면·시작 메뉴·Dock에 능선 아이콘
- 맥 Safari(17+): 파일 메뉴 → 'Dock에 추가' 안내
- 그 밖의 브라우저(파이어폭스 등): 크롬·엣지에서 열어 달라는 안내
- 설치한 아이콘으로 열면: 첫 클릭(시작 버튼 등)에서 바로 전체 화면으로
- sw.js: 설치 조건을 맞추는 서비스 워커. 늘 인터넷의 최신 파일을 먼저 받고, 끊겼을 때만 저장본을 보여 줘요.
"""
import os

SW_JS = r"""// 능선 서비스 워커 (pipeline/app_patch.py): 늘 최신 파일을 먼저, 인터넷이 끊겼을 때만 저장본
const C = 'neungseon-v1';
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', e => {
  const r = e.request; if(r.method !== 'GET') return;
  const u = new URL(r.url); if(u.origin !== location.origin) return;
  e.respondWith(fetch(r).then(res => { if(res.ok && (r.mode === 'navigate' || /\.(png|jpg|webmanifest)$/.test(u.pathname))){ const cp = res.clone(); caches.open(C).then(c => c.put(r, cp)); } return res; })
    .catch(() => caches.match(r).then(m => m || Response.error())));
});
"""

PC_SHEET = r"""
<div id="pcSheet" class="panel" hidden><div class="card aiCard"><button class="pX" id="pcX" aria-label="닫기">✕</button>
  <h3 class="aiH">PC에 능선 설치하기</h3>
  <ol class="aiSteps" id="pcChrome" hidden>
    <li>주소창 오른쪽 끝의 설치 아이콘(모니터에 ↓ 모양)을 눌러요. 안 보이면 ⋮ 메뉴 → ‘전송, 저장, 공유’ → ‘페이지를 앱으로 설치’를 눌러요.</li>
    <li>‘설치’를 누르면 바탕화면·시작 메뉴(맥은 Dock·응용 프로그램)에 능선 아이콘이 생겨요.</li>
    <li>아이콘으로 열면 주소창 없이 열리고, 시작을 누르면 전체 화면이 돼요.</li>
  </ol>
  <ol class="aiSteps" id="pcEdge" hidden>
    <li>주소창 오른쪽의 앱 설치 아이콘을 누르거나, ⋯ 메뉴 → ‘앱’ → ‘이 사이트를 앱으로 설치’를 눌러요.</li>
    <li>‘설치’를 누르면 바탕화면·시작 메뉴에 능선 아이콘이 생겨요.</li>
    <li>아이콘으로 열면 주소창 없이 열리고, 시작을 누르면 전체 화면이 돼요.</li>
  </ol>
  <ol class="aiSteps" id="pcSafari" hidden>
    <li>화면 맨 위 메뉴 막대에서 ‘파일’ → ‘Dock에 추가’를 눌러요. (macOS Sonoma 이상)</li>
    <li>‘추가’를 누르면 Dock과 응용 프로그램 폴더에 능선 아이콘이 생겨요.</li>
    <li>아이콘으로 열면 주소창 없이 열리고, 시작을 누르면 전체 화면이 돼요.</li>
  </ol>
  <p class="aiNote" id="pcOther" hidden>이 브라우저는 앱 설치를 지원하지 않아요. 크롬이나 엣지(맥은 Safari)로 neungseon.com 을 열고 다시 눌러 주세요.</p>
  <p class="aiNote">설치한 앱과 브라우저는 기록을 따로 저장해요. 구글로 로그인하면 산행 기록이 이어져요.</p>
  <button class="btn" id="pcOk" type="button">알겠어요</button>
</div></div>"""

PC_JS = r"""
// ---------- PC에 설치 + 설치한 앱은 전체 화면으로 (pipeline/app_patch.py) ----------
{ const T_ = window.T || (x=>x), UA = navigator.userAgent, box = $('appInst');
  const DESK = !document.body.classList.contains('touch') && !IS_IOS && !/Android|Mobile/i.test(UA);
  const isApp = () => !!(window.matchMedia && (matchMedia('(display-mode: standalone)').matches || matchMedia('(display-mode: fullscreen)').matches || matchMedia('(display-mode: window-controls-overlay)').matches));
  if(isApp()) document.body.classList.add('standalone');
  if(DESK) document.body.classList.add('desk');
  try{ if('serviceWorker' in navigator && location.protocol === 'https:') navigator.serviceWorker.register('sw.js').catch(()=>{}); }catch(e){}
  let pev = null; addEventListener('beforeinstallprompt', e => { pev = e; });
  if(DESK && box && !isApp()){
    box.hidden = false; const b = $('aiBtn'); b.textContent = T_('💻 PC에 설치'); $('aiTxt').textContent = T_('바탕화면 아이콘으로 바로, 전체 화면으로 즐겨요');
    const sh = $('pcSheet'), close = () => { sh.hidden = true; };
    $('pcX').onclick = close; $('pcOk').onclick = close; sh.addEventListener('click', e => { if(e.target === sh) close(); });
    b.onclick = async (ev) => { ev.stopImmediatePropagation();
      if(pev){ const e = pev; pev = null; e.prompt(); try{ const c = await e.userChoice; if(c && c.outcome === 'accepted') return; }catch(_){} }
      const edge = /Edg\//.test(UA), chrome = /Chrome\//.test(UA) && !edge && !/OPR\//.test(UA), safari = /Safari\//.test(UA) && !/Chrome|Chromium|Edg/.test(UA) && /Macintosh/.test(UA);
      $('pcChrome').hidden = !chrome; $('pcEdge').hidden = !edge; $('pcSafari').hidden = !safari; $('pcOther').hidden = chrome || edge || safari;
      sh.hidden = false; };
    // 기존(모바일용) 버튼 처리보다 먼저 받도록 캡처 단계에서
    b.addEventListener('click', b.onclick, true);
  }
  // 설치 유도 버튼을 여러 곳에: 시작 창 '능선' 제목 오른쪽 + 게임 메뉴 지도 아이콘 옆 (누르면 위 설치 버튼과 같은 동작)
  if(box && !box.hidden){ const go = () => $('aiBtn').click(), lab = $('aiBtn').textContent;
    const h = document.querySelector('#start .card h1');
    if(h){ const t = document.createElement('button'); t.type = 'button'; t.id = 'aiTop'; t.className = 'aiTop'; t.textContent = lab; t.onclick = go;
      const sm = h.querySelector('small'); h.insertBefore(t, sm); }
    const bm = $('bMap');
    if(bm){ const d = document.createElement('button'); d.className = 'ib'; d.id = 'bInst'; d.title = lab.replace(/^\S+\s/, ''); d.setAttribute('aria-label', d.title);
      d.innerHTML = '<svg viewBox="0 0 24 24"><path d="M12 4v11M7.5 10.5 12 15l4.5-4.5M5 19.5h14"/></svg>'; d.onclick = go; bm.after(d); }
  }
  addEventListener('appinstalled', () => { toast(T_('설치했어요 · 바탕화면이나 Dock의 능선 아이콘으로 열어 보세요'), 4); if(box) box.hidden = true; ['aiTop','bInst'].forEach(i => { const e = $(i); if(e) e.remove(); }); });
  // 설치한 앱으로 열면: 첫 클릭에서 전체 화면 (브라우저 규칙상 클릭이 있어야 해요)
  if(isApp() && DESK){ const go = () => { if(!document.fullscreenElement && document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(()=>{}); };
    addEventListener('pointerdown', go, {once:true, capture:true}); addEventListener('keydown', go, {once:true, capture:true}); }
}
"""

PC_FIX = [
    ['천천히', 'Slow', 'ゆっくり', '慢走', 'Langsam', 'Lent', 'Piano', 'Despacio', 'बिस्तारै', 'Polepole'],
    ['빠르게', 'Fast', '速く', '快走', 'Schnell', 'Rapide', 'Veloce', 'Rápido', 'छिटो', 'Haraka'],
    ['오르는 중', 'Climbing', '登っています', '上山中', 'Im Aufstieg', 'En montée', 'In salita', 'Subiendo', 'उक्लँदै', 'Inapanda'],
    ['내려가는 중', 'Descending', '下っています', '下山中', 'Im Abstieg', 'En descente', 'In discesa', 'Bajando', 'झर्दै', 'Inashuka'],
    ['등산', 'Up', '登り', '上山', 'Aufstieg', 'Montée', 'Salita', 'Subida', 'उकालो', 'Kupanda'],
    ['하산', 'Down', '下り', '下山', 'Abstieg', 'Descente', 'Discesa', 'Bajada', 'ओरालो', 'Kushuka'],
    ['💻 PC에 설치', '💻 Install on PC', '💻 PCにインストール', '💻 安装到电脑', '💻 Auf dem PC installieren', '💻 Installer sur PC', '💻 Installa sul PC', '💻 Instalar en el PC', '💻 PC मा इन्स्टल गर्नुहोस्', '💻 Sakinisha kwenye PC'],
    ['바탕화면 아이콘으로 바로, 전체 화면으로 즐겨요', 'Open it from a desktop icon and play full screen', 'デスクトップのアイコンからすぐ、全画面で', '从桌面图标直接打开，全屏畅玩', 'Direkt per Desktop-Symbol öffnen und im Vollbild spielen', 'Ouvrez-le depuis une icône du bureau, en plein écran', 'Aprilo da un’icona sul desktop, a schermo intero', 'Ábrelo desde un icono del escritorio, a pantalla completa', 'डेस्कटप आइकनबाट सिधै, पूरा स्क्रिनमा', 'Fungua kutoka kwenye aikoni ya eneo-kazi, skrini nzima'],
    ['PC에 능선 설치하기', 'Install 능선 on your computer', 'PCに능선をインストール', '在电脑上安装 능선', '능선 auf dem Computer installieren', 'Installer 능선 sur l’ordinateur', 'Installa 능선 sul computer', 'Instala 능선 en el ordenador', 'कम्प्युटरमा 능선 इन्स्टल गर्ने', 'Sakinisha 능선 kwenye kompyuta'],
    ['설치했어요 · 바탕화면이나 Dock의 능선 아이콘으로 열어 보세요', 'Installed · open it from the 능선 icon on your desktop or Dock', 'インストールしました · デスクトップやDockの능선アイコンから開いてください', '已安装 · 请从桌面或 Dock 上的 능선 图标打开', 'Installiert · öffne es über das 능선-Symbol auf dem Desktop oder im Dock', 'Installé · ouvrez-le depuis l’icône 능선 du bureau ou du Dock', 'Installato · aprilo dall’icona 능선 sul desktop o nel Dock', 'Instalado · ábrelo desde el icono de 능선 en el escritorio o el Dock', 'इन्स्टल भयो · डेस्कटप वा Dock को 능선 आइकनबाट खोल्नुहोस्', 'Imesakinishwa · ifungue kutoka kwenye aikoni ya 능선 kwenye eneo-kazi au Dock'],
    ['이 브라우저는 앱 설치를 지원하지 않아요. 크롬이나 엣지(맥은 Safari)로 neungseon.com 을 열고 다시 눌러 주세요.', 'This browser can’t install apps. Open neungseon.com in Chrome or Edge (Safari on Mac) and try again.', 'このブラウザはアプリのインストールに対応していません。Chrome か Edge(Macは Safari)で neungseon.com を開いて、もう一度押してください。', '此浏览器不支持安装应用。请用 Chrome 或 Edge（Mac 用 Safari）打开 neungseon.com 后再试。', 'Dieser Browser kann keine Apps installieren. Öffne neungseon.com in Chrome oder Edge (auf dem Mac in Safari) und versuche es erneut.', 'Ce navigateur ne peut pas installer d’applications. Ouvrez neungseon.com dans Chrome ou Edge (Safari sur Mac) et réessayez.', 'Questo browser non può installare app. Apri neungseon.com in Chrome o Edge (Safari su Mac) e riprova.', 'Este navegador no puede instalar apps. Abre neungseon.com en Chrome o Edge (Safari en Mac) y vuelve a intentarlo.', 'यो ब्राउजरले एप इन्स्टल गर्न सक्दैन। Chrome वा Edge (Mac मा Safari) मा neungseon.com खोलेर फेरि थिच्नुहोस्।', 'Kivinjari hiki hakiwezi kusakinisha programu. Fungua neungseon.com kwenye Chrome au Edge (Safari kwenye Mac) ujaribu tena.'],
    ['설치한 앱과 브라우저는 기록을 따로 저장해요. 구글로 로그인하면 산행 기록이 이어져요.', 'The installed app and the browser keep separate records. Sign in with Google to carry your hikes over.', 'インストールしたアプリとブラウザは記録を別々に保存します。Googleでログインすると記録が引き継がれます。', '已安装的应用和浏览器分开保存记录。用 Google 登录即可同步登山记录。', 'App und Browser speichern getrennt. Melde dich mit Google an, um deine Touren mitzunehmen.', 'L’app et le navigateur enregistrent séparément. Connectez-vous avec Google pour retrouver vos randonnées.', 'L’app e il browser salvano separatamente. Accedi con Google per ritrovare le tue escursioni.', 'La app y el navegador guardan por separado. Inicia sesión con Google para conservar tus rutas.', 'एप र ब्राउजरले छुट्टाछुट्टै रेकर्ड राख्छन्। Google बाट लगइन गरे पदयात्रा रेकर्ड जोडिन्छ।', 'Programu na kivinjari huhifadhi rekodi tofauti. Ingia kwa Google kuendeleza safari zako.'],
    ['알겠어요', 'Got it', 'わかりました', '知道了', 'Verstanden', 'Compris', 'Ho capito', 'Entendido', 'बुझें', 'Sawa'],
]


def patch_app(P, m):
    P.rep('<div id="adminLogin" class="panel" hidden>', PC_SHEET.lstrip('\n') + '\n<div id="adminLogin" class="panel" hidden>', 1)
    # 설치한 PC 앱은 창 모드로 열릴 수 있어서 전체 화면 버튼은 남겨요 (휴대폰 앱만 숨김)
    P.rep('body.standalone #bFull{display:none!important}', 'body.standalone:not(.desk) #bFull{display:none!important}', need=False)
    P.rep('</style>', '#start .card h1 .aiTop{display:inline-block;vertical-align:middle;margin:0 0 6px 12px;padding:6px 13px;border-radius:999px;border:1px solid rgba(255,214,150,.55);background:rgba(255,214,150,.16);color:inherit;font-family:var(--body);font-size:13px;font-weight:600;letter-spacing:0;cursor:pointer}#start .card h1 .aiTop:hover{background:rgba(255,214,150,.3)}\n</style>', 1)
    P.rep("window.__game = {", PC_JS + "window.__game = {", 1)
    patch_dir(P)
    patch_quick(P)


def write_sw(out):
    open(os.path.join(out, 'sw.js'), 'w').write(SW_JS)


DIR_CSS = "#walkPill .dirSeg{display:inline-flex;padding:2px;margin-right:6px;border-radius:999px;background:rgba(0,0,0,.18)}#walkPill .dirSeg button{padding:6px 12px;background:transparent}#walkPill .dirSeg button.on{background:rgba(255,255,255,.22);font-weight:700}\n"

DIR_JS = r"""
// ---------- 탐방로 방향: 등산 / 하산 (pipeline/app_patch.py) ----------
function setTrailDir(down){
  if(!st.started){ toast('먼저 산행을 시작해 주세요', 2); return; }
  if(down && !st.descending){ if(st.camp && typeof endCamp === 'function') endCamp(true);
    const ci = nearTrail(st.x, st.z, 1).i; let k = 0; while(k < WPS.length && WPS[k].i <= ci + 10) k++;
    st.descending = true; st.dcp = Math.max(1, k); st.down0 = { sec: st.gameSec, walked: st.walked }; st.sitting = false; st.view = null; }
  else if(!down && st.descending){ st.descending = false; }
  st.goal = null; refreshWalk(); canvas.focus(); }
$('bUp').onclick = () => setTrailDir(false); $('bDown').onclick = () => setTrailDir(true);
"""


def patch_dir(P):
    P.rep('<div id="walkPill" class="glass pill"><span id="walkTxt">', '<div id="walkPill" class="glass pill"><span class="dirSeg"><button id="bUp" class="on" type="button">등산</button><button id="bDown" type="button">하산</button></span><span id="walkTxt">', 1)
    P.rep("document.body.classList.toggle('walking', !!st.auto); }", "document.body.classList.toggle('walking', !!st.auto); $('bUp').classList.toggle('on', !d); $('bDown').classList.toggle('on', !!d); }", 1)
    P.rep('</style>', DIR_CSS + '#walkPill,#walkPill span,#walkPill button{white-space:nowrap}\n</style>', 1)
    # 짧고 직관적인 글자: 버튼은 천천히/빠르게, 상태는 오르는 중/내려가는 중 (줄바꿈 없이)
    P.rep('<button id="bSlow" class="pz">천천히 걷기</button><button id="bFast" class="pz">빠르게 걷기</button>', '<button id="bSlow" class="pz">천천히</button><button id="bFast" class="pz">빠르게</button>', 1)
    P.rep("$('walkTxt').textContent = st.auto ? (fast ? (d?'빠르게 내려가는 중':'빠르게 걷는 중') : (d?'천천히 내려가는 중':'천천히 걷는 중')) : (d?'하산길을 따라':'탐방로를 따라');",
          "$('walkTxt').textContent = st.auto ? (d?'내려가는 중':'오르는 중') : (d?'하산길을 따라':'탐방로를 따라');", 1)
    P.rep("$('bSlow').textContent = d ? '천천히 내려가기' : '천천히 걷기'; $('bFast').textContent = d ? '빠르게 내려가기' : '빠르게 걷기';",
          "$('bSlow').textContent = '천천히'; $('bFast').textContent = '빠르게';", 1)
    P.rep("window.__game = {", DIR_JS + "window.__game = {", 1)


# 휴대폰: 버튼 숨기기·전체 화면을 메뉴 밖 오른쪽 위에, 걷기 막대는 작게
QUICK_CSS = (
  "#quickR{display:none}"
  "body.touch #quickR{display:flex;flex-direction:column;gap:6px;position:fixed;z-index:6;right:max(10px,env(safe-area-inset-right,0px));top:calc(60px + env(safe-area-inset-top,0px))}"
  "body.touch #quickR .ib{width:38px;height:38px;border-radius:50%;background:rgba(20,22,28,.42);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,.14)}"
  "body.touch #quickR .ib svg{width:19px;height:19px}"
  "body.touch.clean #quickR{top:calc(10px + env(safe-area-inset-top,0px))}body.touch.clean #quickR #qFs{display:none}body.touch.clean #quickR .ib{opacity:.6}"
  "body.touch.clean #cleanOff{display:none!important}"
  "body.touch #quickR .eyeOff{display:none}body.touch.clean #quickR .eyeOn{display:none}body.touch.clean #quickR .eyeOff{display:block}"
  "body.standalone.ios #qFs{display:none}"
  "body.touch #walkPill .dirSeg{display:inline-flex!important;margin-right:4px}body.touch #walkPill .dirSeg button:not(.on){display:none}"
  "body.touch #walkPill .dirSeg button{padding:6px 8px}body.touch #walkPill .dirSeg{margin-right:2px;padding:0}"
  "body.touch.walking #walkPill #walkTxt{display:none}"
  "body.touch #walkPill button{padding:6px 8px;font-size:11.5px}body.touch #walkPill .pz+.pz,body.touch.walking #walkPill #bWalk{margin-left:2px}"
  "body.touch.walking #walkPill .pz:not(.on){display:none}body.touch.walking #walkPill #bWalk{margin-left:4px}"
  "@media (orientation:portrait){body.touch #bottom#bottom{bottom:calc(30px + env(safe-area-inset-bottom,0px));padding:0 64px 0 136px;align-items:center}body.touch #walkPill{padding:2px;max-width:100%}}"
  "\n")

QUICK_HTML = ('<div id="quickR">'
  '<button class="ib" id="qEye" type="button" aria-label="버튼 숨기기/보이기" title="버튼 숨기기/보이기">'
  '<svg class="eyeOn" viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="14" rx="2.5"/><path d="M3.5 9h17" opacity=".5"/><path d="M8 14h8" stroke-dasharray="2 2"/></svg>'
  '<svg class="eyeOff" viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="14" rx="2.5"/><path d="M3.5 9h17"/><path d="M7 12.5h10M7 15.5h6"/></svg></button>'
  '<button class="ib" id="qFs" type="button" aria-label="전체 화면" title="전체 화면"><svg viewBox="0 0 24 24"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg></button>'
  '</div>\n')

QUICK_JS = r"""
// ---------- 휴대폰 빠른 버튼 (pipeline/app_patch.py) ----------
{ if(IS_IOS) document.body.classList.add('ios');
  $('qEye').onclick = (e) => { e.stopPropagation(); toggleClean(); };
  $('qFs').onclick = (e) => { e.stopPropagation(); toggleFull(); };
  // 휴대폰에선 등산/하산을 버튼 하나로: 누를 때마다 바뀌어요
  const flip = (e) => { if(!document.body.classList.contains('touch')) return; e.stopImmediatePropagation(); setTrailDir(!st.descending); };
  $('bUp').addEventListener('click', flip, true); $('bDown').addEventListener('click', flip, true);
  // 걷는 중엔 지금 속도 버튼 하나만 보여요: 누르면 다른 속도로 바뀌어요
  const pace = (e) => { const b = e.currentTarget; if(!document.body.classList.contains('touch') || !st.auto || !b.classList.contains('on')) return; e.stopImmediatePropagation(); (b.id === 'bSlow' ? $('bFast') : $('bSlow')).click(); };
  $('bSlow').addEventListener('click', pace, true); $('bFast').addEventListener('click', pace, true);
}
"""


def patch_quick(P):
    P.rep('<div id="toast" class="hud glass pill"></div>', QUICK_HTML + '<div id="toast" class="hud glass pill"></div>', 1)
    P.rep('</style>', QUICK_CSS + '</style>', 1)
    P.rep("window.__game = {", QUICK_JS + "window.__game = {", 1)


# ---------- 걷기 단축키 (2026-11-05 승연): Z 천천히 · X 빠르게 · C 멈추기 ----------
def patch_walk_keys(P, m):
    P.rep("  if(e.code==='KeyF') toggleAuto();",
          "  if(e.code==='KeyF') toggleAuto();\n"
          "  if(e.code==='KeyZ' || e.code==='KeyX'){ PACE = e.code==='KeyZ' ? 1 : 2; store.set('pace', PACE); st.goal = null; if(!st.auto) toggleAuto(); else refreshWalk(); }\n"
          "  if(e.code==='KeyC'){ st.goal = null; try{ goalRing.visible = false; }catch(_){} try{ window.__SIDE && window.__SIDE.stop(); }catch(_){} if(st.auto){ st.auto = false; refreshWalk(); } }", 1)
    P.rep("<kbd>F</kbd> 천천히 걷기", "<kbd>Z</kbd> 천천히 · <kbd>X</kbd> 빠르게 · <kbd>C</kbd> 멈추기", need=False)


# ---------- 아래쪽 버튼 묶음 접기 + PC 단축키 표시 (2026-11-05 승연) ----------
# - 걷기 막대·행동 버튼(·정상 메뉴)을 따로 접었다 펼 수 있어요. 손잡이 버튼 또는 B 키. 상태는 기억해요.
# - PC: 등산(T)·하산(G)·천천히(Z)·빠르게(X)·멈추기(C) 버튼에 단축키를 작게 표시해요
BOT_CSS = r'''
#botMin{align-self:center;border:0;cursor:pointer;font:inherit;font-size:11.5px;line-height:1;padding:4px 12px 5px;border-radius:999px;color:var(--ink,#eee);opacity:.75;display:flex;align-items:center;gap:6px}
#botMin:hover{opacity:1}#botMin svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;transition:transform .2s}
#botMin .l{display:none}
body.botMin #botMin{opacity:.92;padding:6px 14px}body.botMin #botMin .l{display:inline}body.botMin #botMin svg{transform:rotate(180deg)}
body.botMin #walkPill,body.botMin #actions,body.botMin #campBar,body.botMin #summitBtn{display:none!important}
body.touch #botMin{display:none!important}
body:not(.touch) #walkPill button[data-k]::after{content:attr(data-k);margin-left:5px;font-size:10px;font-weight:600;opacity:.55;padding:1px 4px;border-radius:4px;border:1px solid currentColor;line-height:1;vertical-align:1px}
'''
BOT_JS = r'''
// ---------- 아래쪽 버튼 접기 (pipeline/app_patch.py) ----------
{ const b = $('botMin'); const set = v => { document.body.classList.toggle('botMin', v); store.set('botMin', v ? 1 : 0); b.title = v ? '버튼 펼치기 (B)' : '버튼 접기 (B)'; };
  b.onclick = e => { e.stopPropagation(); set(!document.body.classList.contains('botMin')); canvas.focus(); };
  set(!!store.get('botMin', 0)); window.__botMin = set;
  [['bUp','T'],['bDown','G'],['bSlow','Z'],['bFast','X'],['bWalk','C']].forEach(([id, k]) => { const e = $(id); if(e) e.dataset.k = k; }); }
'''


def patch_bottom_min(P, m):
    P.rep('</style>', BOT_CSS + '</style>', 1)
    P.rep('<div id="bottom" class="hud">\n', '<div id="bottom" class="hud">\n  <button id="botMin" class="glass" type="button" title="버튼 접기 (B)"><svg viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg><span class="l">버튼 펼치기</span></button>\n', 1)
    P.rep("  if(e.code==='KeyF') toggleAuto();",
          "  if(e.code==='KeyF') toggleAuto();\n"
          "  if(e.code==='KeyT' && st.descending) setTrailDir(false);\n"
          "  if(e.code==='KeyG' && !st.descending) setTrailDir(true);\n"
          "  if(e.code==='KeyB' && window.__botMin) window.__botMin(!document.body.classList.contains('botMin'));", 1)
    P.rep("<kbd>Z</kbd> 천천히 · <kbd>X</kbd> 빠르게 · <kbd>C</kbd> 멈추기", "<kbd>T</kbd> 등산 · <kbd>G</kbd> 하산 · <kbd>Z</kbd> 천천히 · <kbd>X</kbd> 빠르게 · <kbd>C</kbd> 멈추기 · <kbd>B</kbd> 버튼 접기", need=False)
    P.rep("window.__game = {", BOT_JS + "window.__game = {", 1)
