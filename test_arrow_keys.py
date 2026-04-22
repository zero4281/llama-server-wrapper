#!/usr/bin/env python3
"""Simple test for arrow key navigation in render_menu."""
import curses
curses.initscr()
curses.cbreak()
curses.noecho()
curses.curs_set(0)

# Initialize UIManager
from ui_manager import UIManager

ui = UIManager("Test Menu")

# Create test menu options
test_options = [
    {'label': 'Option 1', 'description': 'First option'},
    {'label': 'Option 2', 'description': 'Second option'},
    {'label': 'Option 3', 'description': 'Third option'},
    {'label': 'Option 4', 'description': 'Fourth option'},
    {'label': 'Option 5', 'description': 'Fifth option'},
]

print("Testing arrow key navigation...")
print("Use arrow keys to navigate, Enter to select, q to quit")

try:
    # Test with default selection
    result = ui.render_menu(test_options, default=2)
    print(f"Selected: {result}")
except KeyboardInterrupt:
    print("Test interrupted (as expected)")
except Exception as e:
    print(f"Error: {e}")
finally:
    ui._cleanup_terminal()

curses.endwin()
