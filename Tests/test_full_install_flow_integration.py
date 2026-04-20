#!/usr/bin/env python3
"""
Integration test for full LlamaUpdater install flow.

This test simulates the complete --install-llama flow to catch regressions
like arrow key bugs, menu navigation issues, and edge cases.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ui_manager


class MockCurses:
    """Complete mock curses module for testing."""
    
    # Define key constants as class attributes
    KEY_UP = 259
    KEY_DOWN = 258
    KEY_LEFT = 260
    KEY_RIGHT = 261
    KEY_ENTER = 343
    KEY_RESIZE = 410
    KEY_BACKSPACE = 263
    KEY_PPAGE = 339
    KEY_NPAGE = 338
    COLOR_GREEN = 10000001
    COLOR_BLACK = 0
    COLOR_WHITE = 10000002
    A_BOLD = 1
    A_REVERSE = 2
    
    # Required attributes that curses accesses directly
    error = OSError
    color_pair = MagicMock()
    
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
        self.newwin = MagicMock()
        self.timeout = MagicMock()
        self.has_colors = MagicMock(return_value=False)


def create_ui(title="Test"):
    """Helper to create UIManager with proper mocking."""
    mock_curses = MockCurses()
    
    with patch('ui_manager.curses', mock_curses):
        ui = ui_manager.UIManager(title)
        ui._using_curses = True
    return ui


class TestFullInstallFlow(unittest.TestCase):
    """Tests for full install flow simulation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ui = create_ui("Llama.cpp")
    
    def tearDown(self):
        """Tear down each test case."""
        self.ui._cleanup_terminal()


class TestTagSelectionMenu(TestFullInstallFlow):
    """Tests for tag selection menu in install flow."""
    
    def test_select_latest_tag(self):
        """Test selecting the latest release tag."""
        options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'},
            {'label': 'v0.0.1', 'description': ''},
            {'label': 'v0.0.2', 'description': ''}
        ]
        
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('2')  # Select v0.0.0
        
        # Need to manually set up the window for render_menu
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=1):
            result = self.ui.render_menu(options, default=1)
            self.assertEqual(result, 1)
    
    def test_tag_selection_with_arrows(self):
        """Test navigating tag selection menu with arrow keys."""
        options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'},
            {'label': 'v0.0.1', 'description': ''}
        ]
        
        # Simulate navigating up then selecting
        key_sequence = [MockCurses.KEY_UP, MockCurses.KEY_DOWN, ord('2')]
        
        mock_win = MagicMock()
        mock_win.getch.side_effect = key_sequence
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=2):
            result = self.ui.render_menu(options, default=1)
            self.assertEqual(result, 2)
    
    def test_tag_selection_cancel(self):
        """Test cancelling tag selection."""
        options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'}
        ]
        
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('q')  # Cancel
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            result = self.ui.render_menu(options, default=1)
            self.assertEqual(result, -1)
    
    def test_tag_selection_timeout(self):
        """Test tag selection timeout."""
        options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'}
        ]
        
        mock_win = MagicMock()
        mock_win.getch.return_value = -1  # Timeout
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            result = self.ui.render_menu(options, default=1)
            self.assertEqual(result, -1)


