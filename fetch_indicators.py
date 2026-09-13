"""FRED에서 지표를 받아 data/indicators.json에 저장한다. 실행: python fetch_indicators.py"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from macro.fred import build_indicators, fetch_csv

KST = timezone(timedelta(hours=9))


def main() -> int:
    path = Path(__file__).resolve().parent / "data" / "indicators.json"
    previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    now = datetime.now(KST).isoformat(timespec="seconds")
    data = build_indicators(fetch_csv, previous, now)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    stale = [sid for sid, s in data["series"].items() if s["stale"]]
    print(f"[fred] 성공 {len(data['series']) - len(stale)}개, 지연 {len(stale)}개 {stale}")
    return 1 if len(stale) == len(data["series"]) else 0


if __name__ == "__main__":
    sys.exit(main())
