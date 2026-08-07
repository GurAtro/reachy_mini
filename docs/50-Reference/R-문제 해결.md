---
type: reference
id: R-troubleshooting
---

# R-문제 해결

| 증상 | 원인과 조치 | 관련 |
|---|---|---|
| `[Reachy] MOCK mode`로 내려감 | 데몬 미실행, 또는 `pip install reachy-mini` 누락 | [[R-데몬과 연결]] |
| 2단계에서 마이크가 안 잡힘 | 데몬이 오디오 점유 중 → `media_backend: "no_media"` | [[M-audio 오디오 입출력]] |
| 말 첫머리가 잘림 | 모션이 블로킹이라 녹음 시작이 늦음 → `motion_duration: 0.3` | [[T-003 비동기 모션]] |
| `[STT] CUDA unavailable` | CUDA 미설치. CPU로도 되지만 느립니다 | [[M-stt 음성 인식]] |
| 응답이 얕음 | `llm.claude.effort: "medium"` 이상으로 | [[M-llm 언어모델]] |
| 응답이 너무 길어 TTS가 지루함 | `llm.system_prompt`의 문장 수 지침 조정 | [[M-llm 언어모델]] |
| VRAM 부족 | `stt.model` 낮추기 → `stt.device: cpu` → TTS를 `edge`로 | [[R-VRAM 예산]] |
| 한글 로그가 깨짐 | `main.py`가 stdout을 UTF-8로 강제. 모듈 직접 실행 중이면 `PYTHONIOENCODING=utf-8` | [[M-main 대화 루프]] |
| 말이 자꾸 끊김 / 안 끝남 | `audio.silence_threshold`는 절대값이라 마이크 게인에 민감. 끊기면 올리고, 안 끝나면 내리기 | [[M-audio 오디오 입출력]] |
| 로봇이 앞 대화를 못 기억함 | 20턴에서 잘립니다 | [[M-conversation 대화 기록]] |

## 새 증상을 만나면
여기 한 줄 추가하고, 원인을 판단하는 데 쓴 로그는 그날의 작업 로그 노트(`40-Log/`)에
남기세요. 표는 결론만, 과정은 로그에.
