"""Synthetic contract tests; no answer implementation or network."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solution", required=True)
    args = parser.parse_args()
    solution = Path(args.solution).resolve(strict=True)
    cases = [
        ("weighted", "batch_id,good,total\nA,9,10\nB,1,100\n", 10 / 110),
        ("duplicates", "batch_id,good,total\nA,1,2\nA,2,3\n", 0.6),
        ("empty", "batch_id,good,total\n", None),
        ("negative", "batch_id,good,total\nA,-1,2\n", None),
        ("over-total", "batch_id,good,total\nA,3,2\n", None),
        ("zero-total", "batch_id,good,total\nA,0,0\n", None),
        ("missing-column", "batch_id,good\nA,1\n", None),
        ("fraction", "batch_id,good,total\nA,0.5,2\n", None),
        ("empty-id", "batch_id,good,total\n,1,2\n", None),
    ]
    failures = []
    with tempfile.TemporaryDirectory(prefix="sprint-grade-") as tmp:
        for name, data, expected in cases:
            path = Path(tmp) / (name + ".csv")
            path.write_text(data, encoding="utf-8")
            try:
                run = subprocess.run([sys.executable, str(solution), str(path)], capture_output=True, text=True, timeout=3)
                if expected is None:
                    assert run.returncode != 0 and run.stderr.strip()
                else:
                    assert run.returncode == 0, run.stderr
                    result = json.loads(run.stdout)
                    assert abs(result["yield"] - expected) < 1e-9
                    expected_batches = {"A": {"good": 9, "total": 10}, "B": {"good": 1, "total": 100}} if name == "weighted" else {"A": {"good": 3, "total": 5}}
                    assert result["batches"] == expected_batches
                print(name + ": pass")
            except (AssertionError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
                failures.append(name)
                print(name + ": fail " + str(exc)[:200])
    print(json.dumps({"passed": len(cases)-len(failures), "total": len(cases), "failed": failures}))
    return bool(failures)

if __name__ == "__main__":
    raise SystemExit(main())
