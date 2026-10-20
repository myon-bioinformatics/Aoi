"""NPB-specific configuration that Aoi passes to its child projects (stdlib only).

The children (QueRyu, DRAgoWing, SakAnalytics) hold no NPB tables or rules; Aoi hands them over:
  TEAMS               -> QueRyu ask.set_teams / ask.py --teams
  CALENDAR_MONTH_KEY  -> QueRyu queryu.py --month-key (npb_calendar pages)
  TEAM_ORDER          -> DRAgoWing heatmap_figure(team_order=...) / --team-order
  ANNUAL_AUDIT_RULES  -> SakAnalytics annual_audit.audit(rules=...) / --rules
  npb_rules()         -> SakAnalytics season_simulator.Rules presets
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 球団名 → コード。取得元の表記（npb_calendar・npb_game_linescore）と、よく使う呼び名
TEAMS: dict[str, str] = {
    "巨人": "g",
    "読売": "g",
    "ジャイアンツ": "g",
    "ヤクルト": "s",
    "東京ヤクルト": "s",
    "スワローズ": "s",
    "DeNA": "db",
    "横浜DeNA": "db",
    "ベイスターズ": "db",
    "中日": "d",
    "ドラゴンズ": "d",
    "阪神": "t",
    "タイガース": "t",
    "広島": "c",
    "広島東洋": "c",
    "カープ": "c",
    "ソフトバンク": "h",
    "福岡ソフトバンク": "h",
    "ホークス": "h",
    "日本ハム": "f",
    "北海道日本ハム": "f",
    "ファイターズ": "f",
    "オリックス": "b",
    "バファローズ": "b",
    "楽天": "e",
    "東北楽天": "e",
    "イーグルス": "e",
    "西武": "l",
    "埼玉西武": "l",
    "ライオンズ": "l",
    "ロッテ": "m",
    "千葉ロッテ": "m",
    "マリーンズ": "m",
}

# npb_calendar の key は「年_月」。打撃成績の key（年_リーグ）は月ではないので、ここには当たらない
CALENDAR_MONTH_KEY = r"(?P<year>\d{4})_(?P<month>\d{2})"

# 球団×年の上から下。中日 d を最上段にする。残りは記録にある記号の並びで、d を先頭に繰り上げたもの
TEAM_ORDER: tuple[str, ...] = ("d", "g", "s", "db", "t", "c", "h", "f", "b", "e", "l", "m")

# 年間表（NPB 公式の年度別成績）の前提
ANNUAL_AUDIT_RULES = dict(
    leagues=("C", "P"),
    # detail 表（試合・守備を含む）と今の勝率規則は 2005 年から。それより前は推測で当てはめない
    detail_from=2005,
    winning_percentage_from=2005,
    # 交流戦のある 2005 年からは各リーグ 6 球団
    fixed_members=6,
    fixed_members_from=2005,
    # 公式の集計の拡張桁は切り捨て（例: 1961 巨人 .2265 = 958/4228）。通常の 3 桁は四捨五入
    extended_rounding="truncate",
    opponents=dict(zip(("対巨", "対中", "対神", "対デ", "対ヤ", "対広", "対ソ", "対日", "対オ", "対楽", "対西", "対ロ"),
                       ("g", "d", "t", "db", "s", "c", "h", "f", "b", "e", "l", "m"))),
)

# 公式原文で確かめた CS の規則だけをプリセットにする
_VERIFIED_CS = {(2022, "CL"), (2022, "PL"), (2025, "CL")}


def npb_rules(year, league, members, previous_order):
    """Only versions actually checked against the official source are preset."""
    if str(ROOT / "sakanalytics") not in sys.path:
        sys.path.append(str(ROOT / "sakanalytics"))
    from season_simulator import Rules

    if (year, league) not in _VERIFIED_CS:
        raise ValueError("unverified year/league: supply explicit Rules with its source")
    if len(members) != 6:
        raise ValueError("NPB presets require six league members")
    return Rules(tuple(members), tuple(previous_order), league == "CL", 3,
                 f"NPB-{year}-{league}", f"https://npb.jp/games/{year}/info_cs{league.lower()}.html")


def write_json(kind: str, path: Path) -> Path:
    """Write TEAMS or ANNUAL_AUDIT_RULES as JSON for child CLIs (--teams / --rules)."""
    value = {"teams": TEAMS, "annual-audit-rules": ANNUAL_AUDIT_RULES}[kind]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv=None) -> int:
    """Supply NPB defaults to generic child CLIs; keep user paths relative to cwd."""
    import argparse

    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("calendar", "draw", "annual-audit"):
        command, *forwarded = argv
        if command == "calendar":
            return subprocess.run([
                sys.executable, str(ROOT / "queryu/queryu.py"),
                "--source", "npb_calendar", "--month-key", CALENDAR_MONTH_KEY, *forwarded,
            ], check=False).returncode
        if command == "draw":
            env = dict(os.environ)
            env["PYTHONPATH"] = os.pathsep.join(filter(None, (str(ROOT), env.get("PYTHONPATH"))))
            return subprocess.run([
                sys.executable, "-m", "dragowing", "--team-order", ",".join(TEAM_ORDER), *forwarded,
            ], env=env, check=False).returncode
        with tempfile.TemporaryDirectory(prefix="aoi-npb-") as directory:
            rules = write_json("annual-audit-rules", Path(directory) / "rules.json")
            return subprocess.run([
                sys.executable, str(ROOT / "sakanalytics/annual_audit.py"),
                "--rules", str(rules), *forwarded,
            ], check=False).returncode

    parser = argparse.ArgumentParser(description="NPB の設定を子の CLI 用の JSON に書き出す")
    parser.add_argument("kind", choices=("teams", "annual-audit-rules"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    print(write_json(args.kind, args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
