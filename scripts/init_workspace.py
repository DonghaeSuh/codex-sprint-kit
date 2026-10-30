"""Add sprint templates without touching existing project/agent configuration."""
import argparse
from pathlib import Path
from common import main_guard, within, write_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve(strict=True)
    target = within(root, ".sprint")
    templates = Path(__file__).resolve().parents[1] / "templates"
    for source in sorted(templates.iterdir()):
        if source.is_file():
            destination = within(root, str(target.relative_to(root) / source.name))
            if destination.exists():
                print(f"KEEP {destination.name}")
            else:
                write_new(destination, source.read_text(encoding="utf-8"))
                print(f"ADD {destination.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main_guard(main))
