"""Optional NPB presets, excluded from the generic single-file distribution."""
CATEGORIES = [
    {"key": "npb_sports", "label": "NPB（プロ野球）公式日程・成績表"},
]
DOM_PATTERNS = {
    "npb_calendar": {
        "key": "npb_calendar",
        "label": "NPB Schedule Calendar Table",
        "category": "npb_sports",
        "selector": "#calendar, .calendar, table.calendar",
        "description": "プロ野球（NPB）公式戦の月別・チーム別日程カレンダー表",
        "example_sites": ["npb.jp bis calendar"],
    },
    "npb_linescore": {
        "key": "npb_linescore",
        "label": "NPB Game Linescore Table",
        "category": "npb_sports",
        "selector": "table.score_table, .linescore, #linescore",
        "description": "プロ野球（NPB）試合ページの得点表（ラン・ヒット・エラー）",
        "example_sites": ["npb.jp linescore"],
    },
}

def get_pattern(key):
    """Explicit research lookup; never modifies BlueProbe's generic registry."""
    if not isinstance(key, str) or not key.strip():
        raise ValueError("pattern key must be a non-empty string")
    try:
        pattern = DOM_PATTERNS[key.strip().lower()]
        return {**pattern, "example_sites": list(pattern["example_sites"])}
    except KeyError:
        raise ValueError(f"unknown research pattern key: {key!r}") from None


def html_source(key, **options):
    """Create a generic source using a research selector explicitly."""
    from blueprobe import HtmlSource
    return HtmlSource(selector=get_pattern(key)["selector"], **options)
