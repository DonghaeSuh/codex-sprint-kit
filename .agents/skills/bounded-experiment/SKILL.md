---
name: bounded-experiment
description: Run a bounded improvement cycle against fixed acceptance cases, preserving the last working baseline and measured evidence.
---
# Bounded experiment
Read STATE, affected acceptance cases, and the relevant implementation.
If no baseline exists, measure one before changing behavior.
Define one causal hypothesis, one main change, a time limit (normally 15–25 minutes), and a decision criterion.
Run trusted checks with scripts/verify.py. It records execution status, not domain correctness unless the command asserts it.
Keep the same cases and input data for the comparison. If a case was wrong, document the correction and remeasure both sides.
Do not promote a noisy change from a single lucky model response; repeat only important uncertain cases.
Keep a change only when evidence supports it or a required correctness fix is established. Record uncertainty explicitly.
Append one JSON object to .sprint/EXPERIMENTS.jsonl:
{"id":"E1","hypothesis":"...","change":"...","baseline":"report path","result":"report path","decision":"keep/revert/inconclusive","duration_seconds":0,"limitations":"..."}
Two stagnant iterations: switch approach. Three: stop that line and reduce scope or report the blocker.
Restore only the experiment's changes; never wipe unrelated work. Update STATE with the next action and remaining time.
