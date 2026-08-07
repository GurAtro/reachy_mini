---
type: reference
id: R-bringup
---

# R-단계별 구동 절차

한 번에 다 켜지 마세요. 단계를 올려야 문제가 생겼을 때 원인이 좁혀집니다.

## 1단계 — mock으로 대화만 (로봇 불필요)
기본 설정 그대로 `python main.py`. 확인할 것:

- [ ] `[STT] Ready on cuda` — `cpu`로 뜨면 CUDA 미설치 → [[M-stt 음성 인식]]
- [ ] 한국어 인식 정확도 — 부족하면 `stt.model: medium`
- [ ] `[LLM] tokens in=... cached=...` — 두 번째 턴부터 `cached`가 오르면 프롬프트 캐싱 성공
- [ ] edge-tts 한국어 목소리가 마음에 드는지

> [!warning] Claude API는 여기서 처음 검증됩니다
> → [[T-005 Claude API 실호출 검증]]

## 2단계 — 로봇 모션 (소리는 PC)
```yaml
reachy: {enabled: true, media_backend: "no_media"}
audio:  {source: "local"}
```
- [ ] `[Reachy] Connected.` 확인. 안 뜨면 mock으로 강등된 것입니다 → [[R-데몬과 연결]]

## 3단계 — 완전 구동
```yaml
reachy: {enabled: true, media_backend: "default"}
audio:  {source: "reachy"}
```

## 4단계 — TTS 비교 (선택)
edge-tts를 기준으로 두고 같은 문장으로 비교하세요.
```bash
pip install -U qwen-tts
```
```yaml
tts:
  backend: "qwen"
  qwen: {model: "Qwen/Qwen3-TTS-12Hz-0.6B-Base", ref_audio: "...", ref_text: "..."}
```
0.6B가 부족하면 `1.7B-Base`로. 그래도 아쉽다면 모델이 아니라 VRAM 문제입니다 —
더 큰 한국어 음성 모델은 12~16 GB부터입니다 → [[R-VRAM 예산]]

## 관련
- [[R-문제 해결]] · [[R-데몬과 연결]]
