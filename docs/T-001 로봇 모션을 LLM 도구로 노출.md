---
status: todo
priority: P1
files:
  - tools/registry.py
  - reachy/robot.py
---

# T-001 로봇 모션을 LLM 도구로 노출

`reachy/robot.py`에 `shake`, `happy`, `confused`가 구현돼 있는데 **아무도 호출하지
않습니다.** 도구로 노출하면 모델이 상황에 맞춰 감정을 표현합니다. 코드량 대비 체감
변화가 가장 큰 작업입니다.

## 무엇을 바꾸나

`tools/registry.py` 세 곳:

1. `TOOLS`에 스키마 추가 (`ANTHROPIC_TOOLS`는 여기서 자동 파생)
2. `_TOOL_MAP`에 이름 → 함수 등록
3. `llm.system_prompt`에 "감정 표현은 말로 설명하지 말고 도구로" 지침

도구는 **하나에 enum 파라미터**로 묶는 게 낫습니다. 4개로 쪼개면 도구 정의가 늘고,
정의는 매 요청의 입력 토큰입니다.

```
express_emotion(emotion: "happy" | "confused" | "nod" | "shake")
```

## 진짜 난관 — 로봇 핸들을 넘길 경로가 없다

`execute_tool(name, args)`는 dict만 받습니다. `pc_control.py`의 도구들은 전역 함수라
`Robot` 객체를 모릅니다.

| 안 | 평가 |
|---|---|
| (a) 모듈 전역에 주입 — `registry.set_robot(robot)` | 간단. 전역 상태가 생김 |
| (b) `execute_tool(name, args, robot=None)` | 호출자(`llm_claude.py`, `llm_ollama.py`) 양쪽 수정 |
| (c) 도구를 클래스로 감싸기 | 가장 깨끗. 변경 범위가 큼 |

(a)로 시작하고 도구가 늘면 (c)로 옮기는 게 현실적입니다.

## 완료 조건

- [ ] `TOOLS` + `_TOOL_MAP` 등록
- [ ] mock 모드에서 `[Reachy] *happy*` 류가 콘솔에 찍힘
- [ ] "좋은 소식이야" 같은 발화에 모델이 실제로 도구를 부름

## 참고

모션이 블로킹이라 감정 모션을 넣으면 대화가 더 끊깁니다 → [[T-003 비동기 모션]]과
함께 보세요.
