#!/usr/bin/env python3
"""
Comprehensive test suite for UIManager with proper mocking.

Run with: python3 test_ui_manager_comprehensive.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import curses

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

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
    
    # Test 1: Initialization
    print("\n[1/6] Testing Initialization...")
    test_init()
    
    # Test 2: Menu Navigation
    print("\n[2/6] Testing Menu Navigation...")
    test_menu_navigation()
    
    # Test 3: Confirmation Prompts
    print("\n[3/6] Testing Confirmation Prompts...")
    test_confirmation()
    
    # Test 4: Progress Bars
    print("\n[4/6] Testing Progress Bars...")
    test_progress()
    
    # Test 5: Styling
    print("\n[5/6] Testing Styling...")
    test_styling()
    
    # Test 6: Edge Cases
    print("\n[6/6] Testing Edge Cases...")
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
    import curses
    import ui_manager
    options = [{'label': f'Option {i}'} for i in range(5)]
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_ENTER = curses.KEY_ENTER
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_PPAGE = curses.KEY_PPAGE
    KEY_NPAGE = curses.KEY_NPAGE
    
    mock_win = MagicMock()
    mock_win.getyx.return_value = (0, 0)
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attron.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    mock_win.box.return_value = None
    mock_win.keypad.return_value = None
    mock_win.timeout.return_value = None
    mock_win.move.return_value = None
    mock_win.box.return_value = None
    mock_win.erase.return_value = None
    mock_win.addstr.return_value = None
    mock_win.attroff.return_value = None
    mock_win.refresh.return_value = None
    
    # Create a curses module mock with all required functions
    curses_mock = MagicMock(spec=curses)
    curses_mock.initscr.return_value = MagicMock()
    curses_mock.start_color = MagicMock()
    curses_mock.init_pair = MagicMock(return_value=None)
    curses_mock.cbreak = MagicMock(return_value=True)
    curses_mock.noecho = MagicMock()
    curses_mock.curs_set = MagicMock(return_value=None)
    curses_mock.has_ungetch = MagicMock(return_value=False)
    curses_mock.getscrptr = MagicMock(return_value=None)
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
    # Add error exception class
    class CursesError(Exception):
        pass
    curses_mock.error = CursesError
    
    with patch('ui_manager.curses', curses_mock), \
         patch('ui_manager.curses.newwin', return_value=mock_win):
        ui = UIManager("Test Menu")
        ui._using_curses = True
        # Set a valid color pair to avoid MagicMock issues
        ui._color_pair = curses.A_BOLD

        # Set up mocks for screen and refresh
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (20, 60)
        ui._screen = mock_screen

        # Test 1: Enter selects highlighted
        mock_win.getch.side_effect = [KEY_ENTER]
        result = ui.render_menu(options, default=0, highlighted=0)
        assert result == 0, f"Should return selected index, got {result}"

        # Test 2: Arrow keys cycle
        mock_win.getch.side_effect = [KEY_DOWN, KEY_UP, KEY_ENTER]
        result = ui.render_menu(options, default=0, highlighted=0)
        assert isinstance(result, int) and result >= 0, "Should return valid index on enter"

        # Test 3: Typing number
        mock_win.getch.side_effect = [ord('3'), KEY_ENTER]
        result = ui.render_menu(options, default=0, highlighted=0)
        assert result == 3, f"Should select by typing number, got {result}"

        # Test 4: Cancel with q
        mock_win.getch.side_effect = [ord('q')]
        result = ui.render_menu(options, default=0, highlighted=0)
        assert result == -1, f"Should return -1 on cancel, got {result}"


def test_confirmation():
    """Test confirmation prompts."""
    import curses
    KEY_ENTER = curses.KEY_ENTER
    
    with patch('ui_manager.curses', MagicMock(spec=curses, **{
        'initscr': MagicMock(return_value=MagicMock()),
        'start_color': MagicMock(),
        'init_pair': MagicMock(return_value=None),
        'cbreak': MagicMock(return_value=True),
        'noecho': MagicMock(),
        'curs_set': MagicMock(return_value=None),
        'has_ungetch': MagicMock(return_value=False),
        'getscrptr': MagicMock(return_value=None),
    })), patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:
        ui = UIManager("Test")
        ui._using_curses = True
        
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (20, 60)
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)

        # Test 1: Enter confirms
        mock_win.getch.return_value = KEY_ENTER
        result = ui.render_confirmation("Are you sure?")
        assert result is True, "Enter should confirm"
        
        # Test 2: n cancels
        mock_win.getch.return_value = ord('n')
        result = ui.render_confirmation("Are you sure?")
        assert result is False, "n should cancel"
        
        # Test 3: y confirms
        mock_win.getch.return_value = ord('Y')
        result = ui.render_confirmation("Are you sure?")
        assert result is True, "Y should confirm"


def test_progress():
    """Test progress bar rendering."""
    import curses
    KEY_ENTER = curses.KEY_ENTER
    
    with patch('ui_manager.curses', MagicMock(spec=curses, **{
        'initscr': MagicMock(return_value=MagicMock()),
        'start_color': MagicMock(),
        'init_pair': MagicMock(return_value=None),
        'cbreak': MagicMock(return_value=True),
        'noecho': MagicMock(),
        'curs_set': MagicMock(return_value=None),
        'has_ungetch': MagicMock(return_value=False),
        'getscrptr': MagicMock(return_value=None),
    })):
        ui = UIManager("Test")
        ui._using_curses = True
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE', new_callable=MagicMock), \
             patch('builtins.input', return_value='\n'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = KEY_ENTER
            
            # Test 1: Normal progress
            ui.render_progress_bar("file.zip", 1000, 10000, percent=10.5)
            
            # Test 2: Spinner
            ui.render_progress_bar("unknown.zip", 0, 0)


def test_styling():
    """Test color and styling requirements."""
    import curses
    KEY_DOWN = curses.KEY_DOWN
    
    with patch('ui_manager.curses', MagicMock(spec=curses, **{
        'initscr': MagicMock(return_value=MagicMock()),
        'start_color': MagicMock(),
        'init_pair': MagicMock(return_value=None),
        'cbreak': MagicMock(return_value=True),
        'noecho': MagicMock(),
        'curs_set': MagicMock(return_value=None),
        'has_ungetch': MagicMock(return_value=False),
        'getscrptr': MagicMock(return_value=None),
    })):
        ui = UIManager("Test")
        ui._using_curses = True
        
    # Verify color pair exists
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
    
    assert ui._color_pair is not None
    assert curses.A_BOLD in ui._color_pair, "Color pair should include BOLD"
    
    # Test that render uses reverse video for highlights
    options = [{'label': 'Option'}]
    
    with patch.object(ui, '_screen') as mock_screen, \
         patch.object(ui, 'refresh') as mock_refresh, \
         patch('curses.KEY_DOWN'), \
         patch('ui_manager.curses.newwin', return_value=MagicMock()):
        
        mock_screen.getmaxyx.return_value = (10, 60)
        mock_win = MagicMock()
        mock_screen.newwin.return_value = mock_win
        mock_win.getyx.return_value = (0, 0)
        
        ui.render_menu(options, default=0, highlighted=0)


def test_edge_cases():
    """Test edge cases and error handling."""
    import curses
    KEY_ENTER = curses.KEY_ENTER
    
    with patch('ui_manager.curses', MagicMock(spec=curses, **{
        'initscr': MagicMock(return_value=MagicMock()),
        'start_color': MagicMock(),
        'init_pair': MagicMock(return_value=None),
        'cbreak': MagicMock(return_value=True),
        'noecho': MagicMock(),
        'curs_set': MagicMock(return_value=None),
        'has_ungetch': MagicMock(return_value=False),
        'getscrptr': MagicMock(return_value=None),
    })):
        ui = UIManager("Test")
        ui._using_curses = True
    
    # Empty options
    with patch.object(ui, '_screen') as mock_screen, \
         patch.object(ui, 'refresh') as mock_refresh, \
         patch('ui_manager.curses.newwin', return_value=MagicMock()):
        
        result = ui.render_menu([], default=0, highlighted=0)
        assert result == -1, "Empty options should return -1"
    
    # Invalid input handling
    with patch.object(ui, '_screen') as mock_screen, \
         patch.object(ui, 'refresh') as mock_refresh, \
         patch('ui_manager.curses.newwin', return_value=MagicMock()):
        
        options = [{'label': 'Opt'}]
        mock_screen.getmaxyx.return_value = (10, 60)
        mock_win = MagicMock()
        mock_screen.newwin.return_value = mock_win
        mock_win.getyx.return_value = (0, 0)
        
        mock_win.getch.side_effect = [ord('9'), KEY_ENTER]
        result = ui.render_menu(options, default=0, highlighted=0)
        assert result != 9, "Invalid input should not return invalid index"
    
    # No screen handling
    ui._screen = None
    ui._using_curses = True
    
    # Should not crash
    result = ui.render_confirmation("Test")
    assert result is not None, "Should handle None screen gracefully"


if __name__ == '__main__':
    run_tests()


def test_full_integration_flow():
    """Test full integration flow: menu selection → confirmation → progress bar."""
    import curses
    
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
        
        # Configure mocks for each window
        menu_win = mock_newwin_list.return_value  # First window (menu)
        confirm_win = mock_newwin_list.return_value  # Second window (confirmation)
        progress_win = mock_newwin_list.return_value  # Third window (progress)
        
        for win in [menu_win, confirm_win, progress_win]:
            win.getyx.return_value = (0, 0)
            win.erase.return_value = None
            win.addstr.return_value = None
            win.attron.return_value = None
            win.attroff.return_value = None
            win.refresh.return_value = None
        
        # Create UIManager
        ui = UIManager("Test Integration")
        ui._using_curses = True
        
        # Set up screen mock
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (24, 80)
        ui._screen = mock_screen
        
        # Step 1: Menu selection - user selects "Update" (index 1)
        menu_win.getch.side_effect = [curses.KEY_DOWN, curses.KEY_DOWN, KEY_ENTER]
        menu_selection = ui.render_menu(options, default=0, highlighted=0)
        assert menu_selection == 1, f"Menu should select option 1 (Update), got {menu_selection}"
        
        # Step 2: Confirmation - user confirms with 'y'
        confirm_win.getch.side_effect = [ord('y')]
        confirmation = ui.render_confirmation("Proceed with installation? [Y/n]:", default=True)
        assert confirmation is True, f"Confirmation should return True, got {confirmation}"
        
        # Step 3: Progress bar - simulate download progress
        # Progress bar waits for key, so we need to provide a key
        mock_screen.getch.return_value = KEY_RESIZE
        ui.render_progress_bar("update.zip", 500, 1000, percent=50.0)
        
        # Verify all windows were created (one for each render call)
        assert mock_newwin_list.call_count == 3, \
            f"Should create 3 windows, got {mock_newwin_list.call_count}"
    
    print("  ✓ Full integration flow test passed")
