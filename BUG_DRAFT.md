### 🟠 MEDIUM: Title and footer bars in menu windows disappear or draw incorrectly
**Status:** **OPEN**  
**Priority:** **P3** - Low; UI visual regression; menus still functional

**Description:**
When running `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama`, the title line and footer bar in numbered menu windows appear correctly for 1-2 frames, then vanish or fail to redraw. The symptoms are:
1. Title and footer bars appear briefly (within 1-2 frames) then vanish
2. Bars appear in correct color momentarily when arrow keys are pressed
3. No errors in debug output
4. Parts of previous menu borders may remain visible (ghost artifacts)
5. Issue is consistent and reproducible
6. Present from the start of the UI session

**Reproduction Steps:**
```bash
UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama 2>&1 <<< $'1\n8\n3\n'
```

**Affected Components:**
- `ui_manager.py` - `render_menu` method (lines 480-977)
- `ui_manager.py` - `render_confirmation` method (lines 983-1544)
- `ui_manager.py` - `create_window` and `redraw` functions
- Section 8.3 & 8.4 of Requirements.md (numbered menus with bordered windows)
- Section 8.6 of Requirements.md (UIManager lifecycle - curses session must remain open)

**Context:**
The bug occurs in the `render_menu` and `render_confirmation` methods of `ui_manager.py`. These methods create bordered curses windows using `win.box()` to draw the border, and call `win.box()` again in the `redraw` function to maintain the border after each update. However, the title and footer bars (content lines within the border) disappear after appearing briefly.

**Expected Behavior:**
- Title and footer bars should be visible and stable throughout menu interaction
- Each menu redraw should be clean without artifacts
- The bordered window should maintain proper content display on every frame

**Actual Behavior:**
- Title and footer bars appear briefly then vanish
- Previous menu borders may leave ghost artifacts
- No errors are logged in debug mode
- The issue is consistent and reproducible

**Key Observations:**
1. The bug manifests as visual artifacts rather than functional failures
2. No errors appear in the debug output, suggesting the issue may be timing-related or involve curses buffer corruption
3. The symptom pattern (brief appearance then disappearance) suggests the window's internal buffer may be getting corrupted or improperly refreshed
4. Arrow key navigation temporarily corrects the display, which may indicate a race condition or stale buffer issue
5. The `win.box()` calls in both `create_window` and `redraw` are present, but may not be persisting correctly

**Suggested Investigation:**
1. Add detailed logging in `redraw` to capture the exact sequence of operations (erase, addstr, refresh, box)
2. Verify that `win.box()` is being called after every content update
3. Check for potential curses buffer corruption due to overlapping window operations
4. Test with different terminal sizes to rule out width/height calculation issues
5. Examine the interaction between `erase()`, `refresh()`, and `box()` calls

**Dependencies:**
- Requirements.md Section 8.3 (Numbered menus with bordered curses windows)
- Requirements.md Section 8.4 (Confirmation prompts must never drop out of curses environment)
- Requirements.md Section 8.6 (UIManager lifecycle - curses session must remain open)

---

**Last Updated:** April 25, 2026
**Reporter:** opencode
**Verified:** Yes (reproducible with provided steps)
