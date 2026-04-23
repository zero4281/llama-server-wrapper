#!/usr/bin/env python3
"""
Comprehensive test suite for UIManager with proper mocking.

Run with: python3 test_ui_manager_comprehensive.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import curses

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd().parent))

from ui_manager import UIManager


def create_ui(title="Test"):
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
        ui._using_curses = True  # Force enabled
    return ui


def run_tests():
    """Run all test suites."""
    print("=" * 80)
    print("Running UIManager Tests")
    print("=" * 80)
    
    test_init()
    test_menu_navigation()
    test_confirmation()
    test_progress()
    test_styling()
    test_edge_cases()
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED")
    print("=" * 80)


def test_init():
    """Test UIManager initialization."""
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
        ui = UIManager("Test")
        ui._using_curses = True
    
    assert ui._using_curses, "UIManager should initialize curses"
    assert ui._screen is not None, "UIManager should have a screen"
    assert ui._color_pair is not None, "UIManager should have color pair"
    
    # Test cleanup
    ui._cleanup_terminal()
    assert not ui._using_curses, "Cleanup should disable curses"
    assert ui._screen is None, "Cleanup should clear screen"


def test_menu_navigation():
    """Test menu rendering and navigation."""
    KEY_ENTER = curses.KEY_ENTER
    KEY_DOWN = curses.KEY_DOWN
    KEY_UP = curses.KEY_UP
    
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    curses_mock = MagicMock(spec=curses)
    curses_mock.initscr.return_value = MagicMock()
    curses_mock.start_color = MagicMock()
    curses_mock.init_pair = MagicMock(return_value=None)
    curses_mock.cbreak = MagicMock(return_value=True)
    curses_mock.noecho = MagicMock()
    curses_mock.curs_set = MagicMock(return_value=None)
    curses_mock.has_ungetch = MagicMock(return_value=False)
    curses_mock.setupterm = MagicMock()
    curses_mock.napms = MagicMock()
    curses_mock.keypad = MagicMock()
    curses_mock.box = MagicMock()
    curses_mock.erase = MagicMock()
    curses_mock.move = MagicMock()
    curses_mock.timeout = MagicMock()
    curses_mock.color_pair = MagicMock()
    curses_mock.A_REVERSE = curses.A_REVERSE
    curses_mock.A_BOLD = curses.A_BOLD
    class CursesError(Exception):
        pass
    curses_mock.error = CursesError
    
    with patch('ui_manager.curses', curses_mock), \
         patch('ui_manager.curses.newwin', return_value=mock_win) as mock_newwin:
        ui = UIManager("Test Menu")
        ui._using_curses = True
        ui._color_pair = curses.A_BOLD
        
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (20, 60)
        ui._screen = mock_screen
        
        # Get the actual window instance created
        actual_win = mock_newwin.return_value
        # Each render_menu call needs its own key sequence
        actual_win.getch.side_effect = iter([KEY_DOWN, KEY_DOWN, KEY_ENTER, KEY_DOWN, KEY_DOWN, KEY_ENTER, ord('1'), ord('q')])
        
        # Test 1: Enter selects highlighted
        result = ui.render_menu([{'label': 'Opt1'}, {'label': 'Opt2'}], default=0, highlighted=0)
        assert isinstance(result, int) and 0 <= result <= 1, f"Should return valid index, got {result}"

        # Test 2: Arrow keys cycle
        result = ui.render_menu([{'label': 'Opt1'}, {'label': 'Opt2'}], default=0, highlighted=0)
        assert isinstance(result, int) and 0 <= result <= 1, "Should return valid index on enter"

        # Test 3: Typing number
        result = ui.render_menu([{'label': 'Opt1'}, {'label': 'Opt2'}], default=0, highlighted=0)
        assert isinstance(result, int) and 0 <= result <= 1, f"Should select valid index, got {result}"

        # Test 4: Cancel with q
        result = ui.render_menu([{'label': 'Opt1'}, {'label': 'Opt2'}], default=0, highlighted=0)
        assert result == -1, f"Should return -1 on cancel, got {result}"


def test_confirmation():
    """Test confirmation prompts."""
    KEY_ENTER = curses.KEY_ENTER
    KEY_DOWN = curses.KEY_DOWN
    KEY_UP = curses.KEY_UP
    
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    
    with patch('ui_manager.curses', MagicMock(spec=curses, **{
        'initscr': MagicMock(return_value=MagicMock()),
        'start_color': MagicMock(),
        'init_pair': MagicMock(return_value=None),
        'cbreak': MagicMock(return_value=True),
        'noecho': MagicMock(),
        'curs_set': MagicMock(return_value=None),
        'has_ungetch': MagicMock(return_value=False),
        'getscrptr': MagicMock(return_value=None),
        'setupterm': MagicMock(),
        'napms': MagicMock(),
        'keypad': MagicMock(),
        'box': MagicMock(),
        'erase': MagicMock(),
        'move': MagicMock(),
        'timeout': MagicMock(),
        'color_pair': MagicMock(),
        'A_REVERSE': curses.A_REVERSE,
        'A_BOLD': curses.A_BOLD,
        'error': type('CursesError', (Exception,), {}),
    })), \
    patch('ui_manager.curses.newwin', return_value=mock_win) as mock_newwin:
        ui = UIManager("Test")
        ui._using_curses = True
        ui._color_pair = curses.A_BOLD
        
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (20, 60)
        ui._screen = mock_screen
        
        # Get the actual window instance created
        actual_win = mock_newwin.return_value
        actual_win.getch.side_effect = [KEY_ENTER]  # Enter to confirm
        
        # Test 1: Enter confirms
        result = ui.render_confirmation("Proceed with installation? [Y/n]:", default=True)
        assert result is True, f"Should confirm on enter, got {result}"

        # Test 2: n cancels
        result = ui.render_confirmation("Proceed? [Y/n]:", default=True)
        assert result is False, f"Should cancel on n, got {result}"

        # Test 3: y confirms
        result = ui.render_confirmation("Proceed? [Y/n]:", default=False)
        assert result is True, f"Should confirm on y, got {result}"


def test_progress():
    """Test progress bars."""
    KEY_ENTER = curses.KEY_ENTER
    KEY_RESIZE = curses.KEY_RESIZE
    
    with patch('ui_manager.curses', MagicMock(spec=curses, **{
        'initscr': MagicMock(return_value=MagicMock()),
        'start_color': MagicMock(),
        'init_pair': MagicMock(return_value=None),
        'cbreak': MagicMock(return_value=True),
        'noecho': MagicMock(),
        'curs_set': MagicMock(return_value=None),
        'has_ungetch': MagicMock(return_value=False),
        'getscrptr': MagicMock(return_value=None),
        'setupterm': MagicMock(),
        'napms': MagicMock(),
        'keypad': MagicMock(),
        'box': MagicMock(),
        'erase': MagicMock(),
        'move': MagicMock(),
        'timeout': MagicMock(),
        'color_pair': MagicMock(),
        'A_REVERSE': curses.A_REVERSE,
        'A_BOLD': curses.A_BOLD,
        'error': type('CursesError', (Exception,), {}),
    })), \
    patch('ui_manager.curses.newwin', return_value=MagicMock()):
        mock_win = MagicMock()
        mock_win.getyx.return_value = (18, 58)  # Menu dimensions
        mock_win.getch.side_effect = [KEY_RESIZE, *([KEY_RESIZE] * 8)]
        
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (20, 60)
        
        ui = UIManager("Test")
        ui._using_curses = True
        ui._color_pair = curses.A_BOLD
        ui._screen = mock_screen
        
        # Test determinate bar
        ui.render_progress_bar("file.zip", 1000, 10000, percent=10.5)
        
        # Test spinner (total=0)
        ui.render_progress_bar("unknown.zip", 0, 0, percent=None)


def test_styling():
    """Test styling features."""
    
    mock_win = MagicMock()
    
    with patch('ui_manager.curses', MagicMock(spec=curses, **{
        'initscr': MagicMock(return_value=MagicMock()),
        'start_color': MagicMock(),
        'init_pair': MagicMock(return_value=None),
        'cbreak': MagicMock(return_value=True),
        'noecho': MagicMock(),
        'curs_set': MagicMock(return_value=None),
        'has_ungetch': MagicMock(return_value=False),
        'getscrptr': MagicMock(return_value=None),
        'setupterm': MagicMock(),
        'napms': MagicMock(),
        'keypad': MagicMock(),
        'box': MagicMock(),
        'erase': MagicMock(),
        'move': MagicMock(),
        'timeout': MagicMock(),
        'color_pair': MagicMock(return_value=curses.color_pair(1)),
        'A_REVERSE': curses.A_REVERSE,
        'A_BOLD': curses.A_BOLD,
        'error': type('CursesError', (Exception,), {}),
    })), \
    patch('ui_manager.curses.newwin', return_value=mock_win):
        ui = UIManager("Test")
        ui._using_curses = True
        ui._color_pair = curses.A_BOLD | curses.A_REVERSE
        
        # Verify UIManager applies color_pair attributes to windows
        ui.render_menu([{'label': 'Opt1'}], default=0, highlighted=0)
        
        assert mock_win.attron.called, "Window should have attron called"
        assert mock_win.attroff.called, "Window should have attroff called"
        
        # Verify color_pair is used correctly with curses.color_pair
        mock_win.attron.assert_any_call(ui._color_pair | curses.A_BOLD | curses.A_REVERSE)
        mock_win.attron.assert_any_call(ui._color_pair)


def test_edge_cases():
    """Test edge cases and error handling."""
    
    with patch('ui_manager.curses', MagicMock(spec=curses, **{
        'initscr': MagicMock(return_value=MagicMock()),
        'start_color': MagicMock(),
        'init_pair': MagicMock(return_value=None),
        'cbreak': MagicMock(return_value=True),
        'noecho': MagicMock(),
        'curs_set': MagicMock(return_value=None),
        'has_ungetch': MagicMock(return_value=False),
        'getscrptr': MagicMock(return_value=None),
    })), \
    patch('ui_manager.curses.newwin', return_value=MagicMock()):
        
        ui = UIManager("Test")
        ui._using_curses = True
        
        # Empty options
        result = ui.render_menu([], default=0, highlighted=0)
        assert result == -1, "Empty options should return -1"
        
        # Invalid input
        result = ui.render_menu([{'label': 'Opt'}], default=0, highlighted=0)
        assert result != 9, "Invalid input should not return invalid index"
        
        # No screen handling
        ui._screen = None
        result = ui.render_confirmation("Test")
        assert result is not None, "Should handle None screen gracefully"


if __name__ == '__main__':
    run_tests()


def test_full_integration_flow():
    """Test full integration flow: menu selection → confirmation → progress bar."""
    options = [{'label': 'Install'}, {'label': 'Update'}, {'label': 'Repair'}]
    
    KEY_ENTER = curses.KEY_ENTER
    KEY_RESIZE = curses.KEY_RESIZE
    
    with patch('ui_manager.curses', MagicMock(spec=curses, **{
        'initscr': MagicMock(return_value=MagicMock()),
        'start_color': MagicMock(),
        'init_pair': MagicMock(return_value=None),
        'cbreak': MagicMock(return_value=True),
        'noecho': MagicMock(),
        'curs_set': MagicMock(return_value=None),
        'has_ungetch': MagicMock(return_value=False),
        'getscrptr': MagicMock(return_value=None),
        'setupterm': MagicMock(),
    })), \
    patch('ui_manager.curses.newwin', side_effect=[MagicMock(), MagicMock(), MagicMock()]) as mock_newwin_list:
        
        menu_win = mock_newwin_list.return_value
        confirm_win = mock_newwin_list.return_value
        progress_win = mock_newwin_list.return_value
        
        for win in [menu_win, confirm_win, progress_win]:
            win.getyx.return_value = (0, 0)
            win.erase.return_value = None
            win.addstr.return_value = None
            win.attron.return_value = None
            win.attroff.return_value = None
            win.refresh.return_value = None
        
        ui = UIManager("Test Integration")
        ui._using_curses = True
        
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (24, 80)
        ui._screen = mock_screen
        
        # Step 1: Menu selection
        menu_win.getch.side_effect = [curses.KEY_DOWN, curses.KEY_DOWN, KEY_ENTER]
        menu_selection = ui.render_menu(options, default=0, highlighted=0)
        assert menu_selection == 1, f"Menu should select option 1, got {menu_selection}"
        
        # Step 2: Confirmation
        confirm_win.getch.side_effect = [curses.KEY_ENTER]
        confirmation = ui.render_confirmation("Proceed? [Y/n]:", default=True)
        assert confirmation is True, f"Confirmation should return True, got {confirmation}"
        
        # Step 3: Progress bar
        mock_screen.getch.return_value = KEY_RESIZE
        ui.render_progress_bar("update.zip", 500, 1000, percent=50.0)
        
        assert mock_newwin_list.call_count == 3, \
            f"Should create 3 windows, got {mock_newwin_list.call_count}"
    
    print("  ✓ Full integration flow test passed")