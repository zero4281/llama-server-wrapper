# UIManager Testing Strategy

**Project:** llama-server-wrapper  
**Module under test:** `ui_manager.py` (1,623 lines, 10 public methods)  
**Date:** April 2026

---

## The Problem

The current test suite has grown organically into 23 files and 223 test functions. The core issues are:

**Flakiness from broken mocking.** The biggest structural problem: ~8 test files try to mock `curses` at the wrong level. `render_menu()` and `render_confirmation()` both call `curses.newwin()` internally to create their own window object. Tests that mock `mock_win.getch()` on a separately-created mock object never actually intercept those calls — the real `curses.newwin()` runs and returns an unmocked object, causing tests to behave non-deterministically depending on whether a TTY is available. This is documented in `Tests/Test Bugs.md` and is the root cause of most flakiness.

**Massive duplication.** At least 15 distinct test names appear in multiple files (e.g., `test_arrow_key_navigation`, `test_cancel_keys`, `test_confirmation_dialog`). The same behavior is tested 3–5 times across files like `test_keyboard_input.py`, `test_arrow_keys_comprehensive.py`, `test_real_terminal_keys.py`, and `test_ui_manager_comprehensive.py`.

**No clear ownership.** 23 files with no consistent convention makes it impossible to answer "where do I add a test for X?" or "which file covers Y?"

---

## The Fix: A Clean Rewrite

Delete the existing 23 test files and replace them with **6 focused files** organized by what they test, not by who wrote them. All tests use **pytest** with a shared `conftest.py` fixture — no more copy-pasted mock setup in every file.

---

## Target File Structure

```
Tests/
├── conftest.py                      # Shared fixtures — UIManager mock setup lives here only
├── test_init_and_lifecycle.py       # UIManager.__init__, _cleanup_terminal
├── test_render_menu.py              # render_menu: navigation, selection, cancel, edge cases
├── test_render_confirmation.py      # render_confirmation: Y/n/Enter/Esc/timeout
├── test_render_progress_bar.py      # render_progress_bar: normal, spinner, adaptation
├── test_rendering_primitives.py     # print_header, print_message, render_success, render_error
└── test_integration.py              # End-to-end flows: tag select → asset select → confirm
```

---

## The Core Fixture (conftest.py)

Every test file used to copy-paste 10–15 lines of mock setup. Put it here once:

```python
# Tests/conftest.py
import curses
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_curses():
    """A fully mocked curses module — safe to use without a TTY."""
    m = MagicMock(spec=curses)
    m.initscr.return_value = MagicMock()
    m.start_color = MagicMock()
    m.init_pair = MagicMock(return_value=None)
    m.cbreak = MagicMock(return_value=True)
    m.noecho = MagicMock()
    m.curs_set = MagicMock(return_value=None)
    m.KEY_UP    = curses.KEY_UP
    m.KEY_DOWN  = curses.KEY_DOWN
    m.KEY_ENTER = curses.KEY_ENTER
    m.KEY_RESIZE = curses.KEY_RESIZE
    m.KEY_BACKSPACE = curses.KEY_BACKSPACE
    m.KEY_PPAGE = curses.KEY_PPAGE
    m.KEY_NPAGE = curses.KEY_NPAGE
    m.A_REVERSE = curses.A_REVERSE
    m.color_pair = MagicMock(return_value=0)
    return m

@pytest.fixture
def ui(mock_curses):
    """A UIManager instance with curses fully mocked, _using_curses=True."""
    with patch('ui_manager.curses', mock_curses):
        from ui_manager import UIManager
        instance = UIManager("Test")
        instance._using_curses = True
    return instance

@pytest.fixture
def mock_win():
    """A mock curses window with sensible defaults."""
    win = MagicMock()
    win.getmaxyx.return_value = (24, 80)
    win.getyx.return_value = (0, 0)
    return win
```

---

## The Critical Mocking Rule

This is what was causing all the flakiness. **Always mock `newwin` to return your mock window:**

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

Every test that drives `render_menu` or `render_confirmation` must use `patch('ui_manager.curses.newwin', return_value=mock_win)`.

---

## What Each File Should Cover

### `test_init_and_lifecycle.py`
- `UIManager` initializes with `_using_curses = True` when curses succeeds
- Falls back to `_using_curses = False` when curses raises an exception  
- `_cleanup_terminal()` sets `_using_curses = False` and restores terminal state
- Color pairs are initialized: pair 1 = green/black, pair 2 = reverse video

### `test_render_menu.py`
The most complex method. Organize by input type:

| Group | Tests |
|-------|-------|
| Arrow navigation | `KEY_UP`/`KEY_DOWN` wrap around, `KEY_PPAGE`/`KEY_NPAGE` jump to top/bottom |
| Number input | Single digit selects directly; out-of-range digit is ignored |
| Enter to confirm | `KEY_ENTER`, `ord('\n')`, `ord('\r')` all confirm |
| Cancel keys | `KEY_RESIZE`, `KEY_BACKSPACE`, `ord('q')`, `ord('Q')`, ASCII 27 (Esc), ASCII 127 all return `-1` |
| Edge cases | Empty options list returns `-1`; single option; default option displayed |
| Terminal sizing | Small (40×20), standard (80×24), large (120×30) all work without crashing |

### `test_render_confirmation.py`

