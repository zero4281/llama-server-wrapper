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
* `test_integration.py`: 15 tests
* **Total:** ~90 tests

---

## Project Roadmap

| Priority | Task | Status |
| :--- | --- | --- |
| **P0 (Critical)** | Fix Confirmation Prompt Fallback Mode Crash | 🔄 Active |
| **P0 (Critical)** | Fix Confirmation Prompt UI Failure (Logger/Curses Error) | ✅ Resolved |
| **P0 (Critical)** | Fix Keyboard Input Hang (Fallback Mode) | ✅ Resolved |

---

## Summary

**Last Updated:** April 22, 2026
**Overall Status:** 1 Critical bug remains in progress; all other previously logged issues have been resolved.

* **Resolved:** Issues relating to test structure, mocking patterns, general cleanup, and terminal input handling.
* **In Progress:** The confirmation fallback mode crash in `render_confirmation()`.
