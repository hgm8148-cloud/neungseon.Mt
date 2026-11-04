"""산마다 정상 실루엣(peakArt)을 만들어 mountains/<id>.json 에 넣어요 (2026-11-04)

Drive 대표 사진을 보고 그 산의 모양을 간단한 도형(원뿔·돔·뾰족 바위·탑)을 겹쳐 그려요.
  python3 make_peaks.py            # 모든 산
  python3 make_peaks.py fuji ...   # 몇 개만
"""
import json, math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
N = 96


def xs():
    return [i / (N - 1) for i in range(N)]


def cone(cx, w, h, p=1.0, top=0.0):
    """cx 가운데, w 반폭, p<1 오목(후지산처럼 아래가 퍼짐) · p>1 볼록, top 평평한 꼭대기 반폭"""
    def f(x):
        d = max(0.0, abs(x - cx) - top) / max(1e-6, w - top)
        return h * max(0.0, 1 - d) ** (1 / p) if d < 1 else 0.0
    return f


def dome(cx, w, h, k=2.0):
    def f(x):
        d = abs(x - cx) / w
        return h * max(0.0, 1 - d ** k) ** 0.5 if d < 1 else 0.0
    return f


def spire(cx, w, h, sharp=1.6):
    def f(x):
        d = abs(x - cx) / w
        return h * max(0.0, 1 - d) ** (1 / sharp) if d < 1 else 0.0
    return f


def tower(cx, w, h, edge=0.15, tilt=0.0):
    """세로 절벽 탑 (트레치메·토레스)"""
    def f(x):
        d = abs(x - cx) / w
        if d >= 1: return 0.0
        t = h * (1 - tilt * (x - cx) / w)
        return t if d < 1 - edge else t * (1 - (d - (1 - edge)) / edge) ** 0.35
    return f


def comb(*fs):
    return lambda x: max(f(x) for f in fs)


def jag(f, amp, freq, seed=1, lo=0.0):
    rnd = random.Random(seed); ph = [rnd.random() * 6.28 for _ in range(4)]
    def g(x):
        v = f(x)
        if v <= lo: return v
        n = sum(math.sin(x * freq * (1.7 ** k) + ph[k]) / (1.6 ** k) for k in range(4))
        return max(0.0, v + amp * n * min(1.0, v * 3))
    return g


def sample(f):
    pts = [[round(x, 4), max(0.0, f(x))] for x in xs()]
    m = max(p[1] for p in pts) or 1
    return [[x, round(y / m, 4)] for x, y in pts]


ALPS = {"spring": 0.72, "summer": 0.5, "autumn": 0.55, "winter": 0.88}
KR_WINTER = lambda w: {"spring": 0.0, "summer": 0.0, "autumn": 0.0, "winter": w}

