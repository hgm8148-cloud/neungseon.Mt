"""나무가 없는 고산·화산 탐방로(BIO.leaf≈0: 에베레스트·킬리만자로·마터호른·트레치메·통가리로) 바닥 무늬:
낙엽 → 화산 자갈·돌 조각, 겨울(또는 늘 겨울인 산)엔 눈 얼룩"""

GRAVEL_JS = r"""if(BIO.leaf < 0.05){
    for(let i=0;i<260;i++){ const px=W*(0.08+trnd()*0.84), py=trnd()*W, r=1.2+trnd()*3.2, l=0.55+trnd()*0.55, dk=trnd()<0.35, a=trnd()*6.28, n=5+((trnd()*3)|0);
      const col = dk ? [62*l,56*l,54*l] : [150*l,142*l,132*l];
      wrapDraw(W,px,py,r+3,(X,Y)=>{ x.save(); x.translate(X,Y); x.rotate(a);
        x.fillStyle='rgba(20,16,12,.28)'; x.beginPath(); for(let k=0;k<n;k++){ const t=k/n*6.28, rr=r*(0.7+0.3*Math.sin(k*2.3+i)); x.lineTo(Math.cos(t)*rr+0.8, Math.sin(t)*rr*0.75+0.8); } x.fill();
        x.fillStyle=rgbStr(col[0],col[1],col[2]); x.beginPath(); for(let k=0;k<n;k++){ const t=k/n*6.28, rr=r*(0.7+0.3*Math.sin(k*2.3+i)); x.lineTo(Math.cos(t)*rr, Math.sin(t)*rr*0.75); } x.fill();
        x.fillStyle='rgba(255,255,255,.18)'; x.fillRect(-r*0.4,-r*0.45,r*0.5,r*0.25); x.restore(); }); }
    if(SEASON === 'winter' || SEASON === 'fixed'){
      for(let i=0;i<26;i++){ const px=W*(0.06+trnd()*0.88), py=trnd()*W, r=3+trnd()*7, m=3+((trnd()*4)|0), rot=trnd()*3;
        wrapDraw(W,px,py,r*3,(X,Y)=>{ for(let k=0;k<m;k++){ const ox=(trnd()-0.5)*r*2.2, oy=(trnd()-0.5)*r*1.2, rr=r*(0.4+trnd()*0.6);
          const g=x.createRadialGradient(X+ox,Y+oy,0,X+ox,Y+oy,rr); g.addColorStop(0,'rgba(246,248,251,.7)'); g.addColorStop(0.6,'rgba(238,242,247,.45)'); g.addColorStop(1,'rgba(238,242,247,0)');
          x.fillStyle=g; x.beginPath(); x.ellipse(X+ox,Y+oy,rr*1.3,rr*0.7,rot,0,7); x.fill(); } }); } }
  } else """


