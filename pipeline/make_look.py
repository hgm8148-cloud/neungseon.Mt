"""산 사진에서 그 산의 바위 색을 뽑아요 → photos/look.json

    python3 make_look.py

사진(photos/web/<산>/)에서 채도가 낮고 밝기가 중간~밝은 픽셀(바위·암벽)의 가운데 값을 바위 색으로 써요.
하늘이 많은 위쪽 1/4은 빼고 봐요. 게임에선 바위·노두·물가 바위와 먼 산 바위 색을 이 색 쪽으로 바꿔요 (look_patch.py).
"""
import json, os, glob
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, 'photos', 'web')


def rock_color(paths):
    px = []
    for p in paths:
        im = np.asarray(Image.open(p).convert('RGB').resize((160, 110))).astype(float) / 255
        im = im[im.shape[0] // 4:]                       # 하늘이 많은 위쪽은 빼요
        a = im.reshape(-1, 3); mx, mn = a.max(1), a.min(1); lum = a @ [0.3, 0.59, 0.11]
        sat = (mx - mn) / np.maximum(mx, 1e-3)
        sel = a[(sat < 0.22) & (lum > 0.3) & (lum < 0.88) & (a[:, 2] < a[:, 0] + 0.08)]   # 회색·베이지 (파란 하늘·눈 그늘 빼고)
        if len(sel): px.append(sel)
    if not px: return None
    a = np.concatenate(px)
    if len(a) < 400: return None
    return [round(float(v), 3) for v in np.median(a, 0)]


def main():
    out = {}
    for d in sorted(glob.glob(os.path.join(WEB, '*'))):
        mid = os.path.basename(d)
        if mid == 'sky': continue
        c = rock_color(sorted(glob.glob(os.path.join(d, '*.jpg'))))
        if c: out[mid] = dict(rock=c)
        print(mid, c)
    json.dump(out, open(os.path.join(HERE, 'photos', 'look.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
