"""달: 낮에 어두운 쪽이 회색 원반으로 남아 월식처럼 보이던 것 수정.
- 빛 안 받는 쪽은 투명 (밤에만 아주 옅은 지구照)
- 크기 1.5배, 바다(어두운 무늬)가 또렷하게 대비를 올림, 가장자리 살짝 어둡게
- 낮달도 조금 더 또렷하게"""


def patch_moon(P, m):
    P.rep("uniforms:{ map:{value:null}, phase:{value:Math.PI}, op:{value:0} }",
          "uniforms:{ map:{value:null}, phase:{value:Math.PI}, op:{value:0}, earth:{value:0} }", 1)
    P.rep("uniform float phase, op; varying vec2 vU;", "uniform float phase, op, earth; varying vec2 vU;", 1)
    P.rep("float lit = smoothstep(-0.05, 0.07, dot(n, L));", "float lit = smoothstep(-0.03, 0.09, dot(n, L));", 1)
    P.rep("vec3 c = t.rgb*(0.035 + lit*1.3)*vec3(1.0, 0.98, 0.93); gl_FragColor = vec4(c, op*smoothstep(1.0, 0.94, r2)); }",
          "float lum = dot(t.rgb, vec3(0.299, 0.587, 0.114)); vec3 tc = clamp((mix(vec3(lum), t.rgb, 0.5) - 0.5)*1.6 + 0.56, 0.0, 1.0);"
          " vec3 c = tc*(0.8 + 0.2*n.z)*1.2*vec3(1.0, 0.98, 0.93)*(lit + (1.0 - lit)*0.3);"
          " gl_FragColor = vec4(c, op*smoothstep(1.0, 0.96, r2)*(lit + (1.0 - lit)*earth)); }", 1)
    P.rep("+ up*0.25*(1-night);", "+ up*0.6*(1-night); MOON.mat.uniforms.earth.value = 0.14*night;", 1)
    P.rep("MOON.mesh.scale.setScalar(250);", "MOON.mesh.scale.setScalar(380);", 1)
    P.rep("MOON.glow.scale.setScalar(2600);", "MOON.glow.scale.setScalar(3400);", 1)
    patch_big_moon(P)


def patch_big_moon(P):
    """밤엔 언제나 크고 둥근 달 (2026-11-06, 승연 요청 '밤에 예쁘고 큰 달').
    - 밤이 되면 실제 날짜와 상관없이 보름달이, 이 산 정상 쪽 하늘 낮은 곳(약 34~46°)에 떠요.
      밤새 조금씩 오른쪽으로 움직이며 올라가요. 낮엔 지금처럼 실제 날짜의 낮달.
    - 크기 약 3배(달 원반은 무리 한가운데를 비워 무늬가 또렷하게), 낮게 뜰수록 더 커 보이고(달 착시) 살짝 금빛.
    - 달무리를 더 부드럽고 넓게."""
    # 셰이더: 낮게 뜬 달은 살짝 금빛
    P.rep("uniforms:{ map:{value:null}, phase:{value:Math.PI}, op:{value:0}, earth:{value:0} }",
          "uniforms:{ map:{value:null}, phase:{value:Math.PI}, op:{value:0}, earth:{value:0}, warm:{value:0} }", 1)
    P.rep("uniform float phase, op, earth; varying vec2 vU;", "uniform float phase, op, earth, warm; varying vec2 vU;", 1)
    P.rep("*(lit + (1.0 - lit)*0.3); gl_FragColor",
          "*(lit + (1.0 - lit)*0.3)*mix(vec3(1.0), vec3(1.06, 0.9, 0.7), warm); gl_FragColor", 1)
    # 달무리: 달 둘레는 밝고 바깥으로 길게 번지게
    P.rep("g.addColorStop(0,'rgba(230,236,255,.55)'); g.addColorStop(0.18,'rgba(210,222,255,.22)'); g.addColorStop(0.5,'rgba(190,205,255,.06)'); g.addColorStop(1,'rgba(190,205,255,0)');",
          "g.addColorStop(0,'rgba(255,250,236,.04)'); g.addColorStop(0.118,'rgba(255,250,236,.05)'); g.addColorStop(0.132,'rgba(250,246,234,.36)'); g.addColorStop(0.2,'rgba(226,232,250,.15)'); g.addColorStop(0.45,'rgba(196,210,250,.05)'); g.addColorStop(1,'rgba(190,205,255,0)');", 1)
    # 위치·모양: 밤엔 정상 쪽 하늘의 보름달, 낮엔 실제 달. 바뀌는 순간은 잠깐 사라졌다 나타나게.
    P.rep("{ const age = moonAge(), ph = age/29.530589*Math.PI*2, md = MOON.dir;\n"
          "    if(SKY.moonForce) md.set(0.55, 0.5, 0.67).normalize(); else md.copy(sunAtHour(SKY.h - age*0.8127, dayOfYear() + age*12.37));",
          "{ const nb = SKY.moonForce ? 1 : THREE.MathUtils.smoothstep(night, 0.2, 0.6), pretty = nb > 0.5, age = pretty ? 14.77 : moonAge(), ph = age/29.530589*Math.PI*2, md = MOON.dir;\n"
          "    if(pretty) md.copy(bigMoonDir(SKY.h)); else md.copy(sunAtHour(SKY.h - age*0.8127, dayOfYear() + age*12.37));", 1)
    P.rep("MOON.mat.uniforms.earth.value = 0.14*night;",
          "MOON.mat.uniforms.earth.value = 0.14*night; MOON.mat.uniforms.op.value *= Math.abs(nb*2 - 1); MOON.mat.uniforms.warm.value = 0.55*(1 - THREE.MathUtils.smoothstep(md.y, 0.12, 0.62));", 1)
    P.rep("MOON.mesh.scale.setScalar(380);", "const big = 1 + 0.15*(1 - THREE.MathUtils.smoothstep(md.y, 0.2, 0.6)); MOON.mesh.scale.setScalar(pretty ? 840*big : 266);   // 2026-11-11 승연: 달 크기 70%", 1)
    P.rep("MOON.glow.scale.setScalar(3400); MOON.glow.material.opacity = MOON.amt*0.9;",
          "MOON.glow.scale.setScalar(6552*big); MOON.glow.material.opacity = MOON.amt*0.95*Math.abs(nb*2 - 1);", 1)
    P.rep("function moonAge(){",
          "// 밤의 큰 달 방향: 들머리→정상 쪽(조금 오른쪽) 하늘, 저녁 6시 고도 34° → 새벽 6시 46° (봉우리·능선에 가리지 않게), 밤새 동→서 쪽으로 천천히\n"
          "function bigMoonDir(h){ if(!MOON.az){ const a = trail[0], b = trail[trail.length - 1]; MOON.az = Math.atan2(b.x - a.x, b.z - a.z); }\n"
          "  const k = THREE.MathUtils.clamp(((h - 18 + 24) % 24)/12, 0, 1), az = MOON.az + 0.5 - 0.35 + k*0.7, el = 0.6 + k*0.2;\n"
          "  return (MOON.bv || (MOON.bv = new THREE.Vector3())).set(Math.sin(az)*Math.cos(el), Math.sin(el), Math.cos(az)*Math.cos(el)); }\n"
          "function moonAge(){", 1)
