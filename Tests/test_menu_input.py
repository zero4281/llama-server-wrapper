#!/usr/bin/env python3
"""
Test keyboard input handling in UIManager
"""

import sys
from pathlib import Path
import curses
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path.cwd()))

from ui_manager import UIManager


def test_menu_with_arrow_keys():
    """Test arrow key navigation in menu."""
    print("[1/3] Testing arrow keys...")
    
    # Create UIManager without mocking curses
    ui = UIManager()
    
    # Set up screen mock
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    
    # Mock window
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    # Use actual key codes directly
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_ENTER = curses.KEY_ENTER
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_BACKSPACE = curses.KEY_BACKSPACE
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    
    # Don't mock curses module - just mock the specific functions
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_UP', KEY_UP), \
         patch('curses.KEY_DOWN', KEY_DOWN), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test: Start at option 0, go down twice, then enter
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_DOWN, KEY_DOWN, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            print(f"  Result: {result}")
            assert result == 2, f"Expected 2, got {result}"
    
    print("  PASSED")


def test_menu_with_number_input():
    """Test typing numbers to select option."""
    print("[2/3] Testing number input...")
    
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    # Use actual key codes directly
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_ENTER = curses.KEY_ENTER
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_BACKSPACE = curses.KEY_BACKSPACE
    
    options = [{'label': 'Option'}] * 10
    
    # Don't mock curses module - just mock the specific functions
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_UP', KEY_UP), \
         patch('curses.KEY_DOWN', KEY_DOWN), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test: Type '3' then enter
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [ord('3'), KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            print(f"  Result: {result}")
            assert result == 3, f"Expected 3, got {result}"
    
    print("  PASSED")


def test_confirmation_dialog():
    """Test confirmation dialog."""
    print("[3/3] Testing confirmation...")
    
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_ENTER = curses.KEY_ENTER
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test: Enter confirms
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_ENTER
            result = ui.render_confirmation("Are you sure?")
            assert result is True, "Enter should confirm"
        
        # Test: n cancels
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = ord('n')
            result = ui.render_confirmation("Are you sure?")
            assert result is False, "n should cancel"
    
    print("  PASSED")


if __name__ == '__main__':
    print("="*60)
    print("Testing UIManager Keyboard Input")
    print("="*60)
    
    try:
        test_menu_with_arrow_keys()
        test_menu_with_number_input()
        test_confirmation_dialog()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED")
        print("="*60)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
