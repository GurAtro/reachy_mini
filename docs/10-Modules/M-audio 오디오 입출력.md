---
type: module
id: M-audio
files:
  - core/audio.py
status: stable
---

# M-audio 오디오 입출력

## 역할
마이크와 스피커를 한 인터페이스 뒤로 감춥니다. PC 장치든 로봇의 4-mic 어레이든
위쪽 코드는 같은 방식으로 씁니다. 발화 단위 녹음(VAD)도 여기 있습니다.

## 핵심 진입점
| 함수 / 클래스 | 하는 일 |
|---|---|
| `AudioSource` (ABC) | `start / stop / read / play` 네 개짜리 계약 |
| `LocalAudio` | 이 PC의 마이크·스피커 |
| `ReachyAudio` | 로봇의 마이크 어레이·스피커. `speech_detected()` 추가 제공 |
| `create_audio_source(config, robot)` | `audio.source` 설정에 따라 둘 중 하나를 만듦 |
| `record_utterance(source, config)` | 침묵이 이어질 때까지 녹음해서 하나의 발화로 반환 |
| `_resample(samples, src, dst)` | 샘플레이트 변환 (로봇 장치와 Whisper의 16 kHz를 맞춤) |

## 설정 (`config.yaml`)
| 키 | 의미 |
|---|---|
| `audio.source` | `local` / `reachy` |
| `audio.sample_rate` | 16000 — Whisper 입력 규격 |
| `audio.silence_threshold` | int16 평균 진폭. 이 아래면 침묵으로 셈 |
| `audio.silence_duration` | 발화를 끝낼 침묵 길이(초). 기본 1.2 |
| `audio.max_record_seconds` | 한 발화 상한. 기본 30 |
| `audio.idle_timeout` | 이만큼 조용하면 대기 포기. 0이면 무한 대기 |

## 주의사항
- **데몬이 오디오 장치를 점유합니다.** `reachy.enabled: true`인데 PC 마이크를 쓰려면 `reachy.media_backend: "no_media"`가 필요합니다. 안 그러면 마이크가 잡히지 않습니다 → [[R-데몬과 연결]]
- `silence_threshold`는 절대값이라 마이크 게인에 민감합니다. 말이 자꾸 끊기면 올리고, 안 끝나면 내리세요.

## 관련
- 다음 단계: [[M-stt 음성 인식]]
- 재생 대상: [[M-tts 음성 합성]]
- 장치 충돌: [[R-데몬과 연결]]

## 이 모듈에 걸린 작업
```dataview
TABLE status AS 상태, priority AS 우선순위
FROM "20-Tasks"
WHERE contains(string(area), "M-audio")
SORT status ASC
```
