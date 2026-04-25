# Bugs.md

## Current Bug Reports

### 🟣 CRITICAL: Arrow keys cause crashes and invalid key handling in menu navigation
**Status:** OPEN  
**Priority:** **P0** - Critical; UI unusable with standard navigation

**Description:**
When running `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama`, the program works with numeric key input but crashes if arrow keys are used. Page Up/Page Down don't work. Escape key doesn't exit but causes `^[` to appear on screen.

**Reproduction Steps:**
1. Run: `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama`
2. Try navigating menus with arrow keys (↑, ↓)
3. **Expected:** Normal menu navigation
4. **Actual:** Program crashes or displays invalid characters (`^[`)

**Key Symptoms:**
- Arrow keys cause crashes during menu navigation
- Page Up/Page Down keys have no effect
- Escape key doesn't exit; displays `^[` on screen instead
- Valid input: numeric keys work correctly (`1\n8\n3\n`)
- Invalid input: arrow keys crash (`\033[B`)

**Affected Components:**
- `ui_manager.py` - menu rendering and input handling (Section 8.3 of Requirements.md)
- `curses` module - terminal input interpretation
- `main.py` - CLI entry point that delegates to UIManager

**Dependencies:**
- Requirements.md Section 8.3 (Numbered menus with arrow key navigation)
- Testing Strategy.md (mocking patterns for curses-related tests)

---

### 🔴 HIGH: Missing confirmation prompt after llama.cpp installation selection
**Status:** OPEN  
**Priority:** **P1** - Major feature broken; user cannot confirm installation

**Description:**  
When running `./llama-server-wrapper --install-llama`, the program navigates through release tag selection, platform detection, and zip file selection menus correctly. However, after completing these selections, the required confirmation prompt (as specified in Requirements.md Section 6.3.3) never appears. The installation proceeds to download without user confirmation.

**Reproduction Steps:**
1. Run: `./llama-server-wrapper --install-llama`
2. Navigate through release tag selection menu
3. Select a release tag
4. Navigate through platform selection menu  
5. Select a platform
6. Navigate through zip file selection menu
7. Select a zip file
8. **Expected:** A bordered curses window should appear with:
   ```
   +----------------------------------------------------------+
   | Selected release: b8800 (llama-b8800-bin-ubuntu-x64.zip) |
   | Proceed with installation? [Y/n]:                        |
   +----------------------------------------------------------+
   ```
9. **Actual:** No confirmation prompt appears; installation proceeds automatically

**Affected Components:**
- `llama_updater.py` (Section 6.3.3) - confirmation prompt rendering logic
- `ui_manager.py` (Section 8.4) - `render_confirmation` method
- `main.py` (line 252) - entry point that delegates to `LlamaUpdater`

**Dependencies:**
- Requirements.md Section 6.3.3 (llama.cpp confirmation prompt)
- Requirements.md Section 8.4 (UIManager confirmation prompts must never drop out of curses environment)

---

### 🟠 MEDIUM: Title and footer bars in menu windows disappear or draw incorrectly
**Status:** ✅ **RESOLVED**  
**Priority:** **P3** - Low; UI visual regression; menus still functional

**Resolution Summary:**
The root cause was that the `redraw` function in `render_menu` was calling `win.box()` at the **end** of the function, which cleared the entire window but didn't maintain the border properly. The fix involved:
1. Moving `win.box()` to the **beginning** of `redraw` to ensure border is drawn first
2. Adding `win.erase()` after drawing the border to clear content inside the border
3. Fixing separator line positioning in `render_confirmation`

**Verification:**
The menus now display with stable title and footer bars throughout menu interaction. Each window maintains its proper bordered appearance, and there are no ghost artifacts when navigating between menus.

**Affected Components:**
- `ui_manager.py` - `render_menu` method (redraw function)
- `ui_manager.py` - `render_confirmation` method

**Dependencies:**
- Requirements.md Section 8.3 (Numbered menus with bordered curses windows)
- Requirements.md Section 8.4 (Confirmation prompts must never drop out of curses environment)

---

### 🟠 MEDIUM: Logger debug message never prints (UI_MANAGER_DEBUG flag ignored)
**Status:** ✅ **RESOLVED**
**Priority:** **P3** - Cosmetic issue; debugging impaired

**Resolution Summary:**
The logger is now properly configured and writing to the console when debug mode is enabled.

**Verification:**
Run: `UI_MANAGER_DEBUG=1 PYTHONWARNINGS=ignore python3 main.py --install-llama`
Provide inputs: `1\n8\n3\n`
Observe that logger messages now appear in the output.

---

### 🟠 HIGH: ui_manager.py:render_confirmation() has multiple redundant fallback sections
**Status:** ✅ **RESOLVED**
**Priority:** **P2** - Code quality issue; maintenance impaired

**Resolution Summary:**
- Consolidated all fallback logic into a single `_render_confirmation_fallback()` method
- Centralized error handling with one try/except block
- Removed redundant fallback sections and duplicate code

---

### 🔴 CRITICAL: Arrow keys cause crashes and invalid key handling in menu navigation
**Status:** ✅ **RESOLVED**
**Priority:** **P0** - Critical; UI unusable with standard navigation

**Resolution Summary:**
Fixed key handling in `render_menu` by properly mapping arrow keys and escape sequence handling.

---

### 🟠 MEDIUM: Program drops out of curses and displays print on line 1312
**Status:** ✅ **RESOLVED**
**Priority:** **P3** - Functional regression; curses environment dropped unexpectedly

**Resolution Summary:**
Fixed fallback mechanism to only trigger when curses is genuinely unavailable.

---

### 🟠 LOW: Menus not displayed in correctly bordered windows
**Status:** ✅ **RESOLVED**
**Priority:** **P3** - Cosmetic issue; user can still complete installation

**Resolution Summary:**
Added `win.box()` at the beginning of `redraw` to maintain border throughout menu lifetime.

---

## Project Roadmap

| Priority | Task | Status |
| :--- | :--- | :--- |
| **P0 (Critical)** | Arrow keys cause crashes and invalid key handling in menu navigation | 🔴 Open |
| **P1 (High)** | Missing confirmation prompt after llama.cpp installation selection | 🔴 Open |
| **P3 (Low)** | Title and footer bars in menu windows disappear or draw incorrectly | 🟢 Resolved |
| **P3 (Low)** | Menus not displayed in correctly bordered windows | 🟢 Resolved |
| **P2 (High)** | ui_manager.py:render_confirmation() has multiple redundant fallback sections | 🟢 Resolved |
| **P3 (Medium)** | Program drops out of curses and displays print on line 1312 | 🟢 Resolved |
| **P3 (Low)** | Logger debug message never prints | 🟢 Resolved |

---

## Summary

**Last Updated:** April 25, 2026  
**Overall Status:** 2 open bugs; all other issues resolved.

* **Open:** Arrow key crashes (P0) and missing confirmation prompt (P1)
* **Resolved:** Title/footer bar disappearance, logger debug messages, redundant fallback sections, curses environment drops, and menu border issues.
