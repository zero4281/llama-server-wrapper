---
name: project-create-todos
description: Use this skill to create `TODOs.md` based on a user request.
---
# Skill Instructions
Prompt the user for a request with AskUserQuestion.

After the user responds delegate the following task to @general:

Read `./Requirements.md` and `./Plan.md`.
Read `./Tests/Testing Strategy.md`.
Read `./TODOs.md`.

Don't do any work yet, just analysis. Create or update `./TODOs.md` with enough detail about each TODO that the work can be picked up later. Mark items as incomplete when they're added to the list. Estimate the level of priority of each item. Make sure to list any other items as dependencies for each TODO. If any TODO involves source code changes, add a corresponding test TODO that depends on it, with the description: "Run /project-test-update after [TODO name] is complete."