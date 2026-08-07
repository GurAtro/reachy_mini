---
type: decision
id: ADR-002
status: accepted
date: 2026-08-07
affects:
  - "[[M-tts 음성 합성]]"
---

# ADR-002 TTS 기본값을 edge-tts로

## 맥락
[[ADR-001 LLM 기본값을 Claude API로]]와 같은 VRAM 예산 문제. 그리고 "설치하자마자
소리가 나야 한다"는 첫 실행 경험.

## 선택지
| 안 | VRAM | 목소리 복제 | 오프라인 | 추가 설치 |
|---|---|---|---|---|
| `edge` (edge-tts) | 0 GB | ❌ 프리셋만 | ❌ | 없음 |
| `qwen` (Qwen3-TTS) | 0.9 ~ 3.4 GB | ✅ 3초 참조 | ✅ | `pip install -U qwen-tts` (torch 동반) |

## 결정
`tts.backend: "edge"`를 기본값으로. `qwen`은 선택.

## 근거
- **첫 실행 장벽**: `qwen`이 기본이면 `requirements.txt`만으로 소리가 안 납니다. torch를 받는 동안 사람은 이게 고장인지 설치인지 모릅니다.
- **VRAM**: 0 GB라 STT를 `medium`이나 `large-v3`로 올릴 여유가 생깁니다.
- edge-tts의 한국어 품질이 실제로 좋습니다. `ko-KR-SunHiNeural`이 기본.

## 결과와 대가
- **텍스트가 Microsoft 서버로 전송됩니다.** 로봇이 하는 말은 집 안 대화의 응답이므로, 프라이버시가 걸리면 `qwen`으로 바꿔야 합니다. 이 사실을 README와 [[M-tts 음성 합성]]에 명시했습니다.
- 인터넷 의존이 하나 더 늘었습니다. 다만 [[ADR-001 LLM 기본값을 Claude API로]] 때문에 어차피 온라인이 전제라 새로운 제약은 아닙니다.
- 목소리를 고를 수 없습니다. 프리셋 두 개뿐입니다.
- edge-tts 실패 시 `pyttsx3` 폴백이 있어 최소한 소리는 납니다 (품질은 크게 떨어집니다).

## 뒤집을 조건
- 오프라인이 요구사항이 되면 즉시 `qwen`으로. 이때 VRAM 재배분이 필요합니다 → [[R-VRAM 예산]]
- 특정 목소리를 원하면 `qwen` + `ref_audio`/`ref_text`

## 관련
- [[M-tts 음성 합성]]
