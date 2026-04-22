---
name: project-bug-create
description: Use this skill to create `Bugs.md` based on a user request.
---
# Skill Instructions
1. Prompt the user for a description of the issue using AskUserQuestion.
2. Once provided, delegate the following to @general:
   - "Analyze current requirements in `./Requirements.md` and the existing plan in `./Plan.md`."
   - "Read `./Testing Strategy.md` to find the current tests."
   - "Read `./Bugs.md` to check for duplicates."
   - "Add the new item to `./Bugs.md` with a priority estimate, dependencies, and clear reproduction steps."
   - "Perform additional analysis to identify the issue."
   - "CRITICAL: Perform NO code changes, refactoring, or bug fixes. This is a documentation-only task."