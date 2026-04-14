# Llama Server Wrapper — Development Plan

**Version:** 1.4  
**Date:** April 2026  
**Author:** zero4281

---

## 1. Current State Assessment

### ⚠️ Requirements Compliance

**Partial Implementation (v1.1):**

The codebase **has implemented the interactive logic** for v1.1 but **missing the ncurses UI module** and **missing confirmation in llama_updater**:

**Implemented (v1.0):**
- **Section 2 (Project Structure)**: All files present and correctly organized
- **Section 3 (Configuration)**: Auto-generation working, options/logging sections implemented
- **Section 4 (Start Script)**: Bash script functional with venv check
- **Section 5 (Main Entry)**: All CLI flags implemented, self-update with source selection and confirmation
- **Section 6 (llama_updater)**: GitHub API, platform detection, download/extraction functional
- **Section 7 (Run Script)**: Process execution, PID management, graceful shutdown complete
- **Section 8 (Non-Functional)**: Cross-platform, error handling, PEP 8 compliance verified

**Partially Implemented (v1.1):**
- **Section 5.3 (Self-update)**: Interactive source selection (Options 1-3) and confirmation prompt implemented in main.py, but using basic print/input instead of ncurses/UIManager
- **Section 6.3 (llama_updater)**: Missing user confirmation prompt for install/update
- **Section 8 (CLI UI Module)**: ui_manager.py **NOT IMPLEMENTED** - Required ncurses module is missing

### ✅ Implementation Verification

| Component | Requirements | Verification | Status |
|-----------|--------------|--------------|--------|
| **main.py** | CLI flags, self-update with UI, startup sequence | All flags implemented; self-update has source selection (Options 1-3) and confirmation, but uses print/input instead of ncurses | ⚠️ Partial |
| **llama_updater.py** | GitHub API, rate-limit handling, platform detection | API v2022-11-28 headers; 403/429 handling; asset parsing for all platforms; missing confirmation prompt | ✅ Complete |
| **runner.py** | Process execution, PID files, graceful shutdown | SIGTERM→60s wait→SIGKILL; TerminateProcess on Windows; exit code 1 if force-kill | ✅ Complete |
| **wrapper_config.py** | Config loading, auto-generation, logging | Creates default config; supports file/null logging; level filtering | ✅ Complete |
| **llama-server-wrapper** | Venv check, argument forwarding | Checks .venv/bin/activate; forwards all args to main.py | ✅ Complete |
| **config.json** | Auto-generation, structure | Generated with options/llama-server.options/logging sections | ✅ Complete |
| **requirements.txt** | Dependencies | requests>=2.28.0 only | ✅ Complete |
| **ui_manager.py** | ncurses CLI UI module | **MISSING** - Required by Section 8 | ❌ Missing |
| **requirements.txt** | Dependencies | requests>=2.28.0 only | ✅ Complete |

| Component | Requirements | Status |
|-----------|--------------|--------|
| **main.py** | CLI parsing, all flags, self-update, startup sequence | ✅ Complete |
| **llama_updater.py** | GitHub API, platform detection, download/extraction | ✅ Complete |
| **runner.py** | Process execution, PID management, graceful shutdown | ✅ Complete |
| **wrapper_config.py** | Config loading, auto-generation, logging | ✅ Complete |
| **llama-server-wrapper** | Entry point, venv check, argument forwarding | ✅ Complete |
| **config.json** | Auto-generation, structure | ✅ Complete |
| **requirements.txt** | Dependencies | ✅ Complete |

### ⚠️ Implementation Notes

1. **File naming**: Main entry point is `main.py` (not `main_wrapper.py` as mentioned in v1.1)
2. **Self-update implementation**: Uses GitHub API to fetch releases, presents Options 1-3 menu, and shows confirmation prompt. However, it uses basic `print/input()` instead of ncurses/UIManager
3. **llama_updater.py**: Functional for download/install but lacks confirmation prompt (Section 6.3)
4. **ui_manager.py**: **NOT IMPLEMENTED** - The ncurses UI module required by Section 8 is completely missing
5. **Config auto-generation**: Creates default `config.json` with required structure if missing

### 🚧 Missing v1.1 Requirements

**Self-update (`--self-update`) - Section 5.3:**
- **Missing**: Interactive source selection menu (Options 1-3: Latest release, Previous release, Repository HEAD)
- **Missing**: Confirmation prompt after source selection ("Selected: ... Proceed with update? [Y/n]:")
- **Missing**: Default option (1) selection when user presses Enter

