"""Bounded Linux CI evidence for identical linkcheck shards; no performance gate."""
import argparse
import collections
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

SEED = 7
ROUNDS = 4
LIMIT_MIB = 128
SAMPLE_SECONDS = 0.02
WORKERS = (1, 2, 2, 1, 1, 2)


def rss_rows():
    rows = {}
    try:
        entries = list(Path("/proc").iterdir())
    except OSError:
        return rows
    for entry in entries:
        if not entry.name.isdecimal():
            continue
        try:
            fields = (entry / "stat").read_text().rsplit(")", 1)[1].split()
            rows[int(entry.name)] = (int(fields[1]), int(fields[21]) * os.sysconf("SC_PAGE_SIZE"))
        except (OSError, ValueError, IndexError):
            continue
    return rows


def rss_total(rows, assigned):
    roots = set(assigned)
    if not rows or not roots.intersection(rows):
        return None
    selected = roots.intersection(rows)
    while True:
        extra = {pid for pid, (parent, _) in rows.items() if parent in selected} - selected
        if not extra:
            return sum(rows[pid][1] for pid in selected)
        selected.update(extra)


def junit_cases(xml):
    return [[case.attrib["classname"], case.attrib["name"],
             next((tag for tag in ("failure", "error", "skipped") if case.find(tag) is not None), "pass")]
            for case in ET.parse(xml).iter("testcase")]


def unsharded_oracle(prefix, env, work):
    xml = work / "unsharded.xml"
    with (work / "unsharded.log").open("w") as stream:
        subprocess.run([*prefix, f"--junitxml={xml}", "tests/test_linkcheck.py"],
                       env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=40, check=True)
    return junit_cases(xml)


def sample_run(prefix, env, work, workers):
    def start(round_id):
        xml = work / f"{round_id}.xml"
        log = work / f"{round_id}.log"
        with log.open("w") as stream:
            command = [*prefix, "-p", "nagoyaction", "--localci-repeat", str(ROUNDS),
                       "--localci-round", str(round_id), "--localci-seed", str(SEED),
                       f"--junitxml={xml}", "tests/test_linkcheck.py"]
            process = subprocess.Popen(command, env=env, stdout=stream, stderr=subprocess.STDOUT)
        return process, xml, log

    clock = time.monotonic()
    cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
    active = {}
    next_round = 1
    reports = {}
    aggregate = None
    per_worker = {}
    try:
        while active or next_round <= ROUNDS:
            while len(active) < workers and next_round <= ROUNDS:
                active[next_round] = start(next_round)
                next_round += 1
            rows = rss_rows()
            combined = rss_total(rows, [job[0].pid for job in active.values()])
            if combined is not None:
                aggregate = max(aggregate or 0, combined)
            for index, (child, xml, log) in list(active.items()):
                sampled = rss_total(rows, [child.pid])
                if sampled is not None:
                    per_worker[index] = max(per_worker.get(index, 0), sampled)
                if (code := child.poll()) is None:
                    continue
                if code:
                    raise RuntimeError(f"shard {index} failed ({code}): {log.read_text()[-1500:]}")
                reports[index] = junit_cases(xml)
                del active[index]
            if time.monotonic() - clock > 40:
                raise TimeoutError("linkcheck comparison exceeded 40 seconds")
            if active:
                time.sleep(SAMPLE_SECONDS)
    finally:
        for child, _, _ in active.values():
            if child.poll() is None:
                child.kill()
            child.wait()
    elapsed = time.monotonic() - clock
    end = resource.getrusage(resource.RUSAGE_CHILDREN)
    counts = collections.Counter(state for cases in reports.values() for _, _, state in cases)
    return {"workers": workers, "wall_seconds": elapsed,
            "child_cpu_seconds": end.ru_utime + end.ru_stime - cpu.ru_utime - cpu.ru_stime,
            "checks_per_second": sum(counts.values()) / elapsed,
            "sampled_aggregate_rss_bytes": aggregate,
            "sampled_worker_tree_rss_bytes": per_worker, "shards": reports, "outcomes": dict(counts)}


def memory_probe(env):
    child = subprocess.run(
        [sys.executable, "-S", "-c",
         "import resource,sys; n=int(sys.argv[1]); resource.setrlimit(resource.RLIMIT_AS,(n,n)); "
         "\ntry: bytearray(2*n)\nexcept MemoryError: sys.exit(17)\nsys.exit(1)", str(LIMIT_MIB * 2**20)],
        env=env, capture_output=True, check=False, timeout=5,
    )
    return {"limit_mib": LIMIT_MIB, "limit_kind": "one child RLIMIT_AS, virtual address space",
            "memory_error_observed": child.returncode == 17, "exit_code": child.returncode}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    env.pop("PYTEST_ADDOPTS", None)
    env["PYTHONPATH"] = str(Path.cwd())
    prefix = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
    preparation = os.environ.get("LOCALCI_PROBE_PREP_SECONDS")
    result = {"seed": SEED, "rounds": ROUNDS,
              "dependency_sync_seconds": int(preparation) if preparation else None,
              "preparation": "excluded from runs; Actions sync elapsed does not distinguish cold/warm",
              "rss_scope": "sampled Linux worker trees, sums RSS including shared pages; not a cgroup high-water mark",
              "sample_delay_seconds": SAMPLE_SECONDS, "runs": [], "acceptance": False,
              "github_event_sha": os.environ.get("GITHUB_SHA")}
    try:
        with tempfile.TemporaryDirectory(prefix="localci-comparison-") as tmp:
            work = Path(tmp)
            result["unsharded_oracle"] = unsharded_oracle(prefix, env, work)
            for workers in WORKERS:
                result["runs"].append(sample_run(prefix, env, work, workers))
        result["memory_budget"] = memory_probe(env)
        first = result["runs"][0]
        identities = [tuple(case[:2]) for cases in first["shards"].values() for case in cases]
        oracle = result["unsharded_oracle"]
        oracle_identities = [tuple(case[:2]) for case in oracle]
        total = len(oracle_identities)
        result["baseline_check_count"] = total
        result["unsharded_parity"] = (total > 0 and total == len(set(oracle_identities))
                                      and all(case[2] == "pass" for case in oracle)
                                      and collections.Counter(identities) == collections.Counter(oracle_identities))
        result["rss_available_in_all_runs"] = all(run["sampled_aggregate_rss_bytes"] is not None for run in result["runs"])
        result["acceptance"] = (result["unsharded_parity"]
                                and all(set(run["shards"]) == set(range(1, ROUNDS + 1))
                                        and run["shards"] == first["shards"]
                                        and run["outcomes"] == {"pass": total}
                                        for run in result["runs"])
                                and result["rss_available_in_all_runs"]
                                and result["memory_budget"]["memory_error_observed"])
    except (OSError, RuntimeError, subprocess.SubprocessError, ET.ParseError) as exc:
        result["error"] = str(exc)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks": result.get("baseline_check_count"), "runs": len(result["runs"]),
                      "unsharded_parity": result.get("unsharded_parity"),
                      "rss_available": result.get("rss_available_in_all_runs"),
                      "memory_limit_observed": result.get("memory_budget", {}).get("memory_error_observed"),
                      "acceptance": result["acceptance"]}))
    return 0 if result["acceptance"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
