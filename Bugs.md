# Bugs.md

## Current Bug Reports

### 🟠 MEDIUM: Missing confirmation prompt after archive selection
**Status:** 🔴 **OPEN**  
**Priority:** **P2** - Feature incomplete; UI does not work as expected when using stdin redirection

**Description:**
When running `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama <<< $'1\n8\n3\n'`, the program fails to display the confirmation prompt after the user selects a release tag, platform, and zip file. The confirmation dialog never appears, and the installation does not proceed.

**Reproduction Steps:**
1. Run: `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama <<< $'1\n8\n3\n'`
2. The program navigates through:
   - Release tag selection menu
   - Platform selection menu
   - Zip file selection menu
3. **Expected:** After selecting a zip file, a bordered curses window should appear with a confirmation prompt
4. **Actual:** The confirmation prompt never appears; the program either hangs or exits without completing the installation

**Key Symptoms:**
- Valid input sequence: `1\n8\n3\n` (release tag, platform, zip file)
- The menus display and accept input correctly
- After the final zip file selection, the confirmation prompt is missing
- The installation does not proceed to download

**Affected Components:**
- `llama_updater.py` (lines 688-694) - confirmation prompt rendering logic
- `ui_manager.py` - `render_confirmation` method (does not properly handle fallback when curses is unavailable)
- `main.py` - entry point that delegates to `LlamaUpdater`

**Dependencies:**
- Requirements.md Section 6.3.3 (llama.cpp confirmation prompt layout specification)
- Requirements.md Section 8.4 (UIManager confirmation prompts must never drop out of curses environment)
- Testing Strategy.md (mocking patterns for curses-related tests)

**Root Cause Analysis:**
The issue occurs when stdin is redirected (e.g., via `<<< $'...'`). In this case:
1. `UIManager.__init__` attempts to initialize curses but fails because stdin is not a TTY
2. The `_using_curses` flag and `_screen` attribute are not properly set
3. The code at `llama_updater.py:688-689` checks these flags and logs a warning
4. However, `render_confirmation` is still called, which fails silently when curses is unavailable
5. The fallback mechanism in `render_confirmation` does not properly handle this scenario, causing the confirmation to be skipped

**Expected Behavior (per Requirements.md 6.3.3):**
```
┌──────────────────────────────────────────────────────────┐
│ Selected release: b8800 (llama-b8800-bin-ubuntu-x64.zip) │
│ Proceed with installation?                               │
│                                                          │
│             ▶ [ Yes ]          [ No  ]                   │
└──────────────────────────────────────────────────────────┘
```

**Current Behavior:**
- The confirmation prompt is completely missing
- The installation does not proceed to download the archive

**Workaround:**
- Interactive mode with a real TTY (no stdin redirection)
- Manually trigger the confirmation by interrupting the process (not recommended)

**Estimated Fix Effort:**
- Medium - Requires extending the fallback mechanism in `render_confirmation` to properly handle cases where curses is unavailable, or implementing a custom confirmation dialog in `llama_updater.py` that renders the exact layout from Requirements.md

**Related Documentation:**
- `./Requirements.md` Section 6.3.3 - Exact layout specification with `▶ [ Yes ]  [ No ]` buttons
- `./Plan.md` Section 6.3.3 - llama.cpp confirmation prompt requirement

---

## Project Roadmap

| Priority | Task | Status |
| :--- | --- | --- |
| **P2 (Medium)** | Missing confirmation prompt after archive selection | 🔴 Open |

---

## Summary

**Last Updated:** April 26, 2026  
**Overall Status:** 1 open bug.

* **Open:** Missing confirmation prompt after archive selection (P2)
