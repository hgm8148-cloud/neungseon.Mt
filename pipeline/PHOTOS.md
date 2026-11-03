# 산별 사진 소스 모으기

컨테이너에서는 Wikimedia·Unsplash·Pexels 같은 사진 사이트에 직접 접속할 수 없어서(네트워크 차단), 사진은 아래 링크에서 골라 **업로드**하거나 **Google Drive 폴더**에 넣어 주시면 파이프라인이 가져다 씁니다.

## 쓸 수 있는 라이선스 (상업 이용·수정 가능)

| 출처 | 라이선스 | 표기 의무 |
|---|---|---|
| Wikimedia Commons | Public domain, CC0 | 없음 (권장) |
| Wikimedia Commons | CC BY, CC BY-SA | **작가·라이선스 표기 필수** (BY-SA는 수정본도 같은 라이선스) |
| Poly Haven (질감·HDRI) | CC0 | 없음 |
| Unsplash / Pexels / Pixabay | 각 사이트 라이선스 | 없음. 단 사진을 그대로 재판매·단독 배포 금지 → 게임 안 질감·배경으로 쓰는 건 괜찮음 |

피할 것: CC BY-NC(비상업), CC BY-ND(변경 금지), '에디토리얼 전용', 사람 얼굴이 크게 나온 사진, 상표·간판이 주인공인 사진.

## 산마다 모을 사진 (5종)

1. **정상 풍경 파노라마** – 360° 전망·먼 산 배경 (가로 4000px 이상)
2. **대표 바위·지형 근접** – 바위 질감 (화강암, 현무암, 화산 자갈, 석회암 등)
3. **탐방로 바닥** – 흙길·돌계단·자갈·눈길
4. **대표 식생** – 나무 수관을 오려 쓸 사진 (구상나무, 주목, 철쭉, 억새, 소나무 등)
5. **하늘·계절** – 운해, 노을, 별 (선택)

## 넣는 방법

- 업로드: 파일 이름을 `산id_종류_번호.jpg` (예: `hallasan_rock_1.jpg`)로, 사진 페이지 주소를 함께 알려 주세요.
- 또는 Drive에 `능선 사진/산id/` 폴더를 만들고 공유해 주시면 Drive 연결로 읽어 옵니다.
- 파이프라인은 `pipeline/photos/<산id>/` 에 저장하고 `credits.json` 에 출처·작가·라이선스를 기록해 게임 크레딧에 자동 표시합니다.

## 산별 검색 링크

