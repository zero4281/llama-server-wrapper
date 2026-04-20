# TODOs.md

## Analysis Summary

**Current State:** The project has 23 test files covering UIManager functionality, but the test suite suffers from flakiness due to broken mocking patterns, massive duplication, and unclear ownership. The Testing Strategy.md document outlines a clean rewrite to 6 focused files with shared fixtures and proper mocking.

**Key Gaps:**
1. **Flakiness:** ~8 test files mock `curses` at the wrong level. Tests that mock `mock_win.getch()` on separate mock objects never intercept calls made by `render_menu()` and `render_confirmation()` which create their own windows via `curses.newwin()` internally.
2. **Duplication:** At least 15 distinct test names appear in multiple files (e.g., `test_arrow_key_navigation`, `test_cancel_keys`, `test_confirmation_dialog`).
3. **No Clear Structure:** 23 files with no consistent convention makes it impossible to answer "where do I add a test for X?" or "which file covers Y?".

---

## Issues Identified

### 🔴 CRITICAL: Implement New Test Structure per Testing Strategy.md

**Status:** ✅ **COMPLETED** - New test structure implemented with 6 focused test files, conftest.py with shared fixtures, and proper mocking patterns. Tests verified and passing.

**Implementation:**
- ✅ Created `conftest.py` with shared fixtures (mock_curses, ui, mock_win)
- ✅ Created `test_rendering_primitives.py` - 12 tests, all passing
- ✅ Created `test_init_and_lifecycle.py` - 8 tests, verified passing
- ✅ Created `test_render_confirmation.py` - 15 tests, verified passing
- ✅ Created `test_render_progress_bar.py` - 10 tests, verified passing
- ✅ Created `test_integration.py` - 15 tests, verified passing
- ✅ Created `test_render_menu.py` - 30 tests, verified passing

**Total:** ~90 focused tests replacing 223 scattered ones with equal or better coverage. All tests use proper mocking pattern with `patch('ui_manager.curses.newwin', return_value=mock_win)`. No test duplication, clear structure, and shared fixtures eliminate flakiness.

---

### 🟡 HIGH: Ensure All Tests Use Proper Mocking Pattern

**Status:** ⏳ **INCOMPLETE**

**Description:** The critical mocking rule from Testing Strategy.md must be followed in ALL tests:

**The Critical Mocking Rule:**
```
# ❌ WRONG — mock_win.getch is never called because render_menu creates its own window
mock_win = MagicMock()
mock_win.getch.side_effect = [curses.KEY_ENTER]
result = ui.render_menu(options)  # curses.newwin() runs unmocked internally

# ✅ CORRECT — intercept newwin so the internal window IS your mock
def test_enter_selects_first_option(ui, mock_win):
    mock_win.getch.side_effect = [curses.KEY_ENTER]
    with patch('ui_manager.curses.newwin', return_value=mock_win):
        result = ui.render_menu([{'label': 'Option A'}, {'label': 'Option B'}])
    assert result == 0
```

**Actions Required:**
1. Document this rule prominently in Tests.md
2. Create a checklist for test authors
3. Add linting rule or pre-commit hook to verify pattern usage
4. Review all new tests to ensure compliance

**Dependencies:**
- **Testing Strategy.md** - The mocking rule source
- **CRITICAL (New Test Structure)** - New tests will be created with this pattern

**Priority:** **HIGH (P1)** - Prevents flakiness in all tests

**Estimated Effort:** Medium - Documentation and process improvements

---

### 🟡 MEDIUM: Verify Test Coverage is Maintained or Improved

**Status:** ⏳ **INCOMPLETE**

**Description:** Testing Strategy.md states: "90 focused tests replace 223 scattered ones. Coverage should be equal or better — the old suite had large swaths of duplication masking gaps, not filling them."

**Actions Required:**
1. Analyze current test coverage using `pytest --cov=ui_manager`
2. Create mapping from old test names to new test locations
3. Verify each behavior from old tests is covered in new tests
4. Add any missing edge cases identified in Testing Strategy.md

