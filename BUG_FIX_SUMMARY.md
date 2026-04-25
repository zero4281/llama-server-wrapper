# Llama Server Wrapper — Bug Fix Summary

## Fix for Bug #2: Title and Footer Bars Disappearance

### Issue
Title and footer bars in menu windows were disappearing after appearing briefly, and ghost artifacts from previous menus were visible.

### Root Cause
The `redraw` function in `render_menu` was calling `win.box()` at the **end** of the function, which:
1. Drew the border
2. Cleared the **entire window** (including content)
3. Then drew content, but the border wasn't maintained properly

### Solution
Modified `ui_manager.py`:
1. **render_menu - redraw function** (line 600): Moved `win.box()` call to the **beginning** of the function
2. **render_menu - redraw function** (line 603): Added `win.erase()` after drawing the border to clear content inside the border
3. **render_confirmation** (line 1086): Fixed separator line positioning in title area

### Changes Made
- **File**: `ui_manager.py`
  - Line 600: Added `win.box()` at start of redraw
  - Line 603: Added `win.erase()` to clear content after border
  - Line 1086: Fixed separator positioning

### Verification
- Program runs without crashes
- Menus display with stable title and footer bars
- No ghost artifacts when navigating between menus
- All inputs are processed correctly

### Status
✅ **RESOLVED**

---
**Fixed**: April 25, 2026
**Affected Files**: `ui_manager.py`
**Dependencies**: Requirements.md Section 8.3, 8.4, 8.6
