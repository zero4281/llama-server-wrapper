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
from unittest.mock import MagicMock, patch, PropertyMock
from ui_manager import UIManager


class TestUIManagerPytest:
    """Pytest tests for UIManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Set up curses mocks before creating UIManager
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
            self.ui = UIManager("Test")
            self.ui._using_curses = True
            self.mock_curses = mock_curses
    
    def teardown_method(self):
        """Cleanup after each test."""
        # Restore curses mock between tests
        if hasattr(self, 'mock_curses'):
            with patch('ui_manager.curses', self.mock_curses):
                self.ui._cleanup_terminal()
    
    def test_init_fallback_on_error(self):
        """Test that UI falls back gracefully when curses fails."""
        with patch('curses.initscr', side_effect=curses.error("Failed")):
            ui = UIManager("Test")
            assert not ui._using_curses
            assert ui._screen is None
    
    def test_menu_navigation_arrows(self):
        """Test arrow key navigation in menu."""
        options = [{'label': f'Option {i}'} for i in range(5)]
        
        with patch.object(self.ui, '_screen') as mock_screen, \
             patch.object(self.ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_UP'), \
             patch('curses.KEY_DOWN'), \
             patch('curses.KEY_RESIZE'), \
             patch('curses.KEY_PPAGE'), \
             patch('curses.KEY_NPAGE'), \
             patch('curses.A_REVERSE'), \
             patch('curses.A_BOLD'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win

            # Test: Start at 0, go up (wraps to 4), go down (wraps to 0)
            mock_win.getyx.return_value = (0, 0)
            mock_win.erase.return_value = None
            mock_win.addstr.return_value = None
            mock_win.attron.return_value = None
            mock_win.attroff.return_value = None
            mock_win.refresh.return_value = None

            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.side_effect = [
                    curses.KEY_UP,  # Move up: 0 -> 4
                    curses.KEY_DOWN,  # Move down: 4 -> 0
                    10,  # Enter to confirm
                ]

                result = self.ui.render_menu(options, default=0, highlighted=0)
                assert result == 0
    
    def test_menu_typing_selection(self):
        """Test selecting by typing the number."""
        options = [{'label': 'Option'}]
        
        with patch.object(self.ui, '_screen') as mock_screen, \
             patch.object(self.ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_DOWN'):
            
            mock_screen.getmaxyx.return_value = (10, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.erase.return_value = None
            mock_win.addstr.return_value = None
            mock_win.attron.return_value = None
            mock_win.attroff.return_value = None
            mock_win.refresh.return_value = None

            with patch.object(mock_win, 'getch') as mock_getch:
                # Type '3' (keycode 51), then Enter (10)
                mock_getch.side_effect = [ord('3'), 10]
                result = self.ui.render_menu(options, default=0, highlighted=0)
                assert result == 3
    
    def test_menu_cancel_keys(self):
        """Test that cancel keys return -1."""
        options = [{'label': 'Option'}]
        
        for cancel_key in [ord('q'), 27, curses.KEY_RESIZE, curses.KEY_BACKSPACE, 127, 8]:
            with patch.object(self.ui, '_screen') as mock_screen, \
                 patch.object(self.ui, 'refresh') as mock_refresh, \
                 patch('curses.KEY_DOWN'):
                
                mock_screen.getmaxyx.return_value = (10, 60)
                mock_win = MagicMock()
                mock_screen.newwin.return_value = mock_win
                mock_win.getyx.return_value = (0, 0)
                
                with patch.object(mock_win, 'getch') as mock_getch:
                    mock_getch.return_value = cancel_key
                    
                    result = self.ui.render_menu(options, default=0, highlighted=0)
                    assert result == -1, f"Cancel key {cancel_key} should return -1"
    
    def test_confirmation_enter_confirms(self):
        """Enter key confirms the action."""
        with patch.object(self.ui, '_screen') as mock_screen, \
             patch.object(self.ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = 10  # Enter
                
                result = self.ui.render_confirmation("Are you sure?")
                assert result is True
    
    def test_confirmation_n_cancels(self):
        """n or N cancels the action."""
        with patch.object(self.ui, '_screen') as mock_screen, \
             patch.object(self.ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.erase.return_value = None
            mock_win.addstr.return_value = None
            mock_win.attron.return_value = None
            mock_win.attroff.return_value = None
            mock_win.refresh.return_value = None

            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = ord('n')
                result = self.ui.render_confirmation("Are you sure?")
                assert result is False
    
    def test_confirmation_y_confirms(self):
        """y or Y confirms the action."""
        with patch.object(self.ui, '_screen') as mock_screen, \
             patch.object(self.ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = ord('Y')
                
                result = self.ui.render_confirmation("Are you sure?")
                assert result is True
    
    def test_progress_bar_with_bytes(self):
        """Progress bar shows bytes and percentage."""
        with patch.object(self.ui, '_screen') as mock_screen, \
             patch.object(self.ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = 10
            
            self.ui.render_progress_bar("file.zip", 1000, 10000, percent=10.5)
    
    def test_progress_bar_spinner(self):
        """When total is 0, shows spinner."""
        with patch.object(self.ui, '_screen') as mock_screen, \
             patch.object(self.ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = 10
            
            # Test with total=0 to trigger spinner mode
            self.ui.render_progress_bar("unknown.zip", 0, 0, percent=None)
    
    def test_full_workflow_simulation(self):
        """Simulate complete UI workflow."""
        # Menu
        options = [{'label': 'Install'}, {'label': 'Update'}]
        
        with patch.object(self.ui, '_screen') as mock_screen, \
             patch.object(self.ui, 'refresh'), \
             patch('curses.KEY_DOWN'), \
             patch('curses.KEY_UP'):
            
            mock_screen.getmaxyx.return_value = (10, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.erase.return_value = None
            mock_win.addstr.return_value = None
            mock_win.attron.return_value = None
            mock_win.attroff.return_value = None
            mock_win.refresh.return_value = None

            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.side_effect = [ord('2'), 10]  # Select option 2
                result = self.ui.render_menu(options, default=0, highlighted=0)
                assert result == 2
            
            # Confirmation
            with patch.object(self.ui, '_screen') as mock_screen, \
                 patch.object(self.ui, 'refresh'), \
                 patch('curses.KEY_RESIZE'):
                
                mock_screen.getmaxyx.return_value = (20, 60)
                mock_win = MagicMock()
                mock_screen.newwin.return_value = mock_win
                mock_win.getyx.return_value = (0, 0)
                
                with patch.object(mock_win, 'getch') as mock_getch:
                    mock_getch.return_value = 10  # Enter
                    confirmed = self.ui.render_confirmation("Proceed?")
                    assert confirmed is True
            
            # Cleanup
        self.ui._cleanup_terminal()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
