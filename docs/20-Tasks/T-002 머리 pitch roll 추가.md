---
type: task
id: T-002
status: todo
priority: P2
area: "[[M-robot 로봇 제어]]"
files:
  - reachy/robot.py
created: 2026-08-07
updated: 2026-08-07
commits: []
---

# T-002 머리 pitch roll 추가

## 왜 하는가
`_head()`가 상하 이동(z)만 씁니다. 고개를 끄덕이거나 갸웃하는 동작이 실제로는
평행이동이라 로봇 같지 않고 엘리베이터 같습니다.

## 무엇을 바꾸는가
- `reachy/robot.py`의 `_head(z_mm)` → 회전 파라미터 추가
- `_goto()`의 시그니처도 따라 확장
- `nod` / `confused`를 회전 기반으로 다시 씀

## 막혀 있는 지점
**`create_head_pose()`의 회전 파라미터명을 실기에서 확인해야 합니다.** SDK 문서만으로는
`pitch`/`roll`인지 `rx`/`ry`인지, 단위가 degree인지 radian인지 확정할 수 없습니다.
mock 모드로는 검증이 안 되는 작업입니다.

확인 경로: 데몬 대시보드 `http://localhost:8000/docs` → [[R-데몬과 연결]]

## 완료 조건
- [ ] 실기에서 `create_head_pose()` 파라미터명·단위 확인 후 여기에 기록
- [ ] `_head()`에 pitch/roll 추가
- [ ] `nod`이 회전으로 동작
- [ ] 관절 한계를 넘지 않도록 값 클램프

## 검증 방법
실기 필요. [[R-단계별 구동 절차]]의 2단계(`media_backend: "no_media"`) 상태에서
모션만 확인하면 됩니다.

## 진행 기록

## 관련
- 영역: [[M-robot 로봇 제어]]
