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
    # 바닥 낙엽 무늬(LEAF_COLS)도 나무 없는 산에선 돌 조각 색으로
    P.rep("if(SZ.leaf) LEAF_COLS.splice(0, LEAF_COLS.length, ...SZ.leaf);",
          "if(SZ.leaf) LEAF_COLS.splice(0, LEAF_COLS.length, ...SZ.leaf);\n"
          "else if(BIO.leaf < 0.05) LEAF_COLS.splice(0, LEAF_COLS.length, [120,112,104],[96,90,86],[150,142,132],[80,74,70],[136,124,110],[110,100,92],[228,232,238]);", 1)
    P.rep("    let r=138*k, g=113*k, b=86*k;\n", "    let r=(BIO.leaf < 0.05 ? 116 : 138)*k, g=(BIO.leaf < 0.05 ? 107 : 113)*k, b=(BIO.leaf < 0.05 ? 99 : 86)*k;\n", 1)
    P.rep("  for(let i=0;i<80;i++){ const px=W*(0.1+trnd()*0.8), py=trnd()*W, c0=LEAF_COLS",
          "  " + GRAVEL_JS + "for(let i=0;i<80;i++){ const px=W*(0.1+trnd()*0.8), py=trnd()*W, c0=LEAF_COLS", 1)
