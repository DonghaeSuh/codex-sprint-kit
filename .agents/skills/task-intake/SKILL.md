---
name: task-intake
description: Convert a time-limited development task and existing project into a short brief, acceptance checks, and an executable first milestone.
---
# Task intake
Read the task README, existing instructions, entrypoints, and provided data before asking questions.
Separate explicit requirements, observations, and assumptions. Do not infer production scope from a practice exercise.
Use the actual stakeholder channel for business ambiguities; use platform help for environment questions.

Write .sprint/BRIEF.md and ACCEPTANCE.md with source, input, expected output, verification method.
Preserve existing content. If templates are absent, use scripts/init_workspace.py from this kit.
Use scripts/inventory.py for bounded CSV/TSV summaries when data exists; partial scans are not full validation.
Record actual stakeholder replies in .sprint/STAKEHOLDER.md and link them to requirement IDs and checks.
While the human asks business questions, continue independent inspection; do not guess missing business rules.
Map the task's exact submission filenames to actual outputs in .sprint/DELIVERABLES.md.
Choose the first end-to-end slice that exercises the core input and output. Keep the supplied stack unless evidence requires changing it.
Record a consequential stack/scope choice in a short ADR; do not create ceremonial records for minor edits.
Allocate roughly 10% of the available time to discovery and reserve the final 15% for verification and delivery.
Report the next executable milestone and unresolved assumptions. Continue authorized implementation after requirements are sufficiently clear.
