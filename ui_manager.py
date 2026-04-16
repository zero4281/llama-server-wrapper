#!/usr/bin/env python3
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
    - Fallback to console output if curses fails
    """

    # Constants
    WIDTH = 60
    TIMEOUT = 100
    
    def __init__(self, title: Optional[str] = None):
        """
        Initialize the UI manager.
        
        Args:
            title: Optional title for windows
        """
        self._screen = None
        self._title = title or "Llama Server Wrapper"
        self._color_pair = None
        self._using_curses = False
        
        try:
            # Initialize curses
            self._screen = curses.initscr()
            
            # Use alternate screen buffer for full-screen UI
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            self._color_pair = curses.color_pair(1) | curses.A_BOLD
            
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Reverse video
            
            # Set terminal mode for interactive curses
            try:
                curses.cbreak()
            except:
                pass
            
            curses.noecho()
            curses.curs_set(0)  # Hide cursor
            self._screen.timeout(100)  # 100ms timeout for key refresh
            
            self._using_curses = True
            
        except (curses.error, OSError, IOError) as e:
            # If curses fails, immediately end curses and fall back to console
            # First, try to reset terminal state
            try:
                curses.reset_prog_mode()
                curses.reset_pair_matrix()
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass
            
            try:
                curses.curs_set(1)
            except:
                pass
            
            try:
                curses.endwin()
            except:
                pass
            
            print(f"Curses initialization failed: {e}", file=sys.stderr)
            self._using_curses = False
            self._screen = None
            self._color_pair = None

    def _cleanup_terminal(self):
        """Clean up curses and restore terminal."""
        if self._using_curses and self._screen:
            try:
                # Reset terminal mode
                curses.echo()
                curses.nocbreak()
                curses.keypad(False)
                curses.curs_set(1)  # Show cursor
                # Reset colors
                if hasattr(curses, 'reset_pair_matrix'):
                    curses.reset_pair_matrix()
                curses.endwin()
            except:
                # Force hard reset
                try:
                    curses.endwin()
                except:
                    pass
            finally:
                self._screen = None
                self._color_pair = None
                self._using_curses = False
                # Try to reset stty if available
                try:
                    import subprocess
                    subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                except:
                    pass

    def __del__(self):
        """Cleanup curses resources."""
        self._cleanup_terminal()

    def refresh(self):
        """Refresh screen."""
        if self._using_curses and self._screen:
            try:
                self._screen.refresh()
            except:
                try:
                    self._cleanup_terminal()
                except:
                    pass

    def clear(self):
        """Clear screen."""
        if self._using_curses and self._screen:
            try:
                self._screen.erase()
            except:
                pass

    def print_header(self, text: str):
        """Print header with color."""
        if not self._using_curses:
            print(f"\n{'='*self.WIDTH}\n{text.center(self.WIDTH)}\n{'='*self.WIDTH}")
            return
            
        if not self._screen:
            return
            
        try:
            self._screen.attron(self._color_pair)
            self._screen.addstr(0, 0, text.ljust(self.WIDTH))
            self._screen.attroff(self._color_pair)
            self._screen.refresh()
        except:
            print(f"\n{'='*self.WIDTH}\n{text.center(self.WIDTH)}\n{'='*self.WIDTH}")

    def print_message(self, text: str, y: int = 1, x: int = 1):
        """Print message at specific position with color."""
        if not self._using_curses:
            print(text)
            return
            
        if not self._screen:
            return
            
        try:
            self._screen.attron(self._color_pair)
            self._screen.addstr(y, x, text)
            self._screen.attroff(self._color_pair)
            self._screen.refresh()
        except:
            print(text)

    def print_line(self, y: int, x: int = 0, length: int = None):
        """Print separator line."""
        if not self._using_curses:
            print("-" * (length or 60))
            return
            
        if not self._screen:
            return
            
        try:
            line = "=" * (length if length else 60)
            self._screen.attron(self._color_pair)
            self._screen.addstr(y, x, line)
            self._screen.attroff(self._color_pair)
            self._screen.refresh()
        except:
            print("-" * (length or 60))

    def create_window(self, height: int, width: int, y: int, x: int, title: Optional[str] = None) -> Optional[curses.window]:
        """
        Create a bordered window.
        
        Args:
            height, width: Window dimensions
            y, x: Position
            title: Optional title line
            
        Returns:
            curses.window object
        """
        if not self._using_curses:
            return None
            
        if not self._screen:
            return None
            
        try:
            win = curses.newwin(height, width, y, x)
            win.box()
            
            if title:
                win.addstr(0, 1, title.center(width - 2))
                win.addstr(1, 0, "-" * (width - 2))
            
            return win
        except:
            return None

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
        # Console fallback
        if not self._using_curses or not self._screen:
            # Reset terminal
            try:
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                curses.curs_set(1)
                curses.endwin()
            except:
                pass
            
            # Clear and display menu
            print("\033[2J\033[H", end="")
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                label = opt.get('label', '')
                desc = opt.get('description', '')
                full_label = f"  {i}. {label}{marker}"
                print(full_label)
                if desc:
                    print(f"     {desc}")
            
            # Prompt with timeout
            print(f"Choice [{highlighted if highlighted is not None else 0}]: ", end="", flush=True)
            try:
                import select
                if sys.stdin.isatty():
                    ready, _, _ = select.select([sys.stdin], [], [], 2.0)
                    if ready:
                        choice_str = sys.stdin.readline().strip()
                    else:
                        choice_str = ""
                else:
                    choice_str = sys.stdin.readline().strip()
            except:
                choice_str = ""
            
            try:
                idx = int(choice_str)
                return idx if 0 <= idx < len(options) else -1
            except ValueError:
                return -1

        # Create menu window
        self._screen.erase()
        height, width = self._screen.getmaxyx()
        menu_height = len(options) + 4
        menu_width = max(max(len(opt.get('label', '')) for opt in options), 20) + 2
        
        y_offset = 2
        x_offset = 2
        highlighted_idx = highlighted if highlighted is not None else 0
        
        # Define redraw function
        def redraw(win, hi_idx):
            try:
                win.erase()
                title = f"Select {self._title.lower()}"
                win.addstr(0, 1, title.center(menu_width - 2))
                win.addstr(1, 0, "-" * (menu_width - 2))
                for i, opt in enumerate(options):
                    label = opt.get('label', '')
                    desc = opt.get('description', '')
                    marker = " (default)" if default is not None and i == default else ""
                    full_label = f"  {i}. {label}{marker}"
                    if i == hi_idx:
                        win.attron(self._color_pair | curses.A_BOLD)
                        win.addstr(i + 2, 0, full_label)
                        if desc:
                            win.addstr(i + 3, 0, desc)
                        win.attroff(self._color_pair | curses.A_BOLD)
                    else:
                        win.attron(self._color_pair)
                        win.addstr(i + 2, 0, full_label)
                        if desc:
                            win.addstr(i + 3, 0, desc)
                        win.attroff(self._color_pair)
                footer = "Use arrow keys to navigate, type number to select, Enter to confirm, q to cancel"
                truncated_footer = footer[:menu_width - 2] if len(footer) > menu_width - 2 else footer
                win.addstr(menu_height - 1, 0, truncated_footer, curses.A_REVERSE)
                if hi_idx is not None and hi_idx >= 0:
                    win.attron(self._color_pair | curses.A_BOLD)
                    win.addstr(menu_height - 2, 0, f"Choice [{hi_idx}]:")
                    win.attroff(self._color_pair | curses.A_BOLD)
                win.refresh()
            except curses.error:
                self._screen.refresh()

        try:
            menu_win = curses.newwin(menu_height, menu_width, y_offset, x_offset)
            menu_win.box()
            menu_win.keypad(True)
        except curses.error:
            try:
                self._cleanup_terminal()
            except:
                pass
            return -1

        # Input loop
        try:
            while True:
                try:
                    key = menu_win.getch()
                except (curses.error, KeyboardInterrupt):
                    try:
                        self._cleanup_terminal()
                    except:
                        pass
                    return -1
                
                # Handle keys
                if key == 27 or key == ord('q') or key == curses.KEY_RESIZE:
                    # Cancel
                    try:
                        self._screen.erase()
                    except:
                        pass
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
                
                elif key == 10 or key == curses.KEY_ENTER:
                    # Confirm
                    return highlighted_idx
                
                elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                    # Backspace - cancel
                    return -1
                
                # Timeout - redraw to refresh display
                else:
                    redraw(menu_win, highlighted_idx)
                
                # Redraw menu
                redraw(menu_win, highlighted_idx)
                
        except curses.error:
            try:
                self._cleanup_terminal()
            except:
                pass
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            try:
                choice = input(f"Choice [{highlighted if highlighted is not None else 0}]: ").strip()
                idx = int(choice)
                return idx if 0 <= idx < len(options) else -1
            except Exception:
                return -1
            try:
                self._cleanup_terminal()
            except:
                pass
            return -1

    def render_confirmation(self, message: str, default: bool = True) -> bool:
        """
        Render a confirmation prompt.
        
        Args:
            message: The message to display
            default: If True, Enter = yes, 'n' = no
            
        Returns:
            True if confirmed, False if cancelled
        """
        # Final safety check for render_menu - ensure we return a valid integer
        if not self._using_curses:
            # Fallback for any unexpected error in render_menu
            import subprocess
            try:
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass
            return -1
        if not self._screen:
            return -1
        return -1
        # Ensure terminal is reset before displaying prompt
        if not self._using_curses:
            # Use console fallback with proper terminal reset
            import subprocess
            try:
                # Reset terminal to cooked mode
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass  # Ignore stty errors
            
            # Clear screen and move to beginning
            print("\033[2J\033[H", end="")
            
            print(f"\n{message}")
            print("Proceed? [Y/n]: ", end="", flush=True)
            
            try:
                # Use select to timeout after 2 seconds for responsiveness
                import select
                
                if sys.stdin.isatty():
                    # Read with timeout
                    ready, _, _ = select.select([sys.stdin], [], [], 2.0)
                    if ready:
                        response = sys.stdin.readline().strip().lower()
                    else:
                        # No input in 2 seconds - assume default
                        response = ""
                else:
                    response = sys.stdin.readline().strip().lower()
            except:
                response = ""
            
            if response in ('', 'y', 'yes'):
                return True
            return False

        if not self._screen:
            return default

        height, width = self._screen.getmaxyx()
        
        # Create window
        try:
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
            self.refresh()

            # Input handling
            while True:
                self.refresh()
                
                key = prompt_win.getch()
                
                if key == 27 or key == curses.KEY_RESIZE:
                    # Cancel
                    self._screen.erase()
                    return False
                
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

        except curses.error:
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            choice = input(f"Choice [{highlighted if highlighted is not None else 0}]: ").strip()
            try:
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except ValueError:
                return None
            try:
                self._cleanup_terminal()
            except:
                pass
            return default

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
        if not self._using_curses:
            # Use console fallback with proper terminal reset
            import subprocess
            try:
                # Reset terminal to cooked mode
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass  # Ignore stty errors
            
            # Clear screen and move to beginning
            print("\033[2J\033[H", end="")
            
            print(f"\nDownloading {Path(filename).name}... {current}/{total} ({percent or (current/total*100 if total else 0.0):.1f}%)")
            print("Press any key to continue...", end="", flush=True)
            
            try:
                # Use select to timeout after 1 second for responsiveness
                import select
                
                if sys.stdin.isatty():
                    # Read with timeout
                    ready, _, _ = select.select([sys.stdin], [], [], 1.0)
                    if ready:
                        # Consume input but don't block
                        sys.stdin.readline()
                    # else: timeout - just continue
                else:
                    sys.stdin.readline()
            except:
                pass
            return

        if not self._screen:
            return

        height, width = self._screen.getmaxyx()
        
        # Create window
        bar_height = 6
        bar_width = min(50, width - 10)
        y_offset = height - bar_height - 2
        x_offset = 2
        
        try:
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
        except curses.error:
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            choice = input(f"Choice [{highlighted if highlighted is not None else 0}]: ").strip()
            try:
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except ValueError:
                return None
            try:
                self._cleanup_terminal()
            except:
                pass
            print(f"\nDownloading {Path(filename).name}... {current}/{total} ({percent or (current/total*100 if total else 0.0):.1f}%)")
            input("Press Enter to continue...")

    def render_success(self, message: str) -> None:
        """Render success message."""
        if not self._using_curses:
            # Use console fallback with proper terminal reset
            import subprocess
            try:
                # Reset terminal to cooked mode
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass  # Ignore stty errors
            
            # Clear screen and move to beginning
            print("\033[2J\033[H", end="")
            
            print(f"\n{'='*60}\n{message.center(60)}\n{'='*60}")
            print("Press any key to continue...", end="", flush=True)
            
            try:
                # Use select to timeout after 1 second for responsiveness
                import select
                
                if sys.stdin.isatty():
                    # Read with timeout
                    ready, _, _ = select.select([sys.stdin], [], [], 1.0)
                    if ready:
                        sys.stdin.readline()
            except:
                pass
            return

        if not self._screen:
            print(message)
            return

        height, width = self._screen.getmaxyx()
        
        # Create window
        msg_height = 4
        y_offset = height - msg_height - 2
        x_offset = 2
        
        try:
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
        except curses.error:
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            choice = input(f"Choice [{highlighted if highlighted is not None else 0}]: ").strip()
            try:
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except ValueError:
                return None
            try:
                self._cleanup_terminal()
            except:
                pass
            print(f"\n{'='*60}\n{message.center(60)}\n{'='*60}")
            input("Press Enter to continue...")

    def render_error(self, message: str) -> None:
        """Render error message."""
        if not self._using_curses:
            # Use console fallback with proper terminal reset
            import subprocess
            try:
                # Reset terminal to cooked mode
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass  # Ignore stty errors
            
            # Clear screen and move to beginning
            print("\033[2J\033[H", end="")
            
            print(f"\n{'='*60}\nError: {message.center(60)}\n{'='*60}")
            print("Press any key to continue...", end="", flush=True)
            
            try:
                # Use select to timeout after 1 second for responsiveness
                import select
                
                if sys.stdin.isatty():
                    # Read with timeout
                    ready, _, _ = select.select([sys.stdin], [], [], 1.0)
                    if ready:
                        sys.stdin.readline()
            except:
                pass
            return

        if not self._screen:
            print(f"Error: {message}")
            return

        height, width = self._screen.getmaxyx()
        
        # Create window
        msg_height = 4
        y_offset = height - msg_height - 2
        x_offset = 2
        
        try:
            msg_win = curses.newwin(msg_height, width - 4, y_offset, x_offset)
            msg_win.box()
            msg_win.keypad(True)
            
            # Title
            msg_win.attron(curses.A_REVERSE | curses.A_BOLD)
            msg_win.addstr(0, 1, "Error".center(width - 4))
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
        except curses.error:
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            choice = input(f"Choice [{highlighted if highlighted is not None else 0}]: ").strip()
            try:
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except ValueError:
                return None
            try:
                self._cleanup_terminal()
            except:
                pass
            print(f"\n{'='*60}\nError: {message.center(60)}\n{'='*60}")
            input("Press Enter to continue...")

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
        if not self._using_curses:
            # Ensure terminal is reset before printing
            self._cleanup_terminal()
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
        
        try:
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

                if highlighted is not None:
                    self._screen.refresh()

        except curses.error:
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            choice = input(f"Choice [{highlighted if highlighted is not None else 0}]: ").strip()
            try:
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except ValueError:
                return None
            try:
                self._cleanup_terminal()
            except:
                pass
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            choice = input(f"Choice [{highlighted if highlighted is not None else 0}]: ").strip()
            try:
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except ValueError:
                return None

    def get_input(self, prompt: str) -> str:
        """Get user input with confirmation styling."""
        if not self._using_curses:
            # Use console fallback with proper terminal reset
            import subprocess
            try:
                # Reset terminal to cooked mode
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass  # Ignore stty errors
            
            # Clear screen and move to beginning
            print("\033[2J\033[H", end="")
            
            try:
                # Use select to timeout after 2 seconds for responsiveness
                import select
                
                if sys.stdin.isatty():
                    # Read with timeout
                    ready, _, _ = select.select([sys.stdin], [], [], 2.0)
                    if ready:
                        return sys.stdin.readline().strip()
                    else:
                        return ""
                else:
                    return sys.stdin.readline().strip()
            except:
                return ""

        height, width = self._screen.getmaxyx()
        y, x = self._screen.getyx()
        
        # Print prompt
        self._screen.attron(self._color_pair)
        self._screen.addstr(y, x, prompt)
        self._screen.attroff(self._color_pair)
        self._screen.refresh()

        try:
            # Get input
            input_str = self._screen.getstr(x + len(prompt), y, width - len(prompt)).decode()
            return input_str.strip()
        except curses.error:
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            choice = input(f"Choice [{highlighted if highlighted is not None else 0}]: ").strip()
            try:
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except ValueError:
                return None
            try:
                self._cleanup_terminal()
            except:
                pass
            return ""

    def get_numbered_input(self, options: List[str], 
                          default: Optional[int] = None) -> Optional[int]:
        """Get numbered input from user."""
        if not self._using_curses:
            # Use console fallback with proper terminal reset
            import subprocess
            try:
                # Reset terminal to cooked mode
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass  # Ignore stty errors
            
            # Clear screen and move to beginning
            print("\033[2J\033[H", end="")
            
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            print(f"Choice [{default if default is not None else 0}]: ", end="", flush=True)
            
            try:
                # Use select to timeout after 2 seconds for responsiveness
                import select
                
                if sys.stdin.isatty():
                    # Read with timeout
                    ready, _, _ = select.select([sys.stdin], [], [], 2.0)
                    if ready:
                        choice = sys.stdin.readline().strip()
                    else:
                        choice = ""
                else:
                    choice = sys.stdin.readline().strip()
                
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except (ValueError, EOFError):
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