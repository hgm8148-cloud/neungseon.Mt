"""숨은 갈래길 · 완등 표시 · 별 (2026-11-04)

- 산마다 3~5개(탐방로 길이에 따라) 숨은 갈래길. 메인 탐방로에서 살짝 비켜난 입구(덤불 사이 작은 돌탑)를
  직접 찾아가야 '발견'돼요. 자동 걷기로 가운데만 걸으면 지나쳐요. 힌트는 주지 않아요.
- 발견하면: "숨은 길 발견!" + 이 길로 갈지 / 그냥 갈지 고르기. 고르면 그 길을 따라 걷고 다시 메인 탐방로로 이어져요.
- 테마: 깎아지른 오르막(밧줄 기둥) · 바위 틈(양쪽 바위벽) · 바위 굴(머리 위를 덮은 바위)
- 발견한 길은 지도에 보이고 저장돼요(이 기기 + 구글 로그인하면 계정). 못 찾은 길은 지도에 안 보여요.
- 정상에 닿으면 '완등' 저장. 산 고르기 화면에 완등 표시와 별(찾은 길 수 / 전체)을 보여 줘요.
"""
import json

STEEP, CREV, CAVE = 'steep', 'crevice', 'cave'
# 각 산의 실제 지점 이름을 딴 갈래길 (이름은 그 근처 지명, 길 모양은 게임 속 상상)
NAMES = {
    'bukhansan': [('숨은벽 오르막', 'Sumeunbyeok Climb', STEEP), ('염초봉 바위틈', 'Yeomchobong Crevice', CREV), ('인수봉 바위굴', 'Insubong Rock Cave', CAVE), ('원효봉 급경사', 'Wonhyobong Steep', STEEP), ('노적봉 바윗길', 'Nojeokbong Crevice', CREV)],
    'deogyusan': [('중봉 오르막', 'Jungbong Climb', STEEP), ('동엽령 바위틈', 'Dongyeopryeong Crevice', CREV), ('오수자굴', 'Osujagul Cave', CAVE), ('백련사 급경사', 'Baengnyeonsa Steep', STEEP), ('칠연 바윗길', 'Chiryeon Crevice', CREV)],
    'jirisan': [('장터목 오르막', 'Jangteomok Climb', STEEP), ('칠선 바위틈', 'Chilseon Crevice', CREV), ('통천문', 'Tongcheonmun Rock Gate', CAVE), ('세석 급경사', 'Seseok Steep', STEEP), ('연하봉 바윗길', 'Yeonhabong Crevice', CREV)],
    'hallasan': [('사라오름 오르막', 'Saraoreum Climb', STEEP), ('삼각봉 바위틈', 'Samgakbong Crevice', CREV), ('왕관릉 바위굴', 'Wanggwalleung Rock Cave', CAVE), ('진달래밭 급경사', 'Jindallaebat Steep', STEEP), ('용진각 바윗길', 'Yongjingak Crevice', CREV)],
    'mudeungsan': [('중머리재 오르막', 'Jungmeorijae Climb', STEEP), ('입석대 바위틈', 'Ipseokdae Crevice', CREV), ('규봉암 바위굴', 'Gyubongam Rock Cave', CAVE), ('장불재 급경사', 'Jangbuljae Steep', STEEP), ('서석대 바윗길', 'Seoseokdae Crevice', CREV)],
    'naejangsan': [('서래봉 오르막', 'Seoraebong Climb', STEEP), ('불출봉 바위틈', 'Bulchulbong Crevice', CREV), ('연자봉 바위굴', 'Yeonjabong Rock Cave', CAVE), ('까치봉 급경사', 'Kkachibong Steep', STEEP), ('신선봉 바윗길', 'Sinseonbong Crevice', CREV)],
    'seoraksan': [('천불동 오르막', 'Cheonbuldong Climb', STEEP), ('공룡능선 바위틈', 'Gongnyong Ridge Crevice', CREV), ('금강굴', 'Geumganggul Cave', CAVE), ('용아장성 급경사', 'Yongajangseong Steep', STEEP), ('울산바위 바윗길', 'Ulsanbawi Crevice', CREV)],
    'sobaeksan': [('연화봉 오르막', 'Yeonhwabong Climb', STEEP), ('국망봉 바위틈', 'Gungmangbong Crevice', CREV), ('희방 바위굴', 'Huibang Rock Cave', CAVE), ('죽령 급경사', 'Jukryeong Steep', STEEP), ('비로봉 바윗길', 'Birobong Crevice', CREV)],
    'taebaeksan': [('장군봉 오르막', 'Janggunbong Climb', STEEP), ('문수봉 바위틈', 'Munsubong Crevice', CREV), ('유일사 바위굴', 'Yuilsa Rock Cave', CAVE), ('부쇠봉 급경사', 'Busoebong Steep', STEEP), ('천제단 바윗길', 'Cheonjedan Crevice', CREV)],
    'wolchulsan': [('천황봉 오르막', 'Cheonhwangbong Climb', STEEP), ('사자봉 바위틈', 'Sajabong Crevice', CREV), ('구정봉 베틀굴', 'Guieongbong Betteul Cave', CAVE), ('바람재 급경사', 'Baramjae Steep', STEEP), ('구름다리 바윗길', 'Cloud Bridge Crevice', CREV)],
    'fuji': [('오사와 오르막', 'Osawa Climb', STEEP), ('호에이산 바위틈', 'Hoeizan Crevice', CREV), ('용암 동굴', 'Lava Cave', CAVE), ('7합목 급경사', '7th Station Steep', STEEP), ('오하치 바윗길', 'Ohachi Crevice', CREV)],
    'everest': [('로체 사면 오르막', 'Lhotse Face Climb', STEEP), ('쿰부 빙하 틈', 'Khumbu Crevice', CREV), ('세락 얼음굴', 'Serac Ice Cave', CAVE), ('힐러리 스텝 급경사', 'Hillary Step Steep', STEEP), ('남봉 바윗길', 'South Summit Crevice', CREV)],
    'halfdome': [('서브돔 오르막', 'Sub Dome Climb', STEEP), ('버널 폭포 바위틈', 'Vernal Fall Crevice', CREV), ('화강암 바위굴', 'Granite Rock Cave', CAVE), ('케이블 급경사', 'Cables Steep', STEEP), ('리틀 요세미티 바윗길', 'Little Yosemite Crevice', CREV)],
    'huangshan': [('연화봉 오르막', 'Lotus Peak Climb', STEEP), ('일선천', 'Yixiantian Crevice', CREV), ('오어봉 바위굴', 'Aoyu Peak Rock Cave', CAVE), ('광명정 급경사', 'Guangmingding Steep', STEEP), ('서해대협곡 바윗길', 'West Sea Canyon Crevice', CREV)],
    'kilimanjaro': [('바랑코 월', 'Barranco Wall', STEEP), ('라바 타워 바위틈', 'Lava Tower Crevice', CREV), ('용암 바위굴', 'Lava Rock Cave', CAVE), ('스텔라 포인트 급경사', 'Stella Point Steep', STEEP), ('시라 고원 바윗길', 'Shira Plateau Crevice', CREV)],
    'matterhorn': [('회른리 능선 오르막', 'Hörnli Ridge Climb', STEEP), ('츠무트 바위틈', 'Zmutt Crevice', CREV), ('빙하 얼음굴', 'Glacier Ice Cave', CAVE), ('솔베이 급경사', 'Solvay Steep', STEEP), ('회른리 바윗길', 'Hörnli Crevice', CREV)],
    'montblanc': [('구테 쿨루아르 오르막', 'Goûter Couloir Climb', STEEP), ('에귀 바위틈', 'Aiguille Crevice', CREV), ('세락 얼음굴', 'Serac Ice Cave', CAVE), ('테트 루스 급경사', 'Tête Rousse Steep', STEEP), ('돔 뒤 구테 바윗길', 'Dôme du Goûter Crevice', CREV)],
    'tongariro': [('레드 크레이터 오르막', 'Red Crater Climb', STEEP), ('사우스 크레이터 바위틈', 'South Crater Crevice', CREV), ('용암 바위굴', 'Lava Rock Cave', CAVE), ('에메랄드 호수 급경사', 'Emerald Lakes Steep', STEEP), ('케테타히 바윗길', 'Ketetahi Crevice', CREV)],
    'torresdelpaine': [('아센시오 오르막', 'Ascencio Climb', STEEP), ('모레인 바위틈', 'Moraine Crevice', CREV), ('화강암 바위굴', 'Granite Rock Cave', CAVE), ('칠레노 급경사', 'Chileno Steep', STEEP), ('토레스 바윗길', 'Torres Crevice', CREV)],
    'seongpanak': [('사라오름 오르막', 'Saraoreum Climb', STEEP), ('진달래밭 바위틈', 'Jindallaebat Crevice', CREV), ('화구벽 바윗길', 'Crater Wall Crevice', CREV), ('용암 바위굴', 'Lava Rock Cave', CAVE)],
    'namche': [('남체 언덕 급경사', 'Namche Hill Steep', STEEP), ('두드코시 바위틈', 'Dudh Koshi Crevice', CREV), ('조르살레 바위굴', 'Jorsalle Rock Cave', CAVE), ('보테코시 오르막', 'Bhote Koshi Climb', STEEP)],
    'trecime': [('라바레도 오르막', 'Lavaredo Climb', STEEP), ('파테르노 바위틈', 'Paterno Crevice', CREV), ('파테르노 동굴', 'Paterno Tunnel', CAVE), ('로카텔리 급경사', 'Locatelli Steep', STEEP), ('아우론초 바윗길', 'Auronzo Crevice', CREV)],
}
THEME_KO = {STEEP: '깎아지른 오르막', CREV: '바위 틈 길', CAVE: '바위 굴'}
THEME_ROWS = [
    ['깎아지른 오르막', 'Sheer climb', '切り立った登り', '陡峭上坡', 'Steiler Anstieg', 'Montée abrupte', 'Salita ripida', 'Subida empinada', 'ठाडो उकालो', 'Mteremko mkali'],
    ['바위 틈 길', 'Rock crevice', '岩の隙間の道', '岩缝小路', 'Felsspalte', 'Passage entre les rochers', 'Passaggio tra le rocce', 'Paso entre rocas', 'चट्टानको चिराबाट बाटो', 'Njia ya ufa wa mwamba'],
    ['바위 굴', 'Rock cave', '岩の洞窟', '岩洞', 'Felshöhle', 'Grotte rocheuse', 'Grotta rocciosa', 'Cueva de roca', 'चट्टानको गुफा', 'Pango la mwamba'],
    ['숨은 길 발견!', 'Hidden trail found!', '隠れた道を発見！', '发现隐藏小路！', 'Versteckter Pfad entdeckt!', 'Sentier caché découvert !', 'Sentiero nascosto scoperto!', '¡Sendero oculto descubierto!', 'लुकेको बाटो भेटियो!', 'Njia iliyofichwa imepatikana!'],
    ['이 길로 가 볼까요? 다시 탐방로로 이어져요', 'Take this path? It rejoins the main trail', 'この道を行ってみますか？ 本道に戻ります', '要走这条路吗？它会回到主步道', 'Diesen Weg nehmen? Er führt zurück zum Hauptweg', 'Prendre ce chemin ? Il rejoint le sentier principal', 'Prendere questo sentiero? Si ricongiunge al principale', '¿Tomar este camino? Vuelve al sendero principal', 'यो बाटो जाने? यो मुख्य बाटोमै जोडिन्छ', 'Kupita njia hii? Inarudi njia kuu'],
    ['이 길로 가기', 'Take it', 'この道へ', '走这条路', 'Los geht’s', 'Y aller', 'Andiamo', 'Ir por aquí', 'यो बाटो जाने', 'Pita hapa'],
    ['그냥 갈래요', 'Not now', 'やめておく', '先不了', 'Lieber nicht', 'Pas maintenant', 'Non ora', 'Ahora no', 'अहिले होइन', 'Si sasa'],
    ['다시 탐방로로 나왔어요', 'Back on the main trail', '本道に戻りました', '回到主步道了', 'Zurück auf dem Hauptweg', 'De retour sur le sentier principal', 'Di nuovo sul sentiero principale', 'De vuelta en el sendero principal', 'मुख्य बाटोमा फर्कियो', 'Umerudi njia kuu'],
    ['◯ 표시된 곳을 누르면 바로 이동해요', '◯ Tap a circled spot to jump there', '◯ 印の場所をタップするとすぐ移動します', '◯ 点击圆圈处即可直接前往', '◯ Markierte Stelle antippen, um hinzuspringen', '◯ Touchez un lieu entouré pour y aller', '◯ Tocca un punto cerchiato per andarci', '◯ Toca un punto marcado para ir allí', '◯ घेरिएको ठाउँ थिच्नुहोस्, सिधै पुगिन्छ', '◯ Gusa sehemu yenye duara kwenda huko'],
    ['완등하면 경유지로 바로 이동할 수 있어요', 'Summit once to jump between checkpoints', '完登すると経由地へすぐ移動できます', '登顶后可直接前往途经点', 'Nach dem Gipfel kannst du zu Etappen springen', 'Après le sommet, allez directement aux étapes', 'Dopo la vetta puoi saltare alle tappe', 'Tras la cumbre podrás ir directo a los puntos', 'शिखर पुगेपछि बिसौनीमा सिधै जान सकिन्छ', 'Ukifika kileleni utaweza kuruka vituoni'],
    ['이 산을 완등하면 지도에서 눌러 바로 이동할 수 있어요', 'Summit this mountain to jump from the map', 'この山を完登すると地図からすぐ移動できます', '登顶这座山后可在地图上直接前往', 'Erst den Gipfel erreichen, dann per Karte springen', 'Atteignez le sommet pour voyager depuis la carte', 'Raggiungi la vetta per spostarti dalla mappa', 'Llega a la cumbre para moverte desde el mapa', 'यो हिमालको शिखर पुगेपछि नक्साबाट सिधै जान सकिन्छ', 'Fika kileleni kwanza ili uruke kutoka ramani'],
    ['버튼 펼치기', 'Show buttons', 'ボタンを表示', '展开按钮', 'Tasten zeigen', 'Afficher les boutons', 'Mostra pulsanti', 'Mostrar botones', 'बटन देखाउनुहोस्', 'Onyesha vitufe'],
    ['버튼 접기 (B)', 'Collapse buttons (B)', 'ボタンを畳む (B)', '收起按钮 (B)', 'Tasten einklappen (B)', 'Replier les boutons (B)', 'Comprimi pulsanti (B)', 'Contraer botones (B)', 'बटन लुकाउनुहोस् (B)', 'Kunja vitufe (B)'],
    ['버튼 펼치기 (B)', 'Show buttons (B)', 'ボタンを表示 (B)', '展开按钮 (B)', 'Tasten zeigen (B)', 'Afficher les boutons (B)', 'Mostra pulsanti (B)', 'Mostrar botones (B)', 'बटन देखाउनुहोस् (B)', 'Onyesha vitufe (B)'],
    ['길이 막혀 있어서 탐방로로 옮겨 드렸어요', 'The path was blocked, so we moved you back to the trail', '道がふさがっていたので本道へ移動しました', '小路被挡住了，已帮你回到主步道', 'Der Weg war versperrt – zurück auf dem Hauptweg', 'Le chemin était bloqué, retour au sentier principal', 'Il sentiero era bloccato, torni sul principale', 'El camino estaba bloqueado; vuelves al sendero principal', 'बाटो बन्द थियो, मुख्य बाटोमा पुर्‍याइयो', 'Njia ilikuwa imezibwa, umerudishwa njia kuu'],
    ['완등', 'Summited', '完登', '登顶', 'Gipfel', 'Sommet', 'Vetta', 'Cumbre', 'शिखर', 'Kilele'],
]

