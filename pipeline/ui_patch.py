"""사용자 화면 다듬기 (휴대폰 위주).
- 관리자 버튼: 관리자 모드가 아니면 메뉴를 펼쳐도 절대 안 보이고, 눌러도 안 열림 (휴대폰 메뉴에서 보이던 문제)
- 후원 버튼: ⋯ 메뉴 버튼 옆에 늘 보이게, 버튼 숨기기 때는 아이콘만
- 휴대폰 ⋯ 메뉴: 세로 화면에서는 아이콘 옆에 이름을 같이 보여 줘서 무슨 버튼인지 바로 알게
- 야영장 메뉴: 접기/펼치기
- 야영을 마친 뒤 정상(야영장)에 있으면 '정상 메뉴' 버튼이 보이게"""

UI_CSS = r"""
body:not(.admin) #bAdmin{display:none!important}
#tr{flex-direction:row-reverse;align-items:flex-start}
body.touch #supportBtn{display:flex;font-size:12px;height:42px;box-sizing:border-box;padding:4px 12px 4px 5px!important}
body.touch #supportBtn .oni{width:30px;height:30px}
body.touch #tr.open #supportBtn{display:flex;font-size:12px;padding:4px 12px 4px 5px!important}
body.clean #tr#tr#tr#tr#tr#tr{opacity:1!important;pointer-events:none!important;top:calc(54px + env(safe-area-inset-top,0px))}
body.clean #tools#tools#tools#tools#tools#tools{display:none!important}
body.clean #supportBtn#supportBtn#supportBtn#supportBtn#supportBtn#supportBtn{display:flex!important;pointer-events:auto!important;padding:4px!important;height:auto;opacity:.8}
body.clean #supportBtn span{display:none!important}
@media (orientation:portrait){
  body.touch #tr.open #tools{align-items:stretch}
  body.touch #tr.open #tools > .ib:not(#bMenu){width:auto;grid-template-columns:24px auto;justify-content:start;gap:8px;padding:0 14px 0 8px;border-radius:20px;color:inherit;font-size:12.5px;white-space:nowrap}
  body.touch #tr.open #tools > .ib:not(#bMenu)::after{content:attr(aria-label)}
  body.touch #tr.open #supportBtn{padding:4px!important}body.touch #tr.open #supportBtn span{display:none!important}
}
#supportBtn .sShort{display:none}
@media (max-width:480px){ body.touch #supportBtn .sLong{display:none} body.touch #supportBtn .sShort{display:inline} }
#cMin .mOpen{display:none}body.campMini #supportBtn .sShort{display:none}
@media (max-width:480px){ body.touch #supportBtn .sLong{display:none} body.touch #supportBtn .sShort{display:inline} }
#cMin .mOpen{display:inline}body.campMini #cMin .mClose{display:none}
body.campMini #campBar button:not(#cMin){display:none!important}
body.campMini #campBar .cTitle{border-right:0}
body.inSummit:not(.camping) #summitBtn#summitBtn#summitBtn{display:inline-flex!important}
"""

CMIN_HTML = '<button id="cMin" aria-label="야영장 메뉴 접기·펼치기"><span class="e mClose">▾</span><span class="e mOpen">▴</span><span class="mClose">접기</span><span class="mOpen">펼치기</span></button>'

UI_JS = r"""
// ---------- 야영장 메뉴 접기 ----------
document.body.classList.toggle('campMini', !!store.get('campMini', false));
$('cMin').onclick = () => { const v = !document.body.classList.contains('campMini'); document.body.classList.toggle('campMini', v); store.set('campMini', v); };
"""

UIX_ROWS = [
    ['후원', 'Support', '応援', '支持'],
    ['접기', 'Fold', 'たたむ', '收起'],
    ['펼치기', 'Open', 'ひらく', '展开'],
    ['야영장 메뉴 접기·펼치기', 'Fold or open the camp menu', 'キャンプメニューをたたむ・ひらく', '收起或展开营地菜单'],
]


def patch_ui(P, m):
    P.rep("</style>", UI_CSS + "</style>", 1)
    P.rep('<span>산행 간식 보태기</span></button>', '<span class="sLong">산행 간식 보태기</span><span class="sShort">후원</span></button>', 1)
    P.rep('<button id="cEnd"><span class="e">↩</span>마치기</button>', '<button id="cEnd"><span class="e">↩</span>마치기</button>\n    ' + CMIN_HTML, 1)
    P.rep("$('bAdmin').onclick = () => { $('adminPanel').hidden = !$('adminPanel').hidden; };",
          "$('bAdmin').onclick = () => { if(!document.body.classList.contains('admin')){ $('adminPanel').hidden = true; return; } $('adminPanel').hidden = !$('adminPanel').hidden; };", 1)
    P.rep("document.querySelectorAll('#adminPanel [data-ad]').forEach(b => b.addEventListener('click', () => {",
          "document.querySelectorAll('#adminPanel [data-ad]').forEach(b => b.addEventListener('click', () => { if(!document.body.classList.contains('admin')) return;", 1)
    P.rep("window.__game = {", UI_JS + "window.__game = {", 1)
