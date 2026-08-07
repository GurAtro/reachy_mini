---
type: reference
id: R-daemon
---

# R-데몬과 연결

## 데몬이 먼저 떠 있어야 합니다
`reachy-mini-daemon`이 카메라·마이크·스피커·모터 하드웨어를 **소유**하고, SDK는 거기
붙는 클라이언트입니다. 데몬이 없으면 연결에 실패하고 앱은 조용히 mock으로 내려갑니다
→ [[ADR-003 연결 실패 시 mock 폴백]]

```
http://localhost:8000        대시보드가 뜨면 데몬 정상
http://localhost:8000/docs   API 문서 — SDK 파라미터명 확인용
```

- **Wireless**: 데몬이 로봇 안에서 자동 실행됩니다.
- **Lite**: PC에서 `reachy-mini-daemon`을 직접 띄우거나, Reachy Mini Control 데스크톱 앱이 대신 관리합니다.

Reachy Mini Control 앱과 대시보드 앱 등록은 **선택 사항**입니다. 이 프로젝트는 독립
스크립트라 데몬만 떠 있으면 `python main.py`로 실행됩니다.

## `media_backend` — 오디오 장치 충돌
데몬이 오디오 장치를 점유하기 때문에, 로봇을 켠 채 PC 마이크를 쓰면 충돌합니다.

| `audio.source` | `reachy.enabled` | `media_backend` |
|---|---|---|
| `local` | `false` | 무관 (연결하지 않음) |
| `local` | `true` | **`no_media`** — 데몬이 오디오/카메라를 놓아줍니다 |
| `reachy` | `true` | `default` |

`no_media`를 줘도 **모터 제어는 정상 동작**하고, 종료 시 하드웨어가 자동으로 데몬에
반환됩니다.

## SDK 주의
`reachy-mini`를 씁니다. **`reachy-sdk`는 대형 Reachy 2용이라 동작하지 않습니다.**

```bash
pip install reachy-mini
```

## 관련
- [[M-robot 로봇 제어]] · [[M-audio 오디오 입출력]]
- [[R-단계별 구동 절차]]