VP_FIX = [
    ['골짜기 너머로 신록 능선이 펼쳐져요','Fresh green ridges stretch beyond the valley','谷の向こうに新緑の稜線が広がります','山谷那头，新绿山脊绵延','Hinter dem Tal erstrecken sich frühlingsgrüne Grate','Au-delà de la vallée s’étendent des crêtes vert tendre','Oltre la valle si stendono creste di verde novello','Más allá del valle se extienden crestas de verde tierno','उपत्यकापारि नयाँ हरियो पहाडी रेखाहरू फैलिएका छन्','Ng’ambo ya bonde matuta ya kijani kibichi yanaenea'],
    ['골짜기 너머로 푸른 능선이 펼쳐져요','Green ridges stretch beyond the valley','谷の向こうに緑の稜線が広がります','山谷那头，青翠山脊绵延','Hinter dem Tal erstrecken sich grüne Grate','Au-delà de la vallée s’étendent des crêtes verdoyantes','Oltre la valle si stendono creste verdi','Más allá del valle se extienden crestas verdes','उपत्यकापारि हरिया पहाडी रेखाहरू फैलिएका छन्','Ng’ambo ya bonde matuta ya kijani yanaenea'],
    ['골짜기 너머로 눈 덮인 능선이 펼쳐져요','Snowy ridges stretch beyond the valley','谷の向こうに雪の稜線が広がります','山谷那头，白雪山脊绵延','Hinter dem Tal erstrecken sich verschneite Grate','Au-delà de la vallée s’étendent des crêtes enneigées','Oltre la valle si stendono creste innevate','Más allá del valle se extienden crestas nevadas','उपत्यकापारि हिउँले ढाकिएका पहाडी रेखाहरू फैलिएका छन्','Ng’ambo ya bonde matuta yenye theluji yanaenea'],
    ['골짜기 너머로 겹겹의 능선이 펼쳐져요','Layer upon layer of ridges stretch beyond the valley','谷の向こうに幾重もの稜線が広がります','山谷那头，层层山脊绵延','Hinter dem Tal erstrecken sich Grat um Grat','Au-delà de la vallée s’étendent des crêtes à perte de vue','Oltre la valle si stendono creste su creste','Más allá del valle se extienden crestas y más crestas','उपत्यकापारि तह-तह पहाडी रेखाहरू फैलिएका छन्','Ng’ambo ya bonde matuta mengi yanaenea'],
    ['정상으로 이어지는 겹겹의 능선이 보여요','Ridge after ridge leads up to the summit','山頂へ続く幾重もの稜線が見えます','层层山脊一路通向山顶','Grat um Grat führt hinauf zum Gipfel','Les crêtes s’enchaînent jusqu’au sommet','Creste su creste salgono verso la vetta','Cresta tras cresta sube hacia la cumbre','शिखरसम्म पुग्ने तह-तह पहाडी रेखाहरू देखिन्छन्','Matuta mengi yanaelekea kileleni'],
    ['물소리를 들으며 신록 계곡을 바라봐요','Listen to the stream and gaze at the fresh green valley','水の音を聞きながら新緑の渓谷を眺めましょう','听着水声，看看新绿溪谷','Lausche dem Bach und blicke ins frühlingsgrüne Tal','Écoutez le ruisseau et contemplez la vallée vert tendre','Ascolta il torrente e guarda la valle di verde novello','Escucha el arroyo y contempla el valle de verde tierno','खोलाको आवाज सुन्दै नयाँ हरियो उपत्यका हेर्नुहोस्','Sikiliza kijito na utazame bonde la kijani kibichi'],
    ['물소리를 들으며 푸른 계곡을 바라봐요','Listen to the stream and gaze at the green valley','水の音を聞きながら緑の渓谷を眺めましょう','听着水声，看看青翠溪谷','Lausche dem Bach und blicke ins grüne Tal','Écoutez le ruisseau et contemplez la vallée verdoyante','Ascolta il torrente e guarda la valle verde','Escucha el arroyo y contempla el valle verde','खोलाको आवाज सुन्दै हरियो उपत्यका हेर्नुहोस्','Sikiliza kijito na utazame bonde la kijani'],
    ['물소리를 들으며 눈 덮인 계곡을 바라봐요','Listen to the stream and gaze at the snowy valley','水の音を聞きながら雪の渓谷を眺めましょう','听着水声，看看白雪溪谷','Lausche dem Bach und blicke ins verschneite Tal','Écoutez le ruisseau et contemplez la vallée enneigée','Ascolta il torrente e guarda la valle innevata','Escucha el arroyo y contempla el valle nevado','खोलाको आवाज सुन्दै हिउँले ढाकिएको उपत्यका हेर्नुहोस्','Sikiliza kijito na utazame bonde lenye theluji'],
    ['물소리를 들으며 계곡을 바라봐요','Listen to the stream and gaze at the valley','水の音を聞きながら渓谷を眺めましょう','听着水声，看看溪谷','Lausche dem Bach und blicke ins Tal','Écoutez le ruisseau et contemplez la vallée','Ascolta il torrente e guarda la valle','Escucha el arroyo y contempla el valle','खोलाको आवाज सुन्दै उपत्यका हेर्नुहोस्','Sikiliza kijito na utazame bonde'],
]
VP_FIX += [
    ['이곳으로 순간이동할까요?','Teleport here?','ここへ移動しますか？','要瞬间移动到这里吗？','Hierher teleportieren?','Se téléporter ici ?','Teletrasportarsi qui?','¿Teletransportarse aquí?','यहाँ सिधै जाने?','Uhamie hapa mara moja?'],
    ['이미 지나온 곳이라 바로 갈 수 있어요','You have been here, so you can jump straight back','一度通った場所なので、すぐに戻れます','这里你已经来过，可以直接回去','Hier warst du schon – du kannst direkt zurück','Vous y êtes déjà passé, vous pouvez y retourner directement','Ci sei già passato, puoi tornarci subito','Ya pasaste por aquí, puedes volver al instante','तपाईं यहाँ आइसक्नुभएको छ, सिधै फर्कन सक्नुहुन्छ','Umeshapita hapa, unaweza kurudi moja kwa moja'],
    ['이동하기','Go','移動する','前往','Los','Y aller','Vai','Ir','जानुहोस्','Nenda'],
    ['취소','Cancel','キャンセル','取消','Abbrechen','Annuler','Annulla','Cancelar','रद्द गर्नुहोस्','Ghairi'],
    ['순간이동했어요','Teleported','移動しました','已瞬间移动','Teleportiert','Téléporté','Teletrasportato','Teletransportado','सिधै पुगियो','Umehamia'],
    ['아직 가 보지 않은 곳이에요 · 걸어서 먼저 들러 보세요','You haven’t been here yet · walk there first','まだ行っていない場所です · まずは歩いて訪れてみましょう','这里还没去过 · 先走过去看看吧','Hier warst du noch nicht · geh zuerst zu Fuß hin','Vous n’y êtes pas encore allé · allez-y d’abord à pied','Non ci sei ancora stato · prima arrivaci a piedi','Aún no has estado aquí · ve primero caminando','तपाईं अझै यहाँ पुग्नुभएको छैन · पहिले हिँडेर जानुहोस्','Bado hujafika hapa · tembea huko kwanza'],
]

