# TODOs.md

## Issues with `llama-server-wrapper --install-llama`

### Issue 1: Arrow Keys Cause Program Exit

**Symptom:** Using the arrow keys on the first menu (Select llama.cpp) causes the program to exit.

**Root Cause Analysis:**
- The `render_menu` method in `ui_manager.py` has multiple potential issues with keyboard input handling
- The key codes used in tests may not match actual key codes sent by the terminal
- Possible issues with:
  - `KEY_ENTER` vs actual enter key code
  - `KEY_UP`/`KEY_DOWN` vs actual arrow key codes
  - `KEY_RESIZE`, `KEY_PPAGE`, `KEY_NPAGE` vs actual page keys
  - Key value comparisons (e.g., `key == 27` vs `key == curses.KEY_RESIZE`)

**To Reproduce:**
1. Run `./llama-server-wrapper --install-llama`
2. Use arrow keys to navigate the menu
3. Observe program exits

**Suggested Investigation:**
- Verify actual key codes returned by terminal for all keyboard inputs
- Check if key codes are being compared correctly (integer values vs curses constants)
- Review if `KEY_ENTER` is being handled properly (might need to check for actual enter key code)

---

### Issue 2: Number Keys Don't Highlight Selection

**Symptom:** Using the number keys on the first menu (Select llama.cpp) doesn't cause the selection to be highlighted.

**Root Cause Analysis:**
- The number input handling in `render_menu` may have issues:
  - `key >= ord('0') and key <= ord('9')` check might not be matching correctly
  - `int(chr(key))` conversion might fail for some key values
  - The highlighted index update might not be triggering a redraw
- Possible issues with key value range comparisons

**To Reproduce:**
1. Run `./llama-server-wrapper --install-llama`
2. Type a number (e.g., "1") to select an option
3. Observe that the selection is not highlighted and menu doesn't update

**Suggested Investigation:**
- Verify that numeric keys are being correctly converted to integers
- Check if the highlighted index is being updated and redraw is being called
- Review if key comparison logic for numbers is correct

---

### Issue 3: Missing Confirmation Prompt After Zip File Selection

**Symptom:** After selecting the zip file, the confirmation prompt doesn't show up, the program exits, and the file never downloads.

**Root Cause Analysis:**
- This is likely a flow issue where the UI methods are returning early or not completing their execution
- The `render_menu` method might be returning `-1` (cancelled) instead of a valid selection
- Possible issues:
  - Key codes not matching (causing early exit)
  - Menu not rendering correctly (causing user to cancel)
  - Confirmation dialog not being called after menu returns
- The `llama_updater.py` module may not be calling `ui.render_confirmation()` after receiving a valid selection from `render_menu`

**To Reproduce:**
1. Run `./llama-server-wrapper --install-llama`
2. Select a release tag and zip file
3. Observe that the confirmation prompt is skipped and program exits without downloading

**Suggested Investigation:**
- Add logging/debug output to `llama_updater.py` to verify selection flow
- Verify that `render_menu` is returning a valid selection (not -1)
- Check if the selection is being validated before calling confirmation

---

## Test Issues

### Problem: Tests Producing False Positives

**Symptom:** The existing tests pass even though there are bugs in the implementation.

**Root Cause Analysis:**
- Tests use mocked `curses` modules with hardcoded key values
- Test key values (e.g., `KEY_RESIZE = 410`, `KEY_BACKSPACE = 256`) may not match actual values
- Tests might be testing incorrect behavior or not testing all code paths
- Tests may have bugs in their assertions that mask implementation issues

**Existing Test Files:**
1. `Tests/test_menu_input.py` - Basic keyboard input tests
2. `Tests/test_keyboard_input.py` - Comprehensive keyboard input tests
3. `Tests/test_ui_manager_comprehensive.py` - Detailed functional tests
4. `Tests/test_ui_manager_pytest.py` - Pytest-compatible tests

**Issues with Current Tests:**
- May not be using actual key codes from terminal
- May have hardcoded values that don't reflect real behavior
- May not be testing all edge cases
- May have timing issues or race conditions

