---
status: todo
priority: P0
files:
  - core/llm_claude.py
---

# T-005 Claude API 실호출 검증

`llm.backend: claude`가 기본값인데 **한 번도 실제로 불러본 적이 없습니다.** 요청 형태는
문서 기준으로 작성했고 구조 검증만 마친 상태입니다. 여기가 깨져 있으면 나머지 작업은
전부 추측 위에 올라갑니다.

## 확인할 것

- [ ] `ANTHROPIC_API_KEY` 환경변수로 인증이 통과하는가
- [ ] 한국어 한 문장이 정상으로 돌아오는가
- [ ] `llm.claude.effort: "low"`가 수용되는가 (거부되면 파라미터명·위치 확인)
- [ ] `ANTHROPIC_TOOLS`의 `input_schema` 구조를 API가 받는가
- [ ] 도구 결과를 되돌려준 뒤 최종 텍스트가 오는가
- [ ] `max_tool_iterations: 5` 상한이 실제로 걸리는가
- [ ] 2번째 턴부터 `[LLM] tokens in=... cached=` 의 `cached`가 0보다 큰가
- [ ] `_text_of()`가 도구 블록 섞인 응답에서 텍스트만 뽑는가

## 어떻게

로봇 없이 mock 모드로 전부 됩니다.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python main.py
```

세 턴이면 대부분 드러납니다.

| 발화 | 확인되는 것 |
|---|---|
| "안녕" | 인증, 기본 응답, 파싱 |
| "CPU 사용률 어때?" | 도구 스키마, 도구 루프 |
| 아무 말 | 프롬프트 캐싱 |

## 끝나면

- `README.md`의 "⚠️ Claude API 실제 호출은 아직 한 번도 검증되지 않았습니다" 문단 제거
- 실패한 항목이 있으면 별도 노트로 분리

## 결과
<!-- 확인한 내용을 여기에. 실패했다면 에러 메시지 전문을 붙여 두세요. -->
