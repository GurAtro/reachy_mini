---
type: decision
id: ADR-001
status: accepted
date: 2026-08-07
affects:
  - "[[M-llm 언어모델]]"
  - "[[M-stt 음성 인식]]"
---

# ADR-001 LLM 기본값을 Claude API로

## 맥락
8 GB GPU 하나에 STT·LLM·TTS를 전부 얹어야 합니다. Windows 데스크톱이 1 GB 가까이
쓰므로 실사용 한도는 약 7 GB → [[R-VRAM 예산]]

## 선택지
| 안 | 장점 | 단점 |
|---|---|---|
| `ollama` 로컬 (~4.7 GB) | 오프라인, 비용 0 | VRAM의 2/3를 먹음. 한국어 품질 보통. 도구 호출 불안정 |
| `claude` API (0 GB) | VRAM 0, 한국어 우수, 도구 호출 안정적 | 인터넷 필요, API 비용 |

## 결정
`llm.backend: "claude"`를 기본값으로.

## 근거
**LLM이 GPU를 안 쓰면 그 자리를 전부 Whisper에 줄 수 있습니다.** 이게 핵심입니다.

- Ollama + `small` = 5.4 GB → STT 품질이 한국어 하한선에 걸림
- Claude + `large-v3` + qwen 1.7B = 6.5 GB → 최고 품질 STT + 로컬 TTS가 동시에 가능

음성 비서에서 체감 품질을 가장 크게 좌우하는 건 STT입니다. 잘못 알아들으면 아무리
좋은 LLM도 엉뚱한 답을 합니다. 그래서 VRAM을 STT에 몰아주는 쪽을 골랐습니다.

## 결과와 대가
- 인터넷이 끊기면 동작하지 않습니다.
- 대화 내용이 API로 나갑니다. 완전 오프라인이 필요하면 `ollama` + `qwen` 조합으로 바꿔야 하는데, 이때는 VRAM 때문에 STT를 `small`로 낮춰야 합니다.
- **아직 실제로 검증되지 않은 결정입니다** → [[T-005 Claude API 실호출 검증]]

## 뒤집을 조건
- 로컬 한국어 모델이 3 GB 이하로 쓸 만해지면
- 또는 GPU가 12 GB 이상으로 올라가면 — 그때는 둘 다 로컬로 갈 수 있습니다

## 관련
- 같은 제약에서 나온 결정: [[ADR-002 TTS 기본값을 edge-tts로]]
