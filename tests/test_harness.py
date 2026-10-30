import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

KIT = Path(__file__).resolve().parents[1]


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="sprint-test-")
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, script, *args):
        return subprocess.run([sys.executable, str(KIT / "scripts" / script), *map(str, args)],
                              cwd=self.root, capture_output=True, text=True, timeout=15)

    def verify(self, checks, *args):
        config = self.root / "checks.json"
        config.write_text(json.dumps({"checks": checks}))
        result = self.cli("verify.py", "--root", self.root, "--config", config, *args)
        reports = sorted(self.root.glob(".sprint/runs/*/report.json"))
        return result, json.loads(reports[-1].read_text()) if reports else None

    def py(self, name, code, **kw):
        return {"id": name, "argv": [sys.executable, "-c", code], **kw}

    def test_success_failure_manual_and_missing_are_distinct(self):
        result, report = self.verify([
            self.py("ok", "print('good')"), self.py("bad", "raise SystemExit(7)"),
            {"id": "human", "manual": "click manually"},
            {"id": "missing", "argv": ["/no-such-sprint-command"]}])
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual([x["status"] for x in report["checks"]], ["pass", "fail", "not_run", "not_run"])
        self.assertEqual(report["checks"][1]["exit_code"], 7)
        self.assertFalse(report["all_passed"])

    def test_all_success_returns_zero(self):
        run, report = self.verify([self.py("ok", "assert 2 + 2 == 4")])
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(report["all_passed"])

    def test_malformed_config_fails_cleanly(self):
        config = self.root / "invalid.json"
        for content in ("[]", '{"checks":[null]}', '{"checks":[]}', '{'):
            config.write_text(content)
            run = self.cli("verify.py", "--config", config)
            self.assertEqual(run.returncode, 2)
            self.assertNotIn("Traceback", run.stderr)

    def test_successful_command_cannot_leave_background_child(self):
        child = "import time; from pathlib import Path; time.sleep(0.7); Path('escaped').touch()"
        code = f"import subprocess,sys; subprocess.Popen([sys.executable,'-c',{child!r}],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)"
        _, report = self.verify([self.py("parent", code), self.py("observe", "import time; time.sleep(0.8)")])
        self.assertEqual(report["checks"][0]["status"], "pass")
        self.assertFalse((self.root / "escaped").exists())

    def test_timeout_kills_descendant(self):
        marker = self.root / "escaped"
        child = "import time; from pathlib import Path; time.sleep(0.7); Path('escaped').touch()"
        code = f"import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',{child!r}]); time.sleep(5)"
        run, report = self.verify([self.py("slow", code, timeout_seconds=0.15),
                                   self.py("observe", "import time; time.sleep(0.8)")])
        self.assertEqual(report["checks"][0]["status"], "timeout", run.stderr)
        self.assertFalse(marker.exists())

    def test_timeout_after_child_closes_stdout(self):
        _, report = self.verify([self.py("closed", "import os,time; os.close(1); os.close(2); time.sleep(5)", timeout_seconds=0.1)])
        self.assertEqual(report["checks"][0]["status"], "timeout")

    def test_bounded_logs(self):
        run, report = self.verify([self.py("chatty", "print('x' * 200000)")], "--max-log-bytes", "1024")
        check = report["checks"][0]
        self.assertEqual(run.returncode, 0)
        self.assertTrue(check["output_truncated"])
        self.assertEqual((self.root / check["evidence_path"]).stat().st_size, 1024)

    def test_argv_does_not_evaluate_shell(self):
        literal = "$(touch PWNED); `touch PWNED2`"
        _, report = self.verify([{"id": "literal", "argv": [sys.executable, "-c", "import sys; print(sys.argv[1])", literal]}])
        self.assertEqual((self.root / report["checks"][0]["evidence_path"]).read_text().strip(), literal)
        self.assertFalse((self.root / "PWNED").exists())
        self.assertFalse((self.root / "PWNED2").exists())

    def test_invalid_checks_rejected_before_any_command_runs(self):
        marker = self.py("marker", "from pathlib import Path; Path('executed').touch()")
        for invalid in ({"id": "../escape", "argv": ["true"]},
                        {"id": "marker", "argv": ["true"]},
                        {"id": "invalid", "argv": "echo bad"},
                        self.py("nan", "pass", timeout_seconds=float("nan")),
                        self.py("escape", "pass", cwd=".."),
                        {"id": "manual", "argv": ["true"], "manual": "review"}):
            with self.subTest(invalid=invalid):
                run, report = self.verify([marker, invalid])
                self.assertEqual(run.returncode, 2, run.stdout)
                self.assertIsNone(report)
                self.assertFalse((self.root / "executed").exists())

    def test_output_symlink_cannot_escape_root(self):
        (self.root / "outside").symlink_to(self.root.parent, target_is_directory=True)
        run, _ = self.verify([self.py("ok", "pass")], "--output-dir", "outside/runs")
        self.assertEqual(run.returncode, 2)

    def test_repeat_runs_preserve_evidence(self):
        self.verify([self.py("ok", "print('first')")])
        self.verify([self.py("ok", "print('second')")])
        reports = list(self.root.glob(".sprint/runs/*/report.json"))
        self.assertEqual(len(reports), 2)
        outputs = {(p.parent / "ok.log").read_text().strip() for p in reports}
        self.assertEqual(outputs, {"first", "second"})

    def test_initialization_preserves_existing_files(self):
        (self.root / "AGENTS.md").write_text("existing rules")
        (self.root / "README.md").write_text("original task")
        self.assertEqual(self.cli("init_workspace.py", "--root", self.root).returncode, 0)
        state = self.root / ".sprint/STATE.md"
        state.write_text("custom state")
        self.assertEqual(self.cli("init_workspace.py", "--root", self.root).returncode, 0)
        self.assertEqual(state.read_text(), "custom state")
        self.assertEqual((self.root / "AGENTS.md").read_text(), "existing rules")
        self.assertEqual((self.root / "README.md").read_text(), "original task")

    def test_handoff_is_bounded_and_never_overwrites(self):
        self.cli("init_workspace.py", "--root", self.root)
        (self.root / ".sprint/STATE.md").write_text("x" * 20000)
        self.verify([{"id": "manual", "manual": "human review"}])
        report = next(self.root.glob(".sprint/runs/*/report.json"))
        args = ["--root", self.root, "--report", report, "--output", ".sprint/handoff.md"]
        run = self.cli("snapshot.py", *args)
        self.assertEqual(run.returncode, 0, run.stderr)
        text = (self.root / ".sprint/handoff.md").read_text()
        self.assertLess(len(text), 8000)
        self.assertIn("not_run", text)
        self.assertEqual(self.cli("snapshot.py", *args).returncode, 2)

    def test_provenance_rejects_unlicensed_vendoring(self):
        source = {"id": "x", "url": "https://example.com", "revision": "a"*40,
                  "license": "unknown", "use": "vendored", "decision": "use",
                  "verification": "source", "evidence": ["readme"]}
        manifest = self.root / "source.json"
        manifest.write_text(json.dumps({"sources": [source]}))
        self.assertEqual(self.cli("provenance.py", "--manifest", manifest).returncode, 2)


if __name__ == "__main__":
    unittest.main()
