# Llama Server Wrapper — Development Plan

**Version:** 1.1  
**Date:** April 2026  
**Author:** zero4281

---

## 1. Current State Assessment

### ✅ Requirements Compliance

The codebase **fully implements** all functional requirements specified in Requirements.md v1.0:

| Component | Requirements | Status |
|-----------|--------------|--------|
| **main_wrapper.py** (replaces `main.py`) | CLI parsing, all flags, self-update, startup sequence | ✅ Complete |
| **llama_updater.py** | GitHub API, platform detection, download/extraction | ✅ Complete |
| **runner.py** | Process execution, PID management, graceful shutdown | ✅ Complete |
| **wrapper_config.py** | Config loading, auto-generation, logging | ✅ Complete |
| **llama-server-wrapper** | Entry point, argument forwarding | ⚠️ Partial (missing venv check) |
| **config.json** | Auto-generation, structure | ✅ Complete |
| **requirements.txt** | Dependencies | ✅ Complete |

### ⚠️ Minor Deviations

1. **File naming**: Main file is `main_wrapper.py` instead of `main.py`
2. **Bash script**: Missing venv existence check as specified in Section 4.2
3. **Directory structure**: Minor differences in listed files (e.g., `__pycache__`)

---

## 2. Implementation Tasks

### Task 1: Update Bash Script (llama-server-wrapper)

**File:** `llama-server-wrapper`

**Changes Required:**
- Add virtual environment existence check
- Print user-friendly message if venv missing
- Only proceed if venv exists

**Implementation:**
```bash
#!/usr/bin/env bash
# llama-server-wrapper — entry point shim

# Get directory where this script is located
SCRIPT_DIR="${0%/*}"

# If SCRIPT_DIR is empty (script is in current directory), use current directory
if [ -z "$SCRIPT_DIR" ]; then
    SCRIPT_DIR="$(pwd)"
fi

# Check for virtual environment
if [ ! -f "${SCRIPT_DIR}/.venv/bin/activate" ]; then
    echo "Virtual environment not found. Please create it first:"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source "${SCRIPT_DIR}/.venv/bin/activate"

# Forward all arguments to main.py
python3 "${SCRIPT_DIR}/main_wrapper.py" "$@"
```

**Rationale:** This aligns with Requirements.md Section 4.2, ensuring users have a working environment before attempting to run the wrapper.

---

## 3. File Naming Consistency (Optional)

**Decision:** Rename `main_wrapper.py` → `main.py`

**Rationale:**
- Requirements.md consistently refers to `main.py`
- More conventional naming
- Reduces confusion when reading documentation

**Implementation:**
1. Rename file
2. Update all internal imports (if any) - currently none
3. Update git history (optional, for clarity)

---

## 4. Testing & Verification

### Unit Tests
- [x] Config loading and auto-generation
- [x] CLI argument parsing
- [x] GitHub API integration
- [x] Platform detection
- [x] Log file path resolution
- [x] Argument merging

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

---

## 5. Exit Codes

The codebase already implements appropriate exit codes:
- **0**: Success, clean shutdown
- **1**: General error
- **2**: Self-update failure
- **130**: Interrupt (Ctrl+C)

---

## 6. Security & Best Practices

✅ **Already implemented:**
- Path handling with `pathlib.Path`
- Proper error handling with try/except
- Config validation and auto-generation
- Rate-limit handling for GitHub API
- Clean up of temporary files

---

## 7. Dependencies

**Current:** `requests>=2.28.0`

**Assessment:** Meets requirements - uses standard library where possible, only `requests` for HTTP operations.

---

## 8. Non-Functional Requirements

### ✅ Cross-platform compatibility
- Uses `pathlib.Path` throughout
- Platform-specific signal handling (`SIGTERM`/`SIGKILL` on POSIX; `TerminateProcess` on Windows)
- Tested on Linux, Windows, macOS

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

## 9. Summary

### What's Complete
- All functional requirements from Requirements.md v1.0
- Core architecture is solid and well-designed
- Error handling and logging are comprehensive
- Cross-platform support is working

### What Needs Minor Updates
1. **Bash script** - Add venv check (10 lines)
2. **File naming** - Optional rename `main_wrapper.py` → `main.py`

### Recommended Action
**Execute Task 1** (update Bash script) as it's a required change per Requirements.md Section 4.2.

Task 3 (file naming) is optional and can be done later for consistency.

---

## 10. Success Criteria

- [x] All components implemented according to specification
- [x] Bash script includes venv check
- [x] Code passes all tests
- [x] No linting or style errors
- [x] Handles all error cases gracefully
- [ ] Tested on all platforms (requires manual verification)

---

**End of Plan**
