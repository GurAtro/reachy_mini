---
type: module
id: M-stt
files:
  - core/stt.py
status: stable
---

# M-stt 음성 인식

## 역할
녹음된 발화를 faster-whisper로 한국어 텍스트로 바꿉니다. CUDA를 자동 감지하고
없으면 CPU로 내려갑니다.

## 핵심 진입점
| 함수 / 클래스 | 하는 일 |
|---|---|
| `SpeechToText(config)` | 모델 로드. 시작 로그 `[STT] Ready on cuda` |
| `SpeechToText._load(name, device, compute_type)` | 실제 모델 적재. 디바이스 폴백 담당 |
| `transcribe(audio, samplerate)` | 텍스트 반환, 빈 발화면 `None` |

## 설정 (`config.yaml`)
| 키 | 의미 |
|---|---|
| `stt.model` | `tiny`/`base`/`small`/`medium`/`large-v3`. 한국어는 최소 `small` |
| `stt.language` | `ko` |
| `stt.device` | `auto` / `cpu` / `cuda` |
| `stt.compute_type` | `auto` / `int8` / `int8_float16` / `float16` |
| `stt.beam_size` | 기본 5 |

## 주의사항
- **`[STT] Ready on cpu`가 뜨면 CUDA가 없는 것입니다.** 동작은 하지만 느립니다.
- VRAM이 이 프로젝트에서 가장 빡빡한 자원입니다. LLM을 API로 돌리는 이유가 여기 있습니다 → [[ADR-001 LLM 기본값을 Claude API로]]
- 모델별 VRAM은 [[R-VRAM 예산]] 참고.
- 첫 턴이 느린 건 모델 로딩 때문입니다. 정상입니다.

## 관련
- 이전 단계: [[M-audio 오디오 입출력]]
- 다음 단계: [[M-llm 언어모델]]

## 이 모듈에 걸린 작업
```dataview
TABLE status AS 상태, priority AS 우선순위
FROM "20-Tasks"
WHERE contains(string(area), "M-stt")
SORT status ASC
```
