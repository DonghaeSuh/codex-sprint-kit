"""Validate source records offline; does not claim legal or runtime approval."""
import argparse
import json
from pathlib import Path
import re
from common import main_guard


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="sources.lock.json")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    ids = set()
    for source in manifest["sources"]:
        for key in ("id", "url", "revision", "license", "use", "decision", "verification", "evidence"):
            if not source.get(key):
                raise ValueError(f"source missing {key}")
        if source["id"] in ids:
            raise ValueError("duplicate source ID")
        ids.add(source["id"])
        if not re.fullmatch(r"[0-9a-f]{40}", source["revision"]):
            raise ValueError("Git source revision must be a full SHA")
        if source["use"] == "vendored" and source["license"] in ("unknown", "NOASSERTION", "per-file-review-required"):
            raise ValueError("vendoring requires resolved licensing")
        if source["verification"] not in ("source", "static", "executed", "compared"):
            raise ValueError("unknown verification level")
    print(f"PASS: {len(ids)} source records; metadata only, not runtime certification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main_guard(main))
