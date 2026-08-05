# Reachy Mini AI Assistant

Reachy Mini 로봇에 얹는 한국어 음성 비서. 말을 걸면 알아듣고, 답하고, PC를 조작합니다.
로봇이 없어도 **mock 모드**로 전체 흐름을 그대로 돌려볼 수 있습니다.

```
음성 → faster-whisper(STT) → LLM(+도구 호출) → edge-tts(TTS) → 음성
                                  ↕
                            로봇 모션 / PC 제어
```

## 빠른 시작

```bash
pip install -r requirements.txt
set ANTHROPIC_API_KEY=sk-ant-...     # Claude 백엔드를 쓸 때
python main.py
```

기본 설정은 **로봇 없이(mock) + PC 마이크 + Claude API + 한국어**입니다.
그대로 실행하면 로봇 동작은 콘솔에 `[Reachy] *nods*` 처럼 출력됩니다.

## 설정 (`config.yaml`)

### LLM 백엔드

| `llm.backend` | VRAM | 한국어 | 도구 호출 | 오프라인 |
|---|---|---|---|---|
| `claude` (기본) | **0 GB** | 우수 | 안정적 | ❌ |
| `ollama` | ~4.7 GB | 보통 | 불안정할 수 있음 | ✅ |

`claude`가 기본인 이유는 VRAM입니다. LLM이 GPU를 쓰지 않으면 그 자리를 전부
Whisper에 줄 수 있어서, 8 GB 카드에서 STT 품질을 크게 올릴 수 있습니다.

모델은 `llm.claude.model`에서 바꿉니다. 응답 속도와 비용이 더 중요하면
`claude-haiku-4-5`로 바꾸세요 — 지연시간이 눈에 띄게 줄어듭니다.

### TTS 백엔드

| `tts.backend` | VRAM | 목소리 복제 | 오프라인 |
|---|---|---|---|
| `edge` (기본) | **0 GB** | ❌ 프리셋만 | ❌ |
| `qwen` | 0.9 ~ 3.4 GB | ✅ 3초 참조 | ✅ |

`qwen`은 원하는 한국어 목소리를 직접 지정할 수 있고 인터넷 없이 동작합니다.
Base 모델로 음성 복제를 하려면 참조 오디오와 **정확한 전사문**이 둘 다 필요합니다.

```yaml
tts:
  backend: "qwen"
  qwen:
    model: "Qwen/Qwen3-TTS-12Hz-0.6B-Base"   # 1.7B-Base는 품질 우선
    ref_audio: "voice/reachy.wav"             # 3초 이상 한국어 음성
    ref_text: "안녕하세요, 리치입니다."          # 위 파일에서 실제로 말하는 내용
```

별도 설치가 필요합니다: `pip install -U qwen-tts` (torch를 함께 받습니다)

> Ampere 이전 GPU(GTX 10/16 시리즈 등)는 bfloat16을 지원하지 않습니다.
> `dtype: "float16"`으로 바꾸세요.

### VRAM 예산 (8 GB 기준)

| 구성 | Whisper | LLM | TTS | 합계 |
|---|---|---|---|---|
| Claude + `small` + edge | 0.7 | 0 | 0 | **0.7 GB** |
| Claude + `medium` + qwen 0.6B | 1.6 | 0 | 0.9 | **2.5 GB** |
| Claude + `medium` + qwen 1.7B | 1.6 | 0 | 3.4 | **5.0 GB** |
| Claude + `large-v3` + qwen 1.7B | 3.1 | 0 | 3.4 | **6.5 GB** |
| Ollama + `small` + edge | 0.7 | 4.7 | 0 | **5.4 GB** |

Windows 데스크톱이 1 GB 가까이 쓰므로 8 GB 카드의 실사용 한도는 약 7 GB입니다.
Ollama와 로컬 TTS를 동시에 쓰긴 어렵습니다 — 둘 중 하나는 API/CPU로 내리세요.

### 오디오 입출력

| `audio.source` | 설명 |
|---|---|
| `local` (기본) | 이 PC의 마이크와 스피커. 로봇 없이 개발할 때 |
| `reachy` | 로봇의 4-mic 어레이와 스피커. `reachy.enabled: true` 필요 |

### 로봇

