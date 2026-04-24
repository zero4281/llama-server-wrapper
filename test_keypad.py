#!/usr/bin/env python3
"""Simple test to verify curses keypad behavior."""

import curses
import sys

print("Starting test...", file=sys.stderr)

# Initialize curses
curses.initscr()
curses.start_color()
curses.cbreak()
curses.noecho()
curses.curs_set(0)

print("Before keypad(False):", file=sys.stderr)

# Disable keypad mode on main screen
curses.keypad(False)

print("After keypad(False):", file=sys.stderr)

# Create a window
curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
win = curses.newwin(10, 40, 1, 1)
win.box()
win.addstr(1, 1, "Press arrow keys")
win.refresh()

print("Window created, keypad mode on window:", file=sys.stderr)

# Enable keypad mode on the window
win.keypad(True)

print("Window keypad enabled, waiting for key...", file=sys.stderr)

# Get a key
try:
    key = win.getch()
    print(f"Got key: {key}", file=sys.stderr)
    if key == 258:
        print("SUCCESS: Got KEY_DOWN (258)", file=sys.stderr)
    elif key == 27:
        print("FAILURE: Got Escape (27)", file=sys.stderr)
    else:
        print(f"UNEXPECTED: Got {key}", file=sys.stderr)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)

# Cleanup
curses.endwin()
print("Test complete", file=sys.stderr)
