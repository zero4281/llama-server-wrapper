# UIManager Tests

This folder contains unit tests for the `ui_manager.py` ncurses CLI user interface module.

## ⚠️ CRITICAL MOCKING RULE

**Any test driving `render_menu` or `render_confirmation` MUST patch `ui_manager.curses.newwin` to intercept window creation.**

```python
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

## Entry Point

The tests are orchestrated through **`__init__.py`**, which serves as the entry point. It imports and runs all test modules in the `Tests/` directory.

**Run:** `python Tests/__init__.py`

## Terminal Key Codes Reference

All tests and UIManager methods use standard `curses` key codes. Below is a complete reference:

### Arrow Keys and Navigation
| Key Code | Constant | Description | Used For |
|----------|----------|-------------|----------|
| `curses.KEY_UP` | `KEY_UP` | Move cursor up | Menu navigation, highlight selection |
| `curses.KEY_DOWN` | `KEY_DOWN` | Move cursor down | Menu navigation, highlight selection |
| `curses.KEY_LEFT` | `KEY_LEFT` | Move cursor left | Text input (not used in menus) |
| `curses.KEY_RIGHT` | `KEY_RIGHT` | Move cursor right | Text input (not used in menus) |
| `curses.KEY_PPAGE` | `KEY_PPAGE` | Page up | Jump to top of menu |
| `curses.KEY_NPAGE` | `KEY_NPAGE` | Page down | Jump to bottom of menu |

### Control Keys
| Key Code | Constant | Description | Used For |
|----------|----------|-------------|----------|
| `curses.KEY_ENTER` | `KEY_ENTER` | Enter key | Confirm selection, confirm actions |
| `curses.KEY_RESIZE` | `KEY_RESIZE` | Terminal resize | Cancel operation, reinitialize UI |
| `curses.KEY_BACKSPACE` | `KEY_BACKSPACE` | Backspace | Cancel operation |
| `curses.KEY_HOME` | `KEY_HOME` | Home key | Not used in menus |
| `curses.KEY_END` | `KEY_END` | End key | Not used in menus |

### Cancel Keys
| Key Code | Constant | ASCII Code | Description |
|----------|----------|------------|-------------|
| `curses.KEY_RESIZE` | `KEY_RESIZE` | 27 (Escape) | Cancel operation |
| `curses.KEY_BACKSPACE` | `KEY_BACKSPACE` | 127 (DEL) | Cancel operation |
| ASCII 27 | - | - | Escape key |
| ASCII 127 | - | - | DEL key |
| ASCII 8 | - | - | Backspace (alternative) |
| `ord('q')` | - | 113 | Cancel operation |

### Input Characters
| Character | ASCII Code | Description | Used For |
|-----------|------------|-------------|----------|
| `'0'` - `'9'` | 48-57 | Select option by number | Menu selection |
| `'y'` / `'Y'` | 121 | Confirm action | Confirmation dialogs |
| `'n'` / `'N'` | 110 | Cancel action | Confirmation dialogs |
| `ord('3')` | 51 | Example: Select option 3 | Menu selection |

## Test Setup Procedures

### Running Tests

#### Run All Tests
```bash
# Run all tests via entry point
python Tests/__init__.py

# Run with pytest
python3 -m pytest Tests/ -v
```

#### Run Specific Test Files
```bash
# Run API tests (unittest)
python3 Tests/test_ui_manager_api.py

# Run comprehensive tests (unittest)
python3 Tests/test_ui_manager_comprehensive.py

# Run pytest tests
python3 -m pytest Tests/test_ui_manager_pytest.py -v

# Run timeout tests
python3 -m pytest Tests/test_timeout_pytest.py -v

# Run terminal size tests
python3 -m pytest Tests/test_ui_manager_terminal_sizes.py -v
```

### Test Environment Setup

All tests use **mocked `curses` modules** to verify functionality without requiring a real TTY. This ensures:
- Tests run in CI/CD pipelines
- Tests run in any Python environment
- Tests verify correct curses API calls
- Tests verify UI logic without visual output

#### Mocking Setup Pattern

Most tests follow a consistent mocking pattern:

```python
from unittest.mock import MagicMock, patch
import curses