`reachy.enabled: false`가 기본(mock)입니다. 실기에 연결하려면 `true`로 바꾸고
`pip install reachy-mini`가 되어 있어야 합니다.

> 이 프로젝트는 **`reachy-mini`** SDK를 씁니다. `reachy-sdk`는 대형 Reachy 2용이라
> Reachy Mini에서는 동작하지 않습니다.

#### 데몬이 먼저 떠 있어야 합니다

`reachy-mini-daemon`이 카메라·마이크·스피커·모터 하드웨어를 소유하고, SDK는 거기
붙는 클라이언트입니다. 데몬이 없으면 연결에 실패하고 이 앱은 조용히 mock 모드로
내려갑니다 — 로그에 `[Reachy] Connected.`가 찍히는지 확인하세요.

```
http://localhost:8000        대시보드가 뜨면 데몬 정상
http://localhost:8000/docs   API 문서
```

- **Wireless**: 데몬이 로봇 안에서 자동 실행됩니다.
- **Lite**: PC에서 `reachy-mini-daemon`을 직접 띄우거나 Reachy Mini Control
  데스크톱 앱이 대신 관리합니다.

Reachy Mini Control 데스크톱 앱과 대시보드 앱 등록은 **선택 사항**입니다.
이 프로젝트는 독립 스크립트라 데몬만 떠 있으면 `python main.py`로 실행됩니다.

#### `media_backend` — 오디오 장치 충돌 주의

데몬이 오디오 장치를 점유하기 때문에, 로봇을 켠 채 PC 마이크를 쓰면 충돌할 수
있습니다. 조합에 맞춰 설정하세요.

| `audio.source` | `reachy.enabled` | `media_backend` |
|---|---|---|
| `local` | `false` | 무관 (연결하지 않음) |
| `local` | `true` | **`no_media`** — 데몬이 오디오/카메라를 놓아줍니다 |
| `reachy` | `true` | `default` |

`no_media`를 줘도 모터 제어는 정상 동작하고, 종료 시 하드웨어가 자동으로
데몬에 반환됩니다.

## 음성 명령

```
"유튜브 열어줘"              "유튜브에서 로파이 음악 찾아줘"
"C드라이브 남은 용량 알려줘"    "CPU 사용률 어때?"
"메모장 열어줘"              "스크린샷 찍어줘"
"초기화" / "리셋"            대화 기록 삭제
"종료" / "그만"              프로그램 종료
```

## 구조

```
main.py                 대화 루프
config.yaml             모든 설정
core/
  audio.py              오디오 소스 추상화 (LocalAudio / ReachyAudio) + VAD 녹음
  stt.py                faster-whisper 전사 (CUDA 자동 감지)
  tts.py                TTS 백엔드 선택 + 재생
  tts_edge.py           edge-tts → PCM, pyttsx3 폴백
  tts_qwen.py           Qwen3-TTS 로컬 + 3초 음성 복제
  llm.py                LLM 백엔드 선택
  llm_claude.py         Claude API + 도구 루프 + 프롬프트 캐싱
  llm_ollama.py         Ollama + 도구 루프
  conversation.py       대화 기록
reachy/
  robot.py              Reachy Mini 래퍼 + 모션 프리미티브 + mock 모드
tools/
  registry.py           도구 정의 (Ollama/Anthropic 두 형식) + 디스패치
  pc_control.py         PC 제어 구현
```

## 알려진 제약

- 로봇 모션이 아직 LLM 도구로 노출되지 않았습니다. 감정 표현은 대화 흐름에
  따라 고정 안무로만 재생됩니다(듣기 → 말하기 → 끄덕임).
- 머리 자세는 상하 이동(`z`)만 사용합니다. 실제 pitch/roll 회전은 설치된 SDK에서
  파라미터명을 확인한 뒤 `reachy/robot.py`의 `_head()`에 추가하세요.
- 에코 캔슬레이션과 말 끊기(barge-in)가 없습니다. 말하는 동안에는 듣지 않습니다.
- edge-tts는 인터넷이 필요하고 텍스트가 Microsoft 서버로 전송됩니다.
  완전 오프라인이 필요하면 pyttsx3 폴백만 쓰거나 로컬 TTS로 교체하세요.
