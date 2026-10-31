"""Collect the standalone subscription-pack regressions in ordinary repository CI."""
from pathlib import Path
import runpy

_PACK = (Path(__file__).resolve().parents[1] / 'research' / 'staple-price-survey'
         / 'adjacent_subscription_engel_shares')
EvidenceTests = runpy.run_path(str(_PACK / 'test_subscription_engel_shares.py'))['EvidenceTests']
