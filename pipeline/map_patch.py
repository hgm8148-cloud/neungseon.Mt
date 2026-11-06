"""지도 크게 보기·닫기 (2026-11-06 승연 '모바일에서 지도 확대시 지도 크기를 더 키워줘. 활성화된 지도를 닫을 수 있게 해줘')

- 휴대폰: 지도를 눌러 크게 보면 화면 가운데에 거의 화면 가득 (세로 94vw, 가로 82vh)
- 휴대폰 작은 지도는 오른쪽 빠른 버튼들에 가리지 않게 그 왼쪽으로
- ✕ 버튼: 휴대폰은 지도를 아예 닫고, PC는 크게 본 지도를 원래 크기로
- PC는 Esc 로도 크게 본 지도를 닫아요

빌드 후 처리, 여러 번 돌려도 결과가 같다.
사용: python3 pipeline/map_patch.py <사이트 루트>   (기본: 저장소 루트)
build_site.py --to-site 마지막에 map_patch.patch_dir(root) 를 부른다.
"""

MAP_CSS = r'''<style id="mapXCss">
/* 지도 크게 보기·닫기 (pipeline/map_patch.py) */
#mapX{display:none;position:absolute;top:-8px;right:-8px;width:30px;height:30px;border-radius:50%;border:1px solid rgba(255,255,255,.35);background:rgba(18,20,17,.78);color:#fff;font:600 15px/1 sans-serif;padding:0;place-items:center;z-index:2;pointer-events:auto;cursor:pointer;-webkit-tap-highlight-color:transparent}
#mapWrap.big #mapX,body.touch.mapOn #mapX{display:grid}
body.touch #mapWrap:not(.big){right:calc(58px + env(safe-area-inset-right,0px))}
body.touch #mapWrap:not(.big) #mapX{right:auto;left:-8px;width:28px;height:28px;font-size:13px}
body.touch #mapWrap.big{display:block;top:50%;left:50%;right:auto;bottom:auto;transform:translate(-50%,-50%);z-index:8;padding:6px;border-radius:18px}
body.touch #mapWrap.big #map{width:min(94vw,82vh,620px);height:min(94vw,82vh,620px)}
body.touch #mapWrap.big #mapX{top:10px;right:10px;width:38px;height:38px;font-size:18px}
</style>'''

MAP_JS = r'''<script id="mapXJs">
/* 지도 닫기 버튼 (pipeline/map_patch.py) */
(function(){
  const W = document.getElementById('mapWrap'); if(!W) return;
  const X = document.createElement('button'); X.id = 'mapX'; X.type = 'button'; X.setAttribute('aria-label', '지도 닫기'); X.textContent = '✕';
  W.appendChild(X);
  const close = () => { W.classList.remove('big'); document.body.classList.remove('mapOn'); };
  X.addEventListener('click', e => { e.stopPropagation(); e.preventDefault(); close(); });
  X.addEventListener('pointerdown', e => e.stopPropagation());
  X.addEventListener('touchstart', e => e.stopPropagation(), {passive:true});
  addEventListener('keydown', e => { if(e.key === 'Escape' && W.classList.contains('big')) W.classList.remove('big'); });
})();
</script>'''


import os
import sys

MARK = 'id="mapXJs"'


def patch(s):
    if MARK in s or 'id="mapWrap"' not in s:
        return s
    i = s.rindex('</body>')
    return s[:i] + MAP_CSS + '\n' + MAP_JS + '\n' + s[i:]


def patch_dir(root):
    done = []
    for f in sorted(os.listdir(root)):
        if not f.endswith('.html'):
            continue
        p = os.path.join(root, f)
        s = open(p, encoding='utf-8').read()
        n = patch(s)
        if n != s:
            open(p, 'w', encoding='utf-8').write(n)
            done.append(f)
    return done


if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..')
    print('\n'.join(patch_dir(root)))