SHAPES = {
    # 국내
    'bukhansan': dict(f=comb(cone(0.5, 0.5, 0.42, 1.2), spire(0.5, 0.11, 1.0, 1.3), dome(0.645, 0.075, 0.9, 2.2), spire(0.36, 0.09, 0.84, 1.4), spire(0.29, 0.06, 0.66, 1.2)),
                      aspect=3.0, ang=14, rock='#b5a994', rock2='#d4c8b2', forest='#2f4630', forestTop=0.36, snow=KR_WINTER(0.25), streak=0.3,
                      forestBy={"autumn": "#8a4a2a", "winter": "#5a5a52"}),
    'deogyusan': dict(f=jag(comb(dome(0.5, 0.5, 1.0, 1.6), dome(0.22, 0.2, 0.7), dome(0.8, 0.22, 0.75)), 0.02, 40, 3),
                      aspect=6, ang=7, rock='#5a6450', forest='#38502f', forestTop=0.95, snow=KR_WINTER(0.85), streak=0.15,
                      forestBy={"autumn": "#8a5530", "winter": "#6e6e66", "spring": "#5d8a40"}),
    'jirisan': dict(f=jag(comb(dome(0.5, 0.5, 0.82, 1.4), cone(0.56, 0.16, 1.0, 1.1), dome(0.25, 0.18, 0.72), dome(0.8, 0.16, 0.7)), 0.015, 36, 5),
                    aspect=6, ang=8, rock='#5d6151', forest='#334a2c', forestTop=0.9, snow=KR_WINTER(0.6), streak=0.25,
                    forestBy={"autumn": "#87502c", "winter": "#68665e", "spring": "#557f3c"}),
    'hallasan': dict(f=comb(cone(0.5, 0.5, 0.62, 0.8, 0.12), tower(0.5, 0.14, 1.0, 0.45), lambda x: 0.0),
                     aspect=4.6, ang=9, rock='#5e5850', rock2='#7a7066', forest='#34502f', forestTop=0.55, snow={"spring": 0.12, "summer": 0.0, "autumn": 0.0, "winter": 0.6}, streak=0.6,
                     forestBy={"autumn": "#7a5a34", "winter": "#6a6a64"}),
    'mudeungsan': dict(f=jag(comb(dome(0.5, 0.5, 0.86, 1.5), dome(0.52, 0.14, 1.0, 1.8)), 0.012, 90, 7),
                       aspect=4.6, ang=9, rock='#6b675e', rock2='#8a857a', forest='#35502e', forestTop=0.8, snow=KR_WINTER(0.4), streak=0.3,
                       forestBy={"autumn": "#8a6a3a", "winter": "#707068"}),
    'naejangsan': dict(f=jag(comb(dome(0.5, 0.5, 0.72, 1.4), spire(0.3, 0.07, 0.95, 1.2), spire(0.44, 0.06, 0.9, 1.2), spire(0.58, 0.08, 1.0, 1.2), spire(0.72, 0.06, 0.86, 1.2)), 0.02, 50, 9),
                       aspect=4.6, ang=10, rock='#77705f', forest='#34502d', forestTop=0.85, snow=KR_WINTER(0.4), streak=0.3,
                       forestBy={"autumn": "#a2381e", "winter": "#6c6a62"}),
    'seoraksan': dict(f=jag(comb(cone(0.5, 0.5, 0.55, 1.1), spire(0.47, 0.1, 1.0, 1.2), *[spire(0.55 + 0.045 * k, 0.025, 0.86 - 0.05 * k, 2.4) for k in range(7)], *[spire(0.4 - 0.05 * k, 0.03, 0.8 - 0.07 * k, 2.2) for k in range(4)]), 0.015, 70, 11),
                      aspect=3.6, ang=13, rock='#a29a8a', rock2='#c4bba8', forest='#2f472c', forestTop=0.42, snow={"spring": 0.0, "summer": 0.0, "autumn": 0.0, "winter": 0.55}, streak=0.5,
                      forestBy={"autumn": "#9a4a26", "winter": "#5e5e58"}),
    'sobaeksan': dict(f=comb(dome(0.5, 0.5, 0.8, 1.3), dome(0.45, 0.16, 1.0, 1.6), dome(0.78, 0.15, 0.82, 1.6)),
                      aspect=6.5, ang=7, rock='#6f7550', forest='#5a7a40', forestTop=0.98, snow=KR_WINTER(0.85), streak=0.15,
                      forestBy={"autumn": "#a28a52", "winter": "#77756c", "spring": "#6e8c46"}),
    'taebaeksan': dict(f=comb(dome(0.5, 0.5, 0.86, 1.3), dome(0.5, 0.18, 1.0, 1.7)),
                       aspect=6.5, ang=7, rock='#5d6150', forest='#355030', forestTop=0.95, snow=KR_WINTER(0.85), streak=0.15,
                       forestBy={"autumn": "#8a5a32", "winter": "#6c6c66"}),
    'wolchulsan': dict(f=jag(comb(cone(0.5, 0.5, 0.5, 1.1), *[spire(0.25 + 0.06 * k, 0.04, 0.78 + 0.22 * math.sin(k * 0.9) ** 2, 2.0) for k in range(9)]), 0.02, 80, 13),
                       aspect=4.0, ang=11, rock='#b0a691', rock2='#cfc5b0', forest='#31492c', forestTop=0.4, snow=KR_WINTER(0.25), streak=0.3,
                       forestBy={"autumn": "#8c4a28", "winter": "#5e5e58"}),
    # 해외
    'everest': dict(f=comb(cone(0.42, 0.42, 1.0, 1.05), cone(0.78, 0.26, 0.74, 1.0), cone(0.1, 0.15, 0.5)),
                    aspect=2.8, ang=15, rock='#3a383c', rock2='#55525a', snow={"all": 0.82}, streak=1.0, haze=0.18),
    'halfdome': dict(f=lambda x: (0.0 if x < 0.33 else 1.0 * (1 - ((x - 0.36) / 0.6) ** 2) ** 0.5 if 0.36 <= x <= 0.96 else (x - 0.33) / 0.03 if x < 0.36 else 0.0),
                     aspect=2.6, ang=12, rock='#a29e95', rock2='#c2bdb1', forest='#2c442a', forestTop=0.18, snow={"spring": 0.0, "summer": 0.0, "autumn": 0.0, "winter": 0.18}, streak=0.2),
    'huangshan': dict(f=jag(comb(dome(0.5, 0.5, 0.5, 1.3), *[spire(0.2 + 0.05 * k, 0.03, 0.62 + 0.38 * abs(math.sin(k * 1.7)), 2.0) for k in range(13)]), 0.015, 90, 17),
                      aspect=3.0, ang=14, rock='#8c877c', rock2='#aba59a', forest='#2e4a2c', forestTop=0.5, snow={"spring": 0.0, "summer": 0.0, "autumn": 0.0, "winter": 0.3}, streak=0.4,
                      forestBy={"winter": "#5a5e58"}),
    'kilimanjaro': dict(f=comb(cone(0.45, 0.45, 1.0, 0.75, 0.13), jag(spire(0.86, 0.09, 0.62, 1.4), 0.03, 120, 19)),
                        aspect=6.0, ang=8, rock='#4c4038', rock2='#665448', snow={"all": 0.16}, streak=0.5, haze=0.2),
    'matterhorn': dict(f=lambda x: max(max(0.0, 1 - abs(x - 0.46) / (0.17 if x < 0.46 else 0.26)) ** 1.45, max(0.0, 1 - abs(x - 0.5) / 0.42) * 0.28),
                       aspect=1.7, ang=18, rock='#4a4440', rock2='#6a625c', snow=ALPS, streak=0.8, haze=0.18),
    'montblanc': dict(f=comb(dome(0.36, 0.34, 1.0, 1.7), jag(comb(*[spire(0.62 + 0.05 * k, 0.035, 0.7 - 0.06 * k + 0.1 * (k % 2), 2.2) for k in range(7)]), 0.02, 120, 23)),
                      aspect=3.2, ang=13, rock='#3e3c40', rock2='#5a5660', snow={"spring": 0.85, "summer": 0.72, "autumn": 0.75, "winter": 0.95}, streak=0.7, haze=0.18),
    'tongariro': dict(f=comb(cone(0.58, 0.32, 1.0, 1.05, 0.03), dome(0.25, 0.25, 0.6, 1.4)),
                      aspect=3.0, ang=13, rock='#5a3e36', rock2='#7a4e40', snow={"spring": 0.4, "summer": 0.05, "autumn": 0.15, "winter": 0.6}, streak=1.0),
    'torresdelpaine': dict(f=comb(cone(0.5, 0.5, 0.45, 1.1), spire(0.39, 0.045, 0.86, 0.45), spire(0.5, 0.05, 1.0, 0.45), spire(0.61, 0.045, 0.9, 0.45), jag(cone(0.82, 0.16, 0.7, 1.2), 0.04, 90, 29)),
                           aspect=2.6, ang=15, rock='#7e7a76', rock2='#9a948e', forest='#3b4a2e', forestTop=0.2, snow={"spring": 0.35, "summer": 0.2, "autumn": 0.25, "winter": 0.55}, streak=0.4),
    'trecime': dict(f=comb(cone(0.5, 0.5, 0.38, 1.0), tower(0.35, 0.07, 0.78, 0.35, 0.05), tower(0.5, 0.085, 1.0, 0.3, 0.04), tower(0.665, 0.075, 0.86, 0.35, -0.04)),
                    aspect=2.8, ang=14, rock='#b0a38c', rock2='#cbbfa6', snow={"spring": 0.22, "summer": 0.05, "autumn": 0.1, "winter": 0.5}, streak=0.4),
}


def main():
    only = sys.argv[1:]
    for mid, s in SHAPES.items():
        if only and mid not in only: continue
        p = os.path.join(HERE, 'mountains', mid + '.json')
        m = json.load(open(p))
        art = {k: v for k, v in s.items() if k != 'f'}
        art['profile'] = sample(s['f'])
        art.setdefault('haze', 0.12)
        art['src'] = 'Drive 대표 사진을 보고 그린 실루엣 (make_peaks.py)'
        m['peakArt'] = art
        json.dump(m, open(p, 'w'), ensure_ascii=False, indent=1)
        print(mid, len(art['profile']))


if __name__ == '__main__':
    main()
