"""2026-11-11 승연 수정 묶음 중 화면 쪽: 사진 공유에 능선 주소 · 휴대폰 지도 버튼 · 휴대폰 화면 다듬기

7) 사진 공유: 사진 오른쪽 아래 글씨 밑에 'neungseon.com'을 함께 새기고, 공유할 때 글과 주소(이 산 페이지)를 같이 보내요.
   파일 공유가 안 되는 브라우저에서도 '공유하기'가 주소라도 보내요.
8) 지도 버튼: 휴대폰은 ⋯ 메뉴 안에 있던 지도 버튼을 밖으로 꺼내 오른쪽 아래 구석에 고정. 누르면 지도가 바로 크게 열리고,
   한 번 더 누르거나 ✕로 닫아요. (PC는 지금처럼 오른쪽 아래 작은 지도를 누르면 크게)
9) 휴대폰 화면
   - 오른쪽 아래 행동 버튼·지도 버튼, 왼쪽 채팅·함께 버튼을 같은 둥근 모양으로 맞추고 작은 이름표를 달아 무엇인지 바로 알게
   - 위쪽: 이름표(닉네임)는 머리 위에 이미 보이니 위 막대에서 빼고, 후원 버튼은 동그란 아이콘만 — 산 이름이 가리지 않게
   - 알림(토스트)이 체력 막대를 덮지 않게 조금 아래로
   - PC 단축키 설명(숫자·글자 키, 'H 또는')은 휴대폰에서 안 보이게
   - 키보드가 올라오면 창(인삿말 바꾸기·방명록·초대코드·이름 등)이 보이는 화면 안에 들어오게, 고치는 칸이 가운데로 오게
"""

UX2_ROWS = [
    ['지도', 'Map', '地図', '地图', 'Karte', 'Carte', 'Mappa', 'Mapa', 'नक्सा', 'Ramani'],
    ['지도 열기·닫기', 'Open or close the map', '地図を開く・閉じる', '打开或关闭地图', 'Karte öffnen oder schließen', 'Ouvrir ou fermer la carte', 'Apri o chiudi la mappa', 'Abrir o cerrar el mapa', 'नक्सा खोल्नुहोस् वा बन्द गर्नुहोस्', 'Fungua au funga ramani'],
    ['함께', 'Together', '一緒に', '同行', 'Zusammen', 'Ensemble', 'Insieme', 'Juntos', 'सँगै', 'Pamoja'],
    ['쉬기', 'Rest', '休む', '休息', 'Rast', 'Pause', 'Riposo', 'Descanso', 'आराम', 'Pumzika'],
    ['사진', 'Photo', '写真', '照片', 'Foto', 'Photo', 'Foto', 'Foto', 'फोटो', 'Picha'],
    ['더 보기', 'More', 'もっと', '更多', 'Mehr', 'Plus', 'Altro', 'Más', 'थप', 'Zaidi'],
    ['버튼을 숨겼어요 · 오른쪽 위 버튼으로 다시 보여요', 'Buttons hidden · tap the top-right button to show them again', 'ボタンを隠しました · 右上のボタンでまた表示します', '已隐藏按钮 · 点右上角按钮即可重新显示', 'Tasten ausgeblendet · oben rechts tippen, um sie wieder zu zeigen', 'Boutons masqués · touchez le bouton en haut à droite pour les réafficher', 'Pulsanti nascosti · tocca il pulsante in alto a destra per mostrarli', 'Botones ocultos · toca el botón de arriba a la derecha para verlos', 'बटन लुकाइयो · फेरि देखाउन माथि दायाँको बटन थिच्नुहोस्', 'Vitufe vimefichwa · gusa kitufe cha juu kulia kuvionyesha tena'],
    ['인사를 할 때 머리 위에 보이는 말이에요. 한 줄에 20자까지 쓸 수 있어요.', 'These appear above your head when you greet. Up to 20 characters each.', 'あいさつのとき頭の上に出る言葉です。1行20文字まで。', '打招呼时显示在头顶的话，每行最多20字。', 'Erscheint beim Grüßen über deinem Kopf. Bis zu 20 Zeichen.', 'Apparaît au-dessus de votre tête quand vous saluez. 20 caractères max.', 'Appare sopra la testa quando saluti. Massimo 20 caratteri.', 'Aparece sobre tu cabeza al saludar. Hasta 20 caracteres.', 'अभिवादन गर्दा टाउकोमाथि देखिन्छ। बढीमा २० अक्षर।', 'Huonekana juu ya kichwa unaposalimia. Hadi herufi 20.'],
]

