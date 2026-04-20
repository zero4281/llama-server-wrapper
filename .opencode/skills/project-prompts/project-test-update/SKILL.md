---
name: project-test-update
description: Use this skill to review and update the test suite after code changes.
---
# Skill Instructions
Delegate the following task to @general:

Read `./Requirements.md` and `./Plan.md`.
Read `./Tests/Testing Strategy.md`.
Read every test file in `./Tests/` (all `test_*.py` files, `conftest.py`, and `__init__.py`).
Read the source file(s) that were most recently changed.

Do not modify any source files.  Only modify files inside `./Tests/`.

Perform the following analysis:

1. **Coverage gaps** — Compare the behaviour specified in `./Tests/Testing Strategy.md` (Behaviour Specifications and Coverage Gaps sections) against what the existing tests actually exercise.  Identify any specified behaviours that have no test.

2. **Stale tests** — Identify any tests that are testing behaviour that no longer matches the current source code (wrong return values, removed methods, changed signatures, etc.).

3. **Mocking compliance** — Run `python3 Tests/check_mocking_pattern.py` if it exists.  Otherwise, manually scan every test that calls `render_menu` or `render_confirmation` and verify it uses `patch('ui_manager.curses.newwin', return_value=mock_win)` as required by `./Tests/Testing Strategy.md`.  Flag any violations.

Based on this analysis, make the minimum set of changes needed to bring the tests up to date:

- Add new tests for any coverage gaps identified in step 1.  New tests must go into the existing file that matches their coverage area — do not create new test files.  Follow the standard setup pattern from `./Tests/Testing Strategy.md`.
- Fix or remove stale tests identified in step 2.
- Fix any mocking violations identified in step 3.

After making changes, run `python3 -m pytest Tests/ -v` and confirm all tests pass.  If any test fails, fix it before finishing.

Finally, update `./Tests/Testing Strategy.md`:
- Update the test count column in the Test Files table to reflect the current number of tests per file.
- Update the Coverage Gaps section to remove any gaps that are now covered.
- Do not change any other sections unless the source code changes have made them factually incorrect (e.g. a method signature changed).