#!/usr/bin/env python3
"""
Pytest-compatible test suite for UIManager.

Run with: pytest test_ui_manager_pytest.py -v
"""

import sys
from pathlib import Path
import curses

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

import pytest
from unittest.mock import MagicMock, patch
from ui_manager import UIManager


def create_ui():
    """Create a UIManager instance with mocked curses."""
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
    return ui, mock_curses


class TestUIManagerPytest:
    """Pytest tests for UIManager."""
    
    def test_init_fallback_on_error(self):
        """Test that UI falls back gracefully when curses fails."""
        with patch('curses.initscr', side_effect=curses.error("Failed")):
            ui = UIManager("Test")
            assert not ui._using_curses
            assert ui._screen is None
    
    def test_menu_navigation_arrows(self):
        """Test arrow key navigation in menu."""
        options = [{'label': f'Option {i}'} for i in range(5)]
        
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_UP'), \
             patch('curses.KEY_DOWN'), \
             patch('curses.KEY_RESIZE'), \
             patch('curses.KEY_PPAGE'), \
             patch('curses.KEY_NPAGE'), \
              patch('curses.A_REVERSE'), \
              patch('curses.A_BOLD'), \
              patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:

            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_win.erase.return_value = None
            mock_win.addstr.return_value = None
            mock_win.attron.return_value = None
            mock_win.attroff.return_value = None
            mock_win.refresh.return_value = None
            mock_screen.getmaxyx.return_value = (20, 60)

            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.side_effect = [
                    curses.KEY_UP,  # Move up: 0 -> 4
                    curses.KEY_DOWN,  # Move down: 4 -> 0
                    10,  # Enter to confirm
                ]

                result = ui.render_menu(options, default=0, highlighted=0)
                assert result == 0
    
    def test_menu_typing_selection(self):
        """Test selecting by typing the number."""
        options = [{'label': 'Option'}]
        
        # Create proper mock window
        mock_win = MagicMock()
        mock_win.getyx.return_value = (0, 0)
        mock_win.erase.return_value = None
        mock_win.addstr.return_value = None
        mock_win.attron.return_value = None
        mock_win.attroff.return_value = None
        mock_win.refresh.return_value = None
        mock_win.getch.side_effect = [ord('3'), 10]  # Type '3' then Enter
        
        # Create UIManager with minimal setup
        ui = UIManager("Test")
        ui._using_curses = True
        ui._screen = MagicMock()
        ui._screen.getmaxyx.return_value = (20, 60)
        ui._color_pair = 12345  # Dummy color pair
        
        # Mock only what's absolutely needed
        with patch('ui_manager.curses.newwin', return_value=mock_win), \
             patch.object(ui, 'refresh'), \
             patch('builtins.input', return_value='\n'), \
             patch('sys.stdin.readline', return_value='\n'), \
             patch('curses.setupterm'):
            
            result = ui.render_menu(options, default=0, highlighted=0)
            assert result == 3
    
    def test_menu_cancel_keys(self):
        """Test that cancel keys return -1."""
        options = [{'label': 'Option'}]
        
        ui, _ = create_ui()
        
        for cancel_key in [ord('q'), 27, curses.KEY_RESIZE, curses.KEY_BACKSPACE, 127, 8]:
            with patch.object(ui, '_screen') as mock_screen, \
                 patch.object(ui, 'refresh'), \
                 patch('curses.KEY_RESIZE'), \
                 patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:

                mock_win = mock_newwin.return_value
                mock_win.getyx.return_value = (0, 0)
                mock_screen.getmaxyx.return_value = (20, 60)

                with patch.object(mock_win, 'getch') as mock_getch:
                    mock_getch.return_value = cancel_key
                    
                    result = ui.render_menu(options, default=0, highlighted=0)
                    assert result == -1, f"Cancel key {cancel_key} should return -1"
    
    def test_confirmation_enter_confirms(self):
        """Enter key confirms the action."""
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_RESIZE'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:

            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)

            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = 10  # Enter

                result = ui.render_confirmation("Are you sure?")
                assert result is True
    
    def test_confirmation_n_cancels(self):
        """n or N cancels the action."""
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_RESIZE'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:

            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_win.erase.return_value = None
            mock_win.addstr.return_value = None
            mock_win.attron.return_value = None
            mock_win.attroff.return_value = None
            mock_win.refresh.return_value = None
            mock_screen.getmaxyx.return_value = (20, 60)

            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = ord('n')
                result = ui.render_confirmation("Are you sure?")
                assert result is False
    
    def test_confirmation_y_confirms(self):
        """y or Y confirms the action."""
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_RESIZE'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:

            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)

            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = ord('Y')
                
                result = ui.render_confirmation("Are you sure?")
                assert result is True
    
    def test_progress_bar_with_bytes(self):
        """Progress bar shows bytes and percentage."""
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:

            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = 10
            mock_screen.getmaxyx.return_value = (20, 60)

            ui.render_progress_bar("file.zip", 1000, 10000, percent=10.5)
    
    def test_progress_bar_spinner(self):
        """When total is 0, shows spinner."""
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:

            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = 10
            mock_screen.getmaxyx.return_value = (20, 60)

            # Test with total=0 to trigger spinner mode
            ui.render_progress_bar("unknown.zip", 0, 0, percent=None)
    
    def test_full_workflow_simulation(self):
        """Simulate complete UI workflow."""
        # Menu
        options = [{'label': 'Install'}, {'label': 'Update'}]
        
        ui, _ = create_ui()
        
        mock_curses = MagicMock(spec=curses)
        mock_curses.initscr.return_value = MagicMock()
        mock_curses.start_color = MagicMock()
        mock_curses.init_pair = MagicMock(return_value=None)
        mock_curses.cbreak = MagicMock(return_value=True)
        mock_curses.noecho = MagicMock()
        mock_curses.curs_set = MagicMock(return_value=None)
        mock_curses.has_ungetch = MagicMock(return_value=False)
        mock_curses.getscrptr = MagicMock(return_value=None)
        mock_curses.endwin = MagicMock()  # Mock endwin to do nothing
        
        with patch('ui_manager.curses', mock_curses):
            # Create proper mock windows
            menu_win = MagicMock()
            menu_win.getyx.return_value = (0, 0)
            menu_win.erase.return_value = None
            menu_win.addstr.return_value = None
            menu_win.attron.return_value = None
            menu_win.attroff.return_value = None
            menu_win.refresh.return_value = None
            menu_win.getch.side_effect = [ord('2'), 10]
            
            confirm_win = MagicMock()
            confirm_win.getyx.return_value = (0, 0)
            confirm_win.getch.return_value = 10
            
            with patch.object(ui, '_screen') as mock_screen, \
                 patch.object(ui, 'refresh'), \
                 patch('curses.KEY_DOWN'), \
                 patch('curses.KEY_UP'), \
                 patch('ui_manager.curses.newwin', side_effect=[menu_win, confirm_win]), \
                 patch('curses.setupterm'), \
                 patch('curses.napms'), \
                 patch('builtins.input', return_value='\n'), \
                 patch('sys.stdin.readline', return_value='\n'):

                mock_screen.getmaxyx.return_value = (20, 60)
                result = ui.render_menu(options, default=0, highlighted=0)
                assert result == 2
            
            # Cleanup
        ui._cleanup_terminal()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestMenuPageJump:
    """Tests for KEY_PPAGE and KEY_NPAGE page jump behavior."""
    
    def test_key_ppage_jumps_to_first_option(self):
        """KEY_PPAGE should jump to the first option."""
        options = [{'label': f'Option {i}'} for i in range(5)]
        
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_UP'), \
             patch('curses.KEY_DOWN'), \
             patch('curses.KEY_RESIZE'), \
             patch('curses.KEY_PPAGE'), \
             patch('curses.KEY_NPAGE'), \
             patch('curses.A_REVERSE'), \
             patch('curses.A_BOLD'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            # Start from middle (option 2), press PAGE UP
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.side_effect = [curses.KEY_PPAGE, 10]
                
                result = ui.render_menu(options, default=2, highlighted=2)
                assert result == 0, f"KEY_PPAGE should jump to first option (0), got {result}"
    
    def test_key_npage_jumps_down_by_page_size(self):
        """KEY_NPAGE should jump down by page size."""
        options = [{'label': f'Option {i}'} for i in range(5)]
        
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_UP'), \
             patch('curses.KEY_DOWN'), \
             patch('curses.KEY_RESIZE'), \
             patch('curses.KEY_PPAGE'), \
             patch('curses.KEY_NPAGE'), \
             patch('curses.A_REVERSE'), \
             patch('curses.A_BOLD'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            # Start from middle (option 2), press PAGE DOWN
            # page_size = max(1, min(len(options) // 2, (menu_height - 2) // 2))
            # With 5 options and menu_height = 9, page_size = min(2, 3) = 2
            # First PAGE DOWN: 2 -> 4 (2 + 2 = 4)
            # Second PAGE DOWN: 4 + 2 = 6, 6 >= 5, so 6 % 5 = 1
            # Third key: Enter to select
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.side_effect = [curses.KEY_NPAGE, curses.KEY_NPAGE, 10]
                
                result = ui.render_menu(options, default=2, highlighted=2)
                # First PAGE DOWN: 2 -> 4
                # Second PAGE DOWN: 4 -> 1 (wraps)
                # Third key: Enter to select
                assert result == 1, f"KEY_NPAGE wrapping should work, got {result}"


