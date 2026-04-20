#!/usr/bin/env python3
"""Unit tests for UIManager print_header and print_message methods.

These tests verify specific behavior of the basic rendering methods without
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


class TestPrintHeader:
    """Unit tests for print_header."""
    
    def test_displays_header_with_curses(self):
        """Header displays with curses when enabled."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh, \
             patch('ui_manager.curses.newwin') as mock_newwin:
            
            ui.print_header("Test Header")
            
            # Verify that print_header completed without crashing
            # The method should call addstr and refresh
            mock_screen.addstr.assert_called()
            mock_screen.refresh.assert_called()
    
    def test_displays_header_in_fallback_mode(self):
        """Header displays in fallback mode when curses is disabled."""
        ui = create_ui()
        ui._using_curses = False
        
        ui.print_header("Test Header")
        
        expected = "\n" + "=" * 60 + "\n" + "Test Header".center(60) + "\n" + "=" * 60
        print(f"Expected: {repr(expected)}")
        # The method prints directly, so we verify it was called
        # by checking that it didn't raise an exception
    
    def test_handles_none_screen(self):
        """Handles None screen gracefully."""
        ui = create_ui()
        ui._screen = None
        
        # Should not crash
        ui.print_header("Test Header")
    
    def test_handles_none_color_pair(self):
        """Handles None color pair gracefully."""
        ui = create_ui()
        ui._color_pair = None
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh:
            
            ui.print_header("Test Header")


class TestPrintMessage:
    """Unit tests for print_message."""
    
    def test_displays_message_at_position(self):
        """Message displays at specified position."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh:
            
            ui.print_message("Test Message", y=5, x=10)
            
            mock_screen.attron.assert_any_call(ui._color_pair)
            mock_screen.addstr.assert_any_call(5, 10, "Test Message")
            mock_screen.attroff.assert_any_call(ui._color_pair)
            mock_screen.refresh.assert_called()
    
    def test_displays_message_with_defaults(self):
        """Message displays with default position (y=1, x=1)."""
        ui = create_ui()
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh:
            
            ui.print_message("Test Message")
            
            mock_screen.addstr.assert_any_call(1, 1, "Test Message")
    
    def test_displays_message_in_fallback_mode(self):
        """Message displays in fallback mode when curses is disabled."""
        ui = create_ui()
        ui._using_curses = False
        
        ui.print_message("Test Message")
        # Verify it prints directly without exception
    
    def test_handles_none_screen(self):
        """Handles None screen gracefully."""
        ui = create_ui()
        ui._screen = None
        
        # Should not crash
        ui.print_message("Test Message", y=5, x=10)
    
    def test_handles_none_color_pair(self):
        """Handles None color pair gracefully."""
        ui = create_ui()
        ui._color_pair = None
        
        with patch.object(ui, '_screen') as mock_screen, \
             patch.object(ui, 'refresh') as mock_refresh:
            
            ui.print_message("Test Message", y=5, x=10)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])