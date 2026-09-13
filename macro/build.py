"""site/ 폴더에 모든 페이지를 쓴다. 페이지가 추가될 때마다 build_site에 등록한다."""
from pathlib import Path

from macro.pages.issues import render_issues


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def build_site(data_dir: Path, out_dir: Path, issues: list) -> list[Path]:
    written = [write(out_dir / "issues.html", render_issues(issues))]
    return written
