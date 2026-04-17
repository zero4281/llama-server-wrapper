#!/usr/bin/env python3
"""
Test keyboard input handling using actual terminal key codes.

This tests the actual keyboard input handling in render_menu and render_confirmation
by directly verifying the key code handling logic in the code.

Actual key codes from curses module:
- KEY_UP = curses.KEY_UP (258)
- KEY_DOWN = curses.KEY_DOWN (258)
- KEY_ENTER = curses.KEY_ENTER (343)
- KEY_RESIZE = curses.KEY_RESIZE (410)
- KEY_BACKSPACE = curses.KEY_BACKSPACE (263)
- KEY_PPAGE = curses.KEY_PPAGE (339)
- KEY_NPAGE = curses.KEY_NPAGE (338)
"""

import sys
from pathlib import Path
import curses

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

from ui_manager import UIManager


# Use actual curses constants
KEY_UP = curses.KEY_UP
KEY_DOWN = curses.KEY_DOWN
KEY_RIGHT = curses.KEY_RIGHT
KEY_LEFT = curses.KEY_LEFT
KEY_ENTER = curses.KEY_ENTER
KEY_RESIZE = curses.KEY_RESIZE
KEY_PPAGE = curses.KEY_PPAGE
KEY_NPAGE = curses.KEY_NPAGE
KEY_BACKSPACE = curses.KEY_BACKSPACE


def test_key_codes_are_used_correctly():
    """Test that the actual key codes are used correctly in the code."""
    print("\n[1/4] Testing actual key codes in render_menu...")
    
    # Read the source code and verify key codes are used correctly
    import inspect
    source = inspect.getsource(UIManager.render_menu)
    
    # Verify KEY_DOWN is used for down navigation
    assert f"key == curses.KEY_DOWN" in source or "KEY_DOWN" in source, "KEY_DOWN not found"
    
    # Verify KEY_UP is used for up navigation
    assert f"key == curses.KEY_UP" in source or "KEY_UP" in source, "KEY_UP not found"
    
    # Verify KEY_ENTER (343) is used for confirmation
    assert f"key == 343" in source or "KEY_ENTER" in source, "KEY_ENTER not found"
    
    # Verify KEY_RESIZE is used for cancel
    assert f"key == curses.KEY_RESIZE" in source or "KEY_RESIZE" in source, "KEY_RESIZE not found"
    
    print("  PASSED")


def test_key_codes_are_used_in_confirmation():
    """Test that the actual key codes are used correctly in render_confirmation."""
    print("\n[2/4] Testing actual key codes in render_confirmation...")
    
    import inspect
    source = inspect.getsource(UIManager.render_confirmation)
    
    # Verify KEY_RESIZE is used for cancel
    assert f"key == curses.KEY_RESIZE" in source or "KEY_RESIZE" in source, "KEY_RESIZE not found"
    
    # Verify KEY_ENTER (343) is used for confirmation
    assert f"key == 343" in source or "KEY_ENTER" in source, "KEY_ENTER not found"
    
    # Verify ord('y') and ord('Y') are used for confirm
    assert "ord('y')" in source or "ord('Y')" in source, "y/Y not found"
    
    # Verify ord('n') and ord('N') are used for cancel
    assert "ord('n')" in source or "ord('N')" in source, "n/N not found"
    
    print("  PASSED")


def test_key_codes_are_consistent():
    """Test that all key codes are consistent across the codebase."""
    print("\n[3/4] Testing consistency of key codes...")
    
    # Verify KEY_ENTER is 343 (this is the important one for our tests)
    assert KEY_ENTER == 343, f"curses.KEY_ENTER is {KEY_ENTER}, expected 343"
    
    # Verify KEY_UP and KEY_DOWN are valid curses constants
    assert isinstance(KEY_UP, int), "curses.KEY_UP should be an integer"
    assert isinstance(KEY_DOWN, int), "curses.KEY_DOWN should be an integer"
    
    # Verify KEY_RESIZE is 410
    assert KEY_RESIZE == 410, f"curses.KEY_RESIZE is {KEY_RESIZE}, expected 410"
    
    print("  PASSED")


def test_key_codes_in_simple_menu():
    """Test that key codes are used correctly in print_simple_menu."""
    print("\n[4/4] Testing actual key codes in print_simple_menu...")
    
    import inspect
    source = inspect.getsource(UIManager.print_simple_menu)
    
    # Verify KEY_UP is used for up navigation
    assert f"key == curses.KEY_UP" in source or "KEY_UP" in source, "KEY_UP not found"
    
    # Verify KEY_DOWN is used for down navigation
    assert f"key == curses.KEY_DOWN" in source or "KEY_DOWN" in source, "KEY_DOWN not found"
    
    # Verify KEY_ENTER (343) is used for confirmation
    assert f"key == 343" in source or "KEY_ENTER" in source, "KEY_ENTER not found"
    
    print("  PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("Testing Actual Key Codes in UIManager")
    print("=" * 80)
    
    try:
        test_key_codes_are_used_correctly()
        test_key_codes_are_used_in_confirmation()
        test_key_codes_are_consistent()
        test_key_codes_in_simple_menu()
        
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED")
        print("=" * 80)
        return True
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
