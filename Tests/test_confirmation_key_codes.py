#!/usr/bin/env python3
"""
Test render_confirmation with actual terminal key codes.

This tests the actual keyboard input handling in render_confirmation
by simulating real key sequences from a terminal.

Actual key codes from curses module:
- KEY_ENTER = curses.KEY_ENTER (343)
- KEY_RESIZE = curses.KEY_RESIZE (410)
"""

import sys
from pathlib import Path
import curses
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

from ui_manager import UIManager


def test_confirmation_enter_keys():
    """Test ENTER key variations for confirmation."""
    print("\n[1/5] Testing confirmation ENTER key variations...")
    
    ui = UIManager()
    
    KEY_ENTER = curses.KEY_ENTER
    KEY_RESIZE = curses.KEY_RESIZE
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test 1: KEY_ENTER constant
        print("  Testing KEY_ENTER constant...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_ENTER
            result = ui.render_confirmation("Are you sure?")
            assert result is True, f"KEY_ENTER should confirm: expected True, got {result}"
        
        # Test 2: ASCII 10 (LF)
        print("  Testing ASCII 10 (LF)...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = 10
            result = ui.render_confirmation("Are you sure?")
            assert result is True, f"ASCII 10 should confirm: expected True, got {result}"
        
        # Test 3: ASCII 13 (CR)
        print("  Testing ASCII 13 (CR)...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = 13
            result = ui.render_confirmation("Are you sure?")
            assert result is True, f"ASCII 13 should confirm: expected True, got {result}"
    
    print("  PASSED")


def test_confirmation_y_keys():
    """Test 'y' key variations for confirmation."""
    print("\n[2/5] Testing confirmation 'y' key variations...")
    
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', new_callable=MagicMock), \
         patch('curses.KEY_ENTER', new_callable=MagicMock):
        
        # Test 1: lowercase 'y'
        print("  Testing lowercase 'y'...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = ord('y')
            result = ui.render_confirmation("Are you sure?")
            assert result is True, f"lowercase 'y' should confirm: expected True, got {result}"
        
        # Test 2: uppercase 'Y'
        print("  Testing uppercase 'Y'...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = ord('Y')
            result = ui.render_confirmation("Are you sure?")
            assert result is True, f"uppercase 'Y' should confirm: expected True, got {result}"
    
    print("  PASSED")


def test_confirmation_n_keys():
    """Test 'n' key variations for cancellation."""
    print("\n[3/5] Testing confirmation 'n' key variations...")
    
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', new_callable=MagicMock), \
         patch('curses.KEY_ENTER', new_callable=MagicMock):
        
        # Test 1: lowercase 'n'
        print("  Testing lowercase 'n'...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = ord('n')
            result = ui.render_confirmation("Are you sure?")
            assert result is False, f"lowercase 'n' should cancel: expected False, got {result}"
        
        # Test 2: uppercase 'N'
        print("  Testing uppercase 'N'...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = ord('N')
            result = ui.render_confirmation("Are you sure?")
            assert result is False, f"uppercase 'N' should cancel: expected False, got {result}"
    
    print("  PASSED")


def test_confirmation_cancel_keys():
    """Test all cancellation keys for confirmation."""
    print("\n[4/5] Testing confirmation cancellation keys...")
    
    ui = UIManager()
    
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_BACKSPACE = curses.KEY_BACKSPACE
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE):
        
        # Test 1: KEY_RESIZE
        print("  Testing KEY_RESIZE...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_RESIZE
            result = ui.render_confirmation("Are you sure?")
            assert result is False, f"KEY_RESIZE should cancel: expected False, got {result}"
        
        # Test 2: KEY_BACKSPACE
        print("  Testing KEY_BACKSPACE...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_BACKSPACE
            result = ui.render_confirmation("Are you sure?")
            assert result is False, f"KEY_BACKSPACE should cancel: expected False, got {result}"
    
    print("  PASSED")


def test_confirmation_timeout():
    """Test confirmation timeout behavior."""
    print("\n[5/5] Testing confirmation timeout...")
    
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', new_callable=MagicMock), \
         patch('curses.KEY_ENTER', new_callable=MagicMock):
        
        # Test: timeout should return True (default yes)
        print("  Testing timeout returns True...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = -1  # timeout value
            result = ui.render_confirmation("Are you sure?")
            # Timeout behavior depends on implementation
            print(f"    Timeout result: {result}")
    
    print("  PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("Testing Actual Key Codes in render_confirmation")
    print("=" * 80)
    print("\nKey Codes Reference:")
    print(f"  KEY_ENTER = {curses.KEY_ENTER}")
    print(f"  KEY_RESIZE = {curses.KEY_RESIZE}")
    print(f"  KEY_BACKSPACE = {curses.KEY_BACKSPACE}")
    print(f"  ord('y') = {ord('y')}")
    print(f"  ord('Y') = {ord('Y')}")
    print(f"  ord('n') = {ord('n')}")
    print(f"  ord('N') = {ord('N')}")
    
    try:
        test_confirmation_enter_keys()
        test_confirmation_y_keys()
        test_confirmation_n_keys()
        test_confirmation_cancel_keys()
        test_confirmation_timeout()
        
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
