"""問い合わせ: 日本語の問いを、決まった型（Query）に直し、判定済みの結果から答える（QueRyu/docs/ask.md）。

    python queryu/ask/ask.py "E25 に阪神 2015 以外の判例はある？" --results cycles/c001-chunichi/outputs
    python queryu/ask/ask.py --schema          # Query の JSON Schema（llama.cpp や MCP のツールで、型で縛った選択に使う）

役割の分け方（Jev の「型で縛った選択」の考え方。モデルも API キーも使わない）:
  読み取り : 問い → Query。選べる値は登録済みのもの（命題・式の ID、球団、4つの形、問いの種類）だけ
  答え     : Query → 判定済みの結果（propositions.jsonl・sets.jsonl、PythDRagoras が出したもの）を引くだけ。計算し直さない
読めなかった語は黙って捨てず、unread に返す。数（%・年）は正規表現で読む。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path

FORMS = {"original": "元の命題", "contrapositive": "対偶", "converse": "逆", "inverse": "裏"}
ASKS = {
    "has_counterexample": "判例はあるか（はい・いいえ）",
    "counterexamples": "判例の一覧",
    "unique_exception": "判例がちょうど1つのもの",
    "rate": "成立率が条件を満たすもの",
}
TEAMS = {  # 球団名 → コード。取得元の表記（npb_calendar・npb_game_linescore）と、よく使う呼び名
    "巨人": "g", "読売": "g", "ジャイアンツ": "g", "ヤクルト": "s", "東京ヤクルト": "s", "スワローズ": "s",
    "DeNA": "db", "横浜DeNA": "db", "ベイスターズ": "db", "中日": "d", "ドラゴンズ": "d",
    "阪神": "t", "タイガース": "t", "広島": "c", "広島東洋": "c", "カープ": "c",
    "ソフトバンク": "h", "福岡ソフトバンク": "h", "ホークス": "h", "日本ハム": "f", "北海道日本ハム": "f", "ファイターズ": "f",
    "オリックス": "b", "バファローズ": "b", "楽天": "e", "東北楽天": "e", "イーグルス": "e",
    "西武": "l", "埼玉西武": "l", "ライオンズ": "l", "ロッテ": "m", "千葉ロッテ": "m", "マリーンズ": "m",
}
CODES = set(TEAMS.values())
KINDS = {"any": "命題と式", "proposition": "命題", "expression": "式"}


@dataclass
class Query:
    """問い合わせの型。どの値も、選べるものの中から選ぶ。"""
    ask: str = "counterexamples"                     # ASKS のどれか
    target: str | None = None                        # 命題・式の ID（P12・E25）。None ならすべて
    kind: str = "any"                                # KINDS のどれか（「式」なら式だけ、「命題」なら命題だけ）
    form: str = "original"                           # FORMS のどれか
    exclude: list[str] = field(default_factory=list)  # 判例から除く単位（t-2015）
    about: list[str] = field(default_factory=list)    # この単位・球団が判例にいるものだけ（t-2015 または t）
    min_rate: float | None = None                     # 成立率の下限（0〜1）
    max_rate: float | None = None                     # 成立率の上限（0〜1）


def schema() -> dict:
    """Query の JSON Schema。選べる値を enum で縛る（llama.cpp の json_schema・MCP のツールの引数に渡せる）。"""
    unit = {"type": "string", "pattern": r"^[a-z]{1,2}(-\d{4})?$"}
    return {
        "type": "object", "additionalProperties": False, "required": ["ask"],
        "properties": {
            "ask": {"enum": list(ASKS)}, "target": {"type": ["string", "null"], "pattern": r"^[PE]\d+$"},
            "kind": {"enum": list(KINDS)}, "form": {"enum": list(FORMS)}, "exclude": {"type": "array", "items": unit},
            "about": {"type": "array", "items": unit},
            "min_rate": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
            "max_rate": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        },
    }


def validate_query(raw: dict) -> Query:
    """Validate all fields at the execution boundary, including LLM output."""
    if not isinstance(raw, dict) or set(raw) - set(Query.__dataclass_fields__):
        raise ValueError("Query は定義済み項目だけを持つ object")
    q = Query(**raw)
    if any(not isinstance(v, str) or v not in choices for v, choices in ((q.ask, ASKS), (q.form, FORMS), (q.kind, KINDS))):
        raise ValueError("ask / form / kind が選択肢の外")
    if q.target is not None and (not isinstance(q.target, str) or not re.fullmatch(r"[PE]\d+", q.target)):
        raise ValueError("target は P番号 / E番号 / null")
    if q.target and q.kind != "any" and q.target[0] != ("P" if q.kind == "proposition" else "E"):
        raise ValueError("target と kind が一致しない")
    for values in (q.exclude, q.about):
        if not isinstance(values, list) or len(values) > 200 or any(
            not isinstance(v, str) or not re.fullmatch(r"[a-z]{1,2}(-\d{4})?", v)
            or v.split("-")[0] not in CODES for v in values
        ):
            raise ValueError("単位は登録済み球団コード、または 球団コード-年")
    for v in (q.min_rate, q.max_rate):
        if v is not None and (type(v) not in (int, float) or not 0 <= v <= 1 or not math.isfinite(v)):
            raise ValueError("成立率は 0〜1 の数値 / null")
    if q.min_rate is not None and q.max_rate is not None and q.min_rate > q.max_rate:
        raise ValueError("成立率の下限が上限より大きい")
    return q


_ID = re.compile(r"(?<![A-Za-z])([PE])\s?(\d{1,4})(?!\d)")
_YEAR = re.compile(r"(20\d{2})(?:年)?")
_CODE_UNIT = re.compile(r"(?<![A-Za-z])([a-z]{1,2})-(\d{4})(?!\d)")
_PCT = re.compile(r"(\d{1,3}(?:\.\d+)?)\s?(%|パーセント|割)\s?(以上|以下|未満|超)?")
_TEAM = re.compile("|".join(sorted(map(re.escape, TEAMS), key=len, reverse=True)))


def _norm(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def parse(text: str) -> tuple[Query, list[str]]:
    """問い → (Query, 読めなかったこと)。読めなかったことは、黙って捨てずに返す。"""
    t = _norm(text)
    q, unread = Query(), []
    ids = [f"{a}{int(b)}" for a, b in _ID.findall(t)]
    if len(ids) > 1:
        unread.append(f"命題・式が2つ以上: {', '.join(ids)}（最初の {ids[0]} だけ使う）")
    q.target = ids[0] if ids else None
    has_e, has_p = "式" in t, "命題" in t
    if not q.target and has_e != has_p:
        q.kind = "expression" if has_e else "proposition"
    t_wo_ids = _ID.sub(" ", t)

    # 形: 対偶 → 裏 → 逆 の順に見る（「逆に」は形ではない）
    if "対偶" in t:
        q.form = "contrapositive"
    elif "裏" in t:
        q.form = "inverse"
    elif re.search(r"逆(?!に)", t):
        q.form = "converse"

    # 単位（球団 + 年、または t-2015）と、球団だけ
    units: list[tuple[int, str]] = [(m.start(), f"{m[1]}-{m[2]}") for m in _CODE_UNIT.finditer(t_wo_ids) if m[1] in CODES]
    for m in _TEAM.finditer(t_wo_ids):
        y = _YEAR.match(t_wo_ids[m.end():].lstrip())
        units.append((m.start(), f"{TEAMS[m[0]]}-{y[1]}" if y else TEAMS[m[0]]))
    for pos, u in sorted(units):
        rest = t_wo_ids[pos:]
        (q.exclude if re.match(r"\S+(?:\s?\d{4}年?)?\s?(を)?(以外|除い|除く|抜い|抜き)", rest) else q.about).append(u)

    # 成立率
    for num, unit_, rel in _PCT.findall(t):
        v = float(num) / (10 if unit_ == "割" else 100)
        if rel in ("以下", "未満"):
            q.max_rate = v
        else:
            q.min_rate = v
            if not rel:
                unread.append(f"{num}{unit_} の向き（以上・以下）が書かれていない（以上として読む）")

    # 問いの種類
    if re.search(r"唯一|ただ1つ|1つだけ|ひとつだけ|1個だけ", t):
        q.ask = "unique_exception"
    elif re.search(r"判例|反例|例外", t) and re.search(r"ある[?？か]|ありますか|あるの|有無|はい|いいえ|ない[?？か]", t):
        q.ask = "has_counterexample"
    elif re.search(r"判例|反例|例外", t):
        q.ask = "counterexamples"
    elif q.min_rate is not None or q.max_rate is not None or "成立率" in t:
        q.ask = "rate"
    else:
        unread.append("問いの種類（判例・唯一の例外・成立率）が読めない（判例の一覧として読む）")
    if q.ask == "rate" and q.min_rate is None and q.max_rate is None:
        unread.append("成立率の条件の数が読めない")
    if any(rel in ("未満", "超") for _, _, rel in _PCT.findall(t)):
        unread.append("未満・超は未対応。以上・以下とは区別して問い合わせてください")
    if sum(word in t for word in ("対偶", "裏")) + bool(re.search(r"逆(?!に)", t)) > 1:
        unread.append("形が2つ以上ある")
    # Consume only the supported vocabulary. Unrecognized restrictions must not
    # quietly disappear (e.g. 雨の日だけ, 2025年だけ, E25とE26).
    rest = _ID.sub(" ", t)
    rest = _PCT.sub(" ", rest)
    rest = re.sub(r"(?:" + _TEAM.pattern + r")\s*(?:20\d{2}年?)?", " ", rest)
    rest = _CODE_UNIT.sub(" ", rest)
    words = ("判例", "反例", "例外", "成立率", "命題", "式", "対偶", "逆に", "逆", "裏", "元の", "original",
             "一覧", "唯一", "ただ1つ", "1つだけ", "ひとつだけ", "1個だけ", "以外", "除いて", "除く", "抜いて", "抜き",
             "ありますか", "あるの", "ある", "ない", "有無", "はい", "いいえ", "教えてください", "教えて", "ください")
    rest = re.sub("|".join(map(re.escape, sorted(words, key=len, reverse=True))), " ", rest)
    rest = re.sub(r"[\s?？、。,:：のにはがをでとか]", "", rest)
    if rest:
        unread.append(f"未対応の語・条件: {rest}")
    try:
        validate_query(asdict(q))
    except (ValueError, TypeError) as e:
        unread.append(str(e))
    return q, unread


def load(results: Path) -> list[dict]:
    """判定済みの命題と式（PythDRagoras の出力）。どちらも forms に4つの形の判定を持つ。"""
    out = []
    for name in ("propositions.jsonl", "sets.jsonl"):
        p = results / name
        if p.exists():
            out += [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
    return out


def _id_key(i: str) -> tuple:
    return (i[0], int(i[1:])) if re.fullmatch(r"[PE]\d+", i) else (i, 0)


def registration_status(item: dict) -> str:
    """Conservative provenance label; posthoc false/missing is not preregistration."""
    if item.get("posthoc") is True:
        return "事後構成"
    if item.get("preregistered") is True or item.get("preregistered_at") or item.get("preregistration"):
        return "事前登録"
    return "不明"


def answer(q: Query, items: list[dict]) -> dict:
    """Query に、判定済みの結果だけで答える（計算し直さない）。"""
    if q.target and not any(it["id"] == q.target for it in items):
        return {"answer": "判定不能", "error": f"{q.target} は判定済みの結果にない", "rows": []}
    rows, uncertain, evaluated = [], False, 0
    for it in sorted(items, key=lambda it: _id_key(it["id"])):
        if q.target and it["id"] != q.target:
            continue
        if q.kind != "any" and it["id"][0] != ("E" if q.kind == "expression" else "P"):
            continue
        f = next((f for f in it.get("forms", []) if f.get("form") == q.form), None)
        if f is None or not f.get("n"):
            uncertain = True
            continue
        evaluated += 1
        listed = [c["unit"] for c in f.get("counterexamples", [])]
        # PythDRagoras counts n AFTER removing unknown rows. Do not subtract
        # undetermined again: that used to hide real counterexamples.
        n_cx = f["n"] - f["hold"]
        cx = [u for u in listed if not any(u == a or u.split("-")[0] == a for a in q.exclude)]
        complete = len(listed) == n_cx
        left = n_cx - (len(listed) - len(cx))
        count_known = complete or not q.exclude
        uncertain |= bool(f.get("undetermined", 0)) or not count_known
        if q.about and not any(u == a or u.split("-")[0] == a for u in cx for a in q.about):
            uncertain |= not complete
            continue
        if q.ask == "unique_exception" and (not count_known or left != 1):
            continue
        if q.min_rate is not None and f["rate"] < q.min_rate:
            continue
        if q.max_rate is not None and f["rate"] > q.max_rate:
            continue
        rows.append({"id": it["id"], "form": q.form, "n": f["n"], "hold": f["hold"], "rate": round(f["rate"], 3),
                     "counterexamples_left": left if count_known else None,
                     "has_counterexample": bool(cx) or (count_known and left > 0),
                     "undetermined": f.get("undetermined", 0), "counterexamples": cx, "listed_all": complete,
                     "statement": it.get("statement", ""), "registration": registration_status(it)})
    if q.ask == "has_counterexample":
        ans = ("はい" if any(r["has_counterexample"] for r in rows)
               else "判定不能" if uncertain or not evaluated else "いいえ")
    else:
        ans = len(rows)
    return {"answer": ans, "rows": rows, "incomplete": uncertain or not evaluated}


def render(text: str, q: Query, unread: list[str], res: dict) -> str:
    lines = [f"問い: {text}", "読み取り: " + json.dumps(asdict(q), ensure_ascii=False)]
    lines += [f"読めなかった: {u}" for u in unread]
    if res.get("error"):
        return "\n".join([*lines, f"答え: 判定不能（{res['error']}）"])
    head = f"{ASKS[q.ask]}・{FORMS[q.form]}・{KINDS[q.kind]}" + ("・除いた後の判例" if q.exclude else "")
    lines.append(f"答え（{head}）: {res['answer']}" + ("" if q.ask == "has_counterexample" else " 件"))
    for r in res["rows"][:50]:
        cx = ", ".join(r["counterexamples"]) or "なし"
        more = "" if r["listed_all"] else "（一覧は一部）"
        count = r["counterexamples_left"] if r["counterexamples_left"] is not None else "不明"
        label = "除外後の判例" if q.exclude else "判例"
        excluded = "（除外 " + ", ".join(q.exclude) + "）" if q.exclude else ""
        lines.append(f"- {r['id']}［{r['registration']}］ {FORMS[q.form]}の成立率 {r['hold']}/{r['n']}（{r['rate']:.3f}）／{label} {count}{excluded}: {cx}{more}")
    if len(res["rows"]) > 50:
        lines.append(f"- ほか {len(res['rows']) - 50} 件")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("question", nargs="?", help="日本語の問い")
    ap.add_argument("--results", type=Path, default=Path("cycles/c001-chunichi/outputs"),
                    help="判定済みの結果のフォルダ（propositions.jsonl・sets.jsonl）")
    ap.add_argument("--query", help="読み取りを飛ばし、Query を JSON で直接渡す（llama.cpp・MCP が選んだもの）")
    ap.add_argument("--schema", action="store_true", help="Query の JSON Schema を出す")
    ap.add_argument("--json", action="store_true", help="答えを JSON で出す")
    ap.add_argument("--log", type=Path, help="問いと読み取りを1行ずつ足す（JSONL）。同じ Query なら答えは同じ")
    args = ap.parse_args(argv)

    if args.schema:
        print(json.dumps(schema(), ensure_ascii=False, indent=2))
        return 0
    if args.query:
        try:
            q = validate_query(json.loads(args.query))
        except (ValueError, TypeError) as e:
            print(f"Query の値が型の外: {e}", file=sys.stderr)
            return 2
        unread, text = [], args.query
    elif args.question:
        text = args.question
        q, unread = parse(text)
    else:
        ap.error("問いか --query か --schema が要る")
    res = ({"answer": "判定不能", "error": "解釈を確認してください: " + "; ".join(unread), "rows": []}
           if unread else answer(q, load(args.results)))
    if args.log:
        args.log.parent.mkdir(parents=True, exist_ok=True)
        with args.log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"question": text, "query": asdict(q), "unread": unread}, ensure_ascii=False) + "\n")
    print(json.dumps({"query": asdict(q), "unread": unread, **res}, ensure_ascii=False, indent=2) if args.json
          else render(text, q, unread, res))
    return 1 if res.get("error") else 0


if __name__ == "__main__":
    raise SystemExit(main())
