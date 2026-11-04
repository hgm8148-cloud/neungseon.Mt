"""게임 템플릿 + 산 설정 + 지형 데이터 → 산마다 페이지 한 장.

    python3 build_site.py                       # 미리보기: pipeline/out/ 에 20개 페이지
    python3 build_site.py --to-site             # 저장소 루트(index.html=북한산, hallasan.html …)에 쓰기 (배포 전 승인 필요)
    python3 build_site.py --template game.photo.html --only hallasan

템플릿은 다른 작업이 계속 고치는 game.template.html(또는 photo_patch.py 결과처럼 __DATA__가 남은 파일)을
그대로 읽고, 북한산에 묶여 있던 글자·숫자만 산 설정 값으로 바꿔 끼워요. 템플릿 원본은 건드리지 않아요.
바꿔 끼울 자리를 못 찾으면 멈추고 어디인지 알려 줘요(템플릿이 바뀌었을 때 여기만 고치면 돼요).
"""
import argparse, base64, json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patches2 import EXTRA_ROWS, SEASON_ROWS, patch_common, thumb_svg
from photos_patch import patch_photos, copy_photos, hero_url
from sky_patch import patch_sky, SKY_ROWS
from avatar_patch import patch_avatar
from weather_patch import patch_weather, WX_ROWS
from release_patch import patch_release
from lang_patch import patch_lang
from sound_patch import patch_sound
from camera_patch import patch_camera
from look_patch import patch_look
from landmark_patch import patch_landmark, lm_rows
from admin_patch import patch_admin
from ios_patch import patch_ios, patch_install, INST_ROWS
from ui_patch import patch_ui, UIX_ROWS
from moon_patch import patch_moon
from far_patch import patch_far, patch_flora
from vista_patch import patch_vista
from trail_patch import patch_trail
from loader_patch import patch_loader, loader_rows
from i18n_fix_patch import patch_i18n_fix, FIX_ROWS

HERE = os.path.dirname(os.path.abspath(__file__))
PF = '/mnt/project-files/hiking-game'
LANGS = ('ko', 'en', 'ja', 'zh')

COUNTRY = {
    'kr': ('대한민국', 'Korea', '韓国', '韩国'), 'np': ('네팔', 'Nepal', 'ネパール', '尼泊尔'), 'jp': ('일본', 'Japan', '日本', '日本'),
    'tz': ('탄자니아', 'Tanzania', 'タンザニア', '坦桑尼亚'), 'ch': ('스위스', 'Switzerland', 'スイス', '瑞士'),
    'fr': ('프랑스', 'France', 'フランス', '法国'), 'it': ('이탈리아', 'Italy', 'イタリア', '意大利'), 'us': ('미국', 'USA', 'アメリカ', '美国'),
    'cn': ('중국', 'China', '中国', '中国'), 'cl': ('칠레', 'Chile', 'チリ', '智利'), 'nz': ('뉴질랜드', 'New Zealand', 'ニュージーランド', '新西兰'),
}
# 선택 화면 등 공통 문구 [ko, en, ja, zh]
UI_ROWS = [
    ['어느 산에 오를까요?', 'Which mountain today?', 'どの山に登りますか？', '今天爬哪座山？'],
    ['실제 고도 데이터로 만든 산길을 골라 보세요', 'Pick a trail built from real elevation data', '実際の標高データで作った山道を選んでください', '选择一条用真实海拔数据制作的山路'],
    ['국내 명산 10', 'Korea · 10 mountains', '韓国の名山 10', '韩国名山 10'],
    ['해외 명산 10', 'World · 10 mountains', '世界の名山 10', '世界名山 10'],
    ['다른 산 고르기', 'Choose another mountain', '別の山を選ぶ', '选择其他山'],
    ['지금 이 산', 'You are here', 'いまの山', '当前所在'],
    ['준비 중', 'Coming soon', '準備中', '准备中'],
    ['이 산으로 계속', 'Stay on this mountain', 'この山で続ける', '继续这座山'],
    ['잠시 숨을 고르고 가세요.', 'Catch your breath for a moment.', '少し息を整えていきましょう。', '稍微喘口气再走吧。'],
]


def L(d, l):
    return (d or {}).get(l) or (d or {}).get('en') or (d or {}).get('ko') or ''


