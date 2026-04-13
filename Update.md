# Gap Analysis: Requirements.md v1.2 vs Current Implementation

**Date:** April 2026  
**Status:** Incomplete - v1.2 features not yet implemented  
**Priority:** High (affects core install/update workflow)

---

## Executive Summary

The codebase successfully implements all Requirements.md v1.0 and v1.1 features, but **4 critical features** from v1.2 Section 6.5 (Download & Extraction) are missing. These features affect the security and reliability of the llama.cpp installation workflow.

### Missing Features (v1.2)

| Feature | Priority | Impact | Status |
|---------|----------|--------|--------|
| Checksum verification | High | Security risk - no verification of downloaded binaries | ❌ Missing |
| Progress bar display | Medium | UX improvement - currently silent download | ❌ Missing |
| Delete existing llama-cpp folder | High | Reliability risk - conflicts with old installations | ❌ Missing |
| Post-install sanity check | Low | Verification - missing version output | ❌ Missing |

---

## Detailed Gap Analysis

### 1. Checksum Verification (Section 6.5)

**Requirements:**
- Download checksum file (sha256sum.txt) if present in release assets
- Verify archive checksum after download
- Delete downloaded archive and print error if verification fails

**Current Implementation:**
- Downloads only the release archive
- No checksum verification performed
- Archive is cleaned up only on successful extraction

**Code Analysis:**
```python
# Current (llama_updater.py:478-484)
def install_release(release: dict, release_tag: str) -> None:
    # ... download archive ...
    download_file(selected_asset['browser_download_url'], archive_path)
    
    # ... extract to llama-cpp ...
    extract_archive(archive_path, LLAMA_CPP_DIR)
```

**Required Implementation:**
1. Search release assets for checksum files (pattern: `sha256*`, `checksum*`, `md5*`)
2. Download checksum file to temp location
3. Execute `sha256sum -c` (Unix) or equivalent to verify
4. If verification fails:
   - Delete downloaded archive
   - Print clear error message
   - Exit with non-zero status code

**Estimated Effort:** 2-3 hours

---

### 2. Progress Bar Display (Section 6.5)

**Requirements:**
- Display a progress bar or spinner during download so user can track progress

**Current Implementation:**
- Downloads silently without any progress indicator
- Only calculates `downloaded / total * 100` percentage (lines 374-375 in llama_updater.py) but doesn't display

**Code Analysis:**
```python
# Current (llama_updater.py:369-377)
def download_file(url: str, output_path: Path) -> Path:
    response = requests.get(url, stream=True, timeout=60)
    total = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total > 0:
                progress = downloaded / total * 100  # Calculated but not displayed
```

**Required Implementation:**
- Use `tqdm` library for cross-platform progress bar, or
- Implement ASCII progress bar:
  ```
  Downloading llama-b8800-bin-ubuntu-x64.zip...
  [=====>    ] 65% 15.4MB of 24.0MB
  ```

**Estimated Effort:** 1-2 hours (including optional tqdm dependency)

---

### 3. Delete Existing llama-cpp Folder (Section 6.5)

**Requirements:**
- If `./llama-cpp/` folder already exists, delete it entirely **before** extraction
- Must not prompt user
- Must not create backup
- Must handle case where folder doesn't exist (no-op)

**Current Implementation:**
- Appends files to existing `./llama-cpp/` directory
- No cleanup of old installations
- Risk: Mixing old and new binaries, potential conflicts

**Code Analysis:**
```python
# Current (llama_updater.py:483)
def install_release(release: dict, release_tag: str) -> None:
    # ... download archive ...
    
    # Current: Appends to existing directory
    extract_archive(archive_path, LLAMA_CPP_DIR)
```

**Required Implementation:**
```python
def install_release(release: dict, release_tag: str) -> None:
    # ... download archive ...
    
    # Delete existing folder if present
    if LLAMA_CPP_DIR.exists():
        shutil.rmtree(LLAMA_CPP_DIR)
        print(f"Deleted existing llama-cpp folder: {LLAMA_CPP_DIR}")
    
    # Then extract
    extract_archive(archive_path, LLAMA_CPP_DIR)
```

