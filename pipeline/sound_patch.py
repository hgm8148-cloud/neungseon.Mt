"""산마다 고유한 효과음 + 천둥·돌풍 소리 (2026-11-03)

- 도선사 범종(종소리)은 뺐어요.
- 산마다 그 산다운 소리 2~3가지가 가끔 들려요 (MT_SIG). 모두 실제 녹음이 아니라 합성한 소리예요.
- 천둥(sfx.thunder)과 돌풍(sfx.gust)은 weather_patch.py 의 날씨 효과가 불러요.
"""

SIG_JS = r'''
    // ---------- 산마다 고유한 소리 (pipeline/sound_patch.py) ----------
    const rasp = (tt, f0, f1, dur, bp, q, vol, p) => { const o=ac.createOscillator(), b=filt('bandpass',bp,q), g=gain(0); o.type='sawtooth'; o.frequency.setValueAtTime(f0,tt); o.frequency.linearRampToValueAtTime(f1,tt+dur); env(g,tt,Math.min(0.03,dur*0.3),vol,dur); out(panTo(o.connect(b).connect(g),p),0.7,0.9); o.start(tt); o.stop(tt+dur+0.1); };
    const rumble = (tt, dur, f, vol, p) => { const s=ac.createBufferSource(); s.buffer=brownB; const b=filt('lowpass',f), g=gain(0); g.gain.setValueAtTime(0.0001,tt); g.gain.linearRampToValueAtTime(vol,tt+0.25); g.gain.exponentialRampToValueAtTime(0.0001,tt+dur); out(panTo(s.connect(b).connect(g),p),1,0.8); s.start(tt, Math.random()*6, dur+0.3); };
    const R_ = Math.random, n_ = (a, b) => a + ((R_()*(b-a+1))|0);
    const bigGust = (len, amp) => { breezeT = 0; breezeLen = len; breezeAmp = amp; gustT = Math.max(gustT, len + 10 + R_()*15); if(window.__wxGust) window.__wxGust(len, Math.min(1, amp*0.7)); };
    const SIGL = {
      magpie(t,p,v){ for(let i=0,n=n_(4,7);i<n;i++){ const tt=t+i*0.13; rasp(tt,1350,1150,0.07,1700,2,v*0.55,p); burst(tt,2600,1.1,0.06,v*0.5,p,'bandpass',0.6,0.004); } },
      carabiner(t,p,v){ let tt=t; for(let i=0,n=n_(2,4);i<n;i++){ tone('sine',3150,3120,tt,0.35,v,p,0.4); tone('sine',4720,4700,tt,0.25,v*0.55,p,0.4); tone('sine',7900,7850,tt,0.12,v*0.3,p,0.4); tt+=0.15+R_()*0.3; } },
      scops(t,p,v){ for(let i=0,n=n_(3,5);i<n;i++){ const tt=t+i*1.7; tone('sine',1230,1200,tt,0.09,v,p,1.1); tone('sine',1290,1240,tt+0.2,0.17,v,p,1.1); } },
      roe(t,p,v){ for(let i=0,n=n_(1,3);i<n;i++){ const tt=t+i*1.4; rasp(tt,520,380,0.22,1100,1.3,v,p); burst(tt,900,1.2,0.18,v*0.8,p,'bandpass',0.8,0.01); } },
      gust(t,p,v){ bigGust(6 + R_()*4, 1.25); },
      tinkle(t,p,v){ for(let i=0,n=n_(6,12);i<n;i++){ const f=5000+R_()*4000; tone('sine',f,f*0.99,t+R_()*1.6,0.05,v*0.5,p+(R_()-0.5)*0.6,0.9); } },
      blackcuckoo(t,p,v){ for(let k=0,m=n_(2,3);k<m;k++) [1180,1180,1180,950].forEach((f,i) => tone('sine',f,f*0.98,t+k*1.9+i*0.33,0.2,v,p,1.1)); },
      woodroll(t,p,v){ const n=n_(24,32); for(let i=0;i<n;i++) burst(t+i*0.038, 1250, 2, 0.02, v*(1-i/n*0.4), p, 'bandpass', 1.0, 0.002); },
      crowflock(t,p,v){ for(let c=0,m=n_(3,5);c<m;c++) birds.bigcrow(t+c*0.5+R_()*0.4, p+(R_()-0.5)*0.9, v*0.4); },
      scree(t,p,v){ let tt=t; for(let i=0,n=n_(7,14);i<n;i++){ burst(tt,900+R_()*1500,1.6,0.04,v*(1-i/n*0.6),p+i*0.03,'bandpass',0.6,0.002); if(i%2===0) tone('sine',130,70,tt,0.08,v*0.4,p,0.6); tt+=0.05+R_()*0.22*(1-i/n*0.5); } },
      grass(t,p,v){ burst(t,3800,0.5,4,v*0.5,p,'bandpass',0.4,1.6); burst(t+0.8,2400,0.6,3,v*0.35,-p,'bandpass',0.4,1.2); },
      cuckoo(t,p,v){ for(let i=0,n=n_(3,6);i<n;i++){ const tt=t+i*0.95; tone('sine',700,690,tt,0.16,v,p,1.0); tone('sine',560,550,tt+0.24,0.26,v*0.95,p,1.0); } },
      bridge(t,p,v){ tone('sine',182,178,t,1.6,v*1.1,p,0.9); tone('sine',463,458,t,1.0,v*0.5,p,0.9); tone('sine',1021,1015,t,0.6,v*0.25,p,0.9); rasp(t+0.15,150,120,0.35,700,4,v*0.45,p); tone('sine',182,178,t+0.7,1.2,v*0.6,p,0.9); },
      hawk(t,p,v){ for(let i=0,n=n_(2,3);i<n;i++){ const tt=t+i*0.9; tone('sine',2700,2000,tt,0.6,v,p,1.0); tone('triangle',2750,2050,tt,0.55,v*0.25,p,1.0); } },
      leafshower(t,p,v){ for(let i=0;i<45;i++) burst(t+R_()*3.2, 2500+R_()*3500, 0.8, 0.05+R_()*0.05, v*(0.25+R_()*0.4), p+(R_()-0.5)*1.2, 'bandpass', 0.3, 0.01); },
      pheasant(t,p,v){ rasp(t,1250,950,0.18,1400,1.5,v,p); rasp(t+0.32,1300,980,0.2,1400,1.5,v,p); for(let i=0;i<12;i++) burst(t+0.65+i*0.028,300+R_()*300,0.8,0.035,v*0.6,p,'bandpass',0.3,0.004); },
      gondola(t,p,v){ const o=ac.createOscillator(), o2=ac.createOscillator(), b=filt('lowpass',320), g=gain(0); o.type='sawtooth'; o.frequency.value=98; o2.type='sine'; o2.frequency.value=147; g.gain.setValueAtTime(0.0001,t); g.gain.linearRampToValueAtTime(v*0.35,t+1.6); g.gain.linearRampToValueAtTime(v*0.35,t+3.4); g.gain.exponentialRampToValueAtTime(0.0001,t+5.5); out(panTo(o.connect(b).connect(g),p),0.6,1.0); o2.connect(g); o.start(t); o2.start(t); o.stop(t+5.6); o2.stop(t+5.6); burst(t+4.2,700,2,0.06,v*0.6,p,'bandpass',0.9,0.003); burst(t+4.45,650,2,0.06,v*0.5,p,'bandpass',0.9,0.003); },
      longtit(t,p,v){ for(let i=0,n=n_(5,9);i<n;i++){ const f=7200+R_()*900; tone('sine',f,f*0.97,t+i*0.16+R_()*0.05,0.05,v*0.5,p,0.6); } rasp(t+1.6,4200,3800,0.12,4000,3,v*0.3,p); },
      skylark(t,p,v){ let tt=t; for(let i=0;i<46;i++){ const f=2800+R_()*2400, d=0.04+R_()*0.06; tone('sine',f,f*(0.85+R_()*0.3),tt,d,v*0.55,p,0.6); tt+=d+0.02; } },
      cricketbuzz(t,p,v){ for(let i=0;i<46;i++) burst(t+i*0.05, 7000, 3, 0.03, v*0.6, p, 'bandpass', 0.2, 0.004); },
      nutcracker(t,p,v){ for(let i=0,n=n_(3,6);i<n;i++) rasp(t+i*0.36,900,760,0.2,1300,1.1,v*0.8,p); },
      icewind(t,p,v){ const s=ac.createBufferSource(); s.buffer=whiteB; const b=filt('bandpass',1400,6), g=gain(0); b.frequency.setValueAtTime(1100,t); b.frequency.linearRampToValueAtTime(1700,t+2.5); b.frequency.linearRampToValueAtTime(1200,t+5); g.gain.setValueAtTime(0.0001,t); g.gain.linearRampToValueAtTime(v*1.4,t+2); g.gain.exponentialRampToValueAtTime(0.0001,t+5.2); out(panTo(s.connect(b).connect(g),p),1,0.6); s.start(t, R_()*4, 5.4); },
      yakbells(t,p,v){ const base=600+R_()*90; let tt=t; for(let i=0,n=n_(4,9);i<n;i++){ tone('sine',base,base*0.995,tt,0.7,v,p,0.6); tone('sine',base*2.43,base*2.42,tt,0.4,v*0.5,p,0.6); tone('triangle',base*3.9,base*3.88,tt,0.2,v*0.22,p,0.6); burst(tt,2000,2,0.02,v*0.4,p,'bandpass',0.3,0.002); tt+=0.25+R_()*0.45; } },
      glacier(t,p,v){ burst(t,2500,0.7,0.08,v*1.6,p,'bandpass',1.0,0.002); rumble(t+0.1, 4, 170, v*7, p); },
      flags(t,p,v){ for(let k=0;k<n_(3,6);k++) flap(t+k*0.55+R_()*0.2, v*0.9); },
      hototogisu(t,p,v){ for(let k=0;k<2;k++) [1500,2150,2150,1950,1500].forEach((f,i) => tone('sine',f,f*0.95,t+k*1.6+i*0.15,0.12,v*0.8,p,1.0)); },
      cinder(t,p,v){ let tt=t; for(let i=0,n=n_(8,16);i<n;i++){ burst(tt,500+R_()*700,1.2,0.05,v*(1-i/n*0.5),p+i*0.02,'bandpass',0.5,0.003); tt+=0.04+R_()*0.15; } },
      turaco(t,p,v){ for(let i=0,n=n_(6,11);i<n;i++) rasp(t+i*Math.max(0.16,0.32-i*0.014),520,470,0.14,700,1.4,v*1.2,p); },
      raven(t,p,v){ for(let i=0,n=n_(1,3);i<n;i++) rasp(t+i*0.7,300,240,0.4,600,1.2,v*1.4,p); },
      cowbells(t,p,v){ for(let c=0,m=n_(2,3);c<m;c++){ const base=900+R_()*600, pc=(R_()-0.5)*1.4; let tt=t+R_()*0.8; for(let i=0,n=n_(3,6);i<n;i++){ tone('sine',base,base*0.996,tt,0.5,v*0.8,pc,0.6); tone('sine',base*2.1,base*2.09,tt,0.3,v*0.4,pc,0.6); burst(tt,3200,2,0.015,v*0.3,pc,'bandpass',0.3,0.002); tt+=0.3+R_()*0.6; } } },
      chough(t,p,v){ for(let i=0,n=n_(2,4);i<n;i++){ const tt=t+i*0.45; rasp(tt,2400,1700,0.22,2200,2,v*0.8,p); tone('sine',3400,2600,tt,0.2,v*0.4,p,0.8); } },
      marmot(t,p,v){ for(let i=0,n=n_(1,3);i<n;i++){ const tt=t+i*0.7; tone('sine',2900,2500,tt,0.22,v,p,0.9); tone('sine',5800,5000,tt,0.15,v*0.15,p,0.9); } },
      stellerjay(t,p,v){ for(let i=0,n=n_(3,5);i<n;i++){ const tt=t+i*0.3; burst(tt,2600,1.2,0.12,v*1.2,p,'bandpass',0.7,0.01); rasp(tt,1100,950,0.12,2400,2,v*0.4,p); } },
      chickaree(t,p,v){ for(let i=0;i<30;i++) tone('sine',5200,4800,t+i*0.035,0.02,v*0.5,p,0.5); },
      hwamei(t,p,v){ let tt=t; for(let i=0,n=n_(12,20);i<n;i++){ const f=1400+R_()*2200, d=0.08+R_()*0.17; tone('sine',f,f*(0.8+R_()*0.45),tt,d,v*0.8,p,0.9); tt+=d+0.03; } },
      macaque(t,p,v){ for(let i=0,n=n_(2,4);i<n;i++){ const tt=t+i*0.35; rasp(tt,600,900,0.12,1300,1.2,v,p); rasp(tt+0.12,900,650,0.1,1300,1.2,v*0.8,p); } },
      porter(t,p,v){ for(let i=0,n=n_(2,4);i<n;i++) rasp(t+i*0.9,210,150,0.35,900,3,v*0.8,p); },
      guanaco(t,p,v){ for(let i=0,n=n_(2,3);i<n;i++) rasp(t+i*0.8,1300,900,0.45,1500,1,v,p); },
      tui(t,p,v){ tone('sine',1900,1880,t,0.25,v,p,0.9); for(let i=0;i<3;i++) burst(t+0.3+i*0.05,3500,3,0.01,v*0.6,p,'bandpass',0.4,0.001); tone('sine',2600,3300,t+0.5,0.12,v*0.7,p,0.9); burst(t+0.7,6000,1,0.2,v*0.3,p,'bandpass',0.4,0.05); tone('sine',1500,1480,t+1.0,0.3,v*0.8,p,0.9); },
      fumarole(t,p,v){ burst(t,3200,0.4,3.5,v*0.6,p,'highpass',0.5,1.2); rumble(t, 3.5, 90, v*2, p); },
    };
    // 산별 구성: [소리, 최소 간격(초), 최대 간격, 조건]
    const MT_SIG = {
      bukhansan:[['magpie',30,70,'day'],['carabiner',40,90,'mid'],['scops',30,70,'night']],
      hallasan:[['roe',40,90,'any'],['gust',70,140,'any'],['tinkle',30,70,'winterTop']],
      jirisan:[['blackcuckoo',40,90,'warmDay'],['woodroll',40,90,'day'],['scops',35,80,'night']],
      seoraksan:[['scree',45,100,'mid'],['crowflock',40,90,'top'],['falls',0,0,'low']],
      mudeungsan:[['grass',35,80,'any'],['cuckoo',40,90,'warmDay'],['scree',60,120,'mid']],
      wolchulsan:[['bridge',40,90,'mid'],['hawk',40,90,'day'],['magpie',50,100,'low']],
      naejangsan:[['leafshower',35,80,'any'],['pheasant',40,90,'day']],
      deogyusan:[['gondola',50,110,'top'],['longtit',30,70,'day'],['tinkle',30,70,'winterTop']],
      sobaeksan:[['skylark',35,80,'day'],['cricketbuzz',30,70,'summer'],['grass',40,90,'top']],
      taebaeksan:[['nutcracker',35,80,'day'],['icewind',45,100,'top'],['woodroll',50,110,'day']],
      everest:[['yakbells',40,90,'any'],['glacier',60,130,'any'],['flags',30,70,'any']],
      fuji:[['hototogisu',35,80,'day'],['cinder',40,90,'any'],['gust',70,140,'top']],
      kilimanjaro:[['turaco',35,80,'low'],['raven',35,80,'any']],
      matterhorn:[['cowbells',35,80,'low'],['chough',35,80,'any']],
      montblanc:[['marmot',35,80,'day'],['glacier',60,130,'any'],['chough',45,100,'top']],
      trecime:[['scree',40,90,'any'],['marmot',40,90,'day'],['chough',45,100,'any']],
      halfdome:[['stellerjay',35,80,'day'],['chickaree',35,80,'day'],['falls',0,0,'low']],
      huangshan:[['hwamei',35,80,'day'],['macaque',45,100,'any'],['porter',40,90,'any']],
      torresdelpaine:[['guanaco',40,90,'any'],['gust',50,110,'any']],
      tongariro:[['tui',35,80,'day'],['fumarole',40,90,'any']],
    }['__MT__'] || [];
    let SZN = 'autumn'; try{ SZN = SEASON; }catch(e){}
    const okSig = (c, k) => { const night = k.night||0, top = (k.summit||0) > 0.3 || k.prog > 0.75, win = SZN === 'winter' || SZN === 'fixed';
      return c === 'any' || (c === 'day' && night < 0.5) || (c === 'night' && night > 0.5) || (c === 'low' && k.prog < 0.45) || (c === 'mid' && k.prog > 0.2 && k.prog < 0.95) || (c === 'top' && top)
        || (c === 'warmDay' && !win && night < 0.5) || (c === 'summer' && SZN === 'summer' && night < 0.7) || (c === 'winterTop' && win && (top || k.prog > 0.5)); };
    const SIGT = MT_SIG.map(s => 8 + R_()*40);
    // 폭포: 들머리 쪽에서 멀리 계속 들리는 물소리
    let fallsG = null; if(MT_SIG.some(s => s[0] === 'falls')){ fallsG = gain(0); loop(brownB, filt('lowpass',700), fallsG).connect(master); loop(whiteB, filt('bandpass',1400,0.4), gain(0.25)).connect(fallsG); }
    const sigUpdate = (dt, t, k) => {
      if(fallsG) fallsG.gain.setTargetAtTime(Math.max(0, 1 - k.prog/0.4)*0.05*AMB, t, 2);
      MT_SIG.forEach((s, i) => { if(s[0] === 'falls') return; SIGT[i] -= dt; if(SIGT[i] > 0) return; SIGT[i] = s[1] + R_()*(s[2]-s[1]);
        if(okSig(s[3], k)) SIGL[s[0]](t + 0.05, R_()*1.6 - 0.8, 0.016*AMB); });
    };
    window.__sig = (name) => { if(SIGL[name]) SIGL[name](ac.currentTime + 0.05, 0, 0.02); };
    // 천둥: 번쩍 뒤 delay 초 만에 우르릉
    sfx.thunder = (delay, vol) => { const t0 = ac.currentTime + delay; burst(t0, 1600, 0.6, 0.3, 0.05*vol, (R_()-0.5)*0.6, 'bandpass', 0.6, 0.004);
      rumble(t0 + 0.05, 3.5 + R_()*2.5, 260, 0.35*vol, (R_()-0.5)*0.5); rumble(t0 + 0.6 + R_()*0.6, 3 + R_()*2, 140, 0.3*vol, (R_()-0.5)*0.5); };
    sfx.gust = (len, amp) => { breezeT = 0; breezeLen = len; breezeAmp = amp; gustT = Math.max(gustT, len + 12 + R_()*20); };
'''


def patch_sound(P, m):
    # 1) 도선사 범종 빼기
    P.rep("      bellT -= dt; if(bellT < 0){ bellT = 70 + Math.random()*60; if(k.prog < 0.35) bell(t+0.1, 0.03*(1 - k.prog*2)); }\n", "", 1)
    # 2) 산별 소리 (변수 선언 뒤, sfx.update 앞)
    P.rep("    sfx.update = (dt, k) => {", SIG_JS.replace('__MT__', m.get('base', m['id'])) + "    sfx.update = (dt, k) => {", 1)
    P.rep("      birdT -= dt;\n", "      sigUpdate(dt, t, k);\n      birdT -= dt;\n", 1)
