---
type: module
id: M-llm
files:
  - core/llm.py
  - core/llm_claude.py
  - core/llm_ollama.py
status: unverified
---

# M-llm 언어모델

> [!warning] Claude API 실제 호출은 아직 검증되지 않았습니다
> 요청 형태는 문서 기준으로 작성했고 구조 검증만 끝난 상태입니다.
> → [[T-005 Claude API 실호출 검증]]

## 역할
대화 기록을 받아 답변 텍스트를 돌려줍니다. 중간에 도구 호출이 끼면 루프를 돌며
[[M-tools 도구 레지스트리]]를 실행하고 결과를 다시 모델에 넣습니다.

## 핵심 진입점
| 함수 / 클래스 | 하는 일 |
|---|---|
| `create_llm(config)` | `llm.backend`에 따라 `ClaudeLLM` 또는 `OllamaLLM` |
| `ClaudeLLM._create(messages)` | 실제 API 요청 구성 (프롬프트 캐싱 포함) |
| `ClaudeLLM._text_of(response)` | 응답 블록에서 텍스트만 추출 |
| `ClaudeLLM._log_usage(response)` | `[LLM] tokens in=... cached=...` 로그 |
| `ClaudeLLM.chat(history)` / `OllamaLLM.chat(history)` | 도구 루프 포함한 한 턴 |

## 설정 (`config.yaml`)
| 키 | 의미 |
|---|---|
| `llm.backend` | `claude` (기본) / `ollama` |
| `llm.max_tool_iterations` | 도구 연쇄 상한. 기본 5 — 폭주 방지 |
| `llm.claude.model` | 기본 `claude-opus-5`. 지연시간이 중요하면 `claude-haiku-4-5` |
| `llm.claude.effort` | `low`(기본) ~ `max`. 답이 얕으면 `medium` 이상 |
| `llm.claude.max_tokens` | 8192 |
| `llm.ollama.model` | 기본 `exaone3.5:7.8b` |
| `llm.system_prompt` | 말투·분량·도구 사용 지침. **음성으로 읽히는 걸 전제**로 씁니다 |

API 키는 환경변수 `ANTHROPIC_API_KEY`에서 읽습니다. `config.yaml`에 넣지 마세요 —
이 저장소는 public입니다.

## 주의사항
- **프롬프트 캐싱이 걸렸는지 확인하는 법**: 두 번째 턴부터 로그의 `cached=`가 올라갑니다. 시스템 프롬프트와 도구 정의가 캐시에서 읽히면 입력 비용이 크게 줍니다.
- Ollama 백엔드는 도구 호출이 불안정할 수 있습니다. 오프라인이 꼭 필요할 때만.
- 답이 너무 길면 모델 문제가 아니라 `llm.system_prompt`의 문장 수 지침 문제입니다.

## 관련
- 도구: [[M-tools 도구 레지스트리]]
- 기록 관리: [[M-conversation 대화 기록]]
- 왜 Claude가 기본인가: [[ADR-001 LLM 기본값을 Claude API로]]

## 이 모듈에 걸린 작업
```dataview
TABLE status AS 상태, priority AS 우선순위
FROM "20-Tasks"
WHERE contains(string(area), "M-llm")
SORT status ASC
```
