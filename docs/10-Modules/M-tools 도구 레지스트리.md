---
type: module
id: M-tools
files:
  - tools/registry.py
  - tools/pc_control.py
status: stable
---

# M-tools 도구 레지스트리

## 역할
LLM이 부를 수 있는 함수들의 정의와 실행. 스키마를 두 가지 형식(Ollama/OpenAI 방식,
Anthropic 방식)으로 내보냅니다.

## 핵심 진입점
| 함수 | 하는 일 |
|---|---|
| `TOOLS` | Ollama/OpenAI 형식 정의 (`{"type":"function","function":{...,"parameters":...}}`) |
| `to_anthropic_tools(tools)` / `ANTHROPIC_TOOLS` | 같은 도구를 Anthropic 형식으로 (`input_schema`, 최상위 필드) |
| `_TOOL_MAP` | 이름 → 실제 함수 |
| `execute_tool(name, args)` | 디스패치. 예외는 문자열로 감싸 모델에 돌려줌 |

## 등록된 도구 10개
| 이름 | 구현 (`tools/pc_control.py`) |
|---|---|
| `open_youtube` | 검색어가 있으면 검색 결과로 |
| `shutdown_pc` / `restart_pc` / `cancel_shutdown` | 기본 30초 지연 |
| `get_disk_space` | 드라이브 지정 |
| `get_system_info` | CPU/메모리 |
| `set_volume` | 0~100 |
| `open_application` | 앱 실행 |
| `take_screenshot` | 캡처 저장 |
| `list_running_processes` | 상위 N개 |

## 주의사항
- **새 도구를 추가하려면 세 곳을 고쳐야 합니다**: `pc_control.py`에 함수, `TOOLS`에 스키마, `_TOOL_MAP`에 등록. 하나라도 빠지면 `Unknown tool` 또는 조용한 미노출.
- `ANTHROPIC_TOOLS`는 모듈 로드 시점에 `TOOLS`에서 파생됩니다. `TOOLS`만 고치면 양쪽 다 반영됩니다.
- **되돌리기 어려운 도구**(`shutdown_pc`, `restart_pc`)는 시스템 프롬프트에서 "실행 전 확인"을 요구합니다. 모델 지시에만 의존하므로 코드 레벨 확인은 없습니다.
- 도구 연쇄는 `llm.max_tool_iterations`(기본 5)로 제한됩니다.

## 관련
- 호출자: [[M-llm 언어모델]]
- 노출 후보: [[M-robot 로봇 제어]]의 모션 → [[T-001 로봇 모션을 LLM 도구로 노출]]

## 이 모듈에 걸린 작업
```dataview
TABLE status AS 상태, priority AS 우선순위
FROM "20-Tasks"
WHERE contains(string(area), "M-tools")
SORT status ASC
```
