"""다른 사이트 안(iframe)에서 열렸을 때만 'neungseon.com에서 크게 열기' 버튼 (빌드 후 처리, 여러 번 돌려도 결과가 같다).

사용: python3 pipeline/embed_patch.py <사이트 루트>   (기본: 저장소 루트)
build_site.py --to-site 마지막에 embed_patch.patch_dir(root) 를 부른다.

왜 (승연 님, 2026-11-06): 저잣거리(https://jeojat.altolab.ai) 같은 곳에 iframe으로 올라가면
- 브라우저가 저장 공간을 따로 나눠 '이어서 오르기' 기록이 원래 사이트와 이어지지 않고
- 구글 로그인 창·후원 링크가 막힐 수 있고
- 사람들이 neungseon.com 주소를 모르고 지나갈 수 있다.
그래서 iframe 안일 때만 원래 사이트를 새 탭으로 여는 버튼을 위쪽 가운데에 띄운다.
처음엔 글자와 함께 보였다가 12초 뒤 작은 ↗ 아이콘으로 줄어든다(마우스를 올리면 다시 펼쳐짐).
어느 사이트가 iframe으로 넣을 수 있는지는 Cloudflare 응답 머리글(CSP frame-ancestors)이 정한다.
"""
import os
import sys

MARK = 'id="embedOpen"'

SNIPPET = r"""<style id="embedOpenCss">
#embedOpen{position:fixed;z-index:60;top:calc(12px + env(safe-area-inset-top,0px));left:50%;transform:translateX(-50%);
display:flex;align-items:center;gap:6px;padding:8px 14px;border-radius:999px;font:600 13px/1 system-ui,-apple-system,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;
color:#fff;text-decoration:none;background:rgba(20,32,28,.62);border:1px solid rgba(255,255,255,.28);
-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);box-shadow:0 4px 16px rgba(0,0,0,.25);white-space:nowrap;transition:padding .25s,opacity .25s}
#embedOpen[hidden]{display:none}
#embedOpen:hover{background:rgba(20,32,28,.8)}
#embedOpen .eoI{font-size:14px}
#embedOpen.mini{padding:8px 10px}
#embedOpen.mini .eoT{display:none}
#embedOpen.mini:hover{padding:8px 14px}
#embedOpen.mini:hover .eoT{display:inline}
body.touch #embedOpen{top:calc(8px + env(safe-area-inset-top,0px));font-size:12px;padding:7px 12px}
</style>
<a id="embedOpen" hidden target="_blank" rel="noopener" href="https://neungseon.com/"><span class="eoT"></span><span class="eoI">↗</span></a>
<script>
(function(){
  var inFrame; try { inFrame = window.self !== window.top; } catch (e) { inFrame = true; }
  if (!inFrame) return;
  var a = document.getElementById('embedOpen'); if (!a) return;
  var l = ''; try { l = localStorage.getItem('neungseon.lang') || ''; } catch (e) {}
  l = (l || navigator.language || 'ko').slice(0, 2).toLowerCase();
  var T = { ko: 'neungseon.com에서 크게 열기', ja: 'neungseon.comで大きく開く', zh: '在 neungseon.com 全屏打开' };
  var t = T[l] || 'Open full size on neungseon.com';
  a.querySelector('.eoT').textContent = t;
  a.title = t; a.setAttribute('aria-label', t); a.setAttribute('translate', 'no');
  a.href = 'https://neungseon.com' + location.pathname + location.search;
  a.hidden = false;
  setTimeout(function(){ a.classList.add('mini'); }, 12000);
})();
</script>
"""


def patch(s):
    if MARK in s or '</body>' not in s:
        return s
    i = s.rfind('</body>')
    return s[:i] + SNIPPET + s[i:]


def patch_dir(root):
    done = []
    for f in sorted(os.listdir(root)):
        if not f.endswith('.html'):
            continue
        p = os.path.join(root, f)
        s = open(p, encoding='utf-8').read()
        if '<meta property="og:url"' not in s:  # 게임 페이지만
            continue
        n = patch(s)
        if n != s:
            open(p, 'w', encoding='utf-8').write(n)
        done.append(f)
    return done


if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..')
    print('\n'.join(patch_dir(root)))
