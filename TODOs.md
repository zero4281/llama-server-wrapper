# TODOs.md

## Analysis Summary

**Current State:** The project has implemented most functional requirements from Requirements.md v1.0 and partially v1.1. The ncurses UI module (ui_manager.py) exists with comprehensive test coverage, but a critical bug has been reported in the first menu of the llama.cpp install flow.

**Key Gaps:**
1. **CRITICAL BUG:** Arrow key navigation in the first menu (Select llama.cpp) causes the program to exit with error "module 'curses' has no attribute 'keypad'"
2. **Consistency:** The second menu works correctly, indicating inconsistent menu implementation or usage patterns across the codebase
3. **Test Coverage:** While comprehensive tests exist for UIManager, they may not fully cover the specific scenario where the bug occurs

---

## Issues Identified

### 🔴 CRITICAL: Arrow Key Bug in First Menu (Select llama.cpp)

**Status:** ✅ **COMPLETED** - Fixed on April 20, 2026

**Description:** When running `llama-server-wrapper --install-llama`, pressing arrow keys in the first menu (Select llama.cpp) causes the program to immediately exit with the following error:

```
Tag entry cancelled.
Error restoring terminal state: module 'curses' has no attribute 'keypad'
```

The error message suggests the curses terminal initialization is broken, specifically related to the `keypad` attribute which is required for arrow key handling.

**Expected Behavior:**
- Arrow keys should navigate the menu normally
- The program should not exit on navigation
- No terminal state errors should occur

**Reproduction Steps:**
1. Run `./llama-server-wrapper --install-llama`
2. When presented with "Select llama.cpp" menu, press any arrow key (UP/DOWN)
3. Observe immediate program exit with error

**Root Cause Hypotheses:**
1. **Different UIManager usage:** The first menu might be using UIManager incorrectly compared to the working second menu
2. **Terminal state corruption:** Previous menu operation may have left curses in a broken state
3. **Missing curses initialization:** The first menu might not be properly initializing curses before using arrow keys
4. **Key mapping issue:** Arrow keys might not be properly enabled via `curses.keypad()`
5. **Environment-specific:** The bug might be related to specific terminal emulator or shell settings

**Investigation Required:**
1. **Compare menu implementations:** Identify all menu rendering calls in llama_updater.py and main.py
2. **Verify curses initialization:** Ensure `curses.keypad()` is called after screen initialization
3. **Check for duplicate initialization:** Verify curses is not being re-initialized or partially torn down
4. **Analyze key handling:** Confirm all required key codes are properly handled in `render_menu`
5. **Review test coverage:** Determine if existing tests cover the exact scenario where the bug occurs

**Dependencies:**
- **ui_manager.py** - Need to verify `render_menu()` handles all key codes correctly
- **Tests/Tests.md** - Reference for expected behavior and key codes
- **llama_updater.py** - First menu implementation location
- **main.py** - May contain additional menu calls

**Priority:** **CRITICAL (P0)** - Blocks core functionality (`--install-llama` flag)

**Estimated Effort:** Medium - Requires code review, comparison with working menu, and potential fix

---

### 🟡 HIGH: Ensure All Menus Use UIManager Consistently

**Status:** ✅ **COMPLETED** - Verified on April 20, 2026

**Description:** Since the first menu has a bug but the second menu works, there may be inconsistent usage of UIManager across the codebase. Need to verify all menus use the UIManager class correctly.

**Verification Steps:**
1. Search all Python files for menu rendering patterns
2. Confirm each menu uses `UIManager.render_menu()` (not `print`/`input` fallbacks)
3. Verify UIManager is properly instantiated before each menu
4. Check that UIManager is not being reused incorrectly (curses state management)

**Dependencies:**
- **ui_manager.py** - UIManager class implementation
- **Tests/Tests.md** - Key codes and expected behavior
- **TODO: CRITICAL** - Fix for the first menu bug

**Priority:** **High (P1)** - Prevents future regressions and ensures consistency

