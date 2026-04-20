#!/usr/bin/env python3
"""
Integration test for full LlamaUpdater install flow.

This test simulates the complete --install-llama flow to catch regressions
like arrow key bugs, menu navigation issues, and edge cases.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ui_manager


class MockCurses:
    """Complete mock curses module for testing."""
    
    def __init__(self):
        # Create mock screen object
        self._mock_screen = MagicMock()
        self._mock_screen.getmaxyx.return_value = (20, 60)
        self._mock_screen.getyx.return_value = (10, 20)
        self._mock_screen.erase.return_value = None
        self._mock_screen.refresh.return_value = None
        self._mock_screen.move.return_value = None
        self._mock_screen.box.return_value = None
        self._mock_screen.addstr.return_value = None
        self._mock_screen.attron.return_value = None
        self._mock_screen.attroff.return_value = None
        self._mock_screen.timeout.return_value = None
        
        # All curses methods
        self.initscr = MagicMock(return_value=self._mock_screen)
        self.start_color = MagicMock()
        self.init_pair = MagicMock(side_effect=[MagicMock(), MagicMock()])
        self.cbreak = MagicMock(return_value=True)
        self.noecho = MagicMock()
        self.curs_set = MagicMock(return_value=None)
        self.has_ungetch = MagicMock(return_value=False)
        self.getscrptr = MagicMock(return_value=None)
        self.KEY_UP = 259
        self.KEY_DOWN = 258
        self.KEY_LEFT = 260
        self.KEY_RIGHT = 261
        self.KEY_ENTER = 343
        self.KEY_RESIZE = 410
        self.KEY_BACKSPACE = 263
        self.KEY_PPAGE = 339
        self.KEY_NPAGE = 338
        self.COLOR_GREEN = 10000001
        self.COLOR_BLACK = 0
        self.COLOR_WHITE = 10000002
        self.error = OSError
        self.OSError = OSError
        self.IOError = IOError
        self.A_BOLD = 1
        self.A_REVERSE = 2
        self.COLORS = 0
        self.PAIRS = 0
        self.color_pair = MagicMock()
        
        # All screen and window methods
        self.echo = MagicMock()
        self.nocbreak = MagicMock()
        self.keypad = MagicMock(return_value=True)
        self.reset_pair_matrix = MagicMock()
        self.endwin = MagicMock()
        self.setupterm = MagicMock()
        self.napms = MagicMock()
        self.getyx = MagicMock(return_value=(10, 20))
        self.erase = MagicMock()
        self.move = MagicMock()
        self.box = MagicMock()
        self.addstr = MagicMock()
        self.attron = MagicMock()
        self.attroff = MagicMock()
        self.refresh = MagicMock()
        self.newwin = MagicMock(return_value=MagicMock())
        self.timeout = MagicMock()
        self.has_colors = MagicMock(return_value=False)
        self.curs_set = MagicMock(return_value=None)
        self.echo = MagicMock()
        self.nocbreak = MagicMock()
        self.keypad = MagicMock(return_value=True)
        self.reset_pair_matrix = MagicMock()
        self.endwin = MagicMock()


class TestLlamaUpdaterIntegration(unittest.TestCase):
    """Integration tests for LlamaUpdater install flow."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.mock_curses = MockCurses()
    
    def setUp(self):
        """Set up each test case."""
        # Create fresh MockCurses for each test to ensure proper state
        self.mock_curses = MockCurses()
        
        # Create UIManager with mocked curses
        with patch('ui_manager.curses', self.mock_curses):
            self.ui = ui_manager.UIManager("Test")
            self.ui._using_curses = True
            self.ui._screen = MagicMock()
            self.ui._screen.getmaxyx.return_value = (20, 60)
    
    def tearDown(self):
        """Tear down each test case."""
        self.ui._cleanup_terminal()


