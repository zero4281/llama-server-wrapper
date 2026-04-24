# Bugs.md

## Current Bug Reports

### 🆕 MEDIUM: Logger debug message never prints (UI_MANAGER_DEBUG flag ignored)
**Status:** 🆕 **NEW**
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

## Project Roadmap

| Priority | Task | Status |
| :--- | --- | --- |
| **P2 (High)** | ui_manager.py:render_confirmation() has multiple redundant fallback sections | 🔴 New |
| **P3 (Low)** | Logger debug message never prints (UI_MANAGER_DEBUG flag ignored) | 🆕 New |

---

## Summary

**Last Updated:** April 23, 2026
**Overall Status:** 1 New bug identified; all previously logged issues have been resolved.

* **Resolved:** Issues relating to test structure, mocking patterns, general cleanup, and terminal input handling.
* **New:** Logger debug message never prints (UI_MANAGER_DEBUG flag ignored)
