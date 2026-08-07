---
status: blocked
priority: P2
files:
  - reachy/robot.py
---

# T-002 머리 pitch roll 추가

`_head()`가 상하 이동(z)만 씁니다. 고개를 끄덕이거나 갸웃하는 동작이 실제로는
평행이동이라, 로봇이 아니라 엘리베이터처럼 움직입니다.

## 막혀 있는 이유

**`create_head_pose()`의 회전 파라미터명을 실기에서 확인해야 합니다.** SDK 문서만으로는
`pitch`/`roll`인지 `rx`/`ry`인지, 단위가 degree인지 radian인지 확정할 수 없습니다.
mock 모드로는 검증이 안 됩니다.

확인 경로: 데몬 대시보드 `http://localhost:8000/docs`

## 무엇을 바꾸나

- `_head(z_mm)` → 회전 파라미터 추가
- `_goto()` 시그니처도 따라 확장
- `nod` / `confused`를 회전 기반으로 다시 쓰기

## 완료 조건

- [ ] 실기에서 파라미터명·단위 확인 후 아래에 기록
- [ ] `_head()`에 pitch/roll 추가
- [ ] `nod`이 회전으로 동작
- [ ] 관절 한계를 넘지 않도록 값 클램프

## 확인한 SDK 파라미터
<!-- 실기에서 확인한 내용을 여기에 -->