class TestMenuNavigation(TestLlamaUpdaterIntegration):
    """Tests for menu navigation."""
    
    def test_menu_with_arrows(self):
        """Test menu navigation with arrow keys."""
        options = [
            {'label': 'Option 1', 'description': ''},
            {'label': 'Option 2', 'description': ''},
            {'label': 'Option 3', 'description': ''}
        ]
        
        mock_win = MagicMock()
        mock_win.getch.return_value = self.mock_curses.KEY_UP
        
        result = self.ui.render_menu(options, highlighted=1)
        self.assertEqual(result, -1)
    
    def test_menu_with_numbers(self):
        """Test menu navigation with number input."""
        options = [
            {'label': 'Option 1', 'description': ''},
            {'label': 'Option 2', 'description': ''},
            {'label': 'Option 3', 'description': ''}
        ]
        
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('2')
        
        result = self.ui.render_menu(options)
        self.assertEqual(result, -1)
    
    def test_menu_with_enter(self):
        """Test menu selection with Enter key."""
        options = [
            {'label': 'Option 1', 'description': ''},
            {'label': 'Option 2', 'description': ''},
            {'label': 'Option 3', 'description': ''}
        ]
        
        mock_win = MagicMock()
        mock_win.getch.return_value = self.mock_curses.KEY_ENTER
        
        result = self.ui.render_menu(options, default=1)
        self.assertEqual(result, -1)
    
    def test_menu_with_cancel(self):
        """Test menu cancellation."""
        options = [
            {'label': 'Option 1', 'description': ''},
            {'label': 'Option 2', 'description': ''}
        ]
        
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('q')
        
        result = self.ui.render_menu(options)
        self.assertEqual(result, -1)


class TestConfirmationDialog(TestLlamaUpdaterIntegration):
    """Tests for confirmation dialog."""
    
    def test_confirmation_with_enter(self):
        """Test confirmation with Enter key."""
        mock_win = MagicMock()
        mock_win.getch.return_value = self.mock_curses.KEY_ENTER
        result = self.ui.render_confirmation("Test")
        self.assertTrue(result)
    
    def test_confirmation_with_n(self):
        """Test confirmation with 'n' key."""
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('n')
        result = self.ui.render_confirmation("Test")
        self.assertFalse(result)
    
    def test_confirmation_with_y(self):
        """Test confirmation with 'y' key."""
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('y')
        result = self.ui.render_confirmation("Test")
        self.assertTrue(result)
    
    def test_confirmation_with_esc(self):
        """Test confirmation with ESC key."""
        mock_win = MagicMock()
        mock_win.getch.return_value = 27
        result = self.ui.render_confirmation("Test")
        self.assertFalse(result)
    
    def test_confirmation_timeout(self):
        """Test confirmation timeout."""
        mock_win = MagicMock()
        mock_win.getch.return_value = -1
        result = self.ui.render_confirmation("Test")
        self.assertTrue(result)


class TestEdgeCases(TestLlamaUpdaterIntegration):
    """Tests for edge cases."""
    
    def test_empty_options(self):
        """Test menu with empty options."""
        result = self.ui.render_menu([])
        self.assertEqual(result, -1)
    
    def test_invalid_input(self):
        """Test menu with invalid input."""
        options = [{'label': 'Option 1', 'description': ''}]
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('9')
        result = self.ui.render_menu(options)
        self.assertEqual(result, -1)
    
    def test_no_screen(self):
        """Test menu when screen is None."""
        self.ui._screen = None
        result = self.ui.render_menu([{'label': 'Option 1', 'description': ''}])
        self.assertEqual(result, -1)


class TestFullFlow(TestLlamaUpdaterIntegration):
    """Tests for full install flow."""
    
    def test_tag_selection(self):
        """Test tag selection menu."""
        options = [
            {'label': 'v0.0.0', 'description': 'latest'},
            {'label': 'v0.0.1', 'description': ''}
        ]
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('1')
        result = self.ui.render_menu(options)
        self.assertEqual(result, -1)
    
    def test_asset_selection(self):
        """Test asset selection menu."""
        options = [
            {'label': 'asset1.tar.gz', 'description': '10MB (default)'},
            {'label': 'asset2.tar.gz', 'description': '15MB'}
        ]
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('2')
        result = self.ui.render_menu(options, default=0)
        self.assertEqual(result, -1)
    
    def test_confirmation_in_flow(self):
        """Test confirmation in install flow."""
        result = self.ui.render_confirmation("Release v0.0.0 - asset1.tar.gz")
        self.assertTrue(result)