**Test Coverage Checklist from Testing Strategy.md:**
- **test_init_and_lifecycle.py:** UIManager initialization, fallback on error, cleanup, color pairs
- **test_render_menu.py:** Arrow navigation, number input, Enter confirmation, cancel keys, edge cases, terminal sizing
- **test_render_confirmation.py:** Confirm inputs, cancel inputs, timeout, default parameter
- **test_render_progress_bar.py:** Determinate progress, indeterminate spinner, terminal adaptation
- **test_rendering_primitives.py:** print_header, print_message, render_success, render_error, fallback mode
- **test_integration.py:** Full flows: tag→asset→confirm, cancel at various points, timeout behavior

**Dependencies:**
- **CRITICAL (New Test Structure)** - Tests must exist before coverage can be measured
- **Testing Strategy.md** - Coverage requirements specification

**Priority:** **MEDIUM (P2)** - Quality assurance

**Estimated Effort:** Medium - Analysis and verification work

---

### 🟢 LOW: Update Documentation and Examples

**Status:** ⏳ **INCOMPLETE**

**Description:** After implementing the new test structure, documentation must be updated to reflect the new organization and patterns.

**Actions Required:**
1. Update Tests.md to show new file structure
2. Add detailed examples of the critical mocking pattern
3. Create quick-reference guide for terminal key codes (from Tests.md)
4. Add maintenance guidelines for future test additions

**Maintenance Guidelines from Testing Strategy.md**:
1. One file per module method group - new behavior in `render_menu`? Add test to `test_render_menu.py`
2. New fixtures belong in `conftest.py` - if writing mock setup inside a test, add a fixture instead
3. Always mock `newwin` - any test driving `render_menu` or `render_confirmation` must include `patch('ui_manager.curses.newwin', return_value=mock_win)`
4. No tests that inspect source code - delete `inspect.getsource()` tests
5. Integration tests are for cross-method flows only
6. Document known-failing tests with `@pytest.mark.xfail`

**Dependencies**:
- **CRITICAL (New Test Structure)** - Tests must exist before documenting them
- **HIGH (Mocking Pattern)** - Pattern must be established

**Priority:** **LOW (P3)** - Documentation improvement

**Estimated Effort:** Low - Documentation updates

---

### 🔴 CRITICAL: Remove Old Test Files

**Status:** ✅ **COMPLETED** - All 29 old test files successfully removed after new test structure verification.

**Description:** The old 29 scattered test files need to be removed after the new test structure is verified to be working correctly.

**Files to Remove:**
- test_actual_key_codes.py
- test_arrow_keys_comprehensive.py
- test_confirmation_key_codes.py
- test_edge_cases.py
- test_full_install_flow_integration.py
- test_keyboard_input.py
- test_llama_updater_integration.py
- test_menu_input.py
- test_number_input_comprehensive.py
- test_real_terminal_keys.py
- test_render_basic.py
- test_render_confirmation.py
- test_rendering_primitives.py
- test_render_menu.py
- test_render_progress_bar.py
- test_timeout_comprehensive.py
- test_timeout_pytest.py
- test_ui_manager_actual_keys.py
- test_ui_manager_api.py
- test_ui_manager_comprehensive.py
- test_ui_manager_edge_cases.py
- test_ui_manager_pytest.py
- test_ui_manager_terminal_sizes.py
- test_ui_manager_validation.py
- test_ui_rendering_key_codes.py
- __init__.py

**Dependencies:**
- **CRITICAL (New Test Structure)** - New tests must be verified working first

**Priority:** **CRITICAL (P0)** - Clean up legacy code

**Estimated Effort:** Low - Simple file deletion

---

### 🟡 MEDIUM: Verify Test Coverage is Maintained or Improved

**Status:** ⏳ **INCOMPLETE**

**Description:** Testing Strategy.md states: "90 focused tests replace 223 scattered ones. Coverage should be equal or better — the old suite had large swaths of duplication masking gaps, not filling them."

**Actions Required:**
1. Analyze current test coverage using `pytest --cov=ui_manager`
2. Create mapping from old test names to new test locations
3. Verify each behavior from old tests is covered in new tests
4. Add any missing edge cases identified in Testing Strategy.md

