"""Run trusted argv checks sequentially; preserve bounded evidence locally.

This is NOT a sandbox. Review commands before running. No implicit shell,
network call, dependency install, environment dump, or model call is performed.
"""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import selectors
import signal
import subprocess
import time
import uuid
from common import main_guard, within, write_json

STATUSES = {"pass", "fail", "timeout", "not_run"}


def validate(config, root):
    if not isinstance(config, dict):
        raise ValueError("config must be an object")
    checks = config.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("checks must be a non-empty list")
    ids = set()
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("each check must be an object")
        name = check.get("id", "")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", name) or name in ids:
            raise ValueError("check IDs must be unique safe identifiers")
        ids.add(name)
        if "manual" in check and not isinstance(check["manual"], str):
            raise ValueError("manual must describe the human check")
        if "manual" in check and "argv" in check:
            raise ValueError("a check cannot be both manual and executable")
        if "manual" not in check:
            argv = check.get("argv")
            if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x and '\x00' not in x for x in argv):
                raise ValueError("argv must be a non-empty string array")
        timeout = check.get("timeout_seconds", 30)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= 600:
            raise ValueError("timeout_seconds must be finite, >0 and <=600")
        cwd = within(root, check.get("cwd", "."))
        if not cwd.is_dir():
            raise ValueError(f"missing cwd: {cwd}")
    return checks


def kill_group(process):
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_check(check, root, log_path, limit):
    started = time.monotonic()
    result = {"check_id": check["id"], "status": "not_run", "exit_code": None,
              "duration": 0, "evidence_path": None}
    if "manual" in check:
        result["reason"] = check["manual"]
        return result
    result["evidence_path"] = str(log_path)
    result["argv"] = check["argv"]
    try:
        process = subprocess.Popen(check["argv"], cwd=within(root, check.get("cwd", ".")),
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, start_new_session=True)
    except OSError as exc:
        log_path.write_text(str(exc), encoding="utf-8")
        result["reason"] = "command could not start"
        result["duration"] = round(time.monotonic() - started, 4)
        return result
    timed_out = False
    received = 0
    try:
        with selectors.DefaultSelector() as selector, log_path.open("wb") as stream:
            selector.register(process.stdout, selectors.EVENT_READ)
            while selector.get_map():
                remaining = check.get("timeout_seconds", 30) - (time.monotonic() - started)
                if remaining <= 0:
                    timed_out = True
                    break
                for key, _ in selector.select(min(remaining, 0.1)):
                    chunk = os.read(key.fileobj.fileno(), 8192)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    if received < limit:
                        stream.write(chunk[:limit - received])
                    received += len(chunk)
            if not timed_out:
                remaining = check.get("timeout_seconds", 30) - (time.monotonic() - started)
                try:
                    process.wait(timeout=max(remaining, 0.001))
                except subprocess.TimeoutExpired:
                    timed_out = True
    finally:
        # A check must not leave background children behind, even on success.
        kill_group(process)
        process.wait()
        process.stdout.close()
    result.update(status="timeout" if timed_out else ("pass" if process.returncode == 0 else "fail"),
                  exit_code=process.returncode, duration=round(time.monotonic() - started, 4),
                  output_truncated=received > limit)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", default=".sprint/runs")
    parser.add_argument("--max-log-bytes", type=int, default=131072)
    args = parser.parse_args()
    if os.name != "posix":
        raise ValueError("POSIX process groups required (Linux/macOS)")
    if not 1024 <= args.max_log_bytes <= 1048576:
        raise ValueError("max-log-bytes must be 1024..1048576")
    root = Path(args.root).resolve(strict=True)
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    checks = validate(config, root)  # Validate all before executing any.
    run_dir = within(root, args.output_dir) / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    run_dir.mkdir(parents=True, exist_ok=False)
    results = []
    for check in checks:
        result = run_check(check, root, run_dir / (check["id"] + ".log"), args.max_log_bytes)
        if result["evidence_path"]:
            result["evidence_path"] = str(Path(result["evidence_path"]).relative_to(root))
        results.append(result)
        print(f'{result["check_id"]}: {result["status"]} ({result["duration"]}s)')
    report = {"schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
              "checks": results, "all_passed": all(x["status"] == "pass" for x in results)}
    write_json(run_dir / "report.json", report)
    print(f"REPORT={run_dir / 'report.json'}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard(main))
