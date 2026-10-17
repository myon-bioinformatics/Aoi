"""Acquire R001 data with the existing cache/parser; respect environment proxies."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "BlueProbe"), str(ROOT / "BlueProbe/baseball"), str(ROOT / "QueRyu")]
import httpx
import npb_calendar
from queryu import Cache, PoliteFetcher, UA


def main():
    cache = Cache(ROOT / "data/raw/npb_calendar")
    # PR #2's explicit HTTPTransport bypasses proxy settings in this environment.
    # Inject a proxy-aware client; do not alter the upstream acquisition module.
    with httpx.Client(headers={"User-Agent": UA}, timeout=45, follow_redirects=True) as client:
        fetcher = PoliteFetcher(cache, wait=3.0, client=client)
        for year in range(2013, 2026):
            for key, url, group in npb_calendar.pages([year]):
                fetcher.get(key, url, group)
            print(year, "calendar pages cached", flush=True)
        print("HTTP requests:", fetcher.requests)



if __name__ == "__main__":
    main()
