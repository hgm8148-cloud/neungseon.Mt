"""저사양 휴대폰 자동 최적화 (2026-11-06 승연 '사양이 낮은 스마트폰을 위한 사양 자동 최적화 기능 넣어줘')

화질 단계 3가지: 높음(지금까지와 같음) · 보통 · 낮음
- 처음 열 때: 기기 메모리·CPU 코어·GPU 이름으로 단계를 골라요 (오래된 Mali·Adreno·PowerVR, 메모리 2~4GB 폰 등).
- 걷는 동안: 3초마다 초당 화면 수(FPS)를 재서 버벅이면 해상도를 조금씩 낮추고,
  그래도 느리면 한 단계 내려요 (그림자 끄기·나무와 풀 줄이기). 여유가 생기면 해상도만 다시 올려요.
- 한 번 내려간 단계는 기기에 14일 동안 기억해서 다음 방문 때 처음부터 가볍게 시작해요.
- 메뉴의 '화질' 버튼: 자동 → 높음 → 보통 → 낮음 순서로 직접 고를 수 있어요 (localStorage neungseon.gfx).

나무·풀은 그릴 때만 개수를 줄이고 그린 뒤 원래 개수로 되돌려서,
명소 자리 나무 치우기처럼 o.count 로 돌며 고치는 다른 코드에는 영향이 없어요.
game.template.html 은 고치지 않고 빌드할 때 덧대요.
"""

# 번역: ko, en, ja, zh, de, fr, it, es, ne, sw
GFX_ROWS = [
    ['화질 바꾸기', 'Change graphics quality', '画質を変更', '更改画质', 'Grafikqualität ändern', 'Changer la qualité graphique', 'Cambia qualità grafica', 'Cambiar calidad gráfica', 'ग्राफिक्स गुणस्तर बदल्नुहोस्', 'Badilisha ubora wa picha'],
    ['화질', 'Graphics', '画質', '画质', 'Grafik', 'Graphismes', 'Grafica', 'Gráficos', 'ग्राफिक्स', 'Picha'],
    ['화질: 자동', 'Graphics: Auto', '画質: 自動', '画质: 自动', 'Grafik: Automatisch', 'Graphismes : Auto', 'Grafica: Automatica', 'Gráficos: Automático', 'ग्राफिक्स: स्वचालित', 'Picha: Kiotomatiki'],
    ['화질: 높음', 'Graphics: High', '画質: 高', '画质: 高', 'Grafik: Hoch', 'Graphismes : Élevés', 'Grafica: Alta', 'Gráficos: Altos', 'ग्राफिक्स: उच्च', 'Picha: Juu'],
    ['화질: 보통', 'Graphics: Medium', '画質: 中', '画质: 中', 'Grafik: Mittel', 'Graphismes : Moyens', 'Grafica: Media', 'Gráficos: Medios', 'ग्राफिक्स: मध्यम', 'Picha: Wastani'],
    ['화질: 낮음', 'Graphics: Low', '画質: 低', '画质: 低', 'Grafik: Niedrig', 'Graphismes : Bas', 'Grafica: Bassa', 'Gráficos: Bajos', 'ग्राफिक्स: न्यून', 'Picha: Chini'],
    ['지금 높음', 'now High', '現在 高', '当前 高', 'jetzt Hoch', 'actuellement Élevés', 'ora Alta', 'ahora Altos', 'अहिले उच्च', 'sasa Juu'],
    ['지금 보통', 'now Medium', '現在 中', '当前 中', 'jetzt Mittel', 'actuellement Moyens', 'ora Media', 'ahora Medios', 'अहिले मध्यम', 'sasa Wastani'],
    ['지금 낮음', 'now Low', '現在 低', '当前 低', 'jetzt Niedrig', 'actuellement Bas', 'ora Bassa', 'ahora Bajos', 'अहिले न्यून', 'sasa Chini'],
    ['기기에 맞춰 저절로 조절해요', 'Adjusts to your device automatically', '端末に合わせて自動で調整します', '根据设备自动调整', 'Passt sich automatisch an dein Gerät an', 'S’adapte automatiquement à votre appareil', 'Si adatta automaticamente al dispositivo', 'Se ajusta solo a tu dispositivo', 'तपाईंको उपकरण अनुसार आफैँ मिल्छ', 'Hujirekebisha kulingana na kifaa chako'],
    ['화면이 부드럽게 움직이도록 화질을 조금 낮췄어요', 'Lowered the graphics a little so it runs smoothly', 'なめらかに動くよう画質を少し下げました', '为了画面流畅，已稍微降低画质', 'Grafik etwas reduziert, damit alles flüssig läuft', 'Graphismes un peu réduits pour plus de fluidité', 'Grafica ridotta un po’ per una maggiore fluidità', 'Bajamos un poco los gráficos para que vaya fluido', 'सहज चलोस् भनेर ग्राफिक्स अलि घटाइयो', 'Ubora wa picha umepunguzwa kidogo ili kwenda vizuri'],
]

