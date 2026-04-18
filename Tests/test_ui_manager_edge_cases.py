#!/usr/bin/env python3
"""
Edge case tests for UIManager using actual curses constants.

This test file covers edge cases and boundary conditions for the
UIManager keyboard input handling.

Run with: python3 test_ui_manager_edge_cases.py
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
        ui._using_curses = True
    return ui


def test_single_option():
    """Test menu with single option."""
    print("\n[1/12] Testing single option menu...")
    
    options = [{'label': 'Only Option'}]
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
        
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_ENTER
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 0, f"Single option should return 0, got {result}"
    
    print("  PASSED")


def test_large_menu():
    """Test menu with many options."""
    print("\n[2/12] Testing large menu...")
    
    options = [{'label': f'Option {i}'} for i in range(100)]
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
    
    KEY_DOWN = curses.KEY_DOWN
    KEY_UP = curses.KEY_UP
    KEY_ENTER = curses.KEY_ENTER
    KEY_RESIZE = curses.KEY_RESIZE
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_DOWN', KEY_DOWN), \
         patch('curses.KEY_UP', KEY_UP), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Navigate to last option (99)
        with patch.object(mock_win, 'getch') as mock_getch:
            # Down 99 times from 0 to reach 99
            mock_getch.side_effect = [KEY_DOWN] * 99 + [KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 99, f"Expected 99, got {result}"
    
    print("  PASSED")


def test_invalid_number_input():
    """Test invalid number input is ignored."""
    print("\n[3/12] Testing invalid number input...")
    
    options = [{'label': 'Option'}] * 5  # Only 5 options, so 9 is invalid
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
        
        # Type 9 (invalid for 5 options) then Enter - should not select
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [ord('9'), KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == -1 or result == 0, f"Invalid input should not select, got {result}"
    
    print("  PASSED")


def test_negative_number_input():
    """Test negative number input is ignored."""
    print("\n[4/12] Testing negative number input...")
    
    options = [{'label': 'Option'}] * 5  # Only 5 options, so 5 is invalid
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
        
        # Type '-' then '5' then Enter - should not select
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [ord('-'), ord('5'), KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == -1 or result == 0, f"Invalid input should not select, got {result}"
    
    print("  PASSED")


def test_special_characters():
    """Test special characters are ignored."""
    print("\n[5/12] Testing special characters...")
    
    options = [{'label': 'Option'}] * 5  # Only 5 options, so 343 is invalid
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
        
        # Type special characters then Enter - should not select
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [ord('@'), ord('#'), KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == -1 or result == 0, f"Invalid input should not select, got {result}"
    
    print("  PASSED")


def test_page_keys_large_menu():
    """Test page keys with large menu."""
    print("\n[6/12] Testing page keys with large menu...")
    
    options = [{'label': f'Option {i}'} for i in range(50)]
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
    
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_ENTER = curses.KEY_ENTER
    KEY_RESIZE = curses.KEY_RESIZE
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Page down twice from 0
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_NPAGE, KEY_NPAGE, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            # First page down: 0 -> 5, Second: 5 -> 10
            assert result == 10, f"Expected 10 after page down, got {result}"
    
    print("  PASSED")


def test_confirmation_cancel():
    """Test confirmation dialog cancellation."""
    print("\n[7/12] Testing confirmation cancellation...")
    
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
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('builtins.input', return_value='n'):  # Prevent fallback
        
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_RESIZE
            result = ui.render_confirmation("Are you sure?")
            assert result is False, "KEY_RESIZE should return False"
    
    print("  PASSED")


def test_confirmation_y_n():
    """Test confirmation with y/n input."""
    print("\n[8/12] Testing confirmation y/n...")
    
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
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE):
        
        # Test y
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = ord('y')
            result = ui.render_confirmation("Are you sure?")
            assert result is True, "y should confirm"
        
        # Test Y (uppercase)
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = ord('Y')
            result = ui.render_confirmation("Are you sure?")
            assert result is True, "Y should confirm"
        
        # Test n
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = ord('n')
            result = ui.render_confirmation("Are you sure?")
            assert result is False, "n should cancel"
    
    print("  PASSED")


def test_description_in_menu():
    """Test menu with descriptions."""
    print("\n[9/12] Testing menu with descriptions...")
    
    options = [
        {'label': 'Install', 'description': 'Install the package'},
        {'label': 'Update', 'description': 'Update to latest version'},
        {'label': 'Uninstall', 'description': 'Remove the package'},
    ]
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
        
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_ENTER
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 0, f"Should select first option with description, got {result}"
    
    print("  PASSED")


def test_no_default():
    """Test menu without default option."""
    print("\n[10/12] Testing menu without default...")
    
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
        
        # Select option 2 without default
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [ord('2'), KEY_ENTER]
            result = ui.render_menu(options, default=None, highlighted=0)
            assert result == 2, f"Should select option 2, got {result}"
    
    print("  PASSED")


def test_multiple_cancel_methods():
    """Test multiple ways to cancel."""
    print("\n[11/12] Testing multiple cancel methods...")
    
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
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_BACKSPACE = curses.KEY_BACKSPACE
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE):
        
        # Test various cancel keys
        cancel_keys = [KEY_RESIZE, KEY_PPAGE, KEY_NPAGE, KEY_BACKSPACE]
        for cancel_key in cancel_keys:
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = cancel_key
                result = ui.render_menu(options, default=0, highlighted=0)
                assert result == -1, f"Cancel key {cancel_key} should return -1"
    
    print("  PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("Running UIManager Edge Case Tests")
    print("=" * 80)
    
    try:
        test_single_option()
        test_large_menu()
        test_invalid_number_input()
        test_negative_number_input()
        test_special_characters()
        test_page_keys_large_menu()
        test_confirmation_cancel()
        test_confirmation_y_n()
        test_description_in_menu()
        test_no_default()
        test_multiple_cancel_methods()
        
        print("\n" + "=" * 80)
        print("ALL EDGE CASE TESTS PASSED")
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
