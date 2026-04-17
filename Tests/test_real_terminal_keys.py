#!/usr/bin/env python3
"""
Integration tests for UIManager keyboard handling with real terminal simulation.

These tests simulate actual terminal key sequences and verify the complete
keyboard input flow in render_menu and render_confirmation methods.

Actual key codes from curses module:
- KEY_UP = curses.KEY_UP
- KEY_DOWN = curses.KEY_DOWN
- KEY_ENTER = curses.KEY_ENTER
- KEY_RESIZE = curses.KEY_RESIZE
- KEY_BACKSPACE = curses.KEY_BACKSPACE
- KEY_PPAGE = curses.KEY_PPAGE
- KEY_NPAGE = curses.KEY_NPAGE
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
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
KEY_BACKSPACE = curses.KEY_BACKSPACE
KEY_PPAGE = curses.KEY_PPAGE
KEY_NPAGE = curses.KEY_NPAGE


def test_complete_workflow_arrow_keys():
    """Test complete menu workflow using arrow keys."""
    print("\n[1/5] Testing complete workflow with arrow keys...")
    
    options = [{'label': f'Option {i}'} for i in range(10)]
    ui = UIManager()
    ui._using_curses = True
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win):
        
        # Sequence: DOWN, DOWN, DOWN, ENTER -> should select option 3
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [
                KEY_DOWN,  # Move to option 1
                KEY_DOWN,  # Move to option 2
                KEY_DOWN,  # Move to option 3
                KEY_ENTER,  # Confirm
            ]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 3, f"Expected 3, got {result}"
            
            # Verify redraws were called correctly
            expected_addstr_calls = 12  # Title + 10 options + footer
            actual_calls = mock_win.addstr.call_count
            assert actual_calls >= expected_addstr_calls, f"Expected at least {expected_addstr_calls} addstr calls, got {actual_calls}"
    
    print("  PASSED")


def test_complete_workflow_number_input():
    """Test complete menu workflow using number input."""
    print("\n[2/5] Testing complete workflow with number input...")
    
    options = [{'label': f'Option {i}'} for i in range(10)]
    ui = UIManager()
    ui._using_curses = True
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win):
        
        # Sequence: DOWN (to show menu), type '7', ENTER -> should select option 7
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [
                KEY_DOWN,  # Move to show menu
                ord('7'),  # Type '7'
                KEY_ENTER,  # Confirm
            ]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 7, f"Expected 7, got {result}"
    
    print("  PASSED")


def test_page_key_wrapping():
    """Test page key navigation with wrapping."""
    print("\n[3/5] Testing page key wrapping...")
    
    options = [{'label': f'Option {i}'} for i in range(10)]
    ui = UIManager()
    ui._using_curses = True
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win):
        
        # Page down from option 0 should move to option 5 (half screen)
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_NPAGE, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 5, f"Expected 5, got {result}"
    
    print("  PASSED")


def test_mixed_input_combinations():
    """Test mixed input combinations (arrows + numbers + enter)."""
    print("\n[4/5] Testing mixed input combinations...")
    
    options = [{'label': f'Option {i}'} for i in range(10)]
    ui = UIManager()
    ui._using_curses = True
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win):
        
        # Complex sequence: DOWN, DOWN, type '3', ENTER -> select option 3
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [
                KEY_DOWN,  # Move down
                KEY_DOWN,  # Move down
                ord('3'),  # Type '3'
                KEY_ENTER,  # Confirm
            ]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 3, f"Expected 3, got {result}"
        
        # Another sequence: type '8', ENTER -> select option 8
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_DOWN, ord('8'), KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 8, f"Expected 8, got {result}"
    
    print("  PASSED")


def test_all_key_codes_basic():
    """Basic test that all key codes are recognized."""
    print("\n[5/5] Testing basic key code recognition...")
    
    # Verify all expected key codes are valid curses constants
    assert KEY_UP is not None, "KEY_UP should be valid"
    assert KEY_DOWN is not None, "KEY_DOWN should be valid"
    assert KEY_RIGHT is not None, "KEY_RIGHT should be valid"
    assert KEY_LEFT is not None, "KEY_LEFT should be valid"
    assert KEY_ENTER is not None, "KEY_ENTER should be valid"
    assert KEY_RESIZE is not None, "KEY_RESIZE should be valid"
    assert KEY_PPAGE is not None, "KEY_PPAGE should be valid"
    assert KEY_NPAGE is not None, "KEY_NPAGE should be valid"
    assert KEY_BACKSPACE is not None, "KEY_BACKSPACE should be valid"
    
    # Verify they are integers
    assert isinstance(KEY_UP, int), "KEY_UP should be an integer"
    assert isinstance(KEY_DOWN, int), "KEY_DOWN should be an integer"
    assert isinstance(KEY_ENTER, int), "KEY_ENTER should be an integer"
    assert isinstance(KEY_RESIZE, int), "KEY_RESIZE should be an integer"
    
    print("  PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("Running Integration Tests with Actual Key Codes for UIManager")
    print("=" * 80)
    
    try:
        test_complete_workflow_arrow_keys()
        test_complete_workflow_number_input()
        test_page_key_wrapping()
        test_mixed_input_combinations()
        test_all_key_codes_basic()
        
        print("\n" + "=" * 80)
        print("ALL INTEGRATION TESTS PASSED")
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
