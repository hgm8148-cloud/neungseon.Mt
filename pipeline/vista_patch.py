"""높은 산의 먼 풍경 (산 설정의 "vista3d"):
- 구름바다 높이를 실제 해발로 (예전: 들머리 기준 200~300m 위 → 킬리만자로는 해발 5,200m 구름이 마웬지 봉까지 덮었어요)
- 먼 산에만 낮은 설선 (가까운 탐방로 바닥은 그대로)
- 지평선 너머 능선을 눈 덮인 산줄기로, 실제 먼 봉우리(예: 메루 산)를 제 방향에 솟게"""
import json, math

# 먼 산줄기 바위·눈 결 (세로로 흘러내리는 골짜기 줄기 + 잔무늬) — 꼭짓점 색(바위/눈)에 곱해져요
RIDGE_TEX_JS = r"""  const RIDGE_TEX = (() => { const c = pixelCanvas(512, (u, v) => {
      const g = pfbm(u*6, v*6, 6, 4), d = pfbm(u*24 + 3, v*24, 24, 3), s = Math.abs(g*2 - 1);
      const val = Math.min(1, 0.8 + 0.2*THREE.MathUtils.smoothstep(s, 0.02, 0.5) + (d - 0.5)*0.06);
      return [255*val, 255*val, 255*Math.min(1, val*1.02)]; });
    return toTex(c); })();
"""

# 구름바다 위 뭉게구름 (점 스프라이트: 위는 햇빛에 밝고 아래는 푸른 그늘)
PUFF_JS = r"""{
  // 구름바다 윗면: 뭉게뭉게 솟은 결을 셰이더로 (높이 잡음 → 법선 → 햇빛·그늘·먼 곳 안개)
  PUFF_M = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, fog: false,
    uniforms: { uSun: {value: new THREE.Vector3(0.4, 0.8, 0.3)}, uDay: {value: 1}, uTint: {value: new THREE.Color(0xdfe7f2)}, uCam: {value: new THREE.Vector3()}, uTime: {value: 0} },
    vertexShader: 'varying vec3 vW; void main(){ vec4 w = modelMatrix*vec4(position,1.0); vW = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; }',
    fragmentShader: `precision highp float; uniform vec3 uSun; uniform float uDay; uniform vec3 uTint; uniform vec3 uCam; uniform float uTime; varying vec3 vW;
      float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7)))*43758.5453); }
      float noise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f); return mix(mix(hash(i), hash(i+vec2(1.0,0.0)), f.x), mix(hash(i+vec2(0.0,1.0)), hash(i+vec2(1.0,1.0)), f.x), f.y); }
      float fbm(vec2 p){ float v = 0.0, a = 0.5; for(int i = 0; i < 5; i++){ v += a*noise(p); p = p*2.03 + vec2(1.7, 9.2); a *= 0.5; } return v; }
      float H(vec2 p){ return fbm(p/5200.0)*0.6 + pow(fbm(p/1500.0 + 3.1), 1.3)*0.5; }
      void main(){
        vec2 p = vW.xz + vec2(uTime*4.0, uTime*1.6);
        float h = H(p), e = 90.0, hx = H(p + vec2(e, 0.0)) - h, hz = H(p + vec2(0.0, e)) - h;
        vec3 n = normalize(vec3(-hx*55.0, 1.0, -hz*55.0));
        float d = length(vW.xz - uCam.xz), lam = mix(clamp(dot(n, normalize(uSun)), 0.0, 1.0), 0.7, smoothstep(4000.0, 24000.0, d)), ao = smoothstep(0.3, 0.8, h);
        vec3 col = mix(vec3(0.7, 0.75, 0.86), vec3(1.0, 0.99, 0.96), clamp(lam*0.7 + ao*0.4, 0.0, 1.0));
        col = mix(col, uTint, smoothstep(5000.0, 42000.0, d)*0.7);
        float a = smoothstep(0.3, 0.46, h) * (1.0 - smoothstep(42000.0, 52000.0, d)) * smoothstep(700.0, 1800.0, d);
        gl_FragColor = vec4(col*(0.3 + 0.7*uDay), a*0.97);
      }` });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(110000, 110000), PUFF_M); m.rotation.x = -Math.PI/2; m.position.y = __CS__ + 55; m.renderOrder = 2; m.frustumCulled = false; scene.add(m);
}
"""


