"""아이폰(iOS Safari·홈 화면 앱) 최적화.
- 주소창이 접히고 펴질 때 실제 보이는 높이(--vh)로 카드·패널 높이 맞춤
- 화면을 돌린 뒤 늦게 바뀌는 크기를 한 번 더 맞춤
- 페이지 전체가 확대·튕김·길게 눌러 선택되는 것 막기 (게임 화면 두 손가락 확대는 그대로)
- 입력칸 글씨 16px: 누를 때 화면이 저절로 확대되지 않게, 키보드 닫히면 화면 제자리로
- 소리: 다른 앱 음악과 섞이고 무음 스위치를 따름, 백그라운드에서 멈췄다가 돌아오면 다시 재생
- 홈 화면 앱(이미 전체 화면)에서는 전체 화면 버튼 숨김"""

IOS_CSS = r"""
html{touch-action:manipulation;-webkit-text-size-adjust:100%}
html,body{overscroll-behavior:none}
body{-webkit-tap-highlight-color:transparent;-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}
input,textarea{-webkit-user-select:text;user-select:text;-webkit-touch-callout:default}
body.ios .field input,body.ios #adminPanel .adMsg input,body.ios #adPw{font-size:16px}
body.standalone #bFull{display:none!important}
"""

IOS_JS = r"""
// ---------- 아이폰 최적화 ----------
const IS_IOS = /iP(hone|ad|od)/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
if(IS_IOS) document.body.classList.add('ios');
if(navigator.standalone || (window.matchMedia && matchMedia('(display-mode: standalone)').matches)) document.body.classList.add('standalone');
{ const vv = window.visualViewport;
  const setVH = () => document.documentElement.style.setProperty('--vh', Math.round(vv ? vv.height : innerHeight) + 'px');
  const reSize = () => { camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); setVH(); };
  setVH(); addEventListener('resize', setVH); if(vv) vv.addEventListener('resize', setVH);
  addEventListener('orientationchange', () => { setTimeout(reSize, 150); setTimeout(reSize, 600); });
  if(IS_IOS){
    document.addEventListener('gesturestart', e => e.preventDefault());
    document.addEventListener('gesturechange', e => e.preventDefault());
    document.addEventListener('focusout', e => { if(e.target && /^(INPUT|TEXTAREA)$/.test(e.target.tagName)) setTimeout(() => { if(!document.activeElement || !/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) window.scrollTo(0, 0); }, 60); });
  }
  try{ if(navigator.audioSession) navigator.audioSession.type = 'ambient'; }catch(e){}
  const wakeAudio = () => { if(audio && audio.ac.state !== 'running' && !document.hidden) audio.ac.resume().catch(()=>{}); };
  for(const t of ['touchend', 'pointerup', 'keydown']) addEventListener(t, wakeAudio, {passive:true});
  document.addEventListener('visibilitychange', () => { if(!audio) return; if(document.hidden) audio.ac.suspend().catch(()=>{}); else wakeAudio(); });
  addEventListener('pageshow', wakeAudio);
}
"""


def patch_ios(P, m):
    P.rep("</style>", IOS_CSS + "</style>", 1)
    P.rep("100vh", "var(--vh,100vh)")
    P.rep("window.__game = {", IOS_JS + "window.__game = {", 1)


# ---------- 앱으로 설치 (아이폰: 홈 화면에 추가 안내 / 안드로이드·PC 크롬: 설치 창) ----------
INST_HTML = r"""
    <div id="appInst" hidden><button id="aiBtn" class="gBtn" type="button">📲 앱으로 설치</button><span id="aiTxt">홈 화면에 두고 앱처럼 꽉 찬 화면으로 즐겨요</span></div>"""

INST_SHEET = r"""
<div id="aiSheet" class="panel" hidden><div class="card aiCard"><button class="pX" id="aiX" aria-label="닫기">✕</button>
  <h3 class="aiH">아이폰에 앱으로 설치하기</h3>
  <ol class="aiSteps" id="aiSafari">
    <li><span>Safari 주소창 옆 <b>공유 버튼</b></span><svg class="aiIc" viewBox="0 0 24 24"><path d="M12 3v12M7.5 7.5 12 3l4.5 4.5M6 11H5v10h14V11h-1"/></svg><span>을 눌러요. 안 보이면 <b>⋯</b> 버튼을 먼저 눌러요.</span></li>
    <li><span>목록을 내려 <b>홈 화면에 추가</b>를 눌러요.</span></li>
    <li><span><b>웹 앱으로 열기</b>가 켜져 있으면 그대로 두고 <b>추가</b>를 눌러요.</span></li>
    <li><span>홈 화면의 <b>능선</b> 아이콘으로 열면 주소창 없이 꽉 찬 화면이에요.</span></li>
  </ol>
  <p class="aiNote" id="aiOther" hidden>카카오톡·네이버 같은 앱 안에서 연 화면에서는 설치할 수 없어요. 오른쪽 위(또는 아래) 메뉴에서 <b>Safari로 열기</b>를 누른 뒤 다시 해 주세요.</p>
  <p class="aiNote">앱과 Safari는 기록을 따로 저장해요. 구글로 로그인하면 산행 기록이 앱으로 이어져요.</p>
  <button class="btn" id="aiOk" type="button">알겠어요</button>
</div></div>"""

