import json

"""먼 지형(70m~)과 원경 산의 숲·초원 질감을 산마다 실제 사진 질감으로 (make_canopy.py → photos/<id>/canopy.jpg).
예전: 모든 산에 같은 '색 동그라미' 단풍 무늬 → 통가리로 같은 화산 초원도 단풍 숲처럼 보였어요.
- 사진이 초록이면 가을엔 단풍빛으로 물들여요 (활엽수가 있는 산만)"""


# 2026-11-04: 북한산 사계절 확인 끝 → 20개 산 모두 같은 로직
FAR_READY = {'bukhansan', 'deogyusan', 'everest', 'fuji', 'halfdome', 'hallasan', 'huangshan', 'jirisan', 'kilimanjaro', 'matterhorn',
             'montblanc', 'mudeungsan', 'naejangsan', 'seoraksan', 'sobaeksan', 'taebaeksan', 'tongariro', 'torresdelpaine', 'trecime', 'wolchulsan'}

# 그 산 사진이 다른 계절(단풍·눈)뿐이면, 그 계절엔 가까운 산의 푸른 숲 사진을 빌려 써요
CANOPY_SEASON = {
    'naejangsan': dict(spring='mudeungsan', summer='mudeungsan', winter='mudeungsan'),   # 내장산 사진은 단풍뿐
    'deogyusan':  dict(spring='jirisan', summer='jirisan', autumn='jirisan'),             # 덕유산 사진은 눈 덮인 숲
    'seoraksan':  dict(spring='jirisan', summer='jirisan', autumn='jirisan'),             # 설악산 사진은 눈 쌓인 바위
    'hallasan':   dict(spring='jirisan', summer='jirisan'),                                # 한라산 사진은 겨울·늦가을 고원
}

def patch_far(P, m):
    if m.get('base', m['id']) not in FAR_READY: return
    # 먼 산 숲 무리(스프라이트 15만 개)가 계절과 상관없이 단풍색이던 것 → 그 계절의 숲 색(SZ.pals)으로
    P.rep("const pals=[[[150,40,26],[176,74,32],[124,32,22],[96,56,32]]", "const pals=SZ.pals ? (SZ.notCherry ? [1,2,3,2].map(i => SZ.pals[i]) : SZ.pals.slice(0, 4)) : (BIO.leaf < 0.5 && SEASON === 'autumn') ? [[[196,150,52],[214,176,70],[176,128,44],[150,110,40]],[[52,74,40],[40,60,34],[66,86,46],[88,96,50]],[[40,62,36],[34,54,30],[56,78,42],[30,48,28]],[[150,96,48],[124,80,40],[170,118,58],[110,76,40]]] : [[[150,40,26],[176,74,32],[124,32,22],[96,56,32]]", 1)
    tex = "const TEX = { litter: makeLitter(), litter2: makeLitter2(), canopy: makeCanopy(), granite: makeGranite(), trail: makeTrailTex() };"
    P.rep(tex, tex + "\n{ const im = new Image(); im.onload = () => { TEX.canopy.image = im; TEX.canopy.needsUpdate = true; }; im.src = 'photos/' + (%s[SEASON] || '%s') + '/canopy.jpg'; }" % (json.dumps(CANOPY_SEASON.get(m.get('base', m['id']), {})), m.get('base', m['id'])), 1)
    P.rep("const seasonGLSL = () => `",
          "const seasonGLSL = () => (SEASON === 'autumn' && BIO.leaf ? `{ float gr = clamp((lit.g - max(lit.r, lit.b))*5.0, 0.0, 1.0); "
          "float h = fract(sin(dot(floor(vWP.xz/9.0), vec2(12.9898, 78.233)))*43758.5453); "
          "vec3 au = lit.g*mix(vec3(1.45, 0.55, 0.22), vec3(1.25, 0.95, 0.3), h); lit = mix(lit, au, gr*0.65); } ` : '') + `", 1)