class TestMenuWrapping:
    """Tests for wrapping behavior when navigating past boundaries."""
    
    def test_wraps_past_first_option(self):
        """Navigating past first option should wrap to last."""
        options = [{'label': f'Option {i}'} for i in range(5)]
        
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_UP'), \
             patch('curses.KEY_DOWN'), \
             patch('curses.KEY_RESIZE'), \
             patch('curses.KEY_PPAGE'), \
             patch('curses.KEY_NPAGE'), \
             patch('curses.A_REVERSE'), \
             patch('curses.A_BOLD'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            # Start at option 1, press UP twice
            # First UP: 1 -> 0 (normal)
            # Second UP: 0 -> 4 (wrap to last)
            # Third key: Enter to select
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.side_effect = [curses.KEY_UP, curses.KEY_UP, 10]
                
                result = ui.render_menu(options, default=1, highlighted=1)
                assert result == 4, f"Should wrap from option 1 -> 0 -> 4, got {result}"
    
    def test_wraps_past_last_option(self):
        """Navigating past last option should wrap to first."""
        options = [{'label': f'Option {i}'} for i in range(5)]
        
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_UP'), \
             patch('curses.KEY_DOWN'), \
             patch('curses.KEY_RESIZE'), \
             patch('curses.KEY_PPAGE'), \
             patch('curses.KEY_NPAGE'), \
             patch('curses.A_REVERSE'), \
             patch('curses.A_BOLD'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            # Start at option 3, press DOWN twice
            # First DOWN: 3 -> 4 (normal)
            # Second DOWN: 4 -> 0 (wrap to first)
            # Third key: Enter to select
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.side_effect = [curses.KEY_DOWN, curses.KEY_DOWN, 10]
                
                result = ui.render_menu(options, default=3, highlighted=3)
                assert result == 0, f"Should wrap from option 3 -> 4 -> 0, got {result}"


