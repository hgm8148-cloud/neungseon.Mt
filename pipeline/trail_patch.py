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


def patch_trail(P, m):
    # 바닥 낙엽 무늬(LEAF_COLS)도 나무 없는 산에선 돌 조각 색으로
    P.rep("if(SZ.leaf) LEAF_COLS.splice(0, LEAF_COLS.length, ...SZ.leaf);",
          "if(SZ.leaf) LEAF_COLS.splice(0, LEAF_COLS.length, ...SZ.leaf);\n"
          "else if(BIO.leaf < 0.05) LEAF_COLS.splice(0, LEAF_COLS.length, [120,112,104],[96,90,86],[150,142,132],[80,74,70],[136,124,110],[110,100,92],[228,232,238]);", 1)
    P.rep("    let r=138*k, g=113*k, b=86*k;\n", "    let r=(BIO.leaf < 0.05 ? 116 : 138)*k, g=(BIO.leaf < 0.05 ? 107 : 113)*k, b=(BIO.leaf < 0.05 ? 99 : 86)*k;\n", 1)
    P.rep("  for(let i=0;i<80;i++){ const px=W*(0.1+trnd()*0.8), py=trnd()*W, c0=LEAF_COLS",
          "  " + GRAVEL_JS + "for(let i=0;i<80;i++){ const px=W*(0.1+trnd()*0.8), py=trnd()*W, c0=LEAF_COLS", 1)
