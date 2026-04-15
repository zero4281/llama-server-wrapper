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
            # Check if curses is already initialized
            is_curses_initialized = curses.has_ungetch() if hasattr(curses, 'has_ungetch') else False
            
            if is_curses_initialized:
                # Curses is already initialized, reuse existing screen
                self._using_curses = True
                self._screen = curses.getscrptr()
                return
            
            # Initialize curses
            try:
                self._screen = curses.initscr()
                
                # Use alternate screen buffer for full-screen UI
                curses.start_color()
                # Set color pair: black background, green text
                curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
                self._color_pair = curses.color_pair(1) | curses.A_BOLD
                
                # Initialize colors for reverse video
                curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Reverse video
                
                # Set terminal mode for interactive curses
                # Put terminal in raw mode BEFORE any menu is created
                curses.cbreak()
                curses.noecho()
                curses.curs_set(0)  # Hide cursor
                self._screen.timeout(100)  # 100ms timeout for key refresh
                
                self._using_curses = True
            except curses.error:
                # If curses fails, immediately end curses and fall back to console
                try:
                    curses.endwin()
                except:
                    pass
                # Fall through to fallback handling below
            except (curses.error, OSError, IOError) as e:
                # If curses fails, immediately end curses and fall back to console
                try:
                    curses.endwin()
                except:
                    pass
                # Restore terminal to normal state
                try:
                    curses.echo()
                    curses.nocbreak()
                    curses.curs_set(1)
                except:
                    pass
                print(f"Curses initialization failed: {e}", file=sys.stderr)
                self._using_curses = False
                self._screen = None
                self._color_pair = None
            
        except (curses.error, OSError, IOError) as e:
            # If curses fails, immediately end curses and fall back to console
            try:
                curses.endwin()
            except:
                pass
            # Ensure terminal is reset to non-raw state BEFORE any console output
            try:
                import termios
                import fcntl
                fd = sys.stdin.fileno()
                tty = fcntl.ioctl(fd, termios.TIOCGWINSZ, None) is not None
                if tty:
                    # This is a tty, reset terminal attributes
                    termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))
            except:
                pass
            # Also try curses methods as fallback
            try:
                curses.echo()
                curses.nocbreak()
                curses.curs_set(1)
            except:
                pass
            print(f"Curses initialization failed: {e}", file=sys.stderr)
            self._using_curses = False
            self._screen = None
            self._color_pair = None
            # The methods will use console output

    def __del__(self):
        """Cleanup curses resources."""
        self._close()

    def _close(self):
        """Close curses and restore terminal."""
        if self._using_curses and self._screen:
            try:
                # Restore terminal settings
                curses.echo()
                curses.nocbreak()
                curses.keypad(False)
                curses.curs_set(1)  # Show cursor
                
                # End curses
                curses.endwin()
            except:
                pass
            finally:
                # Ensure screen is None to prevent double cleanup
                self._screen = None

    def refresh(self):
        """Refresh screen."""
        if self._using_curses and self._screen:
            try:
                self._screen.refresh()
            except:
                # If refresh fails, try to restore terminal
                try:
                    self._close()
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
            print(f"\n{'='*60}\n{text.center(60)}\n{'='*60}")
            return
            
        if not self._screen:
            return
            
        try:
            self._screen.attron(self._color_pair)
            self._screen.addstr(0, 0, text.ljust(60))
            self._screen.attroff(self._color_pair)
            self._screen.refresh()
        except:
            # Fallback to console
            print(f"\n{'='*60}\n{text.center(60)}\n{'='*60}")

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
            # Fallback to console
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
            # Fallback to console
            print("-" * (length or 60))

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

    def _put_in_raw_mode(self):
        """Put terminal into raw mode."""
        if self._using_curses and self._screen:
            try:
                # Put terminal in raw mode
                curses.cbreak()
                curses.noecho()
                curses.curs_set(0)
                curses.keypad(True)
            except curses.error:
                # If we can't put terminal in raw mode, it might already be in raw mode
                # or there's an issue. Try to restore terminal.
                self._restore_terminal()
                return False
            except:
                # If we can't put terminal in raw mode, fall back to console
                self._restore_terminal()
                return False
            return True
        return False

    def _restore_terminal(self):
        """Restore terminal to normal state."""
        if self._using_curses and self._screen:
            try:
                curses.echo()
                curses.nocbreak()
                curses.keypad(False)
                curses.curs_set(1)
                curses.endwin()
            except:
                pass
            finally:
                self._screen = None
                self._color_pair = None
                self._using_curses = False

    def _ensure_raw_mode(self):
        """Ensure terminal is in raw mode before menu."""
        if not self._using_curses:
            # Terminal is not in curses mode, so we're fine
            return True
        
        # Terminal is already in curses mode, so it should be in raw mode
        return True



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
        # Put terminal into raw mode BEFORE creating menu
        self._put_in_raw_mode()
        
        if not self._using_curses:
            # Fallback to console
            # Ensure terminal is reset to non-raw state BEFORE printing menu
            import sys
            try:
                import termios
                import fcntl
                fd = sys.stdin.fileno()
                tty = fcntl.ioctl(fd, termios.TIOCGWINSZ, None) is not None
                if tty:
                    # This is a tty, reset terminal attributes
                    termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))
            except:
                pass
            # Also try curses methods as fallback
            try:
                curses.echo()
                curses.nocbreak()
                curses.curs_set(1)
            except:
                pass
            
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                label = opt.get('label', '')
                desc = opt.get('description', '')
                full_label = f"  {i}. {label}{marker}"
                print(f"{full_label}")
                if desc:
                    print(f"     {desc}")
            
            # Use sys.stdin.readline() instead of input() for better compatibility
            try:
                choice_str = sys.stdin.readline().strip()
            except:
                choice_str = ""
            
            try:
                idx = int(choice_str)
                return idx if 0 <= idx < len(options) else -1
            except ValueError:
                return -1

        if not self._screen:
            return -1

        # Clear screen before displaying menu
        self._screen.erase()
        
        # Create window for menu
        height, width = self._screen.getmaxyx()
        menu_height = len(options) + 4
        menu_width = max(max(len(opt.get('label', '')) for opt in options), 20) + 2
        
        y_offset = 2
        x_offset = 2
        try:
            menu_win = curses.newwin(menu_height, menu_width, y_offset, x_offset)
            menu_win.box()
            menu_win.keypad(True)
            
            # Helper function to redraw the entire menu
            def _draw_menu(hi_idx):
                # Clear the window
                menu_win.erase()
                
                # Title
                title = f"Select {self._title.lower()}"
                menu_win.addstr(0, 1, title.center(menu_width - 2))
                menu_win.addstr(1, 0, "-" * (menu_width - 2))
                
                # Options
                for i, opt in enumerate(options):
                    label = opt.get('label', '')
                    desc = opt.get('description', '')
                    
                    # Build label with default marker
                    marker = ""
                    if default is not None and i == default:
                        marker = " (default)"
                    
                    full_label = f"  {i}. {label}{marker}"
                    
                    if i == hi_idx:
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
                truncated_footer = footer[:menu_width - 2] if len(footer) > menu_width - 2 else footer
                menu_win.addstr(menu_height - 1, 0, truncated_footer, curses.A_REVERSE)
                
                # Show current position
                if hi_idx is not None and hi_idx >= 0:
                    menu_win.attron(curses.A_REVERSE | curses.A_BOLD)
                    menu_win.addstr(menu_height - 2, 0, f"Choice [{hi_idx}]:")
                    menu_win.attroff(curses.A_REVERSE | curses.A_BOLD)
                
                menu_win.refresh()
                self.refresh()
            
            # Initial draw
            _draw_menu(highlighted_idx if highlighted_idx is not None else 0)

            # Input handling
            while True:
                # Use getch with timeout to allow for processing
                try:
                    key = menu_win.getch(timeout=100)
                except:
                    key = -1
                
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
                    return highlighted_idx
                
                elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                    # Backspace - handle as cancel
                    return -1
                
                # Redraw menu with updated highlight
                _draw_menu(highlighted_idx)

        except:
            # If anything fails, fall back to console
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
        if not self._using_curses:
            # Fallback to console
            # Ensure terminal is reset to non-raw state BEFORE printing confirmation
            import sys
            try:
                import termios
                import fcntl
                fd = sys.stdin.fileno()
                tty = fcntl.ioctl(fd, termios.TIOCGWINSZ, None) is not None
                if tty:
                    # This is a tty, reset terminal attributes
                    termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))
            except:
                pass
            # Also try curses methods as fallback
            try:
                curses.echo()
                curses.nocbreak()
                curses.curs_set(1)
            except:
                pass
            
            print(f"\n{message}")
            # Use sys.stdin.readline() instead of input() for better compatibility
            try:
                response = sys.stdin.readline().strip().lower()
            except:
                response = ""
            
            if response in ('', 'y', 'yes'):
                return True
            return False

        if not self._screen:
            return default  # Return default if no screen

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

        except:
            # If anything fails, fall back to console
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
            # Fallback to console
            # Ensure terminal is reset to non-raw state BEFORE printing
            import sys
            try:
                import termios
                import fcntl
                fd = sys.stdin.fileno()
                tty = fcntl.ioctl(fd, termios.TIOCGWINSZ, None) is not None
                if tty:
                    # This is a tty, reset terminal attributes
                    termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))
            except:
                pass
            # Also try curses methods as fallback
            try:
                curses.echo()
                curses.nocbreak()
                curses.curs_set(1)
            except:
                pass
            
            print(f"\nDownloading {Path(filename).name}... {current}/{total} ({percent or current/total*100:.1f}%)")
            # Use sys.stdin.readline() instead of input() for better compatibility
            try:
                input("Press Enter to continue...")
            except EOFError:
                pass  # Handle EOF gracefully
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
        except:
            # If anything fails, fall back to console
            print(f"\nDownloading {Path(filename).name}... {current}/{total} ({percent or current/total*100:.1f}%)")
            input("Press Enter to continue...")

    def render_success(self, message: str) -> None:
        """Render success message."""
        if not self._using_curses:
            # Ensure terminal is reset to non-raw state BEFORE printing
            import sys
            try:
                import termios
                import fcntl
                fd = sys.stdin.fileno()
                tty = fcntl.ioctl(fd, termios.TIOCGWINSZ, None) is not None
                if tty:
                    termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))
            except:
                pass
            try:
                curses.echo()
                curses.nocbreak()
                curses.curs_set(1)
            except:
                pass
            
            print(f"\n{'='*60}\n{message.center(60)}\n{'='*60}")
            try:
                input("Press Enter to continue...")
            except EOFError:
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
        except:
            # If anything fails, fall back to console
            print(f"\n{'='*60}\n{message.center(60)}\n{'='*60}")
            input("Press Enter to continue...")

    def render_error(self, message: str) -> None:
        """Render error message."""
        if not self._using_curses:
            # Ensure terminal is reset to non-raw state BEFORE printing
            import sys
            try:
                import termios
                import fcntl
                fd = sys.stdin.fileno()
                tty = fcntl.ioctl(fd, termios.TIOCGWINSZ, None) is not None
                if tty:
                    termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))
            except:
                pass
            try:
                curses.echo()
                curses.nocbreak()
                curses.curs_set(1)
            except:
                pass
            
            print(f"\n{'='*60}\nError: {message.center(60)}\n{'='*60}")
            try:
                input("Press Enter to continue...")
            except EOFError:
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
            msg_win.attron(curses.color_pair(1))  # Green on black
            msg_win.addstr(2, 2, message)
            msg_win.attroff(curses.color_pair(1))
            
            msg_win.addstr(3, 2, "Press any key to continue...", curses.A_REVERSE)
            msg_win.refresh()
            
            # Wait for key
            self.refresh()
            self._screen.getch()
            msg_win.erase()
        except:
            # If anything fails, fall back to console
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

        except:
            # If anything fails, fall back to console
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
            # Ensure terminal is reset to non-raw state BEFORE getting input
            import sys
            try:
                import termios
                import fcntl
                fd = sys.stdin.fileno()
                tty = fcntl.ioctl(fd, termios.TIOCGWINSZ, None) is not None
                if tty:
                    termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))
            except:
                pass
            try:
                curses.echo()
                curses.nocbreak()
                curses.curs_set(1)
            except:
                pass
            
            try:
                return input(f"{prompt}: ").strip()
            except EOFError:
                return ""

        if not self._screen:
            # Ensure terminal is reset to non-raw state BEFORE getting input
            import sys
            try:
                import termios
                import fcntl
                fd = sys.stdin.fileno()
                tty = fcntl.ioctl(fd, termios.TIOCGWINSZ, None) is not None
                if tty:
                    termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))
            except:
                pass
            try:
                curses.echo()
                curses.nocbreak()
                curses.curs_set(1)
            except:
                pass
            
            try:
                return input(f"{prompt}: ").strip()
            except EOFError:
                return ""

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
        if not self._using_curses:
            # Ensure terminal is reset to non-raw state BEFORE printing
            import sys
            try:
                import termios
                import fcntl
                fd = sys.stdin.fileno()
                tty = fcntl.ioctl(fd, termios.TIOCGWINSZ, None) is not None
                if tty:
                    termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))
            except:
                pass
            try:
                curses.echo()
                curses.nocbreak()
                curses.curs_set(1)
            except:
                pass
            
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            try:
                choice = input(f"Choice [{default if default is not None else 0}]: ").strip()
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except (ValueError, EOFError):
                return None

        if not self._screen:
            # Ensure terminal is reset to non-raw state BEFORE printing
            import sys
            try:
                import termios
                import fcntl
                fd = sys.stdin.fileno()
                tty = fcntl.ioctl(fd, termios.TIOCGWINSZ, None) is not None
                if tty:
                    termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))
            except:
                pass
            try:
                curses.echo()
                curses.nocbreak()
                curses.curs_set(1)
            except:
                pass
            
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            try:
                choice = input(f"Choice [{default if default is not None else 0}]: ").strip()
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