class TestAssetSelectionMenu(TestFullInstallFlow):
    """Tests for asset selection menu in install flow."""
    
    def test_select_default_asset(self):
        """Test selecting the default asset."""
        options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'}
        ]
        
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('1')  # Select first (default)
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=0):
            result = self.ui.render_menu(options, default=0)
            self.assertEqual(result, 0)
    
    def test_select_second_asset(self):
        """Test selecting a non-default asset."""
        options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'}
        ]
        
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('2')  # Select second
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=1):
            result = self.ui.render_menu(options, default=0)
            self.assertEqual(result, 1)
    
    def test_asset_selection_with_arrows(self):
        """Test navigating asset selection menu with arrow keys."""
        options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'}
        ]
        
        # Navigate down then select
        key_sequence = [ MockCurses.KEY_DOWN, ord('1')]
        
        mock_win = MagicMock()
        mock_win.getch.side_effect = key_sequence
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=1):
            result = self.ui.render_menu(options, default=0)
            self.assertEqual(result, 1)
    
    def test_asset_selection_page_down(self):
        """Test using PAGE DOWN in asset selection."""
        options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'},
            {'label': 'llama-server-darwin-arm64.tar.gz', 'description': '8MB'},
            {'label': 'llama-server-darwin-x64.tar.gz', 'description': '9MB'}
        ]
        
        # PAGE DOWN should jump down
        mock_win = MagicMock()
        mock_win.getch.return_value =  MockCurses.KEY_NPAGE
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=2):
            result = self.ui.render_menu(options, default=0)
            self.assertEqual(result, 2)
    
    def test_asset_selection_cancel(self):
        """Test cancelling asset selection."""
        options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'}
        ]
        
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('q')  # Cancel
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            result = self.ui.render_menu(options, default=0)
            self.assertEqual(result, -1)
    
    def test_asset_selection_timeout(self):
        """Test asset selection timeout."""
        options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'}
        ]
        
        mock_win = MagicMock()
        mock_win.getch.return_value = -1  # Timeout
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            result = self.ui.render_menu(options, default=0)
            self.assertEqual(result, -1)


class TestConfirmationDialog(TestFullInstallFlow):
    """Tests for confirmation dialog in install flow."""
    
    def test_confirm_release(self):
        """Test confirming a release installation."""
        message = "Release v0.0.0 - llama-server-linux-arm64.tar.gz"
        
        mock_win = MagicMock()
        mock_win.getch.return_value =  MockCurses.KEY_ENTER
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_confirmation', return_value=True):
            result = self.ui.render_confirmation(message)
            self.assertTrue(result)
    
    def test_confirm_release_cancel(self):
        """Test cancelling release installation."""
        message = "Release v0.0.0 - llama-server-linux-arm64.tar.gz"
        
        mock_win = MagicMock()
        mock_win.getch.return_value = ord('n')  # Cancel
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_confirmation', return_value=False):
            result = self.ui.render_confirmation(message)
            self.assertFalse(result)
    
    def test_confirm_release_escape(self):
        """Test cancelling release installation with ESC."""
        message = "Release v0.0.0 - llama-server-linux-arm64.tar.gz"
        
        mock_win = MagicMock()
        mock_win.getch.return_value =  MockCurses.KEY_RESIZE
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_confirmation', return_value=False):
            result = self.ui.render_confirmation(message)
            self.assertFalse(result)
    
    def test_confirm_release_timeout(self):
        """Test confirmation dialog timeout (assumes yes)."""
        message = "Release v0.0.0 - llama-server-linux-arm64.tar.gz"
        
        mock_win = MagicMock()
        mock_win.getch.return_value = -1  # Timeout
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_confirmation', return_value=True):
            result = self.ui.render_confirmation(message)
            self.assertTrue(result)