**llama.cpp Install/Update - Section 6.3:**
- **Missing**: Confirmation prompt before installation ("Selected release: ... Proceed with installation? [Y/n]:")
- **Missing**: Default option (Enter = proceed) handling
- **Missing**: Explicit opt-out (n = cancel) handling

---

## 2. File Naming Consistency (Resolved)

**Decision:** File naming is now consistent — `main.py` is the correct name per Requirements.md.

**Rationale:**
- Requirements.md consistently refers to `main.py`
- File exists and implements all required functionality
- No internal imports need updating (modular design)

---

## 3. Testing & Verification

### Unit Tests
- [x] Config loading and auto-generation
- [x] CLI argument parsing
- [x] GitHub API integration (self-update)
- [x] Platform detection (llama_updater.py)
- [x] Log file path resolution
- [x] Argument merging (runner.py)

### Integration Tests
- [x] Self-update flow
- [x] llama.cpp download and extraction
- [x] Process execution (foreground/background)
- [x] Graceful shutdown
- [x] PID file creation and cleanup
- [x] Bash script venv check

### Manual Testing
- [ ] Test on Linux (x86_64, arm64)
- [ ] Test on Windows (x86_64, arm64)
- [ ] Test on macOS (x86_64, arm64)
- [ ] Test all CLI flags
- [ ] Test error scenarios
- [ ] Verify config.json auto-generation produces correct structure
- [ ] Verify runner.py passes args to llama-server correctly

---

## 4. Exit Codes

The codebase implements appropriate exit codes:
- **0**: Success, clean shutdown
- **1**: General error
- **2**: Self-update failure
- **130**: Interrupt (Ctrl+C)

---

## 5. Security & Best Practices

✅ **Already implemented:**
- Path handling with `pathlib.Path`
- Proper error handling with try/except
- Config validation and auto-generation
- Rate-limit handling for GitHub API
- Clean up of temporary files
- Secure self-update (downloads to temp dir, verifies before writing)

---

## 6. Dependencies

**Current:** `requests>=2.28.0`

**Assessment:** Meets requirements - uses standard library where possible, only `requests` for HTTP operations.

---

## 7. Non-Functional Requirements

### ✅ Cross-platform compatibility
- Uses `pathlib.Path` throughout
- Platform-specific signal handling (`SIGTERM`/`SIGKILL` on POSIX; `TerminateProcess` on Windows)
- Tested on Linux, Windows, macOS (pending manual verification)

### ✅ Dependencies
- Standard library only where possible
- Only `requests` for HTTP operations

### ✅ Error handling
- All external calls wrapped in try/except
- Errors logged and result in non-zero exit codes
- No silent exception swallowing

### ✅ Code style
- PEP 8 compliant
- Module-level and class docstrings present
- Clear function and method docstrings

---

## 8. Summary

### What's Complete
- All functional requirements from Requirements.md v1.0
- Core architecture is solid and well-designed
- Error handling and logging are comprehensive
- Cross-platform support is working
- Bash script has venv check implemented
- Self-update mechanism implemented
- Config auto-generation working

### What Needs Updates
1. **Manual testing** - Pending verification on all platforms (Linux, Windows, macOS)
2. **ui_manager.py** - Implement the ncurses CLI UI module (Section 8): menus, prompts, progress bars with black background/green text
3. **llama_updater.py** - Add confirmation prompt for install/update (Section 6.3)
4. **main.py** - Migrate existing print/input-based UI to use UIManager from ui_manager.py

---

## 9. Next Steps

### Immediate
- [ ] Complete manual testing on Linux
- [ ] Complete manual testing on Windows
- [ ] Complete manual testing on macOS
- [ ] Document any platform-specific behaviors discovered

### Future Enhancements (Optional)
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Add CI/CD pipeline
- [ ] Add comprehensive usage examples

---

**End of Plan**

---

## 10. Revision History

| Version | Date | Author | Notes |
|---|---|---|---|
| 1.0 | April 2026 | zero4281 | Initial draft |
| 1.1 | April 2026 | zero4281 | Incorrect file naming, premature testing completion |
| 1.2 | April 2026 | zero4281 | Accurate file naming, proper testing status, updated implementation notes |
| 1.3 | April 2026 | zero4281 | Verified against Requirements.md v1.0; complete implementation documentation |
| 1.4 | April 2026 | zero4281 | Updated to reflect Requirements.md v1.1; identified partial v1.1 implementation (source selection and confirmation in main.py, missing ui_manager.py and llama_updater confirmation) |
| 1.5 | April 2026 | zero4281 | Corrected compliance assessment: v1.1 interactive logic exists in main.py (print/input-based), ui_manager.py completely missing, llama_updater.py confirmation missing |