VP_FIX += [['📮 경유지 도착 · 이 산의 사진 엽서','📮 Checkpoint reached · a postcard from this mountain','📮 経由地に到着 · この山の写真はがき','📮 抵达途经点 · 这座山的明信片','📮 Etappe erreicht · eine Postkarte von diesem Berg','📮 Étape atteinte · une carte postale de cette montagne','📮 Tappa raggiunta · una cartolina da questa montagna','📮 Punto alcanzado · una postal de esta montaña','📮 बिसौनीमा पुगियो · यो हिमालको पोस्टकार्ड','📮 Umefika kituo · postikadi ya mlima huu']]
VP_JS = "const VP_SZ = (a, b, c, d, e) => (BIO.leaf < 0.05 || SEASON === 'fixed') ? e : ({spring:a, summer:b, autumn:c, winter:d})[SEASON] || e;\n"


def patch_vp_text(P, m):
    # 전망 안내 문구가 계절·산과 맞게 (겨울에 '단풍 계곡', 다른 산에서 '인수봉'이 나오던 문제)
    P.rep("// rocks\nconst restSpots = [];", VP_JS + "// rocks\nconst restSpots = [];", 1)
    P.rep(": '골짜기 너머로 단풍 능선이 펼쳐져요'}", ": VP_SZ('골짜기 너머로 신록 능선이 펼쳐져요', '골짜기 너머로 푸른 능선이 펼쳐져요', '골짜기 너머로 단풍 능선이 펼쳐져요', '골짜기 너머로 눈 덮인 능선이 펼쳐져요', '골짜기 너머로 겹겹의 능선이 펼쳐져요')}", 1)
    if m['id'] != 'bukhansan':
        P.rep("? '인수봉과 겹겹의 능선이 보여요' :", "? '정상으로 이어지는 겹겹의 능선이 보여요' :", 1)
    P.rep("sub:'물소리를 들으며 단풍 계곡을 바라봐요'", "sub:VP_SZ('물소리를 들으며 신록 계곡을 바라봐요', '물소리를 들으며 푸른 계곡을 바라봐요', '물소리를 들으며 단풍 계곡을 바라봐요', '물소리를 들으며 눈 덮인 계곡을 바라봐요', '물소리를 들으며 계곡을 바라봐요')", need=False)


