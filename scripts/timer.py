"""Persistent local timer. No hooks, configuration changes, or automatic stopping."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time
from common import main_guard, within, write_json


CHECKPOINTS = (
    ("setup", "과제 시작 시각·제출 조건·환경을 확인할 차례입니다.",
     "과제 안내와 기존 기록을 확인하고 첫 작업을 시작해줘."),
    ("intake", "필수 요구사항과 실무자 질문을 좁힐 차례입니다.",
     "필수 조건과 확인할 질문을 정리하고 답변 대기 중 가능한 작업을 진행해줘."),
    ("baseline", "첫 입력부터 결과까지 동작하는 기준점을 만들 차례입니다.",
     "핵심 흐름을 작게 완성하고 실제 검사 결과를 기록해줘."),
    ("experiment", "기준 결과와 비교하며 중요한 실패를 개선할 차례입니다.",
     "가장 중요한 실패 하나를 골라 남은 단계 시간 안에서 실험해줘."),
    ("verify", "실험을 정리하고 필수 검사와 수동 확인을 진행할 차례입니다.",
     "요구사항별 근거와 실제 제출 파일을 점검하고 내가 확인할 화면 동작을 알려줘."),
    ("freeze", "새 기능을 멈추고 제출을 막는 결함만 처리할 차례입니다.",
     "기능을 동결하고 남은 결함·미검증 항목·제출 준비 상태를 정리해줘."),
    ("defense", "제출 전 설명 자료를 정리하고 읽을 차례입니다.",
     "현재 구현·검증·ADR을 근거로 DEFENSE.md를 정리하고 3분 안에 읽을 핵심을 설명해줘."),
    ("explain", "핵심 동작과 선택 이유를 본인 말로 설명해 볼 차례입니다.",
     "내가 핵심 흐름과 선택 이유를 설명할 수 있도록 제출 전 이해 확인을 진행해줘."),
    ("submit", "최종 저장·필수 파일을 확인하고 사용자가 제출할 차례입니다.", None),
    ("expired", "로컬 작업 시간이 끝났습니다. 플랫폼 시간을 확인하고 AI 금지 단계에서는 작업을 중단하세요.", None),
)


def checkpoints(start, budget):
    minutes = ([0, 5, 20, 45, 125, 160, 165, 170, 175, 180] if budget == 180
               else [v * budget / 60 for v in (0, 5, 12, 27, 42, 47, 50, 55, 58, 60)])
    return [{"id": ident, "after_minutes": minute,
             "at": datetime.fromtimestamp(start + minute * 60, timezone.utc).isoformat(),
             "message": message, "suggested_request": request}
            for minute, (ident, message, request) in zip(minutes, CHECKPOINTS)]


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
    schedule = checkpoints(start, budget)
    current = max(i for i, checkpoint in enumerate(schedule) if elapsed >= checkpoint["after_minutes"] * 60)
    upcoming = schedule[current + 1] if current + 1 < len(schedule) else None
    return {"started_at": datetime.fromtimestamp(start, timezone.utc).isoformat(),
            "checked_at": datetime.fromtimestamp(now, timezone.utc).isoformat(),
            "deadline_at": datetime.fromtimestamp(start + budget * 60, timezone.utc).isoformat(),
            "budget_minutes": budget, "elapsed_seconds": round(elapsed),
            "remaining_seconds": max(0, math.ceil(budget * 60 - elapsed)),
            "phase": phase, "feature_freeze_after_minutes": limits[4],
            "checkpoint": schedule[current], "next_checkpoint": upcoming,
            "seconds_until_next_checkpoint": (max(0, math.ceil(upcoming["after_minutes"] * 60 - elapsed))
                                              if upcoming else None),
            "advisory": "Platform timer and AI permissions take precedence. Suggestions require an agent check; no background alerts or automatic shutdown."}


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