**Risk Assessment:** High - affects existing installations. Users with existing `llama-cpp` folders will lose their current installation when updating.

**Estimated Effort:** 30-60 minutes

---

### 4. Post-Install Sanity Check (Section 6.5)

**Requirements:**
- After successful extraction, run `llama-server --version`
- Display output to user
- If sanity check fails, print warning but exit with code 0 (binaries were installed; version check is informational)

**Current Implementation:**
- No post-install verification
- Installation completes silently after extraction

**Required Implementation:**
```python
# After extract_archive() succeeds:
try:
    result = subprocess.run(
        [str(LLAMA_CPP_DIR / "llama-server"), "--version"],
        capture_output=True,
        text=True,
        timeout=10
    )
    print(f"llama-server version: {result.stdout.strip()}")
except Exception as e:
    print(f"Warning: Could not verify llama-server version: {e}")
```

**Estimated Effort:** 30 minutes

---

## Implementation Order Recommendation

1. **Checksum Verification** (High Priority) - Critical for security
   - Most important feature for trust
   - Prevents installation of corrupted or tampered downloads

2. **Delete Existing Folder** (High Priority) - Reliability
   - Prevents conflicts from old installations
   - Required for clean update behavior

3. **Progress Bar** (Medium Priority) - UX
   - Improves user experience during downloads
   - Provides feedback during potentially long operations

4. **Sanity Check** (Low Priority) - Verification
   - Nice-to-have verification
   - Can be deferred to next sprint

---

## Testing Requirements

### Unit Tests Needed
- [ ] Checksum verification success path
- [ ] Checksum verification failure path (corrupt file)
- [ ] Checksum verification failure path (missing checksum file)
- [ ] Progress bar display (visual regression)
- [ ] Folder deletion on existing installation
- [ ] Sanity check success path
- [ ] Sanity check failure path

### Integration Tests Needed
- [ ] Full install flow with existing llama-cpp folder
- [ ] Full install flow with checksum verification
- [ ] Update flow (delete old, install new)
- [ ] Download failure scenarios

---

## Code Structure Recommendations

### New Methods to Add

**In `llama_updater.py`:**
```python
# Section: Download & Verification
class LlamaUpdater:
    def verify_checksum(self, archive_path: Path, checksum_path: Path) -> bool:
        """Verify archive against checksum file."""
        pass
    
    def download_with_progress(self, url: str, output_path: Path) -> Path:
        """Download file with progress bar."""
        pass
    
    def delete_existing_installation(self) -> None:
        """Delete existing llama-cpp folder."""
        pass
```

### Files to Modify

1. **llama_updater.py** (Primary) - Main implementation
2. **runner.py** (Optional) - May need adjustment for sanity check subprocess

---

## Risk Assessment

| Feature | Risk Level | Impact if Failed | Mitigation |
|---------|-----------|------------------|------------|
| Checksum Verification | Low | False negative (corrupted install) | Verify with known-good releases |
| Delete Existing Folder | High | Loss of current installation | Requires user acceptance; documented behavior |
| Progress Bar | None | None | Optional feature |
| Sanity Check | None | None | Warning only |

---

## Acceptance Criteria

### Checksum Verification
- [ ] Downloads sha256sum.txt if present
- [ ] Verifies archive checksum
- [ ] Fails fast if verification fails
- [ ] Handles missing checksum file gracefully (skip verification)

### Delete Existing Folder
- [ ] Removes existing llama-cpp folder if present
- [ ] No prompts or backups
- [ ] Creates new folder on extraction
- [ ] Handles permission errors gracefully

### Progress Bar
- [ ] Shows visual progress during download
- [ ] Displays percentage and remaining time (optional)
- [ ] Works on Windows, Linux, macOS

### Sanity Check
- [ ] Executes llama-server --version after install
- [ ] Displays version output
- [ ] Warns but exits successfully if check fails

---

## Related Documentation

- **Requirements.md v1.2** - Section 6.5: Download & Extraction
- **Plan.md v1.5** - Section 2: Missing v1.2 Requirements

---

**Date Created:** April 2026  
**Last Updated:** April 2026  
**Author:** zero4281

(End of file - total 128 lines)