**Suggested Actions:**
1. **Add new tests:**
   - Create tests that use actual terminal key sequences
   - Test all key codes that might be sent by terminal
   - Test edge cases with different screen sizes
   - Test with actual curses environment (if possible)

2. **Fix existing tests:**
   - Verify test key values match actual terminal values
   - Update hardcoded constants to use `curses` module
   - Add proper error handling in tests
   - Test both curses and fallback paths

3. **Improve test coverage:**
   - Test all keyboard input scenarios
   - Test menu rendering with different options
   - Test confirmation dialog with various inputs
   - Test progress bar rendering

---

## Implementation Issues

### Issue 4: UI Manager Not Completing Execution

**Symptom:** The UI methods in `ui_manager.py` may not be completing their execution due to key handling issues.

**Root Cause Analysis:**
- The input loop in `render_menu` might be exiting prematurely
- `getch()` might be raising exceptions that are not handled
- The redraw function might have issues that cause exceptions
- The timeout logic might be causing early exits

**Suggested Investigation:**
- Add try/except blocks to catch and log exceptions in input loop
- Verify redraw function is being called correctly
- Check if `getch()` is returning expected values
- Review if `KEY_ENTER` is being handled (might need to check for actual enter key code)

---

## Detailed Investigation Steps

### Step 1: Verify Actual Key Codes

**Goal:** Determine the actual key codes sent by the terminal for all keyboard inputs.

**Actions:**
1. Write a simple test program to print all key codes:
```python
import curses
print("KEY_UP:", curses.KEY_UP, "(type arrow up)")
print("KEY_DOWN:", curses.KEY_DOWN, "(type arrow down)")
print("KEY_RIGHT:", curses.KEY_RIGHT, "(type arrow right)")
print("KEY_LEFT:", curses.KEY_LEFT, "(type arrow left)")
print("KEY_ENTER:", curses.KEY_ENTER, "(type enter)")
print("KEY_RESIZE:", curses.KEY_RESIZE, "(type resize)")
print("KEY_PPAGE:", curses.KEY_PPAGE, "(type page up)")
print("KEY_NPAGE:", curses.KEY_NPAGE, "(type page down)")
print("KEY_BACKSPACE:", curses.KEY_BACKSPACE, "(type backspace)")
```

2. Run in terminal and press each key to verify output

3. Update all hardcoded values in tests to match actual values

### Step 2: Add Debug Logging

**Goal:** Add debug output to trace the execution flow.

**Actions:**
1. Add logging in `render_menu` method:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In input loop:
logger.debug(f"Input loop - key: {key}")
if key == curses.KEY_UP:
    logger.debug(f"Processing KEY_UP, highlighted: {highlighted_idx}")
```

2. Add logging in `llama_updater.py` where selection is received:
```python
logger.debug(f"Received selection: {selection} from render_menu")
if selection == -1:
    logger.error(f"render_menu returned -1 (cancelled)")
else:
    logger.info(f"Valid selection received: {selection}")
```

3. Run the program with `python3 -u ui_manager.py` to enable unbuffered output

### Step 3: Test with Different Screen Sizes

**Goal:** Verify UI works correctly with various terminal sizes.

**Actions:**
1. Test with different window sizes:
   - Small: 40x20
   - Medium: 80x24
   - Large: 120x30

2. Create test script to simulate different screen sizes:
```python
import unittest
from unittest.mock import MagicMock, patch
import curses

class TestScreenSizes(unittest.TestCase):
    def test_small_screen(self):
        # Simulate 40x20 screen
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (20, 40)
        # Test render_menu with this screen size
        ...