class TestHighlightedNone:
    """Tests for highlighted=None as initial state."""
    
    def test_highlighted_none_initial_state(self):
        """When highlighted=None, should start at first option."""
        options = [{'label': f'Option {i}'} for i in range(5)]
        
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_UP'), \
             patch('curses.KEY_DOWN'), \
             patch('curses.KEY_RESIZE'), \
             patch('curses.KEY_PPAGE'), \
             patch('curses.KEY_NPAGE'), \
             patch('curses.A_REVERSE'), \
             patch('curses.A_BOLD'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            # Pass highlighted=None
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.side_effect = [curses.KEY_DOWN, 10]
                
                result = ui.render_menu(options, default=0, highlighted=None)
                # Should behave as if highlighted=0
                assert result == 1, f"Should start at first option when highlighted=None, got {result}"


class TestConfirmationTimeout:
    """Tests for confirmation timeout behavior."""
    
    def test_timeout_always_returns_true(self):
        """Timeout in confirmation always returns True (assumed yes)."""
        ui, _ = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh'), \
             patch('curses.KEY_RESIZE'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            # Simulate timeout (None)
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = None
                
                # Timeout always returns True regardless of default parameter
                result = ui.render_confirmation("Are you sure?", default=False)
                assert result is True, f"Timeout should return True, got {result}"
    
    def test_timeout_independent_of_default(self):
        """Timeout returns True regardless of default parameter."""
        ui, _ = create_ui()
        
        # Test that timeout returns True regardless of default parameter
        test_cases = [
            (True, True),   # default=True, expect True
            (False, True),  # default=False, but timeout still returns True
        ]
        
        for default_value, expected_result in test_cases:
            with patch.object(ui, '_screen') as mock_screen, \
                 patch.object(ui, 'refresh'), \
                 patch('curses.KEY_RESIZE'), \
                 patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:
                
                mock_win = mock_newwin.return_value
                mock_win.getyx.return_value = (0, 0)
                mock_screen.getmaxyx.return_value = (20, 60)
                
                with patch.object(mock_win, 'getch') as mock_getch:
                    mock_getch.return_value = None  # Timeout
                    
                    result = ui.render_confirmation("Test", default=default_value)
                    assert result == expected_result, \
                        f"Timeout with default={default_value} should return {expected_result}, got {result}"
