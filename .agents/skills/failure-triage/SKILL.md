---
name: failure-triage
description: Diagnose a reproducible failure under a time budget, isolate its first failing boundary, and verify a minimal correction.
---
# Failure triage
Capture the exact symptom, input, expected behavior, command, and exit status.
Inspect the first relevant error and recent changes. Follow the input through the failing boundary.
Avoid collecting secrets, environment dumps, or unrelated logs.
Create the smallest reproduction that fails for the same reason; an assertion must distinguish correct from incorrect behavior.
State one suspected cause and the evidence for it. Change only the relevant behavior.
Rerun the reproduction and adjacent critical acceptance cases.
After 10 minutes without narrowing the cause, summarize evidence and try an alternate diagnostic path.
After three unsuccessful fixes, stop stacking patches; return to the last working state or propose a smaller valid solution.
If environment access is blocked, record the limitation; do not bypass it.
Update STATE and record the actual result, including failures.