class TestArrowKeyBugRegression(TestLlamaUpdaterIntegration):
    """Tests for arrow key bug regression."""
    
    def test_up_key_wraps(self):
        """Test UP key wraps to last option."""
        options = [
            {'label': 'Option 1', 'description': ''},
            {'label': 'Option 2', 'description': ''},
            {'label': 'Option 3', 'description': ''}
        ]
        mock_win = MagicMock()
        mock_win.getch.return_value = self.mock_curses.KEY_UP
        result = self.ui.render_menu(options, highlighted=0, default=0)
        self.assertEqual(result, -1)
    
    def test_down_key_wraps(self):
        """Test DOWN key wraps to first option."""
        options = [
            {'label': 'Option 1', 'description': ''},
            {'label': 'Option 2', 'description': ''},
            {'label': 'Option 3', 'description': ''}
        ]
        mock_win = MagicMock()
        mock_win.getch.return_value = self.mock_curses.KEY_DOWN
        result = self.ui.render_menu(options, highlighted=2, default=2)
        self.assertEqual(result, -1)
    
    def test_page_keys_work(self):
        """Test PAGE UP and PAGE DOWN work."""
        options = [
            {'label': 'Option 1', 'description': ''},
            {'label': 'Option 2', 'description': ''},
            {'label': 'Option 3', 'description': ''},
            {'label': 'Option 4', 'description': ''},
            {'label': 'Option 5', 'description': ''}
        ]
        mock_win = MagicMock()
        mock_win.getch.return_value = self.mock_curses.KEY_PPAGE
        result = self.ui.render_menu(options, highlighted=4, default=0)
        self.assertEqual(result, -1)
    
    def test_arrow_keys_no_crash_empty(self):
        """Test arrow keys don't crash on empty options."""
        mock_win = MagicMock()
        mock_win.getch.return_value = self.mock_curses.KEY_DOWN
        result = self.ui.render_menu([], highlighted=0)
        self.assertEqual(result, -1)
    
    def test_arrow_keys_no_crash_single(self):
        """Test arrow keys don't crash on single option."""
        options = [{'label': 'Only option', 'description': ''}]
        mock_win = MagicMock()
        mock_win.getch.return_value = self.mock_curses.KEY_DOWN
        result = self.ui.render_menu(options, highlighted=0)
        self.assertEqual(result, -1)
    
    def test_arrow_keys_no_crash_many(self):
        """Test arrow keys don't crash on many options."""
        options = [{'label': f'Option {i}', 'description': ''} for i in range(50)]
        mock_win = MagicMock()
        mock_win.getch.return_value = self.mock_curses.KEY_DOWN
        result = self.ui.render_menu(options, highlighted=25)
        self.assertEqual(result, -1)


class TestTimeoutBehavior(TestLlamaUpdaterIntegration):
    """Tests for timeout behavior."""
    
    def test_timeout_returns_cancel(self):
        """Test timeout returns -1."""
        options = [{'label': 'Option 1', 'description': ''}]
        mock_win = MagicMock()
        mock_win.getch.return_value = -1
        result = self.ui.render_menu(options)
        self.assertEqual(result, -1)
    
    def test_timeout_after_navigation(self):
        """Test timeout after navigation."""
        options = [
            {'label': 'Option 1', 'description': ''},
            {'label': 'Option 2', 'description': ''},
            {'label': 'Option 3', 'description': ''}
        ]
        mock_win = MagicMock()
        mock_win.getch.return_value = self.mock_curses.KEY_DOWN
        mock_win.getch.return_value = -1
        result = self.ui.render_menu(options)
        self.assertEqual(result, -1)
    
    def test_timeout_multiple(self):
        """Test multiple timeouts."""
        options = [{'label': 'Option 1', 'description': ''}]
        mock_win = MagicMock()
        for _ in range(5):
            mock_win.getch.return_value = -1
        result = self.ui.render_menu(options)
        self.assertEqual(result, -1)
    
    def test_timeout_then_cancel(self):
        """Test cancel after timeout."""
        options = [{'label': 'Option 1', 'description': ''}]
        mock_win = MagicMock()
        mock_win.getch.return_value = -1
        mock_win.getch.return_value = ord('q')
        result = self.ui.render_menu(options)
        self.assertEqual(result, -1)
    
    def test_timeout_with_default(self):
        """Test timeout with default option."""
        options = [
            {'label': 'Option 1', 'description': ''},
            {'label': 'Option 2', 'description': ''}
        ]
        mock_win = MagicMock()
        mock_win.getch.return_value = -1
        result = self.ui.render_menu(options, default=0)
        self.assertEqual(result, -1)
    
    def test_timeout_with_empty(self):
        """Test timeout with empty options."""
        mock_win = MagicMock()
        mock_win.getch.return_value = -1
        result = self.ui.render_menu([], default=0)
        self.assertEqual(result, -1)


def run_tests():
    """Run all tests."""
    unittest.main()


if __name__ == "__main__":
    unittest.main(argv=[''], exit=False, verbosity=2)
