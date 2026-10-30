# Validation — 2026-10-30

## Executed locally
- macOS, Python 3.10.8; Python standard library only.
- 14 unittest cases passed. Includes all-pass, fail, manual/not_run, missing command,
  malformed configuration, timeouts, descendant cleanup on success and timeout,
  bounded logs, literal argv, escaped paths/symlinks, repeat runs, template preservation,
  bounded handoff and refusal to overwrite, unresolved-license vendoring rejection.
- All 4 SKILL.md files passed the installed skill-creator quick validator.
  This validates format, not agent behavior or compatibility with every CLI.
- All 10 source records passed the offline provenance checker.
- Synthetic CSV rehearsal: deliberately incorrect unweighted ratio passed 7/9 cases;
  changing only the ratio to total-good / total-count passed 9/9.
  Baseline and candidate logs remained separate, and a bounded handoff was generated.

## Not established
- No AI productivity or model comparison benchmark was run.
- No upstream skill/MCP package was installed or runtime-certified.
- Current shell DNS prevented direct remote MCP checks; source access used connected tools.
- No Linux runtime, constrained evaluation environment, or native skill auto-discovery test was run.
- Manual UI and human explanation rehearsal remain for the user.
- The initial public repository was confirmed through GitHub; each subsequent update
  must be checked against its remote branch head. MCP runtime remains unverified.

## Session guide update
README now uses the actual public URL and a two-command entrypoint.
SESSION.md routes bootstrap, requirements, task-specific checks, bounded experiments,
manual verification, handoff, and submission inside the evaluation workspace.
BOUNDARIES.md and expanded STATE fields are added without replacing existing files.
The guide is an operational contract, not a technical network isolation mechanism.
No actual evaluation problem or experiment was run to validate this guide.

## Reproduce
From the kit root:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/provenance.py
```

For a new synthetic solution, follow practice/README.md and run practice/grade_csv.py.
The rehearsal solution is deliberately not included in the generic public kit.

## Stakeholder/rehearsal enhancement
- Public suite now has 25 passing tests (the original 14 plus 11 session-tool checks).
- Timer tests cover preserved start/budget, elapsed platform time, phase boundaries,
  expiry, clock regression and invalid input. This is an advisory clock, not an automatic stop.
- Inventory tests cover missing fields/ragged rows, no sample-value output, UTF-8 BOM,
  TSV/quoted newlines, empty input, malformed CSV/encoding, byte/row/file limits,
  hidden/symlink paths, and exact-limit scans. Complete means scanned, not domain-valid.
- All four skill formats pass the installed quick validator. The source manifest has 11 entries.
- Two local-only preparation integration checks pass for synthetic web/data cases:
  source preservation, no credential/secret copy into the candidate, exclusive new folders,
  file hashes, preserved attempts and initially unstarted timers. Private fixtures/tests
  are not included in this public package.
- No human 60-minute rehearsal, stakeholder model conversation, or real task was executed
  by these checks. Native skill behavior and productivity gains remain unmeasured.
