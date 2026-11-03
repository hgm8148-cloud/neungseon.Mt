# 능선 · 산 추가 파이프라인

북한산 v1을 만들 때 손으로 하던 일(prep.py · far.py · ultra.py · build.py)을 **산 설정 파일 하나**로 돌릴 수 있게 정리했어요.

```
mountains/<id>.json   산 설정 (이름 4개 언어, 코스 지점 좌표, 해발, 깃발, 시간대 …)
make_terrain.py       설정 → data/<id>.json  (AWS Terrarium 고도 → 가까운 지형 + 14km + 48km 먼 산, 탐방로 A*)
build_site.py         템플릿 + 설정 + 지형 → out/<page>.html  (산 선택 화면 포함)
PHOTOS.md             산별 저작권 문제없는 사진 모으기 안내
photos/<id>/          받은 사진, photos/credits.json 에 출처·라이선스
```

## 새 산 추가하기

1. `mountains/hallasan.json` 을 복사해 `mountains/<새id>.json` 으로 만들고 값을 채워요.
   - `region`: `kr`(국내 탭) 또는 `world`(해외 탭), `order`: 목록 순서
   - `waypoints`: 들머리 → 중간 지점 → 끝 지점. `lat`/`lon`은 대략이어도 돼요.
     `"snap":"peak"`(봉우리)나 `"snap":"elev"`+`"elev"`(해발)를 주면 실제 지형에 맞춰 옮겨요.
   - `flag`: 정상 깃발 (`kr jp ch fr it cn tz us cl nz np`), `tz`: 시간대(해 뜨는 시각 계산), `cityLights`: 밤 도시 불빛
2. `python3 make_terrain.py <새id>` → 지점마다 `설정 / DEM` 해발이 출력돼요. `← 확인 필요`가 뜨면 좌표를 고쳐 다시 돌려요.
3. `python3 build_site.py --only <새id>` → `out/<새id>.html` 미리보기.
4. 배포는 승인 후 `python3 build_site.py --to-site` (저장소 루트에 index.html=북한산, 나머지 `<id>.html`).

## 템플릿이 바뀌면

`build_site.py`는 `/mnt/project-files/hiking-game/game.template.html`(또는 `--template`으로 준 파일)을 읽어
북한산에 묶인 글자·숫자만 바꿔 끼워요. 바꿀 자리를 못 찾으면 그 문구를 보여 주며 멈추니,
`patch_mountain()`의 해당 줄만 새 문구로 고치면 돼요. 북한산 페이지는 지형·문구를 그대로 두고 산 선택 화면만 더해요.

## 지금 한계 (다음 단계)

- 나무·풀·단풍은 모든 산이 북한산 가을 숲 그대로예요. 수목한계선 위(에베레스트·킬리만자로·마터호른·몽블랑 등)는
  설정에 `biome`을 두고 나무를 줄이고 눈·자갈 질감으로 바꾸는 작업이 필요해요 (사진 소스가 모이면 진행).
- 탐방로는 실제 GPS 길이 아니라 지점 사이를 경사 비용 A*로 이은 근사예요. GPX를 받으면 그대로 쓰도록 바꿀 수 있어요.
- 사진은 컨테이너에서 사진 사이트에 접속이 막혀 있어 직접 받지 못해요. PHOTOS.md 참고.
