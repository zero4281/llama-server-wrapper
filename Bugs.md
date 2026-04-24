# Bugs.md

## Current Bug Reports

### 🟠 MEDIUM: Logger debug message never prints (UI_MANAGER_DEBUG flag ignored)
**Status:** ✅ **RESOLVED**
**Priority:** **P3** - Cosmetic issue; debugging impaired

**Resolution Summary:**
The logger is now properly configured and writing to the console when debug mode is enabled. Running with `UI_MANAGER_DEBUG=1` now shows messages like:
```
17:37:48 - ui_manager - INFO - render_menu: options_count=7, default=1, highlighted=None, timeout=None
17:37:48 - ui_manager - DEBUG - Creating menu window: size=11x50, pos=(6,15)
17:37:48 - ui_manager - DEBUG - Window created: <_curses.window object at 0x77f76b764390>
```

**Verification:**
Run: `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama`
Provide inputs: `1\n8\n3\n`
Observe that logger messages now appear in the output, confirming the logger is properly configured and working.

**Affected Components:**
- ui_manager.py (line 1004)
- Logger configuration in the application

**Context:**
- The logger is imported but appears to be not properly configured
- When UI_MANAGER_DEBUG=1 is set, we expect debug messages to be visible
- The logger.debug() call is clearly in the code but produces no output

**Dependencies:**
- Requirements.md Section 9.4 (Code style - logging)
- Testing Strategy.md (logging expectations)

---

### 🟠 HIGH: ui_manager.py:render_confirmation() has multiple redundant fallback sections making it overly engineered
**Status:** ✅ **RESOLVED**
**Priority:** **P2** - Code quality issue; maintenance impaired

**Resolution Summary:**
- Consolidated all fallback logic into a single `_render_confirmation_fallback()` method
- Centralized error handling with one try/except block
- Removed redundant fallback sections and duplicate code
- Simplified the method flow with proper indentation
- The fix maintains the same functionality while improving code maintainability and testability

**Description:**
The `render_confirmation()` method in ui_manager.py has multiple fallback sections scattered throughout the implementation, making it overly engineered and difficult to maintain. Instead of a single, well-defined fallback mechanism, the method has at least 6 separate fallback paths:

1. Lines 1014-1076: Console fallback when not using curses
2. Lines 1135-1188: Validation fallback when window/screen invalid
3. Lines 1282-1343: Missing curses attributes fallback
4. Lines 1357-1438: Recovery fallback within input loop
5. Lines 1479-1509: Exception handling fallback
6. Lines 1510-1540: Another exception handling fallback

This redundancy violates the principle of having a single source of truth for error handling and makes the code harder to understand, test, and maintain.

**Reproduction Steps:**
The issue is structural and present whenever the method is used. The complexity can be observed by examining the method code (lines 983-1544) and noting the multiple try/except blocks with fallback logic.

**Affected Components:**
- ui_manager.py (render_confirmation method)
- main.py (uses for self-update confirmation)
- llama_updater.py (uses for installation confirmation)

**Why This Matters:**
1. Violates Single Responsibility Principle and DRY principle
2. Increases maintenance overhead
3. Makes testing difficult (coverage gaps for _screen is None scenarios)
4. Inconsistent error handling could lead to unpredictable behavior
5. New developers find the code intimidating

**Suggested Fix:**
Consolidate all fallback logic into a single method (e.g., _render_confirmation_fallback()) called from a single error handler. This would centralize fallback implementation, make the normal flow clearer, and simplify testing.

---

### 🔴 CRITICAL: Arrow keys cause crashes and invalid key handling in menu navigation
**Status:** **RESOLVED**
**Priority:** **P0** - Critical; UI unusable with standard navigation

**Description:**
When running `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama`, the program works with numeric key input but crashes if arrow keys are used. Page Up/Page Down don't work. Escape key doesn't exit but causes `^[` to appear on screen. The down arrow seems to be interpreted at the escape key (27).

**Reproduction Steps:**
1. Run: `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama`
2. Observe that the program works with numeric key input (e.g., `1\n8\n3\n`)
3. Try navigating menus with arrow keys (↑, ↓)
4. **Expected:** Normal menu navigation
5. **Actual:** Program crashes or displays invalid characters (`^[`)

