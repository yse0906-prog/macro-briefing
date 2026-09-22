"""site/ 폴더에 모든 페이지를 쓴다. 페이지가 추가될 때마다 build_site에 등록한다."""
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from macro.data import load_site_data
from macro.pages.archive import render_archive
from macro.pages.briefing import render_briefing, render_briefing_empty
from macro.pages.fomc import render_fomc
from macro.pages.home import render_home
from macro.pages.indicators import render_indicators
from macro.pages.issues import render_issues
from macro.pages.sectors import render_sectors, render_sectors_day

KST = timezone(timedelta(hours=9))
STATIC = Path(__file__).resolve().parent.parent / "static"


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def build_site(data_dir: Path, out_dir: Path, issues: list, today=None) -> list[Path]:
    today = today or datetime.now(KST).date()
    site = load_site_data(data_dir)
    written = [
        write(out_dir / "index.html", render_home(site, today)),
        write(out_dir / "archive.html", render_archive(site)),
        write(out_dir / "fomc.html", render_fomc(site, today)),
        write(out_dir / "indicators.html", render_indicators(site)),
        write(out_dir / "issues.html", render_issues(issues)),
        write(out_dir / "sectors.html", render_sectors(site)),
    ]
    for day in site.sectors:
        written.append(write(out_dir / "sectors" / f"{day['date']}.html", render_sectors_day(site, day)))
    for b in site.briefings:
        written.append(write(out_dir / "briefings" / f"{b['date']}.html", render_briefing(site, b, today)))
    latest = render_briefing(site, site.latest, today) if site.latest else render_briefing_empty()
    written.append(write(out_dir / "briefings" / "latest.html", latest))
    if STATIC.exists():
        shutil.copytree(STATIC, out_dir, dirs_exist_ok=True)
    return written
