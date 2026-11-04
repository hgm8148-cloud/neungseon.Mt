"""산별 공유 미리보기 그림(1200x630) 만들기.

사용: python3 pipeline/make_og.py --font <GowunBatang-Bold.ttf> [--root .]
- 사진: <root>/photos/<산id>/load.jpg (없으면 hero.jpg)  — 저장소에 이미 있는 무료 라이선스 사진
- 결과: <root>/og/<산id>.jpg
- 글자: 능선 온라인 / 산 이름 / 한 줄 소개 (산 개수, 정상 이벤트는 쓰지 않는다)
글꼴 GowunBatang-Bold.ttf 는 구글 폰트(OFL)이며 저장소에 넣지 않는다:
https://raw.githubusercontent.com/google/fonts/main/ofl/gowunbatang/GowunBatang-Bold.ttf
"""
import argparse
import os
import re

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
CREAM = (244, 239, 230)
GOLD = (227, 176, 79)


def place_of(html_path):
    s = open(html_path, encoding='utf-8').read()
    m = re.search(r'<h1>능선 온라인 · (.+?) 온라인 등산</h1>', s)
    if not m:
        m = re.search(r'<meta property="og:title" content="[^"]*·\s*([^"]+)">', s)
    return m.group(1).strip() if m else ''


def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, int((im.height - h) * 0.45)
    return im.crop((x, y, x + w, y + h))


def make(root, mid, font_path):
    photo = None
    for n in ('load.jpg', 'hero.jpg'):
        p = os.path.join(root, 'photos', mid, n)
        if os.path.exists(p):
            photo = p
            break
    if not photo:
        return None
    page = os.path.join(root, 'index.html' if mid == 'bukhansan' else mid + '.html')
    place = place_of(page)
    im = cover(Image.open(photo).convert('RGB'), W, H)

    # 아래쪽을 어둡게 눌러 글자가 읽히게
    grad = Image.new('L', (1, H))
    for y in range(H):
        t = max(0.0, (y - H * 0.30) / (H * 0.70))
        grad.putpixel((0, y), int(215 * t ** 1.4))
    shade = Image.new('RGB', (W, H), (14, 16, 24))
    im = Image.composite(shade, im, grad.resize((W, H)))

    d = ImageDraw.Draw(im)
    f_brand = ImageFont.truetype(font_path, 40)
    f_big = ImageFont.truetype(font_path, 92 if len(place) <= 9 else 74)
    f_sub = ImageFont.truetype(font_path, 34)
    x = 72
    d.text((x, 372), '능선 온라인', font=f_brand, fill=GOLD)
    d.text((x, 428), place, font=f_big, fill=CREAM)
    d.text((x, 548), '브라우저에서 천천히 오르는 온라인 등산', font=f_sub, fill=(244, 239, 230, 220))

    out_dir = os.path.join(root, 'og')
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, mid + '.jpg')
    im.save(out, quality=84, optimize=True, progressive=True)
    return out, place


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--font', required=True)
    ap.add_argument('--root', default=os.path.join(os.path.dirname(__file__), '..'))
    a = ap.parse_args()
    ids = sorted(d for d in os.listdir(os.path.join(a.root, 'photos'))
                 if os.path.isdir(os.path.join(a.root, 'photos', d)) and d != 'sky')
    for mid in ids:
        r = make(a.root, mid, a.font)
        print(mid, r)
