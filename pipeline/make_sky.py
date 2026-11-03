"""승연 님 드라이브 하늘 사진 → 게임 밤하늘·달 텍스처 (2026-11-03)

    python3 make_sky.py      # photos/web/sky/ 에 milkyway.jpg · moon.jpg, photos/sky_credits.json

- milkyway.jpg: 머리 위(천정)를 가운데 둔 온하늘 사진(입체 사영, 게임 STARS 셰이더와 같은 좌표).
  lanius 님 은하수 사진의 띠를 펴서 하늘을 가로지르는 큰 원을 따라 두르고,
  띠 밖은 같은 사진에서 뽑은 별(배경을 걷어 낸 고주파 성분)을 깔아요.
  사진의 초록빛 대기광·지평선 불빛은 걷어 내고(행마다 배경 밝기 추정) 별과 은하수 빛만 남겨요.
- moon.jpg: Pexels 님 보름달 사진에서 달 원반만 정사각으로 잘라요(위상은 게임이 그려요).
원본은 /mnt/project-files/hiking-game/pipeline/photos/raw/sky/ (용량이 커서 저장소 밖).
"""
import json, os, re
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = '/mnt/project-files/hiking-game/pipeline/photos/raw/sky'
OUT = os.path.join(HERE, 'photos', 'web', 'sky')
MW = '1VwkvEtiZH0yvVQQZhYbxInfNkBDmYhYK'      # lanius-milky-way-10528056
MOON = '1LbM6eDycZb8pMg_wl1_GqPFmbi9JIWuP'    # pexels-full-moon-1869760
REF = {  # 색·밝기를 참고만 한 사진 (게임 안에 직접 들어가지 않음)
    'gradient': ['1Wbgo26kxva0g8_UTg8UjXH2-MoS5gvNq', '1SeCTb_LjLYTxOmYjdZ090EhAKZPp4rTx', '1TSOP9Lfgk9W1uDAd_RmxnA-sbFLSpCJ8', '1wHN2q8gmtSxyMEYExtBxUF2KJCD_Do2E',
                 '1NOrVO0P74wNs5M3uehWCzA2nvOYxE1xB', '18SPKnPZVql7j1Mt58GER74whQ-fTjsSV', '1kyzQesDvrl8hIFRItCKXG7_btksvb0uq', '1xPUcOe9QQGGTDMibjgBPDPBwNVN41WFS',
                 '1lFTlJZb_4sqShHn1aarIWpmt8uFyF6Z5', '11vpPNdua096re3NQrGzw9u-SO51YzFwl', '1Gu6abMKUl-rOY8mMneFWZGgfT2KwE6VW', '102rKZXWc4cUCqp1nWlX9m6JSoONQhALy',
                 '1uNlrjv_YWRW3T2_B08pFMWnCT0XZ1bhE'],
    'night': ['1LxnsGrLuen0BNVwcp8ccvmPXaV4ill1r', '1bv6fjeR1rHCBtYF0oMqLvO6yr5iwlLF_', '1mJLUk296rkLi8tQrEXrON4iu_wdfRtry'],
}
CAT = '/mnt/project-files/hiking-game/pipeline/photos/drive_catalog.tsv'
PIX = re.compile(r'^([a-z0-9_]+)-([a-z0-9-]+)-(\d{5,9})_1920(?: \(\d\))?\.(?:jpg|png)$')


def load(i):
    return np.asarray(Image.open(os.path.join(RAW, i + '.jpg')).convert('RGB')).astype(np.float32) / 255


def blur(a, r):
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255


