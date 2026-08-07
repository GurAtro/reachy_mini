---
type: module
id: M-conversation
files:
  - core/conversation.py
status: stable
---

# M-conversation 대화 기록

## 역할
주고받은 메시지를 순서대로 들고 있다가 LLM에 넘길 형태로 내보냅니다. 29줄짜리
가장 작은 모듈이지만, 로봇이 "무엇을 기억하는가"를 혼자 결정합니다.

## 핵심 진입점
| 함수 | 하는 일 |
|---|---|
| `ConversationManager(max_turns=20)` | 기본 20턴 |
| `add_user(text)` / `add_assistant(text)` | 추가 후 `_trim()` |
| `get_messages()` | LLM에 넘길 리스트 |
| `_trim()` | 오래된 턴부터 버림 |
| `clear()` | 전체 삭제. 음성 명령 "초기화"/"리셋"이 여기로 |

## 주의사항
- **20턴을 넘어가면 앞의 맥락은 사라집니다.** 사용자는 로봇이 "까먹었다"고 느끼지만 로그에는 아무 표시도 남지 않습니다.
- 기록은 메모리에만 있습니다. 프로그램을 끄면 사라집니다.
- `max_turns`를 늘리면 [[M-llm 언어모델]]의 입력 토큰이 함께 늘어납니다. 프롬프트 캐싱은 시스템 프롬프트/도구 정의에만 걸리고 대화 기록에는 그대로 비용이 붙습니다.

## 관련
- 소비자: [[M-llm 언어모델]]
- 초기화 명령 처리: [[M-main 대화 루프]]

## 이 모듈에 걸린 작업
```dataview
TABLE status AS 상태, priority AS 우선순위
FROM "20-Tasks"
WHERE contains(string(area), "M-conversation")
SORT status ASC
```
