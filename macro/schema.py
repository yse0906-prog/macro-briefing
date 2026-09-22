"""data/ 파일 형식 검사. 각 함수는 오류 메시지 목록을 돌려준다(빈 목록 = 통과)."""
import json
from datetime import date, datetime
from pathlib import Path

from macro.fred import SERIES

IMPACTS = {"positive", "negative", "neutral"}
SECTOR_IMPACTS = IMPACTS | {"mixed"}
DIRECTIONS = {"up", "down", None}
ASSETS = {"us_equities", "us_rates", "usd", "krw"}
INSTITUTIONS = ["securities", "lp", "gp"]
OUTCOMES = {"hold", "cut25", "cut50", "hike25", "hike50"}


def _is_date(value) -> bool:
    if not isinstance(value, str) or len(value) != 10:
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _is_kst(value) -> bool:
    try:
        return datetime.fromisoformat(value).utcoffset().total_seconds() == 9 * 3600
    except (TypeError, ValueError, AttributeError):
        return False


def _https(value) -> bool:
    return isinstance(value, str) and value.startswith("https://")


def _check_probabilities(items, where, err):
    if not isinstance(items, list) or not items:
        err(f"{where}: 확률 목록이 비어 있음")
        return
    for p in items:
        if p.get("outcome") not in OUTCOMES:
            err(f"{where}: 알 수 없는 outcome {p.get('outcome')}")
    total = sum(p.get("pct", 0) for p in items)
    if abs(total - 100) > 1:
        err(f"{where}: 확률 합이 100이 아님({total})")


def _check_fomc(fomc, err):
    nxt = fomc.get("next_meeting")
    if nxt is not None:
        if not _is_date(nxt.get("date")):
            err("fomc.next_meeting.date 형식 오류")
        if not _is_kst(nxt.get("announce_kst")):
            err("fomc.next_meeting.announce_kst는 KST ISO 시각이어야 함")
        _check_probabilities(nxt.get("probabilities"), "fomc.next_meeting.probabilities", err)
        if nxt.get("view") not in OUTCOMES:
            err("fomc.next_meeting.view 값 오류")
    last = fomc.get("last_meeting")
    if last is not None:
        if not _is_date(last.get("date")):
            err("fomc.last_meeting.date 형식 오류")
        if last.get("decision") not in OUTCOMES:
            err("fomc.last_meeting.decision 값 오류")
        rng = last.get("range")
        if not (isinstance(rng, list) and len(rng) == 2 and rng[0] < rng[1]):
            err("fomc.last_meeting.range는 [하단, 상단]")
        tone = last.get("tone")
        if not (isinstance(tone, (int, float)) and 0 <= tone <= 1):
            err("fomc.last_meeting.tone은 0~1")


def _check_releases(releases, source_ids, err):
    for i, r in enumerate(releases):
        where = f"releases[{i}]"
        for key in ("series", "name", "release_date", "period", "impact", "interpretation"):
            if key not in r:
                err(f"{where}: 필수 항목 없음: {key}")
        if r.get("impact") not in IMPACTS:
            err(f"{where}: impact 값 오류")
        if r.get("series") in SERIES:
            if "actual" in r or "previous" in r:
                err(f"{where}: FRED 지표({r['series']})에는 actual/previous를 적지 않습니다")
        else:
            for key in ("actual", "previous", "actual_source"):
                if key not in r:
                    err(f"{where}: 웹 수집 지표에는 {key}가 필요합니다")
        for key in ("consensus_source", "actual_source"):
            if r.get(key) is not None and r[key] not in source_ids:
                err(f"{where}.{key}: 출처 번호 {r[key]} 없음")


def _check_weekly(b, err):
    for key in ("releases", "fomc", "sectors", "scenarios", "interview_insights"):
        if key not in b:
            err(f"weekly 필수 항목 없음: {key}")
    sectors = b.get("sectors", [])
    if not 3 <= len(sectors) <= 5:
        err("sectors는 3~5개")
    if not any(s.get("name") == "금융" for s in sectors):
        err("sectors에 금융 섹터가 있어야 함")
    for i, s in enumerate(sectors):
        if s.get("impact") not in SECTOR_IMPACTS:
            err(f"sectors[{i}]: impact 값 오류")
        for n in s.get("news", []):
            if not _https(n.get("url")):
                err(f"sectors[{i}]: 뉴스 url은 https://로 시작해야 함")
    if "scenarios" in b and sum(s.get("probability", 0) for s in b["scenarios"]) != 100:
        err("시나리오 확률 합이 100이 아님")
    if len(b.get("interview_insights", [])) < 2:
        err("interview_insights는 2개 이상")