def js(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")


def area_peak(m, l):
    a, p = L(m['area'], l), L(m['peak'], l)
    if a == p: return a
    return a + {'ko': ' ', 'en': ' · ', 'ja': '・', 'zh': ' · '}[l] + p


def mountain_rows(m):
    """모든 페이지에 넣는 이름 번역(선택 화면에서 쓰여요)."""
    rows = []
    for key in ('area', 'peak', 'end', 'course', 'trailheadArea'):
        if m.get(key): rows.append([L(m[key], l) for l in LANGS])
    for w in m['waypoints']: rows.append([L(w, l) for l in LANGS])
    rows.append(list(COUNTRY[m['flag']]))
    return rows


def page_rows(m):
    """이 산 페이지에서만 쓰는 문장 번역."""
    e = m['elev']; th = m['trailheadArea']; sub = m['summitSub']; end = m['end']; peak = m['peak']; area = m['area']
    R = []
    R.append([area_peak(m, l) for l in LANGS])
    R.append([f"{L(area,'ko')} · {L(peak,'ko')} {e}m", f"{L(area,'en')} · {L(peak,'en')} {e} m", f"{L(area,'ja')}・{L(peak,'ja')} {e}m", f"{L(area,'zh')} · {L(peak,'zh')} {e}米"])
    R.append([f"{L(end,'ko')} {e}m", f"{L(end,'en')} {e} m", f"{L(end,'ja')} {e}m", f"{L(end,'zh')} {e}米"])
    R.append([f"{L(end,'ko')} 360°", f"{L(end,'en')} 360°", f"{L(end,'ja')} 360°", f"{L(end,'zh')} 360°"])
    R.append([f"해발 {e}m · {L(sub,'ko')}", f"{e} m · {L(sub,'en')}", f"標高{e}m・{L(sub,'ja')}", f"海拔{e}米 · {L(sub,'zh')}"])
    R.append([L(m['vista'], l) for l in LANGS])
    R.append([tagline(m, l) for l in LANGS])
    R.append([f"{L(peak,'ko')}에서 맞는 해돋이", f"Sunrise from {L(peak,'en')}", f"{L(peak,'ja')}で迎える日の出", f"在{L(peak,'zh')}迎接日出"])
    R.append([f"{L(th,'ko')} 들머리", f"{L(th,'en')} trailhead", f"{L(th,'ja')}登山口", f"{L(th,'zh')}登山口"])
    mids = m['waypoints'][1:-1]
    if mids:
        R.append(['→ ' + ' → '.join(L(w, l) for w in mids) + ' →' for l in LANGS])
    for k, d in wp_desc(m).items():
        R.append(d)
    return R


def tagline(m, l):
    a, end = L(m['area'], l), L(m['end'], l)
    both = end.startswith(a)
    if l == 'ko': return f"{end if both else a + ' ' + end}에 함께 오르다"
    if l == 'en': return f"Climbing to {end if both else end + ' on ' + a} together"
    if l == 'ja': return f"{end if both else a + '・' + end}へいっしょに登る"
    return f"一起登上{end if both else a + end}"


def wp_desc(m):
    """{지점 이름(ko): [ko,en,ja,zh]}"""
    e = m['elev']; th = m['trailheadArea']; sub = m['summitSub']; out = {}
    W = m['waypoints']
    for i, w in enumerate(W):
        d = w.get('desc')
        if d and all(d.get(l) for l in LANGS):
            out[w['ko']] = [d[l] for l in LANGS]; continue
        if i == 0 and not d:
            out[w['ko']] = [f"{L(th,'ko')} 들머리. 산행을 시작합니다.", f"Trailhead at {L(th,'en')}. Your hike begins here.",
                            f"{L(th,'ja')}の登山口。ここから山歩きが始まります。", f"{L(th,'zh')}登山口，从这里出发。"]
        elif i == len(W) - 1 and not d:
            se = L(sub, 'en'); se = se[:1].upper() + se[1:]
            out[w['ko']] = [f"{L(sub,'ko')}, 해발 {e}m.", f"{se}, {e} m above sea level.", f"{L(sub,'ja')}、標高{e}m。", f"{L(sub,'zh')}，海拔{e}米。"]
        elif d:
            out[w['ko']] = [d.get(l) or d.get('en') or d['ko'] for l in LANGS]
        else:
            out[w['ko']] = UI_ROWS[-1]
    return out


# ---------------- 템플릿 바꿔 끼우기 ----------------
class Patch:
    def __init__(self, t, name):
        self.t, self.name, self.warn = t, name, []

    def rep(self, a, b, n=None, need=True):
        c = self.t.count(a)
        if (n is not None and c != n) or (need and c == 0):
            raise SystemExit(f"[{self.name}] 템플릿에서 바꿀 자리를 못 찾았어요 ({c}곳): {a[:80]!r}")
        self.t = self.t.replace(a, b)
        return c

    def sub(self, pat, b, need=True, flags=0):
        t2, c = re.subn(pat, b, self.t, flags=flags)
        if need and c == 0: raise SystemExit(f"[{self.name}] 패턴을 못 찾았어요: {pat[:80]!r}")
        self.t = t2
        return c


def split_R(t):
    a = t.index('  const R = [')
    b = t.index('\n  ];', a)
    return t[:a], t[a:b], t[b:]


FLAG_JS = r'''
  const FS = __FLAG__;
  const W_ = 384, H_ = 256;
  if(FS.t === 'v' || FS.t === 'h'){ const n = FS.c.length; FS.c.forEach((col,i)=>{ x.fillStyle = col; if(FS.t==='v') x.fillRect(i*W_/n,0,W_/n+1,H_); else x.fillRect(0,i*H_/n,W_,H_/n+1); }); }
  else if(FS.t === 'jp'){ x.fillStyle='#fff'; x.fillRect(0,0,W_,H_); x.fillStyle='#bc002d'; x.beginPath(); x.arc(W_/2,H_/2,H_*0.3,0,7); x.fill(); }
  else if(FS.t === 'ch'){ x.fillStyle='#da291c'; x.fillRect(0,0,W_,H_); x.fillStyle='#fff'; x.fillRect(W_/2-22,H_/2-80,44,160); x.fillRect(W_/2-80,H_/2-22,160,44); }
  else if(FS.t === 'cn'){ x.fillStyle='#de2910'; x.fillRect(0,0,W_,H_); x.fillStyle='#ffde00'; const star=(cx,cy,r,rot)=>{ x.beginPath(); for(let i=0;i<10;i++){ const rr=i%2?r*0.38:r, a=rot+i*Math.PI/5-Math.PI/2; x.lineTo(cx+Math.cos(a)*rr, cy+Math.sin(a)*rr); } x.fill(); }; star(64,64,38,0); [[128,26],[154,52],[154,90],[128,116]].forEach(([a,b])=>star(a,b,12,0.4)); }
  else if(FS.t === 'tz'){ x.fillStyle='#1eb53a'; x.beginPath(); x.moveTo(0,0); x.lineTo(W_,0); x.lineTo(0,H_); x.fill(); x.fillStyle='#00a3dd'; x.beginPath(); x.moveTo(W_,0); x.lineTo(W_,H_); x.lineTo(0,H_); x.fill(); x.strokeStyle='#fcd116'; x.lineWidth=96; x.beginPath(); x.moveTo(-10,H_+10); x.lineTo(W_+10,-10); x.stroke(); x.strokeStyle='#000'; x.lineWidth=64; x.stroke(); }
  else if(FS.t === 'us'){ for(let i=0;i<13;i++){ x.fillStyle=i%2?'#fff':'#b22234'; x.fillRect(0,i*H_/13,W_,H_/13+1); } x.fillStyle='#3c3b6e'; x.fillRect(0,0,W_*0.4,H_*7/13); x.fillStyle='#fff'; for(let r=0;r<9;r++) for(let c=0;c<(r%2?5:6);c++){ x.beginPath(); x.arc(10+c*25+(r%2?12:0), 9+r*14.5, 3.2, 0, 7); x.fill(); } }
  else if(FS.t === 'cl'){ x.fillStyle='#fff'; x.fillRect(0,0,W_,H_/2); x.fillStyle='#d52b1e'; x.fillRect(0,H_/2,W_,H_/2); x.fillStyle='#0039a6'; x.fillRect(0,0,H_/2,H_/2); x.fillStyle='#fff'; x.beginPath(); for(let i=0;i<10;i++){ const rr=i%2?14:36, a=i*Math.PI/5-Math.PI/2; x.lineTo(64+Math.cos(a)*rr, 64+Math.sin(a)*rr); } x.fill(); }
  else if(FS.t === 'nz'){ x.fillStyle='#012169'; x.fillRect(0,0,W_,H_); x.strokeStyle='#fff'; x.lineWidth=26; x.beginPath(); x.moveTo(0,0); x.lineTo(W_/2,H_/2); x.moveTo(W_/2,0); x.lineTo(0,H_/2); x.stroke(); x.strokeStyle='#c8102e'; x.lineWidth=9; x.stroke(); x.fillStyle='#fff'; x.fillRect(W_/4-21,0,42,H_/2); x.fillRect(0,H_/4-21,W_/2,42); x.fillStyle='#c8102e'; x.fillRect(W_/4-12,0,24,H_/2); x.fillRect(0,H_/4-12,W_/2,24); x.fillStyle='#c8102e'; [[290,60],[250,128],[330,120],[292,210]].forEach(([a,b])=>{ x.beginPath(); for(let i=0;i<10;i++){ const rr=i%2?6:15, an=i*Math.PI/5-Math.PI/2; x.lineTo(a+Math.cos(an)*rr, b+Math.sin(an)*rr); } x.fill(); }); }
  else if(FS.t === 'np'){ ['#1f5fbf','#f5f5f0','#c8312c','#2c8a3e','#f2c230'].forEach((col,i)=>{ x.fillStyle=col; x.fillRect(i*W_/5,0,W_/5+1,H_); }); }
'''
FLAGS = {'fr': {'t': 'v', 'c': ['#0055a4', '#fff', '#ef4135']}, 'it': {'t': 'v', 'c': ['#009246', '#fff', '#ce2b37']},
         'jp': {'t': 'jp'}, 'ch': {'t': 'ch'}, 'cn': {'t': 'cn'}, 'tz': {'t': 'tz'}, 'us': {'t': 'us'}, 'cl': {'t': 'cl'}, 'nz': {'t': 'nz'}, 'np': {'t': 'np'}}


def selector_html():
    return '''
<div id="mtSel" class="panel" hidden>
  <div class="mtCard">
    <div class="mtHead">
      <div><h1>어느 산에 오를까요?</h1><p>실제 고도 데이터로 만든 산길을 골라 보세요</p></div>
      <button type="button" class="mtX" id="mtX" aria-label="닫기">✕</button>
    </div>
    <p class="mtSaved" id="mtSaved" hidden>지금까지 걸은 기록을 저장했어요</p>
    <div class="mtTabs" role="tablist"><button type="button" data-r="kr">국내 명산 10</button><button type="button" data-r="world">해외 명산 10</button></div>
    <div class="mtList" id="mtList"></div>
  </div>
</div>
'''


SEL_CSS = '''
#mtSel{z-index:15;background:rgba(40,52,74,.35);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}
.mtCard{width:min(980px,100%);max-height:calc(100vh - 32px);display:flex;flex-direction:column;gap:12px;padding:22px 22px 18px;border-radius:24px;
  background:linear-gradient(180deg,#fffaf2 0%,#f4f8ff 100%);color:#24304a;box-shadow:0 24px 60px rgba(20,30,60,.28)}
.mtHead{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.mtHead h1{margin:0;font-family:var(--display);font-size:clamp(22px,3.4vw,30px);color:#1f2a44}
.mtHead p{margin:4px 0 0;font-size:14px;color:#5b6784}
.mtX{width:38px;height:38px;border-radius:50%;border:none;background:#eef1f8;color:#33405e;font-size:16px;cursor:pointer;flex:none}
.mtX:hover{background:#e2e7f3}
.mtTabs{display:flex;gap:4px;padding:4px;border-radius:999px;background:#e9eef7;align-self:flex-start}
.mtTabs button{padding:9px 18px;border-radius:999px;border:none;background:transparent;color:#4b5877;font-size:15px;cursor:pointer;transition:background .2s,color .2s}
.mtTabs button.on{background:#fff;color:#1f2a44;box-shadow:0 2px 8px rgba(30,45,80,.14);font-weight:700}
.mtList{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));grid-auto-rows:max-content;align-content:start;gap:14px;overflow:auto;padding:4px 4px 8px;min-height:0}
.mtItem{flex:none;height:auto;display:flex;flex-direction:column;text-align:left;padding:0;border-radius:18px;border:none;background:#fff;color:#24304a;cursor:pointer;overflow:hidden;
  box-shadow:0 4px 14px rgba(30,45,80,.10);transition:transform .18s ease,box-shadow .18s ease;font-family:inherit}
.mtItem:hover,.mtItem:focus-visible{transform:translateY(-3px);box-shadow:0 12px 26px rgba(30,45,80,.18);outline:none}
.mtPic{flex:none;position:relative;aspect-ratio:16/9;width:100%;background:#dde7f3}
.mtPic svg{width:100%;height:100%;display:block}
.mtPic img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .5s ease}
.mtPic img.on{opacity:1}
.mtPic .mtTag{position:absolute;left:10px;top:10px;font-size:11.5px;padding:3px 10px;border-radius:999px;background:rgba(255,255,255,.92);color:#c8562a;font-weight:700}
.mtPic .mtElev{position:absolute;right:10px;bottom:8px;font-size:12px;padding:2px 9px;border-radius:999px;background:rgba(20,28,48,.55);color:#fff;font-variant-numeric:tabular-nums}
.mtBody{display:flex;flex-direction:column;gap:3px;padding:11px 14px 13px}
.mtBody b{font-family:var(--display);font-size:18px;color:#1f2a44}
.mtBody .mtSub{font-size:12.5px;color:#66728c;line-height:1.4}
.mtItem.here{box-shadow:0 0 0 3px #e9a25a,0 8px 22px rgba(200,86,42,.25)}
.mtSaved{margin:0;font-size:13px;color:#2f7a55;background:#e6f4ec;border-radius:10px;padding:7px 12px;align-self:flex-start}
#mtOpen{margin-bottom:8px}
@media (max-width:520px){.mtCard{padding:16px 14px 12px;border-radius:18px}.mtList{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.mtBody b{font-size:16px}.mtBody{padding:9px 10px 11px}}
@media (prefers-reduced-motion:reduce){.mtItem{transition:none}}
'''


def selector_js(cur, mts):
    lst = [dict(id=m['id'], r=m['region'], page=m['page'], built=m['_built'], area=m['area']['ko'], end=m['end']['ko'],
                course=(m.get('course') or {}).get('ko', ''), country=COUNTRY[m['flag']][0], elev=m['elev'], km=m.get('_km'), pic=m.get('_thumb', ''), photo=hero_url(m['id'])) for m in mts]
    key = 'hike' if any(m.get('legacy') and m['id'] == cur for m in mts) else 'hike.' + cur
    return '''
<script>
// ---------- 산 고르기: 오프닝이 끝나면 국내 10 / 해외 10 가운데 고르기 · 산 이름을 누르면 기록 저장 후 다시 열기 ----------
(function(){
  const CUR = %s, MTS = %s, KEY = %s;
  const box = document.getElementById('mtSel'), list = document.getElementById('mtList'), saved = document.getElementById('mtSaved');
  const here = MTS.find(m => m.id === CUR) || MTS[0];
  let tab = here.r;
  function draw(){
    document.querySelectorAll('.mtTabs button').forEach(b => { const on = b.dataset.r === tab; b.classList.toggle('on', on); b.setAttribute('aria-selected', on); });
    list.innerHTML = '';
    MTS.filter(m => m.r === tab).forEach(m => {
      const b = document.createElement('button'); b.type = 'button'; b.className = 'mtItem' + (m.id === CUR ? ' here' : '');
      const pic = document.createElement('div'); pic.className = 'mtPic'; pic.innerHTML = m.pic; b.appendChild(pic);
      if(m.photo){ const im = document.createElement('img'); im.alt = ''; im.loading = 'lazy'; im.src = m.photo; im.onload = () => im.classList.add('on'); im.onerror = () => im.remove(); pic.appendChild(im); }
      const ev = document.createElement('span'); ev.className = 'mtElev'; ev.textContent = m.elev.toLocaleString() + 'm'; pic.appendChild(ev);
      if(m.id === CUR){ const t = document.createElement('span'); t.className = 'mtTag'; t.textContent = '지금 이 산'; pic.appendChild(t); }
      const body = document.createElement('div'); body.className = 'mtBody'; b.appendChild(body);
      const add = (tag, cls, txt) => { const e = document.createElement(tag); if(cls) e.className = cls; e.textContent = txt; body.appendChild(e); return e; };
      add('b', '', m.area);
      add('span', 'mtSub', m.end);
      const c = add('span', 'mtSub', ''); const cc = document.createElement('span'); cc.textContent = m.r === 'kr' ? m.course : m.country; c.appendChild(cc); if(m.km) c.appendChild(document.createTextNode(' · ' + m.km + ' km'));
      if(!m.built){ b.disabled = true; add('span', 'mtSub', '준비 중'); }
      b.onclick = () => { if(m.id === CUR){ close(); return; } if(m.built){ try{ sessionStorage.setItem('neungseon.go', m.id); }catch(e){} location.href = m.page + '?go=1'; } };
      list.appendChild(b);
    });
  }
  function open(withSave){
    let w = null; if(withSave && window.__saveHike){ try{ w = window.__saveHike(); }catch(e){} }
    saved.hidden = w == null; if(w != null) saved.textContent = '지금까지 걸은 기록을 저장했어요' + (w > 0 ? ' · ' + (w/1000).toFixed(2) + 'km' : '');
    tab = here.r; draw(); box.hidden = false;
  }
  function close(){ box.hidden = true; }
  document.querySelectorAll('.mtTabs button').forEach(b => b.onclick = () => { tab = b.dataset.r; draw(); });
  document.getElementById('mtX').onclick = close;
  box.addEventListener('click', e => { if(e.target === box) close(); });
  document.addEventListener('keydown', e => { if(e.key === 'Escape' && !box.hidden) close(); });
  const ob = document.getElementById('mtOpen'); if(ob) ob.onclick = () => open(false);
  document.querySelectorAll('#brand .mtName').forEach(n => { const go = e => { e.stopPropagation(); e.preventDefault(); open(true); };
    n.addEventListener('click', go); n.addEventListener('keydown', e => { if(e.key === 'Enter' || e.key === ' ') go(e); }); });
  window.MT_SELECT = { open, close };
  let skip = /[?&]go=1/.test(location.search);
  try{ if(sessionStorage.getItem('neungseon.go') === CUR){ skip = true; sessionStorage.removeItem('neungseon.go'); } }catch(e){}
  if(!skip) open(false);
})();
</script>
''' % (json.dumps(cur), json.dumps(lst, ensure_ascii=False), json.dumps(key))


def inline_assets(t):
    A = os.path.join(PF, 'assets')
    for const, f, mime in (("const MOON_URL = 'moon.png';", 'moon.png', 'png'), ("const STARS_URL = 'stars.jpg';", 'stars.jpg', 'jpeg'),
                           ("const FARTEX_URL = 'fartile.jpg';", 'fartile.jpg', 'jpeg')):
        if const in t:
            v = const.split("'")[1]
            t = t.replace(const, const.replace(v, f'data:image/{mime};base64,' + base64.b64encode(open(os.path.join(A, f), 'rb').read()).decode()))
    return t


def build_page(T, m, mts, data):
    P = Patch(T, m['id'])
    meta = data['meta']
    # 공통: 번역 표에 모든 산 이름 + 선택 화면 문구, 이 산 문장
    rows = list(UI_ROWS)
    for x in mts: rows += mountain_rows(x)
    if m['id'] != 'bukhansan': rows += page_rows(m)
    rows += EXTRA_ROWS + SEASON_ROWS + SKY_ROWS + WX_ROWS + lm_rows(m) + FIX_ROWS + loader_rows(m) + [[tagline(m, l) for l in LANGS]]
    pre, R, post = split_R(P.t)
    R += ',\n    // 산 고르기·산 이름 (pipeline/build_site.py)\n' + ',\n'.join('    ' + json.dumps(r, ensure_ascii=False) for r in rows)
    if not m.get('legacy'):
        pre, post = patch_mountain(Patch(pre, m['id'] + ':head'), Patch(post, m['id']), m, meta)
    P.t = pre + R + post
    patch_hike(P, m)
    patch_common(P, m, data)
    patch_photos(P, m)
    patch_sky(P, m)
    patch_avatar(P)
    patch_weather(P, m)
    patch_sound(P, m)
    patch_camera(P, m)
    patch_look(P, m)
    patch_landmark(P, m)
    patch_release(P, m)
    patch_admin(P, m)
    patch_ios(P, m)
    patch_install(P, m)
    patch_ui(P, m)
    patch_moon(P, m)
    patch_far(P, m)
    patch_flora(P, m)
    patch_vista(P, m, meta)
    patch_trail(P, m)
    patch_loader(P, m, mts, data)
    patch_i18n_fix(P, m)
    patch_lang(P, m)
    # 선택 화면
    P.rep('</style>', SEL_CSS + '</style>', 1)
    P.rep('<button class="btn" id="go">', '<button class="btn sec" id="mtOpen" type="button">다른 산 고르기</button>\n    <button class="btn" id="go">', 1)
    P.rep('<div id="flash"></div>', selector_html() + '<div id="flash"></div>', 1)
    P.rep('</body>', selector_js(m['id'], mts) + '</body>', 1)
    # 데이터
    P.rep('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'), 1)
    return P.t


