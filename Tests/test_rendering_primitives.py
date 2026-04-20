#!/usr/bin/env python3
"""Tests for rendering primitives in UIManager."""

import curses
import pytest
from unittest.mock import MagicMock, patch


class TestPrintHeader:
    """Tests for UIManager.print_header."""

    def test_print_header_no_curses(self, ui, capsys):
        """print_header displays formatted text when curses is disabled."""
        ui._using_curses = False
        ui.print_header("Test Header")
        captured = capsys.readouterr()
        assert "Test Header" in captured.out
        assert "=" in captured.out

    def test_print_header_with_curses(self, ui, mock_curses, capsys):
        """print_header calls screen methods when curses is enabled."""
        with patch('ui_manager.curses.newwin', return_value=mock_curses.screen):
            ui.print_header("Test Header")
            mock_curses.screen.attron.assert_called()
            mock_curses.screen.addstr.assert_called()
            mock_curses.screen.attroff.assert_called()
            mock_curses.screen.refresh.assert_called()

    def test_print_header_no_screen_returns_early(self, ui, capsys):
        """print_header returns early when screen is None."""
        ui._using_curses = True
        ui._screen = None
        ui.print_header("Test Header")
        # Should not print anything when screen is None
        captured = capsys.readouterr()
        assert captured.out == ""


class TestPrintMessage:
    """Tests for UIManager.print_message."""

    def test_print_message_no_curses(self, ui, capsys):
        """print_message prints text when curses is disabled."""
        ui._using_curses = False
        ui.print_message("Test message")
        captured = capsys.readouterr()
        assert "Test message" in captured.out

    def test_print_message_with_curses(self, ui, mock_curses, capsys):
        """print_message places text at specified coordinates."""
        with patch('ui_manager.curses.newwin', return_value=mock_curses.screen):
            ui.print_message("Test message", y=1, x=2)
            mock_curses.screen.addstr.assert_called_with(1, 2, "Test message")

    def test_print_message_default_coordinates(self, ui, mock_curses):
        """print_message uses default coordinates (1, 1) when not specified."""
        with patch('ui_manager.curses.newwin', return_value=mock_curses.screen):
            ui.print_message("Test message")
            mock_curses.screen.addstr.assert_called_with(1, 1, "Test message")


class TestRenderSuccess:
    """Tests for UIManager.render_success."""

    def test_render_success_no_curses(self, ui, capsys):
        """render_success displays message when curses is disabled."""
        ui._using_curses = False
        ui.render_success("Operation completed successfully")
        captured = capsys.readouterr()
        assert "Operation completed successfully" in captured.out

    def test_render_success_with_curses(self, ui, mock_win, capsys):
        """render_success creates window and displays message."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            ui.render_success("Operation completed successfully")
            mock_win.addstr.assert_any_call(0, 1, "Success".center(mock_win.getmaxx() - 4))
            mock_win.addstr.assert_any_call(2, 2, "Operation completed successfully")
            mock_win.refresh.assert_called()

    def test_render_success_fallback_on_error(self, ui, capsys):
        """render_success falls back to console on curses error."""
        ui._using_curses = True
        ui._screen = None
        ui.render_success("Operation completed successfully")
        captured = capsys.readouterr()
        assert "Operation completed successfully" in captured.out


class TestRenderError:
    """Tests for UIManager.render_error."""

    def test_render_error_no_curses(self, ui, capsys):
        """render_error displays error message when curses is disabled."""
        ui._using_curses = False
        ui.render_error("Something went wrong")
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "Something went wrong" in captured.out

    def test_render_error_with_curses(self, ui, mock_curses):
        """render_error creates window and displays error."""
        with patch('ui_manager.curses.newwin', return_value=mock_curses.screen):
            ui.render_error("Something went wrong")
            mock_curses.screen.attron.assert_called()
            # Verify that addstr was called (exact string check is complex due to centering)
            mock_curses.screen.addstr.assert_called()
            mock_curses.screen.refresh.assert_called()

    def test_render_error_fallback_on_error(self, ui, capsys):
        """render_error falls back to console on curses error."""
        ui._using_curses = True
        ui._screen = None
        ui.render_error("Something went wrong")
        captured = capsys.readouterr()
        assert "Error: Something went wrong" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