# 이 날짜부터 발행한 브리핑은 업권별 운용자산 항목과(주간이면) 외환 섹션을 모두 채운다.
DEEP_SINCE = "2026-09-19"
INSTITUTION_TOPICS = {
    "securities": ["trading", "brokerage", "ib", "wm"],
    "lp": ["duration_gap", "kics", "allocation", "fx_hedge"],
    "gp": ["flows", "fees", "products", "alternatives"],
}
POINT_DIRECTIONS = {"positive", "negative", "neutral", "mixed"}
FX_EFFECTS = {"krw_weak", "krw_strong", "neutral"}


def _check_institutions(items, source_ids, deep, err):
    names = [i.get("institution") for i in items]
    for name in INSTITUTIONS:
        if name not in names:
            err(f"institution_impact에 {name}(증권사·LP·GP) 항목이 필요함")
    for i, item in enumerate(items):
        where = f"institution_impact[{i}] {item.get('institution')}"
        if not item.get("text"):
            err(f"{where}: text 없음")
        topics = INSTITUTION_TOPICS.get(item.get("institution"), [])
        points = item.get("points", [])
        if deep:
            have = {p.get("topic") for p in points}
            for topic in topics:
                if topic not in have:
                    err(f"{where}: points에 {topic} 항목이 필요함")
        for p in points:
            if p.get("topic") not in topics:
                err(f"{where}: 이 업권에 없는 항목 {p.get('topic')} (가능: {topics})")
            if p.get("direction") not in POINT_DIRECTIONS:
                err(f"{where}.{p.get('topic')}: direction은 {sorted(POINT_DIRECTIONS)} 중 하나")
            if not p.get("text"):
                err(f"{where}.{p.get('topic')}: text 없음")
            cited = p.get("source")
            for sid in (cited if isinstance(cited, list) else [cited] if cited is not None else []):
                if sid not in source_ids:
                    err(f"{where}.{p.get('topic')}: 출처 번호 {sid} 없음")


def _check_fx(fx, source_ids, err):
    if not fx.get("headline"):
        err("fx: headline 없음")
    numbers = fx.get("numbers", [])
    if len(numbers) < 2:
        err("fx: 숫자 근거를 2개 이상 적어야 함")
    for n in numbers:
        if not n.get("text"):
            err("fx: 숫자 근거 text 없음")
        if n.get("source") not in source_ids:
            err(f"fx: 출처 번호 {n.get('source')} 없음")
    drivers = fx.get("drivers", [])
    if len(drivers) < 3:
        err("fx: 환율 방향 요인(drivers)을 3개 이상 적어야 함")
    for d in drivers:
        if not d.get("factor") or not d.get("text"):
            err("fx: drivers 항목에 factor와 text가 필요함")
        if d.get("effect") not in FX_EFFECTS:
            err(f"fx: drivers effect는 {sorted(FX_EFFECTS)} 중 하나")
    for field, label in (("hedge", "hedge(환헤지 비용)"), ("flows", "flows(수급)")):
        if not fx.get(field):
            err(f"fx: {label} 없음")
    if not fx.get("watch_next"):
        err("fx: watch_next(관전 포인트)를 1개 이상 적어야 함")


def validate_briefing(b: dict, filename: str) -> list[str]:
    errors = []
    err = lambda msg: errors.append(f"{filename}: {msg}")
    for key in ("date", "type", "headline", "summary", "market_impact", "sources"):
        if key not in b:
            err(f"필수 항목 없음: {key}")
    if errors:
        return errors
    if not _is_date(b["date"]):
        err("date 형식 오류")
    if filename != f"{b['date']}.json":
        err("파일 이름과 date가 다름")
    if b["type"] not in ("weekly", "event"):
        err("type은 weekly 또는 event")
    if len(b["headline"]) > 60:
        err("headline은 60자 이내")
    if not (isinstance(b["summary"], list) and len(b["summary"]) == 3):
        err("summary는 정확히 3개")
    source_ids = {s.get("id") for s in b["sources"]}
    for s in b["sources"]:
        if not _https(s.get("url")):
            err(f"sources[{s.get('id')}]: url은 https://로 시작해야 함")
    for i, m in enumerate(b["market_impact"]):
        if m.get("asset") not in ASSETS or m.get("direction") not in DIRECTIONS or not m.get("text"):
            err(f"market_impact[{i}]: asset/direction/text 오류")
    deep = b["date"] >= DEEP_SINCE
    _check_institutions(b.get("institution_impact", []), source_ids, deep, err)
    if "fx" in b:
        _check_fx(b["fx"], source_ids, err)
    elif deep and b["type"] == "weekly":
        err("weekly 브리핑에는 fx(외환) 섹션이 필요함")
    _check_releases(b.get("releases", []), source_ids, err)
    if "fomc" in b:
        _check_fomc(b["fomc"], err)
    if b["type"] == "weekly":
        _check_weekly(b, err)
    elif not b.get("releases") and not b.get("fomc", {}).get("last_meeting"):
        err("event 브리핑에는 releases 또는 fomc.last_meeting이 필요함")
    return errors


