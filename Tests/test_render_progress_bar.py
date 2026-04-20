#!/usr/bin/env python3
"""Tests for UIManager.render_progress_bar method."""

import curses
import pytest
from unittest.mock import MagicMock, patch


class TestRenderProgressBar:
    """Tests for UIManager.render_progress_bar."""

    def test_progress_bar_determinate_100(self, ui, mock_win):
        """Progress bar shows 100% when complete."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            ui.render_progress_bar("test.txt", 1000, 1000, percent=100.0)
            mock_win.addstr.assert_any_call(
                2, 0, "1,000/1,000 bytes (100.0% - 1.0MB/1.0MB)"
            )

    def test_progress_bar_determinate_50(self, ui, mock_win):
        """Progress bar shows 50% progress."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            ui.render_progress_bar("test.txt", 500, 1000, percent=50.0)
            mock_win.addstr.assert_any_call(
                2, 0, "500/1,000 bytes (50.0% - 0.5MB/1.0MB)"
            )

    def test_progress_bar_determinate_0(self, ui, mock_win):
        """Progress bar shows 0% progress."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            ui.render_progress_bar("test.txt", 0, 1000, percent=0.0)
            mock_win.addstr.assert_any_call(
                2, 0, "0/1,000 bytes (0.0% - 0.0MB/1.0MB)"
            )

    def test_progress_bar_indeterminate(self, ui, mock_win):
        """Progress bar shows spinner when total is 0."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            ui.render_progress_bar("test.txt", 500, 0)
            mock_win.addstr.assert_any_call(
                2, 0, "Downloading test.txt... (◐)"
            )

    def test_progress_bar_no_curses(self, ui, capsys):
        """Progress bar falls back to console when curses is disabled."""
        ui._using_curses = False
        ui.render_progress_bar("test.txt", 500, 1000, percent=50.0)
        captured = capsys.readouterr()
        assert "test.txt" in captured.out
        assert "500/1000" in captured.out

    def test_progress_bar_no_screen(self, ui, mock_win):
        """Progress bar returns early when screen is None."""
        ui._screen = None
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            ui.render_progress_bar("test.txt", 500, 1000)
            mock_win.addstr.assert_not_called()

    def test_progress_bar_fallback_on_error(self, ui, mock_win, capsys):
        """Progress bar falls back to console on curses error."""
        ui._using_curses = True
        ui._screen = None
        ui.render_progress_bar("test.txt", 500, 1000)
        captured = capsys.readouterr()
        assert "test.txt" in captured.out

    def test_progress_bar_wait_for_key(self, ui, mock_win, capsys):
        """Progress bar waits for key press."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = curses.KEY_ENTER
            ui.render_progress_bar("test.txt", 500, 1000)
            mock_win.getch.assert_called()

    def test_progress_bar_multiple_keys(self, ui, mock_win, capsys):
        """Progress bar handles multiple key inputs."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.side_effect = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_ENTER]
            ui.render_progress_bar("test.txt", 500, 1000)
            mock_win.getch.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
