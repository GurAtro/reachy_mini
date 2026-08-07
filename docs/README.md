# docs — Obsidian 볼트

이 폴더 자체가 Obsidian 보관소(vault)입니다.
Obsidian → **폴더를 보관소로 열기** → `Reachy/docs` 를 고르세요.

먼저 열 노트: **`00-Index/Home.md`** (작업 대시보드)
쓰는 법: **`00-Index/볼트 사용법.md`**

## 구성

| 폴더 | 내용 |
|---|---|
| `00-Index` | 대시보드, 사용법 |
| `10-Modules` | 코드 서브시스템 8장 — 소스 파일과 1:N 대응 |
| `20-Tasks` | 구현 작업 `T-###` |
| `30-Decisions` | 결정 기록 `ADR-###` — 왜 그렇게 골랐는가 |
| `40-Log` | 날짜별 작업 로그 (git 커밋 자동 연동) |
| `50-Reference` | VRAM 예산, 데몬 연결, 구동 절차, 문제 해결, 동작 특성 |
| `_templates` | 새 노트 틀 |
| `_scripts` | `sync_log.py` — 그날 커밋을 로그 노트로 |

## 왜 코드와 같은 저장소에 두는가

노트가 코드와 같은 커밋에 담기면 "무엇을 고쳤는가"와 "왜 고쳤는가"가 함께 남습니다.
브랜치를 옮기면 그 시점의 설계 메모도 함께 따라옵니다.

> 이 저장소는 **public**입니다. 개인적인 메모나 키·토큰은 넣지 마세요.

## 플러그인

`00-Index/Home.md`의 표는 [Dataview](https://github.com/blacksmithgu/obsidian-dataview)로
그립니다. `.obsidian/plugins/dataview/`에 이미 설치·활성화되어 있습니다.
