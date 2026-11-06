"""조작 간편화 (2026-11-06 승연 '네 제안대로 모두 반영해줘')

1) 휴대폰 걷기 버튼 하나로: 누르면 걷기/멈추기, 길게 누르면 빠르기 바꾸기
2) 휴대폰 행동 버튼: 쉬기·사진만 보이고 나머지는 + 로 펼치기
3) 휴대폰 화면 두 번 톡톡 = 걷기/멈추기
4) (side_patch.py) 걷는 중 숨은 길 카드는 6초 뒤 저절로 닫힘
5) 처음 온 사람에게 조작 안내 카드 3장 (건너뛰기 가능, 한 번만)
6) PC Space 키 = 걷기/멈추기
7) 정상에 도착하면 큰 '하산하기' 버튼

game.template.html 은 고치지 않고 빌드할 때 덧대요.
"""

# 번역: ko, en, ja, zh, de, fr, it, es, ne, sw
UX_ROWS = [
    ['걷기', 'Walk', '歩く', '走', 'Gehen', 'Marcher', 'Cammina', 'Caminar', 'हिँड्नुहोस्', 'Tembea'],
    ['빠르게 걸어요', 'Walking fast', '速く歩きます', '快走', 'Schnell gehen', 'Marche rapide', 'Passo veloce', 'Paso rápido', 'छिटो हिँड्दै', 'Unatembea haraka'],
    ['천천히 걸어요', 'Walking slowly', 'ゆっくり歩きます', '慢走', 'Langsam gehen', 'Marche lente', 'Passo lento', 'Paso lento', 'बिस्तारै हिँड्दै', 'Unatembea polepole'],
    ['누르면 걷기/멈추기, 길게 누르면 빠르기 바꾸기', 'Tap to walk/stop, hold to change pace', 'タップで歩く/止まる、長押しで速さを変更', '点击走/停，长按切换速度', 'Tippen: gehen/stoppen, halten: Tempo ändern', 'Touchez pour marcher/arrêter, maintenez pour changer de rythme', 'Tocca per camminare/fermarti, tieni premuto per cambiare passo', 'Toca para caminar/parar, mantén para cambiar el ritmo', 'थिच्दा हिँड्ने/रोकिने, थिचिराख्दा गति फेर्ने', 'Gusa kutembea/kusimama, shikilia kubadili kasi'],
    ['더 보기', 'More', 'もっと見る', '更多', 'Mehr', 'Plus', 'Altro', 'Más', 'थप', 'Zaidi'],
    ['탐방로를 따라 걸어요', 'Walking along the trail', '登山道に沿って歩きます', '沿着步道走', 'Dem Weg folgen', 'On suit le sentier', 'Si segue il sentiero', 'Siguiendo el sendero', 'बाटो पछ्याउँदै हिँड्दै', 'Unafuata njia'],
    ['🥾 하산하기', '🥾 Head down', '🥾 下山する', '🥾 下山', '🥾 Abstieg', '🥾 Descendre', '🥾 Scendere', '🥾 Bajar', '🥾 ओर्लनुहोस्', '🥾 Shuka'],
    ['건너뛰기', 'Skip', 'スキップ', '跳过', 'Überspringen', 'Passer', 'Salta', 'Omitir', 'छोड्नुहोस्', 'Ruka'],
    ['다음', 'Next', '次へ', '下一步', 'Weiter', 'Suivant', 'Avanti', 'Siguiente', 'अर्को', 'Ifuatayo'],
    ['산행 시작', 'Start hiking', '登山開始', '开始登山', 'Los geht’s', 'C’est parti', 'Si parte', 'A caminar', 'हिँड्न सुरु', 'Anza safari'],
    ['저절로 걷기', 'Auto-walk', '自動で歩く', '自动行走', 'Automatisch gehen', 'Marche automatique', 'Cammino automatico', 'Caminar solo', 'आफैँ हिँड्ने', 'Tembea kiotomatiki'],
    ['직접 걷고 둘러보기', 'Walk and look around', '自分で歩いて見回す', '自己走、四处看', 'Selbst gehen und umsehen', 'Marcher et regarder autour', 'Cammina e guardati intorno', 'Camina y mira alrededor', 'आफैँ हिँड्ने र वरिपरि हेर्ने', 'Tembea na tazama pande zote'],
    ['쉬고, 사진 남기기', 'Rest and take photos', '休んで写真を残す', '休息、拍照留念', 'Rasten und Fotos machen', 'Se reposer et photographier', 'Riposa e scatta foto', 'Descansa y toma fotos', 'आराम र फोटो', 'Pumzika na piga picha'],
    ['Space 키를 누르면 탐방로를 따라 저절로 걸어요', 'Press Space to walk along the trail by itself', 'Space キーで登山道に沿って自動で歩きます', '按 Space 键即可沿步道自动行走', 'Mit der Leertaste folgst du dem Weg automatisch', 'Appuyez sur Espace pour suivre le sentier automatiquement', 'Premi Spazio per seguire il sentiero da solo', 'Pulsa Espacio para seguir el sendero solo', 'Space थिच्दा बाटो पछ्याएर आफैँ हिँडिन्छ', 'Bonyeza Space kufuata njia yenyewe'],
    ['Z 천천히, X 빠르게, C 멈추기', 'Z slow, X fast, C stop', 'Z ゆっくり、X 速く、C 止まる', 'Z 慢走，X 快走，C 停下', 'Z langsam, X schnell, C stopp', 'Z lent, X rapide, C arrêt', 'Z lento, X veloce, C stop', 'Z lento, X rápido, C parar', 'Z बिस्तारै, X छिटो, C रोक्ने', 'Z polepole, X haraka, C simama'],
    ['WASD나 방향키로 직접 걸어요', 'Walk yourself with WASD or the arrow keys', 'WASD か矢印キーで自分で歩きます', '用 WASD 或方向键自己走', 'Mit WASD oder Pfeiltasten selbst gehen', 'Marchez avec ZQSD/WASD ou les flèches', 'Cammina con WASD o le frecce', 'Camina con WASD o las flechas', 'WASD वा तीर कुञ्जीले आफैँ हिँड्नुहोस्', 'Tembea mwenyewe kwa WASD au mishale'],
    ['마우스로 끌면 둘러보고, 땅을 누르면 그곳으로 가요', 'Drag to look around, click the ground to go there', 'ドラッグで見回し、地面をクリックでそこへ移動', '拖动可环顾四周，点击地面即可前往', 'Ziehen zum Umsehen, auf den Boden klicken zum Hingehen', 'Faites glisser pour regarder, cliquez au sol pour y aller', 'Trascina per guardarti intorno, clicca il terreno per andarci', 'Arrastra para mirar, haz clic en el suelo para ir allí', 'तानेर वरिपरि हेर्नुहोस्, जमिनमा थिचेर त्यहाँ जानुहोस्', 'Buruta kutazama, bofya ardhi kwenda huko'],
    ['힘들면 2번으로 쉬고, 5번으로 사진을 찍어요', 'Press 2 to rest when tired, 5 to take a photo', '疲れたら 2 で休み、5 で写真を撮ります', '累了按 2 休息，按 5 拍照', 'Mit 2 rasten, mit 5 fotografieren', '2 pour se reposer, 5 pour une photo', '2 per riposare, 5 per una foto', '2 para descansar, 5 para una foto', 'थाक्दा 2 थिचेर आराम, 5 थिचेर फोटो', 'Bonyeza 2 kupumzika, 5 kupiga picha'],
    ['M 지도, B 버튼 접기', 'M map, B hide buttons', 'M 地図、B ボタンを畳む', 'M 地图，B 收起按钮', 'M Karte, B Tasten einklappen', 'M carte, B replier les boutons', 'M mappa, B comprimi pulsanti', 'M mapa, B ocultar botones', 'M नक्सा, B बटन लुकाउने', 'M ramani, B kunja vitufe'],
    ['아래 걷기 버튼을 누르면 탐방로를 따라 저절로 걸어요', 'Tap the Walk button below to follow the trail by itself', '下の「歩く」ボタンで登山道に沿って自動で歩きます', '点击下方“走”按钮即可沿步道自动行走', 'Tippe unten auf „Gehen“, um dem Weg automatisch zu folgen', 'Touchez « Marcher » en bas pour suivre le sentier', 'Tocca «Cammina» in basso per seguire il sentiero', 'Toca «Caminar» abajo para seguir el sendero', 'तलको हिँड्ने बटन थिच्दा बाटो पछ्याएर आफैँ हिँडिन्छ', 'Gusa kitufe cha Tembea chini kufuata njia'],
    ['길게 누르면 빠르기가 바뀌고, 화면을 두 번 톡톡 눌러도 돼요', 'Hold it to change pace, or double-tap the screen', '長押しで速さが変わり、画面をダブルタップしても OK', '长按可切换速度，也可以双击屏幕', 'Halten ändert das Tempo, oder doppelt auf den Bildschirm tippen', 'Maintenez pour changer de rythme, ou touchez deux fois l’écran', 'Tieni premuto per il passo, o tocca due volte lo schermo', 'Mantén para cambiar el ritmo, o toca dos veces la pantalla', 'थिचिराख्दा गति फेरिन्छ, वा स्क्रिनमा दुई पटक ट्याप गर्नुहोस्', 'Shikilia kubadili kasi, au gusa skrini mara mbili'],
    ['왼쪽 아래 동그라미를 밀어 직접 걸어요', 'Push the circle at bottom left to walk yourself', '左下の丸を動かして自分で歩きます', '推动左下角的圆圈自己走', 'Schiebe den Kreis unten links, um selbst zu gehen', 'Poussez le cercle en bas à gauche pour marcher', 'Sposta il cerchio in basso a sinistra per camminare', 'Mueve el círculo de abajo a la izquierda para caminar', 'तल बायाँको गोलो धकेलेर आफैँ हिँड्नुहोस्', 'Sukuma duara la chini kushoto kutembea'],
    ['화면을 끌면 둘러보고, 땅을 누르면 그곳으로 가요', 'Drag to look around, tap the ground to go there', '画面をドラッグで見回し、地面をタップでそこへ移動', '拖动屏幕环顾四周，点击地面即可前往', 'Ziehen zum Umsehen, Boden antippen zum Hingehen', 'Glissez pour regarder, touchez le sol pour y aller', 'Trascina per guardarti intorno, tocca il terreno per andarci', 'Arrastra para mirar, toca el suelo para ir allí', 'स्क्रिन तानेर हेर्नुहोस्, जमिन थिचेर त्यहाँ जानुहोस्', 'Buruta kutazama, gusa ardhi kwenda huko'],
    ['오른쪽 버튼으로 쉬고 사진을 찍어요', 'Use the buttons on the right to rest and take photos', '右のボタンで休んだり写真を撮ったりします', '用右侧按钮休息和拍照', 'Mit den Tasten rechts rasten und fotografieren', 'Boutons à droite pour se reposer et photographier', 'Pulsanti a destra per riposare e fotografare', 'Botones de la derecha para descansar y hacer fotos', 'दायाँका बटनले आराम र फोटो', 'Vitufe vya kulia kupumzika na kupiga picha'],
    ['+를 누르면 물, 숨 고르기, 인사가 나와요', 'Tap + for water, breathing and greetings', '+ で水・呼吸・あいさつが出ます', '点 + 可喝水、调整呼吸、打招呼', 'Unter + findest du Wasser, Atmen und Grüßen', '+ pour l’eau, la respiration et les saluts', '+ per acqua, respiro e saluti', '+ para agua, respirar y saludar', '+ थिच्दा पानी, सास र अभिवादन देखिन्छ', 'Gusa + kwa maji, kupumua na salamu'],
]

