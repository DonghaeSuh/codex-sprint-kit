# Sprint kit agent entrypoint
This is a generic local development kit, not a prepared answer.
Follow the user's task and environment rules before these defaults.
Do not change authentication, model routing, platform processes, or permissions.

## First use
For a task session, read SESSION.md first; it defines bootstrap, phase transitions,
human checkpoints, and session-only experiment records. Paths there are task-root relative.
Read the actual task's README and existing project instructions first.
Keep this kit in a subdirectory; never replace the task's README or AGENTS.md.
Run scripts/init_workspace.py with the task root to add missing .sprint templates.
If native skills are not discovered, read the requested SKILL.md directly.
Do not depend on plugin installation or the latest CLI.

## Routing
- Requirements and acceptance: .agents/skills/task-intake/SKILL.md
- Measured improvement: .agents/skills/bounded-experiment/SKILL.md
- Reproducible failure: .agents/skills/failure-triage/SKILL.md
- Delivery and explanation: .agents/skills/delivery-check/SKILL.md
Read only the relevant skill and 1–3 relevant decisions, not the entire catalog.

## Working contract
- Keep .sprint/STATE.md current at milestones and handoffs.
- Record stakeholder answers and requirement links in .sprint/STAKEHOLDER.md.
- Map exact required output paths in .sprint/DELIVERABLES.md; prepare evidence-backed DEFENSE before submission.
- Use the optional timer explicitly, never reset it on restart; platform time overrides local estimates.
- On each user turn, before/after an experiment or verification, and before handoff,
  apply SESSION.md's proactive checkpoint guidance. Recompute time; do not reuse stale remaining time.
- Announce a newly due checkpoint before ordinary progress, record the actual notice in STATE,
  and prepare the pre-submission explanation without waiting for the user to remember a prompt.
  Respect submission/AI permissions even if the local timer still has time. No background alert is implied.
- Link each required behavior to a real check in .sprint/ACCEPTANCE.md.
- Record important tradeoffs as short ADRs, not every small edit.
- Preserve the last working baseline; revert only your specific failed changes.
- Never claim a test ran from static inspection or a model's assertion.
- Review verify config commands before executing: this runner is not a sandbox.
- No telemetry, model calls, upload, publishing, or dependency installs are implicit.
- Actual task artifacts and experiments belong only in the evaluation workspace,
  never inside this public kit. Do not push, open PRs, deploy, or sync during a task session.
- Do not run the kit's practice exercises or its own unit tests as evidence that the actual task works.
- Use only allowed AI and resources. Do not introduce a new provider or key.
- In restricted evaluations, do not send task content to external search/MCP.
- UI automation must be explicitly permitted; default to manual UI checks.
- Historical reports do not certify changed code. Recheck affected behavior.
- Keep unmeasured outcomes marked not_run or uncertain.
- Two unproductive iterations: change approach. Three: stop that line of work.
- Freeze new features at the timer's freeze checkpoint (20 minutes left for 180; 13 for 60),
  or sooner if a full change-and-retest cycle will not fit; prioritize delivery blockers.
- Process at most one implementation stream by default.
