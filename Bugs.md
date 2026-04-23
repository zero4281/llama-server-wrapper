# Bugs.md

## Current Bug Reports

### 🔴 CRITICAL: Confirmation Prompt Fallback Mode Crashes with "curses not properly initialized"
**Status:** ✅ **RESOLVED**
**Priority:** **P0** - Blocks `--install-llama` workflow

**Resolution:**
Added `self._cleanup_terminal()` calls in all fallback paths within `render_confirmation()` in `ui_manager.py`. This ensures proper terminal state restoration and curses cleanup when fallback mode is activated, eliminating the "curses not properly initialized" crash.

**Changes Made:**
- Modified `ui_manager.py` to call `self._cleanup_terminal()` before performing console fallback operations in all fallback paths
- Fixed syntax errors introduced during editing (orphaned `except:` block)

**Verification:**
- All timeout tests (8 tests) pass
- All API tests (4 tests) pass
- The fix addresses the requirements: proper terminal state restoration and curses cleanup in fallback paths

---

### 🔴 CRITICAL: Confirmation Prompt UI Failure (Logger/Curses Error)
**Status:** 🔄 **RESOLVED**
**Priority:** **P0** - Blocks `llama.cpp` installation workflow

**Description:**
The confirmation prompt (`Proceed? [Y/n]:`) fails to render correctly. The system crashes with an "Error: name 'logger' is not defined" and "curses not properly initialized, forcing cleanup."

**Root Cause:**
* The confirmation flow is bypassing `UIManager.render_confirmation()`, causing it to render as plain text without ncurses initialization.
* The code attempts to access a non-existent `logger` variable during the prompt handling.
* `render_confirmation()` appears to print text but fails to instantiate a curses window (no `curses.newwin()` call).

