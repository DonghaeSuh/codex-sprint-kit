"""Bounded CSV/TSV inventory, without raw rows or sample values. Local use only."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
from common import main_guard, within

SKIP = {"node_modules", "venv", "dist", "build", "__pycache__", "codex-sprint-kit"}


def summarize(path, max_bytes, max_rows):
    with path.open("rb") as stream:
        raw = stream.read(max_bytes + 1)
    partial = len(raw) > max_bytes
    reasons = ["byte_limit"] if partial else []
    raw = raw[:max_bytes]
    if partial:
        # Do not count an obviously cut line as a complete record.
        raw = raw.rsplit(b"\n", 1)[0] if b"\n" in raw else b""
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return {"status": "unsupported_encoding", "partial": True, "raw_values_printed": False}
    reader = csv.reader(io.StringIO(text, newline=""), delimiter="\t" if path.suffix.lower() == ".tsv" else ",", strict=True)
    result = {"rows_scanned": 0, "ragged_rows": 0, "blank_rows": 0,
              "partial": partial, "limits_reached": reasons, "raw_values_printed": False}
    try:
        header = next(reader, [])
        result["column_count"] = len(header)
        # File/header names are metadata; values never appear in output.
        columns = [{"name": h[:80], "missing": 0, "observed_nonempty": 0, "_seen": set()} for h in header[:50]]
        result["duplicate_headers"] = len(set(header)) != len(header)
        result["empty_headers"] = sum(not h.strip() for h in header)
        if len(header) > 50:
            reasons.append("column_limit")
        for row in reader:
            if result["rows_scanned"] >= max_rows:
                reasons.append("row_limit")
                break
            result["rows_scanned"] += 1
            result["ragged_rows"] += len(row) != len(header)
            result["blank_rows"] += not row or all(not v.strip() for v in row)
            for i, column in enumerate(columns):
                value = row[i].strip() if i < len(row) else ""
                column["missing"] += not bool(value)
                column["observed_nonempty"] += bool(value)
                if value and len(column["_seen"]) < 256:
                    # Never retain unbounded cell content in the uniqueness cache.
                    column["_seen"].add(hashlib.sha256(value.encode()).digest())
        for column in columns:
            seen = column.pop("_seen")
            column["distinct_count"] = len(seen)
            column["distinct_count_capped"] = len(seen) == 256
        result["columns"] = columns
    except csv.Error:
        reasons.append("csv_parse_error")  # Never echo offending content.
    result["partial"] = bool(reasons)
    result["status"] = "partial" if reasons else ("empty" if not result.get("column_count") else "complete")
    return result


def inspect(root, target, max_files, max_bytes, max_rows):
    report = {"files": [], "scan_partial": False, "raw_values_printed": False}
    visited = 0
    if target.is_file():
        candidates = [(target.parent, [], [target.name])]
    else:
        candidates = os.walk(target, followlinks=False)
    for folder, dirs, names in candidates:
        visited += 1
        if visited > 2000:
            report["scan_partial"] = True
            return report
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in SKIP and not (Path(folder) / d).is_symlink())
        for name in sorted(names):
            visited += 1
            if visited > 2000:
                report["scan_partial"] = True
                return report
            path = Path(folder) / name
            if name.startswith(".") or path.is_symlink() or path.suffix.lower() not in (".csv", ".tsv"):
                continue
            if len(report["files"]) == max_files:
                report["scan_partial"] = True
                return report
            resolved = within(root, path)
            summary = summarize(resolved, max_bytes, max_rows)
            summary["path"] = str(path.relative_to(root))
            report["files"].append(summary)
    report["no_supported_files"] = not report["files"]
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--path", default="uploads")
    parser.add_argument("--max-files", type=int, default=20)
    parser.add_argument("--max-rows", type=int, default=10000)
    parser.add_argument("--max-bytes", type=int, default=2097152)
    args = parser.parse_args()
    if not 1 <= args.max_files <= 100 or not 1 <= args.max_rows <= 100000 or not 1024 <= args.max_bytes <= 10485760:
        raise ValueError("limits: files 1..100, rows 1..100000, bytes 1024..10485760")
    root = Path(args.root).resolve(strict=True)
    lexical = root / args.path
    if lexical.is_symlink():
        raise ValueError("explicit symlink target refused")
    target = within(root, args.path)
    if not target.exists():
        raise ValueError("input path does not exist")
    print(json.dumps(inspect(root, target, args.max_files, args.max_bytes, args.max_rows), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main_guard(main))
