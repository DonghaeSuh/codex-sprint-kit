import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))
from timer import status


class SessionToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sprint-tools-")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, name, *args):
        return subprocess.run([sys.executable, str(KIT / "scripts" / name), *map(str, args)],
                              cwd=self.root, capture_output=True, text=True, timeout=10)

    def inventory(self, *args):
        return self.cli("inventory.py", "--root", self.root, "--path", "uploads", *args)

    def data(self, name, text):
        p = self.root / "uploads" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def test_timer_restart_preserves_start_and_budget(self):
        args = ("start", "--root", self.root, "--minutes", "60")
        self.assertEqual(self.cli("timer.py", *args).returncode, 0)
        p = self.root / ".sprint/timer.json"
        original = p.read_bytes()
        again = self.cli("timer.py", *args, "--elapsed-minutes", "5")
        self.assertEqual(again.returncode, 0)
        self.assertIn("KEEP", again.stdout)
        self.assertEqual(p.read_bytes(), original)
        changed = self.cli("timer.py", "start", "--root", self.root, "--minutes", "180")
        self.assertEqual(changed.returncode, 2)
        self.assertEqual(p.read_bytes(), original)

    def test_timer_existing_platform_elapsed(self):
        run = self.cli("timer.py", "start", "--root", self.root, "--minutes", "60", "--elapsed-minutes", "20")
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)
        self.assertAlmostEqual(report["elapsed_seconds"], 1200, delta=2)
        self.assertEqual(report["phase"], "baseline")

    def test_timer_freeze_expiry_and_clock_regression(self):
        state = {"started_epoch": 1000, "budget_minutes": 60}
        self.assertEqual(status(state, 1000 + 47 * 60)["phase"], "freeze")
        self.assertEqual(status(state, 1000 + 60 * 60)["remaining_seconds"], 0)
        self.assertEqual(status(state, 1000 + 61 * 60)["phase"], "expired")
        with self.assertRaises(ValueError):
            status(state, 999)
        self.assertEqual(status({"started_epoch": 1000, "budget_minutes": 180}, 10600)["phase"], "freeze")

    def test_timer_invalid_input_and_missing_state(self):
        for value in ("0", "-1", "1441", "oops"):
            self.assertEqual(self.cli("timer.py", "start", "--minutes", value).returncode, 2)
        self.assertEqual(self.cli("timer.py", "start", "--minutes", "60", "--elapsed-minutes", "nan").returncode, 2)
        self.assertEqual(self.cli("timer.py", "status").returncode, 2)
        self.assertFalse((self.root / ".sprint/timer.json").exists())

    def test_inventory_aggregate_only_and_ragged_rows(self):
        self.data("input.csv", "id,value\nPRIVATE_RAW_SENTINEL,2\nB,\nC,3,extra\n")
        run = self.inventory()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertNotIn("PRIVATE_RAW_SENTINEL", run.stdout)
        file = json.loads(run.stdout)["files"][0]
        self.assertEqual(file["rows_scanned"], 3)
        self.assertEqual(file["ragged_rows"], 1)
        self.assertEqual(file["columns"][1]["missing"], 1)
        self.assertEqual(file["status"], "complete")

    def test_inventory_empty_tsv_bom_and_quoted_newline(self):
        self.data("empty.csv", "")
        self.data("valid.tsv", '\ufeffid\tnote\nA\t"line1\nline2"\n')
        report = json.loads(self.inventory().stdout)
        self.assertEqual(report["files"][0]["status"], "empty")
        self.assertEqual(report["files"][1]["rows_scanned"], 1)
        self.assertEqual(report["files"][1]["columns"][0]["name"], "id")

    def test_inventory_row_file_byte_limits_are_explicit(self):
        self.data("a.csv", "x\n" + "abcdefghij\n" * 200)
        self.data("b.csv", "x\na\n")
        report = json.loads(self.inventory("--max-files", "1", "--max-rows", "2", "--max-bytes", "1024").stdout)
        self.assertTrue(report["scan_partial"])
        file = report["files"][0]
        self.assertTrue(file["partial"])
        self.assertEqual(file["rows_scanned"], 2)
        self.assertIn("byte_limit", file["limits_reached"])
        self.assertIn("row_limit", file["limits_reached"])

    def test_inventory_malformed_csv_and_encoding(self):
        self.data("bad.csv", 'id,note\nA,"unclosed\n')
        path = self.data("binary.csv", "")
        path.write_bytes(b'\xff\xfe')
        report = json.loads(self.inventory().stdout)
        self.assertIn("csv_parse_error", report["files"][0]["limits_reached"])
        self.assertEqual(report["files"][1]["status"], "unsupported_encoding")

    def test_inventory_exact_limit_is_not_incomplete(self):
        self.data("a.csv", "x\na\nb\n")
        report = json.loads(self.inventory("--max-rows", "2", "--max-files", "1").stdout)
        self.assertFalse(report["scan_partial"])
        self.assertFalse(report["files"][0]["partial"])

    def test_inventory_paths_and_hidden_data(self):
        self.data(".hidden.csv", "secret\nnever\n")
        outside = self.root / "outside.csv"
        outside.write_text("x\nprivate\n")
        (self.root / "uploads/link.csv").symlink_to(outside)
        report = json.loads(self.inventory().stdout)
        self.assertEqual(report["files"], [])
        self.assertEqual(self.cli("inventory.py", "--path", "uploads/link.csv").returncode, 2)
        self.assertEqual(self.cli("inventory.py", "--path", "..").returncode, 2)

    def test_new_templates_preserve_existing_stakeholder_records(self):
        self.cli("init_workspace.py")
        path = self.root / ".sprint/STAKEHOLDER.md"
        path.write_text("actual answer: keep this")
        self.cli("init_workspace.py")
        self.assertEqual(path.read_text(), "actual answer: keep this")
        self.assertTrue((self.root / ".sprint/DEFENSE.md").is_file())
        self.assertTrue((self.root / ".sprint/DELIVERABLES.md").is_file())


if __name__ == "__main__":
    unittest.main()