UX2_CSS = r'''
/* ---------- 2026-11-11 휴대폰 화면 다듬기 (pipeline/ux2_patch.py) ---------- */
#mapFab{display:none}
body.touch #mapFab{display:grid;position:fixed;z-index:6;right:max(10px,env(safe-area-inset-right,0px));bottom:calc(14px + env(safe-area-inset-bottom,0px));width:54px;height:54px;border-radius:50%;place-items:center;color:var(--text,#fff);pointer-events:auto;cursor:pointer;padding:0;border:1px solid var(--line);-webkit-tap-highlight-color:transparent}
body.touch #mapFab svg{width:23px;height:23px;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;margin-top:-6px}
body.touch #mapFab .l{position:absolute;bottom:6px;left:0;right:0;font-size:9.5px;font-weight:700;text-align:center;line-height:1;opacity:.9}
body.touch.mapOn #mapFab{background:rgba(63,138,85,.85)!important;border-color:rgba(160,230,180,.6)}
body.touch #bMap{display:none!important}
body.touch.mapOn #mapWrap{display:block}
body.touch #mapWrap.big{z-index:8}
body.clean #mapFab{opacity:.3}
body.camping #mapFab,body.photo #mapFab{display:none!important}
/* 행동 버튼: 지도 버튼 위로, 같은 둥근 모양 + 작은 이름표 */
body.touch #actions{bottom:calc(76px + env(safe-area-inset-bottom,0px));gap:4px;padding:4px;border-radius:30px}
body.touch #actions button{width:50px;height:50px;font-size:0;position:relative}
body.touch #actions button svg{margin-top:-8px}
body.touch #actions button .l{position:absolute;bottom:5px;left:0;right:0;font-size:9.5px;font-weight:700;text-align:center;line-height:1;opacity:.88;white-space:nowrap}
body.touch #soBar button{width:50px;height:50px}
body.touch #soBar button svg{margin-top:-8px}
body.touch #soBar button .l{position:absolute;bottom:5px;left:0;right:0;font-size:9.5px;font-weight:700;text-align:center;line-height:1;opacity:.88;font-style:normal}
#actions .l,#soBar .l,#mapFab .l{display:none;font-style:normal}
body.touch #actions .l,body.touch #soBar .l,body.touch #mapFab .l{display:block}
/* 위쪽: 닉네임 빼고, 후원은 동그란 아이콘만 */
body.touch #brand .me,body.touch #brand .sep{display:none!important}
@media (max-width:480px){ body.touch #supportBtn{padding:4px!important;width:42px;justify-content:center} body.touch #supportBtn span{display:none!important} }
/* 알림이 체력 막대를 덮지 않게 */
@media (orientation:portrait){
  body.touch #toast{top:calc(112px + env(safe-area-inset-top,0px));max-width:calc(100vw - 110px)}
  body.touch #banner{top:calc(170px + env(safe-area-inset-top,0px))}
  body.touch #soNote{top:calc(150px + env(safe-area-inset-top,0px))}
  body.touch #soInv,body.touch #soChip{top:calc(150px + env(safe-area-inset-top,0px))}
  body.touch #soFollowPill{top:calc(192px + env(safe-area-inset-top,0px))}
}
/* 휴대폰 가로: 지도 버튼은 구석, 행동 버튼 줄은 그 왼쪽 */
@media (orientation:landscape) and (max-height:540px){
  body.touch #actions{bottom:calc(10px + env(safe-area-inset-bottom,0px));right:calc(max(10px,env(safe-area-inset-right,0px)) + 62px)}
  body.touch #mapFab{bottom:calc(10px + env(safe-area-inset-bottom,0px))}
  body.touch #bottom{padding:0 360px 0 150px}
  body.touch #actions button{width:46px;height:46px}
}
/* PC 단축키 설명은 휴대폰에서 숨기기 */
body.touch kbd,body.touch .deskKeys{display:none!important}
/* 키보드가 올라와도 창이 보이는 화면 안에 */
body.touch .panel{top:var(--vvt,0px);bottom:auto;height:var(--vh,100vh)}
body.touch .panel > .card{max-height:calc(var(--vh,100vh) - 24px);overflow:auto;-webkit-overflow-scrolling:touch}
body.touch.kbd .panel{align-items:flex-start;padding-top:10px;padding-bottom:10px}
body.touch #soChat{top:calc(var(--vvt,0px) + 8px + env(safe-area-inset-top,0px))}
body.touch.kbd #soChat{top:calc(var(--vvt,0px) + 6px)}
body.touch.kbd #joy,body.touch.kbd #actions,body.touch.kbd #mapFab,body.touch.kbd #bottom,body.touch.kbd #soBar{visibility:hidden}
'''

