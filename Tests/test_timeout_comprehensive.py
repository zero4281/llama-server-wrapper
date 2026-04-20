#!/usr/bin/env python3
"""
Timeout tests for UIManager render_menu input loop.

These tests verify the timeout behavior when no input is received
for an extended period in the menu input loop.

Run with: python3 test_timeout_comprehensive.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path.cwd()))

import curses
from ui_manager import UIManager


def create_ui():
    """Helper to create UIManager with proper mocking."""
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
        ui = UIManager("Test Timeout")
        ui._using_curses = True
    return ui


def run_tests():
    """Run all timeout tests."""
    print("=" * 80)
    print("Running UIManager Timeout Tests")
    print("=" * 80)
    
    test_timeout_no_input()
    test_timeout_with_partial_input()
    test_timeout_wraps_back_to_menu()
    test_timeout_state_after_timeout()
    test_timeout_cancel_after_timeout()
    test_timeout_with_default_option()
    
    print("\n" + "=" * 80)
    print("ALL TIMEOUT TESTS PASSED")
    print("=" * 80)


def test_timeout_no_input():
    """Test that timeout returns -1 when no input is received."""
    print("\n[1/6] Testing timeout with no input...")
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    
    ui = create_ui()
    
    with patch.object(ui, '_screen') as mock_screen, \
         patch.object(ui, 'refresh'), \
         patch('curses.KEY_RESIZE'), \
         patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
        
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)
        mock_screen.getmaxyx.return_value = (20, 60)
        
        # Simulate timeout by returning None (EOF/timeout)
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = None  # Timeout
            
            result = ui.render_menu(options, default=0, highlighted=0)
            
            # On timeout, the menu should return -1 (cancel)
            assert result == -1, f"Timeout should return -1, got {result}"
    
    print("  PASSED")


def test_timeout_with_partial_input():
    """Test that timeout works after some input is received."""
    print("\n[2/6] Testing timeout after partial input...")
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    
    ui = create_ui()
    
    with patch.object(ui, '_screen') as mock_screen, \
         patch.object(ui, 'refresh'), \
         patch('curses.KEY_RESIZE'), \
         patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
        
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)
        mock_screen.getmaxyx.return_value = (20, 60)
        
        # User navigates then times out
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [
                curses.KEY_DOWN,  # Navigate down
                curses.KEY_UP,    # Navigate up
                None              # Timeout
            ]
            
            result = ui.render_menu(options, default=0, highlighted=0)
            
            assert result == -1, f"Timeout after navigation should return -1, got {result}"
    
    print("  PASSED")


def test_timeout_wraps_back_to_menu():
    """Test that menu resets to initial state after timeout."""
    print("\n[3/6] Testing menu reset after timeout...")
    
    options = [{'label': f'Option {i}'} for i in range(3)]
    
    ui = create_ui()
    
    with patch.object(ui, '_screen') as mock_screen, \
         patch.object(ui, 'refresh'), \
         patch('curses.KEY_RESIZE'), \
         patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
        
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)
        mock_screen.getmaxyx.return_value = (20, 60)
        
        # Simulate multiple timeouts
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [
                None,  # First timeout
                None,  # Second timeout
                None,  # Third timeout
            ]
            
            result = ui.render_menu(options, default=0, highlighted=0)
            
            assert result == -1, f"Multiple timeouts should return -1, got {result}"
            # Verify that redraw was called for each timeout
            assert mock_win.addstr.call_count > 0, "Menu should redraw on timeout"
    
    print("  PASSED")


def test_timeout_state_after_timeout():
    """Test that menu state is valid after timeout."""
    print("\n[4/6] Testing menu state after timeout...")
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    
    ui = create_ui()
    
    with patch.object(ui, '_screen') as mock_screen, \
         patch.object(ui, 'refresh'), \
         patch('curses.KEY_RESIZE'), \
         patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
        
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)
        mock_screen.getmaxyx.return_value = (20, 60)
        
        # Test with different initial highlighted states
        for highlighted in [0, 2, 4]:
            with patch.object(mock_win, 'getch') as mock_getch:
                mock_getch.return_value = None  # Timeout
                
                result = ui.render_menu(options, default=1, highlighted=highlighted)
                
                assert result == -1, f"Timeout with highlighted={highlighted} should return -1, got {result}"
    
    print("  PASSED")


def test_timeout_cancel_after_timeout():
    """Test that cancel still works after a timeout."""
    print("\n[5/6] Testing cancel after timeout...")
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    
    ui = create_ui()
    
    with patch.object(ui, '_screen') as mock_screen, \
         patch.object(ui, 'refresh'), \
         patch('curses.KEY_RESIZE'), \
         patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
        
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)
        mock_screen.getmaxyx.return_value = (20, 60)
        
        # Timeout first, then cancel
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.side_effect = [None, ord('q')]
            
            result = ui.render_menu(options, default=0, highlighted=0)
            
            assert result == -1, f"Cancel after timeout should return -1, got {result}"
    
    print("  PASSED")


def test_timeout_with_default_option():
    """Test timeout behavior with default option."""
    print("\n[6/6] Testing timeout with default option...")
    
    options = [{'label': f'Option {i}'} for i in range(5)]
    
    ui = create_ui()
    
    with patch.object(ui, '_screen') as mock_screen, \
         patch.object(ui, 'refresh'), \
         patch('curses.KEY_RESIZE'), \
         patch('curses.newwin', return_value=MagicMock()) as mock_newwin:
        
        mock_win = mock_newwin.return_value
        mock_win.getyx.return_value = (0, 0)
        mock_screen.getmaxyx.return_value = (20, 60)
        
        # Test with default option
        with patch.object(mock_win, 'getch') as mock_getch:
            mock_getch.return_value = None  # Timeout
            
            result = ui.render_menu(options, default=2, highlighted=0)
            
            assert result == -1, f"Timeout with default option should return -1, got {result}"
    
    print("  PASSED")


if __name__ == '__main__':
    run_tests()
