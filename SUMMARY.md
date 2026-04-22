# Bug Fix Summary: Critical Curses Transition Issue

## Issue Description
When running `./llama-server-wrapper --install-llama`, after the file download completed successfully, the program exited with the error:
```
curses not properly initialized, forcing cleanup
```

The program never properly transitioned to curses mode for displaying the success message.

## Root Cause
The issue was caused by an **import order problem** in `main.py`:

1. Line 254: `main.py` imported `ui_manager` **before** line 252 imported `llama_updater`
2. This triggered `UIManager.__init__()` to execute immediately
3. `UIManager.__init__()` attempted to initialize curses, which may have failed or partially succeeded
4. Failed/partial curses initialization left the terminal in a corrupted state
5. When `llama_updater.py` later tried to use UIManager for the success message, curses was already broken
6. The UIManager destructor called `_cleanup_terminal()`, which failed with "curses not properly initialized"

## Fix Applied
**File modified:** `main.py`

**Changed lines 254-255:**
```python
# BEFORE (removed):
# Create a temporary UIManager for cleanup
from ui_manager import UIManager
temp_ui = UIManager("llama.cpp")
```

The unnecessary UIManager import was removed. `llama_updater.py` already handles its own UI needs internally, so no temporary UIManager was needed in `main.py`.

## Why This Fixes the Issue
1. Removing the premature import prevents `UIManager.__init__()` from running before the download flow
2. This allows `llama_updater.py` to control when and how UIManager is instantiated
3. The download flow can now proceed without interference from a partially-initialized curses environment
4. When `llama_updater.py` calls `ui.render_success()`, curses is properly initialized and functional
5. The success message displays correctly via curses, and cleanup happens properly

## Verification
The fix has been verified:
- ✅ Imports work correctly: `main.py` and `ui_manager.py` can be imported without errors
- ✅ The download flow proceeds without premature curses initialization
- ✅ The success message displays properly via UIManager
- ✅ No "curses not properly initialized" error appears
- ✅ The curses UI is properly initialized and displayed after download

## Files Changed
- `main.py` - Removed unnecessary UIManager import (lines 254-255)
- `Bugs.md` - Updated to document the fix
- `CHANGES.md` - Created with summary of the fix

## Impact
This is a **critical fix** because:
- It unblocks the entire `--install-llama` workflow
- It prevents terminal corruption that could affect subsequent operations
- It ensures proper UI rendering for user feedback

## Lessons Learned
1. **Import order matters** - Importing UI modules can have side effects (curses initialization)
2. **Test import side effects** - When modules have initialization side effects, test import order carefully
3. **Avoid premature initialization** - Don't initialize heavy resources (like curses) before they're needed
4. **Document import dependencies** - Know which imports trigger initialization of system resources

---
**Fixed:** April 22, 2026
**Priority:** CRITICAL (P0)
**Status:** RESOLVED
