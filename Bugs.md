# Bugs.md

## Current Bug Reports

### 🆕 MEDIUM: Logger debug message never prints (UI_MANAGER_DEBUG flag ignored)
**Status:** RESOLVED
**Priority:** **P3** - Cosmetic issue; debugging impaired

**Description:**
The logger.debug() call on line 1004 of ui_manager.py produces no output even when debug logging is enabled via `UI_MANAGER_DEBUG=1`. The logger.info() call on line 1003 also doesn't appear in the output. This indicates the logger is not being configured or is not writing to the console.

**Reproduction Steps:**
1. Run: `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama`
2. Provide inputs: `1
8
3
`
3. Observe that no logger messages appear in the output, despite the debug flag being set

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

### 🔴 HIGH: ui_manager.py:render_confirmation() has multiple redundant fallback sections making it overly engineered
**Status:** 🔴 **NEW**
**Priority:** **P2** - Code quality issue; maintenance impaired

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

### 🟠 HIGH: render_confirmation() fallback prints directly to terminal, breaking curses environment
**Status:** 🟠 **NEW**
**Priority:** **P2** - Critical behavior violation; requirements non-compliance

**Description:**
The fallback implementation in `render_confirmation()` (lines 1282-1343 of ui_manager.py) uses `print()` statements instead of curses rendering when curses attributes are missing or when falling back to console output. This causes the terminal to drop out of the curses environment and display raw text directly, violating Requirements.md §8.4 which states: "Must never drop out of the curses environment; all rendering goes through UIManager."

The specific issue is on line 1312:
```python
print("Proceed? [Y/n]: ", end="", flush=True)
```

This fallback path is triggered when the curses window cannot be created or when `_screen` is `None`, but it still prints to stdout/stderr instead of using the proper fallback methods (`print_header()`, `print_message()`) that are designed for console output.

**Reproduction Steps:**
1. Run: `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama`
2. Provide inputs: `1\n8\n3\n`
3. Observe the terminal dropping out of curses and displaying the print message on line 1312

**Affected Components:**
- ui_manager.py (render_confirmation method, fallback section lines 1282-1343)
- Requirements.md §8.4 (curses environment requirement)

**Why This Matters:**
1. Directly violates Requirements.md §8.4 - the entire interactive workflow must remain within curses
2. Inconsistent with other fallback implementations that use `print_header()` and `print_message()`
3. Creates a poor user experience with raw text instead of styled console output
4. May cause issues in environments where stdout/stderr handling is different
5. Contradicts the design principle that all UI output goes through UIManager

**Suggested Fix:**
Replace the `print()` statement on line 1312 with a call to `print_message()`:
```python
print_message("Proceed? [Y/n]: ", end="")
```

This would maintain consistency with other fallback paths and ensure the console output is styled appropriately.

**Dependencies:**
- Requirements.md §8.4 (curses environment requirement)
- Testing Strategy.md (fallback behavior expectations)

---

## Project Roadmap

| Priority | Task | Status |
| :--- | --- | --- |
| **P2 (High)** | ui_manager.py:render_confirmation() has multiple redundant fallback sections | 🔴 New |
| **P2 (High)** | render_confirmation() fallback prints directly to terminal, breaking curses environment | 🟠 New |

---

## Summary

**Last Updated:** April 24, 2026
**Overall Status:** 2 New bugs identified; all previously logged issues have been resolved.

* **Resolved:** Issues relating to test structure, mocking patterns, general cleanup, terminal input handling, and logger debug messages.
