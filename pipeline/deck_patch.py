"""전망 포인트 데크 위에 서기 (2026-11-06 승연 '전망포인트 데크 평상 위에 사람이 올라가게 수정해줘')

예전에는 데크가 탐방로 높이에 평평하게 놓이고 사람은 땅 높이에 서서, 비탈에서는 사람이 데크 속에 묻혀 보였어요.
- 데크 바닥을 그 자리 땅의 가장 높은 곳 위로 올리고, 낮은 쪽은 나무 기둥으로 받쳐요.
- 데크 위(발판 범위)에서는 내 캐릭터·다른 사람 아바타·NPC 모두 데크 바닥 위에 서요 (standY 하나로 처리).
모든 산에 똑같이 적용돼요.
"""

DECK_OLD = ("    const deck = new THREE.Mesh(new THREE.BoxGeometry(2.6,0.12,1.8), wood); deck.position.set(p.x+Math.sin(dir)*1.2, p.h+0.05, p.z+Math.cos(dir)*1.2); "
            "deck.rotation.y = dir; deck.receiveShadow=true; scene.add(deck);")

DECK_NEW = r"""    { // 데크: 땅 위로 올리고 기둥으로 받치기 + 서는 높이 등록 (pipeline/deck_patch.py)
      const cx = p.x+Math.sin(dir)*1.2, cz = p.z+Math.cos(dir)*1.2, ca = Math.cos(dir), sa = Math.sin(dir), HW = 1.3, HD = 0.9;
      const at = (a, b) => [cx + ca*a + sa*b, cz - sa*a + Math.cos(dir)*b];
      let top = p.h;
      for(let a = -HW; a <= HW + 1e-6; a += HW/2) for(let b = -HD; b <= HD + 1e-6; b += HD/2){ const [x, z] = at(a, b); top = Math.max(top, heightAt(x, z)); }
      top += 0.14;
      const deck = new THREE.Mesh(new THREE.BoxGeometry(HW*2, 0.1, HD*2), wood); deck.position.set(cx, top - 0.05, cz); deck.rotation.y = dir; deck.receiveShadow = true; deck.castShadow = true; scene.add(deck);
      for(const a of [-HW+0.1, 0, HW-0.1]) for(const b of [-HD+0.1, HD-0.1]){ const [x, z] = at(a, b), g0 = heightAt(x, z) - 0.15, L = top - 0.1 - g0; if(L < 0.05) continue;
        const leg = new THREE.Mesh(new THREE.BoxGeometry(0.11, L, 0.11), wood); leg.position.set(x, g0 + L/2, z); leg.rotation.y = dir; leg.castShadow = true; scene.add(leg); }
      VP_DECKS.push({ x: cx, z: cz, ca, sa, hw: HW, hd: HD, top });
    }"""

STAND_OLD = "function standY(x, z, ni){"
STAND_NEW = r"""// 전망 포인트 데크 위에 서기 (pipeline/deck_patch.py)
var VP_DECKS = window.__vpDecks = [];
function vpDeckY(x, z){ if(!VP_DECKS) return null; for(const d of VP_DECKS){ const dx = x - d.x, dz = z - d.z, a = dx*d.ca - dz*d.sa, b = dx*d.sa + dz*d.ca; if(Math.abs(a) <= d.hw + 0.05 && Math.abs(b) <= d.hd + 0.05) return d.top; } return null; }
function standY(x, z, ni){ const y0 = standY0(x, z, ni), dk = vpDeckY(x, z); return dk != null && dk > y0 ? dk : y0; }
function standY0(x, z, ni){"""


def patch_deck(P, m):
    P.rep(DECK_OLD, DECK_NEW, 1)
    P.rep(STAND_OLD, STAND_NEW, 1)
