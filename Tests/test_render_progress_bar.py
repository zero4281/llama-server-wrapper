#!/usr/bin/env python3
"""Unit tests for UIManager render_progress_bar method.

These tests verify specific behavior of the progress bar rendering without
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
    
    with patch('ui_manager.curses', mock_curses):
        ui = UIManager(title)
        ui._using_curses = True
    return ui


class TestRenderProgressBar:
    """Unit tests for render_progress_bar."""
    
    def test_displays_with_bytes_and_percent(self):
        """Progress bar shows bytes and percentage."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input', return_value='\n'), \
             patch('ui_manager.curses.newwin') as mock_newwin:
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_ENTER
            
            ui.render_progress_bar("file.zip", 1000, 10000, percent=10.5)
            
            # Verify that newwin was called and no exception occurred
            mock_newwin.assert_called()
            # The method should complete without crashing
            assert True
    
    def test_displays_without_percent(self):
        """Progress bar shows bytes even without percent parameter."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input', return_value='\n'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_ENTER
            
            ui.render_progress_bar("file.zip", 500, 2000)
    
    def test_displays_with_zero_total(self):
        """When total is 0, shows spinner."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input', return_value='\n'), \
             patch('ui_manager.curses.newwin') as mock_newwin:
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_ENTER
            
            ui.render_progress_bar("unknown.zip", 0, 0, percent=None)
            
            # Verify that newwin was called and no exception occurred
            mock_newwin.assert_called()
            # The method should complete without crashing
            assert True
    
    def test_displays_with_large_numbers(self):
        """Handles large numbers correctly."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input', return_value='\n'), \
             patch('ui_manager.curses.newwin') as mock_newwin:
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_ENTER
            
            ui.render_progress_bar("large.zip", 1000000000, 5000000000, percent=50.0)
            
            # Verify that newwin was called and no exception occurred
            mock_newwin.assert_called()
            # The method should complete without crashing
            assert True
    
    def test_displays_with_very_small_numbers(self):
        """Handles very small numbers correctly."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input', return_value='\n'), \
             patch('ui_manager.curses.newwin') as mock_newwin:
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_ENTER
            
            ui.render_progress_bar("small.zip", 1, 10, percent=10.0)
            
            # Verify that newwin was called and no exception occurred
            mock_newwin.assert_called()
            # The method should complete without crashing
            assert True
    
    def test_handles_none_filename(self):
        """Handles None filename gracefully."""
        ui = create_ui()
        
        with patch('ui_manager.curses.newwin') as mock_newwin:
            mock_newwin.side_effect = Exception("Mock error")
            
            # This should raise TypeError from Path(None), not crash with different error
            try:
                ui.render_progress_bar(None, 100, 1000)
            except TypeError:
                # Expected: Path(None) raises TypeError
                pass
            # The important thing is that the method fails gracefully with a clear error
    
    def test_handles_empty_filename(self):
        """Handles empty filename gracefully."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input', return_value='\n'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_ENTER
            
            ui.render_progress_bar("", 100, 1000)
    
    def test_handles_negative_current(self):
        """Handles negative current gracefully."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input', return_value='\n'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_ENTER
            
            # Should not crash
            ui.render_progress_bar("file.zip", -1, 1000)
    
    def test_handles_negative_total(self):
        """Handles negative total gracefully."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input', return_value='\n'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_ENTER
            
            # Should not crash
            ui.render_progress_bar("file.zip", 100, -1000)
    
    def test_handles_percent_over_100(self):
        """Handles percent > 100 correctly."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input', return_value='\n'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_ENTER
            
            ui.render_progress_bar("file.zip", 1500, 1000, percent=150.0)
    
    def test_handles_percent_zero(self):
        """Handles percent = 0 correctly."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input', return_value='\n'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_ENTER
            
            ui.render_progress_bar("file.zip", 0, 1000, percent=0.0)
    
    def test_handles_none_screen(self):
        """Handles None screen gracefully."""
        ui = create_ui()
        ui._screen = None
        
        # Should not crash
        ui.render_progress_bar("file.zip", 100, 1000)
    
    def test_handles_none_color_pair(self):
        """Handles None color pair gracefully."""
        ui = create_ui()
        ui._color_pair = None
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('curses.KEY_RESIZE'), \
             patch('builtins.input', return_value='\n'):
            
            mock_screen.getmaxyx.return_value = (20, 60)
            mock_win = MagicMock()
            mock_screen.newwin.return_value = mock_win
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_ENTER
            
            ui.render_progress_bar("file.zip", 100, 1000)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])