# Timeout Behavior Documentation

## Overview

The `render_menu` method in `ui_manager.py` handles user input through an input loop that waits for keyboard events using `curses.getch()`. This document describes the timeout behavior when no input is received for an extended period.

## Current Implementation

The input loop in `render_menu` (lines 452-638) uses `menu_win.getch()` to wait for user input. The curses window is initialized with `self._screen.timeout(100)` (100ms timeout) which means:

- `getch()` will return a key if one is available
- `getch()` returns `None` when the timeout expires (no input received)
- The loop continues indefinitely, waiting for input

## Timeout Behavior

### 1. Timeout Returns -1 (Cancel)
When `getch()` returns `None` (timeout), the menu returns `-1`, which is the same return value as the cancel key (q, Esc). This provides a clean way to exit the menu without selecting an option.

### 2. Menu State Reset
On timeout, the menu redraws itself with the current highlighted index, maintaining the UI state. The menu doesn't crash or enter an error state.

### 3. Timeout with Navigation
If the user navigates with arrow keys before timeout, the menu continues to respond. Timeout simply returns to the cancel behavior.

### 4. Timeout with Partial Input
If the user types a number before timeout (e.g., "3" to select option 3), that selection is processed. Timeout after that returns to cancel behavior.

### 5. Multiple Timeouts
Multiple consecutive timeouts all result in returning `-1`. The menu doesn't accumulate timeouts or behave differently after several timeouts.

### 6. Interaction with Cancel Keys
Cancel keys (q, Esc, KEY_RESIZE, KEY_BACKSPACE) still work after timeout. The menu doesn't enter a "disabled" state.

## Test Coverage

The timeout behavior is tested in `Tests/test_timeout_pytest.py`:

| Test | Description |
|------|-------------|
| `test_timeout_returns_cancel` | Timeout returns -1 when no input is received |
| `test_timeout_after_navigation` | Timeout works after arrow key navigation |
| `test_timeout_multiple_times` | Multiple timeouts all return -1 |
| `test_timeout_with_different_highlighted_states` | Timeout works regardless of highlighted index |
| `test_timeout_then_cancel` | Cancel still works after timeout |
| `test_timeout_with_default_option` | Timeout works with default option |
| `test_timeout_with_empty_options` | Timeout handles empty options |

## Running Tests

```bash
# Run pytest timeout tests
python -m pytest Tests/test_timeout_pytest.py -v

# Run all timeout tests
python -m pytest Tests/test_*.py -v -k timeout
```

## Configuration

The timeout is currently hardcoded to 100ms in `ui_manager.py` line 108:
```python
self._screen.timeout(100)  # 100ms timeout for key refresh
```

To change the timeout value, modify this line. However, this affects all input loops in the UIManager, not just `render_menu`.

## Future Enhancements

Potential improvements for timeout handling:

1. **Configurable timeout per menu**: Allow `render_menu` to accept a `timeout_ms` parameter
2. **Timeout with message**: Display a timeout message before returning
3. **Default selection on timeout**: Instead of returning -1, could select a default option
4. **Partial input handling**: Better handling of user input that gets cut off by timeout

## Example Usage

```python
# Basic menu with default timeout
ui = UIManager()
result = ui.render_menu(options)
# Returns: selected index (0-4) or -1 if cancelled/timeout

# Menu with custom timeout (requires code change)
# result = ui.render_menu(options, timeout_ms=500)  # 500ms timeout
```

## Related Code

- `render_confirmation`: Also has timeout handling (returns True on timeout)
- `print_simple_menu`: Minimal timeout handling (returns None on timeout)
- `get_input`: Has timeout using `select.select()` with 2-second timeout

## Error Handling

Timeout is not considered an error condition. The menu handles it gracefully by:
1. Returning a valid value (-1 for cancel)
2. Maintaining UI state
3. Allowing continued interaction
4. Not triggering cleanup or fallback modes

This design ensures robust behavior even when users take longer to respond or when the system is under load.