MAP_ICON = '<svg viewBox="0 0 24 24"><path d="M3 6.5 9 4l6 2.5L21 4v13.5L15 20l-6-2.5L3 20z"/><path d="M9 4v13.5M15 6.5V20"/></svg>'

UX2_JS = r'''
// ---------- 2026-11-11 휴대폰 지도 버튼 · 키보드 · 단축키 설명 (pipeline/ux2_patch.py) ----------
{ const touch = () => document.body.classList.contains('touch'), W = $('mapWrap'), F = $('mapFab');
  const setMap = on => { document.body.classList.toggle('mapOn', on); W.classList.toggle('big', on); $('tr').classList.remove('open'); };
  F.addEventListener('click', e => { e.stopPropagation(); setMap(!document.body.classList.contains('mapOn')); });
  // 휴대폰: 크게 연 지도를 눌러도 작아지지 않게 (순간이동 표시만), 닫기는 지도 버튼이나 ✕
  W.onclick = e => { if(tpClick(e)) return; if(touch()) return; W.classList.toggle('big'); };
  new MutationObserver(() => { if(touch() && document.body.classList.contains('mapOn') && !W.classList.contains('big')) document.body.classList.remove('mapOn'); }).observe(W, { attributes: true, attributeFilter: ['class'] });
  // 행동 버튼·채팅/함께 버튼 이름표 (휴대폰에서만 보여요)
  const lab = (id, t) => { const b = $(id); if(b && !b.querySelector('.l')){ const s = document.createElement('i'); s.className = 'l'; s.textContent = t; b.appendChild(s); } };
  lab('aRest', '쉬기'); lab('aPhoto', '사진'); lab('aMore', '더 보기'); lab('aWave', '인사'); lab('aWater', '물'); lab('aBreath', '숨 고르기'); lab('soChatB', '채팅'); lab('soPeopleB', '함께');
  // 키보드: 보이는 화면 높이(--vh)와 위치(--vvt)를 따라가고, 고치는 칸이 가운데로
  const vv = window.visualViewport;
  const sync = () => { if(!vv) return; document.documentElement.style.setProperty('--vvt', Math.round(vv.offsetTop) + 'px'); document.documentElement.style.setProperty('--vh', Math.round(vv.height) + 'px');
    const a = document.activeElement, typing = !!(a && /^(INPUT|TEXTAREA)$/.test(a.tagName)); document.body.classList.toggle('kbd', touch() && typing && vv.height < innerHeight*0.82); };
  if(vv){ vv.addEventListener('resize', sync); vv.addEventListener('scroll', sync); }
  document.addEventListener('focusin', e => { if(!touch() || !/^(INPUT|TEXTAREA)$/.test(e.target.tagName)) return; sync();
    setTimeout(() => { sync(); try{ e.target.scrollIntoView({ block: 'center', behavior: 'smooth' }); }catch(_){} }, 320); });
  document.addEventListener('focusout', () => setTimeout(sync, 80));
}
'''


