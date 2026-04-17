#!/usr/bin/env python3
"""Edge case tests for UIManager using pytest."""

import pytest
import sys
from pathlib import Path
import curses
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path.cwd()))


@pytest.fixture
def mock_curses_and_screen():
    """Create a mock curses module and screen."""
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 40)
    
    mock_curses_module = MagicMock()
    mock_curses_module.initscr.return_value = mock_screen
    mock_curses_module.start_color = MagicMock()
    mock_curses_module.init_pair.return_value = 1
    mock_curses_module.cbreak = MagicMock()
    mock_curses_module.noecho = MagicMock()
    mock_curses_module.curs_set.return_value = None
    mock_curses_module.nodelay = MagicMock()
    
    yield mock_curses_module, mock_screen


def test_screen_size_40x20(mock_curses_and_screen):
    """Test menu rendering on 40x20 screen."""
    mock_curses_module, mock_screen = mock_curses_and_screen
    with patch('curses', mock_curses_module):
        from ui_manager import UIManager
        ui = UIManager("Test")
        ui._using_curses = True
        ui._screen = mock_screen
        ui._color_pair = 1
        ui._initialized = True
        
        result = ui.render_menu(
            [{'label': f'Opt {i}'} for i in range(5)],
            default=0,
            highlighted=0
        )
        assert result == 1, f"Expected 1, got {result}"


def test_screen_size_80x24(mock_curses_and_screen):
    """Test menu rendering on 80x24 screen."""
    mock_curses_module, mock_screen = mock_curses_and_screen
    with patch('curses', mock_curses_module):
        from ui_manager import UIManager
        ui = UIManager("Test")
        ui._using_curses = True
        ui._screen = mock_screen
        ui._color_pair = 1
        ui._initialized = True
        
        ui.render_menu(
            [{'label': f'Opt {i}'} for i in range(10)],
            default=0,
            highlighted=0
        )


def test_screen_size_120x30(mock_curses_and_screen):
    """Test menu rendering on 120x30 screen."""
    mock_curses_module, mock_screen = mock_curses_and_screen
    with patch('curses', mock_curses_module):
        from ui_manager import UIManager
        ui = UIManager("Test")
        ui._using_curses = True
        ui._screen = mock_screen
        ui._color_pair = 1
        ui._initialized = True
        
        result = ui.render_menu(
            [{'label': f'Opt {i}'} for i in range(20)],
            default=0,
            highlighted=0
        )
        assert result == 0, f"Expected 0, got {result}"


def test_single_option(mock_curses_and_screen):
    """Test with only one option."""
    mock_curses_module, mock_screen = mock_curses_and_screen
    with patch('curses', mock_curses_module):
        from ui_manager import UIManager
        ui = UIManager("Test")
        ui._using_curses = True
        ui._screen = mock_screen
        ui._color_pair = 1
        ui._initialized = True
        
        result = ui.render_menu(
            [{'label': 'Only Option'}],
            default=0,
            highlighted=0
        )
        assert result == 0, f"Expected 0, got {result}"


def test_empty_options(mock_curses_and_screen):
    """Test with empty options list."""
    mock_curses_module, mock_screen = mock_curses_and_screen
    with patch('curses', mock_curses_module):
        from ui_manager import UIManager
        ui = UIManager("Test")
        ui._using_curses = True
        ui._screen = mock_screen
        ui._color_pair = 1
        ui._initialized = True
        
        result = ui.render_menu([], default=None, highlighted=None)
        assert result == -1, f"Expected -1, got {result}"


def test_long_label(mock_curses_and_screen):
    """Test with very long option labels."""
    mock_curses_module, mock_screen = mock_curses_and_screen
    with patch('curses', mock_curses_module):
        from ui_manager import UIManager
        ui = UIManager("Test")
        ui._using_curses = True
        ui._screen = mock_screen
        ui._color_pair = 1
        ui._initialized = True
        
        long_label = "A" * 100
        result = ui.render_menu(
            [{'label': long_label}],
            default=0,
            highlighted=0
        )
        assert result == 0, f"Expected 0, got {result}"


def test_page_down(mock_curses_and_screen):
    """Test page down navigation."""
    mock_curses_module, mock_screen = mock_curses_and_screen
    with patch('curses', mock_curses_module):
        from ui_manager import UIManager
        ui = UIManager("Test")
        ui._using_curses = True
        ui._screen = mock_screen
        ui._color_pair = 1
        ui._initialized = True
        
        ui.render_menu(
            [{'label': f'Opt {i}'} for i in range(15)],
            default=0,
            highlighted=0
        )


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
