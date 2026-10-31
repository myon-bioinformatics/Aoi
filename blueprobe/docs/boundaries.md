# Boundaries of responsibility: BlueProbe / QueRyu / web-ui

> A proposal. web-ui and Aoi code are not moved here. Whatever is agreed is moved within each repository.

| | Responsible for | Not responsible for |
|---|---|---|
| **QueRyu** (Aoi/queryu) | Fetching (intervals, conditional GET, recording 404s), caching, provenance (manifest), writing datasets | How to read the body (parser), judging notation |
| **BlueProbe** | **Looking at** saved bodies: observing HTML/CSS/DOM structure, extraction, notation normalization, the report contract, the format of observation evidence | Fetching, caching, network, judging wins/losses or causes |
| **web-ui** | The side that **emits** HTML from Python: `web_ui.render_document`, shared CSS/JS, the HTML structure contract (contract/v1) | Methodology for observing and extracting external pages |

## Seams

- QueRyu → BlueProbe: the supplier contract ([snapshot.md](contract/v1/snapshot.md)). QueRyu is one supplier
- BlueProbe → QueRyu / SakAnalytics: the report contract ([report.md](contract/v1/report.md))
- web-ui → BlueProbe: HTML emitted by web-ui has the contract/v1 structure, so to BlueProbe it is "one of the things to read"

## What we'd like to move to BlueProbe (proposal)

| Current location | Contents | Proposal |
|---|---|---|
| web-ui `docs/evidence/*-dom.json` | Evidence of observed DOM (listing `source_url`, `observed_date`, `http_response.sha256`, `region`, `raw_html` / `dom_html` / `text_content` / `inner_text` / `page_text`) | BlueProbe holds the format definition as a contract (e.g. `dom-evidence/1`). web-ui's evidence follows that format |
| web-ui `docs/local-dom-lab.md`, `tests/integration/test_gradio_dom.py` | Comparing rendered `innerText` with extraction results from saved DOM | The idea of "comparing observations" goes in BlueProbe's docs. Serving with Gradio and launching browsers stay in web-ui |
| browser-test-kit `scripts/page_text.py` | Body text extraction | Don't copy. Reference it at a pinned SHA and keep the comparison observations on the BlueProbe side |

What stays in web-ui: serving (generating Gradio/HTML), CSS/themes, the HTML structure contract.

## Open: owner of the "looking" side

`inspect_cache` stays for now, still emitting a DeprecationWarning.

The "fetching and looking" side (supplying saved bodies, and generating and checking mcp-toolcall-lab's snapshot evidence = `html-snapshot/1`)
may be more naturally owned by QueRyu than BlueProbe, since QueRyu already has fetching, provenance, and `Cache.snapshot()`.
In that case BlueProbe narrows to "reading and reporting observations" and holds only the supplier contract (`docs/contract/v1/snapshot.md`).
Where to put it is undecided (open question).
