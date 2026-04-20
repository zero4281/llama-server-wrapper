#!/usr/bin/env python3
"""Tests for UIManager initialization and lifecycle."""

import curses
import pytest
from unittest.mock import MagicMock, patch


class TestUIManagerInit:
    """Tests for UIManager.__init__ method."""

    def test_init_with_curses_success(self, mock_curses):
        """UIManager initializes with curses when available."""
        with patch('ui_manager.curses', mock_curses):
            from ui_manager import UIManager
            ui = UIManager("Test Title")
            assert ui._using_curses is True
            assert ui._initialized is True
            assert ui._title == "Test Title"
            assert ui._color_pair is not None

    def test_init_with_curses_failure(self):
        """UIManager falls back to False when curses fails."""
        # Use a mock that raises on initscr but has valid error class
        failing_curses = MagicMock()
        failing_curses.initscr.side_effect = OSError("Curses not available")
        # Preserve the real curses.error class
        failing_curses.error = curses.error

        with patch('ui_manager.curses', failing_curses):
            from ui_manager import UIManager
            ui = UIManager("Test Title")
            assert ui._using_curses is False
            assert ui._initialized is False
            assert ui._screen is None
            assert ui._color_pair is None

    def test_init_default_title(self):
        """UIManager uses default title when none provided."""
        with patch('ui_manager.curses', MagicMock()):
            from ui_manager import UIManager
            ui = UIManager()
            assert ui._title == "Llama Server Wrapper"


class TestCleanupTerminal:
    """Tests for UIManager._cleanup_terminal method."""

    def test_cleanup_when_using_curses(self, mock_curses):
        """_cleanup_terminal calls restore when curses is enabled."""
        with patch('ui_manager.UIManager._restore_terminal_state') as mock_restore:
            from ui_manager import UIManager
            ui = UIManager("Test")
            ui._using_curses = True
            ui._screen = MagicMock()

            ui._cleanup_terminal()

            mock_restore.assert_called()
            ui._using_curses = False

    def test_cleanup_when_not_using_curses(self, mock_curses):
        """_cleanup_terminal resets state when curses is disabled."""
        with patch('ui_manager.curses', mock_curses):
            from ui_manager import UIManager
            ui = UIManager("Test")
            ui._using_curses = False
            ui._screen = None

            ui._cleanup_terminal()

            assert ui._screen is None
            assert ui._color_pair is None
            assert ui._using_curses is False


class TestInitAndCleanupIntegration:
    """Integration tests for init and cleanup."""

    def test_init_then_cleanup(self, mock_curses):
        """UIManager can be initialized and then cleaned up."""
        with patch('ui_manager.curses', mock_curses):
            from ui_manager import UIManager
            ui = UIManager("Test")

            assert ui._using_curses is True
            assert ui._initialized is True

            ui._cleanup_terminal()

            assert ui._using_curses is False
            assert ui._initialized is False

    def test_multiple_cleanup_calls(self, mock_curses):
        """Multiple cleanup calls are safe."""
        with patch('ui_manager.UIManager._restore_terminal_state') as mock_restore:
            from ui_manager import UIManager
            ui = UIManager("Test")
            ui._using_curses = True
            ui._screen = MagicMock()

            ui._cleanup_terminal()
            ui._cleanup_terminal()
            ui._cleanup_terminal()

            mock_restore.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
