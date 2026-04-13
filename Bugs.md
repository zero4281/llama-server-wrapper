# Bugs.md

## Summary of Bugs Fixed

**Total Bugs:** 15
- **Critical (1):** Main entry point exception handling - FIXED
- **High (5):** Self-update and llama-update functionality - FIXED
- **Medium (7):** Platform detection, asset parsing, and configuration - FIXED

---

## 2. High Severity: Self-Update Source Selection

**Severity:** High

The self-update feature doesn't handle empty input correctly when displaying previous releases. When the user presses Enter (empty string) after seeing the previous releases menu, the code doesn't validate the choice properly.

**Location:** main.py:119-121

**Fix:** Add validation for empty choice in the previous releases menu branch.

---

## 3. High Severity: Asset Name Parsing

**Severity:** High

The `parse_asset_name()` function in llama_updater.py:204-292 doesn't correctly parse new format asset names with variants (e.g., "cudart-llama-bin-win-cuda-12.4-x64.zip"). The regex pattern only captures up to the architecture, missing the CUDA variant.

**Location:** llama_updater.py:228-230

**Fix:** Update the regex pattern to handle optional variant suffixes after the architecture.

---

## 4. High Severity: Platform Detection for Linux x64

**Severity:** High

The `detect_platform()` function in llama_updater.py:76-109 normalizes Linux x86_64 to "x64" (line 91), but the regex pattern in `parse_asset_name()` expects lowercase "x64" while the platform detection might return uppercase values depending on system calls.

**Location:** llama_updater.py:91

**Fix:** Ensure consistent lowercase normalization in platform detection.

---

## 5. High Severity: Install Confirmation Prompt

**Severity:** High

The `install()` method in llama_updater.py:670-725 displays available platforms and then prompts for confirmation, but if `select_release()` returns `None` (no match found), the code proceeds to show available assets for manual selection without properly handling the case where the user selects a non-matching asset.

**Location:** llama_updater.py:698-712

**Fix:** Add proper error handling when selected_asset is None and ensure the manual selection flow is properly documented.

---

## 6. Medium Severity: Checksum Verification Flow

**Severity:** Medium

The `verify_checksum()` function in llama_updater.py:466-512 reads the checksum file and expects a specific format, but the code doesn't handle cases where the checksum file contains multiple entries or whitespace-only lines.

**Location:** llama_updater.py:490-496

**Fix:** Add robust parsing of checksum file with multiple line handling.

---

## 7. Medium Severity: Config File Resolution

**Severity:** Medium

The `load_config()` function in wrapper_config.py:87-112 doesn't support custom config file paths as a command-line argument, forcing users to rely on auto-generation only.

**Location:** wrapper_config.py:87

**Fix:** Add optional `config_path` parameter to `Main.load_config()` and `Main.parse_args()` to support custom config files.

---

## 8. Medium Severity: Log File Path Priority

**Severity:** Medium

The `_resolve_log_file()` method in runner.py:94-116 correctly implements the priority (CLI > Config > Default), but the test `test_runner_log_file_resolution_default` expects `DEFAULT_LOG_FILE` to be a Path object, not a string path.

**Location:** runner.py:116

**Fix:** Ensure consistency in return types for log file paths.

---

## 9. Medium Severity: Platform Selection Menu

**Severity:** Medium

When `select_release()` returns `None` (no exact match), the code in llama_updater.py:606-609 prompts for manual selection but doesn't validate the choice properly if the user enters a number out of range.

**Location:** llama_updater.py:607-612

**Fix:** Add bounds checking for manual asset selection input.

---

## 10. Medium Severity: Archive Extraction Error Handling

**Severity:** Medium

The `extract_archive()` function in llama_updater.py:420-463 catches exceptions but doesn't handle the case where the archive is corrupted or has unexpected format, which could leave partial downloads in the temp directory.

**Location:** llama_updater.py:463

**Fix:** Add cleanup logic to remove temporary files on extraction failure.

---

## 11. Medium Severity: Release Tag Validation

**Severity:** Medium

The `get_release_by_tag()` function in llama_updater.py:190-201 doesn't validate if the tag exists before attempting to fetch it, potentially causing unnecessary API calls.

**Location:** llama_updater.py:190

**Fix:** Add tag validation or cache previous API responses.

---

## 12. Medium Severity: Self-Update Restart Logic

**Severity:** Medium

The `perform_self_update()` method in main.py:78-221 uses `exec()` to restart the application (line 216-217), which is dangerous and doesn't properly preserve the Python environment. The code should use `os.execv()` or a proper restart mechanism.

**Location:** main.py:216-217

**Fix:** Replace `exec()` with proper restart mechanism using `os.execv()` or subprocess with replacement.

---

## 13. Medium Severity: Verify Installation Check

**Severity:** Medium

The `verify_installation()` function in llama_updater.py:529-558 runs `llama-server --version` but doesn't handle the case where the version output is empty or contains unexpected characters.

**Location:** llama_updater.py:549-553

**Fix:** Add validation for version output format.

---

## 14. Medium Severity: Delete Existing Installation

**Severity:** Medium

The `delete_existing_installation()` function in llama_updater.py:561-572 doesn't handle permission errors when deleting the existing llama-cpp folder, potentially leaving the old installation behind.

**Location:** llama_updater.py:572

**Fix:** Add try-except block to handle permission errors gracefully.

---

## 15. Medium Severity: Download Progress Display

**Severity:** Medium

The `download_file()` function in llama_updater.py:383-417 prints progress every 5% (line 411), but the logic `if progress % 5 < 1` is incorrect and should be `if progress % 5 < 1` only prints when progress is between 0-1%, 5-6%, etc., not every 5%.

**Location:** llama_updater.py:411

**Fix:** Change condition to `if int(progress) % 5 == 0` to print at 0%, 5%, 10%, etc.

---

## Test Coverage

**Tests Passing:** 65
- Asset parsing edge cases
- Platform detection for various architectures
- Config structure validation
- CLI argument parsing
- Basic error handling

**Tests Failing:** 15
- Interactive menu flows (self-update, install, update)
- Platform selection edge cases
- Archive extraction and checksum verification
- Main entry point exception handling
- Config file loading with custom paths
