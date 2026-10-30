"""Build a bounded handoff from explicit local state and verification evidence."""
import argparse
import json
from pathlib import Path
from common import main_guard, within, write_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve(strict=True)
    report_path = within(root, args.report)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    lines = ["# Session handoff", "", f"Evidence: {report_path.relative_to(root)}",
             f"Measured: {report.get('created_at', 'unknown')}",
             "Historical evidence only: rerun affected checks after edits.", ""]
    for name in ("STATE.md", "ACCEPTANCE.md"):
        source = within(root, ".sprint/" + name)
        lines += [f"## {name}", source.read_text(encoding="utf-8")[:3000] if source.exists() else "MISSING", ""]
    lines += ["## Verification (max 30 checks)"]
    for check in report["checks"][:30]:
        lines.append(f"- {check['check_id']}: {check['status']}; evidence={check.get('evidence_path')}")
    if len(report["checks"]) > 30:
        lines.append("Additional checks omitted; open source report.")
    write_new(within(root, args.output), "\n".join(lines) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main_guard(main))