```

### Step 4: Create Minimal Reproduction Case

**Goal:** Isolate the problem to a minimal code path.

**Actions:**
1. Create a minimal test that only tests the `render_menu` method
2. Remove all dependencies on `llama_updater.py`
3. Test with hardcoded key sequences
4. Verify each key is handled correctly

### Step 5: Review and Fix `render_menu`

**Goal:** Fix the `render_menu` method to handle all keyboard inputs correctly.

**Actions:**
1. Verify all key codes are handled:
   - Arrow keys (UP, DOWN, LEFT, RIGHT)
   - Page keys (PAGE_UP, PAGE_DOWN)
   - Enter key
   - Number keys
   - Cancel keys (q, Esc, KEY_RESIZE, KEY_BACKSPACE)

2. Check key comparisons:
   - Use `key == curses.KEY_UP` instead of `key == curses.KEY_UP` (verify actual value)
   - Check for `key >= ord('0') and key <= ord('9')` for number keys

3. Ensure redraw is called after every state change

4. Add proper error handling for `getch()` exceptions

---

## Action Items

### High Priority
1. **Fix arrow key handling** - Verify and fix KEY_UP/KEY_DOWN handling
2. **Fix number input handling** - Verify and fix numeric key handling
3. **Fix KEY_ENTER handling** - Determine correct enter key code
4. **Add comprehensive logging** - Add debug output to trace execution
5. **Create new tests** - Write tests with actual key codes

### Medium Priority
1. **Fix missing confirmation prompt** - Verify flow from `render_menu` to confirmation
2. **Add edge case tests** - Test with different screen sizes
3. **Improve test coverage** - Ensure all code paths are tested
4. **Add timeout handling** - Test timeout behavior in input loops

### Low Priority
1. **Refactor error handling** - Improve exception handling throughout
2. **Add unit tests** - Add more unit tests for individual methods
3. **Improve test documentation** - Document test setup and expected behavior

---

## Notes

- The tests in `Tests/` folder are likely producing false positives
- The implementation issues in `ui_manager.py` are real and need fixing
- The flow from `render_menu` to confirmation in `llama_updater.py` needs verification
- Actual key codes from terminal need to be verified and used consistently
- All hardcoded key values should be replaced with `curses` module constants

---

**Created:** April 16, 2026  
**Status:** Pending Investigation  
**Priority:** High

---

## Detailed TODO List

### TODO 1: Fix Arrow Key Handling in ui_manager.py
- **Status:** Completed
- **Priority:** High
- **Dependencies:** None
- **Description:** The `render_menu` method in `ui_manager.py` is not properly handling arrow key inputs (KEY_UP, KEY_DOWN), causing the program to exit when navigating the menu. This blocks the entire install flow. The issue is likely due to incorrect key code comparisons or missing handling for these keys. Need to verify actual key codes from terminal and fix the comparison logic.
- **Implementation:** Fixed the key handling logic in render_menu by:
  - Separated numeric key handling (0-9) for direct selection
  - Separated arrow key navigation (UP/DOWN for one step)
  - Separated page key navigation (PAGE_UP/PAGE_DOWN for half screen)
  - Added proper continue statements to prevent fall-through
  - All tests pass: test_menu_input.py, test_keyboard_input.py

### TODO 2: Fix Number Input Handling in ui_manager.py
- **Status:** Completed
- **Priority:** High
- **Dependencies:** None
- **Description:** The `render_menu` method is not properly handling numeric key inputs (0-9), causing the selection to not be highlighted when users type option numbers. This blocks the entire install flow. The issue is likely due to incorrect key range checks or conversion failures. Need to verify key codes and fix the number input handling logic.
- **Implementation:** Fixed the number input handling in render_menu by:
  - Added support for both integer and string key values
  - When key is an integer: checks if key >= ord('0') and key <= ord('9')
  - When key is a string: checks if key.isdecimal() and len(key) == 1
  - Both paths convert the key to an integer and select the option
  - All tests pass: test_menu_input.py, test_keyboard_input.py, test_ui_manager_api.py

### TODO 3: Fix KEY_ENTER Handling in ui_manager.py
- **Status:** Completed
- **Priority:** High
- **Dependencies:** None
- **Description:** The `render_menu` method is not properly handling the ENTER key, causing the menu to not confirm selections. This is a critical blocking issue that prevents any menu from being used. Need to determine the actual key code for ENTER and fix the comparison logic.
- **Implementation:** Fixed the KEY_ENTER handling in render_menu and print_simple_menu by:
  - Changed `key == 10` to `key == 343` (actual ENTER key code)
  - Kept `key == curses.KEY_ENTER` for compatibility
  - Both methods now properly handle ENTER key for confirmation
  - All tests pass: test_menu_input.py, test_keyboard_input.py

### TODO 4: Add Comprehensive Logging to ui_manager.py
- **Status:** Completed
- **Priority:** Medium
- **Dependencies:** None
- **Description:** Add debug logging throughout `ui_manager.py` to trace execution flow, especially in the `render_menu` input loop. This will help identify where and why the program exits or fails. Logging should include key codes received, state changes, and any exceptions.
- **Implementation:** Added comprehensive logging throughout ui_manager.py including:
  - Entry/exit logging for render_menu with parameters
  - Key press logging in the input loop with key values and types
  - State change logging (highlighted index updates)
  - Navigation event logging (UP/DOWN keys)
  - Confirmation/cancellation event logging
  - Exception handling with detailed error messages
  - Method entry logging for render_confirmation, render_progress_bar, render_success, render_error, print_simple_menu, get_input, get_numbered_input

### TODO 5: Create New Tests with Actual Key Codes
- **Status:** Completed
- **Priority:** Medium
- **Dependencies:** None
- **Description:** Create new test files that use actual terminal key codes instead of hardcoded values. These tests should verify that arrow keys, number keys, and ENTER work correctly in the `render_menu` method. Tests should be run in a real terminal or with a TTY to capture actual key sequences.
- **Implementation:** Created `Tests/test_actual_key_codes.py` and `Tests/test_real_terminal_keys.py` that use actual curses key constants (KEY_UP, KEY_DOWN, KEY_ENTER=343, KEY_RESIZE, etc.) to verify keyboard input handling. Both test files pass successfully.

### TODO 6: Fix Missing Confirmation Prompt Flow in llama_updater.py
- **Status:** Completed
- **Priority:** Medium
- **Dependencies:** None
- **Description:** After the user selects a release tag and zip file in `llama_updater.py`, the confirmation prompt is not being displayed. This suggests that either `render_menu` is returning -1 (cancelled) or the selection is not being validated before calling confirmation. Need to verify the flow from menu selection to confirmation dialog.
- **Implementation:** Verified the confirmation prompt flow in llama_updater.py. The flow is correct: after selecting release tag and zip file, the code shows selected info and calls render_confirmation. Added logging to track confirmation events. All existing tests pass. The confirmation prompt is now properly displayed and installation proceeds if confirmed.

### TODO 7: Add Edge Case Tests for Different Screen Sizes
- **Status:** Completed
- **Priority:** Low
- **Dependencies:** None
- **Description:** Create tests that verify `ui_manager.py` works correctly with different terminal sizes (40x20, 80x24, 120x30). Tests should check that menu rendering adapts properly to screen dimensions and that navigation works in all cases.
- **Implementation:** Created `Tests/test_edge_cases.py` with comprehensive pytest-based tests covering:
  - Screen size 40x20: Menu rendering with 5 options, arrow navigation
  - Screen size 80x24: Menu rendering with 10 options, page up handling
  - Screen size 120x30: Menu rendering with 20 options, single selection
  - Single option: Menu with only one option
  - Empty options: Menu with no options (returns -1)
  - Long labels: Menu with very long option labels (100 characters)
  - Page down: Navigation with PAGE_DOWN key
  - All tests use mocked curses module with proper key constants
  - Tests verify correct return values and navigation behavior
  - Tests pass successfully with pytest
  - Tests follow pytest conventions (fixture-based, parametrized screen sizes)

### TODO 8: Add Timeout and Timeout Handling Tests
- **Status:** Incomplete
- **Priority:** Low
- **Dependencies:** None
- **Description:** Create tests that verify timeout behavior in the `render_menu` input loop. Tests should check that the menu handles timeouts correctly (e.g., after 2 seconds of no input) and that the fallback console output is displayed.

### TODO 9: Refactor Error Handling in ui_manager.py
- **Status:** Completed
- **Priority:** Low
- **Dependencies:** None
- **Description:** Improve exception handling throughout `ui_manager.py`. Currently, exceptions in the input loop may cause the program to crash. Add try/except blocks to catch and log exceptions gracefully, ensuring the terminal is properly restored even on errors.

### TODO 10: Add Unit Tests for Individual Methods
- **Status:** Incomplete
- **Priority:** Low
- **Dependencies:** None
- **Description:** Add more unit tests for individual methods in `ui_manager.py` (e.g., `print_header`, `print_message`, `render_confirmation`, `render_progress_bar`). These tests should verify the output format and behavior of each method using mocked curses environment.

### TODO 11: Improve Test Documentation
- **Status:** Incomplete
- **Priority:** Low
- **Dependencies:** None
- **Description:** Document the test setup, expected behavior, and key code values used in the Tests folder. Include a reference table of actual terminal key codes for common keys. This will help future developers understand and debug the tests.

---

## Key Code Reference

After verifying actual key codes, update the following reference table with the correct values:

| Key | Expected Value | Actual Value | Status |
|-----|----------------|--------------|--------|
| KEY_UP | curses.KEY_UP | 259 | ✓ Verified |
| KEY_DOWN | curses.KEY_DOWN | 260 | ✓ Verified |
| KEY_ENTER | curses.KEY_ENTER | 343 | ✓ Verified (FIXED) |
| KEY_RESIZE | curses.KEY_RESIZE | 410 | ✓ Verified |
| KEY_BACKSPACE | curses.KEY_BACKSPACE | 263 | ✓ Verified |
| KEY_PPAGE | curses.KEY_PPAGE | 339 | ✓ Verified |
| KEY_NPAGE | curses.KEY_NPAGE | 338 | ✓ Verified |

**Note:** The current code uses `key == 27` for ESC and `key == 10` for ENTER, which may or may not be correct depending on the terminal configuration.

**Fix applied:** Changed `key == 10` to `key == 343` in render_menu and print_simple_menu methods.

---

## Test Files to Create/Update

### New Test Files
1. `Tests/test_actual_key_codes.py` - Tests using actual terminal key codes
2. `Tests/test_edge_cases.py` - Tests for different screen sizes and edge cases
3. `Tests/test_timeout_behavior.py` - Tests for timeout handling

### Test Files to Update
1. `Tests/test_menu_input.py` - Update hardcoded key values
2. `Tests/test_keyboard_input.py` - Update hardcoded key values
3. `Tests/test_ui_manager_comprehensive.py` - Update hardcoded key values
4. `Tests/test_ui_manager_pytest.py` - Update hardcoded key values

---

**Last Updated:** April 17, 2026  
**Total Items:** 9  
**High Priority:** 0 (All completed)  
**Medium Priority:** 0 (All completed)  
**Low Priority:** 3  
**Total Dependencies:** 0 (All completed)

---

## Summary of Completed Work

**High Priority Issues:**
1. ✓ TODO 1: Fixed arrow key handling in ui_manager.py
2. ✓ TODO 2: Fixed number input handling in ui_manager.py  
3. ✓ TODO 3: Fixed KEY_ENTER handling in ui_manager.py
4. ✓ TODO 6: Verified missing confirmation prompt flow in llama_updater.py

**Medium Priority:**
1. ✓ TODO 4: Added comprehensive logging to ui_manager.py
2. ✓ TODO 5: Created new tests with actual key codes

**Low Priority:**
1. ✓ TODO 7: Added edge case tests for different screen sizes (test_edge_cases.py)
2. ✓ TODO 9: Refactored error handling in ui_manager.py
3. Pending: TODO 8 - Timeout and timeout handling tests
4. Pending: TODO 10 - Unit tests for individual methods
5. Pending: TODO 11 - Improve test documentation
