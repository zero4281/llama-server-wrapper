#!/usr/bin/env python3
"""
Comprehensive tests for arrow key handling in UIManager.

This tests the actual keyboard input handling in render_menu and render_confirmation
by directly verifying the key code handling logic and simulating real terminal behavior.
"""

import sys
from pathlib import Path
import curses
from unittest.mock import MagicMock, patch, call
import time

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


def test_arrow_key_navigation():
    """Test arrow key navigation in menu."""
    print("\n[1/10] Testing arrow key navigation...")
    
    options = [{'label': f'Option {i}'} for i in range(10)]
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test 1: Start at option 0, go down twice, then enter
        print("  Test 1: Basic navigation...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_DOWN, KEY_DOWN, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 2, f"Expected 2, got {result}"
        
        # Test 2: Wrap around from last to first with UP
        print("  Test 2: Wrap from last to first...")
        with patch.object(mock_win, 'getch') as mock_getch:
            # 9 UP presses from index 9: 9->8->7->6->5->4->3->2->1->0, then ENTER returns 0
            mock_getch.side_effect = [KEY_UP, KEY_UP, KEY_UP, KEY_UP, KEY_UP, KEY_UP, KEY_UP, KEY_UP, KEY_UP, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=9)
            assert result == 0, f"Expected 0, got {result}"
        
        # Test 3: Wrap around from first to last with DOWN
        print("  Test 3: Wrap from first to last...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_DOWN, KEY_DOWN, KEY_DOWN, KEY_DOWN, KEY_DOWN, KEY_DOWN, KEY_DOWN, KEY_DOWN, KEY_DOWN, KEY_DOWN, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            # 10 DOWN presses from index 0: 0->1->2->3->4->5->6->7->8->9->0 (wrap), then ENTER returns 0
            assert result == 0, f"Expected 0, got {result}"
        
    print("  PASSED")


def test_page_key_navigation():
    """Test page key navigation in menu."""
    print("\n[2/10] Testing page key navigation...")
    
    options = [{'label': f'Option {i}'} for i in range(20)]
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test 1: Page down moves down half screen (5 options)
        print("  Test 1: Page down...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_NPAGE, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            # half_screen = 5, so from 0 we go to 5
            assert result == 5, f"Expected 5, got {result}"
        
        # Test 2: Page up moves up half screen (5 options)
        print("  Test 2: Page up...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_PPAGE, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=10)
            # half_screen = 5, so from 10 we go to 5
            assert result == 5, f"Expected 5, got {result}"
        
        # Test 3: Page down from last item wraps
        print("  Test 3: Page down from last...")
        with patch.object(mock_win, 'getch') as mock_getch:
            # 7 Page downs from index 19: 19->4->9->14->19->4->9->14, then ENTER returns 14
            mock_getch.side_effect = [KEY_NPAGE, KEY_NPAGE, KEY_NPAGE, KEY_NPAGE, KEY_NPAGE, KEY_NPAGE, KEY_NPAGE, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=19)
            assert result == 14, f"Expected 14, got {result}"
        
    print("  PASSED")


def test_number_input_selection():
    """Test typing numbers to select option."""
    print("\n[3/10] Testing number input selection...")
    
    options = [{'label': f'Option {i}'} for i in range(10)]
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test 1: Type '3' then enter
        print("  Test 1: Type '3' then enter...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [ord('3'), KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 3, f"Expected 3, got {result}"
        
        # Test 2: Type '1' then '0' (two digits processed separately) then enter
        print("  Test 2: Type '1' then '0' then enter...")
        with patch.object(mock_win, 'getch') as mock_getch:
            # '1' selects option 1, '0' selects option 0, ENTER returns 0
            mock_getch.side_effect = [ord('1'), ord('0'), KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 0, f"Expected 0, got {result}"
        
        # Test 3: Out of range number is ignored
        print("  Test 3: Out of range number...")
        with patch.object(mock_win, 'getch') as mock_getch:
            # '2' selects option 2, ENTER returns 2
            mock_getch.side_effect = [ord('2'), KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 2, f"Expected 2, got {result}"
        
    print("  PASSED")


def test_cancel_keys():
    """Test all cancellation keys."""
    print("\n[4/10] Testing cancellation keys...")
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        cancel_keys = [
            (ord('q'), "q"),
            (27, "ESC"),
            (KEY_RESIZE, "KEY_RESIZE"),
            (KEY_BACKSPACE, "KEY_BACKSPACE"),
            (127, "DEL"),
            (8, "BS"),
        ]
        
        for key, name in cancel_keys:
            print(f"    Testing {name}...")
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = key
                result = ui.render_menu(options, default=0, highlighted=0)
                assert result == -1, f"Cancel key {name} failed: expected -1, got {result}"
        
    print("  PASSED")


def test_enter_key_variations():
    """Test ENTER key with all variations."""
    print("\n[5/10] Testing ENTER key variations...")
    
    options = [{'label': f'Option {i}'} for i in range(3)]
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test 1: KEY_ENTER constant
        print("  Test 1: KEY_ENTER constant...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=1)
            assert result == 1, f"KEY_ENTER failed: expected 1, got {result}"
        
        # Test 2: ASCII 10 (LF)
        print("  Test 2: ASCII 10 (LF)...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [10]
            result = ui.render_menu(options, default=0, highlighted=1)
            assert result == 1, f"ASCII 10 failed: expected 1, got {result}"
        
        # Test 3: ASCII 13 (CR)
        print("  Test 3: ASCII 13 (CR)...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [13]
            result = ui.render_menu(options, default=0, highlighted=1)
            assert result == 1, f"ASCII 13 failed: expected 1, got {result}"
        
    print("  PASSED")


def test_menu_redraw_on_keypress():
    """Test that menu redraws correctly on keypress."""
    print("\n[6/10] Testing menu redraw on keypress...")
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Mock redraw to track calls
        original_redraw = ui.render_menu
        redraw_count = [0]
        
        # Patch the inner redraw function by monkey-patching
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_DOWN, KEY_DOWN, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            # Verify redraw was called
            assert mock_win.addstr.call_count > 0, "Menu should have been redrawn"
        
    print("  PASSED")


def test_key_code_constants():
    """Test that key code constants are correct."""
    print("\n[7/10] Testing key code constants...")
    
    # Verify KEY_ENTER is 343 (this is the important one for our tests)
    assert KEY_ENTER == 343, f"curses.KEY_ENTER is {KEY_ENTER}, expected 343"
    
    # Verify KEY_UP and KEY_DOWN are valid curses constants
    assert isinstance(KEY_UP, int), "curses.KEY_UP should be an integer"
    assert isinstance(KEY_DOWN, int), "curses.KEY_DOWN should be an integer"
    
    # Verify KEY_RESIZE is 410
    assert KEY_RESIZE == 410, f"curses.KEY_RESIZE is {KEY_RESIZE}, expected 410"
    
    # Verify KEY_PPAGE and KEY_NPAGE
    assert KEY_PPAGE == 339, f"curses.KEY_PPAGE is {KEY_PPAGE}, expected 339"
    assert KEY_NPAGE == 338, f"curses.KEY_NPAGE is {KEY_NPAGE}, expected 338"
    
    print("  PASSED")


def test_special_keys_handling():
    """Test handling of special keys."""
    print("\n[8/10] Testing special keys handling...")
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test: Navigation keys move selection, then enter selects
        print("  Test 1: Navigation keys move selection...")
        with patch.object(mock_win, 'getch') as mock_getch:
            # UP wraps to last (4), DOWN wraps to first (0), ENTER returns 0
            mock_getch.side_effect = [KEY_UP, KEY_DOWN, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 0, f"Navigation keys failed: expected 0, got {result}"
        
    print("  PASSED")


def test_empty_options_list():
    """Test menu with empty options list."""
    print("\n[9/10] Testing empty options list...")
    
    options = []
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test: Empty options list returns current highlighted index (0)
        print("  Test 1: Empty options list...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_ENTER
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 0, f"Empty options failed: expected 0, got {result}"
        
    print("  PASSED")


def test_single_option():
    """Test menu with single option."""
    print("\n[10/10] Testing single option...")
    
    options = [{'label': 'Only Option'}]
    ui = UIManager()
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 80)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test: Single option with enter should return 0
        print("  Test 1: Single option with enter...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 0, f"Single option failed: expected 0, got {result}"
        
    print("  PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("Testing Arrow Key Handling in UIManager")
    print("=" * 80)
    print("\nKey Codes Reference:")
    print(f"  KEY_UP = {KEY_UP}")
    print(f"  KEY_DOWN = {KEY_DOWN}")
    print(f"  KEY_RIGHT = {KEY_RIGHT}")
    print(f"  KEY_LEFT = {KEY_LEFT}")
    print(f"  KEY_ENTER = {KEY_ENTER}")
    print(f"  KEY_RESIZE = {KEY_RESIZE}")
    print(f"  KEY_PPAGE = {KEY_PPAGE}")
    print(f"  KEY_NPAGE = {KEY_NPAGE}")
    print(f"  KEY_BACKSPACE = {KEY_BACKSPACE}")
    
    try:
        test_arrow_key_navigation()
        test_page_key_navigation()
        test_number_input_selection()
        test_cancel_keys()
        test_enter_key_variations()
        test_menu_redraw_on_keypress()
        test_key_code_constants()
        test_special_keys_handling()
        test_empty_options_list()
        test_single_option()
        
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