# 1. Create mock curses object
mock_curses = MagicMock(spec=curses)
mock_curses.initscr.return_value = MagicMock()
mock_curses.start_color = MagicMock()
mock_curses.init_pair = MagicMock(return_value=None)
mock_curses.cbreak = MagicMock(return_value=True)
mock_curses.noecho = MagicMock()
mock_curses.curs_set = MagicMock(return_value=None)
mock_curses.has_ungetch = MagicMock(return_value=False)
mock_curses.getscrptr = MagicMock(return_value=None)

# 2. Patch curses module
with patch('ui_manager.curses', mock_curses):
    ui = UIManager("Test")
    ui._using_curses = True  # Force enabled for testing
```

#### Helper Functions

The `test_ui_manager_comprehensive.py` provides a helper function:

```python
def create_ui(title="Test"):
    """Helper to create UIManager with proper mocking."""
    mock_curses = MagicMock(spec=curses)
    # ... (setup mock curses attributes)
    
    with patch('ui_manager.curses', mock_curses):
        ui = UIManager(title)
        ui._using_curses = True
    return ui
```

### Running Tests in Different Environments

#### Terminal Size Tests
Tests for terminal size adaptation require mocked screen dimensions:

```python
with patch.object(ui, '_screen') as mock_screen:
    mock_screen.getmaxyx.return_value = (20, 60)  # 20 rows, 60 columns
    # ... test code
```

#### Timeout Tests
Timeout tests verify behavior when no input is received:

```python
# Test that timeout returns -1
mock_win.getch.return_value = -1  # Timeout value
result = ui.render_menu(options)
assert result == -1
```

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

---

### `test_ui_manager_comprehensive.py`
Detailed functional tests with mocked curses environment:

**1. Initialization** (`test_init`)
- **Expected Behavior**: UIManager initializes curses screen and color pairs
- **Verification**: `_using_curses` is `True`, `_screen` is not `None`, `_color_pair` is not `None`
- **Cleanup**: `_cleanup_terminal()` restores terminal state and sets `_using_curses` to `False`

**2. Menu Navigation** (`test_menu_navigation`)
- **Expected Behavior**: 
  - Enter key (`KEY_ENTER`) selects highlighted option
  - Arrow keys (`KEY_UP`, `KEY_DOWN`, `KEY_PPAGE`, `KEY_NPAGE`) cycle through options
  - Number input (`'0'`-'`9'`) selects option directly
  - Cancel keys (`q`, `Esc`, `KEY_RESIZE`, `KEY_BACKSPACE`) return `-1`
  - Default option is displayed when `default` parameter provided
- **Verification**: Returns selected index, or `-1` on cancel

**3. Confirmation Prompts** (`test_confirmation`)
- **Expected Behavior**:
  - Enter key (`KEY_ENTER`) confirms (default yes)
  - `'n'` cancels
  - `'y'`/`'Y'` confirms
  - Escape (`Esc`) cancels
  - Timeout returns default (assumed yes)
- **Verification**: Returns `True` for confirm, `False` for cancel

**4. Progress Bars** (`test_progress`)
- **Expected Behavior**:
  - Normal progress shows filled bar with bytes and percentage
  - Spinner animation for indeterminate progress (total = 0)
- **Verification**: Creates progress window, renders bar or spinner

**5. Styling** (`test_styling`)
- **Expected Behavior**:
  - Color pair creation with green on black background
  - Reverse video (`curses.A_REVERSE`) for highlighted items
  - Bordered windows for dialogs
- **Verification**: Color pairs initialized, attributes applied correctly

**6. Edge Cases** (`test_edge_cases`)
- **Expected Behavior**:
  - Empty options list returns `-1` without error
  - Invalid input (e.g., `'9'` when only 5 options) is ignored
  - No screen (`_screen is None`) handled gracefully without crashing
- **Verification**: Returns appropriate error codes, no exceptions raised

---

### `test_ui_manager_pytest.py`
Pytest-compatible test suite for comprehensive UI testing:

