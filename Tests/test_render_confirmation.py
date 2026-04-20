#!/usr/bin/env python3
"""Tests for UIManager.render_confirmation method."""

import curses
import pytest
from unittest.mock import MagicMock, patch


class TestRenderConfirmation:
    """Tests for UIManager.render_confirmation."""

    def test_confirmation_confirm_enter(self, ui, mock_win):
        """Confirmation returns True when Enter is pressed."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = curses.KEY_ENTER
            result = ui.render_confirmation("Proceed?", default=True)
            assert result is True

    def test_confirmation_confirm_y_key(self, ui, mock_win):
        """Confirmation returns True when 'y' is pressed."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = ord('y')
            result = ui.render_confirmation("Proceed?", default=True)
            assert result is True

    def test_confirmation_confirm_Y_key(self, ui, mock_win):
        """Confirmation returns True when 'Y' is pressed."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = ord('Y')
            result = ui.render_confirmation("Proceed?", default=True)
            assert result is True

    def test_confirmation_cancel_n_key(self, ui, mock_win):
        """Confirmation returns False when 'n' is pressed."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = ord('n')
            result = ui.render_confirmation("Proceed?", default=True)
            assert result is False

    def test_confirmation_cancel_N_key(self, ui, mock_win):
        """Confirmation returns False when 'N' is pressed."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = ord('N')
            result = ui.render_confirmation("Proceed?", default=True)
            assert result is False

    def test_confirmation_cancel_esc(self, ui, mock_win):
        """Confirmation returns False when Escape is pressed."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = 27
            result = ui.render_confirmation("Proceed?", default=True)
            assert result is False

    def test_confirmation_cancel_resize(self, ui, mock_win):
        """Confirmation returns False when KEY_RESIZE is pressed."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = curses.KEY_RESIZE
            result = ui.render_confirmation("Proceed?", default=True)
            assert result is False

    def test_confirmation_timeout_returns_default_true(self, ui, mock_win):
        """Confirmation returns default (True) on timeout."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = -1
            result = ui.render_confirmation("Proceed?", default=True)
            assert result is True

    def test_confirmation_timeout_returns_default_false(self, ui, mock_win):
        """Confirmation returns default (False) on timeout."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = -1
            result = ui.render_confirmation("Proceed?", default=False)
            assert result is False

    def test_confirmation_no_screen_returns_default(self, ui, mock_win):
        """Confirmation returns default when screen is None."""
        ui._screen = None
        result = ui.render_confirmation("Proceed?", default=True)
        assert result is True

    def test_confirmation_fallback_console(self, ui, mock_win, capsys):
        """Confirmation falls back to console on curses error."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            ui._using_curses = True
            ui._screen = None
            result = ui.render_confirmation("Proceed?", default=True)
            assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
