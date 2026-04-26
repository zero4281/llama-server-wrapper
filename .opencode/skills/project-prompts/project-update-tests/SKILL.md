---
name: project-update-tests
description: Use this skill to review and update the test suite after code changes.
---
# Skill Instructions
**Constraint:** Do not modify any source files. Only modify files inside `./Tests/`.  Use the todowrite tool to track all tasks. 

⚠️ **AGENT BOUNDARY** — The orchestrator must NOT read files inside `./Tests/` or execute any tests directly. All such actions must be delegated to an @general agent. 

**EXECUTION POLICY:** Perform only one task at a time. Do not initiate any agent until the output of the previous agent has been returned and reviewed. 

---

## Phase 1 — Analyse

**Constraint:** You must execute these tasks sequentially. Do not batch them. Wait for the summary of each task before creating the next.

Use todowrite to create the following three tasks and assign each to @general. 

Include the following context in every task:
- Only modify files inside `./Tests/`.
- Read `./Requirements.md`, `./Plan.md`, and `./Testing Strategy.md` before starting.
- Return a written summary of findings, including a list of specific fixes needed.

### Task 1 — Coverage Gaps
> Compare behaviours specified in the **Behaviour Specifications** and **Coverage Gaps** sections of `./Testing Strategy.md` against the existing tests in `./Tests`. For each specified behaviour with no corresponding test, note it as a gap. New tests must go into the existing file that matches their coverage area — do not create new test files. Follow the standard setup pattern from `./Testing Strategy.md`. Return a written summary with a list of specific gaps found.

**WAIT:** Do not proceed until Task 1 is complete and the summary is returned.

### Task 2 — Stale Tests
> Identify tests that no longer match the current source code — wrong return values, removed methods, changed signatures, etc. Note each one with a description of what needs to change. Return a written summary with a list of specific staleness issues found.

**WAIT:** Do not proceed until Task 2 is complete and the summary is returned.

### Task 3 — Mocking Compliance
> Run `python3 Tests/check_mocking_pattern.py` if it exists. Otherwise, manually scan every test that calls `render_menu` or `render_confirmation` and verify it uses `patch('ui_manager.curses.newwin', return_value=mock_win)` as required by `./Testing Strategy.md`. Note any violations. Return a written summary with a list of any violations found.

---

## Phase 2 — Fix

Once all three analysis tasks are complete and their summaries are returned, use todowrite to create one task per finding. Assign each task to @general one at a time.

**Constraint:** You must create and execute these tasks one at a time. Wait for the agent to confirm the fix before moving to the next finding.

Each task must include:
- The specific file and test to add or modify (from the analysis summary)
- The constraint: only modify files inside `./Tests/`
- Enough context from the summary so @general can act without re-reading everything

**WAIT:** Do not begin Phase 3 until all fix tasks are marked complete.

---

## Phase 3 — Verify

Use todowrite to create the following task and assign it to an @general agent: Run `python3 -m pytest Tests/ -v` and return a summary of the results.

Once the task is complete, for each failing test, use todowrite to create a new fix task.  Assign each task to an @general agent one at a time.  Have the agent do all of the analysis and code updates.  Send the agent a propmt with an appropriate amount of details.

Repeat until all tests pass.

---

## Phase 4 — Update Testing Strategy

Use todowrite to create the following task and assign it to @general:

> Update `./Testing Strategy.md` only:
> - Update the test count column in the Test Files table to reflect the current number of tests per file.
> - Remove any entries from the Coverage Gaps section that are now covered.
> - Do not change any other sections unless source code changes have made them factually incorrect (e.g. a method signature changed).