# 렌더러를 만들기 전에 단계를 정해요 (안티에일리어싱은 만들 때만 정할 수 있어서)
GFX_JS = r'''// 화질 자동 조절 (pipeline/perf_patch.py): 기기 판별 → 시작 단계, FPS 측정 → 해상도·단계 낮추기
const GFX = window.__GFX = (() => {
  const K = 'neungseon.gfx', KA = 'neungseon.gfxAuto', TOUCH = document.body.classList.contains('touch');
  const ls = { get(k){ try { return localStorage.getItem(k); } catch(e){ return null; } }, set(k, v){ try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch(e){} } };
  const NAME = ['낮음', '보통', '높음'], MODES = ['auto', 'high', 'mid', 'low'], IDX = { low:0, mid:1, high:2 };
  // 단계별 값: 최대 화소 비율 · 동적 해상도 하한 · 그림자 · 그림자 지도 크기 · 나무 비율 · 풀 비율
  const PR = [1, 1.25, TOUCH ? 1.5 : 2], SMIN = [0.7, 0.8, 0.85], SH = [false, true, true], SHS = [0, 1024, TOUCH ? 1024 : 2048], TREE = [0.6, 0.85, 1], PLANT = [0.4, 0.7, 1];
  let gpu = '';
  try { const c = document.createElement('canvas'), g = c.getContext('webgl2') || c.getContext('webgl');
    if(g){ const e = g.getExtension('WEBGL_debug_renderer_info'); gpu = String((e && g.getParameter(e.UNMASKED_RENDERER_WEBGL)) || g.getParameter(g.RENDERER) || ''); const l = g.getExtension('WEBGL_lose_context'); if(l) l.loseContext(); }
  } catch(e){}
  const mem = navigator.deviceMemory || 0, cores = navigator.hardwareConcurrency || 0;
  function detect(){
    const G = gpu.toLowerCase(); let t = 2, m;
    if(/swiftshader|llvmpipe|softpipe|software|microsoft basic/.test(G)) return 0;
    if(/mali-[34]\d\d|mali-t\d|powervr|sgx|videocore|vivante|tegra 3|tegra 4/.test(G)) t = 0;
    else if((m = G.match(/adreno\D*(\d{3})/))){ const n = +m[1]; t = n < 530 ? 0 : n < 640 ? 1 : 2; }
    else if((m = G.match(/mali-g(\d+)/))){ const n = +m[1]; t = n <= 52 ? 0 : n <= 76 ? 1 : 2; }
    else if(/intel.*hd graphics( \d{3,4})?\b/.test(G) && !/iris/.test(G)) t = 1;
    if(TOUCH){
      if((mem && mem <= 2) || (cores && cores <= 4)) t = Math.min(t, 0);
      else if((mem && mem <= 4) || (cores && cores <= 6)) t = Math.min(t, 1);
    } else if(mem && mem <= 2) t = Math.min(t, 1);
    return t;
  }
  const base = detect();
  let learned = 2; try { const a = JSON.parse(ls.get(KA) || 'null'); if(a && Date.now() - a.ts < 14*864e5) learned = a.t; } catch(e){}
  let mode = MODES.includes(ls.get(K)) ? ls.get(K) : 'auto';
  let tier = mode === 'auto' ? Math.min(base, learned) : IDX[mode], scale = 1, R = null, SUN = null, veg = [];
  const T_ = s => (window.T || (x => x))(s);
  function apply(){
    if(!R) return;
    R.setPixelRatio(Math.max(0.5, Math.min(devicePixelRatio || 1, PR[tier]) * scale));
    if(SUN){ SUN.castShadow = SH[tier];
      if(SH[tier] && SUN.shadow.mapSize.x !== SHS[tier]){ SUN.shadow.mapSize.set(SHS[tier], SHS[tier]); if(SUN.shadow.map){ SUN.shadow.map.dispose(); SUN.shadow.map = null; } } }
  }
  // 나무·풀: 그릴 때(그림자 포함)만 앞쪽 일부만 그리고, 다 그리면 개수를 되돌려요
  function addVeg(list, plant){
    for(const m of list){ const v = { m, plant, keep: m.count, full: 0 };
      const pre = () => { if(v.full) return; v.full = m.count; v.keep = Math.round(m.count * (plant ? PLANT[tier] : TREE[tier])); if(v.keep < m.count) m.count = v.keep; };
      const post = () => { if(v.full) m.count = v.full; v.full = 0; };
      const b1 = m.onBeforeRender, a1 = m.onAfterRender, b2 = m.onBeforeShadow, a2 = m.onAfterShadow;
      m.onBeforeRender = function(...x){ pre(); return b1.apply(this, x); }; m.onAfterRender = function(...x){ post(); return a1.apply(this, x); };
      m.onBeforeShadow = function(...x){ pre(); return b2.apply(this, x); }; m.onAfterShadow = function(...x){ post(); return a2.apply(this, x); };
      veg.push(v); }
  }
  function label(){ return T_(mode === 'auto' ? '화질: 자동' : '화질: ' + NAME[IDX[mode]]); }
  function btn(){ const b = document.getElementById('bGfx'); if(!b) return; const l = label(); b.title = l; b.setAttribute('aria-label', l); b.dataset.tier = tier; }
  // FPS 측정: 3초 묶음, 탭 전환·로딩 멈춤은 빼고
  let last = 0, t0 = 0, n = 0, warm = 0, bad = 0, good = 0, slow = 0, told = false;
  function tick(){
    const now = performance.now();
    if(!last){ last = t0 = now; warm = now + 6000; return; }
    const gap = now - last; last = now; GFX.gap = Math.round(gap);
    if(document.hidden){ n = 0; t0 = now; slow = 0; return; }
    if(gap > 1500){ n = 0; t0 = now;   // 한 장 그리는 데 1.5초 넘게: 탭 전환일 수도 있으니 세 번 이어질 때만 아주 느린 것으로
      if(++slow >= 3){ slow = 0; GFX.fps = Math.round(10000/gap)/10; judge(GFX.fps, now); } else warm = Math.max(warm, now + 1500);
      return; }
    slow = 0; n++; if(now - t0 < 3000) return;
    const fps = n*1000/(now - t0); n = 0; t0 = now; GFX.fps = Math.round(fps); judge(fps, now);
  }
  function judge(fps, now){
    if(mode !== 'auto' || now < warm) return;
    if(fps < 24){ bad++; good = 0;
      if(scale > SMIN[tier] + 0.01){ scale = Math.max(SMIN[tier], scale - 0.15); apply(); warm = now + 2500; }
      else if(tier > 0 && bad >= 2){ tier--; scale = Math.max(SMIN[tier], scale); bad = 0; apply(); btn(); warm = now + 5000; ls.set(KA, JSON.stringify({ t: tier, ts: Date.now() }));
        if(!told && typeof toast === 'function'){ told = true; toast(T_('화면이 부드럽게 움직이도록 화질을 조금 낮췄어요'), 3.5); } }
    } else if(fps < 30){ bad = 0; good = 0; if(scale > SMIN[tier] + 0.01){ scale = Math.max(SMIN[tier], scale - 0.08); apply(); warm = now + 2500; } }
    else { bad = 0; if(fps > 52 && scale < 1){ if(++good >= 4){ good = 0; scale = Math.min(1, scale + 0.1); apply(); warm = now + 2500; } } else good = 0; }
  }
  // 메뉴 버튼: 자동 → 높음 → 보통 → 낮음
  function cycle(){
    mode = MODES[(MODES.indexOf(mode) + 1) % MODES.length]; ls.set(K, mode === 'auto' ? null : mode);
    if(mode === 'auto'){ ls.set(KA, null); tier = base; } else tier = IDX[mode];
    scale = 1; bad = good = 0; warm = performance.now() + 4000; apply(); btn();
    if(typeof toast === 'function') toast(label() + (mode === 'auto' ? ' · ' + T_('지금 ' + NAME[tier]) : ''), 2.5);
  }
  return { get tier(){ return tier; }, get mode(){ return mode; }, get scale(){ return scale; }, gpu, base, fps: 0, gap: 0, aa: tier >= 1,
    pr(){ return Math.min(devicePixelRatio || 1, PR[tier]); }, shadow(){ return SH[tier]; }, shadowSize(){ return SHS[tier] || 1024; },
    bind(r, s){ R = r; SUN = s; apply(); btn(); }, addVeg, tick, cycle, btn, apply };
})();
'''