def patch_trail(P, m):
    patch_vp_text(P, m)
    patch_teleport(P, m)
    patch_prog_fit(P, m)
    # 바닥 낙엽 무늬(LEAF_COLS)도 나무 없는 산에선 돌 조각 색으로
    P.rep("if(SZ.leaf) LEAF_COLS.splice(0, LEAF_COLS.length, ...SZ.leaf);",
          "if(SZ.leaf) LEAF_COLS.splice(0, LEAF_COLS.length, ...SZ.leaf);\n"
          "else if(BIO.leaf < 0.05) LEAF_COLS.splice(0, LEAF_COLS.length, [120,112,104],[96,90,86],[150,142,132],[80,74,70],[136,124,110],[110,100,92],[228,232,238]);", 1)
    P.rep("    let r=138*k, g=113*k, b=86*k;\n", "    let r=(BIO.leaf < 0.05 ? 116 : 138)*k, g=(BIO.leaf < 0.05 ? 107 : 113)*k, b=(BIO.leaf < 0.05 ? 99 : 86)*k;\n", 1)
    P.rep("  for(let i=0;i<80;i++){ const px=W*(0.1+trnd()*0.8), py=trnd()*W, c0=LEAF_COLS",
          "  " + GRAVEL_JS + "for(let i=0;i<80;i++){ const px=W*(0.1+trnd()*0.8), py=trnd()*W, c0=LEAF_COLS", 1)


