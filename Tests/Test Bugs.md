# Test Bugs Analysis

**Date:** April 15, 2026  
**Author:** AI Analysis  
**Scope:** UIManager tests (`Tests/__init__.py`, `ui_manager.py`, test files)

---

## Executive Summary

The test suite contains **4 distinct bugs**: 2 in `ui_manager.py` (code being tested) and 2 in the test files themselves. The errors occur across all three test runners:

| Bug Location | Type | Severity | Frequency |
|--------------|------|----------|----------|
| `ui_manager.py:393` | Logic Error | High | All tests |
| `ui_manager.py:605` | Division by Zero | Medium | When fallback triggered with total=0 |
| `Tests/test_ui_manager_pytest.py:84,105,160,229` | Test Bug | Low | 4 tests |

---

## Detailed Analysis

### Bug 1: Undefined `_draw_menu` in Curses Path (ui_manager.py:393)

**Location:** `ui_manager.py`, line 393  
**Severity:** High  
**Type:** Logic Error / Undefined Behavior

**Description:**
The `_draw_menu()` helper function is defined inside the `if not self._using_curses:` block (lines 297-344), making it only available when curses is NOT being used. However, at line 393, the curses code path (when `self._using_curses` is True) calls `_draw_menu(highlighted_idx)` without defining it in that scope.

**Code Flow:**
```
Line 278-398: curses path (self._using_curses is True)
  └─ Line 393: _draw_menu(highlighted_idx)  ← NameError raised
  └─ Line 395: bare except catches NameError
  └─ Line 397: returns -1 (cancel/error)
```

**Impact:**
When `render_menu()` is called with curses enabled, it raises `NameError: name '_draw_menu' is not defined`, which is caught by the bare `except:` block and returns -1 (cancel).

**Evidence:**
- `test_ui_manager_comprehensive.py` line 137: `AssertionError: Should return selected index, got -1`
- `test_ui_manager_pytest.py` tests that reach line 393 would fail similarly

**Fix Required:**
Move `_draw_menu()` outside the `if not self._using_curses:` block, or implement the curses rendering path properly.

---

### Bug 2: Division by Zero in Progress Bar Fallback (ui_manager.py:605)

**Location:** `ui_manager.py`, line 605  
**Severity:** Medium  
**Type:** Arithmetic Error / Race Condition

**Description:**
In `render_progress_bar()`, when the curses code fails and falls back to console output, line 605 calculates `percent or current/total*100`. When `total=0` (unknown size), this causes a `ZeroDivisionError`.

**Code Flow:**
```
Line 587-606: curses rendering
  └─ Line 603: bare except catches _curses.error ("must call initscr() first")
  └─ Line 605: print(f"... ({percent or current/total*100:.1f}%)")  ← ZeroDivisionError
  └─ Line 606: exception caught by outer try-except
  └─ Line 606: falls back to console with same calculation
```

**Impact:**
When mocked curses fails (as in `test_ui_manager_pytest.py::test_progress_bar_spinner`), the fallback code at line 605 executes `current/total*100` where `total=0`, causing a `ZeroDivisionError`.

**Evidence:**
- `test_ui_manager_pytest.py` line 210: `test_progress_bar_spinner` fails with `ZeroDivisionError: division by zero`

**Fix Required:**
Add a guard clause before the calculation: `percent or 0 if total > 0 else 0` or handle the `total=0` case explicitly.

---

### Bug 3: References to Non-existent `_draw_menu` Method (Tests/test_ui_manager_pytest.py)

**Location:** `Tests/test_ui_manager_pytest.py`, lines 84, 105, 160, 229  
**Severity:** Low  
**Type:** Test Bug / Mocking Error

**Description:**
Four test methods in `test_ui_manager_pytest.py` attempt to patch `ui_manager.UIManager._draw_menu`, a method that does not exist in the `UIManager` class.

**Affected Tests:**
1. `test_menu_navigation_arrows` (line 84)
2. `test_menu_typing_selection` (line 105)
3. `test_confirmation_n_cancels` (line 160)
4. `test_full_workflow_simulation` (line 229)

**Code:**
```python
with patch('ui_manager.UIManager._draw_menu') as mock_draw_menu:
    ...
```

**Impact:**
The `patch()` call raises `AttributeError: <class 'ui_manager.UIManager'> does not have the attribute '_draw_menu'`, causing these tests to fail immediately without exercising the actual code paths.

**Evidence:**
- `test_ui_manager_pytest.py` line 84: `AttributeError: <class 'ui_manager.UIManager'> does not have the attribute '_draw_menu'`
- Same error at lines 105, 160, 229

**Fix Required:**
Remove the `patch('ui_manager.UIManager._draw_menu')` lines or replace with appropriate mocks for the actual methods being tested.

---

## Root Cause Analysis

### Why These Bugs Occurred

1. **Partial Implementation**: The `ui_manager.py` file appears to be a work-in-progress. The `_draw_menu` helper was likely copied from the fallback code block but never moved to the curses code path, or the curses path was never fully implemented.

2. **Inconsistent Error Handling**: The bare `except:` blocks at lines 395 and 603 catch all exceptions, but the fallback code at line 605 performs calculations that can fail, creating a race condition between curses failure and fallback execution.

3. **Test-Assisted Regression**: The `test_ui_manager_pytest.py` file appears to have been written with assumptions about the API that no longer match the current implementation, suggesting the tests were written against a different version of the code.

---

## Recommendations

### Immediate Fixes (Priority: High)

1. **Fix `_draw_menu` scoping** (`ui_manager.py`):
   - Move the `_draw_menu()` function outside the `if not self._using_curses:` block (around line 277)
   - OR implement the curses rendering logic in the curses path (lines 278+)
   - OR delete the reference to `_draw_menu` at line 393 and implement proper curses drawing

2. **Fix division by zero** (`ui_manager.py:605`):
   - Change: `percent or current/total*100` → `percent or (current/total*100 if total > 0 else 0)`
   - OR handle the `total=0` case earlier in the method with an early return

3. **Fix test mocking** (`Tests/test_ui_manager_pytest.py`):
   - Remove `patch('ui_manager.UIManager._draw_menu')` from the four failing tests
   - OR verify the tests are testing the correct behavior and fix the mocking strategy

### Verification Steps

After fixes are applied, run:
```bash
python Tests/__init__.py
python -m pytest Tests/test_ui_manager_pytest.py -v
```

All tests should pass without exceptions or assertion errors.

---

## Files Modified (Not Yet)

- `ui_manager.py` (2 bugs)
- `Tests/test_ui_manager_pytest.py` (4 test bugs)

---

## Conclusion

The test suite exposes **2 bugs in the production code** and **2 bugs in the tests**. The production code bugs prevent `render_menu()` from functioning correctly when curses is enabled, and create a division-by-zero risk in edge cases. The test bugs prevent pytest from running certain test cases. All issues are straightforward to fix and do not indicate architectural problems.
