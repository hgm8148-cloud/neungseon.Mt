# 파이어베이스 데이터베이스 규칙 (채팅·방명록 추가판)

Firebase 콘솔 → neungseon-mt → Realtime Database → 규칙 탭에서 전부 지우고 아래를 통째로 붙여 넣은 뒤 **게시**를 눌러요.
`rooms`(함께 걷기·관리자 효과)와 `users`(구글 로그인 기록)는 지금 규칙 그대로이고, 아래 4가지가 새로 생겨요.

- `chat`: 산마다 채팅. 누구나 읽고, 쓰기는 자기 이름으로 새 글만(80자). 지우기는 쓴 사람·관리자, 하루 지난 글은 누구나(정리용).
- `chatlast`: 채팅을 2.5초에 한 번만 보내게 하는 시계.
- `guest`: 정상 방명록. 산마다 한 사람 한 장(60자, 색 0~4). 구글 로그인한 사람만 붙이고, 10초에 한 번만 고칠 수 있어요. 관리자는 지울 수 있어요.
- `flags`: 신고. 한 사람이 한 글에 한 번. 3명이 신고하면 게임에서 가려져요.

함께 가기 제안·수락과 바뀐 인삿말은 지금 쓰는 위치 신호(`rooms/…/peers`)에 실려 가서 규칙을 바꾸지 않아도 돼요.

```json
{
  "rules": {
    "rooms": {
      "$room": {
        ".read": "auth != null && $room.matches(/^[a-z0-9-]{1,30}$/)",
        "peers": {
          "$uid": {
            ".write": "auth != null && auth.uid === $uid",
            ".validate": "newData.val() === null || (newData.hasChildren(['n','x','z','t']) && newData.child('n').isString() && newData.child('n').val().length <= 12 && newData.child('x').isNumber() && newData.child('z').isNumber() && newData.child('t').val() === now)"
          }
        },
        "event": {
          ".write": "auth != null && auth.token.email === 'hgm8148@gmail.com' && auth.token.email_verified === true",
          ".validate": "newData.val() === null || (newData.child('t').isNumber() && (!newData.child('msg').exists() || newData.child('msg/text').val().length <= 40))"
        }
      }
    },
    "users": {
      "$uid": {
        ".read": "auth != null && auth.uid === $uid",
        ".write": "auth != null && auth.uid === $uid && auth.token.firebase.sign_in_provider === 'google.com'",
        ".validate": "newData.val() === null || (newData.child('t').val() === now && newData.child('nick').isString() && newData.child('nick').val().length <= 12)"
      }
    },
    "chat": {
      "$room": {
        ".read": "auth != null && $room.matches(/^[a-z0-9-]{1,30}$/)",
        ".indexOn": ["t"],
        "$id": {
          ".write": "auth != null && $room.matches(/^[a-z0-9-]{1,30}$/) && ((!data.exists() && newData.child('u').val() === auth.uid) || (!newData.exists() && (data.child('u').val() === auth.uid || data.child('t').val() < now - 86400000 || (auth.token.email === 'hgm8148@gmail.com' && auth.token.email_verified === true))))",
          ".validate": "newData.hasChildren(['u','n','x','t']) && newData.child('n').isString() && newData.child('n').val().length <= 12 && newData.child('x').isString() && newData.child('x').val().length >= 1 && newData.child('x').val().length <= 80 && newData.child('t').val() === now && newData.parent().parent().parent().child('chatlast').child(auth.uid).val() === now"
        }
      }
    },
    "chatlast": {
      "$uid": {
        ".write": "auth != null && auth.uid === $uid",
        ".validate": "newData.val() === now && (!data.exists() || data.val() < now - 2500)"
      }
    },
    "guest": {
      "$mt": {
        ".read": "auth != null && $mt.matches(/^[a-z0-9-]{1,30}$/)",
        ".indexOn": ["t"],
        "$uid": {
          ".write": "auth != null && $mt.matches(/^[a-z0-9-]{1,30}$/) && ((auth.uid === $uid && auth.token.firebase.sign_in_provider === 'google.com' && (!newData.exists() || !data.exists() || data.child('t').val() < now - 10000)) || (!newData.exists() && auth.token.email === 'hgm8148@gmail.com' && auth.token.email_verified === true))",
          ".validate": "newData.hasChildren(['n','x','c','t']) && newData.child('n').isString() && newData.child('n').val().length <= 12 && newData.child('x').isString() && newData.child('x').val().length >= 1 && newData.child('x').val().length <= 60 && newData.child('c').isNumber() && newData.child('c').val() >= 0 && newData.child('c').val() <= 4 && newData.child('t').val() === now"
        }
      }
    },
    "flags": {
      "$kind": {
        "$room": {
          ".read": "auth != null && ($kind === 'chat' || $kind === 'guest')",
          "$id": {
            "$uid": {
              ".write": "auth != null && auth.uid === $uid && ($kind === 'chat' || $kind === 'guest') && $room.matches(/^[a-z0-9-]{1,30}$/)",
              ".validate": "newData.val() === true"
            }
          }
        }
      }
    }
  }
}
```

## 채팅도 구글 로그인한 사람만 쓰게 하려면

1. 위 `chat` → `$id` → `.write` 안의 `(!data.exists() && newData.child('u').val() === auth.uid)`를
   `(!data.exists() && newData.child('u').val() === auth.uid && auth.token.firebase.sign_in_provider === 'google.com')`로 바꿔요.
2. `pipeline/social_patch.py`의 `LOGIN_CHAT = True`로 바꾸고 다시 빌드해요.

방명록도 누구나 쓰게 하려면 `guest`의 `auth.token.firebase.sign_in_provider === 'google.com' && `을 지우고 `LOGIN_GUEST = False`.

## 관리자

관리자 메일(hgm8148@gmail.com)은 이 규칙에만 들어가고 게임 코드에는 들어가지 않아요.
게임에서 관리자 모드를 켜면 채팅 줄이나 포스트잇을 눌러 **지우기 (관리자)** 를 고를 수 있어요.