UX_CSS = r'''
#bGo,#downBtn{display:none}body:not(.touch) #actions #aMore{display:none!important}
body.touch #walkPill #bSlow,body.touch #walkPill #bFast,body.touch #walkPill #bWalk{display:none!important}
body.touch #walkPill #bGo{display:inline-flex;flex-direction:column;align-items:center;justify-content:center;min-width:84px;padding:8px 16px 7px;margin-left:4px;font-size:15px;font-weight:800;line-height:1.05;border-radius:999px;border:0;color:#fff;background:linear-gradient(135deg,#3f8a55,#5aa66d);-webkit-touch-callout:none;-webkit-user-select:none;user-select:none;touch-action:manipulation}
body.touch #bGo small{font-size:10px;font-weight:600;opacity:.85;margin-top:2px}
body.touch #bGo .g2{display:none}body.touch.walking #bGo .g1,body.touch.sideFollow #bGo .g1{display:none}body.touch.walking #bGo .g2,body.touch.sideFollow #bGo .g2{display:inline}
body.touch.walking #walkPill #bGo,body.touch.sideFollow #walkPill #bGo{background:linear-gradient(135deg,#a8552e,#c76a3a)}
body.touch #bGo.press{transform:scale(.94)}
body.touch #aMore{display:flex}body.touch #aMore svg{transition:transform .2s}body.touch.actMore #aMore svg{transform:rotate(45deg)}
body.touch:not(.actMore) #actions #aWave,body.touch:not(.actMore) #actions #aWater,body.touch:not(.actMore) #actions #aBreath{display:none}
#downBtn{border:0;padding:12px 26px;font-size:16px;font-weight:800;color:#fff;background:linear-gradient(135deg,rgba(54,120,74,.95),rgba(84,150,98,.95));cursor:pointer;pointer-events:auto;box-shadow:0 8px 24px rgba(0,0,0,.25)}
body.atSummit #downBtn{display:inline-flex}body.camping #downBtn,body.inSummit #downBtn,body.botMin #downBtn{display:none!important}
#tut{position:fixed;inset:0;z-index:60;display:flex;align-items:center;justify-content:center;background:rgba(10,12,10,.45);padding:16px}
#tut[hidden]{display:none}
#tut .tc{background:var(--paper,#fbf7ef);color:var(--ink,#2a2620);border-radius:22px;padding:22px 22px 16px;width:min(92vw,360px);text-align:center;box-shadow:0 18px 50px rgba(0,0,0,.4)}
#tut .ti{font-size:38px;line-height:1}#tut b{display:block;font-size:19px;margin:10px 0 8px}
#tut p{font-size:14px;line-height:1.5;margin:4px 0;opacity:.85}
#tut .dots{display:flex;gap:6px;justify-content:center;margin:14px 0 12px}#tut .dots i{width:7px;height:7px;border-radius:50%;background:currentColor;opacity:.2}#tut .dots i.on{opacity:.75}
#tut .row{display:flex;gap:8px;justify-content:space-between}
#tut button{border:0;border-radius:999px;padding:10px 18px;font:inherit;font-size:14px;font-weight:700;cursor:pointer}
#tutSkip{background:transparent;color:inherit;opacity:.6}#tutNext{background:#3f8a55;color:#fff;min-width:110px}
'''

