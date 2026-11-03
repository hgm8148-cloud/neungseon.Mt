"""산 하나의 지형·탐방로 데이터 만들기.

    python3 make_terrain.py hallasan        # mountains/hallasan.json → data/hallasan.json
    python3 make_terrain.py --all

북한산 v1에서 쓰던 prep.py(가까운 지형+탐방로) · far.py(14km) · ultra.py(48km)를
산 설정 파일 하나로 돌릴 수 있게 합친 것입니다.

- 고도: AWS Terrain Tiles (Terrarium, 공개 DEM) — 타일은 cache/ 에 저장해 다시 받지 않아요.
- 탐방로: 설정의 지점(waypoints)을 경사 비용 A*로 이어 근사합니다. 실제 등산로 GPS가 아니에요.
- 지점 보정(snap): "peak"는 반경 안의 가장 높은 곳, "elev"는 설정한 해발에 가장 가까운 곳으로 옮겨요.
- 높은 산: 들머리가 600m를 넘으면 게임 안 높이를 BASE만큼 내려(북한산 들머리와 비슷한 높이로)
  게임의 구름바다·바위·하늘 기준값이 그대로 맞게 하고, 화면 해발 표시는 BASE를 더해 실제 값으로 보여요.
"""
import math, json, base64, heapq, os, sys, urllib.request
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'cache')
EARTH = 40075016.686


def tx(lon, Z): return (lon + 180) / 360 * 2 ** Z
def ty(lat, Z):
    r = math.radians(lat); return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2 ** Z


def tile(Z, x, y):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, f'{Z}_{x}_{y}.png')
    if not os.path.exists(p):
        url = f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{x}/{y}.png'
        for k in range(4):
            try:
                data = urllib.request.urlopen(url, timeout=30).read(); break
            except Exception:
                if k == 3: raise
        open(p, 'wb').write(data)
    a = np.asarray(Image.open(p).convert('RGB')).astype(np.float64)
    return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768


def dem_crop(clat, clon, size_m, Z):
    """중심 (clat,clon), 한 변 size_m 의 정사각형 고도 배열(원본 해상도)과 좌표 변환 함수."""
    mpp = EARTH * math.cos(math.radians(clat)) / (2 ** Z * 256)
    half = size_m / 2 / mpp
    cx, cy = tx(clon, Z) * 256, ty(clat, Z) * 256
    x0, x1 = int((cx - half) // 256), int((cx + half) // 256)
    y0, y1 = int((cy - half) // 256), int((cy + half) // 256)
    H = np.vstack([np.hstack([tile(Z, x, y) for x in range(x0, x1 + 1)]) for y in range(y0, y1 + 1)])
    ox, oy, span = int(cx - half - x0 * 256), int(cy - half - y0 * 256), int(2 * half)
    crop = H[oy:oy + span, ox:ox + span].astype(np.float32)
    def to_px(lat, lon):  # crop 픽셀 좌표 (x, y)
        return (tx(lon, Z) * 256 - x0 * 256 - ox, ty(lat, Z) * 256 - y0 * 256 - oy)
    def to_ll(px, py):
        X = (px + x0 * 256 + ox) / 256; Y = (py + y0 * 256 + oy) / 256
        lon = X / 2 ** Z * 360 - 180
        lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * Y / 2 ** Z))))
        return lat, lon
    return crop, mpp, span, to_px, to_ll


def _snap_once(crop, mpp, px, py, w, radius):
    mode = w['snap']
    r = int(radius / mpp)
    j0, j1 = max(0, int(py) - r), min(crop.shape[0], int(py) + r + 1)
    i0, i1 = max(0, int(px) - r), min(crop.shape[1], int(px) + r + 1)
    sub = crop[j0:j1, i0:i1]
    J, I = np.mgrid[j0:j1, i0:i1]
    dist = np.hypot(I - px, J - py) * mpp
    inside = dist <= radius
    if mode == 'peak':
        # 봉우리: 둘레(약 60m)에서 가장 높은 점들 가운데, 설정 해발에 가깝고 가까운 곳
        k = max(1, int(30 / mpp)); P = np.pad(sub, k, mode='edge'); mx = sub.copy()
        for dy in range(-k, k + 1):
            for dx in range(-k, k + 1):
                mx = np.maximum(mx, P[k + dy:k + dy + sub.shape[0], k + dx:k + dx + sub.shape[1]])
        top = sub >= mx - 0.01
        target = w.get('elev', float(sub[inside].max()))
        cost = np.where(inside & top, np.abs(sub - target) + 0.03 * dist, np.inf)
    else:
        cost = np.where(inside, np.abs(sub - w['elev']) + 0.08 * dist, np.inf)
    k = np.unravel_index(np.argmin(cost), cost.shape)
    return I[k] + 0.5, J[k] + 0.5, float(dist[k]), float(sub[k])


