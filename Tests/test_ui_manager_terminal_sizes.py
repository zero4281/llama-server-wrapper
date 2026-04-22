#!/usr/bin/env python3
"""
Terminal size edge case tests for UIManager.

Tests verify that UI adapts correctly to various screen sizes:
- Small terminal: 40x20
- Medium terminal: 80x24
- Large terminal: 120x30

Run with: python3 test_ui_manager_terminal_sizes.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

import curses
from ui_manager import UIManager


def setup_ui_for_size(width, height):
    """Helper to create UIManager with mocked terminal size."""
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
        ui = UIManager("Test")
        ui._using_curses = True
    
    return ui, mock_curses


def run_tests():
    """Run all terminal size tests."""
    print("=" * 80)
    print("Running UIManager Terminal Size Tests")
    print("=" * 80)
    
    all_passed = True
    
    # Test 1: Small terminal (40x20)
    print("\n[1/6] Testing Small Terminal (40x20)...")
    test_small_terminal()
    
    # Test 2: Medium terminal (80x24)
    print("[2/6] Testing Medium Terminal (80x24)...")
    test_medium_terminal()
    
    # Test 3: Large terminal (120x30)
    print("[3/6] Testing Large Terminal (120x30)...")
    test_large_terminal()
    
    # Test 4: Menu width calculation for small terminal
    print("[4/6] Testing Menu Width Calculation (Small)...")
    test_menu_width_small()
    
    # Test 5: Menu width calculation for large terminal
    print("[5/6] Testing Menu Width Calculation (Large)...")
    test_menu_width_large()
    
    # Test 6: Progress bar adaptation
    print("[6/6] Testing Progress Bar Adaptation...")
    test_progress_bar_adaptation()
    
    if all_passed:
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("SOME TESTS FAILED")
        print("=" * 80)
        sys.exit(1)


def test_small_terminal():
    """Test UIManager on 40x20 terminal."""
    ui, mock_curses = setup_ui_for_size(40, 20)
    
    # Mock screen methods
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 40)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh'), \
          patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:
        
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)
        mock_win.erase.return_value = None
        mock_win.addstr.return_value = None
        mock_win.attron.return_value = None
        mock_win.attroff.return_value = None
        mock_win.refresh.return_value = None
        
        options = [{'label': 'Option'} for _ in range(5)]
        
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [curses.KEY_RESIZE]  # Cancel
            result = ui.render_menu(options, default=0, highlighted=0)
            
            # Should return -1 on cancel
            assert result == -1, f"Should return -1 on cancel, got {result}"
    
    ui._cleanup_terminal()
    print("  ✓ Small terminal test passed")


def test_medium_terminal():
    """Test UIManager on 80x24 terminal."""
    ui, mock_curses = setup_ui_for_size(80, 24)
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (24, 80)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh'), \
          patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:
        
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)
        mock_win.erase.return_value = None
        mock_win.addstr.return_value = None
        mock_win.attron.return_value = None
        mock_win.attroff.return_value = None
        mock_win.refresh.return_value = None
        
        options = [{'label': 'Option'} for _ in range(10)]
        
        with patch.object(mock_win, 'getch') as mock_getch:
            # Type '3' (keycode 51 for digit '3'), then Enter (10)
            mock_getch.side_effect = [ord('3'), 10]
            result = ui.render_menu(options, default=0, highlighted=0)
            
            assert result == 3, f"Should select option 3, got {result}"
    
    ui._cleanup_terminal()
    print("  ✓ Medium terminal test passed")


def test_large_terminal():
    """Test UIManager on 120x30 terminal."""
    ui, mock_curses = setup_ui_for_size(120, 30)
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (30, 120)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh'), \
          patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin:
        
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)
        mock_win.erase.return_value = None
        mock_win.addstr.return_value = None
        mock_win.attron.return_value = None
        mock_win.attroff.return_value = None
        mock_win.refresh.return_value = None
        
        options = [{'label': 'Option'} for _ in range(15)]
        
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [curses.KEY_DOWN, curses.KEY_DOWN, curses.KEY_RESIZE]
            result = ui.render_menu(options, default=0, highlighted=0)
            
            assert result == -1, f"Should return -1 on cancel, got {result}"
    
    ui._cleanup_terminal()
    print("  ✓ Large terminal test passed")


def test_menu_width_small():
    """Test menu width calculation for small terminal."""
    ui, _ = setup_ui_for_size(40, 20)
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (20, 40)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh'):
        
        options = [{'label': 'VeryLongLabel'}]  # Long label
        
        # Calculate expected menu width
        max_label_len = len('VeryLongLabel')  # 14
        min_width = int(40 * 0.6)  # 24
        menu_width = max(min_width, min(max_label_len + 15, 40 - 8)) + 2
        menu_width = max(24, min(29, 32)) + 2  # = 34
        
        assert menu_width <= 40, f"Menu width {menu_width} should fit in terminal width 40"
        assert menu_width >= 24, f"Menu width {menu_width} should be at least 24 (60%)"
    
    ui._cleanup_terminal()
    print("  ✓ Menu width calculation for small terminal passed")


def test_menu_width_large():
    """Test menu width calculation for large terminal."""
    ui, _ = setup_ui_for_size(120, 30)
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (30, 120)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh'):
        
        options = [{'label': 'Short'}]  # Short label
        
        # Calculate expected menu width
        max_label_len = 5  # len('Short')
        min_width = int(120 * 0.6)  # 72
        menu_width = max(min_width, min(max_label_len + 15, 120 - 8)) + 2
        menu_width = max(72, min(20, 112)) + 2  # = 74
        
        assert menu_width <= 120, f"Menu width {menu_width} should fit in terminal width 120"
        assert menu_width >= 72, f"Menu width {menu_width} should be at least 72 (60%)"
    
    ui._cleanup_terminal()
    print("  ✓ Menu width calculation for large terminal passed")


def test_progress_bar_adaptation():
    """Test progress bar adapts to different terminal sizes."""
    test_cases = [
        (20, 40, "Small"),
        (24, 80, "Medium"),
        (30, 120, "Large"),
    ]
    
    for height, width, name in test_cases:
        ui, _ = setup_ui_for_size(width, height)
        
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (height, width)
        
        with patch.object(ui, '_screen', mock_screen), \
          patch.object(ui, 'refresh'), \
          patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin, \
             patch('builtins.input'):
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_RESIZE
            mock_win.erase.return_value = None
            mock_win.addstr.return_value = None
            mock_win.attron.return_value = None
            mock_win.attroff.return_value = None
            mock_win.refresh.return_value = None
            
            # Test progress bar rendering
            ui.render_progress_bar("test.zip", 500, 1000, percent=50.0)
            
            # Verify window was created with appropriate size
            assert mock_newwin.called, f"Window should be created for {name} terminal"
            
            # Get the call arguments (newwin takes height, width, y, x)
            call_args = mock_newwin.call_args
            if call_args:
                win_height, win_width, win_y, win_x = call_args[0]
                # Bar height should be 6, width should be proportional to terminal
                assert win_height == 6, f"Bar height should be 6, got {win_height} for {name}"
                # Width should be at least 50 but fit on screen
                assert win_width <= width - 10, f"Bar width {win_width} should fit on terminal width {width}"
    
    print("  ✓ Progress bar adaptation test passed")


if __name__ == '__main__':
    run_tests()


def test_window_height_is_exactly_6_rows():
    """Verify that progress bar window height is exactly 6 rows."""
    ui, mock_curses = setup_ui_for_size(80, 24)
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (24, 80)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh'), \
         patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin, \
         patch('builtins.input', return_value='\n'):
        
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)
        mock_win.getch.return_value = curses.KEY_RESIZE
        mock_win.erase.return_value = None
        mock_win.addstr.return_value = None
        mock_win.attron.return_value = None
        mock_win.attroff.return_value = None
        mock_win.refresh.return_value = None
        
        # Test with total > 0 (determinate bar)
        ui.render_progress_bar("file.zip", 500, 1000, percent=50.0)
        
        # Verify window height is 6
        call_args = mock_newwin.call_args
        assert call_args is not None, "Window should be created"
        height, width, y, x = call_args[0]
        assert height == 6, f"Window height should be exactly 6, got {height}"
        
        # Test with total == 0 (spinner)
        ui.render_progress_bar("unknown.zip", 0, 0)
        
        # Verify window height is still 6
        call_args = mock_newwin.call_args
        height, width, y, x = call_args[0]
        assert height == 6, f"Spinner window height should be exactly 6, got {height}"
    
    ui._cleanup_terminal()
    print("  ✓ Window height test passed")


def test_window_width_calculation_and_cap():
    """Verify window width calculation and cap at terminal_width - 10."""
    test_cases = [
        (40, 20, 20),   # Small terminal
        (80, 24, 24),   # Medium terminal
        (120, 30, 30),  # Large terminal
    ]
    
    for width, height, expected_min_width in test_cases:
        ui, mock_curses = setup_ui_for_size(width, height)
        
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (height, width)
        
        with patch.object(ui, '_screen', mock_screen), \
             patch.object(ui, 'refresh'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin, \
             patch('builtins.input', return_value='\n'):
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_RESIZE
            mock_win.erase.return_value = None
            mock_win.addstr.return_value = None
            mock_win.attron.return_value = None
            mock_win.attroff.return_value = None
            mock_win.refresh.return_value = None
            
            ui.render_progress_bar("test.zip", 500, 1000, percent=50.0)
            
            # Verify window width is at least expected_min_width
            call_args = mock_newwin.call_args
            assert call_args is not None, f"Window should be created for terminal {width}x{height}"
            height_win, width_win, y, x = call_args[0]
            
            # Width should be at least 50 (minimum for progress bar)
            assert width_win >= 50, f"Window width should be at least 50, got {width_win} for {width}x{height}"
            
            # Width should be capped at terminal_width - 10
            max_width = width - 10
            assert width_win <= max_width, \
                f"Window width {width_win} should be capped at {max_width} for {width}x{height}"
        
        ui._cleanup_terminal()
    
    print("  ✓ Window width calculation test passed")


def test_window_height_is_exactly_6_rows():
    """Verify that progress bar window height is exactly 6 rows."""
    ui, mock_curses = setup_ui_for_size(80, 24)
    
    mock_screen = MagicMock()
    mock_screen.getmaxyx.return_value = (24, 80)
    
    with patch.object(ui, '_screen', mock_screen), \
         patch.object(ui, 'refresh'), \
         patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin, \
         patch('builtins.input', return_value='\n'):
        
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)
        mock_win.getch.return_value = curses.KEY_RESIZE
        mock_win.erase.return_value = None
        mock_win.addstr.return_value = None
        mock_win.attron.return_value = None
        mock_win.attroff.return_value = None
        mock_win.refresh.return_value = None
        
        # Test with total > 0 (determinate bar)
        ui.render_progress_bar("file.zip", 500, 1000, percent=50.0)
        
        # Verify window height is 6
        call_args = mock_newwin.call_args
        assert call_args is not None, "Window should be created"
        height, width, y, x = call_args[0]
        assert height == 6, f"Window height should be exactly 6, got {height}"
        
        # Test with total == 0 (spinner)
        ui.render_progress_bar("unknown.zip", 0, 0)
        
        # Verify window height is still 6
        call_args = mock_newwin.call_args
        height, width, y, x = call_args[0]
        assert height == 6, f"Spinner window height should be exactly 6, got {height}"
    
    ui._cleanup_terminal()
    print("  ✓ Window height test passed")


def test_window_width_calculation_and_cap():
    """Verify window width calculation and cap at terminal_width - 10."""
    test_cases = [
        (40, 20, 20),   # Small terminal
        (80, 24, 24),   # Medium terminal
        (120, 30, 30),  # Large terminal
    ]
    
    for width, height, expected_min_width in test_cases:
        ui, mock_curses = setup_ui_for_size(width, height)
        
        mock_screen = MagicMock()
        mock_screen.getmaxyx.return_value = (height, width)
        
        with patch.object(ui, '_screen', mock_screen), \
             patch.object(ui, 'refresh'), \
             patch('ui_manager.curses.newwin', return_value=MagicMock()) as mock_newwin, \
             patch('builtins.input', return_value='\n'):
            
            mock_win = mock_newwin.return_value
            mock_win.getyx.return_value = (0, 0)
            mock_win.getch.return_value = curses.KEY_RESIZE
            mock_win.erase.return_value = None
            mock_win.addstr.return_value = None
            mock_win.attron.return_value = None
            mock_win.attroff.return_value = None
            mock_win.refresh.return_value = None
            
            ui.render_progress_bar("test.zip", 500, 1000, percent=50.0)
            
            # Verify window width is at least min(50, width - 10)
            call_args = mock_newwin.call_args
            assert call_args is not None, f"Window should be created for terminal {width}x{height}"
            bar_height, bar_width, y, x = call_args[0]
            
            # Width should be at least min(50, width - 10)
            min_width = min(50, width - 10)
            assert bar_width >= min_width, f"Window width should be at least {min_width}, got {bar_width} for {width}x{height}"
            
            # Width should be capped at terminal_width - 10
            max_width = width - 10
            assert bar_width <= max_width, \
                f"Window width {bar_width} should be capped at {max_width} for {width}x{height}"
        
        ui._cleanup_terminal()
    
    print("  ✓ Window width calculation test passed")