UX_HTML_TUT = ('<div id="tut" hidden><div class="tc"><div class="ti" id="tutI"></div><b id="tutH"></b><p id="tutP1"></p><p id="tutP2"></p>'
               '<div class="dots"><i></i><i></i><i></i></div><div class="row"><button id="tutSkip" type="button">건너뛰기</button><button id="tutNext" type="button">다음</button></div></div></div>\n')

UX_JS = r'''
// ---------- 조작 간편화 (pipeline/ux_patch.py) ----------
{ const touch = () => document.body.classList.contains('touch');
  const following = () => !!(window.__SIDE && window.__SIDE.following);
  const walkToggle = () => { if(following()){ window.__SIDE.stop(); st.auto = false; refreshWalk(); return; } toggleAuto(); };
  window.__walkToggle = walkToggle;
  // 1) 휴대폰 걷기 버튼 하나: 누르면 걷기/멈추기, 길게 누르면 빠르기 바꾸기
  const g = $('bGo'); let lt = 0, long = false;
  const paceLbl = () => { const s = $('goPace'); if(s) s.textContent = PACE > 1.5 ? '빠르게' : '천천히'; };
  const flipPace = () => { PACE = PACE > 1.5 ? 1 : 2; store.set('pace', PACE); refreshWalk(); toast(PACE > 1.5 ? '빠르게 걸어요' : '천천히 걸어요', 1.6); try{ navigator.vibrate && navigator.vibrate(15); }catch(_){} };
  g.addEventListener('pointerdown', e => { long = false; g.classList.add('press'); clearTimeout(lt); lt = setTimeout(() => { long = true; g.classList.remove('press'); flipPace(); }, 520); });
  const up = () => { clearTimeout(lt); g.classList.remove('press'); };
  g.addEventListener('pointerup', up); g.addEventListener('pointercancel', up); g.addEventListener('pointerleave', up);
  g.addEventListener('contextmenu', e => e.preventDefault());
  g.onclick = e => { e.stopPropagation(); if(long){ long = false; return; } walkToggle(); canvas.focus(); };
  window.__goPace = paceLbl; paceLbl();
  // 2) 휴대폰 행동 버튼: + 로 나머지 펼치기
  $('aMore').onclick = e => { e.stopPropagation(); document.body.classList.toggle('actMore'); };
  ['aWater','aBreath'].forEach(id => { const b = $(id); if(b) b.addEventListener('click', () => setTimeout(() => document.body.classList.remove('actMore'), 0)); });
  canvas.addEventListener('pointerdown', () => document.body.classList.remove('actMore'));
  // 7) 정상: 큰 하산하기 버튼
  $('downBtn').onclick = e => { e.stopPropagation(); startDescent(); };
  // 5) 처음 온 사람에게 조작 안내 카드 3장
  const CARDS = () => touch() ? [
      ['🥾', '저절로 걷기', '아래 걷기 버튼을 누르면 탐방로를 따라 저절로 걸어요', '길게 누르면 빠르기가 바뀌고, 화면을 두 번 톡톡 눌러도 돼요'],
      ['🧭', '직접 걷고 둘러보기', '왼쪽 아래 동그라미를 밀어 직접 걸어요', '화면을 끌면 둘러보고, 땅을 누르면 그곳으로 가요'],
      ['📷', '쉬고, 사진 남기기', '오른쪽 버튼으로 쉬고 사진을 찍어요', '+를 누르면 물, 숨 고르기, 인사가 나와요'] ] : [
      ['🥾', '저절로 걷기', 'Space 키를 누르면 탐방로를 따라 저절로 걸어요', 'Z 천천히, X 빠르게, C 멈추기'],
      ['🧭', '직접 걷고 둘러보기', 'WASD나 방향키로 직접 걸어요', '마우스로 끌면 둘러보고, 땅을 누르면 그곳으로 가요'],
      ['📷', '쉬고, 사진 남기기', '힘들면 2번으로 쉬고, 5번으로 사진을 찍어요', 'M 지도, B 버튼 접기'] ];
  const tut = $('tut'); let ti = 0;
  const show = () => { const c = CARDS()[ti]; $('tutI').textContent = c[0]; $('tutH').textContent = c[1]; $('tutP1').textContent = c[2]; $('tutP2').textContent = c[3];
    tut.querySelectorAll('.dots i').forEach((d, k) => d.classList.toggle('on', k === ti)); $('tutNext').textContent = ti === 2 ? '산행 시작' : '다음'; };
  const close = () => { tut.hidden = true; store.set('tut', 1); canvas.focus(); };
  $('tutSkip').onclick = close; $('tutNext').onclick = () => { if(ti >= 2) close(); else { ti++; show(); } };
  window.__tut = () => { ti = 0; show(); tut.hidden = false; for(const k in keys) keys[k] = false; };
  addEventListener('keydown', e => { if(tut.hidden) return; e.stopImmediatePropagation(); e.preventDefault();
    if(e.code === 'Escape') close(); else if(e.code === 'Enter' || e.code === 'Space' || e.code === 'ArrowRight') $('tutNext').click(); }, true);
}
'''

