## Summary of Changes

**File Modified:** `llama_updater.py`

**Issue:** After the file download completes, the program printed success messages using plain `print()` calls, which interfered with curses state. The UIManager destructor then ran and called `_cleanup_terminal()`, which failed with the error "curses not properly initialized, forcing cleanup" because the curses state was corrupted.

**Fix:** Replaced the plain `print()` calls with a call to `ui.render_success()`, which properly displays the success message using curses and handles cleanup correctly.

**Before:**
```python
print("\nInstallation complete!")
# Post-install sanity check
verify_installation()
# Successfully completed installation
ui_logger.info(f"Installation of {release_tag} completed successfully")
print("\n" + "="*60)
print("Installation complete! llama-cpp has been installed successfully.")
print("="*60)
```

**After:**
```python
# Use UIManager to display success message
ui.render_success(
    f"Installation of llama.cpp release {release_tag} completed successfully."
)

# Post-install sanity check
verify_installation()
```

This ensures that after the download completes, the program properly transitions to curses mode by using UIManager to display the success message. The UIManager handles the curses cleanup correctly, preventing the "curses not properly initialized" error.