# ---------- 지도에서 지나온 곳으로 순간이동 ----------
TP_CSS = '''
#tpAsk{position:fixed;inset:0;z-index:60;display:grid;place-items:center;background:rgba(10,12,10,.28)}
#tpAsk[hidden]{display:none}
#tpAsk .box{background:var(--paper,#fbf7ef);color:var(--ink,#2a2620);border-radius:18px;padding:18px 20px 16px;min-width:260px;max-width:min(88vw,360px);box-shadow:0 18px 50px rgba(0,0,0,.35);text-align:center}
#tpAsk .nm{font-size:19px;font-weight:700;margin:2px 0 4px}
#tpAsk .q{font-size:15px;margin:0}
#tpAsk small{display:block;opacity:.65;font-size:12.5px;margin:6px 0 14px}
#tpAsk .row{display:flex;gap:8px;justify-content:center}
#tpAsk button{border:0;border-radius:999px;padding:9px 20px;font:inherit;font-size:14px;font-weight:600;cursor:pointer}
#tpAsk .go{background:#3f6e48;color:#fff}#tpAsk .no{background:rgba(0,0,0,.07);color:inherit}
'''
TP_HTML = '<div id="tpAsk" hidden><div class="box"><div class="nm" id="tpName"></div><p class="q">이곳으로 순간이동할까요?</p><small>이미 지나온 곳이라 바로 갈 수 있어요</small><div class="row"><button class="no" id="tpNo">취소</button><button class="go" id="tpGo">이동하기</button></div></div></div>'
TP_JS = r'''
// ---------- 지도: 지나온 체크포인트·전망 스팟을 눌러 순간이동 (pipeline/trail_patch.py) ----------
const TP_KEY = 'neungseon.reach.__ID__';
let TP_REACH = 0; try{ TP_REACH = +localStorage.getItem(TP_KEY) || 0; }catch(e){}
setInterval(() => { if(!st || st.x == null) return; const nt = nearTrail(st.x, st.z, 1); if(nt.i >= 0 && nt.d < 6 && nt.i > TP_REACH){ TP_REACH = nt.i; try{ localStorage.setItem(TP_KEY, TP_REACH); }catch(e){} } }, 700);
// 순간이동 규칙 (2026-11-05 승연): 경유지·전망 스팟은 이 산을 완등한 사람만, 숨은 길 입구는 그 길을 찾은 사람만 (관리자는 모두)
const tpAdm = () => document.body.classList.contains('admin');
const tpSum = () => { try{ return !!((JSON.parse(localStorage.getItem('neungseon.prog') || '{}') || {})['__ID__'] || {}).sum; }catch(e){ return false; } };
const tpOk = s => tpAdm() || (s.side != null ? !!(window.__SIDE && window.__SIDE.found(s.side)) : tpSum());
const tpSpots = () => { const out = []; const T_ = window.T || (x => x);
  WPS.forEach((w, k) => { const p = trail[w.i]; out.push({ i: w.i, x: p.x, z: p.z, name: T_(w.name.replace(/\(.*\)/, '')), wp: k }); });
  for(const v of VIEWPOINTS) if(!v.spin){ const p = trail[v.i]; out.push({ i: v.i, x: p.x, z: p.z, name: T_(v.name), vp: true }); }
  const S = window.__SIDE; if(S) for(const q of S.paths){ if(!tpAdm() && !S.found(q.k)) continue; const p = q.pts[q.e]; out.push({ x: p.x, z: p.z, name: S.label(q), side: q.k }); }
  return out; };
let tpPick = null;
function tpGo(){ const s = tpPick; $('tpAsk').hidden = true; if(!s) return;
  if(s.side != null){ window.__SIDE.goTo(s.side); st.auto = false; refreshWalk(); st.cf = null; toast('순간이동했어요', 2); canvas.focus(); return; }
  const p = trail[Math.min(trail.length - 1, s.i)], q = trail[Math.min(trail.length - 1, s.i + 4)];
  st.x = p.x; st.z = p.z; st.face = Math.atan2(q.x - p.x, q.z - p.z); st.yaw = st.face + Math.PI; st.goal = null; st.sitting = false; st.breathing = 0; st.auto = false; refreshWalk();
  goalRing.visible = false; st.camInit = false; st.cf = null; toast('순간이동했어요', 2); canvas.focus(); }
$('tpGo').onclick = tpGo; $('tpNo').onclick = () => { $('tpAsk').hidden = true; tpPick = null; };
$('tpAsk').addEventListener('click', e => { if(e.target === $('tpAsk')){ $('tpAsk').hidden = true; tpPick = null; } });
function tpClick(e){ const W = $('mapWrap'); const big = W.classList.contains('big') || document.body.classList.contains('mapOn');
  if(!big || !drawMap.tf) return false;
  const r = mapC.getBoundingClientRect(), mx = (e.clientX - r.left) / r.width * MAPN, my = (e.clientY - r.top) / r.height * MAPN;
  let best = null, bd = 26; for(const s of tpSpots()){ const d = Math.hypot(drawMap.tf.u(s.x) - mx, drawMap.tf.v(s.z) - my); if(d < bd){ bd = d; best = s; } }
  if(!best) return false;
  if(!tpOk(best)){ toast('이 산을 완등하면 지도에서 눌러 바로 이동할 수 있어요', 2.8); return true; }
  tpPick = best; $('tpName').textContent = best.name; $('tpAsk').hidden = false; return true; }
window.__tp = { spots: tpSpots, tf: () => drawMap.tf, reach: () => TP_REACH, ok: tpOk };
'''


