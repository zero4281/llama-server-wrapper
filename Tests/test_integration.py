#!/usr/bin/env python3
"""Integration tests for UIManager end-to-end flows."""

import curses
import pytest
from unittest.mock import MagicMock, patch


class TestIntegrationFlows:
    """Integration tests for cross-method flows."""

    def test_tag_asset_selection_flow(self, ui, mock_win):
        """Full flow: select tag, select asset, confirm."""
        options = [
            {'label': 'Tag A'},
            {'label': 'Tag B'},
            {'label': 'Tag C'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            # Step 1: Select Tag B (index 1)
            mock_win.getch.return_value = 1  # Direct number input
            tag_idx = ui.render_menu(options)
            assert tag_idx == 1

            # Step 2: Select Asset B (index 1)
            mock_win.getch.return_value = 1
            asset_idx = ui.render_menu([{'label': 'Asset B'}])
            assert asset_idx == 1

            # Step 3: Confirm selection
            mock_win.getch.return_value = curses.KEY_ENTER
            confirmed = ui.render_confirmation("Proceed with selection?", default=True)
            assert confirmed is True

    def test_cancel_at_tag_selection(self, ui, mock_win):
        """Cancel at tag selection prevents further flow."""
        options = [{'label': 'Tag A'}, {'label': 'Tag B'}]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = curses.KEY_RESIZE  # Cancel key
            tag_idx = ui.render_menu(options)
            assert tag_idx == -1

    def test_cancel_at_asset_selection(self, ui, mock_win):
        """Cancel at asset selection stops the flow."""
        options = [{'label': 'Asset A'}, {'label': 'Asset B'}]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = ord('q')  # Cancel key
            asset_idx = ui.render_menu(options)
            assert asset_idx == -1

    def test_timeout_at_confirmation(self, ui, mock_win):
        """Timeout at confirmation proceeds with default."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = -1  # Timeout
            confirmed = ui.render_confirmation("Proceed?", default=True)
            assert confirmed is True

    def test_timeout_at_confirmation_default_false(self, ui, mock_win):
        """Timeout at confirmation with default=False returns False."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = -1  # Timeout
            confirmed = ui.render_confirmation("Proceed?", default=False)
            assert confirmed is False

    def test_full_flow_with_navigation(self, ui, mock_win):
        """Full flow with arrow key navigation."""
        options = [
            {'label': 'Option A', 'description': 'First option'},
            {'label': 'Option B', 'description': 'Second option'},
            {'label': 'Option C', 'description': 'Third option'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            # Navigate with arrow keys: down, down, Enter
            mock_win.getch.side_effect = [
                curses.KEY_DOWN,  # Move to Option B
                curses.KEY_DOWN,  # Move to Option C
                curses.KEY_ENTER  # Select Option C
            ]

            selected = ui.render_menu(options)
            assert selected == 2

    def test_full_flow_with_page_navigation(self, ui, mock_win):
        """Full flow with page navigation keys."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'},
            {'label': 'Option C'},
            {'label': 'Option D'},
            {'label': 'Option E'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            # Page up: moves to Option D (page_size=2)
            mock_win.getch.return_value = curses.KEY_PPAGE

            selected = ui.render_menu(options)
            # Should return -1 on page navigation (no selection made)
            assert selected == -1

    def test_full_flow_with_number_selection(self, ui, mock_win):
        """Full flow with direct number selection."""
        options = [
            {'label': 'Option A'},
            {'label': 'Option B'},
            {'label': 'Option C'}
        ]

        with patch('ui_manager.curses.newwin', return_value=mock_win):
            # Direct selection: type '2' then Enter
            mock_win.getch.side_effect = [ord('2'), curses.KEY_ENTER]

            selected = ui.render_menu(options)
            assert selected == 2

    def test_full_flow_with_cancel_multiple_ways(self, ui, mock_win):
        """Test various cancel keys in a flow."""
        options = [{'label': 'Option A'}, {'label': 'Option B'}]

        for cancel_key in [27, ord('q'), curses.KEY_RESIZE, curses.KEY_BACKSPACE, 127, 8]:
            mock_win.getch.return_value = cancel_key
            selected = ui.render_menu(options)
            assert selected == -1


class TestEdgeCaseIntegration:
    """Integration tests for edge cases."""

    def test_empty_options_list(self, ui, mock_win):
        """Empty options list returns -1."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = curses.KEY_ENTER
            selected = ui.render_menu([])
            assert selected == -1

    def test_single_option(self, ui, mock_win):
        """Single option can be selected."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.return_value = curses.KEY_ENTER
            selected = ui.render_menu([{'label': 'Only Option'}])
            assert selected == 0

    def test_number_out_of_range(self, ui, mock_win):
        """Number input out of range returns -1."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            mock_win.getch.side_effect = [ord('9'), curses.KEY_ENTER]
            selected = ui.render_menu([{'label': 'Option A'}])
            assert selected == -1

    def test_confirmation_default_parameter(self, ui, mock_win):
        """Confirmation respects default parameter."""
        with patch('ui_manager.curses.newwin', return_value=mock_win):
            # Test with default=True
            mock_win.getch.return_value = -1
            result1 = ui.render_confirmation("Proceed?", default=True)
            assert result1 is True

            # Test with default=False
            mock_win.getch.return_value = -1
            result2 = ui.render_confirmation("Proceed?", default=False)
            assert result2 is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
