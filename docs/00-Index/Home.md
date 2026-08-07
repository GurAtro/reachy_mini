---
type: index
---

# Reachy Mini — 작업 허브

```
음성 → faster-whisper(STT) → LLM(+도구 호출) → edge-tts(TTS) → 음성
                                  ↕
                            로봇 모션 / PC 제어
```

> [!danger] 지금 가장 먼저 할 것
> [[T-005 Claude API 실호출 검증]] — 기본 백엔드인데 한 번도 실제로 불러본 적이 없습니다.

---

## 남은 작업

```dataview
TABLE WITHOUT ID
  file.link AS 작업,
  priority AS 순위,
  status AS 상태,
  area AS 영역
FROM "20-Tasks"
WHERE status != "done"
SORT priority ASC, id ASC
```

## 끝난 작업

```dataview
TABLE WITHOUT ID
  file.link AS 작업,
  updated AS 완료일,
  area AS 영역
FROM "20-Tasks"
WHERE status = "done"
SORT updated DESC
LIMIT 10
```

---

## 모듈 지도

```dataview
TABLE WITHOUT ID
  file.link AS 모듈,
  status AS 상태,
  join(files, "<br>") AS 파일
FROM "10-Modules"
SORT id ASC
```

파이프라인 순서: [[M-main 대화 루프]] → [[M-audio 오디오 입출력]] → [[M-stt 음성 인식]] →
[[M-llm 언어모델]] (+[[M-tools 도구 레지스트리]], [[M-conversation 대화 기록]]) →
[[M-tts 음성 합성]] → [[M-audio 오디오 입출력]] · 곁가지 [[M-robot 로봇 제어]]

---

## 결정 기록

```dataview
TABLE WITHOUT ID
  file.link AS 결정,
  status AS 상태,
  date AS 날짜
FROM "30-Decisions"
SORT id ASC
```

---

## 최근 작업 로그

```dataview
TABLE WITHOUT ID
  file.link AS 날짜,
  tasks AS 다룬작업
FROM "40-Log"
SORT file.name DESC
LIMIT 14
```

---

## 참고 문서
- [[R-단계별 구동 절차]] — 처음 구동할 때 이 순서대로
- [[R-문제 해결]] — 증상 → 조치 표
- [[R-VRAM 예산]] — 8 GB 카드에 뭘 얹을 수 있는가
- [[R-데몬과 연결]] — 로봇을 붙일 때 반드시
- [[R-동작 특성]] — 버그로 오해하기 쉬운 것들

## 쓰는 법
[[볼트 사용법]]