def snap(crop, mpp, to_px, to_ll, w, radius=350):
    """설정 좌표 근처에서 실제 지형에 맞는 점 찾기. 해발이 60m 넘게 어긋나면 더 넓게(1.5km, 3km) 찾아봐요."""
    if not w.get('snap'): return w['lat'], w['lon'], None
    px, py = to_px(w['lat'], w['lon'])
    for rad in (radius, 1500, 3000):
        x, y, d, h = _snap_once(crop, mpp, px, py, w, rad)
        if 'elev' not in w or abs(h - w['elev']) <= 60: break
    lat, lon = to_ll(x, y)
    return lat, lon, d


def astar(G, cell, s, t):
    N = G.shape[0]
    s = (int(round(s[1])), int(round(s[0]))); t = (int(round(t[1])), int(round(t[0])))
    openq = [(0, s)]; came = {s: None}; cost = {s: 0}
    nb = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    while openq:
        _, c = heapq.heappop(openq)
        if c == t: break
        for dy, dx in nb:
            n = (c[0] + dy, c[1] + dx)
            if not (0 <= n[0] < N and 0 <= n[1] < N): continue
            d = math.hypot(dx, dy) * cell; sl = abs(G[n] - G[c]) / d
            nc = cost[c] + d * (1 + (sl * 4) ** 2)
            if nc < cost.get(n, 1e18):
                cost[n] = nc; came[n] = c
                heapq.heappush(openq, (nc + math.hypot(n[0] - t[0], n[1] - t[1]) * cell, n))
    p = []; c = t
    while c: p.append(c); c = came[c]
    return p[::-1]


def resize(crop, N):
    return np.asarray(Image.fromarray(crop, mode='F').resize((N, N), Image.BILINEAR)).astype(np.float64)


