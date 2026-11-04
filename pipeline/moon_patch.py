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
