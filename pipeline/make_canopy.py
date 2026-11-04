"""산마다 먼 숲·초원 질감(canopy.jpg)을 원본 사진에서 잘라 만들어요.
- 사진 아래쪽 65%에서 하늘·너무 어두운 곳·큰 경계(능선선, 물가)를 피해, 질감이 고르고 자세한 칸을 골라요
- 이음매 없이 반복되도록 가장자리를 섞어 512px 타일로 저장 → photos/<id>/canopy.jpg
- 게임은 이 그림을 먼 지형(70m~)과 원경 산에 깔아요 (예전: 색 동그라미 무늬)
사용: python3 make_canopy.py [id ...]   (원본: /mnt/project-files/hiking-game/pipeline/photos/raw/<id>/)"""
import os, sys, json, glob
import numpy as np
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = '/mnt/project-files/hiking-game/pipeline/photos/raw'
OUT = os.path.join(HERE, 'photos', 'web')
PICKS = json.load(open(os.path.join(HERE, 'canopy_picks.json')))

def score_tile(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.3*r + 0.59*g + 0.11*b
    m = lum.mean()
    if m < 40 or m > 205: return -1
    sky = ((b > r + 12) & (b > g) & (lum > 140)).mean()
    if sky > 0.04: return -1
    white = (lum > 225).mean()
    # 큰 경계: 4x4 블록 평균의 차이가 크면 (능선선·물가) 감점
    h, w = lum.shape; bh, bw = h//4, w//4
    blocks = lum[:bh*4, :bw*4].reshape(4, bh, 4, bw).mean(axis=(1, 3))
    uneven = blocks.std()
    detail = np.abs(np.diff(lum, axis=1)).mean() + np.abs(np.diff(lum, axis=0)).mean()
    sat = (a.max(axis=2) - a.min(axis=2)).mean()
    return detail*1.0 + sat*0.25 - uneven*1.6 - white*80

def best_crop(paths):
    best = None
    for p in paths:
        try: im = Image.open(p).convert('RGB')
        except Exception: continue
        W, H = im.size; s = 900/max(W, H); im = im.resize((int(W*s), int(H*s)), Image.LANCZOS); W, H = im.size
        a = np.asarray(im).astype(np.float32)
        for frac in (0.22, 0.3):
            t = int(min(W, H)*frac)
            for y in range(int(H*0.35), H - t + 1, t//3):
                for x in range(0, W - t + 1, t//3):
                    sc = score_tile(a[y:y+t, x:x+t])
                    if best is None or sc > best[0]: best = (sc, p, (x/s, y/s, (x+t)/s, (y+t)/s))
    return best

def seamless(im):
    a = np.asarray(im).astype(np.float32); n = a.shape[0]
    sh = np.roll(np.roll(a, n//2, 0), n//2, 1)
    yy, xx = np.mgrid[0:n, 0:n] / (n - 1)
    d = np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy))     # 가장자리 거리
    w = np.clip(d / 0.22, 0, 1)[..., None]                              # 가장자리에선 밀린 그림
    out = a*w + sh*(1 - w)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

def level(im):
    # 밝기·채도 맞춤: 너무 어둡거나 뿌연 사진도 비슷한 밝기로
    a = np.asarray(im).astype(np.float32)/255; lum = a @ np.array([0.3, 0.59, 0.11])
    a = a*(0.42/max(lum.mean(), 0.05))**0.7
    m = a.mean(axis=2, keepdims=True); a = m + (a - m)*1.0
    lo, hi = np.percentile(a, 1), np.percentile(a, 99.5); a = (a - lo)/max(hi - lo, 1e-3)*0.92 + 0.03
    return Image.fromarray((a.clip(0, 1)*255).astype(np.uint8))

def seamless4(im, f=0.3):
    # 네 장(원본·가로로 민 것·세로로 민 것·둘 다 민 것)을 섞어 이음매 없는 타일로
    a = np.asarray(im).astype(np.float32); n = a.shape[0]; h = n//2
    rx, ry = np.roll(a, h, 1), np.roll(a, h, 0); rxy = np.roll(rx, h, 0)
    t = np.arange(n)/(n - 1); e = np.minimum(t, 1 - t)
    k = np.clip(1 - e/f, 0, 1); k = k*k*(3 - 2*k)
    fx = k[None, :, None]; fy = k[:, None, None]
    top = a*(1 - fx) + rx*fx; bot = ry*(1 - fx) + rxy*fx
    out = top*(1 - fy) + bot*fy
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

def mirror_tile(im):
    # 거울로 2x2 이어 붙이면 이음매가 없어요 (멀리서 두 크기로 섞어 깔아 대칭은 잘 안 보여요)
    n = im.size[0]; out = Image.new('RGB', (n*2, n*2))
    out.paste(im, (0, 0)); out.paste(im.transpose(Image.FLIP_LEFT_RIGHT), (n, 0))
    out.paste(im.transpose(Image.FLIP_TOP_BOTTOM), (0, n)); out.paste(im.transpose(Image.ROTATE_180), (n, n))
    return out

def make(mid):
    paths = sorted(glob.glob(os.path.join(RAW, mid, '*')))
    if not paths: print(f'{mid}: 원본 없음'); return None
    pk = PICKS.get(mid)
    if pk:   # 사진을 보고 고른 칸 (canopy_picks.json)
        src_id, k, cx, cy, sz = pk; p = sorted(glob.glob(os.path.join(RAW, src_id, '*')))[k]
        src = Image.open(p).convert('RGB'); W, H = src.size; t = min(sz*W, H, W)
        x0 = min(max(cx*W - t/2, 0), W - t); y0 = min(max(cy*H - t/2, 0), H - t); box = (x0, y0, x0 + t, y0 + t); sc = 0
    else:
        b = best_crop(paths)
        if not b or b[0] < 0: print(f'{mid}: 알맞은 칸 없음'); return None
        sc, p, box = b; src = Image.open(p).convert('RGB')
    im = src.crop(tuple(int(v) for v in box))
    im = seamless4(level(im.resize((512, 512), Image.LANCZOS)))
    d = os.path.join(OUT, mid); os.makedirs(d, exist_ok=True)
    im.save(os.path.join(d, 'canopy.jpg'), quality=82, optimize=True)
    print(f'{mid}: {os.path.basename(p)} {tuple(int(v) for v in box)} score {sc:.1f}')
    return os.path.join(d, 'canopy.jpg')

if __name__ == '__main__':
    ids = sys.argv[1:] or sorted(os.path.splitext(f)[0] for f in os.listdir(os.path.join(HERE, 'mountains')))
    outs = [o for o in (make(i) for i in ids) if o]
    sheet = Image.new('RGB', (5*200, ((len(outs)+4)//5)*200))
    for k, o in enumerate(outs): sheet.paste(Image.open(o).resize((200, 200)), ((k % 5)*200, (k//5)*200))
    sheet.save(os.path.join(HERE, 'cache', 'canopy_sheet.jpg'), quality=80)
