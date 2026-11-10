# 능선 안드로이드 앱 (플레이 스토어) 출시 순서

능선 앱은 neungseon.com 을 그대로 여는 **TWA(신뢰할 수 있는 웹 활동)** 방식이에요.
사이트를 고쳐 배포하면 앱에도 바로 반영되고, 스토어 심사를 다시 받을 필요가 없어요.
앱 껍데기(AAB)를 다시 올리는 건 아이콘·이름·패키지 설정을 바꿀 때뿐이에요.

## 이미 사이트에 들어간 것
- `manifest.webmanifest`, `sw.js`, 아이콘(192·512): 앱으로 감쌀 조건
- `privacy.html`: 개인정보처리방침 (플레이 콘솔에 주소를 넣어야 해요)
- `pipeline/android_patch.py`: 앱으로 열렸을 때만 후원 버튼·‘앱으로 설치’ 안내를 숨겨요
  (플레이 결제 정책 때문. 웹사이트에서는 그대로 보여요)

## 1. 플레이 개발자 계정 (승연 님)
1. https://play.google.com/console 에서 개인 계정으로 가입, 등록비 25달러, 신분 확인
2. 개인 계정은 **테스터 12명이 14일 동안 비공개 테스트**를 해야 공개 출시를 신청할 수 있어요

## 2. 앱 파일 만들기 (PWABuilder)
1. https://www.pwabuilder.com 에 `https://neungseon.com` 입력 → Package For Stores → Android → Generate Package
2. Options 에서 아래처럼 맞춰요

| 항목 | 값 |
|---|---|
| Package ID | `com.neungseon.app` (출시 후 못 바꿔요) |
| App name | 능선 온라인 |
| Launcher name | 능선 |
| Version / Version code | 1.0.0 / 1 |
| Host | neungseon.com |
| Start URL | `/?src=twa` (앱인지 알아보는 표시. 꼭 이대로) |
| Display mode | fullscreen |
| Status bar / Nav bar / Splash color | `#1d2238` |
| Fallback behavior | Custom Tabs |
| Signing key | Create new |

3. 내려받은 zip 안의 파일
   - `*.aab`: 플레이 콘솔에 올릴 파일
   - `signing.keystore` + `signing-key-info.txt`: **업로드 키. 잃어버리면 업데이트가 어려워요.** 안전한 곳 두 군데에 보관하고, 저장소(GitHub)나 공유 폴더에는 절대 올리지 마세요.
   - `assetlinks.json`: 아래 3번에서 지문을 합쳐서 써요

## 3. 앱과 사이트 연결 (assetlinks.json)
연결이 안 되면 앱 위쪽에 주소창이 보여요.
1. 플레이 콘솔 → 앱 → 테스트 및 출시 → 설정 → **앱 서명** 에서 ‘앱 서명 키 인증서’의 **SHA-256** 값을 복사
2. Claude에게 그 값과 PWABuilder zip의 `assetlinks.json` 속 지문을 알려 주세요.
   두 지문을 함께 넣은 `.well-known/assetlinks.json` 을 사이트에 올려요.
   (지문은 비밀이 아니에요. 키스토어 파일과 비밀번호만 비밀이에요)

## 4. 플레이 콘솔에서 채울 것
- 스토어 등록정보: `store-listing.md` 초안
- 개인정보처리방침 URL: https://neungseon.com/privacy.html
- 앱 액세스: 로그인 없이 모든 기능 사용 가능 (구글 로그인은 선택)
- 광고: 없음
- 콘텐츠 등급 설문: 사용자끼리 채팅 가능(예), 신고 기능 있음
- 타겟 연령: 만 13세 이상 권장 (채팅이 있어서 어린이 대상으로 하면 심사가 까다로워요)
- 데이터 보안: 아래 표

| 데이터 | 수집 | 공유 | 용도 | 선택 여부 |
|---|---|---|---|---|
| 이메일 주소, 이름 | 예 | 아니요 | 계정 관리 | 선택 (구글 로그인 시) |
| 사용자 ID | 예 | 아니요 | 앱 기능 | 필수 |
| 기타 사용자 생성 콘텐츠 (채팅·방명록) | 예 | 아니요 | 앱 기능 | 선택 |
| 게임 진행 기록 | 예 | 아니요 | 앱 기능 | 선택 (구글 로그인 시) |
| 위치 | 아니요 (게임 속 좌표만, GPS 안 씀) | | | |
- 전송 중 암호화: 예 (HTTPS) · 삭제 요청 방법: 개인정보처리방침의 문의 주소

## 5. 테스트 때 꼭 볼 것
- 앱 위쪽에 주소창이 안 보이는지 (보이면 assetlinks 문제)
- 구글 로그인 창이 열리고 앱으로 돌아오는지 (TWA 안에서 팝업 로그인이 막히는 폰이 있으면 알려 주세요)
- 후원 버튼이 안 보이는지
- 저사양 폰에서 화질 자동 조절이 잘 되는지, 발열