SIDE_CSS = r'''
#sideAsk{position:fixed;left:50%;bottom:calc(150px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:30;background:var(--paper,#fbf7ef);color:var(--ink,#2a2620);border-radius:18px;padding:14px 18px 14px;box-shadow:0 16px 44px rgba(0,0,0,.35);text-align:center;min-width:260px;max-width:min(92vw,380px)}
#sideAsk[hidden]{display:none}
body.sideFollow #walkPill #bWalk{display:inline-block!important}
#sideAsk .k{font-size:12px;font-weight:800;letter-spacing:.06em;color:#c0602e}
#sideAsk .n{font-size:19px;font-weight:700;margin:3px 0 1px}
#sideAsk .t{font-size:12.5px;opacity:.7}
#sideAsk p{font-size:13.5px;margin:8px 0 12px}
#sideAsk .row{display:flex;gap:8px;justify-content:center}
#sideAsk button{border:0;border-radius:999px;padding:9px 18px;font:inherit;font-size:14px;font-weight:600;cursor:pointer}
#sideAsk .go{background:#c0602e;color:#fff}#sideAsk .no{background:rgba(0,0,0,.07);color:inherit}
'''
SIDE_HTML = '<div id="sideAsk" hidden><div class="k">숨은 길 발견!</div><div class="n" id="sdName"></div><div class="t" id="sdTheme"></div><p>이 길로 가 볼까요? 다시 탐방로로 이어져요</p><div class="row"><button class="no" id="sdNo">그냥 갈래요</button><button class="go" id="sdGo">이 길로 가기</button></div></div>'

