#!/usr/bin/env python3
"""
Test keyboard input handling using actual terminal key codes.

This tests the actual keyboard input handling in render_menu and render_confirmation
by simulating real key sequences from a terminal.

Actual key codes from curses module:
- KEY_UP = curses.KEY_UP (259)
- KEY_DOWN = curses.KEY_DOWN (260)
- KEY_RIGHT = curses.KEY_RIGHT (261)
- KEY_LEFT = curses.KEY_LEFT (262)
- KEY_ENTER = curses.KEY_ENTER (343)
- KEY_RESIZE = curses.KEY_RESIZE (410)
- KEY_PPAGE = curses.KEY_PPAGE (339)
- KEY_NPAGE = curses.KEY_NPAGE (338)
- KEY_BACKSPACE = curses.KEY_BACKSPACE (263)
"""

import sys
from pathlib import Path
import curses
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

from ui_manager import UIManager


def test_all_key_codes_comprehensive():
    """Comprehensive test of all key codes in render_menu."""
    print("\n[1/6] Comprehensive key code testing in render_menu...")
    
    options = [{'label': f'Option {i}'} for i in range(10)]
    ui = UIManager()
    
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
    
    # Create test UI with mocked curses
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
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
        
        # Test 1: Arrow key navigation
        print("  Testing arrow keys...")
        with patch.object(mock_win, 'getch') as mock_getch:
            # KEY_DOWN (0->1), KEY_DOWN (1->2), KEY_UP (2->1), KEY_ENTER -> returns 1
            mock_getch.side_effect = [KEY_DOWN, KEY_DOWN, KEY_UP, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 1, f"Arrow navigation failed: expected 1, got {result}"
        
        # Test 2: Number input selection
        print("  Testing number input...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [ord('5'), KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 5, f"Number input failed: expected 5, got {result}"
        
        # Test 3: Page keys navigation
        print("  Testing page keys...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_NPAGE, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 5, f"Page down failed: expected 5, got {result}"
        
        # Test 4: Cancel with q
        print("  Testing cancel with 'q'...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = ord('q')
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == -1, f"Cancel with 'q' failed: expected -1, got {result}"
        
        # Test 5: Cancel with ESC
        print("  Testing cancel with ESC...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = 27
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == -1, f"Cancel with ESC failed: expected -1, got {result}"
        
        # Test 6: Cancel with KEY_RESIZE
        print("  Testing cancel with KEY_RESIZE...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = KEY_RESIZE
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == -1, f"Cancel with KEY_RESIZE failed: expected -1, got {result}"
    
    print("  PASSED")


# Commented out due to issues with print_simple_menu mocking
def test_all_key_codes_simple_menu():
    """Comprehensive test of all key codes in print_simple_menu."""
    print("\n[2/6] Comprehensive key code testing in print_simple_menu...")
    
    options = ['Option 1', 'Option 2', 'Option 3']
    ui = UIManager()
    
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_ENTER = curses.KEY_ENTER
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_BACKSPACE = curses.KEY_BACKSPACE
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_screen.getyx.return_value = (0, 0)
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_RESIZE', KEY_RESIZE), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test 1: Arrow key navigation
        print("  Testing arrow keys...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_DOWN, KEY_DOWN, KEY_ENTER]
            result = ui.print_simple_menu(options, default=0, highlighted=0)
            assert result == 2, f"Arrow navigation failed: expected 2, got {result}"
        
        # Test 2: Number input
        print("  Testing number input...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [ord('2'), KEY_ENTER]
            result = ui.print_simple_menu(options, default=0, highlighted=0)
            assert result == 1, f"Number input failed: expected 1, got {result}"
        
        # Test 3: Enter confirmation
        print("  Testing enter confirmation...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_ENTER]
            result = ui.print_simple_menu(options, default=0, highlighted=1)
            assert result == 1, f"Enter failed: expected 1, got {result}"
        
        # Test 4: Cancel with q
        print("  Testing cancel with 'q'...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = ord('q')
            result = ui.print_simple_menu(options, default=0, highlighted=0)
            assert result is None, f"Cancel with 'q' failed: expected None, got {result}"
    
    print("  PASSED")


def test_page_keys_edge_cases():
    """Test page keys with edge cases."""
    print("\n[3/6] Testing page keys edge cases...")
    
    # Small menu - page keys should wrap
    options = [{'label': 'Option'}] * 3
    ui = UIManager()
    
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_ENTER = curses.KEY_ENTER
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 40)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_UP', KEY_UP), \
         patch('curses.KEY_DOWN', KEY_DOWN), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Page down on small menu should wrap
        print("  Testing page down on small menu...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_NPAGE, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 0, f"Page down wrap failed: expected 0, got {result}"
        
        # Page up from last item should wrap
        print("  Testing page up from last...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_UP, KEY_UP, KEY_UP, KEY_UP, KEY_PPAGE, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 0, f"Page up wrap failed: expected 0, got {result}"
    
    print("  PASSED")


def test_number_input_edge_cases():
    """Test number input with edge cases."""
    print("\n[4/6] Testing number input edge cases...")
    
    ui = UIManager()
    
    KEY_ENTER = curses.KEY_ENTER
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 40)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    # Test 1: Out of range number
    print("  Testing out-of-range number...")
    options = [{'label': 'Option'}] * 3
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_UP', new_callable=MagicMock), \
         patch('curses.KEY_DOWN', new_callable=MagicMock), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_PPAGE', new_callable=MagicMock), \
         patch('curses.KEY_NPAGE', new_callable=MagicMock), \
         patch('curses.KEY_BACKSPACE', new_callable=MagicMock), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [ord('9'), KEY_ENTER]  # 9 is out of range
            result = ui.render_menu(options, default=0, highlighted=0)
            # Should return -1 or current highlighted, not crash
            print(f"    Result: {result}")
    
    # Test 2: Non-numeric key should be ignored
    print("  Testing non-numeric key ignored...")
    with patch.object(mock_win, 'getch') as mock_getch:
        mock_getch.side_effect = [KEY_UP, ord('a'), KEY_ENTER]  # 'a' is invalid
        result = ui.render_menu(options, default=0, highlighted=0)
        assert result == 0, f"Non-numeric should be ignored: expected 0, got {result}"
    
    print("  PASSED")


def test_cancel_keys_all_variations():
    """Test all cancellation keys."""
    print("\n[5/6] Testing all cancellation keys...")
    
    options = [{'label': 'Option'}] * 5
    ui = UIManager()
    
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    KEY_BACKSPACE = curses.KEY_BACKSPACE
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    cancel_keys = [
        (ord('q'), "q"),
        (27, "ESC"),
        (KEY_RESIZE, "KEY_RESIZE"),
        (KEY_BACKSPACE, "KEY_BACKSPACE"),
        (127, "DEL"),
        (8, "BS"),
    ]
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_UP', new_callable=MagicMock), \
         patch('curses.KEY_DOWN', new_callable=MagicMock), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_PPAGE', KEY_PPAGE), \
         patch('curses.KEY_NPAGE', KEY_NPAGE), \
         patch('curses.KEY_BACKSPACE', KEY_BACKSPACE), \
         patch('curses.KEY_ENTER', new_callable=MagicMock):
        
        for key, name in cancel_keys:
            print(f"    Testing {name}...")
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = key
                result = ui.render_menu(options, default=0, highlighted=0)
                assert result == -1, f"Cancel key {name} failed: expected -1, got {result}"
    
    print("  PASSED")


def test_enter_key_all_variations():
    """Test ENTER key with all variations."""
    print("\n[6/6] Testing ENTER key variations...")
    
    options = [{'label': 'Option'}] * 3
    ui = UIManager()
    
    KEY_ENTER = curses.KEY_ENTER
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 60)
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh', return_value=None), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_UP', new_callable=MagicMock), \
         patch('curses.KEY_DOWN', new_callable=MagicMock), \
         patch('curses.newwin', return_value=mock_win), \
         patch('curses.KEY_PPAGE', new_callable=MagicMock), \
         patch('curses.KEY_NPAGE', new_callable=MagicMock), \
         patch('curses.KEY_BACKSPACE', new_callable=MagicMock), \
         patch('curses.KEY_ENTER', KEY_ENTER):
        
        # Test 1: KEY_ENTER constant
        print("    Testing KEY_ENTER constant...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=1)
            assert result == 1, f"KEY_ENTER failed: expected 1, got {result}"
        
        # Test 2: ASCII 10 (LF)
        print("    Testing ASCII 10 (LF)...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [10]
            result = ui.render_menu(options, default=0, highlighted=1)
            assert result == 1, f"ASCII 10 failed: expected 1, got {result}"
        
        # Test 3: ASCII 13 (CR)
        print("    Testing ASCII 13 (CR)...")
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [13]
            result = ui.render_menu(options, default=0, highlighted=1)
            assert result == 1, f"ASCII 13 failed: expected 1, got {result}"
    
    print("  PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("Testing Actual Key Codes in UIManager")
    print("=" * 80)
    print("\nKey Codes Reference:")
    print(f"  KEY_UP = {curses.KEY_UP}")
    print(f"  KEY_DOWN = {curses.KEY_DOWN}")
    print(f"  KEY_RIGHT = {curses.KEY_RIGHT}")
    print(f"  KEY_LEFT = {curses.KEY_LEFT}")
    print(f"  KEY_ENTER = {curses.KEY_ENTER}")
    print(f"  KEY_RESIZE = {curses.KEY_RESIZE}")
    print(f"  KEY_PPAGE = {curses.KEY_PPAGE}")
    print(f"  KEY_NPAGE = {curses.KEY_NPAGE}")
    print(f"  KEY_BACKSPACE = {curses.KEY_BACKSPACE}")
    
    try:
        test_all_key_codes_comprehensive()
        test_all_key_codes_simple_menu()
        test_page_keys_edge_cases()
        test_number_input_edge_cases()
        test_cancel_keys_all_variations()
        test_enter_key_all_variations()
        
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