**Requirements for Fix:**
1.  Ensure all confirmation prompts for `--install-llama` are strictly routed through `UIManager.render_confirmation()`.
2.  Remove direct `input()` or `print()` calls in the confirmation path.
3.  Implement proper logging (using the wrapper's logging system, not a local `logger` variable).
4.  Follow **Requirements.md Section 8.4** for implementation.

---

### 🟢 RESOLVED: Keyboard Input Hang in Fallback Mode
**Status:** ✅ **RESOLVED**
**Priority:** **P0**

**Resolution:**
The terminal state issues and `select.select()` timeout failures have been addressed. The fallback console mode now correctly resets the terminal state and accurately detects keyboard input after `curses` initialization failures.

---

### 🟠 HIGH: Failing UIManager Tests - Menu Navigation, Confirmation, Styling, Edge Cases
**Status:** 🆕 **NEW**
**Priority:** **P1** - Blocks test suite reliability

**Description:**
Several tests in `Tests/test_ui_manager_comprehensive.py` are failing due to UIManager returning unexpected values:
1. `test_menu_navigation` fails because `render_menu()` returns -1 instead of a valid index
2. `test_confirmation` likely fails due to similar initialization issues
3. `test_styling` fails due to color pair setup issues
4. `test_edge_cases` fails due to various edge case handling

**Root Cause:**
The UIManager's `render_menu()` method is detecting that curses is not properly initialized and falling back to console mode, but the test setup is not correctly mocking the terminal environment for the fallback path. Specifically:
- Line 515-517: The method checks `(not sys.stdin.isatty() and not self._using_curses) or not self._screen` and returns early
- The test setup creates a UIManager but doesn't properly mock `sys.stdin.isatty()` to return True
- Even when curses is mocked, the `_ensure_terminal_ready()` method may be returning False, forcing fallback to console mode

**Affected Components:**
- `ui_manager.py` - `render_menu()` method (lines 514-525)
- `ui_manager.py` - `_ensure_terminal_ready()` method (lines 478-487)
- `Tests/test_ui_manager_comprehensive.py` - Multiple test functions

**Reproduction Steps:**
1. Run `python3 -m pytest Tests/test_ui_manager_comprehensive.py::test_menu_navigation -v`
2. Observe that the test fails with "Should return valid index, got -1"
3. Similar failures occur in `test_confirmation`, `test_styling`, and `test_edge_cases`

**Requirements for Fix:**
1. Ensure UIManager methods properly handle mocked terminal environments in tests
2. Fix `_ensure_terminal_ready()` to return True when curses is properly mocked
3. Ensure test setups properly mock `sys.stdin.isatty()` to return True for interactive mode
4. Verify that curses state checks don't incorrectly trigger fallback mode during testing

**Dependencies:**
- Requirements.md Section 8 (CLI User Interface Module)
- Testing Strategy.md (for proper mocking patterns)
- conftest.py (shared test fixtures)

---

### 🟠 MEDIUM: TODO Comment in llama_updater.py - Curses UI Reverting to Terminal
**Status:** 🆕 **NEW**
**Priority:** **P2** - Affects UI consistency

**Description:**
There is a TODO comment in `llama_updater.py` at line 684 that indicates the code is reverting to terminal output instead of using the curses UIManager for displaying selected release information.

**Code Reference:**
```python
#TODO: DEBUG HERE - Add support for curses ui.render_menu or something similar so it doesn't revert to the terminal below.
# Show selected release info
print(f"\nSelected: {release_tag} ({asset_name})")
```

**Root Cause:**
After successfully using `ui.render_menu()` for platform and zip file selection, the code falls back to using `print()` to display the selected release information instead of using UIManager methods. This breaks the consistent curses UI experience required by Requirements.md Section 8.

**Requirements for Fix:**
1. Replace the `print()` statement with appropriate UIManager method calls
2. Consider using `ui.print_message()` or similar to display the selection information
3. Ensure all output after UIManager initialization goes through the UIManager interface

**Affected Components:**
- `llama_updater.py` - `install_release()` function (line 686)

**Reproduction Steps:**
1. Run `./llama-server-wrapper --install-llama`
2. Navigate through the platform selection menu (uses curses UI)
3. Navigate through the zip file selection menu (uses curses UI)
4. Observe that the "Selected: ..." output appears as plain terminal text instead of in the curses UI

**Dependencies:**
- Requirements.md Section 8.3 (Numbered menus)
- Requirements.md Section 8.6 (Lifecycle - UIManager must remain active for entire workflow)
- ui_manager.py API (specifically print_message or similar methods)

---

## Implementation Notes

**1. Rewrite Sequence (from `Testing Strategy.md`):**
* **Order:** `conftest.py` → `test_init_and_lifecycle.py` → `test_rendering_primitives.py` → `test_render_confirmation.py` → `test_render_menu.py` → `test_render_progress_bar.py` → `test_integration.py`.
* **Goal:** Run `pytest Tests/ -v` and confirm full suite pass.

**2. Target Test Counts:**
* `test_init_and_lifecycle.py`: 8 tests
* `test_render_menu.py`: 30 tests
* `test_render_confirmation.py`: 15 tests
* `test_render_progress_bar.py`: 10 tests
* `test_rendering_primitives.py`: 12 tests
* **Total:** ~90 tests

---

## Project Roadmap

| Priority | Task | Status |
| :--- | --- | --- |
| **P0 (Critical)** | Fix Confirmation Prompt Fallback Mode Crash | ✅ Resolved |
| **P0 (Critical)** | Fix Confirmation Prompt UI Failure (Logger/Curses Error) | ✅ Resolved |
| **P0 (Critical)** | Fix Keyboard Input Hang (Fallback Mode) | ✅ Resolved |
| **P1 (High)** | Failing UIManager Tests - Menu Navigation, Confirmation, Styling, Edge Cases | 🆕 New |
| **P2 (Medium)** | TODO Comment in llama_updater.py - Curses UI Reverting to Terminal | 🆕 New |

---

## Summary

**Last Updated:** April 23, 2026
**Overall Status:** 2 New bugs identified; all previously logged issues have been resolved.

* **Resolved:** Issues relating to test structure, mocking patterns, general cleanup, and terminal input handling.
* **New:** Failing UIManager tests and UI consistency issue identified and documented.

