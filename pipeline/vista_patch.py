"""높은 산의 먼 풍경 (산 설정의 "vista3d"):
- 구름바다 높이를 실제 해발로 (예전: 들머리 기준 200~300m 위 → 킬리만자로는 해발 5,200m 구름이 마웬지 봉까지 덮었어요)
- 먼 산에만 낮은 설선 (가까운 탐방로 바닥은 그대로)
- 지평선 너머 능선을 눈 덮인 산줄기로, 실제 먼 봉우리(예: 메루 산)를 제 방향에 솟게"""
import json, math


def patch_vista(P, m, meta):
    v = m.get('vista3d')
    if not v: return
    base = meta['BASE']
    if 'cloudSea' in v:
        cs = round(v['cloudSea'] - base)
        P.rep("for(const L of [{y:205, op:0.97", "for(const L of [{y:%d, op:0.97" % cs, 1)
        P.rep("{y:250, op:0.6", "{y:%d, op:0.6" % (cs + 60), 1)
        P.rep("{y:300, op:0.3", "{y:%d, op:0.3" % (cs + 130), 1)
        # 구름바다를 지평선(46km)까지 넓혀요 — 예전엔 28km에서 끊겨 그 너머 평원 가장자리가 네모난 덩어리처럼 보였어요
        P.rep("(1.0 - smoothstep(16000.0, 28000.0, length(vCW)))", "(1.0 - smoothstep(42000.0, 52000.0, length(vCW)))", 1)
        P.rep("const mesh = new THREE.Mesh(new THREE.PlaneGeometry(60000, 60000), m);", "const mesh = new THREE.Mesh(new THREE.PlaneGeometry(110000, 110000), m);", 1)
        # 원경 바닥(23~46km)이 들머리 높이에 떠 있던 것 → 구름바다 높이로, 구름빛으로 (지평선까지 구름바다)
        P.rep("new THREE.MeshBasicMaterial({color:0x6f7468, fog:true}));\n    m.position.y = -20;", "new THREE.MeshBasicMaterial({color:0xeef1f5, fog:true}));\n    m.position.y = %d;" % (cs - 20), 1)
    if 'farSnow' in v:
        P.rep("if(h > BIO.snow - 120){ const s = THREE.MathUtils.smoothstep(h + (vnoise(x/300,z/300)-0.5)*160, BIO.snow-120, BIO.snow+80)",
              "const SNL = Math.max(Math.abs(x), Math.abs(z)) > HALF - 20 ? %d : BIO.snow;\n  if(h > SNL - 120){ const s = THREE.MathUtils.smoothstep(h + (vnoise(x/300,z/300)-0.5)*160, SNL-120, SNL+80)" % round(v['farSnow'] - base), 1)
        # 먼 산 재질은 사진 질감 위주라 꼭짓점 색의 눈이 거의 안 보여요 → 셰이더에서 높이로 눈 덮기
        P.rep("      diffuseColor.rgb = mix(forest*1.5, rk*1.1, rock);`)",
              "      diffuseColor.rgb = mix(forest*1.5, rk*1.1, rock);\n"
              "      { float sn = smoothstep(%.1f, %.1f, vTW3.y + (f3.g-0.5)*180.0) * (0.5 + 0.5*smoothstep(0.35, 0.75, vWN.y)); "
              "diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.92,0.94,0.97)*(0.86 + 0.18*f3.g), sn); }`)" % (v['farSnow'] - base - 120, v['farSnow'] - base + 100), 1)
    r = v.get('ridges')
    if r:
        lat0, lon0 = meta['lat'], meta['lon']
        peaks = []
        for p in r.get('peaks', []):
            x = (p['lon'] - lon0) * 111320 * math.cos(math.radians(lat0)); z = -(p['lat'] - lat0) * 110540
            peaks.append(dict(a=math.atan2(z, x), d=math.hypot(x, z), h=p['elev'] - base))
        sn = round(r['snow'] - base)
        # 능선 높이·색: 아래는 구름 밑으로, 꼭대기는 눈
        # 먼 능선 색이 안개색을 그대로 곱해 눈이 묻혔어요 → 밝기만 따르고 푸른 기는 덜어서 눈·바위 대비를 살려요
        P.rep("for(const rm of RIDGES) rm.color.copy(scene.fog.color).multiplyScalar(1.12);",
              "for(const rm of RIDGES){ rm.color.copy(scene.fog.color).multiplyScalar(1.12); const lu = rm.color.r*0.3 + rm.color.g*0.59 + rm.color.b*0.11; rm.color.lerp(_cl.setRGB(lu, lu, lu), 0.55); }", 1)
        P.rep("new THREE.MeshBasicMaterial({vertexColors:true, fog:false, side:THREE.DoubleSide})", "new THREE.MeshBasicMaterial({vertexColors:true, fog:false, side:THREE.DoubleSide, toneMapped:false})", 1)
        P.rep("{R:36000, amp:1500, base:-100,", "{R:36000, amp:%d, base:%d," % (r['amp'], round(r['base'] - base)), 1)
        P.rep("{R:46000, amp:2000, base:-200,", "{R:46000, amp:%d, base:%d," % (round(r['amp'] * 1.25), round(r['base'] - base - 150)), 1)
        P.rep("      const hgt = L.base + Math.pow(ridge,1.6)*L.amp + n*L.amp*0.25;\n      const x = Math.cos(a)*L.R, z = Math.sin(a)*L.R;\n      pos.push(x, -400, z, x, hgt, z);\n      cols.push(...L.col.map(v=>v*1.08), ...L.top);\n      if(i>0){ const k=i*2; idx.push(k-2,k,k-1, k-1,k,k+1); }",
              "      let hgt = L.base + Math.pow(ridge,1.6)*L.amp + n*L.amp*0.25;\n"
              "      if(L.seed === 3) for(const p of VPEAKS){ let da = Math.abs(a - p.a); da = Math.min(da, Math.PI*2 - da); hgt = Math.max(hgt, p.h*L.R/p.d - da*L.R*0.42); }\n"
              "      const x = Math.cos(a)*L.R, z = Math.sin(a)*L.R, sl = VSNOW - (L.seed === 3 ? 150 : -250) + (vnoise(Math.cos(a)*40, Math.sin(a)*40)-0.5)*420, mid = Math.max(VLOW, Math.min(hgt, sl));\n"
              "      pos.push(x, VLOW, z, x, mid, z, x, mid, z, x, hgt, z);\n"
              "      const seg = L.R*Math.PI*2/segs, sh0 = THREE.MathUtils.clamp((hgt - (L.ph ?? hgt))/seg*1.6, -1, 1), sh = L.ps = (L.ps ?? sh0)*0.6 + sh0*0.4; L.ph = hgt;\n"
              "      const lit = 1 + 0.16*sh, rk = L.col.map(v=>v*0.5*(1+0.25*sh)), rk2 = L.top.map(v=>v*0.56*(1+0.25*sh));\n"
              "      const snowT = sh >= 0 ? [1.24*lit,1.22*lit,1.18*lit] : [0.86*lit,0.92*lit,1.04*lit];\n"
              "      cols.push(...rk, ...rk2, ...snowT.map(v=>v*0.9), ...snowT);\n"
              "      if(i>0){ const k=i*4; idx.push(k-4,k,k-3, k-3,k,k+1, k-2,k+2,k-1, k-1,k+2,k+3); }", 1)
        P.rep("  const layers = [\n", "  const VPEAKS = %s, VSNOW = %d, VLOW = %d;\n  const layers = [\n" % (json.dumps(peaks), sn, round(r['base'] - base - 1500)), 1)