# 3) 두 번 톡톡: 첫 탭(누른 곳으로 가기)을 되돌리고, 그 전 상태 기준으로 걷기/멈추기
DTAP_JS = r'''function clickMove(e){
  if(e.pointerType === 'touch' && !st.camp){ const now = performance.now(), D = clickMove.dt;
    if(D && now - D.t < 380 && Math.hypot(e.clientX - D.x, e.clientY - D.y) < 40){ clickMove.dt = null; st.goal = null; goalRing.visible = false; st.sitting = false; st.breathing = 0;
      try{ window.__SIDE && window.__SIDE.stop(); }catch(_){} st.auto = !D.walking; refreshWalk(); toast(st.auto ? '탐방로를 따라 걸어요' : '멈췄어요', 1.4); return; }
    clickMove.dt = { t: now, x: e.clientX, y: e.clientY, walking: st.auto || !!(window.__SIDE && window.__SIDE.following) }; }
'''


def patch_ux(P, m):
    P.rep('</style>', UX_CSS + '</style>', 1)
    # 1) 걷기 버튼 하나
    P.rep('<button id="bWalk">멈추기</button></div>',
          '<button id="bWalk">멈추기</button><button id="bGo" type="button" title="누르면 걷기/멈추기, 길게 누르면 빠르기 바꾸기"><span class="g1">걷기</span><span class="g2">멈추기</span><small id="goPace"></small></button></div>', 1)
    P.rep("document.body.classList.toggle('walking', !!st.auto);", "document.body.classList.toggle('walking', !!st.auto); if(window.__goPace) window.__goPace();", 1)
    # 2) 행동 버튼 + (사진 뒤)
    P.rep('사진<kbd>5</kbd></button>\n  </div>',
          '사진<kbd>5</kbd></button>\n    <button id="aMore" type="button" title="더 보기" aria-label="더 보기"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>더 보기</button>\n  </div>', 1)
    # 7) 정상 하산 버튼
    P.rep('<button id="summitBtn" class="glass pill">⛰ 정상 메뉴</button>',
          '<button id="summitBtn" class="glass pill">⛰ 정상 메뉴</button>\n  <button id="downBtn" class="glass pill" type="button">🥾 하산하기</button>', 1)
    # 5) 안내 카드
    P.rep('<div id="mapWrap" class="hud glass click">', UX_HTML_TUT + '<div id="mapWrap" class="hud glass click">', 1)
    P.rep("  $('start').hidden = true; st.started = true; canvas.focus(); startAudio(); refreshSound();",
          "  $('start').hidden = true; st.started = true; canvas.focus(); startAudio(); refreshSound();\n"
          "  if(!store.get('tut', 0) && window.__tut) setTimeout(window.__tut, 700);", 1)
    # 3) 두 번 톡톡
    P.rep('function clickMove(e){\n', DTAP_JS, 1)
    # 6) Space = 걷기/멈추기 (F 도 숨은 길 따라 걷기를 멈춰요)
    P.rep("  if(e.code==='KeyF') toggleAuto();", "  if(e.code==='KeyF' || e.code==='Space'){ if(window.__walkToggle) window.__walkToggle(); else toggleAuto(); }", 1)
    P.rep("window.__game = {", UX_JS + "window.__game = {", 1)
