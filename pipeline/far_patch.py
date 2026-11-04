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