def patch_vista(P, m, meta):
    v = m.get('vista3d')
    if not v: return
    base = meta['BASE']
    if 'cloudSea' in v:
        cs = round(v['cloudSea'] - base)
        P.rep("for(const L of [{y:205, op:0.97", "for(const L of [{y:%d, op:0.97" % cs, 1)
        P.rep("{y:250, op:0.6", "{y:%d, op:0.25" % (cs + 60), 1)
        P.rep("{y:300, op:0.3", "{y:%d, op:0.12" % (cs + 130), 1)
        # 구름바다를 지평선(46km)까지 넓혀요 — 예전엔 28km에서 끊겨 그 너머 평원 가장자리가 네모난 덩어리처럼 보였어요
        P.rep("(1.0 - smoothstep(16000.0, 28000.0, length(vCW)))", "(1.0 - smoothstep(42000.0, 52000.0, length(vCW)))", 1)
        P.rep("const mesh = new THREE.Mesh(new THREE.PlaneGeometry(60000, 60000), m);", "const mesh = new THREE.Mesh(new THREE.PlaneGeometry(110000, 110000), m);", 1)
        # 원경 바닥(23~46km)이 들머리 높이에 떠 있던 것 → 구름바다 높이로, 구름빛으로 (지평선까지 구름바다)
        P.rep("new THREE.MeshBasicMaterial({color:0x6f7468, fog:true}));\n    m.position.y = -20;", "new THREE.MeshBasicMaterial({color:0xeef1f5, fog:true}));\n    m.position.y = %d;" % (cs - 20), 1)
        P.rep("const _cl = new THREE.Color(); const RIDGES = [];", "const _cl = new THREE.Color(); const RIDGES = []; let PUFF_M = null;", 1)
        P.rep("for(const c of CLOUDSEA){ c.m.opacity = c.op*(0.32 + 0.68*day);", "if(PUFF_M){ const U = PUFF_M.uniforms; U.uDay.value = day; U.uTint.value.copy(scene.fog.color); U.uCam.value.copy(camera.position); U.uTime.value = performance.now()/1000; const sl = scene.children.find(o => o.isDirectionalLight); if(sl) U.uSun.value.copy(sl.position).normalize(); }\n  for(const c of CLOUDSEA){ c.m.opacity = c.op*(0.32 + 0.68*day);", 1)
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
              "      const u = a*L.R/7000; uvs.push(u, VLOW/9000, u, mid/9000, u, mid/9000, u, hgt/9000);\n"
              "      if(i>0){ const k=i*4; idx.push(k-4,k,k-3, k-3,k,k+1, k-2,k+2,k-1, k-1,k+2,k+3); }", 1)
        P.rep("const segs = 720, pos = [], cols = [], idx = [];", "const segs = 720, pos = [], cols = [], idx = [], uvs = [];", 1)
        P.rep("g.setAttribute('color', new THREE.Float32BufferAttribute(cols,3)); g.setIndex(idx);", "g.setAttribute('color', new THREE.Float32BufferAttribute(cols,3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uvs,2)); g.setIndex(idx);", 1)
        P.rep("new THREE.MeshBasicMaterial({vertexColors:true, fog:false, side:THREE.DoubleSide, toneMapped:false})", "new THREE.MeshBasicMaterial({vertexColors:true, map:RIDGE_TEX, fog:false, side:THREE.DoubleSide, toneMapped:false})", 1)
        P.rep("  const layers = [\n", RIDGE_TEX_JS + "  const layers = [\n", 1)
        P.rep("  const layers = [\n", "  const VPEAKS = %s, VSNOW = %d, VLOW = %d;\n  const layers = [\n" % (json.dumps(peaks), sn, round(r['base'] - base - 1500)), 1)
