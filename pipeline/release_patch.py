"""출시 전 최종 점검(리허설)에서 찾은 문제 고치기 (2026-11-03)

2) 무작위 별명이 다른 언어에서도 한국어로 나왔어요 → 고른 언어로 번역되는 낱말만 골라 그 언어로.
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

    P.rep("const randNick = () => NICK_A[(Math.random()*NICK_A.length)|0]+' '+NICK_B[(Math.random()*NICK_B.length)|0];",
          "const randNick = () => { const L = (window.I18N && I18N.lang) || 'ko', pick = a => a[(Math.random()*a.length)|0];\n"
          "  if(L === 'ko' || typeof T !== 'function') return pick(NICK_A)+' '+pick(NICK_B);\n"
          "  const ok = w => !/\\s/.test(w) && T(w) !== w, A = NICK_A.filter(ok), B = NICK_B.filter(ok);   // 이 언어로 옮길 수 있는 낱말만\n"
          "  let n = A.length && B.length ? T(pick(A)+' '+pick(B)) : 'Hiker ' + (100 + Math.random()*900|0);\n"
          "  if(/^(fr|it|es)$/.test(L)) n = n.charAt(0).toUpperCase() + n.slice(1).toLowerCase();   // rocher Solide → Rocher solide\n"
          "  return n; };", 1)