SIDE_JS = r'''
// ---------- 숨은 갈래길 (pipeline/side_patch.py) ----------
const SIDE = (() => {
  const MID = '__ID__', DEF = __DEF__, T_ = x => (window.T || (y => y))(x);
  const isKo = () => { try{ return I18N.lang === 'ko'; }catch(e){ return true; } }, nm = S => isKo() ? S.name : S.en;
  const isAdm = () => document.body.classList.contains('admin');
  let rs = 9173 + MID.length * 131; const rnd = () => (rs = (rs * 16807) % 2147483647) / 2147483647;
  const L = trail.length, cum = [0]; for(let i = 1; i < L; i++) cum.push(cum[i-1] + Math.hypot(trail[i].x - trail[i-1].x, trail[i].z - trail[i-1].z));
  const TOT = cum[L-1], idxAt = d => { let lo = 0, hi = L - 1; while(lo < hi){ const m = (lo + hi) >> 1; if(cum[m] < d) lo = m + 1; else hi = m; } return lo; };
  const n = Math.min(DEF.length, TOT < 3000 ? 3 : TOT < 5500 ? 4 : 5);
  const paths = [];
  const nrm = i => { const p = trail[Math.max(0, i-3)], q = trail[Math.min(L-1, i+3)], dx = q.x - p.x, dz = q.z - p.z, l = Math.hypot(dx, dz) || 1; return [-dz/l, dx/l]; };
  // 한 갈래길 만들기 (v: 다시 시도할 때마다 방향·폭·자리를 조금씩 바꿔요)
  const make = (k, v) => {
    const f = 0.10 + (k + 0.5) * (0.76 / n) + (rnd() - 0.5) * 0.04 + (v ? ((v % 2 ? 1 : -1) * Math.ceil((v % 16 || 16) / 2) * 0.022) : 0), d0 = Math.max(0.05, f) * TOT;
    const th = DEF[k][2], span = (th === 'steep' ? 140 + rnd()*80 : 200 + rnd()*120) * (v >= 16 ? 0.5 : v >= 4 ? 0.75 : 1);
    const a = idxAt(d0), b = idxAt(Math.min(TOT * 0.93, d0 + span));
    if(b - a < 10) return null;
    let side = (k % 2 ? 1 : -1);
    { const [nx, nz] = nrm(((a+b)/2)|0), m = trail[((a+b)/2)|0]; const h1 = Math.abs(heightAt(m.x + nx*35*side, m.z + nz*35*side) - heightAt(m.x, m.z)), h2 = Math.abs(heightAt(m.x - nx*35*side, m.z - nz*35*side) - heightAt(m.x, m.z)); if(h1 > h2 * 1.6) side = -side; }
    if(v % 2) side = -side;
    const sc = v >= 16 ? 0.35 : [1, 1, 0.75, 0.75, 0.6, 0.6, 0.5, 0.5][v % 8];
    const D = (th === 'steep' ? 14 + rnd()*8 : 26 + rnd()*22) * sc, pts = [];
    const steps = Math.max(12, Math.round((cum[b] - cum[a]) / 2));
    for(let s = 0; s <= steps; s++){ const t = s / steps;
      // 모든 갈래길이 탐방로 모양을 따라가다 옆으로 비켜나요 (곧은 지름길은 굽은 탐방로를 가로질러 꼬일 수 있어서)
      const i = Math.round(a + (b - a)*t), q = trail[i]; let x = q.x, z = q.z;
      const [nx, nz] = nrm(i), off = D * Math.pow(Math.sin(Math.PI * t), th === 'steep' ? 0.6 : 0.75) * side + (rnd() - 0.5) * 0.6;
      x += nx * off; z += nz * off;
      if(Math.abs(x) > HALF - 8 || Math.abs(z) > HALF - 8) return null;
      pts.push({x, z}); }
    // 점 사이가 너무 벌어지지 않게 1.5m 간격으로 고르게
    const R = [pts[0]]; for(let s = 1; s < pts.length; s++){ const p = R[R.length-1], q = pts[s], d = Math.hypot(q.x - p.x, q.z - p.z), m = Math.ceil(d / 1.5); for(let j = 1; j <= m; j++) R.push({ x: p.x + (q.x - p.x)*j/m, z: p.z + (q.z - p.z)*j/m }); }
    let e = 0; for(let s = 0; s < R.length; s++){ if(nearTrail(R[s].x, R[s].z, 2).d > 10){ e = s; break; } }
    if(!e) e = Math.min(R.length - 1, 6);
    return { k, name: DEF[k][0], en: DEF[k][1], theme: th, pts: R, a, b, e, side };
  };
  // 쓸 만한지: 탐방로 양 끝에 붙고, 다른 탐방로 구간·다른 갈래길과 엉키지 않고, 너무 가파르지 않고, 저절로 꼬이지 않기
  const check = (S) => { const P = S.pts, lo = S.a - 20, hi = S.b + 20, why = [];
    if(Math.hypot(P[0].x - trail[S.a].x, P[0].z - trail[S.a].z) > 2 || Math.hypot(P[P.length-1].x - trail[S.b].x, P[P.length-1].z - trail[S.b].z) > 2) why.push('ends');
    for(let s = 0; s < P.length && !why.length; s += 2){ const p = P[s]; for(let i = 0; i < L; i += 2){ if(i >= lo && i <= hi) continue; const q = trail[i]; if((q.x - p.x)*(q.x - p.x) + (q.z - p.z)*(q.z - p.z) < 144){ why.push('cross'); break; } } }
    let mg = 0; for(let s = 1; s < P.length; s++){ const d = Math.hypot(P[s].x - P[s-1].x, P[s].z - P[s-1].z) || 1; mg = Math.max(mg, Math.abs(heightAt(P[s].x, P[s].z) - heightAt(P[s-1].x, P[s-1].z)) / d); }
    let tg = 0; for(let i = S.a + 2; i <= S.b; i += 2){ const d = Math.hypot(trail[i].x - trail[i-2].x, trail[i].z - trail[i-2].z) || 1; tg = Math.max(tg, Math.abs(trail[i].h - trail[i-2].h) / d); }
    if(mg > Math.max(S.theme === 'steep' ? 1.1 : 0.85, tg * 1.15)) why.push('grade');
    for(const O of paths){ for(let s = 0; s < P.length && !why.includes('other'); s += 3) for(let t = 0; t < O.pts.length; t += 3){ const dx = O.pts[t].x - P[s].x, dz = O.pts[t].z - P[s].z; if(dx*dx + dz*dz < 100){ why.push('other'); break; } } }
    for(let s = S.e + 4; s < P.length - 4 && !why.includes('self'); s += 2) for(let t = s + 8; t < P.length - 4; t += 2){ const dx = P[t].x - P[s].x, dz = P[t].z - P[s].z; if(dx*dx + dz*dz < 4){ why.push('self'); break; } }
    S.mg = +mg.toFixed(2); return why; };
  const report = [];
  for(let k = 0; k < n; k++){ let ok = null, last = null;
    for(let v = 0; v < 26 && !ok; v++){ const S = make(k, v); if(!S) continue; const w = check(S); last = { v, why: w, mg: S.mg }; if(!w.length){ S.v = v; ok = S; } }
    report.push({ k, ok: !!ok, v: ok ? ok.v : -1, last }); if(ok) paths.push(ok); }
  window.__SIDE_CHECK = report;
  // 저장: 이 기기(store) + 구글 로그인하면 계정(prog)
  const P0 = store.get('prog', {}), me = P0[MID] || (P0[MID] = {}); me.tr = me.tr || []; me.n = paths.length;
  const save = () => { const p = store.get('prog', {}); const o = p[MID] || {}; o.tr = [...new Set([...(o.tr || []), ...me.tr])]; o.n = paths.length; if(me.sum) o.sum = 1; p[MID] = o; store.set('prog', p); try{ cloudPush(true); }catch(e){} };
  save();
  const found = k => me.tr.includes(k);
  // ---- 길 그리기 ----
  const ribbon = (pts, w, from) => { const P = [], I = [], U = []; let acc = 0;
    for(let s = from; s < pts.length; s++){ const p = pts[s], q = pts[Math.min(pts.length-1, s+1)], o = pts[Math.max(0, s-1)]; let dx = q.x - o.x, dz = q.z - o.z; const l = Math.hypot(dx, dz) || 1; dx /= l; dz /= l;
      if(s > from) acc += Math.hypot(p.x - pts[s-1].x, p.z - pts[s-1].z);
      const fade = Math.min(1, (s - from) / 5);
      for(const sg of [-1, 1]){ const x = p.x - dz*w*sg*fade, z = p.z + dx*w*sg*fade; P.push(x, heightAt(x, z) + 0.06, z); U.push(sg < 0 ? 0 : 1, acc / 6); } }
    for(let s = 0; s < pts.length - from - 1; s++){ const i = s*2; I.push(i, i+1, i+2, i+1, i+3, i+2); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.setIndex(I); g.computeVertexNormals(); return g; };
  const pathMat = new THREE.MeshStandardMaterial({map: TEX.trail, roughness: 1, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, transparent: true, opacity: 0.92, depthWrite: false});
  const rockMat = new THREE.MeshStandardMaterial({map: TEX.granite, roughness: 0.95, color: (window.__rocks && window.__rocks.material.color) ? window.__rocks.material.color.clone() : new THREE.Color(0xcfc8bc)});
  const rockGeo = new THREE.IcosahedronGeometry(1, 1);
  const deco = new THREE.Group(); scene.add(deco);
  const dir = (pts, s) => { const p = pts[Math.max(0, s-1)], q = pts[Math.min(pts.length-1, s+1)]; return Math.atan2(q.x - p.x, q.z - p.z); };
  for(const S of paths){ const pts = S.pts;
    const m = new THREE.Mesh(ribbon(pts, 0.75, S.e), pathMat); m.receiveShadow = true; deco.add(m);
    // 입구 돌탑 (작게)
    { const p = pts[S.e], y = heightAt(p.x, p.z); for(let i = 0; i < 4; i++){ const r = new THREE.Mesh(rockGeo, rockMat); const sc = 0.32 - i*0.06; r.scale.set(sc*1.2, sc*0.7, sc); r.position.set(p.x + 0.9, y + 0.12 + i*0.2, p.z + 0.4); r.rotation.y = i; r.castShadow = true; deco.add(r); } }
    const s0 = Math.floor(pts.length * 0.35), s1 = Math.floor(pts.length * 0.65);
    if(S.theme === 'crevice'){ // 양쪽으로 높은 바위벽
      for(let s = s0; s < s1; s += 2){ const p = pts[s], an = dir(pts, s), nx = Math.cos(an), nz = -Math.sin(an);
        for(const sg of [-1, 1]){ const d = 1.7 + Math.random()*0.4, x = p.x + nx*d*sg, z = p.z + nz*d*sg, h = 3.2 + Math.random()*2.6; const r = new THREE.Mesh(rockGeo, rockMat);
          r.scale.set(0.8 + Math.random()*0.5, h, 1.6 + Math.random()*0.8); r.position.set(x + nx*sg*0.6, heightAt(x, z) + h*0.55, z + nz*sg*0.6); r.rotation.set((Math.random()-0.5)*0.15, an, sg*0.08); r.castShadow = true; r.receiveShadow = true; deco.add(r); } } }
    else if(S.theme === 'cave'){ // 머리 위를 덮은 바위 굴
      const c0 = Math.floor(pts.length * 0.42), c1 = Math.floor(pts.length * 0.58);
      for(let s = c0; s < c1; s += 1){ const p = pts[s], an = dir(pts, s), y = heightAt(p.x, p.z);
        const arch = new THREE.Mesh(new THREE.CylinderGeometry(2.4, 2.4, 2.2, 10, 1, true, 0, Math.PI), rockMat); arch.material.side = THREE.DoubleSide;
        arch.rotation.set(0, an, Math.PI/2); arch.rotateX(Math.PI/2); arch.position.set(p.x, y + 0.2, p.z); arch.castShadow = true; arch.receiveShadow = true; deco.add(arch);
        const top = new THREE.Mesh(rockGeo, rockMat); top.scale.set(3.4, 1.6 + Math.random(), 2.6); top.position.set(p.x, y + 2.9, p.z); top.rotation.set(Math.random(), an, Math.random()*0.3); top.castShadow = true; deco.add(top); } }
    else { // 깎아지른 오르막: 밧줄 기둥
      const postM = new THREE.MeshStandardMaterial({color: 0x5a3e2a, roughness: 0.8}), postG = new THREE.CylinderGeometry(0.05, 0.06, 1.1, 6);
      for(let s = S.e; s < pts.length; s += 3){ const p = pts[s], an = dir(pts, s), nx = Math.cos(an), nz = -Math.sin(an), x = p.x + nx*0.95, z = p.z + nz*0.95; const po = new THREE.Mesh(postG, postM); po.position.set(x, heightAt(x, z) + 0.55, z); deco.add(po); } }
  }
  // 갈래길 위 바위·나무는 치우고(걷는 자리), 통과는 막지 않아요
  const onSide = (x, z, r) => { for(const S of paths){ const pts = S.pts; for(let s = S.e; s < pts.length; s += 1){ const dx = pts[s].x - x, dz = pts[s].z - z; if(dx*dx + dz*dz < r*r) return S; } } return null; };
  // 바위·나무·큰 바위봉우리(크기까지 고려)가 갈래길과 그 입구 쪽 길을 막으면 치워요
  { const M = new THREE.Matrix4(), Z = new THREE.Matrix4().makeScale(0, 0, 0), v = new THREE.Vector3(), C = 6, G = new Map(), key = (i, j) => i*100003 + j;
    for(const S of paths) for(let s = 0; s < S.pts.length; s++){ const q = S.pts[s], k = key(Math.floor(q.x/C), Math.floor(q.z/C)); let a = G.get(k); if(!a) G.set(k, a = []); a.push(q); }
    const near = (x, z, r) => { const i0 = Math.floor((x - r)/C), i1 = Math.floor((x + r)/C), j0 = Math.floor((z - r)/C), j1 = Math.floor((z + r)/C);
      for(let i = i0; i <= i1; i++) for(let j = j0; j <= j1; j++){ const a = G.get(key(i, j)); if(a) for(const q of a) if((q.x - x)*(q.x - x) + (q.z - z)*(q.z - z) < r*r) return true; } return false; };
    scene.traverse(o => { if(!o.isInstancedMesh || o.parent === deco) return; let ch = false;
      if(!o.geometry.boundingSphere) o.geometry.computeBoundingSphere(); const R0 = o.geometry.boundingSphere ? o.geometry.boundingSphere.radius : 1;
      for(let i = 0; i < o.count; i++){ o.getMatrixAt(i, M); const e = M.elements, sc = Math.max(Math.hypot(e[0], e[1], e[2]), Math.hypot(e[8], e[9], e[10])); if(sc === 0) continue; v.setFromMatrixPosition(M);
        const rr = Math.min(40, R0*sc*0.8); if(near(v.x, v.z, Math.max(2.6, rr + 1.2))){ o.setMatrixAt(i, Z); ch = true; } }
      if(ch) o.instanceMatrix.needsUpdate = true; }); }
  if(typeof ROCKC !== 'undefined' && ROCKC){ const ob = ROCKC.blocked.bind(ROCKC); ROCKC.blocked = (x, z) => onSide(x, z, 2.2) ? false : ob(x, z); }
  // ---- 발견 · 고르기 · 따라 걷기 ----
  let ask = null, follow = null;
  const box = $('sideAsk');
  const showAsk = S => { ask = S; $('sdName').textContent = nm(S); $('sdTheme').textContent = T_(({steep:'깎아지른 오르막', crevice:'바위 틈 길', cave:'바위 굴'})[S.theme]); box.hidden = false; clearTimeout(box._t); if(st.auto) box._t = setTimeout(() => { if(ask === S){ box.hidden = true; ask = null; } }, 6000); };
  $('sdNo').onclick = () => { box.hidden = true; ask = null; canvas.focus(); };
  const endFollow = msg => { if(!follow) return; follow = null; if(st.goal && st.goal.__side) st.goal = null; goalRing.visible = false; document.body.classList.remove('sideFollow'); if(msg) toast(T_(msg), 2.6); };
  $('sdGo').onclick = () => { const S = ask; box.hidden = true; ask = null; if(!S) return; follow = { S, s: S.e, g: null, t: performance.now(), px: st.x, pz: st.z }; st.auto = false; refreshWalk(); st.sitting = false; document.body.classList.add('sideFollow'); canvas.focus(); };
  // 숨은 길을 따라 걷는 중에도 '멈추기'가 보이고, 누르면 바로 멈춰요
  { const bw = $('bWalk'); if(bw) bw.addEventListener('click', e => { if(follow){ e.stopImmediatePropagation(); endFollow(); } }, true); }
  let tick = 0;
  return {
    paths, found,
    update(){
      if(follow){
        // 직접 조작(키보드·조이스틱·땅 클릭)이나 자동 걷기·멈추기를 누르면 따라 걷기를 그만둬요
        const userMove = ['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].some(k => keys[k]) || (joy.id !== null && Math.hypot(joy.x, joy.y) > 0.18);
        if(userMove || st.auto || (follow.g && st.goal !== follow.g)){ endFollow(); }
      }
      if(follow){ const S = follow.S, pts = S.pts; let s = follow.s; while(s < pts.length - 1 && Math.hypot(pts[s].x - st.x, pts[s].z - st.z) < 2.2) s++;
        // 막혀서 못 가면: 4초마다 다음 점으로 건너뛰고, 12초가 지나면 탐방로 합류 지점으로 옮겨 줘요
        const nowT = performance.now();
        if(s !== follow.s || Math.hypot(st.x - follow.px, st.z - follow.pz) > 1.2){ follow.t = nowT; follow.px = st.x; follow.pz = st.z; follow.st0 = follow.st0 && s === follow.s ? follow.st0 : 0; }
        else if(nowT - follow.t > 4000){ follow.st0 = (follow.st0 || 0) + 1; follow.t = nowT; s = Math.min(pts.length - 1, s + 3);
          if(follow.st0 >= 3){ const q = pts[pts.length - 1], q2 = trail[Math.min(trail.length - 1, S.b + 4)]; endFollow('길이 막혀 있어서 탐방로로 옮겨 드렸어요'); adminTeleport(q.x, q.z, Math.atan2(q2.x - q.x, q2.z - q.z)); return; } }
        follow.s = s;
        if(s >= pts.length - 1 && Math.hypot(pts[s].x - st.x, pts[s].z - st.z) < 2.5){ endFollow('다시 탐방로로 나왔어요'); st.auto = true; refreshWalk(); }
        else { const g = { x: pts[s].x, z: pts[s].z, __side: 1 }; st.goal = g; follow.g = g; goalRing.visible = false; } }
      if((tick++ % 10) !== 0 || st.finished) return;
      for(const S of paths){ if(found(S.k)) continue; const p = S.pts[S.e]; if(Math.hypot(p.x - st.x, p.z - st.z) < 7){ me.tr.push(S.k); S._askedAt = Date.now(); save(); try{ sfx.chime && sfx.chime(); }catch(e){} banner(T_('숨은 길 발견!'), nm(S), 3); showAsk(S); break; } }
      // 이미 찾은 길 입구에 다시 서면 또 고를 수 있어요
      if(!ask && !follow){ for(const S of paths){ if(!found(S.k)) continue; const p = S.pts[S.e]; if(Math.hypot(p.x - st.x, p.z - st.z) < 3.5 && (!S._askedAt || Date.now() - S._askedAt > 60000)){ S._askedAt = Date.now(); showAsk(S); break; } } }
      if(ask && Math.hypot(ask.pts[ask.e].x - st.x, ask.pts[ask.e].z - st.z) > 25){ box.hidden = true; ask = null; }
    },
    stop(){ endFollow(); },
    get following(){ return !!follow; },
    on(x, z){ return !!follow || !!onSide(x, z, 2.6); },
    summit(){ me.sum = 1; save(); },
    draw(mctx, toU, toV, big){ const adm = isAdm(); for(const S of paths){ const f = found(S.k); if(!f && !adm) continue; const col = f ? '#9fe0a8' : '#ffb347';
        mctx.save(); mctx.strokeStyle = col; mctx.lineWidth = big ? 2.4 : 5; mctx.setLineDash(big ? [5, 4] : [10, 8]); mctx.beginPath();
        S.pts.forEach((p, i) => { const u = toU(p.x), v = toV(p.z); i ? mctx.lineTo(u, v) : mctx.moveTo(u, v); }); mctx.stroke(); mctx.setLineDash([]);
        const p = S.pts[S.e]; mctx.fillStyle = col; mctx.strokeStyle = '#1e2a1e'; mctx.lineWidth = big ? 1.5 : 3; mctx.beginPath(); mctx.arc(toU(p.x), toV(p.z), big ? 4.5 : 9, 0, 7); mctx.fill(); mctx.stroke();
        if(adm){ mctx.font = `bold ${big ? 12 : 26}px sans-serif`; mctx.textAlign = 'left'; mctx.lineWidth = big ? 3 : 6; mctx.strokeStyle = 'rgba(20,20,20,.85)'; const t = (S.k + 1) + ' ' + nm(S), u = toU(p.x) + (big ? 7 : 14), v = toV(p.z) + (big ? 4 : 9); mctx.strokeText(t, u, v); mctx.fillStyle = col; mctx.fillText(t, u, v); }
        mctx.restore(); } },
    // 관리자: 입구로 바로 이동 · 이 산 숨은 길 기록 지우기
    label: S => nm(S),
    goTo(k){ this.adminGo(k); },
    adminGo(k){ const S = paths.find(q => q.k === k); if(!S) return; if(!st.started){ toast('먼저 산행을 시작해 주세요', 2); return; }
      const p = S.pts[Math.max(0, S.e - 1)], q = S.pts[Math.min(S.pts.length - 1, S.e + 1)]; endFollow(); adminTeleport(p.x, p.z, Math.atan2(q.x - p.x, q.z - p.z)); S._askedAt = 0; },
    adminReset(){ me.tr = []; me.sum = 0; const p = store.get('prog', {}); if(p[MID]){ p[MID].tr = []; delete p[MID].sum; } store.set('prog', p); try{ cloudPush(true); }catch(e){} for(const S of paths) S._askedAt = 0; toast('이 산의 숨은 길·완등 기록을 지웠어요', 2.5); },
  };
})();
window.__SIDE = SIDE;
{ const box = $('adSide'); if(box){
  SIDE.paths.forEach(S => { const b = document.createElement('button'); b.textContent = (S.k + 1) + '. ' + S.name; b.title = S.theme; b.onclick = () => SIDE.adminGo(S.k); box.appendChild(b); });
  const r = document.createElement('button'); r.textContent = '기록 지우기'; r.onclick = () => SIDE.adminReset(); box.appendChild(r);
  const n = $('adSideN'); if(n) n.textContent = SIDE.paths.length + '개'; } }
'''


