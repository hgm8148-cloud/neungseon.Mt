"""미리보기 아티팩트 첫 화면: 20개 산 카드 + 실제 지형으로 그린 고도 단면."""
import json, os, base64, math
import numpy as np, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patches2 import thumb_svg
HERE = os.path.dirname(os.path.abspath(__file__))
COUNTRY = {'kr':'대한민국','np':'네팔','jp':'일본','tz':'탄자니아','ch':'스위스','fr':'프랑스','it':'이탈리아','us':'미국','cn':'중국','cl':'칠레','nz':'뉴질랜드'}
def profile(d):
    N, S = d['N'], d['size']; c = S/(N-1); h = np.frombuffer(base64.b64decode(d['h']), '<u2').astype(float).reshape(N, N)/10
    M = d['meta']; tr = d['trail']; out = []; s = 0
    for k, (x, z) in enumerate(tr):
        if k: s += math.dist(tr[k-1], tr[k])
        gx, gz = min(max((x+S/2)/c, 0), N-1.001), min(max((z+S/2)/c, 0), N-1.001); i, j = int(gx), int(gz); u, w = gx-i, gz-j
        v = (h[j,i]*(1-u)+h[j,i+1]*u)*(1-w)+(h[j+1,i]*(1-u)+h[j+1,i+1]*u)*w
        out.append((s, M['H0']+(v-M['H0'])*M['VEX']+M['BASE']))
    return out
cards = {'kr': [], 'world': []}
for f in os.listdir(os.path.join(HERE, 'mountains')):
    m = json.load(open(os.path.join(HERE, 'mountains', f))); d = json.load(open(os.path.join(HERE, 'data', m['id']+'.json')))
    pr = profile(d); L = pr[-1][0]; hs = [p[1] for p in pr]; lo, hi = min(hs), max(hs)
    gain = sum(max(0, b-a) for a, b in zip(hs[::10], hs[10::10]))
    W, H = 280, 64; pad = 4
    pts = [(p[0]/L*W, H-pad-(p[1]-lo)/max(1, hi-lo)*(H-2*pad)) for p in pr[::max(1, len(pr)//140)]] + [(W, H-pad-(hs[-1]-lo)/max(1,hi-lo)*(H-2*pad))]
    line = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    sub = m['course']['ko'] if m['region'] == 'kr' else f"{COUNTRY[m['flag']]} · {m['course']['ko']}"
    cards[m['region']].append((m['order'], f'''<a class="card" href="{m['id']}.html?go=1" data-id="{m['id']}">
  <div class="pic">{thumb_svg(m, d)}</div>
  <div class="top"><b>{m['area']['ko']}</b><span class="en">{m['area']['en']}</span></div>
  <div class="sub">{sub}</div>
  <svg viewBox="0 0 {W} {H}" preserveAspectRatio="none" aria-hidden="true"><polygon points="0,{H} {line} {W},{H}" class="fill"/><polyline points="{line}" class="ln"/></svg>
  <div class="nums"><span>{round(hs[0]):,}m → <b>{m['elev']:,}m</b></span><span>{L/1000:.1f} km</span><span>↑{round(gain):,}m</span></div>
  <div class="end">{m['waypoints'][0]['ko']} → {m['end']['ko']}</div>
</a>'''))
sec = lambda r: '\n'.join(c for _, c in sorted(cards[r]))
html = f'''<title>능선 20개 산 미리보기</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Gowun+Dodum&display=swap">
<style>
/* 레이아웃: 게임 오프닝과 같은 새벽 남색 바탕 위에 산 카드 격자, 카드마다 실제 지형 고도 단면 */
:root{{--bg:#1d2338;--card:#262d47;--line:rgba(246,234,214,.14);--fg:#f6ead6;--mute:rgba(246,234,214,.66);--maple:#e9a25a;--ridge:#c8562a;
--display:"Gowun Batang","Noto Serif KR",serif;--body:"Gowun Dodum","Apple SD Gothic Neo","Malgun Gothic",sans-serif;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:var(--body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 48px}}
main{{max-width:1080px;margin:0 auto;display:flex;flex-direction:column;gap:28px}}
header{{display:flex;flex-direction:column;gap:8px}}
.badge{{align-self:flex-start;font-size:12px;letter-spacing:.06em;padding:3px 10px;border-radius:999px;border:1px solid var(--line);color:var(--mute)}}
h1{{font-family:var(--display);font-size:clamp(28px,5vw,42px);margin:0;text-wrap:balance}}
header p{{margin:0;color:var(--mute);line-height:1.6;max-width:64ch}}
h2{{font-family:var(--display);font-size:22px;margin:0 0 12px;display:flex;gap:10px;align-items:baseline}}
h2 small{{font-family:var(--body);font-size:13px;color:var(--mute);font-weight:400}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}}
.pic{{margin:-14px -14px 4px;aspect-ratio:16/9;overflow:hidden;border-radius:13px 13px 0 0}} .pic svg{{width:100%;height:100%;display:block}}
.card{{display:flex;flex-direction:column;gap:6px;padding:14px 14px 12px;border-radius:14px;background:var(--card);border:1px solid var(--line);color:inherit;text-decoration:none;min-width:0;transition:border-color .15s,transform .15s}}
.card:hover,.card:focus-visible{{border-color:var(--maple);transform:translateY(-2px);outline:none}}
.top{{display:flex;gap:8px;align-items:baseline;justify-content:space-between}}
.top b{{font-family:var(--display);font-size:20px}}
.en{{font-size:12px;color:var(--mute);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.sub,.end{{font-size:12.5px;color:var(--mute)}}
svg{{width:100%;height:56px;display:block}}
.fill{{fill:var(--ridge);opacity:.28}} .ln{{fill:none;stroke:var(--maple);stroke-width:1.6;vector-effect:non-scaling-stroke}}
.nums{{display:flex;justify-content:space-between;gap:8px;font-size:13px;font-variant-numeric:tabular-nums}}
.nums b{{color:var(--maple)}}
footer{{color:var(--mute);font-size:12.5px;line-height:1.7}}
@media (prefers-reduced-motion:reduce){{.card{{transition:none}}}}
</style>
<main>
<header>
  <span class="badge">미리보기 · 아직 배포 전</span>
  <h1>능선, 20개의 산길</h1>
  <p>국내 명산 10곳과 해외 명산 10곳을 실제 고도 데이터로 만들었어요. 카드를 누르면 그 산에서 바로 시작하고, 게임 안 시작 화면의 ‘다른 산 고르기’로 언제든 산을 바꿀 수 있어요. 그래프는 각 코스의 실제 지형 고도 단면이에요.</p>
</header>
<section><h2>국내 명산 10 <small>대한민국</small></h2><div class="grid">{sec('kr')}</div></section>
<section><h2>해외 명산 10 <small>6개 대륙</small></h2><div class="grid">{sec('world')}</div></section>
<footer>지형 고도: AWS Terrain Tiles (Mapzen Terrarium, SRTM 등 공개 DEM, 약 30m 해상도). 탐방로는 주요 지점을 지형에 맞춰 이은 근사치예요. 지금은 모든 산이 북한산 가을 숲으로 그려져요(산별 식생은 다음 단계). 페이지 하나가 약 2MB라 처음 열 때 몇 초 걸려요.</footer>
</main>
<script>document.querySelectorAll('.card').forEach(a=>a.addEventListener('click',()=>{{try{{sessionStorage.setItem('neungseon.go',a.dataset.id);}}catch(e){{}}}}));</script>
'''
open(os.path.join(HERE, 'preview', 'launcher.html'), 'w').write(html)
print('ok', len(html))
