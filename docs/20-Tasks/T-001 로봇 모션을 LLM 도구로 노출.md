---
type: task
id: T-001
status: todo
priority: P1
area:
  - "[[M-robot 로봇 제어]]"
  - "[[M-tools 도구 레지스트리]]"
files:
  - reachy/robot.py
  - tools/registry.py
created: 2026-08-07
updated: 2026-08-07
commits: []
---

# T-001 로봇 모션을 LLM 도구로 노출

## 왜 하는가
`shake`, `happy`, `confused`가 [[M-robot 로봇 제어]]에 이미 구현돼 있는데 아무도 부르지
않습니다. 도구로 노출하면 모델이 상황에 맞춰 감정을 표현합니다. 코드량 대비 체감
변화가 가장 큰 작업입니다.

## 무엇을 바꾸는가
[[M-tools 도구 레지스트리]]의 세 곳을 함께 고쳐야 합니다.

1. `tools/registry.py` — `TOOLS`에 스키마 추가 (`ANTHROPIC_TOOLS`는 자동 파생)
2. `tools/registry.py` — `_TOOL_MAP`에 이름 → 함수 등록
3. 로봇 인스턴스 접근 경로 — `pc_control.py`의 도구들은 전역 함수라 `Robot` 객체를
   모릅니다. 여기서 설계 판단이 필요합니다.

### 짚어야 할 설계 문제
`execute_tool(name, args)`는 인자로 dict만 받습니다. 로봇 핸들을 어떻게 넘길지:
- (a) 모듈 전역에 `Robot`을 주입 (`registry.set_robot(robot)`) — 간단하지만 전역 상태
- (b) `execute_tool(name, args, robot=None)`으로 시그니처 확장 — 호출자 [[M-llm 언어모델]] 양쪽(claude/ollama) 모두 수정
- (c) 도구를 클래스로 감싸기 — 가장 깨끗하지만 변경 범위가 큼

(a)로 시작하고 도구가 늘면 (c)로 옮기는 게 현실적입니다.

### 도구 후보
| 도구 이름 | 매핑 | 설명(모델이 읽는 문장) |
|---|---|---|
| `express_emotion` | `happy` / `confused` / `nod` / `shake` | 하나의 도구에 enum 파라미터 — 도구 수를 늘리지 않는 쪽 |

도구를 4개로 쪼개는 것보다 `emotion` enum 하나가 낫습니다. 도구 정의는 매 요청의
입력 토큰이고, 프롬프트 캐싱이 걸려도 정의가 늘면 캐시 갱신 비용이 붙습니다.

## 완료 조건
- [ ] `TOOLS`에 감정 표현 도구 추가
- [ ] `_TOOL_MAP` 등록, `execute_tool`로 실제 모션 호출됨
- [ ] mock 모드에서 `[Reachy] *happy*` 류가 콘솔에 찍힘
- [ ] 시스템 프롬프트에 "감정 표현은 말로 설명하지 말고 도구로" 지침 추가

## 검증 방법
mock 모드(`reachy.enabled: false`)로 충분합니다. "좋은 소식이야, 나 시험 붙었어"
같은 발화에 모델이 `express_emotion(happy)`를 부르는지 콘솔에서 확인.

## 진행 기록
<!-- 날짜 - 무엇을 했고 무엇을 알게 됐는지 -->

## 관련
- 영역: [[M-robot 로봇 제어]], [[M-tools 도구 레지스트리]]
- 블로킹 모션 문제와 함께 보면 좋음: [[T-003 비동기 모션]]
