# TODOs.md

## Issues with `llama-server-wrapper --install-llama`

### Issue 1: Arrow Keys Cause Program Exit

**Status:** ✅ Fixed (April 17, 2026)
**Fix:** Fixed f-string formatting bug in logging at line 418 that caused exceptions
**Verified:** All key tests pass confirming arrow key (KEY_UP, KEY_DOWN) handling works correctly

### Issue 2: Number Keys Don't Highlight Selection

**Status:** ✅ Fixed (April 17, 2026)
**Fix:** Added `key is not None` check and removed dead string branch
**Verified:** All key tests pass confirming number input (0-9) handling works correctly

### Issue 3: Missing Confirmation Prompt After Zip File Selection

**Status:** ⏳ Incomplete
**Description:** After selecting a zip file, the confirmation prompt doesn't show up, program exits without downloading
**To Reproduce:**
1. Run `./llama-server-wrapper --install-llama`
2. Select a release tag and zip file
3. Observe that the confirmation prompt is skipped
**Suggested Investigation:**
- Add logging/debug output to `llama_updater.py` to verify selection flow
- Verify that `render_menu` is returning a valid selection (not -1)
- Check if the selection is being validated before calling confirmation

### Issue 4: UI Manager Not Completing Execution

**Status:** ✅ Fixed (April 17, 2026)
**Fix:** Added comprehensive logging, error handling, and terminal restoration
**Verified:** All tests pass; logging provides detailed trace information when enabled

---

## Remaining TODOs

### TODO 6: Fix Missing Confirmation Prompt Flow
- **Status:** Incomplete
- **Priority:** Medium
- **Description:** After selecting a zip file, the confirmation prompt is not displayed

### TODO 7: Add Edge Case Tests for Screen Sizes
- **Status:** Incomplete
- **Priority:** Low
- **Description:** Create tests for different terminal sizes (40x20, 80x24, 120x30)

### TODO 8: Add Timeout Tests
- **Status:** Incomplete
- **Priority:** Low
- **Description:** Create tests for timeout behavior in render_menu input loop

### TODO 10: Add Unit Tests for Individual Methods
- **Status:** Incomplete
- **Priority:** Low
- **Description:** Add unit tests for render_confirmation, render_progress_bar, etc.

### TODO 11: Improve Test Documentation
- **Status:** Incomplete
- **Priority:** Low
- **Description:** Document terminal key codes and test setup

---

**Last Updated:** April 18, 2026
**Summary:** 4 issues identified, 3 fixed, 1 incomplete. 5 TODOs remaining.
