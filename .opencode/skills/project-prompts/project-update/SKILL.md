---
name: project-update
description: Use this skill to generate `Update.md` based on `Plan.md`.
---
# Skill Instructions
Delegate the following task to @general:

Read `./Requirements.md` and `./Plan.md`.  Perform a gap assessment on the code base, but ignore './Unit Tests'.  Look for features to remove that have been implemented but are not required.  Then use the gap assessment to create or update `./Update.md` with information about the code updates that are still required.
