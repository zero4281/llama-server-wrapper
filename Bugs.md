# Bugs.md

## Current Bug Reports

### 🔴 CRITICAL: Confirmation prompt missing or not displaying correctly after archive selection
**Status:** 🔴 **OPEN**  
**Priority:** **P1** - Major feature broken; user cannot confirm installation

**Description:**  
When running `./llama-server-wrapper --install-llama`, after selecting a release tag, platform, and zip file, the required confirmation prompt (as specified in Requirements.md Section 6.3.3) either never appears or fails to display properly. The user reports that after hitting enter on the archive selection, no confirmation prompt is shown, yet the file downloads automatically.

**Reproduction Steps:**
1. Run: `./llama-server-wrapper --install-llama`
2. Navigate through release tag selection menu and select an option
3. Navigate through platform selection menu and select an option
4. Navigate through zip file selection menu and select an option
5. Hit enter on the archive selection
6. **Expected:** A bordered curses window should appear with:
    ```
    +----------------------------------------------------------+
    | Selected release: vX.Y.Z (filename.zip)                   |
    | Proceed with installation? [Y/n]:                         |
    +----------------------------------------------------------+
    ```
7. **Actual:** No confirmation prompt appears; installation proceeds automatically

**Key Symptoms:**
- Confirmation prompt appears to be missing after archive selection
- Prompt fails to display when it should appear
- Installation proceeds to download without user confirmation
- Archive selection archive selection works (file downloads when enter is pressed)

**Affected Components:**
- `llama_updater.py` (Section 6.3.3) - confirmation prompt rendering logic
- `ui_manager.py` (Section 8.4) - `render_confirmation` method
- `main.py` - entry point that delegates to `LlamaUpdater`

**Dependencies:**
- Requirements.md Section 6.3.3 (After a release tag and asset are selected, UIManager must render a bordered curses window displaying both selections and prompt for confirmation before downloading anything)
- Requirements.md Section 8.4 (UIManager confirmation prompts must never drop out of curses environment)


## Project Roadmap

| Priority | Task | Status |
| :--- | :--- | :--- |
| **P0 (Critical)** | Arrow keys cause crashes and invalid key handling in menu navigation | 🟢 Resolved |
| **P1 (High)** | Missing confirmation prompt after llama.cpp installation selection | 🟢 Resolved |
| **P1 (High)** | Confirmation prompt missing or not displaying correctly after archive selection | 🔴 Open |
| **P2 (Medium)** | Confirmation prompt in llama_updater.py doesn't match Requirements.md border styling specification | 🟢 Resolved |
| **P2 (Medium)** | Confirmation prompt in llama_updater.py uses render_confirmation() but Requirements.md Section 6.3.3 specifies a different layout | 🟢 Resolved |
| **P3 (Low)** | Title and footer bars in menu windows disappear or draw incorrectly | 🟢 Resolved |
| **P3 (Low)** | Menus not displayed in correctly bordered windows | 🟢 Resolved |
| **P2 (High)** | ui_manager.py:render_confirmation() has multiple redundant fallback sections | 🟢 Resolved |
| **P3 (Medium)** | Program drops out of curses and displays print on line 1312 | 🟢 Resolved |
| **P3 (Low)** | Logger debug message never prints | 🟢 Resolved |


## Summary

**Last Updated:** April 26, 2026  
**Overall Status:** 1 open bug.

* **Open:** Confirmation prompt missing/not displaying (P1)
* **Resolved:** Arrow key crashes (P0), missing confirmation prompt (P1), title/footer bar disappearance, logger debug messages, redundant fallback sections, curses environment drops, menu border issues, confirmation prompt layout (P2).