def patch_ux2(P, m, mt_ko=''):
    P.rep('</style>', UX2_CSS + '</style>', 1)
    # 8) 휴대폰 지도 버튼 (오른쪽 아래 구석)
    P.rep('<div id="mapWrap"', '<button id="mapFab" class="glass" type="button" title="지도 열기·닫기" aria-label="지도 열기·닫기">' + MAP_ICON + '<i class="l">지도</i></button>\n<div id="mapWrap"', 1)
    P.rep("window.__game = {", UX2_JS + "window.__game = {", 1)
    # 9) 단축키 안내를 휴대폰에선 빼기
    P.rep("if(v) toast('버튼을 숨겼어요 · H 또는 오른쪽 위 버튼으로 다시 보여요', 2.5);",
          "if(v) toast(document.body.classList.contains('touch') ? '버튼을 숨겼어요 · 오른쪽 위 버튼으로 다시 보여요' : '버튼을 숨겼어요 · H 또는 오른쪽 위 버튼으로 다시 보여요', 2.5);", 1)
    P.rep("function soOpenGreet(){ $('waveMenu').hidden = true;",
          "function soOpenGreet(){ $('waveMenu').hidden = true; { const n = $('soGreet').querySelector('.note'); if(n) n.textContent = document.body.classList.contains('touch') ? '인사를 할 때 머리 위에 보이는 말이에요. 한 줄에 20자까지 쓸 수 있어요.' : '인사(1)를 할 때 머리 위에 보이는 말이에요. 한 줄에 20자까지 쓸 수 있어요.'; }", 1)
    # 7) 사진: 오른쪽 아래에 neungseon.com, 공유할 때 글 + 이 산 주소
    P.rep("c.width - 26*k, c.height - 22*k);",
          "c.width - 26*k, c.height - 46*k);\n"
          "  x.font = `600 ${Math.round(15*k)}px \"Gowun Dodum\", sans-serif`; x.fillStyle = 'rgba(255,255,255,.82)'; x.fillText('neungseon.com', c.width - 26*k, c.height - 22*k);", 1)
    P.rep("$('psShare').style.display = canShare ? '' : 'none';\n      $('psShare').onclick = () => navigator.share({files:[file], title: T_('능선'), text: T_('능선, 여유 있는 산행')}).catch(()=>{});",
          "const link = /^https:/.test(location.protocol) && /neungseon\\.com$/.test(location.hostname) ? location.origin + location.pathname : PHOTO_URL;\n"
          "      const msg = T_('능선, 여유 있는 산행') + ' · ' + T_(PHOTO_MT) + ' ' + Math.round(heightAt(st.x, st.z)) + 'm';\n"
          "      $('psShare').style.display = (canShare || navigator.share) ? '' : 'none';\n"
          "      $('psShare').onclick = () => (canShare ? navigator.share({files:[file], title: T_('능선'), text: msg + '\\n' + link, url: link}) : navigator.share({title: T_('능선'), text: msg, url: link})).catch(()=>{});", 1)
    page = m.get('page', 'index.html')
    url = 'https://neungseon.com/' + ('' if page in ('', 'index.html') else page)
    mt = mt_ko.replace('\\', '').replace("'", "\\'")
    P.rep("function takePhoto(){", f"const PHOTO_URL = '{url}', PHOTO_MT = '{mt}';\nfunction takePhoto(){{", 1)

