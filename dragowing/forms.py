"""四つの形の 2×2 と、条件の論理記号。

数は propositions.jsonl / sets.jsonl の forms[].n と forms[].hold だけから数える。
判定はやり直さない。図の文は観測で、成立の理由は書かない。

  python dragowing/forms.py --results cycles/c001-chunichi/outputs --id P1
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ASK = Path(__file__).resolve().parents[1] / "queryu" / "ask"
if str(_ASK) not in sys.path:
    sys.path.insert(0, str(_ASK))

from ask import registration_status

FORM_ORDER = ("original", "converse", "inverse", "contrapositive")
FORM_LABEL = {
    "original": "元 P→Q",
    "converse": "逆 Q→P",
    "inverse": "裏 ¬P→¬Q",
    "contrapositive": "対偶 ¬Q→¬P",
}


def _forms(item: dict) -> dict[str, dict]:
    return {f.get("form"): f for f in item.get("forms") or [] if isinstance(f, dict)}


def _counts(form: dict | None) -> tuple[int, int] | None:
    if not form:
        return None
    n, hold = form.get("n"), form.get("hold")
    if type(n) is not int or type(hold) is not int or n < 0 or hold < 0 or hold > n:
        return None
    return n, hold


def _agree(values: list[int]) -> int | str | None:
    if not values:
        return None
    if any(v != values[0] for v in values):
        return "不一致:" + "/".join(str(v) for v in values)
    return values[0]


def contingency(item: dict) -> dict[str, int | str | None]:
    """P∧Q, P∧¬Q, ¬P∧Q, ¬P∧¬Q from n and hold.

    Two forms that imply different counts stay as ``不一致`` rather than one of them being picked.
    An empty antecedent (no if and no if_any) makes the ¬P cells 0, because every unit is P.
    """
    forms = _forms(item)
    original, converse = _counts(forms.get("original")), _counts(forms.get("converse"))
    inverse, contra = _counts(forms.get("inverse")), _counts(forms.get("contrapositive"))
    pq, p_not_q, not_p_q, not_p_not_q = [], [], [], []
    if original:
        pq.append(original[1])
        p_not_q.append(original[0] - original[1])
    if converse:
        pq.append(converse[1])
        not_p_q.append(converse[0] - converse[1])
    if contra:
        not_p_not_q.append(contra[1])
        p_not_q.append(contra[0] - contra[1])
    if inverse:
        not_p_not_q.append(inverse[1])
        not_p_q.append(inverse[0] - inverse[1])
    empty_if = not item.get("if") and not item.get("if_any")
    if empty_if:
        not_p_q.append(0)
        not_p_not_q.append(0)
    return {
        "P∧Q": _agree(pq),
        "P∧¬Q": _agree(p_not_q),
        "¬P∧Q": _agree(not_p_q),
        "¬P∧¬Q": _agree(not_p_not_q),
    }


def _cell(value) -> str:
    if value is None:
        return "不明"
    return str(value)


def empty_antecedent(item: dict) -> bool:
    return not item.get("if") and not item.get("if_any")


def format_contingency_cell(item: dict, key: str) -> str:
    """2×2 のマス。空の前件で ¬P 行に置く 0 は注釈付き。"""
    value = contingency(item)[key]
    if empty_antecedent(item) and key in ("¬P∧Q", "¬P∧¬Q") and value == 0:
        return "0（前件が空）"
    return _cell(value)


COUNTEREXAMPLE_PAIR_LABELS = (
    ("original", "contrapositive"),
    ("converse", "inverse"),
)


def _form_cell(form: dict | None) -> str:
    counts = _counts(form)
    if counts is None:
        return "不明"
    n, hold = counts
    return f"{hold}/{n}（反例 {n - hold}）"


def _form_line(name: str, form: dict | None) -> str:
    text = f"{FORM_LABEL[name]}: {_form_cell(form)}"
    if isinstance(form, dict) and "rate" in form:
        text += " rate=" + json.dumps(form.get("rate"), ensure_ascii=False)
    return text


def render_forms_table(item: dict, *, heading: bool = True) -> str:
    """C1. Contingency 2×2, then the four forms as a 2×2. Both carry the registration label."""
    label = registration_status(item)
    forms = _forms(item)
    ident = item.get("id", "")
    lines = []
    if heading:
        lines.extend([f"［{label}］ {ident}", ""])
    lines.extend(
        [
            "|  | Q | ¬Q |",
            "|---|---|---|",
            f"| P | {format_contingency_cell(item, 'P∧Q')} | {format_contingency_cell(item, 'P∧¬Q')} |",
            f"| ¬P | {format_contingency_cell(item, '¬P∧Q')} | {format_contingency_cell(item, '¬P∧¬Q')} |",
            "",
            "|  |  |",
            "| --- | --- |",
            f"| {_form_line('original', forms.get('original'))} | {_form_line('converse', forms.get('converse'))} |",
            f"| {_form_line('inverse', forms.get('inverse'))} | {_form_line('contrapositive', forms.get('contrapositive'))} |",
        ]
    )
    return "\n".join(lines)


def counterexample_lists_equal(left, right) -> bool:
    """反例配列が同じ単位の並びか。記録の順をそのまま比べる。"""
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    a = left.get("counterexamples") or []
    b = right.get("counterexamples") or []
    if len(a) != len(b):
        return False
    return [row.get("unit") for row in a if isinstance(row, dict)] == [
        row.get("unit") for row in b if isinstance(row, dict)
    ]


def _value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _atom(cond: dict) -> str:
    return f"{cond['col']}{cond['op']}{_value(cond['value'])}"


def _and(conds: list, *, group: bool) -> str | None:
    if not conds:
        return None
    parts = [_atom(c) for c in conds]
    body = " ∧ ".join(parts)
    if group and len(parts) > 1:
        return f"({body})"
    return body


def antecedent(item: dict) -> str | None:
    parts = []
    if item.get("if"):
        text = _and(item["if"], group=False)
        if text:
            parts.append(text)
    groups = []
    for group in item.get("if_any") or []:
        text = _and(group, group=True)
        if text:
            groups.append(text)
    if len(groups) == 1:
        parts.append(groups[0])
    elif groups:
        parts.append("(" + " ∨ ".join(groups) + ")")
    if not parts:
        return None
    return " ∧ ".join(parts)


def consequent(item: dict) -> str | None:
    return _and(item.get("then") or [], group=False)


def _negate(expr: str) -> str:
    return f"¬({expr})"


def logic_lines(item: dict) -> list[str]:
    """C2. if / if_any / then as ∧ ∨ ¬ →. Empty antecedent stays 「条件なし」."""
    ant, cons = antecedent(item), consequent(item)
    if cons is None:
        return ["（then がない）"]
    if ant is None:
        return [
            f"元: （条件なし） → {cons}",
            "逆: （if も if_any も空）",
            "裏: （if も if_any も空）",
            f"対偶: ¬({cons}) → （if も if_any も空）",
        ]
    return [
        f"元: {ant} → {cons}",
        f"逆: {cons} → {ant}",
        f"裏: {_negate(ant)} → {_negate(cons)}",
        f"対偶: {_negate(cons)} → {_negate(ant)}",
    ]


def render_logic(item: dict) -> str:
    label = registration_status(item)
    body = "\n".join(logic_lines(item))
    return f"［{label}］ {item.get('id', '')}\n{body}"


def render_item(item: dict) -> str:
    return render_forms_table(item) + "\n\n" + render_logic(item)


def load_items(results: Path) -> tuple[list[dict], dict[str, bool]]:
    present, out = {}, []
    for name in ("propositions.jsonl", "sets.jsonl"):
        path = Path(results) / name
        present[name] = path.is_file()
        if present[name]:
            out += [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(present.values()):
        raise FileNotFoundError(f"結果が読めない: {results}")
    return out, present


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="四つの形の 2×2 と条件の論理記号を出す")
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--id", help="この ID だけ。省略すると読み込んだ順")
    args = parser.parse_args(argv)
    try:
        items, present = load_items(args.results)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.id:
        needed = "sets.jsonl" if args.id.startswith("E") else "propositions.jsonl" if args.id.startswith("P") else None
        if needed and not present.get(needed):
            print(f"結果が読めない: {needed}", file=sys.stderr)
            return 1
        items = [item for item in items if item.get("id") == args.id]
        if not items:
            print(f"{args.id} は判定済みの結果にない", file=sys.stderr)
            return 1
    print("\n\n".join(render_item(item) for item in items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