BTN = ('<button class="ib" id="bGfx" title="화질" aria-label="화질 바꾸기"><svg viewBox="0 0 24 24"><path d="M4.5 16.5a8 8 0 1 1 15 0"/>'
       '<path d="M12 16.5l3.6-5.2"/><circle cx="12" cy="16.5" r="1.4"/><path d="M6.6 11.2l1 .6M12 7.5v1.2M17.4 11.2l-1 .6"/></svg></button>\n    ')


def patch_perf(P, m):
    # 1) 렌더러: 단계에 맞춘 안티에일리어싱·화소 비율
    P.rep("const renderer = new THREE.WebGLRenderer({canvas, antialias:true, preserveDrawingBuffer:true});",
          GFX_JS + "const renderer = new THREE.WebGLRenderer({canvas, antialias:GFX.aa, preserveDrawingBuffer:true});", 1)
    P.rep("renderer.setPixelRatio(Math.min(devicePixelRatio, IS_TOUCH ? 1.5 : 2));", "renderer.setPixelRatio(GFX.pr());", 1)
    # 2) 그림자: 낮음이면 끄고, 지도 크기는 단계대로
    P.rep("sun.castShadow = true; sun.shadow.mapSize.set(IS_TOUCH ? 1024 : 2048, IS_TOUCH ? 1024 : 2048);",
          "sun.castShadow = GFX.shadow(); sun.shadow.mapSize.set(GFX.shadowSize(), GFX.shadowSize());", 1)
    P.rep("scene.add(sun, sun.target);", "scene.add(sun, sun.target); GFX.bind(renderer, sun);", 1)
    # 3) 나무·풀 줄이기
    P.rep("for(const m of [...P.grass, ...P.reed, ...P.fern]) m.castShadow = false;",
          "for(const m of [...P.grass, ...P.reed, ...P.fern]) m.castShadow = false;\n  GFX.addVeg(Object.values(T).flat(), false); GFX.addVeg(Object.values(P).flat(), true);", 1)
    # 4) 매 화면 FPS 재기
    P.rep("  renderer.render(scene, camera);\n  requestAnimationFrame(frame);", "  GFX.tick();\n  renderer.render(scene, camera);\n  requestAnimationFrame(frame);", 1)
    # 5) 메뉴 버튼
    P.rep('<button class="ib" id="bMap"', BTN + '<button class="ib" id="bMap"', 1)
    P.rep('</body>', "<script>{ const b = document.getElementById('bGfx'); if(b){ b.onclick = () => window.__GFX && __GFX.cycle(); } }</script>\n</body>", 1)
    P.rep('</style>', '#bGfx[data-tier="0"] svg path:nth-child(2){transform:rotate(-70deg);transform-origin:12px 16.5px}'
                      '#bGfx[data-tier="1"] svg path:nth-child(2){transform:rotate(-35deg);transform-origin:12px 16.5px}\n</style>', 1)
    # 6) 번역 표
    import json
    a = P.t.index('  const R = ['); b = P.t.index('\n  ];', a)
    P.t = P.t[:b] + ',\n    // 화질 (pipeline/perf_patch.py)\n' + ',\n'.join('    ' + json.dumps(r, ensure_ascii=False) for r in GFX_ROWS) + P.t[b:]