def build(cfg, log=print):
    T = cfg.get('terrain', {})
    wps = cfg['waypoints']
    Zn = T.get('z', 15)
    legacy = cfg.get('legacy')
    # 1) 지점 보정: 넉넉한 영역을 받아 snap
    lats = [w['lat'] for w in wps]; lons = [w['lon'] for w in wps]
    c0 = ((min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2)
    ext = max((max(lats) - min(lats)) * 111320, (max(lons) - min(lons)) * 111320 * math.cos(math.radians(c0[0])))
    report = []
    pts = []
    if legacy:
        pts = [(w['lat'], w['lon']) for w in wps]
    else:
        crop, mpp, span, to_px, to_ll = dem_crop(c0[0], c0[1], ext + 7000, Zn)
        for w in wps:
            lat, lon, moved = snap(crop, mpp, to_px, to_ll, w)
            pts.append((lat, lon))
            px, py = to_px(lat, lon)
            got = float(crop[int(py), int(px)])
            report.append((w['ko'], w.get('elev'), round(got), None if moved is None else round(moved)))
    # 2) 가까운 지형
    if 'center' in T: clat, clon = T['center']
    else:
        la = [p[0] for p in pts]; lo = [p[1] for p in pts]
        clat, clon = (min(la) + max(la)) / 2, (min(lo) + max(lo)) / 2
    if 'near' in T: SIZE = float(T['near'])
    else:
        la = [p[0] for p in pts]; lo = [p[1] for p in pts]
        e2 = max((max(la) - min(la)) * 111320, (max(lo) - min(lo)) * 111320 * math.cos(math.radians(clat)))
        SIZE = float(max(3000, math.ceil((e2 + 1400) / 100) * 100))
    N = int(T.get('nearN', min(385, max(257, int(SIZE / 11.7) | 1))))
    crop, mpp, span, to_px, to_ll = dem_crop(clat, clon, SIZE, Zn)
    if legacy:
        bad = crop < 20
        if bad.any(): crop[bad] = np.median(crop[~bad])
    G = resize(crop, N)
    P = np.pad(G, 1, mode='edge')
    B = sum(P[1 + dy:1 + dy + N, 1 + dx:1 + dx + N] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9
    G = 0.7 * G + 0.3 * B if T.get('sharp') else B   # 뾰족한 바위산은 덜 뭉개요 (절벽·첨봉이 살아 있게)
    cell = SIZE / (N - 1)
    def g(lat, lon):
        px, py = to_px(lat, lon); return (px / span * (N - 1), py / span * (N - 1))
    gw = [g(*p) for p in pts]
    path = []
    for i in range(len(gw) - 1):
        seg = astar(G, cell, gw[i], gw[i + 1])
        if path: seg = seg[1:]
        path += seg
    P2 = np.array([[c[1], c[0]] for c in path], float)
    for _ in range(3):
        q = [P2[0]]
        for a, b in zip(P2[:-1], P2[1:]): q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        q.append(P2[-1]); P2 = np.array(q)
    def w2(px, py): return [round((px - (N - 1) / 2) * cell, 2), round((py - (N - 1) / 2) * cell, 2)]
    trail = [w2(*p) for p in P2]
    L = sum(math.dist(a, b) for a, b in zip(trail[:-1], trail[1:]))
    # 3) 높이 기준: 높은 산은 BASE만큼 내려서 게임 기준값(구름바다 200~300m, 바위 700m…)에 맞춰요
    def at(px, py):
        i, j = min(N - 1, max(0, int(round(py)))), min(N - 1, max(0, int(round(px)))); return float(G[i, j])
    h_start, h_end = at(*gw[0]), at(*gw[-1])
    BASE = 0 if legacy or h_start < 600 else int(round(h_start - 280))
    if legacy:
        H0, VEX = 272, 1.058
    else:
        H0 = round(h_start - BASE, 1)
        # 북한산 v1과 같은 방식: 끝 지점의 DEM 높이가 실제 해발과 맞도록 수직 비율을 조금 늘려요
        dem_rise = max(1.0, (h_end - BASE) - H0)
        VEX = round(min(1.3, max(0.85, (cfg['elev'] - BASE - H0) / dem_rise)), 3)
    out = dict(N=N, size=SIZE, h=base64.b64encode(np.clip(np.round((G - BASE) * 10), 0, 65535).astype('<u2').tobytes()).decode(),
               trail=trail, wps=[dict(name=w['ko'], pos=w2(*p)) for w, p in zip(wps, gw)])
    # 4) 먼 산 (14km, 48km)
    for key, Z, S, NN, sc in (('far', 13, 14000, 161, 2), ('ultra', 11, 48000, 241, 1)):
        c, *_ = dem_crop(clat, clon, S, Z)
        c[c < 0] = 0
        GG = resize(c, NN)   # 먼 산은 실제 해발 그대로 저장 (바다·평야가 잘리지 않게, 게임에서 BASE를 빼요)
        out[key] = dict(N=NN, size=S, h=base64.b64encode(np.clip(np.round(GG * sc), 0, 65535).astype('<u2').tobytes()).decode())
    out['meta'] = dict(farReal=True, id=cfg['id'], lat=round(clat, 5), lon=round(clon, 5), BASE=BASE, H0=H0, VEX=VEX,
                       trail_m=round(L), snapped=[[round(a, 5), round(b, 5)] for a, b in pts])
    log(f"[{cfg['id']}] near {SIZE:.0f}m N={N} cell={cell:.1f}m · trail {L/1000:.2f}km · BASE {BASE} H0 {H0} VEX {VEX} · DEM start {h_start:.0f} end {h_end:.0f}")
    for r in report:
        flag = '' if r[1] is None or abs(r[1] - r[2]) < 80 else '  ← 확인 필요'
        log(f"   {r[0]}: 설정 {r[1]} / DEM {r[2]} m, 옮긴 거리 {r[3]} m{flag}")
    return out


def main(ids):
    os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)
    for i in ids:
        cfg = json.load(open(os.path.join(HERE, 'mountains', i + '.json')))
        out = build(cfg)
        json.dump(out, open(os.path.join(HERE, 'data', i + '.json'), 'w'), ensure_ascii=False, separators=(',', ':'))


if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--all']:
        a = sorted(f[:-5] for f in os.listdir(os.path.join(HERE, 'mountains')) if f.endswith('.json'))
    main(a)