**Key Symptoms:**
- Arrow keys cause crashes during menu navigation
- Page Up/Page Down keys have no effect
- Escape key doesn't exit; displays `^[` on screen instead
- Down arrow appears to be interpreted at escape key (27)
- Valid input: numeric keys work correctly (`1\n8\n3\n`)
- Invalid input: arrow keys crash (`\033[B`)

**Affected Components:**
- `ui_manager.py` - menu rendering and input handling (Section 8.3 of Requirements.md)
- `curses` module - terminal input interpretation
- `main.py` - CLI entry point that delegates to UIManager

**Context:**
- This is a critical issue that prevents users from using the standard arrow key navigation
- The issue may be related to how curses interprets or handles arrow key events
- The escape key behavior suggests there may be a key code collision or misinterpretation

**Dependencies:**
- Requirements.md Section 8.3 (Numbered menus with arrow key navigation)
- Testing Strategy.md (mocking patterns for curses-related tests)
- Testing Strategy.md (patching `'ui_manager.curses.newwin'` requirement)

**Testing Strategy Impact:**
- Requires new test cases in `Tests/test_ui_manager_pytest.py` or `Tests/test_ui_manager_comprehensive.py`
- Should test arrow key navigation with proper mocking
- Verify that `KEY_UP`/`KEY_DOWN` navigation works without crashes
- Test escape key handling returns -1 correctly
- Must patch `'ui_manager.curses.newwin'` in any test that calls `render_menu` or `render_confirmation`

---

### 🟠 MEDIUM: Program drops out of curses and displays print on line 1312 of ui_manager.py in real terminals
**Status:** **RESOLVED**
**Priority:** **P3** - Functional regression; curses environment dropped unexpectedly

**Description:**
When running the program in a real terminal, it drops out of the curses environment and displays a print statement on line 1312 of ui_manager.py. This is not the desired behavior. The program should remain within the curses environment when curses is working, and should only fall back to console output when curses fails. The bug indicates that the fallback mechanism is being triggered unexpectedly in real terminals, causing the program to exit the curses session prematurely.

**Reproduction Steps:**
1. Run: `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama 2>&1`
2. Provide inputs: `1\n8\n3\n`
3. Observe that the program drops out of curses and displays console output instead of rendering through UIManager

**Affected Components:**
- ui_manager.py (line 1312 - fallback console output section)
- render_confirmation method (fallback handling)
- Terminal state management

**Context:**
- The program should maintain the curses environment throughout the entire interactive workflow
- Fallback to console output should only occur when curses initialization fails or curses attributes are missing
- The bug causes the curses session to be torn down unexpectedly, leaving the terminal in an inconsistent state
- This violates the requirement that "The curses session must not be torn down and re-entered mid-workflow; UIManager is constructed once and destroyed once"
- The bug is particularly problematic because it can occur in real terminals where curses should be working

**Dependencies:**
- Requirements.md Section 8.4 (Confirmation prompts must never drop out of the curses environment)
- Requirements.md Section 8.6 (UIManager lifecycle - curses session must remain open for the entire duration)
- Testing Strategy.md (mocking patterns for curses-related tests)

**Suggested Fix:**
1. Review the condition that triggers the fallback console output path (around line 1312)
2. Ensure fallback is only executed when curses is genuinely unavailable or has failed
3. Add proper terminal state restoration before exiting the fallback section
4. Consider consolidating fallback logic (as suggested in the existing bug #2) to make the fallback path more robust and predictable
5. Add unit tests to verify fallback is not triggered unexpectedly in real terminal scenarios

---

## Project Roadmap

| Priority | Task | Status |
| :--- | :--- | :--- |
| **P0 (Critical)** | Arrow keys cause crashes and invalid key handling in menu navigation | 🟣 Open |
| **P2 (High)** | ui_manager.py:render_confirmation() has multiple redundant fallback sections | 🟠 Resolved |
| **P3 (Medium)** | Program drops out of curses and displays print on line 1312 of ui_manager.py in real terminals | 🟠 Resolved |

---

## Summary

**Last Updated:** April 24, 2026
**Overall Status:** 3 New bugs identified; all previously logged issues have been resolved.

* **Resolved:** Issues relating to test structure, mocking patterns, general cleanup, terminal input handling, and logger debug messages.
