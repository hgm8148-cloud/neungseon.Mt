"""출시 전 최종 점검(리허설)에서 찾은 문제 고치기 (2026-11-03)

1) 먼 산 숲: 어느 계절이든 단풍 사진 질감이 그대로 보였어요 → 봄 연둣빛·여름 짙은 초록·겨울 앙상한 회갈색+눈으로.
"""

FAR_JS = r'''
// 먼 산 숲 색을 계절에 맞게 (pipeline/release_patch.py)
const FAR_SEASON = () => { let S = 'autumn'; try{ S = SEASON; }catch(e){}
  const snow = Math.min(1, (SZ && SZ.snow) || 0);
  if(S === 'spring') return 'float fl = dot(forest, vec3(0.3,0.59,0.11)); forest = mix(forest, fl*vec3(0.98,1.24,0.62), 0.82);';
  if(S === 'summer') return 'float fl = dot(forest, vec3(0.3,0.59,0.11)); forest = mix(forest, fl*vec3(0.6,1.02,0.46), 0.9);';
  if(S === 'winter' || S === 'fixed') return 'float fl = dot(forest, vec3(0.3,0.59,0.11)); forest = mix(forest, fl*vec3(0.78,0.74,0.7), 0.9); forest = mix(forest, vec3(0.62,0.64,0.68)*(0.8 + 0.4*f3.g), ' + (0.25 + 0.5*snow).toFixed(2) + ');';
  return ''; };
'''


def patch_release(P, m):
    P.rep("const FAR_MATS = [];", FAR_JS + "const FAR_MATS = [];", 1)
    P.rep("vec3 forest = mix(f1, f2, 0.35) * (0.75 + 0.5*dot(f3, vec3(0.33)));",
          "vec3 forest = mix(f1, f2, 0.35) * (0.75 + 0.5*dot(f3, vec3(0.33)));\n      ${FAR_SEASON()}", 1)
