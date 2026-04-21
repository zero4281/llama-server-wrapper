---
name: project-bug-create
description: Use this skill to create `BUGS.md` based on a user request.
---
# Skill Instructions
Prompt the user for a request with AskUserQuestion.

After the user responds delegate the following task to @general:

Read `./Requirements.md` and `./Plan.md`.
Read `./Testing Strategy.md`.
Read `./BUGS.md`.

Don't do any work yet, just analysis. Create or update `./BUGS.md` with enough detail about each bug that the work can be picked up later. Mark items as incomplete when they're added to the list. Estimate the level of priority of each item. Make sure to list any other items as dependencies for each bug.