# 여름·봄 탐방로 둘레 풀꽃: 주황·노랑 한 가지뿐이던 것 → 초록 덤불에 여러 색 꽃 (덤불마다 한 가지 꽃)
# 산마다 그 지역에 실제로 피는 꽃 색으로 (기후 묶음별). 고사리: 봄 연두 / 여름 초록 / 겨울 마른 갈색
KR_SUMMER = [[[250,150,50],[240,128,40]],     # 원추리 주황
             [[176,150,220],[156,128,206]],   # 비비추 연보라
             [[120,150,228],[150,176,236]],   # 산수국 파랑
             [[246,246,240],[236,236,226]],   # 개망초·까치수염 흰색
             [[236,120,160],[246,156,186]],   # 패랭이 분홍
             [[250,214,80],[244,196,60]],     # 기린초 노랑
             [[228,84,60],[240,110,70]]]      # 하늘나리 주홍
KR_SPRING = [[[232,120,170],[244,160,196]], [[214,82,150],[226,110,170]], [[246,240,236],[250,230,236]],
             [[250,220,90],[240,200,70]], [[180,140,220],[200,170,232]]]   # 진달래·철쭉·조팝·생강나무·제비꽃
FLOWERS = {
    'kr': dict(summer=KR_SUMMER, spring=KR_SPRING),
    'kr-south': dict(summer=KR_SUMMER, spring=KR_SPRING),
    'kr-high': dict(summer=KR_SUMMER + [[[232,96,56],[244,128,80]]], spring=KR_SPRING),   # + 동자꽃
    'jp':   dict(summer=[[[150,90,190],[170,110,206]],    # 후지아자미 보라
                         [[246,246,240],[236,236,228]],   # 온타데 흰색
                         [[250,214,80],[240,196,60]],     # 금매화 노랑
                         [[226,120,176],[240,150,196]]],  # 분홍바늘꽃
                 spring=[[[240,180,200],[250,206,220]], [[246,246,240],[236,236,228]], [[250,220,90],[240,200,70]]]),
    'alps': dict(summer=[[[60,90,210],[80,110,226]],       # 용담 파랑
                         [[246,246,240],[230,232,226]],   # 에델바이스 흰색
                         [[250,196,60],[244,176,40]],     # 아르니카 노랑
                         [[214,70,110],[230,96,136]],     # 알펜로제 진분홍
                         [[160,130,220],[180,156,232]]],  # 초롱꽃 연보라
                 spring=[[[246,246,240],[236,236,230]], [[170,120,210],[190,150,226]], [[250,220,80],[240,200,60]]]),   # 크로커스·할미꽃·앵초
    'sierra': dict(summer=[[[130,100,210],[150,124,226]],  # 루핀 보라
                           [[226,70,50],[240,100,70]],     # 인디언붓꽃 주홍
                           [[250,206,60],[240,186,40]],    # 뮬스이어 노랑
                           [[246,244,236],[234,232,222]]], # 야로 흰색
                   spring=[[[130,100,210],[150,124,226]], [[250,206,60],[240,186,40]], [[246,244,236],[234,232,222]]]),
    'cn':   dict(summer=[[[246,246,240],[236,236,228]], [[236,130,170],[246,160,190]], [[250,200,70],[240,180,50]], [[176,150,220],[156,128,206]]],
                 spring=[[[226,90,150],[240,130,180]], [[246,246,240],[236,236,228]], [[250,220,90],[240,200,70]]]),
    'patagonia': dict(summer=[[[250,214,60],[240,196,40]],   # 칼세올라리아 노랑
                              [[214,50,40],[230,80,56]],     # 노트로 빨강
                              [[246,246,240],[236,236,228]], # 흰 들꽃
                              [[150,110,210],[170,136,226]]],# 루핀 보라
                      spring=[[[250,214,60],[240,196,40]], [[246,246,240],[236,236,228]]]),
    'nz':   dict(summer=[[[246,246,240],[236,236,228]],      # 셀미시아·마운트쿡 백합 흰색
                         [[250,214,80],[240,196,60]],        # 미나리아재비 노랑
                         [[214,70,60],[230,96,80]]],         # 라타 빨강
                 spring=[[[246,246,240],[236,236,228]], [[250,214,80],[240,196,60]]]),
}

