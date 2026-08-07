---
type: task
id: T-005
status: todo
priority: P0
area: "[[M-llm 언어모델]]"
files:
  - core/llm_claude.py
created: 2026-08-07
updated: 2026-08-07
commits: []
---

# T-005 Claude API 실호출 검증

> [!danger] 기본 백엔드인데 한 번도 실제로 불러본 적이 없습니다
> 요청 형태는 문서 기준으로 작성했고 구조 검증만 마쳤습니다. 다른 어떤 작업보다
> 먼저 확인해야 합니다 — 여기가 깨져 있으면 나머지 전부가 mock 위의 추측입니다.

## 왜 하는가
`llm.backend: claude`가 기본값입니다. 처음 실행하는 사람이 가장 먼저 부딪히는 지점인데
검증되지 않았습니다.

## 확인할 것
| 항목 | 어떻게 확인 |
|---|---|
| 인증 | `ANTHROPIC_API_KEY` 환경변수로 요청이 통과하는가 |
| 기본 응답 | 한국어 한 문장이 정상으로 돌아오는가 |
| `effort` 파라미터 | `low`가 실제로 수용되는가. 거부되면 이름/위치 확인 |
| 도구 형식 | `ANTHROPIC_TOOLS`의 `input_schema` 구조를 API가 받는가 → [[M-tools 도구 레지스트리]] |
| 도구 루프 | 도구 결과를 되돌려준 뒤 최종 텍스트가 오는가 |
| `max_tool_iterations` | 5회 상한이 실제로 걸리는가 |
| 프롬프트 캐싱 | 2번째 턴부터 `[LLM] tokens in=... cached=` 의 `cached`가 0보다 큰가 |
| 응답 파싱 | `_text_of()`가 도구 블록이 섞인 응답에서 텍스트만 뽑는가 |

## 완료 조건
- [ ] 위 8개 항목 전부 확인, 결과를 이 노트에 기록
- [ ] 실패한 항목은 별도 작업 노트로 분리
- [ ] 검증 완료 후 [[M-llm 언어모델]]의 `status`를 `unverified` → `stable`로, README의 경고 문단 제거

## 검증 방법
로봇 없이 mock 모드로 전부 가능합니다 — [[R-단계별 구동 절차]]의 1단계.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python main.py
```

첫 발화로 "안녕"(도구 없는 경로), 그다음 "CPU 사용률 어때?"(도구 경로),
그다음 아무 말이나(캐싱 확인) 순서로 세 턴이면 대부분 드러납니다.

## 진행 기록
<!-- 검증 결과를 여기에. 실패했다면 에러 메시지 전문을 붙여 두세요. -->

## 관련
- 영역: [[M-llm 언어모델]]
- 근거가 된 결정: [[ADR-001 LLM 기본값을 Claude API로]]
