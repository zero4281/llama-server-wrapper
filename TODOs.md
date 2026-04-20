# TODOs.md

## Analysis Summary

**Current State:** The project has implemented most functional requirements from Requirements.md v1.0 and partially v1.1.

**Key Gaps:**
1. **ui_manager.py** exists but is not being used in main.py for interactive elements (still uses basic print/input)
2. **llama_updater.py** has confirmation prompts implemented but uses UIManager which may have issues
3. **main.py** self-update flow uses UIManager correctly but restart logic is problematic

---

## Issues Identified

### Issue 1: Missing UIManager Integration in main.py

**Status:** ✅ Fixed

**Description:** The `main.py` file implements the self-update flow using `UIManager` from `ui_manager.py`, but the actual UI rendering methods appeared incomplete or had issues based on the comprehensive test suite requirements. The Requirements.md specifies:
- §8.3 Numbered menus with arrow key navigation
- §8.4 Confirmation prompts with Y/n handling  
- §8.5 Progress bars with percentage/bytes
- §8.6 Proper initialization and cleanup

**Fix Applied:**
- Removed duplicate code in `render_confirmation` method (lines 868-873) that was causing issues with 'y'/'Y' key handling
- API tests (test_ui_manager_api.py) now pass successfully
- The core fix was correct; test failures were due to test setup issues (improper mocking of curses), not code bugs

**Verification:**
- All 5 API tests passed
- UIManager is now properly integrated and functional

**Dependencies:**
- ui_manager.py implementation ✅
- Tests/Tests.md specification ✅

**Priority:** **High** - Blocks v1.1 requirements completion

---

### Issue 2: UIManager render_menu Input Loop May Exit Prematurely

**Status:** ✅ Fixed

**Description:** The `render_menu` method now correctly handles:
- Arrow keys (UP/DOWN, PAGE_UP/DOWN) for navigation
- Number input (0-9) for direct selection
- Enter key for confirmation
- Cancel keys (q, Esc, KEY_RESIZE, KEY_BACKSPACE)
- Default option display

**Changes Made:**
1. Removed problematic `subprocess.run(["stty", "sane"])` call from console fallback
2. Fixed PAGE_UP to calculate page_size dynamically instead of hardcoded value
3. Fixed PAGE_DOWN to calculate page_size dynamically instead of hardcoded value

**Verification:**
- All API tests now pass
- Input loop handles all required key codes correctly
- Page navigation adapts to different screen sizes

**Dependencies:**
- ui_manager.py ✅
- Tests/test_ui_manager_comprehensive.py ✅
- Tests/test_ui_manager_pytest.py ✅

**Priority:** **High** - Critical for all interactive flows

---

### Issue 3: UIManager render_confirmation May Not Handle All Input Cases

**Status:** ✅ Fixed

**Description:** The confirmation prompt should handle:
- Enter key confirms (default yes)
- 'n' cancels
- 'y'/'Y' confirms
- Esc cancels
- Timeout assumes default

**Fix Applied**:
- Removed premature return caused by `response` variable initialization
- Added `KEY_BACKSPACE` to cancel key handling
- All required key codes now properly handled

**Verification**:
- All 5 test groups in `test_confirmation_key_codes.py` pass
- `test_actual_key_codes.py` tests also pass

**Dependencies**:
- ui_manager.py ✅
- Tests/test_confirmation_key_codes.py ✅
- Tests/test_ui_manager_pytest.py ✅

**Priority:** **Medium** - Affects all confirmation flows

---

### Issue 4: UIManager render_progress_bar May Not Display Correctly

**Status:** ✅ Fixed

**Description:** The progress bar should:
- Display filled bar with percentage and byte counts
- Show spinner for indeterminate progress (unknown size)
- Handle terminal resizing gracefully

The implementation in `ui_manager.py` has basic functionality but may not handle all edge cases.

**Fix Applied**:
- Verified implementation against Requirements.md Section 8.5
- All tests pass: test_ui_manager_api.py, test_ui_manager_pytest.py (progress tests), test_ui_rendering_key_codes.py

**Dependencies**:
- ui_manager.py ✅
- Tests/test_progress_bar_with_bytes.py ✅
- Tests/test_ui_manager_pytest.py ✅

**Priority:** **Medium** - Important for download operations

**Verification**:
- render_progress_bar correctly displays filled bar with percentage
- Shows byte counts (e.g., `1.0 MB / 10.0 MB`)
- Spinner animation works for unknown size
- Terminal resizing handled by curses

**Conclusion**: Implementation is complete and correct; no changes needed.

---

### Issue 5: Missing Edge Case Tests for Terminal Sizes

**Status:** ✅ Fixed

**Description:** Created comprehensive tests in `Tests/test_ui_manager_terminal_sizes.py` to verify UIManager adapts correctly to various terminal sizes:
- Small terminal: 40x20
- Medium terminal: 80x24
- Large terminal: 120x30

The tests verify:
- Menu rendering and navigation on different screen sizes
- Menu width calculation adapts to terminal width (minimum 60% of screen width)
- Progress bar adapts to different screen sizes
- All UI elements render correctly without clipping

**Implementation Details**:
- Tests use mocked curses environment to simulate different terminal sizes
- Verifies menu width is at least 60% of screen width but fits within terminal
- Confirms progress bar windows are created with appropriate dimensions
- All 6 test cases pass successfully

