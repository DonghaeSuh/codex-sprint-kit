"""Small, local-only helpers. Python 3.10+, no third-party dependencies."""
import json
from pathlib import Path


def within(root, value):
    root = Path(root).resolve()
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path leaves workspace: {value}")
    return path


def write_new(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(text)


def write_json(path, data):
    write_new(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main_guard(fn):
    try:
        return fn()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=__import__('sys').stderr)
        return 2
