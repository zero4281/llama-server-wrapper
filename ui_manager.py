"""
ui_manager.py — ncurses CLI user interface module.

This module provides ncurses-based UI rendering for menus, prompts,
progress bars, and other interactive elements with black background
and green text styling.
"""

import curses
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any


class UIManagerError(Exception):
    """Base exception for UIManager errors."""
    pass


class UIManager:
    """
    ncurses-based UI manager for rendering menus, prompts, and progress bars.
    
    Features:
    - Black background with green text (curses.COLOR_GREEN)
    - Numbered menu rendering with arrow key navigation
    - Confirmation prompts with Y/n handling
    - Progress bars with percentage and byte counts
    - Spinner animation for indeterminate progress
    - Proper initialization and cleanup
    """

    def __init__(self, title: Optional[str] = None):
        """
        Initialize the UI manager.
        
        Args:
            title: Optional title for windows
        """
        self._screen = None
        self._title = title or "Llama Server Wrapper"
        self._color_pair = None
        
        try:
            # Initialize curses
            self._screen = curses.initscr()
            curses.curs_set(0)  # Hide cursor
            self._screen.nodelay(0)  # Normal mode (wait for input)
            self._screen.timeout(100)  # 100ms timeout for key refresh
            
            # Use alternate screen buffer if available
            try:
                curses.start_color()
                # Set color pair: black background, green text
                curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
                self._color_pair = curses.color_pair(1)
            except:
                # Fallback for systems without alternate screen
                pass
            
            # Use alternate screen buffer
            try:
                curses.use_default_colors()
                curses.start_color()
                self._color_pair = curses.color_pair(1) | curses.A_BOLD
            except:
                pass
            
            # Initialize colors for reverse video
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Reverse video
            
        except curses.error as e:
            raise UIManagerError(f"Failed to initialize curses: {e}")

    def __del__(self):
        """Cleanup curses resources."""
        self._close()

    def _close(self):
        """Close curses and restore terminal."""
        if self._screen:
            try:
                curses.endwin()
            except:
                pass

    def refresh(self):
        """Refresh screen."""
        if self._screen:
            self._screen.refresh()

    def clear(self):
        """Clear screen."""
        if self._screen:
            self._screen.erase()

    def print_header(self, text: str):
        """Print header with color."""
        if self._screen:
            self._screen.attron(self._color_pair)
            self._screen.addstr(0, 0, text.ljust(60))
            self._screen.attroff(self._color_pair)

    def print_message(self, text: str, y: int = 1, x: int = 1):
        """Print message at specific position with color."""
        if self._screen:
            self._screen.attron(self._color_pair)
            self._screen.addstr(y, x, text)
            self._screen.attroff(self._color_pair)

    def print_line(self, y: int, x: int = 0, length: int = None):
        """Print separator line."""
        if self._screen:
            line = "=" * (length if length else 60)
            self._screen.attron(self._color_pair)
            self._screen.addstr(y, x, line)
            self._screen.attroff(self._color_pair)

    def create_window(self, height: int, width: int, y: int, x: int, title: Optional[str] = None) -> curses.window:
        """
        Create a bordered window.
        
        Args:
            height, width: Window dimensions
            y, x: Position
            title: Optional title line
            
        Returns:
            curses.window object
        """
        win = curses.newwin(height, width, y, x)
        win.box()
        win.keypad(True)  # Enable special keys
        
        if title:
            win.addstr(0, 1, title.center(width - 2))
            win.addstr(1, 0, "-" * (width - 2))
        
        return win

    def render_menu(self, options: List[Dict[str, Any]], 
                   default: Optional[int] = None,
                   highlighted: Optional[int] = None) -> int:
        """
        Render a numbered menu with options.
        
        Args:
            options: List of dictionaries with 'label' and optional 'description'
            default: Index of default option (appends '(default)')
            highlighted: Index of currently highlighted option
            
        Returns:
            Selected option index, or -1 if cancelled
        """
        if not self._screen:
            return -1

        # Create window for menu
        height, width = self._screen.getmaxyx()
        menu_height = len(options) + 4
        menu_width = max(max(len(opt.get('label', '')) for opt in options), 20) + 2
        
        y_offset = 2
        x_offset = 2
        menu_win = curses.newwin(menu_height, menu_width, y_offset, x_offset)
        menu_win.box()
        menu_win.keypad(True)
        
        # Title
        title = f"Select {self._title.lower()}"
        menu_win.addstr(0, 1, title.center(menu_width - 2))
        menu_win.addstr(1, 0, "-" * (menu_width - 2))
        
        # Options
        highlighted_idx = highlighted if highlighted is not None else 0
        
        for i, opt in enumerate(options):
            label = opt.get('label', '')
            desc = opt.get('description', '')
            
            # Build label with default marker
            marker = ""
            if default is not None and i == default:
                marker = " (default)"
            
            full_label = f"  {i}. {label}{marker}"
            
            if i == highlighted_idx:
                # Highlighted: reverse video
                menu_win.attron(curses.A_REVERSE | curses.A_BOLD)
                menu_win.addstr(i + 2, 0, full_label)
                if desc:
                    menu_win.addstr(i + 3, 0, desc)
                menu_win.attroff(curses.A_REVERSE | curses.A_BOLD)
            else:
                menu_win.attron(self._color_pair)
                menu_win.addstr(i + 2, 0, full_label)
                if desc:
                    menu_win.addstr(i + 3, 0, desc)
                menu_win.attroff(self._color_pair)
        
        # Footer instructions
        footer = "Use arrow keys to navigate, type number to select, Enter to confirm, q to cancel"
        menu_win.addstr(menu_height - 1, 0, footer, curses.A_REVERSE)
        
        # Show current position
        if highlighted_idx is not None and highlighted_idx >= 0:
            menu_win.attron(curses.A_REVERSE | curses.A_BOLD)
            menu_win.addstr(menu_height - 2, 0, f"Choice [{highlighted_idx}]:")
            menu_win.attroff(curses.A_REVERSE | curses.A_BOLD)
        
        menu_win.refresh()

        # Input handling
        while True:
            self.refresh()
            
            key = menu_win.getch()
            
            if key == 27 or key == ord('q') or key == curses.KEY_RESIZE:
                # Cancel
                self._screen.erase()
                return -1
            
            elif key == curses.KEY_UP or key == curses.KEY_PPAGE:
                # Move up or page up
                if highlighted_idx > 0:
                    highlighted_idx -= 1
                else:
                    highlighted_idx = len(options) - 1
                
            elif key == curses.KEY_DOWN or key == curses.KEY_NPAGE:
                # Move down or page down
                if highlighted_idx < len(options) - 1:
                    highlighted_idx += 1
                else:
                    highlighted_idx = 0
                
            elif key >= ord('0') and key <= ord('9'):
                # Type number
                try:
                    choice = int(chr(key)) - 1
                    if 0 <= choice < len(options):
                        highlighted_idx = choice
                except ValueError:
                    pass
            
            elif key == 10 or key == curses.KEY_ENTER:  # Enter
                # Confirm
                menu_win.erase()
                return highlighted_idx

            if highlighted_idx != menu_win.highlighted_idx:
                menu_win.highlighted_idx = highlighted_idx
                menu_win.refresh()

    def render_confirmation(self, message: str, default: bool = True) -> bool:
        """
        Render a confirmation prompt.
        
        Args:
            message: The message to display
            default: If True, Enter = yes, 'n' = no
            
        Returns:
            True if confirmed, False if cancelled
        """
        if not self._screen:
            return default  # Return default if no screen

        height, width = self._screen.getmaxyx()
        
        # Create window
        prompt_win = curses.newwin(4, width - 4, 1, 2)
        prompt_win.box()
        prompt_win.keypad(True)
        
        # Title
        prompt_win.addstr(0, 1, "Confirm".center(width - 4))
        prompt_win.addstr(1, 0, "-" * (width - 6))
        
        # Message
        prompt_win.attron(self._color_pair)
        prompt_win.addstr(2, 2, message)
        prompt_win.attroff(self._color_pair)
        
        # Prompt
        prompt_str = "Proceed? [Y/n]: "
        prompt_win.attron(curses.A_REVERSE | curses.A_BOLD)
        prompt_win.addstr(3, 2, prompt_str)
        prompt_win.attroff(curses.A_REVERSE | curses.A_BOLD)
        
        prompt_win.refresh()

        # Input handling
        while True:
            self.refresh()
            
            key = prompt_win.getch()
            
            if key == 27 or key == curses.KEY_RESIZE:
                # Cancel
                self._screen.erase()
                return not default  # Return inverse of default (no = False)
            
            elif key == 10 or key == curses.KEY_ENTER:  # Enter
                # Confirm (default yes)
                self._screen.erase()
                return True
            
            elif key == ord('y') or key == ord('Y'):
                # Confirm
                self._screen.erase()
                return True
            
            elif key == ord('n') or key == ord('N'):
                # Cancel
                self._screen.erase()
                return False

    def render_progress_bar(self, filename: str, current: int, total: int, 
                          percent: Optional[float] = None) -> None:
        """
        Render a progress bar for downloads.
        
        Args:
            filename: Name of file being downloaded
            current: Current bytes downloaded
            total: Total bytes
            percent: Optional pre-calculated percentage
        """
        if not self._screen:
            return

        height, width = self._screen.getmaxyx()
        
        # Create window
        bar_height = 6
        bar_width = min(50, width - 10)
        y_offset = height - bar_height - 2
        x_offset = 2
        
        bar_win = curses.newwin(bar_height, bar_width, y_offset, x_offset)
        bar_win.box()
        bar_win.keypad(True)
        
        # Title
        title = f"Download: {Path(filename).name}"
        bar_win.addstr(0, 1, title.center(bar_width - 2))
        bar_win.addstr(1, 0, "-" * (bar_width - 2))
        
        # Calculate bar
        if total > 0:
            progress = min(current / total * bar_width, bar_width - 1)
            empty_bar = " " * (bar_width - 1)
            filled_bar = "█" * int(progress)
            remaining_bar = "░" * (bar_width - 1 - int(progress))
            
            # Status line
            status = f"{current:,}/{total:,} bytes ({percent or current/total*100:.1f}% - {current/1024/1024:.1f}MB/{total/1024/1024:.1f}MB)"
            bar_win.attron(self._color_pair)
            bar_win.addstr(2, 0, status)
            bar_win.attroff(self._color_pair)
            
            # Bar
            bar_win.attron(self._color_pair)
            bar_win.addstr(3, 0, filled_bar + remaining_bar)
            bar_win.attroff(self._color_pair)
        else:
            # Spinner for indeterminate progress
            spinner = ["◐", "◓", "◑", "◒"]
            spinner_idx = int(curses.time() / 100) % 4
            
            bar_win.attron(self._color_pair)
            bar_win.addstr(2, 0, f"Downloading {Path(filename).name}... ({spinner[spinner_idx]})")
            bar_win.attroff(self._color_pair)
        
        bar_win.addstr(4, 0, "Press any key to continue...", curses.A_REVERSE)
        bar_win.refresh()
        
        # Wait for key
        self.refresh()
        self._screen.getch()
        bar_win.erase()

    def render_success(self, message: str) -> None:
        """Render success message."""
        if not self._screen:
            print(message)
            return

        height, width = self._screen.getmaxyx()
        
        # Create window
        msg_height = 4
        y_offset = height - msg_height - 2
        x_offset = 2
        
        msg_win = curses.newwin(msg_height, width - 4, y_offset, x_offset)
        msg_win.box()
        msg_win.keypad(True)
        
        # Title
        msg_win.attron(curses.A_REVERSE | curses.A_BOLD)
        msg_win.addstr(0, 1, "Success".center(width - 4))
        msg_win.attroff(curses.A_REVERSE | curses.A_BOLD)
        
        # Message
        msg_win.attron(self._color_pair)
        msg_win.addstr(2, 2, message)
        msg_win.attroff(self._color_pair)
        
        msg_win.addstr(3, 2, "Press any key to continue...", curses.A_REVERSE)
        msg_win.refresh()
        
        # Wait for key
        self.refresh()
        self._screen.getch()
        msg_win.erase()

    def render_error(self, message: str) -> None:
        """Render error message."""
        if not self._screen:
            print(f"Error: {message}")
            return

        height, width = self._screen.getmaxyx()
        
        # Create window
        msg_height = 4
        y_offset = height - msg_height - 2
        x_offset = 2
        
        msg_win = curses.newwin(msg_height, width - 4, y_offset, x_offset)
        msg_win.box()
        msg_win.keypad(True)
        
        # Title
        msg_win.attron(curses.A_REVERSE | curses.A_BOLD)
        msg_win.addstr(0, 1, "Error".center(width - 4))
        msg_win.attroff(curses.A_REVERSE | curses.A_BOLD)
        
        # Message
        msg_win.attron(curses.color_pair(1))  # Green on black
        msg_win.addstr(2, 2, message)
        msg_win.attroff(curses.color_pair(1))
        
        msg_win.addstr(3, 2, "Press any key to continue...", curses.A_REVERSE)
        msg_win.refresh()
        
        # Wait for key
        self.refresh()
        self._screen.getch()
        msg_win.erase()

    def print_simple_menu(self, options: List[str], 
                         default: Optional[int] = None,
                         highlighted: Optional[int] = None) -> Optional[int]:
        """
        Simple menu without window - just print to screen.
        
        Args:
            options: List of option labels
            default: Index of default option
            highlighted: Currently highlighted index
            
        Returns:
            Selected index, or None if cancelled
        """
        if not self._screen:
            # Fallback to console
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            choice = input(f"Choice [{highlighted if highlighted is not None else 0}]: ").strip()
            try:
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except ValueError:
                return None

        height, width = self._screen.getmaxyx()
        
        # Print at current position
        y, x = self._screen.getyx()
        
        for i, opt in enumerate(options):
            marker = " (default)" if default is not None and i == default else ""
            
            if i == highlighted:
                self._screen.attron(curses.A_REVERSE | curses.A_BOLD)
                self._screen.addstr(y + i + 1, x, f"  {i}. {opt}{marker}")
                self._screen.attroff(curses.A_REVERSE | curses.A_BOLD)
            else:
                self._screen.attron(self._color_pair)
                self._screen.addstr(y + i + 1, x, f"  {i}. {opt}{marker}")
                self._screen.attroff(self._color_pair)

        # Show current selection
        if highlighted is not None:
            self._screen.attron(curses.A_REVERSE | curses.A_BOLD)
            self._screen.addstr(y + len(options) + 2, x, f"Choice [{highlighted}]:")
            self._screen.attroff(curses.A_REVERSE | curses.A_BOLD)

        self._screen.refresh()

        # Input handling
        while True:
            self.refresh()
            key = self._screen.getch()
            
            if key == 27 or key == ord('q'):
                return None
            elif key == curses.KEY_UP:
                if highlighted is not None and highlighted > 0:
                    highlighted -= 1
                else:
                    highlighted = len(options) - 1
            elif key == curses.KEY_DOWN:
                if highlighted is not None and highlighted < len(options) - 1:
                    highlighted += 1
                else:
                    highlighted = 0
            elif key >= ord('0') and key <= ord('9'):
                try:
                    choice = int(chr(key)) - 1
                    if 0 <= choice < len(options):
                        highlighted = choice
                except ValueError:
                    pass
            elif key == 10 or key == curses.KEY_ENTER:
                return highlighted

            if highlighted != self._screen.highlighted_idx:
                self._screen.highlighted_idx = highlighted
                self._screen.refresh()

    def get_input(self, prompt: str) -> str:
        """Get user input with confirmation styling."""
        if not self._screen:
            return input(f"{prompt}: ").strip()

        height, width = self._screen.getmaxyx()
        y, x = self._screen.getyx()
        
        # Print prompt
        self._screen.attron(self._color_pair)
        self._screen.addstr(y, x, prompt)
        self._screen.attroff(self._color_pair)
        self._screen.refresh()

        # Get input
        input_str = self._screen.getstr(x + len(prompt), y, width - len(prompt)).decode()
        return input_str.strip()

    def get_numbered_input(self, options: List[str], 
                         default: Optional[int] = None) -> Optional[int]:
        """Get numbered input from user."""
        if not self._screen:
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            choice = input(f"Choice [{default if default is not None else 0}]: ").strip()
            try:
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except ValueError:
                return None

        height, width = self._screen.getmaxyx()
        y, x = self._screen.getyx()
        
        # Print options
        for i, opt in enumerate(options):
            marker = " (default)" if default is not None and i == default else ""
            
            if i == default:
                self._screen.attron(curses.A_REVERSE | curses.A_BOLD)
                self._screen.addstr(y + i + 1, x, f"  {i}. {opt}{marker}")
                self._screen.attroff(curses.A_REVERSE | curses.A_BOLD)
            else:
                self._screen.attron(self._color_pair)
                self._screen.addstr(y + i + 1, x, f"  {i}. {opt}{marker}")
                self._screen.attroff(self._color_pair)

        self._screen.refresh()

        # Get input
        input_str = self._screen.getstr(x + len(f"\nChoice [{default if default is not None else 0}]: "), y + len(options) + 1, width).decode()
        return int(input_str) if input_str.isdigit() and 0 <= int(input_str) < len(options) else None
