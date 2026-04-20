---
name: project-complete-todo
description: Use this skill to select and complete an item from the TODO list.
---
# Skill Instructions
Read `./Requirements.md` and `./Plan.md`.
Read `./Tests/Testing Strategy.md`.
Read `./TODOs.md`.

Create a list of items to work on from `./TODOs.md`. Ignore items that are already marked as complete. Ask the user which TODO to work on (limit the list to just titles and priority) with AskUserQuestion. Make sure the list indicates the estimated priority and dependencies on other items in the list. Once the user makes a selection delegate the work to @general with the necessary context. After the task is completed verify that the agent completed the work, then mark the item status as complete in `./TODOs.md`. If the completed TODO involved changes to source code (not just documentation), run `python3 -m pytest Tests/ -v` and confirm all tests pass before marking the item complete.