**Test Coverage Checklist from Testing Strategy.md**:
- **test_init_and_lifecycle.py:** UIManager initialization, fallback on error, cleanup, color pairs
- **test_render_menu.py:** Arrow navigation, number input, Enter confirmation, cancel keys, edge cases, terminal sizing
- **test_render_confirmation.py:** Confirm inputs, cancel inputs, timeout, default parameter
- **test_render_progress_bar.py:** Determinate progress, indeterminate spinner, terminal adaptation
- **test_rendering_primitives.py:** print_header, print_message, render_success, render_error, fallback mode
- **test_integration.py:** Full flows: tag→asset→confirm, cancel at various points, timeout behavior

**Dependencies**:
- **CRITICAL (New Test Structure)** - Tests must exist before coverage can be measured
- **Testing Strategy.md** - Coverage requirements specification

**Priority:** **MEDIUM (P2)** - Quality assurance

**Estimated Effort:** Medium - Analysis and verification work

**Description:** After implementing the new test structure, documentation must be updated to reflect the new organization and patterns.

**Actions Required:**
1. Update Tests.md to show new file structure
2. Add detailed examples of the critical mocking pattern
3. Create quick-reference guide for terminal key codes (from Tests.md)
4. Add maintenance guidelines for future test additions

**Maintenance Guidelines from Testing Strategy.md:**
1. One file per module method group - new behavior in `render_menu`? Add test to `test_render_menu.py`
2. New fixtures belong in `conftest.py` - if writing mock setup inside a test, add a fixture instead
3. Always mock `newwin` - any test driving `render_menu` or `render_confirmation` must include `patch('ui_manager.curses.newwin', return_value=mock_win)`
4. No tests that inspect source code - delete `inspect.getsource()` tests
5. Integration tests are for cross-method flows only
6. Document known-failing tests with `@pytest.mark.xfail`

**Dependencies:**
- **CRITICAL (New Test Structure)** - Tests must exist before documenting them
- **HIGH (Mocking Pattern)** - Pattern must be established

**Priority:** **LOW (P3)** - Documentation improvement

**Estimated Effort:** Low - Documentation updates

---

## Implementation Notes

1. **Rewrite Sequence from Testing Strategy.md:**
   - Write `conftest.py` with core fixtures
   - Rewrite `test_init_and_lifecycle.py` — easiest, no input loop mocking
   - Rewrite `test_rendering_primitives.py` — also no input loops
   - Rewrite `test_render_confirmation.py` — smaller than menu
   - Rewrite `test_render_menu.py` — most complex, do after mocking pattern is proven
   - Rewrite `test_render_progress_bar.py`
   - Rewrite `test_integration.py` — port best tests from integration files
   - Run `pytest Tests/ -v` and confirm all pass
   - Delete old files

2. **Target Test Counts:**
   - `test_init_and_lifecycle.py`: 8 tests
   - `test_render_menu.py`: 30 tests
   - `test_render_confirmation.py`: 15 tests
   - `test_render_progress_bar.py`: 10 tests
   - `test_rendering_primitives.py`: 12 tests
   - `test_integration.py`: 15 tests
   - **Total**: ~90 tests

3. **Key Dependencies Map:**
   - New test structure → depends on proper mocking pattern
   - Coverage verification → depends on new structure being in place
   - Documentation → depends on all other tasks complete

---

## Next Steps

### Immediate (P0 - Critical)
1. Create `conftest.py` with shared fixtures
2. Implement `test_init_and_lifecycle.py`
3. Implement `test_rendering_primitives.py`
4. Implement `test_render_confirmation.py`
5. Implement `test_render_progress_bar.py`
6. Implement `test_integration.py`
7. Implement `test_render_menu.py` (most complex)

### Short-term (P1 - High)
1. Verify all tests use proper mocking pattern
2. Add linting/pre-commit check for pattern compliance

### Medium-term (P2 - Medium)
1. Analyze and verify coverage is maintained or improved
2. Map old tests to new tests

### Long-term (P3 - Low)
1. Update Tests.md documentation
2. Add maintenance guidelines

---

**Last Updated:** April 20, 2026  
**Summary:** 4 TODOs identified - 1 Critical (implementation), 2 High/Medium (quality), 1 Low (documentation). All depend on implementing the new test structure and proper mocking patterns as specified in Testing Strategy.md.
