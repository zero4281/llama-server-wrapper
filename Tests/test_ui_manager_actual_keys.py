#!/usr/bin/env python3
"""
Comprehensive test suite for UIManager using actual curses constants.

This test file verifies that all keyboard inputs work correctly using
actual key codes from the curses module, ensuring tests match real
terminal behavior.

Run with: python3 test_ui_manager_actual_keys.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import curses

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

from ui_manager import UIManager


def create_test_ui(title="Test"):
    """Helper to create UIManager with proper mocking."""
    mock_curses = MagicMock(spec=curses)
    mock_curses.initscr.return_value = MagicMock()
    mock_curses.start_color = MagicMock()
    mock_curses.init_pair = MagicMock(return_value=None)
    mock_curses.cbreak = MagicMock(return_value=True)
    mock_curses.noecho = MagicMock()
    mock_curses.curs_set = MagicMock(return_value=None)
    mock_curses.has_ungetch = MagicMock(return_value=False)
    mock_curses.getscrptr = MagicMock(return_value=None)
    
    with patch('ui_manager.curses', mock_curses):
        ui = UIManager(title)
        ui._using_curses = True  # Force enabled for testing
    return ui


def test_arrow_key_navigation():
    """Test arrow keys navigate menu correctly."""
    print("\n[1/10] Testing arrow key navigation...")
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    ui = create_test_ui()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_ENTER = curses.KEY_ENTER
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_BACKSPACE = curses.KEY_BACKSPACE
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_UP', KEY_UP), \
         patch('curses.KEY_DOWN', KEY_DOWN), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test 1: Start at option 0, go down twice, then enter
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_DOWN, KEY_DOWN, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 2, f"Expected 2, got {result}"
        
        # Test 2: Multiple arrow key presses
        mock_getch.side_effect = [KEY_DOWN, KEY_DOWN, KEY_UP, KEY_ENTER]
        result = ui.render_menu(options, default=0, highlighted=2)
        assert result is not None, "Should return on enter"
    
    print("  PASSED")


def test_number_input_selection():
    """Test typing numbers selects the option."""
    print("\n[2/10] Testing number input selection...")
    
    options = [{'label': 'Option'}] * 10
    ui = create_test_ui()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    KEY_ENTER = curses.KEY_ENTER
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_UP', new_callable=MagicMock), \
         patch('curses.KEY_DOWN', new_callable=MagicMock), \
         patch('curses.KEY_RESIZE', new_callable=MagicMock), \
         patch('curses.KEY_PPAGE', new_callable=MagicMock), \
         patch('curses.KEY_NPAGE', new_callable=MagicMock), \
         patch('curses.KEY_BACKSPACE', new_callable=MagicMock), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        with patch.object(mock_win, 'getch') as mock_getch:
            # Test typing a single digit (e.g., "5")
            mock_getch.side_effect = [ord('5'), KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 5, f"Expected 5, got {result}"
    
    print("  PASSED")


def test_enter_key_variants():
    """Test all variants of Enter key work."""
    print("\n[3/10] Testing Enter key variants...")
    
    options = [{'label': 'Option'}] * 5
    ui = create_test_ui()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    KEY_RESIZE = curses.KEY_RESIZE
    
    # Test all Enter key variants: curses.KEY_ENTER, 10, 13
    enter_codes = [curses.KEY_ENTER, 10, 13]
    
    for enter_code in enter_codes:
        with patch.object(ui, '_screen', mock_screen), \
             patch.object(ui, 'refresh', return_value=None), \
             patch('curses.newwin', return_value=mock_win), \
             patch('curses.KEY_RESIZE', KEY_RESIZE):
            
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = enter_code
                result = ui.render_menu(options, default=0, highlighted=0)
                assert result == 0, f"Enter code {enter_code} should select option 0"
    
    print("  PASSED")


def test_page_keys_navigation():
    """Test page up/down keys navigate menu."""
    print("\n[4/10] Testing page key navigation...")
    
    options = [{'label': f'Option {i}'} for i in range(10)]
    ui = create_test_ui()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_ENTER = curses.KEY_ENTER
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_UP', KEY_UP), \
         patch('curses.KEY_DOWN', KEY_DOWN), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test page down
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_NPAGE, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result is not None, "Should return on enter"
            assert result == 5, f"Expected 5 (page down from 0), got {result}"
    
    print("  PASSED")


def test_cancel_keys():
    """Test all cancel keys work."""
    print("\n[5/10] Testing cancel keys...")
    
    options = [{'label': 'Option'}] * 5
    ui = create_test_ui()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_ENTER = curses.KEY_ENTER
    KEY_BACKSPACE = curses.KEY_BACKSPACE
    
    # All cancel keys
    cancel_keys = [
        ord('q'),  # q
        27,       # Escape
        KEY_RESIZE,  # KEY_RESIZE
        KEY_BACKSPACE,  # KEY_BACKSPACE
        127,      # DEL
        8,        # BS
    ]
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_UP', KEY_UP), \
         patch('curses.KEY_DOWN', KEY_DOWN), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_ENTER', KEY_ENTER), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE):
        
        for cancel_key in cancel_keys:
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = cancel_key
                result = ui.render_menu(options, default=0, highlighted=0)
                assert result == -1, f"Cancel key {cancel_key} should return -1"
    
    print("  PASSED")


def test_wrapping_behavior():
    """Test menu wrapping behavior."""
    print("\n[6/10] Testing wrapping behavior...")
    
    options = [{'label': f'Option {i}'} for i in range(3)]
    ui = create_test_ui()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_ENTER = curses.KEY_ENTER
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_BACKSPACE = curses.KEY_BACKSPACE
    
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
        
        # Test wrapping: start at option 0, go down 3 times (wraps to 0)
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_DOWN, KEY_DOWN, KEY_DOWN, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            # 0 -> 1 -> 2 -> 0 (wrap)
            assert result == 0, f"Expected 0 after wrapping, got {result}"
    
    print("  PASSED")


def test_empty_menu():
    """Test empty menu returns -1."""
    print("\n[7/10] Testing empty menu...")
    
    ui = create_test_ui()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
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
        
        result = ui.render_menu([], default=0, highlighted=0)
        assert result == -1, "Empty menu should return -1"
    
    print("  PASSED")


def test_default_option():
    """Test default option marking."""
    print("\n[8/10] Testing default option...")
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    ui = create_test_ui()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    KEY_ENTER = curses.KEY_ENTER
    KEY_RESIZE = curses.KEY_RESIZE
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Just hit Enter without moving - should select default (index 2)
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_ENTER
            result = ui.render_menu(options, default=2, highlighted=2)
            assert result == 2, f"Should select default option 2, got {result}"
    
    print("  PASSED")


def test_confirmation_enter():
    """Test confirmation dialog with Enter."""
    print("\n[9/10] Testing confirmation with Enter...")
    
    ui = create_test_ui()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
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
        
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_ENTER
            result = ui.render_confirmation("Are you sure?")
            assert result is True, "Enter should confirm"
    
    print("  PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("Running UIManager Tests with Actual Curses Constants")
    print("=" * 80)
    
    try:
        test_arrow_key_navigation()
        test_number_input_selection()
        test_enter_key_variants()
        test_page_keys_navigation()
        test_cancel_keys()
        test_wrapping_behavior()
        test_empty_menu()
        test_default_option()
        test_confirmation_enter()
        
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