| Test Function | Expected Behavior | Verification |
|---------------|-------------------|--------------|
| `test_init_fallback_on_error` | Graceful fallback when curses fails | `_using_curses` is `False`, `_screen` is `None` |
| `test_menu_navigation_arrows` | Arrow keys cycle with wrapping | Returns selected index on Enter |
| `test_menu_typing_selection` | Number input selects directly | Returns typed number as index |
| `test_menu_cancel_keys` | All cancel keys return `-1` | Each cancel key tested individually |
| `test_confirmation_enter_confirms` | Enter confirms action | Returns `True` |
| `test_confirmation_n_cancels` | `n` cancels action | Returns `False` |
| `test_confirmation_y_confirms` | `y`/`Y` confirms action | Returns `True` |
| `test_progress_bar_with_bytes` | Progress shows bytes/percent | Window created and rendered |
| `test_progress_bar_spinner` | Spinner for unknown size | Spinner animation rendered |
| `test_full_workflow_simulation` | Complete workflow end-to-end | Menu → Selection → Confirmation |

**Run:** `python3 -m pytest Tests/test_ui_manager_pytest.py -v`

---

### `test_timeout_pytest.py`
Pytest-compatible timeout tests for input loop handling:

| Test Function | Expected Behavior | Verification |
|---------------|-------------------|--------------|
| `test_timeout_returns_cancel` | Timeout returns `-1` when no input | `getch` returns timeout value |
| `test_timeout_after_navigation` | Timeout works after some navigation | Subsequent inputs still timeout |
| `test_timeout_multiple_times` | Multiple timeouts all return `-1` | Consistent behavior |
| `test_timeout_with_different_highlighted_states` | Timeout works regardless of highlighted index | State-independent |
| `test_timeout_then_cancel` | Cancel still works after timeout | Both mechanisms functional |
| `test_timeout_with_default_option` | Timeout works with default option | Default handling correct |
| `test_timeout_with_empty_options` | Timeout handles empty options | Graceful handling |

**Run:** `python3 -m pytest Tests/test_timeout_pytest.py -v`

---

### `test_ui_manager_terminal_sizes.py`
Terminal size adaptation tests:

| Test Function | Expected Behavior | Verification |
|---------------|-------------------|--------------|
| `test_small_terminal` | 40x20 terminal works | No clipping, all elements visible |
| `test_medium_terminal` | 80x24 terminal works | Standard size handling |
| `test_large_terminal` | 120x30 terminal works | Large size handling |
| `test_menu_width_small` | Menu width adapts to small terminal | Minimum 60% of screen width |
| `test_menu_width_large` | Menu width adapts to large terminal | Maximum width constraints |
| `test_progress_bar_adaptation` | Progress bar adapts to different sizes | Window dimensions appropriate |

**Run:** `python3 -m pytest Tests/test_ui_manager_terminal_sizes.py -v`

## Test Author Checklist

### ✅ Checklist for Test Authors

When writing a test that calls `render_menu` or `render_confirmation`, verify:

- [ ] I imported `patch` from `unittest.mock`
- [ ] I imported `curses` for key codes (e.g., `curses.KEY_ENTER`)
- [ ] I have a `mock_win` fixture (or created one with `MagicMock()`)
- [ ] I set up `mock_win.getch.side_effect` with expected input sequence
- [ ] I use `patch('ui_manager.curses.newwin', return_value=mock_win)` as a context manager
- [ ] The patch is applied **before** calling `render_menu()` or `render_confirmation()`
- [ ] The patch is **removed** after the test completes (context manager handles this)

### Quick Reference: Mocking Pattern

| Step | Action | Code |
|------|--------|------|
| 1 | Create mock window | `mock_win = MagicMock()` |
| 2 | Set up input | `mock_win.getch.side_effect = [curses.KEY_ENTER, 13]` |
| 3 | Patch `newwin` | `with patch('ui_manager.curses.newwin', return_value=mock_win):` |
| 4 | Call render method | `result = ui.render_menu(options)` |
| 5 | Assert result | `assert result == 0` |

### Common Mistakes to Avoid

**Mistake 1: Forgetting the patch context manager**
```python
# WRONG — patch is applied globally, not just during the test
def test_something():
    with patch('ui_manager.curses.newwin', return_value=mock_win):
        ...
    # render_menu() called outside the patch
    ui.render_menu(options)  # ❌ Unpatched!
```

**Mistake 2: Patching the wrong path**
```python
# WRONG — patching 'curses.newwin' instead of 'ui_manager.curses.newwin'
with patch('curses.newwin', return_value=mock_win):
    ...
# render_menu() uses ui_manager.curses.newwin, so this patch has no effect
```