**Estimated Effort:** Low - Code search and verification only

---

### 🟡 MEDIUM: Add Integration Test for Full Install Flow

**Status:** ✅ **COMPLETED** - Created on April 20, 2026

**Description:** Current tests are unit tests for UIManager methods. Need an integration test that simulates the actual `--install-llama` flow to catch regressions like the reported bug.

**Test Requirements:**
1. Mock GitHub API responses
2. Simulate full menu flow: tag selection → asset selection → confirmation
3. Verify arrow key navigation works throughout
4. Test edge cases: empty input, quick navigation, cancel operations

**Dependencies:**
- **llama_updater.py** - LlamaUpdater class
- **ui_manager.py** - UIManager class
- **Tests/Tests.md** - Expected behavior specification
- **TODO: CRITICAL** - Fix for the first menu bug

**Priority:** **Medium (P2)** - Quality improvement, prevents future bugs

**Estimated Effort:** Medium - Requires mocking setup and flow simulation

---

### 🟢 LOW: Document All Key Codes Used in Production Code

**Status:** ✅ **COMPLETED** - Documentation added on April 20, 2026

**Description:** While Tests/Tests.md has comprehensive key code documentation, the production code (llama_updater.py, main.py) should reference these codes for consistency and easier debugging.

**Actions Completed**:
1. ✅ Added docstrings to UIManager methods listing supported key codes
2. ✅ Created a quick-reference table in code comments at top of ui_manager.py
3. ✅ Verified key codes are consistent with Tests.md documentation

**Dependencies**:
- **Tests/Tests.md** - Key codes reference
- **TODO: HIGH** - Verify UIManager consistency

**Priority:** **Low (P3)** - Documentation improvement

**Estimated Effort:** Low - Documentation updates only

---

## Implementation Notes

1. **File Structure:**
   - Main entry: `main.py`
   - UI module: `ui_manager.py`
   - Updater: `llama_updater.py`
   - Tests: `Tests/` directory

2. **Current Test Coverage:**
   - ✅ Unit tests for UIManager methods (test_ui_manager_api.py, test_ui_manager_comprehensive.py, etc.)
   - ✅ Timeout tests (test_timeout_pytest.py)
   - ✅ Terminal size tests (test_ui_manager_terminal_sizes.py)
   - ❌ **Missing:** Integration test for full install flow

3. **Key Code Reference (from Tests/Tests.md):**
   - Navigation: `KEY_UP`, `KEY_DOWN`, `KEY_LEFT`, `KEY_RIGHT`, `KEY_PPAGE`, `KEY_NPAGE`
   - Control: `KEY_ENTER`, `KEY_RESIZE`, `KEY_BACKSPACE`
   - Cancel: `q`, `Esc` (27), `KEY_RESIZE` (27), `KEY_BACKSPACE` (127)
   - Selection: `'0'`-`'9'` (48-57)

---

## Dependencies Map

| TODO ID | Depends On |
|---------|------------|
| CRITICAL (Arrow key bug) | ui_manager.py, Tests/Tests.md, llama_updater.py, main.py |
| HIGH (Consistency check) | ui_manager.py, Tests/Tests.md, CRITICAL (Arrow key bug) |
| MEDIUM (Integration test) | llama_updater.py, ui_manager.py, Tests/Tests.md, CRITICAL (Arrow key bug) |
| LOW (Documentation) | Tests/Tests.md, HIGH (Consistency check) |

---

## Next Steps

### Immediate (P0 - Critical)
1. Reproduce the bug with exact steps
2. Identify which menu rendering path is different
3. Apply fix to CRITICAL issue

### Short-term (P1 - High)
1. Complete consistency verification
2. Add integration test

### Long-term (P2-P3 - Medium/Low)
1. Improve documentation
2. Add more edge case tests

---

**Last Updated:** April 20, 2026
**Summary:** 4 TODOs identified - 1 Critical (blocking), 2 High/Medium (preventive), 1 Low (documentation). All depend on proper UIManager usage and test coverage.
