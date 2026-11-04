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
  addEventListener('appinstalled', () => { toast(T_('설치했어요 · 바탕화면이나 Dock의 능선 아이콘으로 열어 보세요'), 4); if(box) box.hidden = true; });
  // 설치한 앱으로 열면: 첫 클릭에서 전체 화면 (브라우저 규칙상 클릭이 있어야 해요)
  if(isApp() && DESK){ const go = () => { if(!document.fullscreenElement && document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(()=>{}); };
    addEventListener('pointerdown', go, {once:true, capture:true}); addEventListener('keydown', go, {once:true, capture:true}); }
}
"""

PC_FIX = [
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
    P.rep("window.__game = {", PC_JS + "window.__game = {", 1)


def write_sw(out):
    open(os.path.join(out, 'sw.js'), 'w').write(SW_JS)
