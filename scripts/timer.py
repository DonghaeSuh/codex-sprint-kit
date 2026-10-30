"""Persistent local timer. No hooks, configuration changes, or automatic stopping."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time
from common import main_guard, within, write_json


def status(state, now):
    start, budget = state["started_epoch"], state["budget_minutes"]
    if (isinstance(start, bool) or not isinstance(start, (int, float))
            or not math.isfinite(start) or start < 0 or not isinstance(budget, int)
            or isinstance(budget, bool) or not 1 <= budget <= 1440):
        raise ValueError("invalid timer state")
    if now < start:
        raise ValueError("clock is earlier than recorded start; confirm platform time")
    elapsed = now - start
    # Explicit schedules: 60-minute rehearsal and 180-minute task.
    limits = [5, 20, 45, 125, 160, 170, 180] if budget == 180 else [v * budget / 60 for v in (5, 12, 27, 42, 47, 55, 60)]
    phases = ("setup", "intake", "baseline", "experiment", "verify", "freeze", "delivery")
    phase = next((p for p, end in zip(phases, limits) if elapsed < end * 60), "expired")
    return {"started_at": datetime.fromtimestamp(start, timezone.utc).isoformat(),
            "budget_minutes": budget, "elapsed_seconds": round(elapsed),
            "remaining_seconds": max(0, math.ceil(budget * 60 - elapsed)),
            "phase": phase, "feature_freeze_after_minutes": limits[4],
            "advisory": "Platform timer takes precedence; no automatic AI/process shutdown."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "status"))
    parser.add_argument("--root", default=".")
    parser.add_argument("--minutes", type=int)
    parser.add_argument("--elapsed-minutes", type=float, default=0,
                        help="Only on first start: already elapsed time from platform display")
    args = parser.parse_args()
    root = Path(args.root).resolve(strict=True)
    path = within(root, ".sprint/timer.json")
    if not math.isfinite(args.elapsed_minutes) or args.elapsed_minutes < 0:
        raise ValueError("elapsed-minutes must be finite and nonnegative")
    if args.action == "start":
        if args.minutes is None or not 1 <= args.minutes <= 1440:
            raise ValueError("start requires --minutes 1..1440")
        if args.elapsed_minutes > args.minutes:
            raise ValueError("elapsed time exceeds budget")
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing["budget_minutes"] != args.minutes:
                raise ValueError("existing budget differs; timer was preserved")
            print("KEEP existing timer (start/elapsed arguments do not reset it)")
        else:
            write_json(path, {"schema_version": 1, "started_epoch": time.time() - args.elapsed_minutes * 60,
                              "budget_minutes": args.minutes})
    elif args.minutes is not None or args.elapsed_minutes:
        raise ValueError("status does not accept start arguments")
    state = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(status(state, time.time()), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main_guard(main))
