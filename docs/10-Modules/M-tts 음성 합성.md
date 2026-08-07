---
type: module
id: M-tts
files:
  - core/tts.py
  - core/tts_edge.py
  - core/tts_qwen.py
status: stable
---

# M-tts 음성 합성

## 역할
텍스트를 PCM으로 만들고 [[M-audio 오디오 입출력]]으로 재생합니다. 백엔드는 둘입니다 —
클라우드(edge-tts)와 로컬(Qwen3-TTS).

## 핵심 진입점
| 함수 / 클래스 | 하는 일 |
|---|---|
| `TTSBackend` (ABC) | `synthesize(text) -> (samples, rate) \| None` |
| `create_tts(config)` | `tts.backend`에 따라 백엔드 선택 |
| `TTSBackend.speak(text, audio_source)` | 합성 + 재생 |
| `to_mono_float32(data)` | 채널/타입 정규화 |
| `EdgeTTS` | edge-tts → PCM. **실패 시 pyttsx3로 폴백** (`_synth_pyttsx3`) |
| `QwenTTS` | 로컬 모델. 3초 참조 음성으로 목소리 복제 |

## 설정 (`config.yaml`)
| 키 | 의미 |
|---|---|
| `tts.backend` | `edge` (기본) / `qwen` |
| `tts.edge.voice` | `ko-KR-SunHiNeural`(여) / `ko-KR-InJoonNeural`(남) |
| `tts.edge.speed` | `+0%` 형식 |
| `tts.qwen.model` | `0.6B-Base` ~0.9 GB / `1.7B-Base` ~3.4 GB |
| `tts.qwen.ref_audio` + `ref_text` | 목소리 복제. **둘 다 있어야** 동작 |
| `tts.qwen.dtype` | Ampere 이전 GPU(GTX 10/16)는 `float16` |

## 주의사항
- **edge-tts는 텍스트를 Microsoft 서버로 보냅니다.** 집 안 대화가 나가는 게 신경 쓰이면 `qwen`으로. 완전 오프라인은 `llm.backend: ollama`까지 함께 바꿔야 합니다.
- **음성 복제에는 정확한 전사문이 필요합니다.** `ref_text`가 실제 발화와 다르면 품질이 무너집니다.
- `qwen`은 별도 설치: `pip install -U qwen-tts` (torch 동반)
- 0.6B가 부족해서 1.7B로 올렸는데도 아쉽다면 그건 VRAM 한계입니다 → [[R-VRAM 예산]]

## 관련
- 왜 edge가 기본인가: [[ADR-002 TTS 기본값을 edge-tts로]]
- 재생 경로: [[M-audio 오디오 입출력]]

## 이 모듈에 걸린 작업
```dataview
TABLE status AS 상태, priority AS 우선순위
FROM "20-Tasks"
WHERE contains(string(area), "M-tts")
SORT status ASC
```