| # | 산 | 코스 끝 | Commons (라이선스 필터는 화면 위 'License'에서 'Public domain'/'CC0' 또는 'Use with attribution') | Unsplash | Pexels | 찾을 것 |
|---|---|---|---|---|---|---|
| 1 | 북한산 | 백운대 정상 836m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Bukhansan) | [Unsplash](https://unsplash.com/s/photos/bukhansan) | [Pexels](https://www.pexels.com/search/Bukhansan/) | 인수봉·백운대 화강암, 단풍 |
| 2 | 한라산 | 윗세오름 대피소 1700m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Hallasan) | [Unsplash](https://unsplash.com/s/photos/hallasan) | [Pexels](https://www.pexels.com/search/Hallasan/) | 백록담 남벽, 구상나무, 현무암, 조릿대 평원 |
| 3 | 지리산 | 천왕봉 정상 1915m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Jirisan) | [Unsplash](https://unsplash.com/s/photos/jirisan) | [Pexels](https://www.pexels.com/search/Jirisan/) | 천왕봉 운해, 고사목, 돌계단 |
| 4 | 설악산 | 대청봉 정상 1708m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Seoraksan) | [Unsplash](https://unsplash.com/s/photos/seoraksan) | [Pexels](https://www.pexels.com/search/Seoraksan/) | 공룡능선, 화강암 첨봉, 단풍 |
| 5 | 무등산 | 서석대 1100m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Mudeungsan) | [Unsplash](https://unsplash.com/s/photos/mudeungsan) | [Pexels](https://www.pexels.com/search/Mudeungsan/) | 서석대·입석대 주상절리, 억새 |
| 6 | 월출산 | 천황봉 정상 809m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Wolchulsan) | [Unsplash](https://unsplash.com/s/photos/wolchulsan) | [Pexels](https://www.pexels.com/search/Wolchulsan/) | 구름다리, 기암 능선 |
| 7 | 내장산 | 신선봉 정상 763m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Naejangsan) | [Unsplash](https://unsplash.com/s/photos/naejangsan) | [Pexels](https://www.pexels.com/search/Naejangsan/) | 단풍 숲, 서래봉 |
| 8 | 덕유산 | 향적봉 정상 1614m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Deogyusan) | [Unsplash](https://unsplash.com/s/photos/deogyusan) | [Pexels](https://www.pexels.com/search/Deogyusan/) | 주목, 상고대, 덕유 능선 |
| 9 | 소백산 | 비로봉 정상 1439m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Sobaeksan) | [Unsplash](https://unsplash.com/s/photos/sobaeksan) | [Pexels](https://www.pexels.com/search/Sobaeksan/) | 철쭉·초원 능선, 비로봉 표지석 |
| 10 | 태백산 | 천제단 1561m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Taebaeksan) | [Unsplash](https://unsplash.com/s/photos/taebaeksan) | [Pexels](https://www.pexels.com/search/Taebaeksan/) | 주목 군락, 천제단 돌 |
| 11 | 에베레스트 | 칼라파타르 전망대 5644m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Everest) | [Unsplash](https://unsplash.com/s/photos/everest) | [Pexels](https://www.pexels.com/search/Everest/) | 칼라파타르에서 본 에베레스트, 빙하 자갈, 타르초 |
| 12 | 후지산 | 후지산 정상 3776m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Mount+Fuji) | [Unsplash](https://unsplash.com/s/photos/mount-fuji) | [Pexels](https://www.pexels.com/search/Mount%20Fuji/) | 요시다 루트 화산 자갈, 산장, 운해 |
| 13 | 킬리만자로 | 우후루 피크 5895m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Kilimanjaro) | [Unsplash](https://unsplash.com/s/photos/kilimanjaro) | [Pexels](https://www.pexels.com/search/Kilimanjaro/) | 정상 빙하, 화산재 자갈, 우후루 표지판 |
| 14 | 마터호른 | 회른리 산장 3260m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Matterhorn) | [Unsplash](https://unsplash.com/s/photos/matterhorn) | [Pexels](https://www.pexels.com/search/Matterhorn/) | 회른리 능선, 암벽, 눈 |
| 15 | 몽블랑 | 락 블랑 2352m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Mont+Blanc) | [Unsplash](https://unsplash.com/s/photos/mont-blanc) | [Pexels](https://www.pexels.com/search/Mont%20Blanc/) | 락 블랑 호수 반영, 알프스 초원 |
| 16 | 트레 치메 | 로카텔리 산장 2405m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Tre+Cime+di+Lavaredo) | [Unsplash](https://unsplash.com/s/photos/tre-cime-di-lavaredo) | [Pexels](https://www.pexels.com/search/Tre%20Cime%20di%20Lavaredo/) | 세 봉우리 북벽, 석회암 자갈길 |
| 17 | 하프돔 | 하프돔 정상 2694m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Half+Dome) | [Unsplash](https://unsplash.com/s/photos/half-dome) | [Pexels](https://www.pexels.com/search/Half%20Dome/) | 케이블 구간, 화강암 판, 요세미티 계곡 |
| 18 | 황산 | 연화봉 정상 1864m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Huangshan) | [Unsplash](https://unsplash.com/s/photos/huangshan) | [Pexels](https://www.pexels.com/search/Huangshan/) | 기송, 화강암 봉우리, 운해, 돌계단 |
| 19 | 토레스 델 파이네 | 토레스 전망대 875m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Torres+del+Paine) | [Unsplash](https://unsplash.com/s/photos/torres-del-paine) | [Pexels](https://www.pexels.com/search/Torres%20del%20Paine/) | 세 탑과 호수, 빙퇴석 |
| 20 | 통가리로 | 레드 크레이터 1886m | [Commons](https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=Tongariro) | [Unsplash](https://unsplash.com/s/photos/tongariro) | [Pexels](https://www.pexels.com/search/Tongariro/) | 에메랄드 호수, 붉은 화구, 화산 자갈 |

## 공통 질감 (Poly Haven, CC0)

[polyhaven.com/textures](https://polyhaven.com/textures) 에서 `rock`, `gravel`, `snow`, `scree`, `forest ground` 로 찾아 2K jpg(diffuse)만 받으면 됩니다. 이미 받은 `forest_slope`, `rainforest_trail`, `phalzer_forest`, `autumn_forest` HDRI도 같은 CC0예요.

## 하늘 사진 (2026-11-03, 승연 님 드라이브 하늘 폴더)

`python3 make_sky.py` → `photos/web/sky/milkyway.jpg`(온하늘 은하수 지도), `moon.jpg`, 출처는 `photos/sky_credits.json`.

- 게임 안에 직접 들어가는 사진: lanius 님 은하수(Pixabay 10528056) → 밤하늘 별·은하수, Pexels 님 보름달(Pixabay 1869760) → 달.
- 색만 참고한 사진(13장): 일출 konevi·21028723, 오전 mustafaelmas·beholz, 오후 bartroman·hias_schell, 일몰 alberto_guevara87·leolo212·tom6667·peggychoucair, 박명·밤 bru-no·manuel-h·stocksnap, 밤 evgenit·kanenori·pexels-camping. 모두 Pixabay Content License.
- 드라이브 하늘 폴더의 Unsplash `.avif`, pngtree·뉴스·블로그 이미지는 라이선스를 확인할 수 없어 쓰지 않았어요.


황산(Pixabay, 승연 님이 직접 받아 올림, 작가 이름 미확인)·소백산·월출산(국립공원공단 누리집, 공공누리 제1유형) 사진은 승연 님이 채팅으로 보낸 것이에요 (2026-11-03). picks.json 의 credit 항목에 출처를 적어 두었어요.
