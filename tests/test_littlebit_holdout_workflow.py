"""The focused holdout job also runs PythDRagoras's Node parity suite."""
from pathlib import Path


def test_holdout_job_provisions_node_before_parity_tests():
    workflow = (Path(__file__).resolve().parents[1] /
                '.github/workflows/littlebit-holdout-drift.yml').read_text()
    job = workflow.split('\n  provenance:\n', 1)[1]
    setup = job.index('uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1')
    version = job.index("node-version: '26'", setup)
    guard = job.index('run: node -e "if (+process.versions.node.split(\'.\')[0] < 24) process.exit(1)"', version)
    suite = job.index('uv run --locked --python 3.14.8 pytest')
    assert setup < version < guard < suite
    assert 'pythdragoras/tests -k littlebit' in job[suite:]
    # Provisioning Node must not weaken the independent provenance guard.
    assert 'HOLDOUT_SOURCE_PROVENANCE:' not in job