**Mistake 3: Not importing required modules**
```python
# Must import these to access curses constants
from unittest.mock import patch
import curses
```

### When NOT to Patch `newwin`

You don't need to patch `newwin` when:
- Testing methods that don't use curses windows (e.g., `print_header`, `print_message` in fallback mode)
- Testing `UIManager.__init__` or `_cleanup_terminal` without driving render methods
- Testing pure logic that doesn't involve UI rendering

In these cases, only patch the `curses` module itself:

```python
with patch('ui_manager.curses', mock_curses):
    # Your test here
```

### Additional Resources

- See `conftest.py` for the shared `mock_win` fixture definition
- Review `test_render_menu.py` and `test_render_confirmation.py` for real-world examples
- See `TODOs.md` for the full mocking rule documentation

### Checklist for Test Authors

When writing a test that calls `render_menu` or `render_confirmation`:

1. **Create a mock window** - Use `MagicMock()` for `mock_win`
2. **Set up input** - Configure `mock_win.getch.side_effect` with expected key codes
3. **Patch `newwin`** - Use `patch('ui_manager.curses.newwin', return_value=mock_win)` in your test
4. **Verify interactions** - Assert that the correct methods were called on `mock_win`

### Examples

**Menu selection example:**
```python
def test_typing_selection_selects_option_3(ui, mock_win):
    """Verify that typing '3' selects the third option."""
    mock_win.getch.side_effect = [
        '3',  # User types '3'
        curses.KEY_ENTER  # User presses Enter to confirm
    ]
    
    with patch('ui_manager.curses.newwin', return_value=mock_win):
        result = ui.render_menu([
            {'label': 'Option 1'},
            {'label': 'Option 2'},
            {'label': 'Option 3'},
            {'label': 'Option 4'}
        ])
    
    assert result == 2  # Zero-indexed, so option 3 is index 2
    mock_win.getch.assert_called_with()
```

**Confirmation example:**
```python
def test_n_cancels_confirmation(ui, mock_win):
    """Verify that 'n' cancels the confirmation dialog."""
    mock_win.getch.side_effect = ['n']
    
    with patch('ui_manager.curses.newwin', return_value=mock_win):
        result = ui.render_confirmation(
            "Proceed with installation? [Y/n]:",
            default=False
        )
    
    assert result is False  # Cancelled
```

## Requirements Compliance

Per **Requirements.md Section 8 (CLI User Interface Module)**:

| Requirement | Test Coverage | Test Files |
|-------------|---------------|------------|
| §8.2 Black background, green text | Color pair setup | `test_ui_manager_api.py`, `test_ui_manager_comprehensive.py`
| §8.3 Numbered menus, arrow key navigation | Menu rendering/navigation | `test_menu_navigation`, `test_ui_manager_pytest.py`
| §8.4 Confirmation prompts Y/n | Confirmation dialogs | `test_confirmation`, `test_ui_manager_pytest.py`
| §8.5 Progress bar with percentage/bytes | Progress display | `test_progress`, `test_ui_manager_pytest.py`
| §8.6 Lifecycle (init/cleanup) | Initialization/cleanup | `test_init`, `test_ui_manager_comprehensive.py`
| §8.7 Timeout handling (input loop) | Timeout scenarios | `test_timeout_pytest.py`, `test_timeout_comprehensive.py`
| Highlighted items reverse video | Styling | `test_styling`, `test_ui_manager_pytest.py`

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

## Critical Mocking Pattern

### The Golden Rule

**Any test driving `render_menu` or `render_confirmation` MUST patch `ui_manager.curses.newwin` to intercept window creation.**

The `render_menu` and `render_confirmation` methods internally call `curses.newwin()` to create a new window for the dialog. Without patching this, your test's `mock_win.getch()` mock will never be called because a completely different (unmocked) window object is created.

### ❌ WRONG — mock_win.getch is never called

```python
mock_win = MagicMock()
mock_win.getch.side_effect = [curses.KEY_ENTER]
result = ui.render_menu(options)  # curses.newwin() runs unmocked internally
# Result: AttributeError or unexpected behavior because real curses.newwin() is called
```

