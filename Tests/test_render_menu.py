#!/usr/bin/env python3
"""Tests for UIManager.render_menu method."""

import curses
import pytest
from unittest.mock import MagicMock, patch


class TestArrowNavigation:
    """Tests for arrow key navigation."""

    def test_arrow_key_navigation_up_down(self, ui, mock_win):
        """Arrow keys navigate menu options."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'},
            {'label': 'Option C'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.side_effect = [
                curses.KEY_DOWN,  # Move to Option B
                curses.KEY_UP     # Move back to Option A
            ]

            selected = ui.render_menu(options)
            assert selected == -1  # No selection, just navigation

    def test_arrow_key_navigation_wrap(self, ui, mock_win):
        """Arrow key navigation wraps around."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'},
            {'label': 'Option C'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            # UP from Option A should wrap to Option C
            mock_win.getch.side_effect = [curses.KEY_UP, curses.KEY_ENTER]

            selected = ui.render_menu(options)
            assert selected == 2

    def test_page_up_page_down_navigation(self, ui, mock_win):
        """Page up/down keys jump through menu."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'},
            {'label': 'Option C'},
            {'label': 'Option D'},
            {'label': 'Option E'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            # PAGE_UP moves up by page size
            mock_win.getch.side_effect = [curses.KEY_PPAGE, curses.KEY_ENTER]

            selected = ui.render_menu(options)
            assert selected == -1


class TestNumberInput:
    """Tests for number input selection."""

    def test_single_digit_selects_directly(self, ui, mock_win):
        """Single digit directly selects option."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'},
            {'label': 'Option C'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.side_effect = [ord('2'), curses.KEY_ENTER]

            selected = ui.render_menu(options)
            assert selected == 2

    def test_out_of_range_digit_ignored(self, ui, mock_win):
        """Out of range digit is ignored."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.side_effect = [ord('9'), curses.KEY_ENTER]

            selected = ui.render_menu(options)
            assert selected == -1

    def test_multiple_digits_first_selected(self, ui, mock_win):
        """Multiple digits: first valid digit selected."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'},
            {'label': 'Option C'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            # '3' is out of range, '1' is valid
            mock_win.getch.side_effect = [ord('3'), ord('1'), curses.KEY_ENTER]

            selected = ui.render_menu(options)
            assert selected == 1


class TestEnterConfirmation:
    """Tests for Enter key confirmation."""

    def test_enter_confirms_selection(self, ui, mock_win):
        """Enter key confirms current selection."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'},
            {'label': 'Option C'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            # Navigate to Option B, then Enter
            mock_win.getch.side_effect = [
                curses.KEY_DOWN,  # Move to Option B
                curses.KEY_DOWN,  # Move to Option C
                curses.KEY_ENTER  # Confirm Option C
            ]

            selected = ui.render_menu(options)
            assert selected == 2

    def test_enter_with_various_key_codes(self, ui, mock_win):
        """Enter confirms with various key codes."""
        options = [{'label': 'Option A'}]

        for enter_key in [curses.KEY_ENTER, 10, 13]:
            with patch('ui_manager.curses.newwin', return_value=mock_win):
                mock_win.getch.return_value = enter_key
                selected = ui.render_menu(options)
                assert selected == 0


class TestCancelKeys:
    """Tests for cancel key handling."""

    def test_cancel_keys_return_minus_one(self, ui, mock_win):
        """All cancel keys return -1."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'}
        ]

        cancel_keys = [
            27,           # Escape
            ord('q'),     # 'q'
            curses.KEY_RESIZE,
            curses.KEY_BACKSPACE,
            127,          # DEL
            8             # Backspace
        ]

        for cancel_key in cancel_keys:
            with patch('ui_manager.curses.newwin', return_value=mock_win):
                mock_win.getch.return_value = cancel_key
                selected = ui.render_menu(options)
                assert selected == -1


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_options_list(self, ui, mock_win):
        """Empty options list returns -1."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = curses.KEY_ENTER
            selected = ui.render_menu([])
            assert selected == -1

    def test_single_option(self, ui, mock_win):
        """Single option returns 0 on selection."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = curses.KEY_ENTER
            selected = ui.render_menu([{'label': 'Only Option'}])
            assert selected == 0

    def test_default_option_displayed(self, ui, mock_win, capsys):
        """Default option is marked with '(default)' in menu."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'},
            {'label': 'Option C'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            ui.render_menu(options, default=1)
            mock_win.addstr.assert_any_call(
                3, 0, "  1. Option B (default)"
            )

    def test_highlighted_option_displayed(self, ui, mock_win, capsys):
        """Highlighted option is shown with reverse video."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'},
            {'label': 'Option C'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            ui.render_menu(options, highlighted=2)
            # Verify highlight attribute is used
            mock_win.attron.assert_any_call(
                ui._color_pair | curses.A_BOLD | curses.A_REVERSE
            )


class TestTerminalSizing:
    """Tests for different terminal sizes."""

    def test_small_terminal(self, ui, mock_win):
        """Menu works on small terminal (40x20)."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getmaxyx.return_value = (20, 40)
            options = [
                {'label': 'Option A'},
                {'label': 'Option B'}
            ]
            selected = ui.render_menu(options)
            assert selected == -1

    def test_standard_terminal(self, ui, mock_win):
        """Menu works on standard terminal (80x24)."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getmaxyx.return_value = (24, 80)
            options = [
                {'label': 'Option A'},
                {'label': 'Option B'}
            ]
            selected = ui.render_menu(options)
            assert selected == -1

    def test_large_terminal(self, ui, mock_win):
        """Menu works on large terminal (120x30)."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getmaxyx.return_value = (30, 120)
            options = [
                {'label': 'Option A'},
                {'label': 'Option B'}
            ]
            selected = ui.render_menu(options)
            assert selected == -1


class TestValidation:
    """Tests for input validation."""

    def test_negative_number_ignored(self, ui, mock_win):
        """Negative numbers are ignored."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.side_effect = [ord('-'), curses.KEY_ENTER]
            selected = ui.render_menu(options)
            assert selected == -1

    def test_non_numeric_character_ignored(self, ui, mock_win):
        """Non-numeric characters are ignored."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.side_effect = [ord('a'), curses.KEY_ENTER]
            selected = ui.render_menu(options)
            assert selected == -1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