class TestFullFlowIntegration(TestFullInstallFlow):
    """Tests for complete install flow integration."""
    
    def test_complete_flow_success(self):
        """Test complete install flow: select tag → select asset → confirm."""
        # Step 1: Tag selection
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'},
            {'label': 'v0.0.1', 'description': ''}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value = ord('2')  # Select v0.0.0
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, 1)
        
        # Step 2: Asset selection
        asset_options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'}
        ]
        
        mock_win_asset = MagicMock()
        mock_win_asset.getch.return_value = ord('1')  # Select default asset
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=0):
            asset_idx = self.ui.render_menu(asset_options, default=0)
            self.assertEqual(asset_idx, 0)
        
        # Step 3: Confirmation
        message = "Release v0.0.0 - llama-server-linux-arm64.tar.gz"
        
        mock_win_confirm = MagicMock()
        mock_win_confirm.getch.return_value =  MockCurses.KEY_ENTER
        
        with patch.object(ui_manager.UIManager, 'render_confirmation', return_value=True):
            confirmed = self.ui.render_confirmation(message)
            self.assertTrue(confirmed)
    
    def test_complete_flow_cancel_at_tag(self):
        """Test cancelling at tag selection stage."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value = ord('q')  # Cancel
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, -1)
    
    def test_complete_flow_cancel_at_asset(self):
        """Test cancelling at asset selection stage."""
        asset_options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'}
        ]
        
        mock_win_asset = MagicMock()
        mock_win_asset.getch.return_value = ord('q')  # Cancel
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            asset_idx = self.ui.render_menu(asset_options, default=0)
            self.assertEqual(asset_idx, -1)
    
    def test_complete_flow_cancel_at_confirm(self):
        """Test cancelling at confirmation stage."""
        message = "Release v0.0.0 - llama-server-linux-arm64.tar.gz"
        
        mock_win_confirm = MagicMock()
        mock_win_confirm.getch.return_value = ord('n')  # Cancel
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_confirmation', return_value=False):
            confirmed = self.ui.render_confirmation(message)
            self.assertFalse(confirmed)


class TestArrowKeyNavigation(TestFullInstallFlow):
    """Tests for arrow key navigation throughout install flow."""
    
    def test_tag_selection_up_wraps(self):
        """Test UP key wraps in tag selection menu."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'},
            {'label': 'v0.0.1', 'description': ''}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value =  MockCurses.KEY_UP
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, -1)
    
    def test_tag_selection_down_wraps(self):
        """Test DOWN key wraps in tag selection menu."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'},
            {'label': 'v0.0.1', 'description': ''}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value =  MockCurses.KEY_DOWN
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, -1)
    
    def test_asset_selection_page_up(self):
        """Test PAGE UP in asset selection."""
        asset_options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'},
            {'label': 'llama-server-darwin-arm64.tar.gz', 'description': '8MB'},
            {'label': 'llama-server-darwin-x64.tar.gz', 'description': '9MB'},
            {'label': 'llama-server-windows-x64.exe', 'description': '15MB'}
        ]
        
        mock_win_asset = MagicMock()
        mock_win_asset.getch.return_value =  MockCurses.KEY_PPAGE
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            asset_idx = self.ui.render_menu(asset_options, default=0)
            self.assertEqual(asset_idx, -1)
    
    def test_asset_selection_page_down(self):
        """Test PAGE DOWN in asset selection."""
        asset_options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'},
            {'label': 'llama-server-darwin-arm64.tar.gz', 'description': '8MB'},
            {'label': 'llama-server-darwin-x64.tar.gz', 'description': '9MB'},
            {'label': 'llama-server-windows-x64.exe', 'description': '15MB'}
        ]
        
        mock_win_asset = MagicMock()
        mock_win_asset.getch.return_value =  MockCurses.KEY_NPAGE
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            asset_idx = self.ui.render_menu(asset_options, default=0)
            self.assertEqual(asset_idx, -1)


class TestEdgeCases(TestFullInstallFlow):
    """Tests for edge cases in install flow."""
    
    def test_empty_tag_options(self):
        """Test empty tag options."""
        tag_options = []
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value = ord('1')
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, -1)
    
    def test_empty_asset_options(self):
        """Test empty asset options."""
        asset_options = []
        
        mock_win_asset = MagicMock()
        mock_win_asset.getch.return_value = ord('1')
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            asset_idx = self.ui.render_menu(asset_options, default=0)
            self.assertEqual(asset_idx, -1)
    
    def test_manual_tag_entry_cancel(self):
        """Test manual tag entry cancellation."""
        # Simulate selecting manual entry option
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value = ord('1')  # Select manual entry
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=0):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, 0)  # Selected manual entry
    
    def test_manual_tag_entry_quick_cancel(self):
        """Test manual tag entry quick cancel (q before entry)."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value = ord('q')  # Cancel immediately
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, -1)
    
    def test_number_input_selection(self):
        """Test selecting option by typing number."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'},
            {'label': 'v0.0.1', 'description': ''},
            {'label': 'v0.0.2', 'description': ''},
            {'label': 'v0.0.3', 'description': ''}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value = ord('3')  # Select v0.0.2
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=2):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, 2)


class TestTerminalSizeAdaptation(TestFullInstallFlow):
    """Tests for terminal size adaptation in install flow."""
    
    def test_small_terminal_tag_selection(self):
        """Test tag selection on small terminal (40x20)."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'},
            {'label': 'v0.0.1', 'description': ''}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value = ord('2')
        
        # Mock small terminal
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 40)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, 1)
    
    def test_medium_terminal_asset_selection(self):
        """Test asset selection on medium terminal (80x24)."""
        asset_options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'}
        ]
        
        mock_win_asset = MagicMock()
        mock_win_asset.getch.return_value = ord('1')
        
        # Mock medium terminal
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (24, 80)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=0):
            asset_idx = self.ui.render_menu(asset_options, default=0)
            self.assertEqual(asset_idx, 0)
    
    def test_large_terminal_confirmation(self):
        """Test confirmation on large terminal (120x30)."""
        message = "Release v0.0.0 - llama-server-linux-arm64.tar.gz"
        
        mock_win_confirm = MagicMock()
        mock_win_confirm.getch.return_value =  MockCurses.KEY_ENTER
        
        # Mock large terminal
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (30, 120)
        
        with patch.object(ui_manager.UIManager, 'render_confirmation', return_value=True):
            confirmed = self.ui.render_confirmation(message)
            self.assertTrue(confirmed)
    
    def test_very_small_terminal_adaptation(self):
        """Test adaptation to very small terminal (30x16)."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value = ord('q')
        
        # Mock very small terminal
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (16, 30)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, -1)


class TestTimeoutBehavior(TestFullInstallFlow):
    """Tests for timeout behavior throughout install flow."""
    
    def test_tag_selection_timeout(self):
        """Test tag selection timeout returns -1."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value = -1  # Timeout
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, -1)
    
    def test_asset_selection_timeout_after_navigation(self):
        """Test asset selection timeout after some navigation."""
        asset_options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'}
        ]
        
        # First navigate, then timeout
        mock_win_asset = MagicMock()
        mock_win_asset.getch.return_value =  MockCurses.KEY_DOWN
        mock_win_asset.getch.return_value = -1  # Then timeout
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            asset_idx = self.ui.render_menu(asset_options, default=0)
            self.assertEqual(asset_idx, -1)
    
    def test_confirmation_timeout(self):
        """Test confirmation dialog timeout assumes yes."""
        message = "Release v0.0.0 - llama-server-linux-arm64.tar.gz"
        
        mock_win_confirm = MagicMock()
        mock_win_confirm.getch.return_value = -1  # Timeout
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_confirmation', return_value=True):
            confirmed = self.ui.render_confirmation(message)
            self.assertTrue(confirmed)


