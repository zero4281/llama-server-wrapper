#!/usr/bin/env python3
"""
Comprehensive tests for UIManager keyboard input handling.

This tests the actual keyboard input handling in render_menu and render_confirmation
with mocked curses but real input simulation.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
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
        # Force enabled for testing
        ui._using_curses = True
    return ui, mock_curses


def test_arrow_key_navigation():
    """Test arrow keys navigate menu correctly."""
    print("\n[1/5] Testing arrow key navigation...")
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    ui = UIManager()
    
    # Set up screen mocks
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    # Use actual key codes from curses module
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_ENTER = curses.KEY_ENTER  # This is 343
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test 1: Start at option 0, go down twice, then enter
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_DOWN, KEY_DOWN, KEY_ENTER]  # Enter
            result = ui.render_menu(options, default=0, highlighted=0)
            print(f"  Result: {result}")
            assert result == 2, f"Expected 2, got {result}"
            
            # Test 2: Multiple arrow key presses
            mock_getch.side_effect = [
                KEY_DOWN, KEY_DOWN, KEY_UP, KEY_ENTER
            ]
            result = ui.render_menu(options, default=0, highlighted=2)
            assert result is not None, "Should return on enter"
    
    print("  PASSED")


def test_number_input_selection():
    """Test typing numbers selects the option."""
    print("\n[2/5] Testing number input selection...")
    
    options = [{'label': 'Option'}] * 10
    ui, mock_curses = create_test_ui()
    
    # Set up screen mocks
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    KEY_ENTER = curses.KEY_ENTER  # This is 343
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.KEY_UP', new_callable=MagicMock), \
         patch('curses.KEY_DOWN', new_callable=MagicMock), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', new_callable=MagicMock), \
         patch('curses.KEY_PPAGE', new_callable=MagicMock), \
         patch('curses.KEY_NPAGE', new_callable=MagicMock), \
         patch('curses.KEY_BACKSPACE', new_callable=MagicMock), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        with patch.object(mock_win, 'getch') as mock_getch:
            # Test typing a single digit (e.g., "5")
            mock_getch.side_effect = [ord('5'), KEY_ENTER]  # Enter
            result = ui.render_menu(options, default=0, highlighted=0)
            # Should select option 5 if it exists
            print(f"  Result for typing '5': {result}")
            assert result == 5, f"Expected 5, got {result}"
    
    print("  PASSED")


def test_page_keys_navigation():
    """Test page up/down keys navigate menu."""
    print("\n[3/5] Testing page key navigation...")
    
    options = [{'label': f'Option {i}'} for i in range(10)]
    ui = UIManager()
    
    # Set up screen mocks
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    # Use actual key codes from curses module
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
        
        # Test page up/down
        with patch.object(mock_win, 'getch') as mock_getch:
            # Page down should move down 5 options (half screen)
            mock_getch.side_effect = [KEY_NPAGE, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result is not None, "Should return on enter"
            assert result == 5, f"Expected 5 (page down from 0), got {result}"
    
    print("  PASSED")


def test_confirmation_dialog():
    """Test confirmation dialog rendering."""
    print("\n[4/5] Testing confirmation dialog...")
    
    ui, mock_curses = create_test_ui()
    
    # Set up screen mocks
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
         patch('curses.KEY_RESIZE', new_callable=MagicMock), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test Enter confirms
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_ENTER
            result = ui.render_confirmation("Are you sure?")
            assert result is True, "Enter should confirm"
        
        # Test n cancels
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = ord('n')
            result = ui.render_confirmation("Are you sure?")
            assert result is False, "n should cancel"
    
    print("  PASSED")


def test_cancel_keys():
    """Test all cancel keys work."""
    print("\n[5/5] Testing cancel keys...")
    
    options = [{'label': 'Option'}] * 5
    ui, mock_curses = create_test_ui()
    
    # Set up screen mocks
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    cancel_keys = [
        ord('q'),  # q
        27,       # Escape
        410,      # KEY_RESIZE (actual value)
        256,      # KEY_BACKSPACE (actual value)
        127,      # DEL
        8,        # BS
    ]
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.KEY_UP', new_callable=MagicMock), \
         patch('curses.KEY_DOWN', new_callable=MagicMock), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_PPAGE', new_callable=MagicMock), \
         patch('curses.KEY_NPAGE', new_callable=MagicMock), \
         patch('curses.KEY_ENTER', new_callable=MagicMock):
        
        for cancel_key in cancel_keys:
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = cancel_key
                result = ui.render_menu(options, default=0, highlighted=0)
                assert result == -1, f"Cancel key {cancel_key} should return -1"
    
    print("  PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("Running Keyboard Input Tests for UIManager")
    print("=" * 80)
    
    try:
        test_arrow_key_navigation()
        test_number_input_selection()
        test_page_keys_navigation()
        test_confirmation_dialog()
        test_cancel_keys()
        
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
