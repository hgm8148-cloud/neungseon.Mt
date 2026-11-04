"""검색 노출용 head 정리 (빌드 후 처리, 여러 번 돌려도 결과가 같다).

사용: python3 pipeline/seo_patch.py <사이트 루트>   (기본: 저장소 루트)
build_site.py 마지막에 seo_patch.patch_dir(root) 를 불러도 된다(sitemap.xml 도 함께 다시 쓴다).

원칙(승연 님 결정, 2026-11-04)
- 산 개수를 쓰지 않는다 ('20개 산' 금지): 산은 계속 추가된다.
- '실제 지형 그대로' 같은 과장 금지: '실제 산을 본떠 만든'으로 쓴다.
- 정상 이벤트·숨은 탐방로는 언급하지 않는다(스포일러 금지).
"""
import html as H
import json
import os
import re
import sys

SITE = 'https://neungseon.com/'
ROOT = '.'  # patch_dir 가 사이트 루트로 바꿔 준다
NAME = '능선 온라인'
KEYWORDS = ('능선 온라인, 능선, 능선 게임, 온라인 등산, 온라인 산행, 온라인 트레킹, 온라인 하이킹, '
            '등산 게임, 산행 게임, 트레킹 게임, 하이킹 게임, 힐링 게임, 브라우저 게임, '
            'online hiking game, Neungseon Online, Neungseon')
MARK = 'data-seo="neungseon"'
# Cloudflare Web Analytics (쿠키 없는 방문 집계). 토큰은 공개 값이다.
CF_TOKEN = '53fa976ecea94716b700fb9d477c7025'


def place_of(s):
    """장소 이름: 이전 실행의 noscript 제목 > og:title 의 '· 장소' > 설명문 '만든 장소 산길'."""
    m = re.search(r'<h1>능선 온라인 · (.+?) 온라인 등산</h1>', s)
    if m:
        return H.unescape(m.group(1)).strip()
    m = re.search(r'<meta property="og:title" content="[^"]*·\s*([^"]+)">', s)
    if m:
        return H.unescape(m.group(1)).strip()
    m = re.search(r'만든 (.+?) 산길', s)
    return m.group(1).strip() if m else ''


