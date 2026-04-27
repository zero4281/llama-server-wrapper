# Plan to Fix Yes/No Menu in render_confirmation()

## Summary
The user wants to modify the Yes/No menu in `render_confirmation()` to put the Yes/No options on one line instead of two lines, while keeping the navigation logic.

## Current Issue
The Yes/No options are rendered on two separate lines:
```
  [ Yes ]
  [ No  ]
```

## Desired Layout
Yes/No options should be on one line:
```
  [ Yes ]  [ No  ]
```

## Implementation Steps

1. **Read current code** - Already done
2. **Modify redraw function** - Change Yes/No rendering to use one line
3. **Adjust positioning** - Calculate button positions for single-line layout
4. **Test** - Verify alignment and functionality

## Changes Required

### Current (two lines):
```python
button_x = 2 + (msg_width - button_width) // 2
prompt_win.addstr(3, button_x, f"  [ Yes ]")
prompt_win.addstr(4, button_x, f"  [ No  ]")
```

### New (one line):
```python
# Calculate positions for two buttons on one line
button_width = 10  # width of "  [ Yes ]" including spaces
button_spacing = 4  # space between buttons

# Center the pair of buttons
pair_width = button_width * 2 + button_spacing
button_start_x = 2 + (msg_width - pair_width) // 2

# Render both buttons on row 3
prompt_win.addstr(3, button_start_x, f"  [ Yes ]  [ No  ]")
```

## Verification
- Test with various message widths
- Ensure buttons are centered
- Verify both buttons fit within the window
- Test arrow key navigation still works
- Test direct input (y, n, enter, esc) still works

## Expected Outcome
After fixing, the confirmation dialog should display:
```
┌─────────────────────────────────────────────────────┐
│ Selected: v1.2.0 (llama-server-wrapper-v1.2.0.zip) │
│ Proceed? [Y/n]:                                   │
│                                                     │
│           [ Yes ]  [ No  ]                        │
└─────────────────────────────────────────────────────┘
```

## Files to Modify
- `ui_manager.py`: Update `render_confirmation()` redraw function (around line 1138)