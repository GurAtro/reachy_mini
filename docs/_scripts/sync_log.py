#!/usr/bin/env python3
"""그날의 git 커밋을 40-Log/YYYY-MM-DD.md 노트에 채웁니다.

    python docs/_scripts/sync_log.py             # 오늘
    python docs/_scripts/sync_log.py 2026-08-06  # 특정 날짜

노트가 없으면 _templates/작업 로그.md 를 바탕으로 새로 만듭니다.
커밋 목록은 <!-- commits:start --> / <!-- commits:end --> 사이만 덮어쓰므로,
손으로 적은 부분은 몇 번을 돌려도 그대로 남습니다.
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent      # docs/
REPO = VAULT.parent                                  # 저장소 루트
LOG_DIR = VAULT / "40-Log"
TEMPLATE = VAULT / "_templates" / "작업 로그.md"

START = "<!-- commits:start -->"
END = "<!-- commits:end -->"


def parse_day(argv: list[str]) -> date:
    if len(argv) < 2:
        return date.today()
    try:
        return datetime.strptime(argv[1], "%Y-%m-%d").date()
    except ValueError:
        sys.exit(f"날짜 형식은 YYYY-MM-DD 입니다: {argv[1]}")


def commits_on(day: date) -> list[str]:
    """그날 00:00 ~ 다음날 00:00 사이의 커밋을 마크다운 줄로."""
    result = subprocess.run(
        # core.quotepath=false — 없으면 한글 파일명이 8진수로 이스케이프됩니다.
        ["git", "-c", "core.quotepath=false", "log",
         f"--since={day.isoformat()} 00:00",
         f"--until={(day + timedelta(days=1)).isoformat()} 00:00",
         "--pretty=format:%h\t%s\t%an",
         "--no-merges"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        sys.exit(f"git log 실패: {result.stderr.strip()}")

    lines = []
    for raw in result.stdout.splitlines():
        if not raw.strip():
            continue
        short, subject, author = raw.split("\t", 2)
        files = changed_files(short)
        suffix = f" — `{'`, `'.join(files)}`" if files else ""
        lines.append(f"- `{short}` {subject} ({author}){suffix}")
    return lines


def changed_files(rev: str, limit: int = 4) -> list[str]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false",
         "show", "--name-only", "--pretty=format:", rev],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
    )
    files = [f for f in result.stdout.splitlines() if f.strip()]
    # 볼트 자신의 변경은 빼야 로그가 자기 얘기로 채워지지 않습니다.
    files = [f for f in files if not f.startswith("docs/")]
    if not files:
        return []
    if len(files) > limit:
        return files[:limit] + [f"…외 {len(files) - limit}개"]
    return files


def note_body(day: date) -> str:
    """기존 노트를 읽거나, 없으면 템플릿으로 새 본문을 만듭니다."""
    path = LOG_DIR / f"{day.isoformat()}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")

    if TEMPLATE.exists():
        body = TEMPLATE.read_text(encoding="utf-8")
        return body.replace("{{date}}", day.isoformat())

    return (f"---\ntype: log\ndate: {day.isoformat()}\ntasks: []\n---\n\n"
            f"# {day.isoformat()}\n\n## 커밋\n{START}\n{END}\n")


def splice(body: str, block: str) -> str:
    """마커 사이를 갈아끼웁니다. 마커가 없으면 끝에 섹션을 붙입니다."""
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    replacement = f"{START}\n{block}\n{END}"
    if pattern.search(body):
        return pattern.sub(lambda _: replacement, body, count=1)
    return body.rstrip() + f"\n\n## 커밋\n{replacement}\n"


def main() -> int:
    day = parse_day(sys.argv)
    lines = commits_on(day)
    block = "\n".join(lines) if lines else "_커밋 없음._"

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"{day.isoformat()}.md"
    path.write_text(splice(note_body(day), block), encoding="utf-8")

    print(f"{path.relative_to(REPO)} — 커밋 {len(lines)}개")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
