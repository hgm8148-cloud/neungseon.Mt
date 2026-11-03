"""승연 님 드라이브 사진 → 게임에 쓰는 크기로 줄이고 출처를 기록해요.

    python3 make_photos.py            # photos/picks.json 대로 photos/web/<산id>/ 와 photos/credits.json 만들기

원본(raw)은 용량이 커서 저장소에 넣지 않고 /mnt/project-files/hiking-game/pipeline/photos/raw/<산id>/ 에 둬요.
무료 라이선스(Pixabay Content License, 공공누리 제1유형)로 확인된 사진만 골라 쓰고, 나머지(뉴스·스톡·블로그 사진)는 쓰지 않아요.
"""
import json, os, re, sys
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = '/mnt/project-files/hiking-game/pipeline/photos/raw'
CAT = '/mnt/project-files/hiking-game/pipeline/photos/drive_catalog.tsv'
WEB = os.path.join(HERE, 'photos', 'web')
PIX = re.compile(r'^([a-z0-9_]+)-([a-z0-9-]+)-(\d{5,9})_1920(?: \(\d\))?\.(?:jpg|png)$')
KOGL = {'국립공원공단': ('국립공원공단', 'https://www.knps.or.kr'), '광주광역시북구': ('광주광역시 북구', 'https://www.bukgu.gwangju.kr')}


def credit(title):
    m = PIX.match(title)
    if m:
        user, slug, pid = m.groups()
        return dict(author=user, source='Pixabay', license='Pixabay Content License', url=f'https://pixabay.com/photos/{slug}-{pid}/')
    if '제1유형' in title:
        for k, (who, url) in KOGL.items():
            if k in title: return dict(author=who, source='공공누리', license='공공누리 제1유형 (출처표시)', url=url)
    return None


def find(mid, ref):
    if isinstance(ref, dict) and 'file' in ref: return os.path.join(RAW, mid, ref['file']), ref['file']   # 채팅으로 받은 사진
    if isinstance(ref, dict): mid, ref = ref['from'], ref['id']
    for f in os.listdir(os.path.join(RAW, mid)):
        if f.startswith(ref): return os.path.join(RAW, mid, f), ref
    raise SystemExit(f'[photos] {mid}/{ref} 원본이 없어요')


def save(im, path, q):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.convert('RGB').save(path, 'JPEG', quality=q, optimize=True, progressive=True)


def main():
    picks = json.load(open(os.path.join(HERE, 'photos', 'picks.json')))
    titles = {}
    for l in open(CAT, encoding='utf-8'):
        p = l.rstrip('\n').split('\t')
        titles[p[3]] = p[2]
    credits = {}
    for mid, P in picks.items():
        if mid.startswith('_') or not P: continue
        out = os.path.join(WEB, mid); cr = []
        def put(role, ref, fn):
            src, fid = find(mid, ref)
            im = ImageOps.exif_transpose(Image.open(src))
            fn(im, os.path.join(out, role + '.jpg'))
            c = ref['credit'] if isinstance(ref, dict) and 'credit' in ref else credit(titles.get(fid, ''))
            if not c: raise SystemExit(f'[photos] {mid} {role}: 라이선스를 확인할 수 없는 사진이에요 ({titles.get(fid)})')
            cr.append(dict(role=role, file=f'photos/{mid}/{role}.jpg', drive=fid, title=titles.get(fid), **c))
        put('hero', P['hero'], lambda im, p: save(ImageOps.fit(im, (480, 300), Image.LANCZOS, centering=(0.5, 0.42)), p, 68))
        def load(im, p):
            w, h = im.size; s = min(1, 1600 / w); im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
            save(im, p, 70)
        put('load', P['load'], load)
        def post(im, p):
            im = im.copy(); im.thumbnail((1100, 820), Image.LANCZOS); save(im, p, 74)
        for k, ref in enumerate(P.get('posts', [])): put(f'p{k + 1}', ref, post)
        put('summit', P['summit'], post)
        credits[mid] = cr
        print(mid, len(cr), sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out)) // 1024, 'KB')
    json.dump(credits, open(os.path.join(HERE, 'photos', 'credits.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
