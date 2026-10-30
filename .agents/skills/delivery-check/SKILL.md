---
name: delivery-check
description: Verify a time-limited deliverable against its task contract, collect honest evidence, and prepare a human explanation before final submission.
---
# Delivery check
Read the actual submission rules and acceptance table before declaring completion.
Freeze new features when the remaining time is shorter than a full change-and-retest cycle.
Run the executable acceptance checks; inspect exit codes AND the meaning of their assertions.
Treat manual checks and unavailable checks as not_run until the human records the actual observation.
Compare requirements to outputs; a green build does not prove the requested behavior exists.
Ask the human to exercise the core UI flow if applicable. Do not drive the browser unless the environment explicitly permits it.
Verify save state, file names, startup instructions, and limitations. Keep platform services intact.
Help the user understand the input-to-output path, key choices, AI contributions, failure fixes, and unverified limits while AI use is permitted.
Never answer a later assessment phase in which AI is prohibited.
Update STATE and acceptance evidence. Report remaining gaps explicitly.
Use the platform's human submission controls; do not automate submission or upload results elsewhere.
