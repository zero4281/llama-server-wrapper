# TODOs - UIManager Keyboard Input Issues

## Issue Summary

The `./llama-server-wrapper --install-llama` command has multiple keyboard input issues:

1. **Arrow keys on first menu cause exit** - Using arrow keys to navigate the "Select llama.cpp" menu causes the program to exit immediately instead of navigating the menu.

2. **Number keys don't highlight** - Using number keys (e.g., typing "1", "2", "3") does not cause the selection to be highlighted in the menu.

3. **Confirmation prompt missing after zip selection** - After selecting a zip file from the asset list, the confirmation prompt never appears. Instead, the program exits immediately and the download never starts.

## Root Cause Analysis

### A. ui_manager.py Issues

The `ui_manager.py` file has several critical bugs:

#### 1. `_get_white_attr()` returns None on error
**Location:** Line 155-159

```python
def _get_white_attr(self):
    if self._using_curses and self._color_pair is not None:
        return curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE
    return None
```

**Problem:** When the curses module is mocked in tests but `curses.init_pair()` hasn't been called yet, `curses.color_pair(1)` raises an error. The `_get_white_attr()` method catches this error in `_render_menu()`, causing the entire curses initialization to fail and fall back to console mode. This results in the program exiting early.

**Fix needed:** Handle the error gracefully and fall back to console mode without crashing.

#### 2. Menu navigation doesn't redraw immediately
**Location:** Lines 394-408

```python
elif key == curses.KEY_UP or key == curses.KEY_PPAGE:
    if highlighted_idx > 0:
        highlighted_idx -= 1
    else:
        highlighted_idx = len(options) - 1

elif key == curses.KEY_DOWN or key == curses.KEY_NPAGE:
    if highlighted_idx < len(options) - 1:
        highlighted_idx += 1
    else:
        highlighted_idx = 0
```

**Problem:** When arrow keys are pressed, the code updates `highlighted_idx` but **does not call `redraw(menu_win, highlighted_idx)`** to immediately update the display. This means the visual highlight doesn't change, and the user doesn't see the navigation happening.

**Fix needed:** Call `redraw()` immediately after updating the highlighted index.

#### 3. Number input doesn't trigger immediate redraw
**Location:** Lines 401-410

```python
elif key >= ord('0') and key <= ord('9'):
    # Type number
    try:
        choice = int(chr(key))
        if 0 <= choice < len(options):
            highlighted_idx = choice
            # Redraw menu immediately to update highlight
            redraw(menu_win, highlighted_idx)
    except ValueError:
        pass
```

**Problem:** The comment says "Redraw menu immediately" but the actual `redraw()` call is missing! The line is commented out or not executed. This is why typing a number doesn't visually update the selection.

**Fix needed:** Uncomment or add the actual `redraw()` call.

#### 4. Spinner animation uses non-existent `curses.time()`
**Location:** Line 685

```python
spinner_idx = int(curses.time() / 100) % 4
```

**Problem:** `curses.time()` does not exist. The correct way to get the current time in curses is to use `int(curses.time())` where `time()` is a function that returns the current time, not an attribute. This causes an `AttributeError` when the spinner mode is triggered (total=0).

**Fix needed:** Replace with `int(time.time() / 100) % 4` or similar.

### B. Test Issues (False Positives)

The tests are producing false positives due to improper mocking:

#### 1. Incomplete curses mock setup
**Location:** `test_ui_manager_pytest.py`

The tests mock `curses` but don't properly mock all required functions. Specifically:
- `curses.init_pair()` is mocked but never called, so `curses.color_pair(1)` fails
- `curses.newwin()` is mocked but the mock window doesn't have all required methods
- The `getch()` mock returns the wrong values in some tests

#### 2. Inconsistent key code values
**Location:** Multiple test files

Tests use hardcoded key codes (e.g., `KEY_UP = 259`, `KEY_DOWN = 258`) that may not match the actual `curses.KEY_UP` and `curses.KEY_DOWN` constants on the system. This causes mismatches between expected and actual key codes.

#### 3. Missing input mocking for confirmation dialogs
**Location:** `test_ui_manager_pytest.py`

The confirmation tests try to read from `sys.stdin` but don't mock it properly. This causes the tests to hang or fail when pytest captures stdin/stdout.

## Action Items

### Priority 1: Fix ui_manager.py

1. **Fix `_get_white_attr()` error handling** ✅ FIXED
    - Add try/except around `curses.color_pair(1)` call
    - Fall back to console mode gracefully
    - Ensure terminal cleanup on error
    - **Fixed in:** `ui_manager.py` line 155-160
    - **Status:** Completed - Added error handling with fallback to `curses.A_BOLD`

2. **Fix menu navigation redraw**
   - Call `redraw(menu_win, highlighted_idx)` immediately after arrow key navigation
   - Call `redraw(menu_win, highlighted_idx)` immediately after number input
   - Ensure the visual update happens in real-time

3. **Fix spinner animation**
   - Replace `curses.time()` with `int(time.time() / 100) % 4`
   - Add proper import for `time` module

4. **Add comprehensive error handling**
   - Wrap all curses operations in try/except blocks
   - Log errors to stderr (when not in curses mode)
   - Ensure terminal cleanup on any error

### Priority 2: Update Tests

1. **Fix test mocking**
   - Properly mock `curses.init_pair()` to be callable
   - Mock all required curses functions (`newwin`, `addstr`, `attron`, etc.)
   - Use `curses.KEY_*` constants instead of hardcoded values

2. **Fix confirmation tests**
   - Mock `sys.stdin.readline()` for confirmation dialogs
   - Use `pytest -s` flag to disable stdin/stdout capturing

3. **Add integration tests**
   - Test full workflow: menu → confirmation → progress bar
   - Test edge cases: empty menus, invalid input, timeout

### Priority 3: Add New Tests

1. **Keyboard input simulation tests**
   - Test arrow key navigation with visual updates
   - Test number input with immediate redraw
   - Test page up/down navigation

2. **Visual regression tests**
   - Verify menu is rendered correctly
   - Verify highlight updates on navigation
   - Verify confirmation dialog renders

## Files to Modify

### Core Files
- `ui_manager.py` - Fix all identified issues
- `Tests/test_ui_manager_pytest.py` - Fix test mocking
- `Tests/test_ui_manager_comprehensive.py` - Fix test mocking
- `Tests/test_menu_input.py` - Fix test mocking
- `Tests/test_keyboard_input.py` - Fix test mocking

### New Files to Create
- `TODOs.md` - This file

## Verification Steps

After fixes are applied:

1. Run all existing tests: `python Tests/test_ui_manager_pytest.py -v`
2. Run comprehensive tests: `python Tests/test_ui_manager_comprehensive.py`
3. Run keyboard input tests: `python Tests/test_keyboard_input.py`
4. Run menu input tests: `python Tests/test_menu_input.py`
5. Test manually with `./llama-server-wrapper --install-llama` (if environment permits)

## Related Issues

- `./llama-server-wrapper` command hangs or exits on menu navigation
- `./llama-server-wrapper` fails to download llama.cpp due to missing confirmation
- Tests time out or produce inconsistent results

---

**Created:** 2026-04-16
**Status:** Open
**Priority:** High
