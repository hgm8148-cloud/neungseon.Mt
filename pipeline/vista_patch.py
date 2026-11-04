"""높은 산의 먼 풍경 (산 설정의 "vista3d"):
- 구름바다 높이를 실제 해발로 (예전: 들머리 기준 200~300m 위 → 킬리만자로는 해발 5,200m 구름이 마웬지 봉까지 덮었어요)
- 먼 산에만 낮은 설선 (가까운 탐방로 바닥은 그대로)
- 지평선 너머 능선을 눈 덮인 산줄기로, 실제 먼 봉우리(예: 메루 산)를 제 방향에 솟게"""
import json, math

# 먼 산줄기 바위·눈 결 (세로로 흘러내리는 골짜기 줄기 + 잔무늬) — 꼭짓점 색(바위/눈)에 곱해져요
RIDGE_TEX_JS = r"""  const RIDGE_TEX = (() => { const c = pixelCanvas(512, (u, v) => {
      const g = pfbm(u*16, v*16, 16, 5), d = pfbm(u*64 + 3, v*64, 64, 3), s = Math.abs(g*2 - 1);
      const val = Math.min(1, 0.6 + 0.4*THREE.MathUtils.smoothstep(s, 0.02, 0.4) + (d - 0.5)*0.16);
      return [255*val, 255*val, 255*Math.min(1, val*1.03)]; });
    return toTex(c); })();
"""

# 구름바다 위 뭉게구름 (점 스프라이트: 위는 햇빛에 밝고 아래는 푸른 그늘)
PUFF_JS = r"""{
  const S = 128, c = document.createElement('canvas'); c.width = c.height = S; const x = c.getContext('2d');
  for(let i = 0; i < 9; i++){ const px = S*(0.28 + Math.random()*0.44), py = S*(0.42 + Math.random()*0.2), r = S*(0.16 + Math.random()*0.16);
    const g = x.createRadialGradient(px, py - r*0.35, r*0.1, px, py, r); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.55, 'rgba(236,240,247,0.9)'); g.addColorStop(1, 'rgba(206,216,232,0)');
    x.fillStyle = g; x.beginPath(); x.arc(px, py, r, 0, 7); x.fill(); }
  const sh = x.createLinearGradient(0, S*0.35, 0, S*0.8); sh.addColorStop(0, 'rgba(150,165,195,0)'); sh.addColorStop(1, 'rgba(150,165,195,0.55)');
  x.globalCompositeOperation = 'source-atop'; x.fillStyle = sh; x.fillRect(0, 0, S, S);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  const N = 1400, pos = new Float32Array(N*3), col = new Float32Array(N*3); let n = 0;
  for(let k = 0; k < N*3 && n < N; k++){ const r = 1400 + Math.pow(Math.random(), 0.75)*26000, a = Math.random()*Math.PI*2;
    const px = Math.cos(a)*r, pz = Math.sin(a)*r, cl = vnoise(px/2600, pz/2600); if(cl < 0.38) continue;
    pos[n*3] = px; pos[n*3+1] = __CS__ + 20 + Math.random()*90 + (cl - 0.38)*260; pos[n*3+2] = pz;
    const b = 0.9 + Math.random()*0.1; col[n*3] = b; col[n*3+1] = b; col[n*3+2] = Math.min(1, b*1.03); n++; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos.slice(0, n*3), 3)); g.setAttribute('color', new THREE.BufferAttribute(col.slice(0, n*3), 3));
  PUFF_M = new THREE.PointsMaterial({ map: tex, size: 900, sizeAttenuation: true, transparent: true, depthWrite: false, vertexColors: true, fog: true, alphaTest: 0.02 });
  const pts = new THREE.Points(g, PUFF_M); pts.renderOrder = 2; pts.frustumCulled = false; scene.add(pts);
}
"""


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
        P.rep("const _cl = new THREE.Color(); const RIDGES = [];", "const _cl = new THREE.Color(); const RIDGES = []; let PUFF_M = null;", 1)
        P.rep("for(const c of CLOUDSEA){ c.m.opacity = c.op*(0.32 + 0.68*day);", "if(PUFF_M){ PUFF_M.color.copy(_cl).multiplyScalar(1.02); PUFF_M.opacity = 0.96*(0.25 + 0.75*day); }\n  for(const c of CLOUDSEA){ c.m.opacity = c.op*(0.32 + 0.68*day);", 1)
        P.rep("// 운해: 골짜기와 도시를 덮는 구름 바다, 봉우리만 섬처럼 솟게\n", "// 운해: 골짜기와 도시를 덮는 구름 바다, 봉우리만 섬처럼 솟게\n" + PUFF_JS.replace('__CS__', str(cs)), 1)
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
              "      const seg = L.R*Math.PI*2/segs, sh0 = THREE.MathUtils.clamp((hgt - (L.ph ?? hgt))/seg*1.2, -1, 1), sh = L.ps = (L.ps ?? sh0)*0.8 + sh0*0.2; L.ph = hgt;\n"
              "      const lt = THREE.MathUtils.smoothstep(sh, -0.45, 0.45), haze = L.seed === 3 ? 0 : 0.28;\n"
              "      const mixc = (a, b, t) => a.map((v, j) => v*(1-t) + b[j]*t), HZ = [0.9, 0.94, 1.0];\n"
              "      const rk = mixc(mixc([0.34,0.36,0.42], [0.52,0.54,0.6], lt), HZ, 0.55 + haze), rk2 = mixc(mixc([0.4,0.42,0.48], [0.62,0.63,0.68], lt), HZ, 0.2 + haze);\n"
              "      const snowT = mixc(mixc([0.78,0.86,1.0], [1.26,1.22,1.16], lt), HZ, haze*0.6);\n"
              "      cols.push(...rk, ...rk2, ...snowT.map(v=>v*0.92), ...snowT);\n"
              "      const u = a*L.R/2600; uvs.push(u, VLOW/5200, u, mid/5200, u, mid/5200, u, hgt/5200);\n"
              "      if(i>0){ const k=i*4; idx.push(k-4,k,k-3, k-3,k,k+1, k-2,k+2,k-1, k-1,k+2,k+3); }", 1)
        P.rep("const segs = 720, pos = [], cols = [], idx = [];", "const segs = 720, pos = [], cols = [], idx = [], uvs = [];", 1)
        P.rep("g.setAttribute('color', new THREE.Float32BufferAttribute(cols,3)); g.setIndex(idx);", "g.setAttribute('color', new THREE.Float32BufferAttribute(cols,3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uvs,2)); g.setIndex(idx);", 1)
        P.rep("new THREE.MeshBasicMaterial({vertexColors:true, fog:false, side:THREE.DoubleSide, toneMapped:false})", "new THREE.MeshBasicMaterial({vertexColors:true, map:RIDGE_TEX, fog:false, side:THREE.DoubleSide, toneMapped:false})", 1)
        P.rep("  const layers = [\n", RIDGE_TEX_JS + "  const layers = [\n", 1)
        P.rep("  const layers = [\n", "  const VPEAKS = %s, VSNOW = %d, VLOW = %d;\n  const layers = [\n" % (json.dumps(peaks), sn, round(r['base'] - base - 1500)), 1)
