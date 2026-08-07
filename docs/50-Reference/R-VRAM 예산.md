---
type: reference
id: R-vram
---

# R-VRAM 예산

8 GB 카드 기준. Windows 데스크톱이 1 GB 가까이 쓰므로 **실사용 한도는 약 7 GB**입니다.

| 구성 | Whisper | LLM | TTS | 합계 |
|---|---|---|---|---|
| Claude + `small` + edge | 0.7 | 0 | 0 | **0.7 GB** |
| Claude + `medium` + qwen 0.6B | 1.6 | 0 | 0.9 | **2.5 GB** |
| Claude + `medium` + qwen 1.7B | 1.6 | 0 | 3.4 | **5.0 GB** |
| Claude + `large-v3` + qwen 1.7B | 3.1 | 0 | 3.4 | **6.5 GB** |
| Ollama + `small` + edge | 0.7 | 4.7 | 0 | **5.4 GB** |

## 읽는 법
- **Ollama와 로컬 TTS는 동시에 못 씁니다.** 둘 중 하나는 API나 CPU로 내려야 합니다.
- LLM을 API로 돌리면 그 자리가 전부 Whisper 몫이 됩니다 → [[ADR-001 LLM 기본값을 Claude API로]]
- 한국어 STT는 `small`이 하한선입니다. `medium`이 눈에 띄게 낫습니다.

## VRAM이 모자랄 때 내리는 순서
1. `stt.model`을 한 단계 낮춤
2. `tts.backend: "edge"` (0 GB)
3. `stt.device: "cpu"` — 느려지지만 VRAM은 0

## 관련
- [[M-stt 음성 인식]] · [[M-tts 음성 합성]] · [[M-llm 언어모델]]
- [[ADR-002 TTS 기본값을 edge-tts로]]