SECTOR_KEYS = ["finance", "energy", "bio", "semiconductor", "ai", "robotics", "realestate"]
SECTOR_STATUS = {"positive", "negative", "neutral", "mixed"}
AI_WATCH = {"OpenAI", "Anthropic"}


def validate_sectors(data: dict, filename: str) -> list[str]:
    """평일마다 쌓이는 섹터 이슈 파일을 검사한다."""
    errors = []
    err = lambda msg: errors.append(f"{filename}: {msg}")
    if not _is_date(data.get("date")):
        err("date 형식 오류")
        return errors
    if filename != f"{data['date']}.json":
        err("파일 이름과 date가 다름")
    if not _is_kst(data.get("updated_at")):
        err("updated_at은 KST ISO 시각이어야 함")
    source_ids = {s.get("id") for s in data.get("sources", [])}
    for s in data.get("sources", []):
        if not _https(s.get("url")):
            err(f"sources[{s.get('id')}]: url은 https://로 시작해야 함")

    sectors = data.get("sectors", [])
    keys = [s.get("key") for s in sectors]
    for key in SECTOR_KEYS:
        if key not in keys:
            err(f"섹터 누락: {key}")
    if keys != SECTOR_KEYS:
        err(f"섹터는 {SECTOR_KEYS} 순서로 7개가 있어야 함")

    for i, sector in enumerate(sectors):
        where = f"sectors[{i}] {sector.get('key')}"
        if sector.get("status") not in SECTOR_STATUS:
            err(f"{where}: status는 {sorted(SECTOR_STATUS)} 중 하나")
        for field, label in (("headline", "headline"), ("trigger", "trigger(촉발 요인)"),
                             ("chain", "chain(파급 경로)"), ("korea", "korea(한국 연결)"),
                             ("interview", "interview(면접 각도)")):
            if not sector.get(field):
                err(f"{where}: {label} 없음")
        numbers = sector.get("numbers", [])
        if len(numbers) < 2:
            err(f"{where}: 숫자 근거를 2개 이상 적어야 함")
        for number in numbers:
            if not number.get("text"):
                err(f"{where}: 숫자 근거 text 없음")
            if number.get("source") not in source_ids:
                err(f"{where}: 출처 번호 {number.get('source')} 없음")
        if not sector.get("watch_next"):
            err(f"{where}: 다음 관전 포인트를 1개 이상 적어야 함")
        days = sector.get("days")
        if days is not None and (not isinstance(days, int) or days < 1):
            err(f"{where}: days는 1 이상의 정수")
        if sector.get("key") == "ai":
            companies = {w.get("company") for w in sector.get("watch", [])}
            for company in sorted(AI_WATCH - companies):
                err(f"{where}: {company} 동향 칸이 필요함")
            for watch in sector.get("watch", []):
                if watch.get("source") not in source_ids:
                    err(f"{where}: {watch.get('company')} 출처 번호 {watch.get('source')} 없음")
                if not watch.get("text"):
                    err(f"{where}: {watch.get('company')} 내용 없음")
    return errors


def validate_calendar(c: dict) -> list[str]:
    errors = []
    for i, e in enumerate(c.get("events", [])):
        if not _is_kst(e.get("kst")):
            errors.append(f"events[{i}]: kst는 KST ISO 시각")
        if not e.get("name"):
            errors.append(f"events[{i}]: name 없음")
        if e.get("importance") not in (1, 2, 3):
            errors.append(f"events[{i}]: importance는 1~3")
    return errors


def _load(path: Path, errors: list):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}: JSON을 읽을 수 없음 ({exc})")
        return None


def validate_data_dir(data_dir: Path) -> list[str]:
    errors = []
    for path in sorted((data_dir / "briefings").glob("*.json")):
        b = _load(path, errors)
        if b is not None:
            errors += validate_briefing(b, path.name)
    for path in sorted((data_dir / "sectors").glob("*.json")):
        s = _load(path, errors)
        if s is not None:
            errors += validate_sectors(s, path.name)
    for name, check in (("calendar.json", validate_calendar),):
        path = data_dir / name
        if path.exists():
            obj = _load(path, errors)
            if obj is not None:
                errors += [f"{name}: {e}" for e in check(obj)]
    path = data_dir / "indicators.json"
    if path.exists():
        obj = _load(path, errors)
        if obj is not None and not isinstance(obj.get("series"), dict):
            errors.append("indicators.json: series 없음")
    return errors
