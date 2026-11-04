"""먼 지형(70m~)과 원경 산의 숲·초원 질감을 산마다 실제 사진 질감으로 (make_canopy.py → photos/<id>/canopy.jpg).
예전: 모든 산에 같은 '색 동그라미' 단풍 무늬 → 통가리로 같은 화산 초원도 단풍 숲처럼 보였어요.
- 사진이 초록이면 가을엔 단풍빛으로 물들여요 (활엽수가 있는 산만)"""


# 승연 님 확인 후 나머지 산으로 넓혀요 (2026-11-04: 북한산 먼저)
FAR_READY = {'bukhansan'}


def patch_far(P, m):
    if m['id'] not in FAR_READY: return
    # 먼 산 숲 무리(스프라이트 15만 개)가 계절과 상관없이 단풍색이던 것 → 그 계절의 숲 색(SZ.pals)으로
    P.rep("const pals=[[[150,40,26],[176,74,32],[124,32,22],[96,56,32]]", "const pals=SZ.pals ? SZ.pals.slice(0, 4) : [[[150,40,26],[176,74,32],[124,32,22],[96,56,32]]", 1)
    tex = "const TEX = { litter: makeLitter(), litter2: makeLitter2(), canopy: makeCanopy(), granite: makeGranite(), trail: makeTrailTex() };"
    P.rep(tex, tex + "\n{ const im = new Image(); im.onload = () => { TEX.canopy.image = im; TEX.canopy.needsUpdate = true; }; im.src = 'photos/%s/canopy.jpg'; }" % m['id'], 1)
    P.rep("const seasonGLSL = () => `",
          "const seasonGLSL = () => (SEASON === 'autumn' && BIO.leaf ? `{ float gr = clamp((lit.g - max(lit.r, lit.b))*5.0, 0.0, 1.0); "
          "float h = fract(sin(dot(floor(vWP.xz/9.0), vec2(12.9898, 78.233)))*43758.5453); "
          "vec3 au = lit.g*mix(vec3(1.45, 0.55, 0.22), vec3(1.25, 0.95, 0.3), h); lit = mix(lit, au, gr*0.65); } ` : '') + `", 1)


# 여름·봄 탐방로 둘레 풀꽃: 주황·노랑 한 가지뿐이던 것 → 초록 덤불에 여러 색 꽃 (덤불마다 한 가지 꽃)
# 고사리: 계절과 상관없이 갈색(가을)이던 것 → 봄 연두 / 여름 초록 / 겨울 마른 갈색
FLORA_JS = r"""
{ const G = [[70,120,52],[84,136,60],[58,104,44]];   // 여름 잎
  const set = (f, g = G) => [...g, ...f];
  if(SEASON === 'summer'){
    SZ.flowerSets = [
      set([[250,150,50],[240,128,40]]),          // 원추리 주황
      set([[176,150,220],[156,128,206]]),        // 비비추 연보라
      set([[120,150,228],[150,176,236]]),        // 산수국 파랑
      set([[246,246,240],[236,236,226]]),        // 개망초·까치수염 흰색
      set([[236,120,160],[246,156,186]]),        // 패랭이 분홍
      set([[250,214,80],[244,196,60]]),          // 기린초 노랑
      set([[228,84,60],[240,110,70]]),           // 하늘나리 주홍
      G.concat([[96,150,66]])                     // 꽃 없는 초록 덤불
    ];
    SZ.flowerAmt = 0.16;
  } else if(SEASON === 'spring'){
    const S = [[110,160,70],[126,174,80],[96,146,60]];
    SZ.flowerSets = [ set([[232,120,170],[244,160,196]], S), set([[214,82,150],[226,110,170]], S), set([[246,240,236],[250,230,236]], S),
                      set([[250,220,90],[240,200,70]], S), set([[180,140,220],[200,170,232]], S), S.concat([[140,186,90]]) ];
  }
  SZ.fern = { spring: [[[120,170,70],[140,186,84],[104,150,60]], [[150,192,92],[130,176,76],[166,202,104]]],
              summer: [[[56,112,44],[70,128,52],[46,98,38]], [[82,140,58],[64,122,48],[98,154,68]]],
              winter: [[[150,128,100],[170,148,118],[128,110,88]], [[160,140,110],[140,120,96],[182,162,132]]] }[SEASON] || null;
}
"""


def patch_flora(P, m):
    if m['id'] not in FAR_READY: return
    P.rep("Object.assign(SZ, SZX[SEASON] || {});", "Object.assign(SZ, SZX[SEASON] || {});" + FLORA_JS, 1)
    P.rep("const PV = { grass:2, reed:2, fern:2, bushRed:2, bushOak:2, bushGreen:1 };",
          "const PV = { grass:2, reed:2, fern:2, bushRed:(SZ.flowerSets ? SZ.flowerSets.length : 2), bushOak:2, bushGreen:1 };", 1)
    P.rep("const pal = kind==='bushRed' ? (SZ.flower ||", "const pal = kind==='bushRed' ? ((SZ.flowerSets && SZ.flowerSets[v % SZ.flowerSets.length]) || SZ.flower ||", 1)
    P.rep("const cols = v? [[132,92,44],[150,104,50],[110,76,38]] : [[96,104,50],[120,110,52],[80,88,42]];",
          "const cols = SZ.fern ? SZ.fern[v ? 1 : 0] : (v? [[132,92,44],[150,104,50],[110,76,38]] : [[96,104,50],[120,110,52],[80,88,42]]);", 1)