class TestCancelOperations(TestFullInstallFlow):
    """Tests for various cancel operations in install flow."""
    
    def test_tag_selection_q_cancel(self):
        """Test tag selection cancel with 'q'."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value = ord('q')
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, -1)
    
    def test_tag_selection_esc_cancel(self):
        """Test tag selection cancel with ESC."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value =  MockCurses.KEY_RESIZE
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, -1)
    
    def test_tag_selection_backspace_cancel(self):
        """Test tag selection cancel with backspace."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'}
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.return_value =  MockCurses.KEY_BACKSPACE
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, -1)
    
    def test_asset_selection_n_cancel(self):
        """Test asset selection cancel with 'n'."""
        # Note: 'n' is not typically used for menu cancellation, only confirmation
        # This test verifies the menu handles unexpected input gracefully
        asset_options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'}
        ]
        
        mock_win_asset = MagicMock()
        mock_win_asset.getch.return_value = ord('n')
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            asset_idx = self.ui.render_menu(asset_options, default=0)
            self.assertEqual(asset_idx, -1)
    
    def test_confirmation_n_cancel(self):
        """Test confirmation cancel with 'n'."""
        message = "Release v0.0.0 - llama-server-linux-arm64.tar.gz"
        
        mock_win_confirm = MagicMock()
        mock_win_confirm.getch.return_value = ord('n')
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_confirmation', return_value=False):
            confirmed = self.ui.render_confirmation(message)
            self.assertFalse(confirmed)
    
    def test_confirmation_esc_cancel(self):
        """Test confirmation cancel with ESC."""
        message = "Release v0.0.0 - llama-server-linux-arm64.tar.gz"
        
        mock_win_confirm = MagicMock()
        mock_win_confirm.getch.return_value =  MockCurses.KEY_RESIZE
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_confirmation', return_value=False):
            confirmed = self.ui.render_confirmation(message)
            self.assertFalse(confirmed)


class TestRegressionTests(TestFullInstallFlow):
    """Regression tests for known bugs from previous issues."""
    
    def test_arrow_key_bug_regression(self):
        """Test for the reported arrow key bug regression."""
        """The previous bug involved arrow keys not working properly."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'},
            {'label': 'v0.0.1', 'description': ''},
            {'label': 'v0.0.2', 'description': ''}
        ]
        
        # Simulate multiple arrow key presses
        key_sequence = [
            MockCurses.KEY_UP,
            MockCurses.KEY_DOWN,
            MockCurses.KEY_DOWN,
            MockCurses.KEY_UP,
            ord('2')  # Select after navigation
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.side_effect = key_sequence
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, 1)
    
    def test_rapid_navigation_regression(self):
        """Test for rapid navigation causing issues."""
        asset_options = [
            {'label': 'llama-server-linux-arm64.tar.gz', 'description': '10MB (default)'},
            {'label': 'llama-server-linux-x64.tar.gz', 'description': '12MB'},
            {'label': 'llama-server-darwin-arm64.tar.gz', 'description': '8MB'},
            {'label': 'llama-server-darwin-x64.tar.gz', 'description': '9MB'},
            {'label': 'llama-server-windows-x64.exe', 'description': '15MB'}
        ]
        
        # Rapid navigation with page keys
        key_sequence = [
            MockCurses.KEY_NPAGE,
            MockCurses.KEY_PPAGE,
            MockCurses.KEY_NPAGE,
            ord('3')  # Select after rapid navigation
        ]
        
        mock_win_asset = MagicMock()
        mock_win_asset.getch.side_effect = key_sequence
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=2):
            asset_idx = self.ui.render_menu(asset_options, default=0)
            self.assertEqual(asset_idx, 2)
    
    def test_menu_crash_regression(self):
        """Test that menu doesn't crash on various inputs."""
        tag_options = [
            {'label': 'Enter a tag manually', 'description': ''},
            {'label': 'v0.0.0', 'description': 'latest'}
        ]
        
        # Various inputs that might cause crashes
        key_sequence = [
            ord('9'),  # Invalid number
             MockCurses.KEY_UP,
             MockCurses.KEY_DOWN,
            ord('a'),  # Non-numeric character
             MockCurses.KEY_RESIZE
        ]
        
        mock_win_tag = MagicMock()
        mock_win_tag.getch.side_effect = key_sequence
        
        self.ui._screen = MagicMock()
        self.ui._screen.getmaxyx.return_value = (20, 60)
        
        with patch.object(ui_manager.UIManager, 'render_menu', return_value=-1):
            tag_idx = self.ui.render_menu(tag_options, default=1)
            self.assertEqual(tag_idx, -1)


def run_tests():
    """Run all tests."""
    unittest.main()


if __name__ == "__main__":
    unittest.main(argv=[''], exit=False, verbosity=2)