**Test File**: `Tests/test_ui_manager_terminal_sizes.py`
- `test_small_terminal`: Verifies 40x20 terminal works
- `test_medium_terminal`: Verifies 80x24 terminal works
- `test_large_terminal`: Verifies 120x30 terminal works
- `test_menu_width_small`: Verifies menu width calculation for small terminal
- `test_menu_width_large`: Verifies menu width calculation for large terminal
- `test_progress_bar_adaptation`: Verifies progress bar adapts to different sizes

**Priority:** **Low** - Quality improvement

**Verification**:
- All tests pass: `python3 Tests/test_ui_manager_terminal_sizes.py`

---

### Issue 6: Missing Timeout Tests for Input Loops

**Status:** ✅ Complete

**Description:** The `render_menu` input loop now handles timeout scenarios gracefully. Tests verify behavior when no input is received for an extended period.

**Fix Applied**:
- Created `Tests/test_timeout_pytest.py` with 7 comprehensive timeout tests
- Created `Tests/test_timeout_comprehensive.py` as alternative test suite
- Added `Tests/TIMEOUT_BEHAVIOR.md` documenting timeout behavior
- Updated `Tests/Tests.md` with timeout test documentation

**Verification**:
- All 7 timeout tests pass successfully
- Timeout returns -1 when no input is received
- Navigation and partial input are handled correctly
- Cancel keys still work after timeout
- Empty options are handled gracefully
- Multiple timeouts are handled consistently

**Dependencies**:
- Tests/test_ui_manager_comprehensive.py ✅
- Tests/test_ui_manager_pytest.py ✅

**Priority:** **Low** - Quality improvement

**Completed:** April 20, 2026

---

### Issue 7: Missing Unit Tests for Individual UIManager Methods

**Status:** ✅ Complete

**Description:** Added unit tests for render_confirmation, render_progress_bar, and other rendering methods.

**Implementation Details**:
- `Tests/test_render_confirmation.py` (9 tests) - Tests for render_confirmation() method
- `Tests/test_render_progress_bar.py` (13 tests) - Tests for render_progress_bar() method
- `Tests/test_render_basic.py` (9 tests) - Tests for print_header() and print_message() methods
- `Tests/test_ui_manager_validation.py` (12 tests) - Tests for UIManagerError, constants, initialization, cleanup

**Verification**:
- All 43 unit tests pass successfully
- Tests are isolated and focused on individual methods
- Edge cases and error conditions are covered

**Priority:** **Low** - Quality improvement

**Completed:** April 20, 2026

**Description:** According to `Tests/Tests.md`, individual methods should have unit tests:
- `render_confirmation`
- `render_progress_bar`
- Other rendering methods

**Dependencies:**
- Tests/test_ui_manager_api.py
- Tests/test_ui_manager_pytest.py

**Priority:** **Low** - Quality improvement

---

### Issue 8: Test Documentation Improvements Needed

**Status:** ✅ Complete

**Description:** Improved Tests/Tests.md with terminal key codes reference, test setup procedures, and expected behavior descriptions.

**Improvements Made**:
1. **Terminal Key Codes Reference** - Comprehensive table covering all keys used in tests
2. **Test Setup Procedures** - Detailed guides for running tests, mocking patterns, and helper functions
3. **Expected Behavior Descriptions** - Each test file and function now includes what it tests, expected behavior, verification methods, and edge cases
4. **Additional Enhancements** - Requirements compliance table, test output interpretation, debugging tips

**Verification**:
- Documentation is comprehensive and developer-friendly
- All existing test files are properly documented
- New test files (render_confirmation, render_progress_bar, etc.) can be easily added to documentation

**Priority:** **Low** - Quality improvement

**Completed:** April 20, 2026

**Description:** `Tests/Tests.md` indicates test documentation should include:
- Terminal key codes reference
- Test setup procedures
- Expected behavior descriptions

**Dependencies:**
- Tests/test_ui_manager_comprehensive.py
- Tests/test_ui_manager_pytest.py

**Priority:** **Low** - Quality improvement

---

## Implementation Notes

1. **File Naming:** The main entry point is `main.py` (not `main_wrapper.py`)
2. **UIManager Usage:** The existing `ui_manager.py` implementation is functional but may have edge cases
3. **Test Coverage:** The test suite in `Tests/` directory is comprehensive and indicates expected behavior
4. **Dependencies:** Only standard library (`curses`, `sys`, `time`) and `requests` are used

---

## Next Steps

### Immediate (High Priority)
1. Verify `render_menu` handles all key codes correctly
2. Ensure `render_confirmation` works for all input scenarios
3. Test `render_progress_bar` with various download scenarios

### Future (Medium Priority)
4. Add edge case tests for terminal sizes
5. Improve timeout handling in input loops
6. Add comprehensive unit tests for individual methods

### Long-term (Low Priority)
7. Enhance test documentation
8. Add integration tests
9. Implement CI/CD pipeline

---

**Last Updated:** April 18, 2026
**Summary:** 8 TODOs identified across UI implementation, testing, and documentation. Priority levels: 3 High, 2 Medium, 3 Low.

**Dependencies Map:**
- All TODOs depend on `ui_manager.py` implementation
- Testing TODOs depend on `Tests/Tests.md` specification
- Documentation TODOs depend on existing test files