FLORA_JS = r"""
{ const FL = __FL__;
  const G = [[70,120,52],[84,136,60],[58,104,44]], S = [[110,160,70],[126,174,80],[96,146,60]];
  const L = SEASON === 'summer' ? G : S;
  if(FL[SEASON]){
    SZ.flowerSets = FL[SEASON].map(f => [...L, ...f]).concat([L.concat([[96,150,66]])]);   // + 꽃 없는 초록 덤불
    if(SEASON === 'summer') SZ.flowerAmt = Math.max(SZ.flowerAmt || 0, 0.16);
    else SZ.flowerAmt = Math.max(SZ.flowerAmt || 0, 0.1);
  }
  SZ.fern = { spring: [[[120,170,70],[140,186,84],[104,150,60]], [[150,192,92],[130,176,76],[166,202,104]]],
              summer: [[[56,112,44],[70,128,52],[46,98,38]], [[82,140,58],[64,122,48],[98,154,68]]],
              winter: [[[150,128,100],[170,148,118],[128,110,88]], [[160,140,110],[140,120,96],[182,162,132]]] }[SEASON] || null;
}
"""


def patch_far_clumps(P, m):
    # 먼 숲 무리: 수목한계선 위(고산 바위·눈밭)엔 심지 않아요 — 킬리만자로 비탈에 단풍 숲 무늬가 깔리던 것
    # 늘 겨울인 산(에베레스트·킬리만자로)의 숲은 짙은 상록 숲 색으로
    if m.get('base', m['id']) not in FAR_READY: return
    P.rep("if(sl > 0.9 || (h > 600 && sl > 0.55)) continue;", "if(sl > 0.9 || (h > 600 && sl > 0.55) || h > BIO.tt + 60) continue;", 1)
    P.rep("const pals=SZ.pals ? (", "const pals=SEASON === 'fixed' ? [[[44,66,40],[36,56,34],[58,80,48],[30,46,28]],[[52,74,44],[40,62,36],[66,88,52],[34,50,30]],[[40,62,36],[34,54,30],[56,78,42],[30,48,28]],[[70,84,52],[56,72,44],[82,96,60],[46,60,38]]] : SZ.pals ? (", 1)


def patch_flora(P, m):
    if m.get('base', m['id']) not in FAR_READY: return
    fl = FLOWERS.get(m.get('climate', 'kr'), {})
    P.rep("Object.assign(SZ, SZX[SEASON] || {});", "Object.assign(SZ, SZX[SEASON] || {});" + FLORA_JS.replace('__FL__', json.dumps(fl, separators=(',', ':'))), 1)
    P.rep("const PV = { grass:2, reed:2, fern:2, bushRed:2, bushOak:2, bushGreen:1 };",
          "const PV = { grass:2, reed:2, fern:2, bushRed:(SZ.flowerSets ? SZ.flowerSets.length : 2), bushOak:2, bushGreen:1 };", 1)
    P.rep("const pal = kind==='bushRed' ? (SZ.flower ||", "const pal = kind==='bushRed' ? ((SZ.flowerSets && SZ.flowerSets[v % SZ.flowerSets.length]) || SZ.flower ||", 1)
    P.rep("const cols = v? [[132,92,44],[150,104,50],[110,76,38]] : [[96,104,50],[120,110,52],[80,88,42]];",
          "const cols = SZ.fern ? SZ.fern[v ? 1 : 0] : (v? [[132,92,44],[150,104,50],[110,76,38]] : [[96,104,50],[120,110,52],[80,88,42]]);", 1)