def patch_hike(P, m):
    """산행 저장을 산마다 따로: 기기 저장 칸은 hike.<id>, 로그인 동기화 값에는 산 id(m)를 붙여 다른 산 기록을 불러오지 않게."""
    i = m['id']; key = 'hike' if m.get('legacy') else 'hike.' + i
    P.rep("store.get('hike', null)", f"store.get('{key}', null)")
    P.rep("store.set('hike', o)", f"store.set('{key}', o)", 1)
    P.rep("const o = { v:1, ts:Date.now() };", f"const o = {{ v:1, ts:Date.now(), m:'{i}' }};", 1)
    P.rep("localStorage.removeItem('neungseon.hike')", f"localStorage.removeItem('neungseon.{key}')", 1)
    ok = "(!c.hike.m || c.hike.m === 'bukhansan')" if m.get('legacy') else f"c.hike.m === '{i}'"
    if P.t.count("store.set('hike', c.hike)"):
        P.rep("if(c.hike && c.hike.v === 1 &&", f"if(c.hike && c.hike.v === 1 && {ok} &&", 1)
        P.rep("store.set('hike', c.hike)", f"store.set('{key}', c.hike)", 1)


def patch_mountain(H, B, m, meta):
    """북한산에 묶인 글자·숫자를 이 산 값으로. H=번역표 앞(head·HTML), B=번역표 뒤(HTML·게임 코드)."""
    ko = lambda d: L(d, 'ko')
    e, end, peak, area = m['elev'], ko(m['end']), ko(m['peak']), ko(m['area'])
    ap = area_peak(m, 'ko'); th = ko(m['trailheadArea'])
    W = m['waypoints']; mids = W[1:-1]
    page = m['page']
    # head 메타
    H.rep('북한산 백운대 836m', f'{ap} {e}m')
    H.rep('북한산 백운대', ap)
    H.sub(r'(og:url" content="https://hgm8148-cloud\.github\.io/neungseon\.Mt/)', r'\g<1>' + page)
    for X in (B,):
        route = f'<b>{ko(W[0])}</b> → ' + (' → '.join(ko(w) for w in mids) + ' → ' if mids else '') + f'<b>{end} {e}m</b>'
        X.rep('<b>백운대탐방지원센터</b> → 하루재 → 백운산장 → 위문 → <b>백운대 정상 836m</b>', route, 1)
        X.rep('가을, 북한산 백운대에 함께 오르다', tagline(m, 'ko'))
        X.rep('<div class="kicker">북한산 · 백운대 836m</div>', f'<div class="kicker">{area} · {peak} {e}m</div>', 1)
        X.rep('<span>북한산 백운대</span>', f'<span>{ap}</span>', 1)
        X.rep("T_('북한산 백운대')", f"T_('{js(ap)}')", 1)
        X.rep('백운대 정상<small>해발 836m · 북한산 최고봉</small>', f'{end}<small>해발 {e}m · {ko(m["summitSub"])}</small>')
        X.rep("'백운대 정상 360°'", f"'{js(end)} 360°'", 1)
        X.rep("'운해 위로 서울과 겹겹의 산줄기가 펼쳐져요'", f"'{js(ko(m['vista']))}'", 1)
        X.rep("banner('백운대 정상',", f"banner('{js(end)}',", 1)
        X.rep("'백운대에서 맞는 해돋이'", f"'{js(peak)}에서 맞는 해돋이'", 1)
        X.rep('우이동 들머리', f'{th} 들머리')
        X.rep("'하루재까지 ' + (WPS[1].s/1000)", "WPS[1].name.replace(/\\(.*\\)/,'') + '까지 ' + (WPS[1].s/1000)", 1)
        s = max(34, min(72, int(236 / max(1, len(peak)))))
        X.rep("{t:'백운대',s:72,b:1},{t:'836m',s:54}", f"{{t:'{js(peak)}',s:{s},b:1}},{{t:'{e}m',s:54}}", 1)
        # 지점 설명
        X.sub(r"const WP_DESC = \{[^}]*\};", 'const WP_DESC = {\n' + ',\n'.join(f"  '{js(k)}':'{js(v[0])}'" for k, v in wp_desc(m).items()) + '\n};', flags=re.S)
        # 높이 기준·표시
        X.sub(r'const H0 = [\d.]+, VEX = [\d.]+;', f"const H0 = {meta['H0']}, VEX = {meta['VEX']}, ALT0 = {meta['BASE']};")
        if meta['BASE']:
            X.sub(r'Math\.round\(heightAt\(st\.x, ?st\.z\)\)', 'Math.round(heightAt(st.x,st.z)+ALT0)')
            X.rep("$('alt').textContent = Math.round(y) + ' m';", "$('alt').textContent = Math.round(y + ALT0) + ' m';", 1)
        start = int(round(meta['H0'] + meta['BASE']))
        X.sub(r"Math\.round\(110 \+ f\*726\)", f"Math.round({start} + f*{e - start})", need=False)
        # 태양: 위도·남중 시각
        noon = 12 + (m['tz'] * 15 - meta['lon']) / 15
        X.rep('const lat = 37.66*Math.PI/180,', f"const lat = {meta['lat']}*Math.PI/180,", 1)
        X.rep('const H = (hour - 12.5)*15*Math.PI/180;', f'const H = (hour - {noon:.2f})*15*Math.PI/180;', 1)
        # 함께 걷기 방·저장 칸은 산마다 따로
        X.rep("const ROOM_ID = 'bukhansan';", f"const ROOM_ID = '{m['id']}';", 1)
        # 도시 불빛
        if not m.get('cityLights', True):
            X.rep('sz.length < 9000', 'sz.length < 0', 1)
        # 정상 깃발
        if m['flag'] != 'kr':
            X.sub(r"  x\.fillStyle = '#fff'; x\.fillRect\(0,0,384,256\);.*?bars\(Math\.PI - a0, \[0,1,0\]\);\n",
                  lambda _: FLAG_JS.replace('__FLAG__', json.dumps(FLAGS[m['flag']])), flags=re.S)
            X.rep('// 정상 태극기', '// 정상 깃발', need=False)
        X.rep('836m', f'{e}m', need=False)
    # 남은 북한산 고유 글자 점검 (주석 제외)
    left = []
    for ln in B.t.split('\n'):
        code = ln.split('//')[0] if not ln.lstrip().startswith('<') else ln
        for tok in ('북한산', '백운대', '하루재', '백운산장', '위문', '우이동', r'\b836\b'):
            if re.search(tok, code): left.append((tok, ln.strip()[:100]))
    for tok, ln in left: print(f"   ! [{m['id']}] 남은 '{tok}': {ln}")
    return H.t, B.t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--template', default=os.path.join(PF, 'game.template.html'))
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--to-site', action='store_true')
    ap.add_argument('--preview', action='store_true', help='모든 페이지를 <id>.html 이름으로 (미리보기 아티팩트용)')
    a = ap.parse_args()
    T = inline_assets(open(a.template).read())
    mts = []
    for f in sorted(os.listdir(os.path.join(HERE, 'mountains'))):
        m = json.load(open(os.path.join(HERE, 'mountains', f)))
        m.setdefault('page', m['id'] + '.html')
        if a.preview: m['page'] = m['id'] + '.html'
        dp = os.path.join(HERE, 'data', m['id'] + '.json')
        m['_built'] = os.path.exists(dp)
        if m['_built']:
            dd = json.load(open(dp)); m['_km'] = round(dd['meta']['trail_m'] / 1000, 1); m['_thumb'] = thumb_svg(m, dd)
        mts.append(m)
    mts.sort(key=lambda m: m['order'])
    out = os.path.dirname(HERE) if a.to_site else os.path.join(HERE, 'preview' if a.preview else 'out')
    os.makedirs(out, exist_ok=True)
    for m in mts:
        if not m['_built'] or (a.only and m['id'] not in a.only): continue
        data = json.load(open(os.path.join(HERE, 'data', m['id'] + '.json')))
        html = build_page(T, m, mts, data)
        p = os.path.join(out, m['page'])
        open(p, 'w').write(html)
        print(f"{m['id']:>15} → {os.path.relpath(p, os.path.dirname(HERE))} ({len(html)/1024:.0f} KB)")
    copy_photos(out, [m['id'] for m in mts] + ['sky'])


if __name__ == '__main__':
    main()
