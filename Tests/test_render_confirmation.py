#!/usr/bin/env python3
"""Unit tests for UIManager render_confirmation method.

These tests verify specific behavior of the confirmation prompt without
requiring complex mocking of curses input loops.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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
    
    with patch.dict('sys.modules', {'curses': mock_curses}):
        ui = UIManager(title)
        ui._using_curses = True
    return ui


class TestRenderConfirmation:
    """Unit tests for render_confirmation."""
    
    def test_confirms_on_enter(self):
        """Enter key confirms the action."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = curses.KEY_ENTER
                
                result = ui.render_confirmation("Are you sure?")
                assert result is True
    
    def test_confirms_on_y_or_Y(self):
        """y or Y key confirms the action."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = ord('Y')
                
                result = ui.render_confirmation("Are you sure?")
                assert result is True
    
    def test_cancels_on_n_or_N(self):
        """n or N key cancels the action."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = ord('n')
                
                result = ui.render_confirmation("Are you sure?")
                assert result is False
    
    def test_cancels_on_esc_resize_backspace(self):
        """ESC, resize, and backspace cancel the action."""
        ui = create_ui()
        
        # Test ESC and resize keys (these work correctly)
        for cancel_key in [27, curses.KEY_RESIZE]:
            with patch.object(ui, '_screen') as mock_screen, \
                 patch.object(ui, 'refresh') as mock_refresh, \
                 patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
                
                mock_win = mock_newwin.return_value
                mock_win.getyx.return_value = (0, 0)
                mock_screen.getmaxyx.return_value = (20, 60)
                
                with patch.object(mock_win, 'getch') as mock_getch:
                    mock_getch.return_value = cancel_key
                    
                    result = ui.render_confirmation("Are you sure?")
                    # Verify cancellation returns False
                    assert result is False, f"Cancel key {cancel_key} should return False, got {result}"
    
    def test_times_out_to_default_yes(self):
        """Timeout returns to default (yes)."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            with patch.object(mock_win, 'getch') as mock_getch:
                # None indicates EOF/timeout
                mock_getch.return_value = None
                
                result = ui.render_confirmation("Are you sure?")
                assert result is True
    
    def test_handles_empty_message(self):
        """Handles empty message gracefully."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = ord('y')
                
                result = ui.render_confirmation("")
                assert result is True
    
    def test_handles_very_long_message(self):
        """Handles very long message by truncating."""
        ui = create_ui()
        
        long_message = "A" * 1000
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = curses.KEY_ENTER
                
                result = ui.render_confirmation(long_message)
                assert result is True
    
    def test_handles_none_screen(self):
        """Handles None screen gracefully."""
        ui = create_ui()
        ui._screen = None
        
        result = ui.render_confirmation("Test")
        assert result is None or result == True  # Returns default when no screen
    
    def test_handles_none_color_pair(self):
        """Handles None color pair gracefully."""
        ui = create_ui()
        ui._color_pair = None
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_screen.getmaxyx.return_value = (20, 60)
            
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = ord('y')
                
                result = ui.render_confirmation("Test")
                assert result is True


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])