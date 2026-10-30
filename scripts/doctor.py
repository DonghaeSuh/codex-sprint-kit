"""Read-only environment report. Never reads credentials or installs tools."""
import argparse
import json
import platform
import shutil
import subprocess
from pathlib import Path
from common import main_guard, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--output")
    args = parser.parse_args()
    root = Path(args.root).resolve(strict=True)
    tools = {}
    for name in ("python3", "node", "npm", "git", "codex", "rg"):
        executable = shutil.which(name)
        if not executable:
            tools[name] = {"available": False}
            continue
        try:
            result = subprocess.run([executable, "--version"], cwd=root,
                                    capture_output=True, text=True, timeout=5)
            tools[name] = {"available": True, "exit_code": result.returncode,
                           "version": result.stdout.strip()[:200]}
        except subprocess.TimeoutExpired:
            tools[name] = {"available": True, "status": "timeout"}
    report = {"root": str(root), "os": platform.system(),
              "python": platform.python_version(),
              "disk_free_bytes": shutil.disk_usage(root).free,
              "tools": tools, "credentials_read": False,
              "exam_environment_verified": False}
    if args.output:
        write_json(args.output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main_guard(main))