INST_CSS = r"""
#appInst{display:flex;align-items:center;gap:10px;margin-top:10px;font-size:12.5px;opacity:.85;flex-wrap:wrap}#appInst[hidden]{display:none}
#aiSheet{z-index:40}.aiCard{max-width:400px;padding:20px 22px 18px;max-height:calc(var(--vh,100vh) - 32px);overflow:auto}
.aiH{margin:0 30px 10px 0;font-size:18px}.aiSteps{margin:0 0 10px;padding-left:22px;font-size:14.5px;line-height:1.55}.aiSteps li{margin:7px 0}
.aiIc{width:20px;height:20px;vertical-align:-4px;margin:0 3px;fill:none;stroke:#2f7cf6;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.aiNote{font-size:12.5px;opacity:.75;margin:8px 0}#aiSheet .btn{width:100%;margin-top:6px}
"""

INST_JS = r"""
// ---------- 앱으로 설치 ----------
{ const T_ = window.T || (x=>x), UA = navigator.userAgent, box = $('appInst'), sheet = $('aiSheet');
  const standalone = document.body.classList.contains('standalone');
  const inApp = /KAKAOTALK|NAVER\(|Instagram|FBAN|FBAV|Line\/|DaumApps|everytimeApp|Whale\/.*Mobile.*inapp/i.test(UA);
  let promptEv = null;
  const show = () => { if(box) box.hidden = standalone || !(IS_IOS || promptEv); };
  addEventListener('beforeinstallprompt', e => { e.preventDefault(); promptEv = e; show(); });
  addEventListener('appinstalled', () => { promptEv = null; if(box) box.hidden = true; toast(T_('설치했어요 · 홈 화면의 능선 아이콘으로 열어 보세요'), 3.5); });
  const close = () => { sheet.hidden = true; };
  $('aiX').onclick = close; $('aiOk').onclick = close; sheet.addEventListener('click', e => { if(e.target === sheet) close(); });
  $('aiBtn').onclick = async () => {
    if(promptEv){ const ev = promptEv; promptEv = null; ev.prompt(); try{ await ev.userChoice; }catch(e){} show(); return; }
    $('aiOther').hidden = !inApp; sheet.hidden = false; };
  show();
  // 아이폰 Safari로 처음 들어온 사람에게 한 번만 살짝 알려 줘요
  if(IS_IOS && !standalone && !inApp && !store.get('aiHint', false)){ store.set('aiHint', true); setTimeout(() => { if(!st.started) toast(T_('📲 앱으로 설치를 누르면 홈 화면에서 바로 열 수 있어요'), 4); }, 2500); }
}
"""

INST_ROWS = [
    ['📲 앱으로 설치', '📲 Install as app', '📲 アプリとして追加', '📲 安装为应用'],
    ['홈 화면에 두고 앱처럼 꽉 찬 화면으로 즐겨요', 'Keep it on your home screen and play full screen like an app', 'ホーム画面に置いて、アプリのように全画面で', '放到主屏幕，像应用一样全屏游玩'],
    ['아이폰에 앱으로 설치하기', 'Install on iPhone', 'iPhoneにアプリとして追加', '在 iPhone 上安装'],
    ['알겠어요', 'Got it', 'わかりました', '知道了'],
    ['설치했어요 · 홈 화면의 능선 아이콘으로 열어 보세요', 'Installed · open it from the 능선 icon on your home screen', 'インストールしました · ホーム画面の「능선」アイコンから開いてください', '已安装 · 请从主屏幕的“능선”图标打开'],
    ['📲 앱으로 설치를 누르면 홈 화면에서 바로 열 수 있어요', '📲 Tap “Install as app” to open it right from your home screen', '📲「アプリとして追加」でホーム画面からすぐ開けます', '📲 点“安装为应用”，就能从主屏幕直接打开'],
    ['앱과 Safari는 기록을 따로 저장해요. 구글로 로그인하면 산행 기록이 앱으로 이어져요.', 'The app and Safari keep separate records. Sign in with Google to carry your hikes over.', 'アプリとSafariは記録を別々に保存します。Googleでログインすると記録が引き継がれます。', '应用和 Safari 分开保存记录。用 Google 登录即可同步登山记录。'],
]


def patch_install(P, m):
    P.rep('<button class="btn" id="go">', INST_HTML.lstrip('\n') + '\n    <button class="btn" id="go">', 1)
    P.rep('<div id="adminLogin" class="panel" hidden>', INST_SHEET.lstrip('\n') + '\n<div id="adminLogin" class="panel" hidden>', 1)
    P.rep("</style>", INST_CSS + "</style>", 1)
    P.rep("window.__game = {", INST_JS + "window.__game = {", 1)
    P.rep('<link rel="apple-touch-icon" href="icon-192.png">', '<link rel="apple-touch-icon" sizes="180x180" href="icon-180.png">', 1)
