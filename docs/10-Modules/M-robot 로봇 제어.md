---
type: module
id: M-robot
files:
  - reachy/robot.py
status: wip
---

# M-robot 로봇 제어

## 역할
`reachy-mini` SDK를 감싸고, 하드웨어가 없으면 **mock 모드**로 같은 API를 콘솔 출력으로
대신합니다. 위쪽 코드는 로봇이 있는지 없는지 몰라도 됩니다.

> `reachy-mini` SDK를 씁니다. `reachy-sdk`는 대형 Reachy 2용이라 여기서 동작하지 않습니다.

## 핵심 진입점
| 함수 | 하는 일 |
|---|---|
| `Robot(config)` | 설정 보관 후 `_connect()` 시도 |
| `_connect()` | 실패하면 조용히 mock으로 강등. `[Reachy] Connected.` 로그를 확인하세요 |
| `connected` / `media` | 연결 상태와 미디어 핸들 |
| `_head(z_mm)` / `_goto(z_mm, antennas_deg, yaw_deg, duration)` | 저수준 포즈 |
| `idle` / `listening` / `speaking` | 상태 표현 포즈 |
| `nod` / `shake` / `happy` / `confused` | 감정 모션 프리미티브 |
| `disconnect()` | 하드웨어를 데몬에 반환 |

## 설정 (`config.yaml`)
| 키 | 의미 |
|---|---|
| `reachy.enabled` | `false`가 기본(mock) |
| `reachy.connection_mode` | `auto` / `localhost_only` / `network` |
| `reachy.media_backend` | `default` / `local` / `webrtc` / `no_media` → [[R-데몬과 연결]] |
| `reachy.motion_duration` | 모션 1회 소요(초). 기본 0.6 |
| `reachy.head_tracking` | 듣는 동안 가까운 얼굴 추적 |

## 주의사항
- **`shake`, `happy`, `confused`는 구현돼 있지만 아무도 호출하지 않습니다.** 도구로 노출하면 체감 변화가 가장 큽니다 → [[T-001 로봇 모션을 LLM 도구로 노출]]
- **`_head()`는 상하 이동(z)만 씁니다.** pitch/roll은 미사용 → [[T-002 머리 pitch roll 추가]]
- **모션이 블로킹입니다.** 말 첫머리가 잘리면 `motion_duration: 0.3`으로 줄이거나 → [[T-003 비동기 모션]]
- 연결 실패가 조용하다는 점을 기억하세요. mock으로 내려가도 앱은 정상 동작하는 것처럼 보입니다 → [[ADR-003 연결 실패 시 mock 폴백]]

## 관련
- 도구 노출 대상: [[M-tools 도구 레지스트리]]
- 호출 지점: [[M-main 대화 루프]]

## 이 모듈에 걸린 작업
```dataview
TABLE status AS 상태, priority AS 우선순위
FROM "20-Tasks"
WHERE contains(string(area), "M-robot")
SORT status ASC
```
