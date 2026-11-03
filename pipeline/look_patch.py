"""산 사진의 바위 색을 게임 바위에 입혀요 (2026-11-03)

photos/look.json (make_look.py 가 사진에서 뽑은 색) →
- 가까운 바위·화강암 노두·물가 바위 색을 그 산 사진의 바위 색 쪽으로 (70%)
- 먼 산 바위 색(TOON_ROCK)도 같은 색 쪽으로
그래서 황산·트레치메는 회갈색, 몽블랑·월출산은 밝은 회백색, 토레스 델 파이네는 짙은 회색처럼 산마다 달라 보여요.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def patch_look(P, m):
    # 나무가 없는 높은 산(에베레스트·킬리만자로)의 먼 골짜기가 단풍색으로 보이던 것 → 흙·자갈 색
    P.rep("const TOON_ROCK = new THREE.Color(0xb3ada2), TOON_ROCK2 = new THREE.Color(0x8f8a82);",
          "const TOON_ROCK = new THREE.Color(0xb3ada2), TOON_ROCK2 = new THREE.Color(0x8f8a82);\n"
          "if(!SZ.toon && BIO.dens === 0) [0x7a6e60, 0x8a7c6a, 0x6e6458, 0x9a8a74, 0x857565, 0x6a5e52, 0x7e7466].forEach((c, i) => TOON_PAL[i] && TOON_PAL[i].set(c));", 1)
    try: L = json.load(open(os.path.join(HERE, 'photos', 'look.json'))).get(m['id'])
    except Exception: L = None
    if not L or m.get('legacy'): return
    r, g, b = L['rock']
    P.rep("const TOON_ROCK = new THREE.Color(0xb3ada2), TOON_ROCK2 = new THREE.Color(0x8f8a82);",
          "const TOON_ROCK = new THREE.Color(0xb3ada2), TOON_ROCK2 = new THREE.Color(0x8f8a82);\n"
          f"const LOOK_ROCK = new THREE.Color({r}, {g}, {b});   // 사진에서 뽑은 바위 색 (pipeline/look_patch.py)\n"
          "TOON_ROCK.lerp(LOOK_ROCK, 0.65); TOON_ROCK2.lerp(LOOK_ROCK.clone().multiplyScalar(0.8), 0.65);", 1)
    P.rep("window.__game = {",
          "// 가까운 바위 색도 사진 쪽으로\n"
          "{ const img = TEX.granite.image; let avg = new THREE.Color(0.75, 0.74, 0.72);\n"
          "  try{ const c = document.createElement('canvas'); c.width = c.height = 32; const x = c.getContext('2d'); x.drawImage(img, 0, 0, 32, 32); const d = x.getImageData(0,0,32,32).data; let s = [0,0,0]; for(let i=0;i<d.length;i+=4){ s[0]+=d[i]; s[1]+=d[i+1]; s[2]+=d[i+2]; } avg = new THREE.Color(s[0]/1024/255, s[1]/1024/255, s[2]/1024/255).convertSRGBToLinear(); }catch(e){}\n"
          "  const want = LOOK_ROCK.clone().convertSRGBToLinear(), k = ['r','g','b'];\n"
          "  scene.traverse(o => { if(!o.isInstancedMesh || o.geometry.type !== 'IcosahedronGeometry' || !o.material.map) return; const c = o.material.color, base = c.clone();\n"
          "    for(const q of k) c[q] = THREE.MathUtils.lerp(base[q], THREE.MathUtils.clamp(want[q]/Math.max(0.05, avg[q]), 0.35, 1.6), 0.7); }); }\n"
          "window.__game = {", 1)