### ✅ CORRECT — intercept newwin so the internal window IS your mock

```python
from unittest.mock import patch

def test_enter_selects_first_option(ui, mock_win):
    mock_win.getch.side_effect = [curses.KEY_ENTER]
    with patch('ui_manager.curses.newwin', return_value=mock_win):
        result = ui.render_menu([{'label': 'Option A'}, {'label': 'Option B'}])
    assert result == 0
```

### Why This Works

1. `patch('ui_manager.curses.newwin', return_value=mock_win)` replaces `curses.newwin` in the `ui_manager` module with a function that returns your mock
2. When `render_menu()` calls `curses.newwin()`, it gets your mock instead of creating a real window
3. Your test can then control the mock's behavior via `mock_win.getch.side_effect`

### Common Mistakes

**Mistake 1: Forgetting the patch context manager**
```python
# WRONG — patch is applied globally, not just during the test
def test_something():
    with patch('ui_manager.curses.newwin', return_value=mock_win):
        ...
    # render_menu() called outside the patch
    ui.render_menu(options)  # ❌ Unpatched!
```

**Mistake 2: Patching the wrong path**
```python
# WRONG — patching 'curses.newwin' instead of 'ui_manager.curses.newwin'
with patch('curses.newwin', return_value=mock_win):
    ...
# render_menu() uses ui_manager.curses.newwin, so this patch has no effect
```

**Mistake 3: Not importing the required modules**
```python
# Must import these to access curses constants
from unittest.mock import patch
import curses
```

### Checklist for Test Authors

Before committing a test that drives `render_menu` or `render_confirmation`, verify:

- [ ] I imported `patch` from `unittest.mock`
- [ ] I imported `curses` for key codes (e.g., `curses.KEY_ENTER`)
- [ ] I have a `mock_win` fixture (or created one with `MagicMock()`)
- [ ] I set up `mock_win.getch.side_effect` with expected input sequence
- [ ] I use `patch('ui_manager.curses.newwin', return_value=mock_win)` as a context manager
- [ ] The patch is applied **before** calling `render_menu()` or `render_confirmation()`
- [ ] The patch is **removed** after the test completes (context manager handles this)

### Example Test Template

```python
import pytest
from unittest.mock import MagicMock, patch
import curses


def test_something_specific(mock_curses, mock_win):
    """Your test description here."""
    # 1. Prepare your mock_win
    mock_win.getch.side_effect = [curses.KEY_ENTER, curses.KEY_RESIZE]
    
    # 2. Create UIManager instance
    with patch('ui_manager.curses', mock_curses):
        from ui_manager import UIManager
        instance = UIManager("Test")
    
    # 3. Patch newwin and run the test
    with patch('ui_manager.curses.newwin', return_value=mock_win):
        result = instance.render_menu([...])
    
    # 4. Assert the expected behavior
    assert result == 0
```

### When NOT to Patch `newwin`

You don't need to patch `newwin` when:
- Testing methods that don't use curses windows (e.g., `print_header`, `print_message` in fallback mode)
- Testing `UIManager.__init__` or `_cleanup_terminal` without driving render methods
- Testing pure logic that doesn't involve UI rendering

In these cases, only patch the `curses` module itself:

```python
with patch('ui_manager.curses', mock_curses):
    # Your test here
```

### Additional Resources

- See `conftest.py` for the shared `mock_win` fixture definition
- Review `test_render_menu.py` and `test_render_confirmation.py` for real-world examples
- See `TODOs.md` for the full mocking rule documentation

## Test Output Interpretation

### Success Indicators
- All tests pass without exceptions
- Mocked curses calls are verified (e.g., `init_pair` called with correct arguments)
- Return values match expected values (e.g., `render_menu` returns `-1` on cancel)

### Failure Indicators
- `AssertionError`: Test logic failure
- `TypeError`: Incorrect mock setup (e.g., missing attribute)
- `AttributeError`: Missing mock configuration

### Debugging Tips
1. Check mock setup: Ensure all required attributes are mocked
2. Verify return values: Mock objects should return appropriate values for curses calls
3. Use `pytest -v`: Verbose output shows which tests pass/fail
4. Add print statements: For complex mocking scenarios

(End of file - total 327 lines)
