"""플레이 스토어 안드로이드 앱(TWA)으로 열렸을 때만 후원 버튼·앱 설치 안내를 숨긴다 (빌드 후 처리, 여러 번 돌려도 결과가 같다).

사용: python3 pipeline/android_patch.py <사이트 루트>   (기본: 저장소 루트)
build_site.py --to-site 마지막에 android_patch.patch_dir(root) 를 부른다.

왜 (승연 님, 2026-11-10 '능선 안드로이드 앱 출시하기'):
- 플레이 스토어 앱은 neungseon.com 을 그대로 여는 TWA 방식이다. 사이트를 고치면 앱도 바로 바뀐다.
- 플레이 결제 정책은 앱 안에서 바깥 결제(토스·카카오페이·Buy Me a Coffee)로 안내하는 걸 엄격하게 본다.
  심사에서 걸리지 않도록 앱 안에서만 후원 버튼과 후원 창을 숨긴다. 웹사이트에서는 그대로 보인다.
- 이미 앱으로 깔았으니 '앱으로 설치' 안내도 앱 안에서는 숨긴다.

앱인지 알아보는 법 (하나라도 맞으면 앱):
- 앱 시작 주소에 ?src=twa 를 붙인다 (PWABuilder의 Start URL 또는 twa-manifest.json의 startUrl)
- 앱이 처음 열 때 document.referrer 가 android-app://com.neungseon.app 로 시작한다
한 번 앱으로 알아보면 그 탭(sessionStorage)이 닫힐 때까지 기억한다. 산을 옮겨 다녀도 이어진다.
"""
import os
import sys

MARK = 'id="inAppCss"'
PKG = 'com.neungseon.app'

SNIPPET = r"""<style id="inAppCss">
html.inapp #supportBtn,html.inapp #endSupport,html.inapp #supportPanel,html.inapp #appInst{display:none!important}
</style>
<script>
(function(){
  var app = false;
  try { app = /(?:^|[?&])src=twa(?:&|$)/.test(location.search.slice(1)) || document.referrer.indexOf('android-app://__PKG__') === 0 || sessionStorage.getItem('neungseon.twa') === '1'; } catch (e) {}
  if (!app) return;
  try { sessionStorage.setItem('neungseon.twa', '1'); } catch (e) {}
  document.documentElement.classList.add('inapp');
})();
</script>
""".replace('__PKG__', PKG)


def patch(s):
    if MARK in s or '</head>' not in s:
        return s
    i = s.index('</head>')
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
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print('\n'.join(patch_dir(root)))