def side_rows():
    rows = list(THEME_ROWS)
    return rows


def patch_side(P, m):
    defs = NAMES.get(m['id'])
    if not defs: return
    P.rep('</style>', SIDE_CSS + '</style>', 1)
    P.rep('<div id="mapWrap" class="hud glass click">', SIDE_HTML + '\n<div id="mapWrap" class="hud glass click">', 1)
    P.rep('<button data-ad="goCamp">야영장</button></div>', '<button data-ad="goCamp">야영장</button></div>\n  <div class="adSec">숨은 길 <span id="adSideN"></span> <small>· 관리자에게만 보여요 · 누르면 입구로 이동</small></div>\n  <div class="adRow" id="adSide"></div>', 1)
    P.rep("window.__game = {", SIDE_JS.replace('__ID__', m['id']).replace('__DEF__', json.dumps(defs, ensure_ascii=False)) + "window.__game = {", 1)
    # 매 프레임: 갈래길 따라 걷기·발견 확인
    P.rep("\n  camera.lookAt(camLook);", "\n  camera.lookAt(camLook);\n  if(window.__SIDE) window.__SIDE.update();", 1)
    # 갈래길 위는 탐방로로 쳐요 (느려짐·'너무 가파름' 경고 없음)
    P.rep("const onTrail = nt.d < 3.2 || st.inSummit;", "const onTrail = nt.d < 3.2 || st.inSummit || !!(window.__SIDE && window.__SIDE.on(st.x, st.z));", 1)
    P.rep("  if(st.camp || st.inSummit) setWarn('');", "  if(st.camp || st.inSummit || (window.__SIDE && window.__SIDE.on(st.x, st.z))) setWarn('');", 1)
    # 직접 움직이면 따라 걷기 멈춤
    P.rep("if(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code)){ stopAuto(); st.goal=null; }",
          "if(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code)){ stopAuto(); st.goal=null; if(window.__SIDE) window.__SIDE.stop(); }", 1)
    # 지도에 찾은 길
    P.rep("  const dot = (x,z,col,rad) => {", "  if(window.__SIDE) window.__SIDE.draw(mctx, toU, toV, big);\n  const dot = (x,z,col,rad) => {", 1)
    # 완등 저장
    P.rep("function finish(){ clearHike();", "function finish(){ clearHike(); try{ window.__SIDE && window.__SIDE.summit(); }catch(e){}", 1)
    # 계정(구글 로그인)에도 저장·불러오기
    P.rep("t: fb.D.serverTimestamp() }", "prog: store.get('prog', {}), t: fb.D.serverTimestamp() }", 1)
    P.rep("    return changed; }catch(e){ return false; } }",
          "    if(c.prog && typeof c.prog === 'object'){ const lp = store.get('prog', {}); for(const k in c.prog){ const a = c.prog[k] || {}, b = lp[k] || (lp[k] = {}); if(a.sum) b.sum = 1; b.tr = [...new Set([...(b.tr || []), ...((a.tr || []).filter(Number.isInteger))])]; if(a.n && !b.n) b.n = a.n; } store.set('prog', lp); }\n"
          "    return changed; }catch(e){ return false; } }", 1)
