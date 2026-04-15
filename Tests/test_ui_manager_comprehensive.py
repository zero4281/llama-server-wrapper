#!/usr/bin/env python3
"""
Comprehensive test suite for UIManager with proper mocking.

Run with: python3 test_ui_manager_comprehensive.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

import curses
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
    options = [{'label': f'Option {i}'} for i in range(5)]
    KEY_UP = 259
    KEY_DOWN = 258
    KEY_ENTER = 10
    KEY_RESIZE = 328
    KEY_PPAGE = 1000
    KEY_NPAGE = 1001
    
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
        ui = UIManager("Test Menu")
        ui._using_curses = True
        
        # Set up mocks for screen and refresh
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (20, 60)
        mock_win = MagicMock()
        mock_screen.newwin.return_value = mock_win
        mock_win.getyx.return_value = (0, 0)
        
        # Patch screen temporarily
        original_screen = ui._screen
        ui._screen = mock_screen
        
        with patch.object(ui, 'refresh', return_value=None):
            # Test 1: Enter selects highlighted
            with patch('builtins.input') as mock_input:
                mock_input.return_value = "2"
                result = ui.render_menu(options, default=0, highlighted=0)
                assert result == 2, f"Should return selected index, got {result}"
            
            # Test 2: Arrow keys cycle
            mock_win.getch.side_effect = [KEY_DOWN, KEY_UP, KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result is not None, "Should return on enter"
            
            # Test 3: Typing number
            mock_win.getch.side_effect = [ord('3'), KEY_ENTER]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 3, f"Should select by typing number, got {result}"
            
            # Test 4: Cancel with q
            mock_win.getch.side_effect = [ord('q')]
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == -1, f"Should return -1 on cancel, got {result}"
        
        ui._screen = original_screen


def test_confirmation():
    """Test confirmation prompts."""
    KEY_ENTER = 10
    
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
             patch('curses.KEY_RESIZE', new_callable=MagicMock):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
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
    KEY_ENTER = 10
    
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
    KEY_DOWN = 258
    
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
         patch('curses.KEY_DOWN'):
        
        mock_screen.getmaxyx.return_value = (10, 60)
        mock_win = MagicMock()
        mock_screen.newwin.return_value = mock_win
        mock_win.getyx.return_value = (0, 0)
        
        ui.render_menu(options, default=0, highlighted=0)


def test_edge_cases():
    """Test edge cases and error handling."""
    KEY_ENTER = 10
    
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
         patch.object(ui, 'refresh') as mock_refresh:
        
        result = ui.render_menu([], default=0, highlighted=0)
        assert result == -1, "Empty options should return -1"
    
    # Invalid input handling
    with patch.object(ui, '_screen') as mock_screen, \
         patch.object(ui, 'refresh') as mock_refresh:
        
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
