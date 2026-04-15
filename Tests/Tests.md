# UIManager Tests

This folder contains unit tests for the `ui_manager.py` ncurses CLI user interface module.

## Test Files

### `test_ui_manager_api.py`
Simple API verification tests that check:
- Class structure and method existence
- Color pair setup (green on black, reverse video)
- Method signatures for key methods

**Run:** `python3 Tests/test_ui_manager_api.py`

**Coverage**:
- `UIManager` class instantiation
- `curses.init_pair` calls (color pair 1: green/black, color pair 2: white/black)
- `render_menu`, `render_confirmation`, `render_progress_bar` method signatures

### `test_ui_manager_comprehensive.py`
Detailed functional tests with mocked curses environment:

1. **Initialization** (`test_init`)
   - Verifies UIManager initializes curses screen and color pairs
   - Tests `_cleanup_terminal()` restores terminal state

2. **Menu Navigation** (`test_menu_navigation`)
   - Enter key selection
   - Arrow key cycling (UP/DOWN, PAGE UP/DOWN)
   - Number input selection (typing option numbers)
   - Cancel handling (q, Esc, KEY_RESIZE, KEY_BACKSPACE)
   - Default option display

3. **Confirmation Prompts** (`test_confirmation`)
   - Enter key confirms (default yes)
   - `n` cancels
   - `y`/`Y` confirms
   - Esc cancels

4. **Progress Bars** (`test_progress`)
   - Normal progress display with bytes and percentage
   - Spinner animation for indeterminate progress (unknown size)

5. **Styling** (`test_styling`)
   - Color pair creation (green on black)
   - Reverse video for highlighted items
   - Bordered windows

6. **Edge Cases** (`test_edge_cases`)
   - Empty options list handling
   - Invalid input handling
   - No screen handling (graceful fallback)

### `test_ui_manager_pytest.py`
Pytest-compatible test suite for comprehensive UI testing:

- `test_init_fallback_on_error`: Verifies graceful fallback when curses fails
- `test_menu_navigation_arrows`: Arrow key cycling and wrapping
- `test_menu_typing_selection`: Number input selection
- `test_menu_cancel_keys`: All cancel key variants (q, Esc, KEY_RESIZE, etc.)
- `test_confirmation_enter_confirms`: Enter confirms (default yes)
- `test_confirmation_n_cancels`: n cancels
- `test_confirmation_y_confirms`: y/Y confirms
- `test_progress_bar_with_bytes`: Progress display with bytes/percent
- `test_progress_bar_spinner`: Indeterminate progress (unknown size)
- `test_full_workflow_simulation`: Complete workflow end-to-end

**Run:** `python3 -m pytest Tests/test_ui_manager_pytest.py -v`

## Requirements Compliance

Per **Requirements.md Section 8 (CLI User Interface Module)**:

| Requirement | Test Coverage |
|-------------|---------------|
| §8.2 Black background, green text | `test_color_pair_setup` |
| §8.3 Numbered menus, arrow key navigation | `test_menu_navigation` |
| §8.4 Confirmation prompts Y/n | `test_confirmation` |
| §8.5 Progress bar with percentage/bytes | `test_progress` |
| §8.6 Lifecycle (init/cleanup) | `test_init`, `test_cleanup` |
| Highlighted items reverse video | `test_styling` |

## Running Tests

```bash
# Run API tests (unittest)
python3 Tests/test_ui_manager_api.py

# Run comprehensive tests (unittest)
python3 Tests/test_ui_manager_comprehensive.py

# Run pytest tests
python3 -m pytest Tests/test_ui_manager_pytest.py -v

# Run all tests
python3 -m pytest Tests/ -v
```

## Dependencies

- `unittest` (standard library)
- `curses` (standard library)
- `pytest>=7.0.0` (for pytest-compatible tests; listed in root `requirements.txt`)

No external dependencies required for unittest tests.

## Test Environment

All tests use mocked `curses` modules to verify functionality without requiring a real TTY. This ensures:
- Tests run in CI/CD pipelines
- Tests run in any Python environment
- Tests verify correct curses API calls
- Tests verify UI logic without visual output
