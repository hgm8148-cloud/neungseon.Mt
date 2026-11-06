"""승연 님 사진을 게임 화면에 넣기 (2026-11-03)
- 첫 로딩: 그 산 사진을 배경으로 천천히 다가가듯 보여 주고, 실제 능선 실루엣·탐방로 진행은 아래쪽에 겹쳐요
- 경유지에 닿으면 사진 엽서가 잠깐 떠올라요, 정상에 닿으면 끝 화면 맨 위에 정상 사진
- 사진마다 작가·출처를 작게 표시 (공공누리 제1유형은 출처 표시가 조건)
사진 파일은 페이지 옆 photos/<산id>/ 에 두고 주소로 불러요(페이지 용량을 늘리지 않게).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, 'photos', 'web')
_CR = None


def credits():
    global _CR
    if _CR is None:
        p = os.path.join(HERE, 'photos', 'credits.json')
        _CR = json.load(open(p)) if os.path.exists(p) else {}
    return _CR


def has_photos(mid):
    return mid in credits()


def hero_url(mid):
    return f'photos/{mid}/hero.jpg' if has_photos(mid) else ''


def label(c):
    return f"{c['author']} · {c['source']}" + (' (공공누리 제1유형)' if c['source'] == '공공누리' else '')


PHOTO_CSS = '''
#loading .ldPhoto{position:absolute;inset:-3%;width:106%;height:106%;object-fit:cover;opacity:0;transform:scale(1.04);transition:opacity 1.6s ease;animation:ldKen 38s ease-out forwards}
#loading .ldPhoto.on{opacity:1}
#loading.hasPhoto::before{content:'';position:absolute;inset:0;z-index:1;pointer-events:none;background:linear-gradient(180deg,rgba(14,18,32,.55) 0%,rgba(14,18,32,.12) 34%,rgba(14,18,32,.05) 55%,rgba(14,18,32,.72) 100%)}
#loading.hasPhoto .scene{z-index:2;transform:translateY(24vh);transition:transform 1.4s ease}
#loading.hasPhoto .scene > rect, #loading.hasPhoto .glow, #loading.hasPhoto .sun{opacity:0 !important}
#loading.hasPhoto #ldRidges path:not(:last-child){opacity:0 !important;animation:none}
#loading.hasPhoto #ldRidges path:last-child{fill:rgba(12,15,28,.42)}
#loading.hasPhoto .copy, #loading.hasPhoto .status{z-index:3}
#loading.hasPhoto .copy{text-shadow:0 2px 18px rgba(0,0,0,.45)}
#loading .ldCredit{position:absolute;right:12px;bottom:8px;z-index:3;font-size:10.5px;color:rgba(255,255,255,.62);letter-spacing:.02em}
@keyframes ldKen{from{transform:scale(1.04) translate(0,0)}to{transform:scale(1.13) translate(-1.5%,-1%)}}
#pcard{position:fixed;left:18px;bottom:96px;z-index:9;width:min(330px,62vw);padding:9px 9px 8px;border-radius:14px;background:#fffdf8;color:#2a2f3e;
  box-shadow:0 18px 40px rgba(10,14,30,.38);transform:translateY(24px) rotate(-2.2deg);opacity:0;pointer-events:none;transition:opacity .9s ease,transform 1.1s cubic-bezier(.2,.8,.2,1)}
#pcard.on{opacity:1;transform:translateY(0) rotate(-1.2deg);pointer-events:auto}
#pcard img{display:block;width:100%;max-height:44vh;object-fit:cover;border-radius:8px;background:#e9e4da}
#pcard .cap{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin:7px 3px 0}
#pcard .cap b{font-family:var(--display);font-size:15px;color:#2a2f3e}
#pcard .cap small{font-size:10.5px;color:#8a8f9c;text-align:right}
#pcard button{position:absolute;right:6px;top:6px;width:26px;height:26px;border-radius:50%;border:none;background:rgba(20,24,36,.55);color:#fff;font-size:13px;cursor:pointer}
body.touch #pcard{bottom:150px;left:10px;width:min(260px,58vw)}
#endPhoto{display:block;width:calc(100% + 0px);max-height:30vh;object-fit:cover;border-radius:14px;margin:0 0 12px}
#endPhotoCr{display:block;margin:-8px 0 10px;font-size:10.5px;color:#8a8f9c;text-align:right}
@media (prefers-reduced-motion:reduce){#loading .ldPhoto{animation:none}}
'''

PHOTO_JS = r'''
<script>
// ---------- 승연 님 사진: 경유지 엽서 · 정상 사진 (pipeline/photos_patch.py) ----------
(function(){
  const PC = __PC__;
  const box = document.getElementById('pcard'); if(!box || !PC.posts.length) return;
  const img = box.querySelector('img'), nm = box.querySelector('b'), cr = box.querySelector('small');
  let timer = 0; const shown = new Set();
  function show(p, name){ img.onload = () => { box.classList.add('on'); clearTimeout(timer); timer = setTimeout(() => box.classList.remove('on'), 9000); };
    nm.textContent = name || ''; cr.textContent = '사진 · ' + p.cr; img.src = p.src; }
  box.querySelector('button').onclick = () => { box.classList.remove('on'); clearTimeout(timer); };
  // 경유지 i(1..n-2)에 엽서를 고르게 나눠요. 같은 사진은 한 번만.
  window.__postcard = (i) => {
    try{
      if(i < 0){ return; }
      const n = Math.max(1, (typeof WPS !== 'undefined' ? WPS.length : 3) - 2), k = PC.posts.length;
      const j = Math.min(k - 1, Math.floor((i - 1) * k / n)); if(shown.has(j)) return; shown.add(j);
      const name = (typeof WPS !== 'undefined' && WPS[i]) ? WPS[i].name.replace(/\(.*\)/, '') : '';
      show(PC.posts[j], name);
    }catch(e){}
  };
})();
</script>
'''


def patch_photos(P, m):
    mid = m.get('base', m['id'])
    if not has_photos(mid): return
    C = {c['role']: c for c in credits()[mid]}
    pc = dict(posts=[dict(src=c['file'], cr=label(c)) for r, c in sorted(C.items()) if r.startswith('p')])
    P.rep('</style>', PHOTO_CSS + '</style>', 1)
    # 첫 로딩 배경
    ld = C['load']
    P.rep('<svg class="scene" viewBox="0 0 1600 900"',
          f'<img class="ldPhoto" alt="" src="{ld["file"]}" onload="this.classList.add(\'on\');document.getElementById(\'loading\').classList.add(\'hasPhoto\')" onerror="this.remove()">\n'
          f'  <span class="ldCredit">사진 · {label(ld)}</span>\n  <svg class="scene" viewBox="0 0 1600 900"', 1)
    # 경유지 엽서
    P.rep('<div id="flash"></div>', '<div id="pcard" aria-live="polite"><button type="button" aria-label="닫기">✕</button><img alt=""><div class="cap"><b></b><small></small></div></div>\n<div id="flash"></div>', 1)
    P.rep("if(i===WPS.length-1) finish(); else banner(", "if(i===WPS.length-1) finish(); else if((window.__postcard && window.__postcard(i)), true) banner(", 1)
    # 정상 사진
    s = C['summit']
    P.rep('<h1 id="endT">', f'<img id="endPhoto" alt="" loading="lazy" src="{s["file"]}" onerror="this.remove();document.getElementById(\'endPhotoCr\').remove()"><small id="endPhotoCr">사진 · {label(s)}</small>\n    <h1 id="endT">', 1)
    P.rep('</body>', PHOTO_JS.replace('__PC__', json.dumps(pc, ensure_ascii=False)) + '</body>', 1)


def copy_photos(out, mids):
    import shutil
    for mid in mids:
        src = os.path.join(WEB, mid)
        if not os.path.isdir(src): continue
        dst = os.path.join(out, 'photos', mid); os.makedirs(dst, exist_ok=True)
        for f in os.listdir(src): shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
