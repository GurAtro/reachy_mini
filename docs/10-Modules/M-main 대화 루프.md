---
type: module
id: M-main
files:
  - main.py
status: stable
---

# M-main 대화 루프

## 역할
전체 파이프라인을 순서대로 돌리는 단일 루프. 설정을 읽고, 각 모듈을 만들고,
"녹음 → 전사 → LLM → 발화"를 반복합니다.

```
record_utterance → SpeechToText.transcribe → LLM.chat → TTS.speak
                                ↕
                       [[M-robot 로봇 제어]] 모션
```

## 핵심 진입점
| 함수 | 하는 일 |
|---|---|
| `load_config(path)` | `config.yaml`을 통째로 dict으로 |
| `normalize(text)` | 소문자화 + 끝 문장부호 제거. 명령어 매칭용 |
| `main()` | 루프 본체 |

## 알아둘 것
- **stdout을 UTF-8로 강제합니다.** 한국어 Windows 콘솔이 cp949라 한글 로그가 깨지는 걸 막습니다. 모듈을 직접 실행할 때는 `PYTHONIOENCODING=utf-8`이 필요합니다.
- 종료어 `QUIT_WORDS`, 초기화어 `CLEAR_WORDS`가 여기 하드코딩되어 있습니다. LLM을 거치지 않고 문자열 매칭으로 처리합니다.
- 무거운 import는 `main()` 안에서 합니다 — 설정 오류가 있으면 모델 로딩 전에 죽게 하려는 의도입니다.

## 관련
- 파이프라인 상류: [[M-audio 오디오 입출력]] → [[M-stt 음성 인식]]
- 하류: [[M-llm 언어모델]] → [[M-tts 음성 합성]]
- 알려진 어색함: [[R-동작 특성]]

## 이 모듈에 걸린 작업
```dataview
TABLE status AS 상태, priority AS 우선순위
FROM "20-Tasks"
WHERE contains(string(area), "M-main")
SORT status ASC
```
