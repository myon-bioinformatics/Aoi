# c001-chunichi NPB season archive (2026-10-25)

Packaged for Claude Code / offline use from Aoi cycle `cycles/c001-chunichi`.

## Included
- `outputs/season.jsonl` — team×season metrics (primary season panel)
- `outputs/fetched/*.jsonl` — QueRyu fetch provenance for calendar/linescore/team pages (URLs + sha256; not HTML bodies)
- `outputs/ledger.jsonl`, `cumulative.jsonl`, `propositions.jsonl`
- `from-cycle-001/outputs/season.jsonl` + `ledger.jsonl` (earlier cycle copy)
- `npb-configuration.md`, cycle `README.md`

## Not included (not on the packaging host)
- `data/raw/npb_calendar/` HTML blob cache (~gitignored local)
- `data/observations/npb_calendar/games.jsonl` (built from cache; also gitignored)

Rebuild games.jsonl from Aoi root when a cache exists:

```bash
PYTHONPATH=blueprobe uv run python queryu/queryu.py --source npb_calendar --years 2012-2025 \
  --cache data/raw/npb_calendar --out data/observations/npb_calendar/games.jsonl --offline
```

Online refill is polite (default 3s wait) and can take many hours.