| Group | Tests |
|-------|-------|
| Confirm inputs | `KEY_ENTER`, `ord('y')`, `ord('Y')`, `ord('\n')` return `True` |
| Cancel inputs | `ord('n')`, `ord('N')`, ASCII 27 (Esc), `KEY_RESIZE` return `False` |
| Timeout | `getch` returning `-1` returns the `default` parameter value |
| Default parameter | `default=True` and `default=False` both respected |

### `test_render_progress_bar.py`

| Group | Tests |
|-------|-------|
| Determinate progress | 0%, 50%, 100% — bar fills correctly, bytes and percent shown |
| Indeterminate (total=0) | Spinner animation renders without crashing |
| Terminal adaptation | Window dimensions fit within available screen space |

### `test_rendering_primitives.py`
These are the easy tests — no input loops, no `newwin`. Just verify the methods call the right curses APIs:
- `print_header` calls `addstr` and `refresh`
- `print_message` places text at the correct coordinates
- `render_success` and `render_error` display without crashing
- All methods degrade gracefully when `_using_curses = False` (fallback mode)

### `test_integration.py`
Tests that cross method boundaries. Each test drives a realistic flow:
- Tag selection → asset selection → confirmation dialog (full happy path)
- Cancel at tag selection → rest of flow never runs
- Cancel at asset selection
- Timeout at confirmation → proceeds with default (True)

These tests use the `MockCurses` class pattern already established in `test_full_install_flow_integration.py` — that file has good integration test bones; keep the structure, delete the duplication.

---

## Mapping: Old Files → New Files

| Old file(s) | Replaced by |
|-------------|-------------|
| `test_ui_manager_api.py` | `test_init_and_lifecycle.py` |
| `test_ui_manager_comprehensive.py`, `test_ui_manager_pytest.py` | `test_render_menu.py`, `test_render_confirmation.py` |
| `test_keyboard_input.py`, `test_arrow_keys_comprehensive.py`, `test_real_terminal_keys.py`, `test_ui_manager_actual_keys.py`, `test_actual_key_codes.py`, `test_ui_rendering_key_codes.py` | `test_render_menu.py` (navigation section) |
| `test_confirmation_key_codes.py`, `test_render_confirmation.py` | `test_render_confirmation.py` |
| `test_render_progress_bar.py` | `test_render_progress_bar.py` |
| `test_render_basic.py` | `test_rendering_primitives.py` |
| `test_timeout_comprehensive.py`, `test_timeout_pytest.py` | Timeout sections in `test_render_menu.py` and `test_render_confirmation.py` |
| `test_ui_manager_terminal_sizes.py` | Terminal sizing section in `test_render_menu.py` |
| `test_ui_manager_edge_cases.py` | Edge case sections across relevant files |
| `test_ui_manager_validation.py` | `test_render_menu.py` (validation group) |
| `test_number_input_comprehensive.py` | `test_render_menu.py` (number input group) |
| `test_menu_input.py` | `test_render_menu.py` |
| `test_edge_cases.py` | `test_init_and_lifecycle.py` + `test_render_menu.py` |
| `test_full_install_flow_integration.py`, `test_llama_updater_integration.py` | `test_integration.py` |

---

## Target Test Count

| File | Approx. tests |
|------|--------------|
| `test_init_and_lifecycle.py` | 8 |
| `test_render_menu.py` | 30 |
| `test_render_confirmation.py` | 15 |
| `test_render_progress_bar.py` | 10 |
| `test_rendering_primitives.py` | 12 |
| `test_integration.py` | 15 |
| **Total** | **~90** |

90 focused tests replace 223 scattered ones. Coverage should be equal or better — the old suite had large swaths of duplication masking gaps, not filling them.

---

## Running Tests

```bash
# All tests
python3 -m pytest Tests/ -v

# One file
python3 -m pytest Tests/test_render_menu.py -v

# One test by name
python3 -m pytest Tests/test_render_menu.py::test_cancel_keys -v

# Stop on first failure
python3 -m pytest Tests/ -x

# Show which tests were collected (dry run)
python3 -m pytest Tests/ --collect-only
```

---

## Rules for Maintaining Tests Going Forward

**1. One file per module method group.** New behavior in `render_menu`? Add a test to `test_render_menu.py`. Don't create a new file.

**2. New fixtures belong in `conftest.py`.** If you find yourself writing mock setup inside a test, stop and add a fixture instead.

**3. Always mock `newwin`.** Any test driving `render_menu` or `render_confirmation` must include `patch('ui_manager.curses.newwin', return_value=mock_win)`. This is the rule that prevents flakiness.

**4. No tests that inspect source code.** Several old tests used `inspect.getsource()` to check whether a key constant appeared in the source text. These are fragile and circular — delete them. Test behavior, not implementation.

**5. Integration tests are for cross-method flows only.** If a test only exercises one public method, it goes in that method's unit test file.

**6. Document known-failing tests with `@pytest.mark.xfail`.** If a test exposes a real known bug, mark it rather than deleting it or commenting it out.

---

## Rewrite Sequence

Do this in order to avoid breaking things mid-rewrite:

1. Write `conftest.py` with the core fixtures
2. Rewrite `test_init_and_lifecycle.py` — easiest, no input loop mocking
3. Rewrite `test_rendering_primitives.py` — also no input loops
4. Rewrite `test_render_confirmation.py` — smaller than menu
5. Rewrite `test_render_menu.py` — most complex, do this after the mocking pattern is proven
6. Rewrite `test_render_progress_bar.py`
7. Rewrite `test_integration.py` — port the best tests from the two integration files
8. Run `pytest Tests/ -v` and confirm all pass
9. Delete the old files