def bilinear(img, x, y):
    h, w, _ = img.shape
    x = np.clip(x, 0, w - 1.001); y = np.clip(y, 0, h - 1.001)
    x0 = x.astype(int); y0 = y.astype(int); fx = (x - x0)[..., None]; fy = (y - y0)[..., None]
    a = img[y0, x0]; b = img[y0, x0 + 1]; c = img[y0 + 1, x0]; d = img[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def milkyway(N=2048):
    a = load(MW); h, w, _ = a.shape
    H = int(h * 0.74); a = a[:H]                                    # 맨 아래 땅·마을 불빛은 빼요
    # 1) 행마다 배경(대기광·지평선 빛) 추정 후 빼기: 띠가 차지하지 않는 어두운 쪽 15% 값
    lum = a.mean(2)
    bg = np.percentile(a.reshape(H, w, 3), 15, axis=1)            # (H,3)
    bg = blur(np.repeat(bg[:, None, :], 8, 1), 12)[:, 4, :]       # 세로로 부드럽게
    s = np.clip(a - bg[:, None, :] * 0.97, 0, None)
    # 초록 대기광 빛깔 걷기: 띠 바깥 평균을 회색으로
    neutral = s[:, : w // 8].reshape(-1, 3).mean(0) + 1e-4
    s *= (neutral.mean() / neutral)[None, None, :] * 0.6 + 0.4
    # 2) 띠 중심선: 흐리게 한 밝기의 행별 최댓값 → 1차 직선
    sm = blur(s, 40).mean(2); ys = np.arange(int(H * 0.04), int(H * 0.96), 8)
    xs = np.array([np.argmax(sm[y]) for y in ys]); wt = np.array([sm[y].max() for y in ys])
    k, b0 = np.polyfit(ys, xs, 1, w=wt)
    # 3) 별 성분(고주파): 띠 바깥에 깔 별
    hp = s[: int(H * 0.7), : int(w * 0.8)]; hp = np.clip(hp - blur(hp, 5), 0, None)   # 구름·불빛·인공위성 줄이 없는 쪽만
    lv = hp.mean(2); th = np.median(lv) + 3.0 * np.median(np.abs(lv - np.median(lv)))
    stars = np.clip(hp - th, 0, None) * 1.6; Hs, Ws = stars.shape[:2]
    # 4) 하늘 방향 계산 (입체 사영의 역)
    u = (np.arange(N) + 0.5) / N; U, V = np.meshgrid(u, u)
    qx = (U - 0.5) / 0.49; qz = (V - 0.5) / 0.49; r2 = qx * qx + qz * qz
    dy = (1 - r2) / (1 + r2); dx = 2 * qx / (1 + r2); dz = 2 * qz / (1 + r2)
    n = np.array([0.62, 0.32, 0.72]); n /= np.linalg.norm(n)
    e1 = np.cross(n, [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
    lat = np.arcsin(np.clip(dx * n[0] + dy * n[1] + dz * n[2], -1, 1))
    lon = np.arctan2(dx * e2[0] + dy * e2[1] + dz * e2[2], dx * e1[0] + dy * e1[1] + dz * e1[2])
    # 5) 띠: 은하 경도 → 사진 세로(왕복 반복), 위도 → 띠 중심에서 가로 거리 (사진 1px ≈ 0.052°)
    deg = 1920 / 100.0
    L = (np.degrees(lon) + 180) % 360; seg = (L // 80).astype(int); f = (L % 80) / 80
    fwd = (seg % 2 == 0); py = np.where(fwd, f, 1 - f) * (H - 40) + 20
    flip = np.where(seg % 4 >= 2, -1, 1)
    px = (k * py + b0) + flip * np.degrees(lat) * deg
    band = bilinear(s, px, py)
    wb = np.exp(-(np.degrees(lat) / 26) ** 4)                       # 띠 사진 폭 안쪽만
    core = 0.55 + 0.45 * np.exp(-((np.degrees(lon) - 35) / 70) ** 2)  # 은하 중심 쪽이 더 밝게
    # 6) 배경 별: 하늘 좌표를 사진 위에 반사 반복으로 깔아요
    sx = (U * N * 1.15) % (2 * Ws); sx = np.where(sx >= Ws, 2 * Ws - sx - 1, sx)
    sy = (V * N * 1.15) % (2 * Hs); sy = np.where(sy >= Hs, 2 * Hs - sy - 1, sy)
    st = bilinear(stars, sx, sy)
    out = st * (1 - wb[..., None]) * 0.5 + band * (wb * core * 1.6)[..., None]
    out *= np.clip((dy[..., None] + 0.08) / 0.1, 0, 1)                # 지평선 아래는 비워요
    out = np.clip(out / np.percentile(out, 99.85) * 0.92, 0, 1) ** 0.85
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray((out * 255).astype(np.uint8)).save(os.path.join(OUT, 'milkyway.jpg'), 'JPEG', quality=86, optimize=True, progressive=True)


def moon(S=512):
    a = load(MOON); m = a.mean(2) > 0.12
    ys, xs = np.nonzero(m); cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    r = max(xs.max() - xs.min(), ys.max() - ys.min()) / 2 + 1
    im = Image.open(os.path.join(RAW, MOON + '.jpg')).convert('RGB').crop((int(cx - r), int(cy - r), int(cx + r), int(cy + r))).resize((S, S), Image.LANCZOS)
    v = np.asarray(im).astype(np.float32) / 255; v = v / np.percentile(v, 99.5) * 0.98       # 밝기 맞추고 노란기는 살짝 덜어요
    v = v * np.array([0.98, 1.0, 1.04]); Image.fromarray((np.clip(v, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, 'moon.jpg'), 'JPEG', quality=88)


def credits():
    titles = {}
    for l in open(CAT, encoding='utf-8'):
        p = l.rstrip('\n').split('\t')
        if p[0] == 'sky': titles[p[3]] = p[2]
    def c(i, role, file=None):
        t = titles[i]; mm = PIX.match(t)
        if not mm: raise SystemExit('[sky] 라이선스를 확인할 수 없는 사진: ' + t)
        user, slug, pid = mm.groups()
        return dict(role=role, file=file, drive=i, title=t, author=user, source='Pixabay', license='Pixabay Content License', url=f'https://pixabay.com/photos/{slug}-{pid}/')
    cr = [c(MW, 'milkyway', 'photos/sky/milkyway.jpg'), c(MOON, 'moon', 'photos/sky/moon.jpg')]
    for role, ids in REF.items(): cr += [c(i, 'ref-' + role) for i in ids]
    json.dump(cr, open(os.path.join(HERE, 'photos', 'sky_credits.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    milkyway(); moon(); credits()
    for f in os.listdir(OUT): print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, 'KB')
