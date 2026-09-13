"""site/ 폴더에 모든 페이지를 쓴다. 페이지가 추가될 때마다 build_site에 등록한다."""
from datetime import datetime, timedelta, timezone
from pathlib import Path

from macro.data import load_site_data
from macro.pages.archive import render_archive
from macro.pages.home import render_home
from macro.pages.issues import render_issues

KST = timezone(timedelta(hours=9))


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def build_site(data_dir: Path, out_dir: Path, issues: list, today=None) -> list[Path]:
    today = today or datetime.now(KST).date()
    site = load_site_data(data_dir)
    return [
        write(out_dir / "index.html", render_home(site, today)),
        write(out_dir / "archive.html", render_archive(site)),
        write(out_dir / "issues.html", render_issues(issues)),
    ]