def patch(s, page):
    place = place_of(s)
    url = SITE + ('' if page == 'index.html' else page)
    if page == 'index.html':
        title = f'{NAME} | 온라인 등산·산행·트레킹 게임'
    else:
        title = f'{place} 온라인 등산 | {NAME}'
    desc = (f'{place} 코스를 본떠 만든 산길을 브라우저에서 천천히 걷는 온라인 등산·산행 게임, 능선 온라인. '
            '설치 없이 무료로 즐기는 힐링 트레킹·하이킹 게임. 한국어·English·日本語·中文')
    e = lambda t: H.escape(t, quote=True)

    s = re.sub(r'<title>[^<]*</title>', f'<title>{e(title)}</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">', s, count=1)

    # 공유 미리보기: 제목은 '능선 온라인', 산 페이지는 산별 그림(og/<id>.jpg, pipeline/make_og.py)
    og_title = f'{NAME} | 온라인 등산·산행·트레킹 게임' if page == 'index.html' else f'{NAME} · {place}'
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{e(og_title)}">', s, count=1)
    mid = page[:-5]
    if page != 'index.html' and os.path.exists(os.path.join(ROOT, 'og', mid + '.jpg')):
        s = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{SITE}og/{mid}.jpg">', s, count=1)
        og_size = True
    else:
        og_size = page == 'index.html'  # og.png 1280x720

    # 이전 실행 결과 제거 후 다시 넣기 (idempotent)
    s = re.sub(r'<meta name="keywords"[^>]*' + MARK + r'[^>]*>\n?', '', s)
    s = re.sub(r'<meta property="og:image:(?:width|height)"[^>]*' + MARK + r'[^>]*>\n?', '', s)
    s = re.sub(r'<link rel="canonical"[^>]*' + MARK + r'[^>]*>\n?', '', s)
    s = re.sub(r'<meta property="og:site_name"[^>]*' + MARK + r'[^>]*>\n?', '', s)
    s = re.sub(r'<meta name="application-name"[^>]*' + MARK + r'[^>]*>\n?', '', s)
    s = re.sub(r'<script type="application/ld\+json" ' + MARK + r'>.*?</script>\n?', '', s, flags=re.S)
    s = re.sub(r'<script defer src="https://static\.cloudflareinsights\.com/[^>]*' + MARK + r'[^>]*></script>\n?', '', s)
    s = re.sub(r'<noscript ' + MARK + r'>.*?</noscript>\n?', '', s, flags=re.S)

    ld = {
        '@context': 'https://schema.org',
        '@type': 'VideoGame',
        'name': NAME,
        'alternateName': ['능선', '능선 게임', 'Neungseon Online', 'Neungseon'],
        'url': url,
        'description': desc,
        'genre': ['온라인 등산 게임', '힐링 게임', 'Hiking', 'Walking simulator'],
        'gamePlatform': ['Web browser', 'PC', 'Mobile'],
        'applicationCategory': 'Game',
        'operatingSystem': 'Any (web browser)',
        'inLanguage': ['ko', 'en', 'ja', 'zh'],
        'isAccessibleForFree': True,
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'KRW'},
        'image': SITE + 'og.png',
    }
    site = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': NAME,
            'alternateName': ['능선', 'Neungseon Online'], 'url': SITE}
    head_add = (f'<meta name="keywords" content="{e(KEYWORDS)}" {MARK}>\n'
                f'<link rel="canonical" href="{url}" {MARK}>\n'
                f'<meta property="og:site_name" content="{NAME}" {MARK}>\n'
                + (f'<meta property="og:image:width" content="{1280 if page == "index.html" else 1200}" {MARK}>\n'
                   f'<meta property="og:image:height" content="{720 if page == "index.html" else 630}" {MARK}>\n' if og_size else '') +
                f'<meta name="application-name" content="{NAME}" {MARK}>\n'
                f'<script type="application/ld+json" {MARK}>{json.dumps(ld, ensure_ascii=False)}</script>\n')
    head_add += (f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
                 f'data-cf-beacon=\'{{"token": "{CF_TOKEN}"}}\' {MARK}></script>\n')
    if page == 'index.html':
        head_add += f'<script type="application/ld+json" {MARK}>{json.dumps(site, ensure_ascii=False)}</script>\n'
    s = s.replace('</head>', head_add + '</head>', 1)

    intro = (f'<noscript {MARK}><section style="padding:24px;color:#f4efe6;background:#1d2238;font-family:sans-serif">'
             f'<h1>{NAME} · {e(place)} 온라인 등산</h1>'
             f'<p>{NAME}은 브라우저에서 바로 즐기는 온라인 등산·산행 게임입니다. '
             f'실제 산을 본떠 만든 {e(place)} 코스를 천천히 걸으며 계절과 날씨, 숲의 소리를 느낄 수 있어요. '
             '설치 없이 무료로 PC와 휴대폰에서 즐길 수 있고, 산은 계속 추가됩니다.</p>'
             '<p>게임을 하려면 자바스크립트를 켜 주세요. '
             f'<a href="{SITE}" style="color:#e3b04f">{NAME} 첫 화면으로</a></p></section></noscript>\n')
    s = re.sub(r'(<body[^>]*>\n?)', lambda m: m.group(1) + intro, s, count=1)
    return s


def write_sitemap(root, pages):
    """게임 페이지 목록으로 sitemap.xml 을 다시 쓴다. 이미 있던 페이지의 lastmod 는 그대로 두고
    새 페이지만 오늘 날짜를 넣는다(여러 번 돌려도 결과가 같다)."""
    import datetime
    path = os.path.join(root, 'sitemap.xml')
    old = {}
    if os.path.exists(path):
        for loc, mod in re.findall(r'<loc>([^<]+)</loc>(?:<lastmod>([^<]*)</lastmod>)?',
                                   open(path, encoding='utf-8').read()):
            old[loc] = mod
    today = datetime.date.today().isoformat()
    ordered = sorted(pages, key=lambda f: (f != 'index.html', f))
    rows = []
    for f in ordered:
        loc = SITE + ('' if f == 'index.html' else f)
        rows.append(f'  <url><loc>{loc}</loc><lastmod>{old.get(loc) or today}</lastmod></url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + '\n'.join(rows) + '\n</urlset>\n')
    if not os.path.exists(path) or open(path, encoding='utf-8').read() != xml:
        open(path, 'w', encoding='utf-8').write(xml)


def patch_dir(root):
    global ROOT
    ROOT = root
    done = []
    for f in sorted(os.listdir(root)):
        if not f.endswith('.html'):
            continue
        p = os.path.join(root, f)
        s = open(p, encoding='utf-8').read()
        if '<meta property="og:url"' not in s:  # 게임 페이지만
            continue
        n = patch(s, f)
        if n != s:
            open(p, 'w', encoding='utf-8').write(n)
        done.append(f)
    write_sitemap(root, done)
    return done


if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..')
    print('\n'.join(patch_dir(root)))