def patch_teleport(P, m):
    P.rep('</style>', TP_CSS + '</style>', 1)
    P.rep('<div id="mapWrap" class="hud glass click"><canvas id="map" width="500" height="500"></canvas></div>',
          '<div id="mapWrap" class="hud glass click"><canvas id="map" width="500" height="500"></canvas></div>' + TP_HTML, 1)
    # 지도 좌표 변환을 밖에서도 쓰게 + 전망 스팟 표시(지나온 곳은 금색, 아직이면 회색)
    P.rep("  const toU = x => (x-ox)*k, toV = z => (z-oz)*k;\n",
          "  const toU = x => (x-ox)*k, toV = z => (z-oz)*k; drawMap.tf = { u: toU, v: toV };\n", 1)
    P.rep("  const dot = (x,z,col,rad) => {",
          "  for(const vp of VIEWPOINTS){ if(vp.spin) continue; const p = trail[vp.i], u = toU(p.x), v = toV(p.z); if(u<-20||v<-20||u>MAPN+20||v>MAPN+20) continue; const rr = big ? 5 : 10, ok = tpOk(vp);\n"
          "    mctx.save(); mctx.translate(u, v); mctx.rotate(Math.PI/4); mctx.fillStyle = ok ? '#f1c862' : 'rgba(200,200,200,.9)'; mctx.strokeStyle = '#2b2118'; mctx.lineWidth = big ? 1.6 : 3; mctx.fillRect(-rr*0.75, -rr*0.75, rr*1.5, rr*1.5); mctx.strokeRect(-rr*0.75, -rr*0.75, rr*1.5, rr*1.5); mctx.restore(); }\n"
          "  if(big){ for(const s of tpSpots()){ if(!tpOk(s)) continue; const u = toU(s.x), v = toV(s.z); mctx.save(); mctx.strokeStyle = 'rgba(255,255,255,.95)'; mctx.lineWidth = 2; mctx.shadowColor = 'rgba(255,255,255,.8)'; mctx.shadowBlur = 6; mctx.beginPath(); mctx.arc(u, v, 10, 0, 7); mctx.stroke(); mctx.restore(); }\n"
          "    mctx.save(); mctx.font = '600 12px sans-serif'; mctx.textAlign = 'left'; mctx.fillStyle = 'rgba(255,255,255,.92)'; mctx.strokeStyle = 'rgba(20,16,12,.75)'; mctx.lineWidth = 3; const lg = tpSum() || tpAdm() ? '◯ 표시된 곳을 누르면 바로 이동해요' : '완등하면 경유지로 바로 이동할 수 있어요'; const lt = (window.T || (x => x))(lg); mctx.strokeText(lt, 10, MAPN - 12); mctx.fillText(lt, 10, MAPN - 12); mctx.restore(); }\n"
          "  const dot = (x,z,col,rad) => {", 1)
    P.rep("$('mapWrap').onclick=()=>$('mapWrap').classList.toggle('big');",
          "$('mapWrap').onclick=e=>{ if(tpClick(e)) return; $('mapWrap').classList.toggle('big'); };", 1)
    P.rep("window.__game = {", TP_JS.replace('__ID__', m['id']) + "window.__game = {", 1)
    # 지도를 처음 열 때 숨은 길(window.__SIDE)이 아직 없을 수 있어서 위 코드는 모두 늦게 읽어요


# ---------- 경로 안내 바(#prog)가 간식 보태기 버튼·툴바와 겹치지 않게 ----------
PROG_FIT_JS = r'''
// ---------- 경로 안내 바 자리 맞추기 (pipeline/trail_patch.py) ----------
{ const fit = () => { const pg = $('prog'), tl = $('brand'), tr = $('tr'); if(!pg || !tl || !tr) return;
    pg.style.left = ''; pg.style.width = ''; pg.classList.remove('tight');
    if(getComputedStyle(pg).display === 'none') return;
    let right = innerWidth; for(const el of [tr, $('supportBtn')]){ if(!el) continue; const r = el.getBoundingClientRect(); if(r.width > 0 && r.top < 80) right = Math.min(right, r.left); }
    const left = tl.getBoundingClientRect().right, gap = 16, room = right - left - gap*2;
    if(room < 240){ pg.classList.add('tight'); return; }
    const w = Math.min(460, room), c = left + gap + room/2;
    pg.style.width = w + 'px'; pg.style.left = (Math.abs(c - innerWidth/2) < 4 ? innerWidth/2 : c) + 'px'; };
  addEventListener('resize', fit); setInterval(fit, 1500); setTimeout(fit, 300); window.__progFit = fit; }
'''


def patch_prog_fit(P, m):
    P.rep('</style>', '#prog.tight{display:none!important}\n#pcard .pk{font-size:11.5px;font-weight:700;letter-spacing:.04em;color:#b5562c;margin:1px 3px 6px}\n</style>', 1)
    # 경유지 사진 엽서가 무엇인지 알 수 있게 머리글
    P.rep('<button type="button" aria-label="닫기">✕</button><img alt="">', '<button type="button" aria-label="닫기">✕</button><div class="pk">📮 경유지 도착 · 이 산의 사진 엽서</div><img alt="">', need=False)
    P.rep("window.__game = {", PROG_FIT_JS + "window.__game = {", 1)
