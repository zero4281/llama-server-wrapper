#!/usr/bin/env python3
"""
uimanager.py — ncurses CLI user interface module.

This module provides ncurses-based UI rendering for menus, prompts,
progress bars, and other interactive elements with black background
and green text styling.
"""

import curses
import sys
import time
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Logging configuration
UI_MANAGER_DEBUG = False
UI_MANAGER_LOG_LEVEL = logging.INFO


def enable_debug_mode():
    """Enable debug logging for UIManager."""
    global UI_MANAGER_DEBUG, UI_MANAGER_LOG_LEVEL
    UI_MANAGER_DEBUG = True
    UI_MANAGER_LOG_LEVEL = logging.DEBUG
    logger.setLevel(logging.DEBUG)
    # Re-add handler with debug level
    if logger.handlers:
        handler = logger.handlers[0]
        handler.setLevel(logging.DEBUG)
    else:
        _configure_logging()

def _configure_logging():
    """Configure logging for UIManager."""
    ui_logger = logging.getLogger("ui_manager")
    if not ui_logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        ui_logger.addHandler(handler)
        ui_logger.setLevel(UI_MANAGER_LOG_LEVEL)


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
    MIN_WIDTH_PERCENT = 0.6
    MIN_HEIGHT_PERCENT = 0.5
    
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
        self._initialized = False
        
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
            self._initialized = True
            
        except (curses.error, OSError, IOError) as e:
            try:
                logger.error(f"Curses initialization failed: {e}")
                self._restore_terminal_state()
                print(f"Curses initialization failed: {e}", file=sys.stderr)
                self._using_curses = False
                self._screen = None
                self._color_pair = None
                self._initialized = False
            except Exception as restore_error:
                try:
                    logger.error(f"Error restoring terminal state: {restore_error}")
                except:
                    pass

    def _restore_terminal_state(self):
        """Restore terminal to original state."""
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
        except Exception as e:
            logger.error(f"Error restoring terminal state: {e}")
        finally:
            self._screen = None
            self._color_pair = None
            self._using_curses = False
            self._initialized = False
            # Try to reset stty if available
            try:
                import subprocess
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass
    
    def _cleanup_terminal(self):
        """Clean up curses and restore terminal."""
        if self._using_curses and self._screen:
            self._restore_terminal_state()
        else:
            # Even if not initialized, ensure clean state
            self._screen = None
            self._color_pair = None
            self._using_curses = False
            self._initialized = False

    def __del__(self):
        """Cleanup curses resources."""
        self._cleanup_terminal()

    def refresh(self):
        """Refresh screen."""
        if self._using_curses and self._screen:
            try:
                self._screen.refresh()
            except curses.error as e:
                logger.error(f"Screen refresh error: {e}")
                try:
                    self._cleanup_terminal()
                except:
                    pass
            except Exception as e:
                logger.error(f"Unexpected error during screen refresh: {e}")
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

    def _get_white_attr(self):
        """Get the white attribute for use when curses is initialized."""
        if self._using_curses and self._color_pair is not None:
            try:
                return curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE
            except (curses.error, OSError, AttributeError):
                # Fallback to just bold attribute if color_pair fails
                return curses.A_BOLD
        return None
    
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
        except curses.error as e:
            logger.error(f"Header rendering error: {e}")
            print(f"\n{'='*self.WIDTH}\n{text.center(self.WIDTH)}\n{'='*self.WIDTH}")
        except Exception as e:
            logger.error(f"Unexpected error during header rendering: {e}")
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
        except curses.error as e:
            logger.error(f"Message rendering error at ({y},{x}): {e}")
            print(text)
        except Exception as e:
            logger.error(f"Unexpected error during message rendering: {e}")
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
        except curses.error as e:
            logger.error(f"Line rendering error at ({y},{x}): {e}")
            print("-" * (length or 60))
        except Exception as e:
            logger.error(f"Unexpected error during line rendering: {e}")
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
        except curses.error as e:
            logger.error(f"Window creation error at ({y},{x}) {height}x{width}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during window creation: {e}")
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
        start_time = time.time()
        logger.info(f"render_menu: options_count={len(options)}, default={default}, highlighted={highlighted}")
        
        # Ensure terminal is in proper state before rendering
        if self._using_curses:
            try:
                curses.setupterm()
            except (curses.error, AttributeError, OSError):
                logger.debug(f"curses.setupterm() failed, continuing with screen")
        
        # Console fallback
        if not self._using_curses or not self._screen:
            # Reset terminal
            try:
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
            
            # Prompt
            print(f"Choice [{highlighted if highlighted is not None else 0}]: ", end="", flush=True)
            try:
                if sys.stdin.isatty():
                    choice_str = sys.stdin.readline().strip()
                else:
                    choice_str = ""
            except:
                choice_str = ""
            
            try:
                idx = int(choice_str)
                return idx if 0 <= idx < len(options) else -1
            except ValueError:
                return -1

        # Create menu window
        self._screen.erase()
        self._screen.refresh()  # Force full screen refresh to clear old content
        screen_height, screen_width = self._screen.getmaxyx()
        menu_height = len(options) + 4
        # Calculate menu width: max label length + padding, but ensure minimum percentage and fit on screen
        max_label_len = max(len(opt.get('label', '')) for opt in options) if options else 20
        min_width = int(screen_width * self.MIN_WIDTH_PERCENT)
        menu_width = max(min_width, min(max_label_len + 15, screen_width - 8)) + 2
        
        y_offset = 2
        x_offset = 2
        highlighted_idx = highlighted if highlighted is not None else 0
        
        # Calculate centered position
        y_center = max(2, (screen_height - menu_height) // 2)
        x_center = max(2, (screen_width - menu_width) // 2)
        
        # Define redraw function
        def redraw(win, hi_idx):
            try:
                logger.debug(f"Redraw called: win={win}, hi_idx={hi_idx}, options_count={len(options)}")
                win.erase()
                white_attr = self._get_white_attr()
                if white_attr is not None:
                    win.attron(white_attr)
                    win.addstr(0, 1, f"Select {self._title.lower()}".center(menu_width - 2))
                    win.attroff(white_attr)
                    win.addstr(1, 0, "-" * (menu_width - 2))
                for i, opt in enumerate(options):
                    label = opt.get('label', '')
                    desc = opt.get('description', '')
                    marker = " (default)" if default is not None and i == default else ""
                    full_label = f"  {i}. {label}{marker}"
                    if i == hi_idx:
                        win.attron(self._color_pair | curses.A_BOLD | curses.A_REVERSE)
                        win.addstr(i + 2, 0, full_label)
                        if desc:
                            win.addstr(i + 3, 0, desc)
                        win.attroff(self._color_pair | curses.A_BOLD | curses.A_REVERSE)
                    else:
                        win.attron(self._color_pair)
                        win.addstr(i + 2, 0, full_label)
                        if desc:
                            win.addstr(i + 3, 0, desc)
                        win.attroff(self._color_pair)
                footer = "Use arrow keys to navigate, type number to select, Enter to confirm, q to cancel"
                truncated_footer = footer[:menu_width - 2] if len(footer) > menu_width - 2 else footer
                win.addstr(menu_height - 1, 0, truncated_footer, curses.A_REVERSE)
                win.refresh()
                logger.debug(f"Redraw completed successfully")
            except curses.error as e:
                logger.error(f"curses.error during redraw: {e}")
                try:
                    self._screen.refresh()
                except:
                    pass
            except Exception as e:
                logger.error(f"Unexpected error during redraw: {e}")
                raise

        try:
            logger.debug(f"Creating menu window: size={menu_height}x{menu_width}, pos=({y_center},{x_center})")
            menu_win = curses.newwin(menu_height, menu_width, y_center, x_center)
            logger.debug(f"Window created: {menu_win}")
            
            menu_win.box()
            menu_win.keypad(True)
            
            logger.debug(f"Redrawing menu with highlighted index: {highlighted_idx}")
            redraw(menu_win, highlighted_idx)
            logger.debug(f"Menu redraw completed")
            
            # Log menu state for debugging
            logger.debug(f"Menu initialized: options_count={len(options)}, default={default}, highlighted={highlighted_idx}")
        except curses.error as e:
            logger.error(f"Menu window creation error: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            return -1
        except Exception as e:
            logger.error(f"Unexpected error during menu rendering: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            return -1
        # Input loop
        try:
            logger.debug("Starting render_menu input loop")
            while True:
                try:
                    key = menu_win.getch()
                except (curses.error, KeyboardInterrupt, OSError, EOFError) as e:
                        logger.error(f"Menu getch() error: {e}")
                        try:
                            self._cleanup_terminal()
                        except:
                            pass
                        return -1
                
                # Log the raw key value with additional details for debugging
                if key is not None:
                    if isinstance(key, int):
                        # Determine key type for better logging
                        key_type = "UNKNOWN"
                        key_name = ""
                        
                        # Check for known key codes first
                        if key in (curses.KEY_UP, 259):
                            key_type = "KEY_UP"
                            key_name = "UP"
                        elif key in (curses.KEY_DOWN, 258):
                            key_type = "KEY_DOWN"
                            key_name = "DOWN"
                        elif key in (curses.KEY_LEFT, 260):
                            key_type = "KEY_LEFT"
                            key_name = "LEFT"
                        elif key in (curses.KEY_RIGHT, 261):
                            key_type = "KEY_RIGHT"
                            key_name = "RIGHT"
                        elif key in (curses.KEY_ENTER, 343, 10, 13):
                            key_type = "KEY_ENTER"
                            key_name = "ENTER"
                        elif key in (27, curses.KEY_RESIZE, 410):
                            key_type = "CANCEL_KEY"
                            key_name = "ESC/RESIZE"
                        elif key in (curses.KEY_PPAGE, 339):
                            key_type = "KEY_PPAGE"
                            key_name = "PAGE_UP"
                        elif key in (curses.KEY_NPAGE, 338):
                            key_type = "KEY_NPAGE"
                            key_name = "PAGE_DOWN"
                        elif key in (curses.KEY_BACKSPACE, 263, 127, 8):
                            key_type = "BACKSPACE"
                            key_name = "BACKSPACE"
                        
                        # Check for numeric keys (0-9) - ASCII codes 48-57
                        elif key >= ord('0') and key <= ord('9'):
                            key_type = "NUMERIC"
                            key_name = f"DIGIT({chr(key)})"
                            selection = int(chr(key))
                            if 0 <= selection < len(options):
                                old_highlighted = highlighted_idx
                                highlighted_idx = selection
                                logger.debug(f"State change: highlighted_idx {old_highlighted} -> {highlighted_idx}")
                                try:
                                    redraw(menu_win, highlighted_idx)
                                except Exception as redraw_error:
                                    logger.error(f"Redraw failed after numeric key {key_name}: {redraw_error}")
                                continue
                        
                        # Check for character keys (printable ASCII)
                        elif 32 <= key < 127:
                            key_type = "CHAR"
                            key_name = f"'{chr(key)}'"
                        
                        # For unknown keys, use hex representation
                        else:
                            char_repr = chr(key) if 32 <= key < 127 else f'0x{key:02X}'
                            key_type = f"UNKNOWN({key})"
                            key_name = char_repr
                        
                        logger.debug(f"Input loop iteration: key={key}, type={type(key).__name__}, key_type={key_type}, key_name={key_name}, hex=0x{key:02X}")
                    else:
                        logger.debug(f"Input loop iteration: key={key}, type={type(key).__name__}")
                else:
                    logger.debug(f"Input loop iteration: key=None (EOF/timeout)")
                

                
                # Handle navigation and control keys
                if key == curses.KEY_UP:
                    # Move up one option
                    old_hi = highlighted_idx
                    if highlighted_idx > 0:
                        highlighted_idx -= 1
                    else:
                        highlighted_idx = len(options) - 1  # Wrap to last
                    logger.debug(f"Navigation: UP key, {old_hi} -> {highlighted_idx}")
                    try:
                        redraw(menu_win, highlighted_idx)
                    except Exception as redraw_error:
                        logger.error(f"Redraw failed after UP key: {redraw_error}")
                    continue
                
                if key == curses.KEY_PPAGE:
                    # Page up - move up half the visible menu
                    old_hi = highlighted_idx
                    # Calculate page size based on screen height and menu size
                    page_size = max(1, min(len(options) // 2, (menu_height - 2) // 2))
                    new_idx = highlighted_idx - page_size
                    if new_idx < 0:
                        # Wrap to end
                        highlighted_idx = len(options) - (abs(new_idx) % len(options))
                    else:
                        highlighted_idx = new_idx
                    logger.debug(f"Navigation: PAGE UP key, {old_hi} -> {highlighted_idx}")
                    try:
                        redraw(menu_win, highlighted_idx)
                    except Exception as redraw_error:
                        logger.error(f"Redraw failed after PAGE UP key: {redraw_error}")
                    continue
                
                if key == curses.KEY_DOWN:
                    # Move down one option
                    old_hi = highlighted_idx
                    if highlighted_idx < len(options) - 1:
                        highlighted_idx += 1
                    else:
                        highlighted_idx = 0  # Wrap to first
                    logger.debug(f"Navigation: DOWN key, {old_hi} -> {highlighted_idx}")
                    try:
                        redraw(menu_win, highlighted_idx)
                    except Exception as redraw_error:
                        logger.error(f"Redraw failed after DOWN key: {redraw_error}")
                    continue
                
                if key == curses.KEY_NPAGE:
                    # Page down - move down half the visible menu
                    old_hi = highlighted_idx
                    # Calculate page size based on screen height and menu size
                    page_size = max(1, min(len(options) // 2, (menu_height - 2) // 2))
                    new_idx = highlighted_idx + page_size
                    if new_idx < len(options):
                        highlighted_idx = new_idx
                    else:
                        # Wrap to beginning
                        highlighted_idx = new_idx % len(options)
                    logger.debug(f"Navigation: PAGE DOWN key, {old_hi} -> {highlighted_idx}")
                    try:
                        redraw(menu_win, highlighted_idx)
                    except Exception as redraw_error:
                        logger.error(f"Redraw failed after PAGE DOWN key: {redraw_error}")
                    continue
                
                if key in (curses.KEY_ENTER, 10, 13):
                    # Confirm selection (Enter key - various codes)
                    logger.debug(f"Confirmation requested: highlighted={highlighted_idx}, options={len(options)}")
                    selected_option = options[highlighted_idx] if 0 <= highlighted_idx < len(options) else None
                    logger.debug(f"Selected option: {selected_option}")
                    try:
                        self._screen.refresh()
                    except (curses.error, OSError, EOFError):
                        pass
                    return highlighted_idx
                
                if key == 27 or key == ord('q') or key == curses.KEY_RESIZE:
                    # Cancel
                    logger.debug(f"Cancellation requested: key={key}, current_highlighted={highlighted_idx}")
                    try:
                        self._screen.erase()
                        self._screen.refresh()
                    except (curses.error, OSError, EOFError):
                        pass
                    return -1
                
                if key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                    # Backspace - cancel
                    logger.debug(f"Backspace received: cancelling, current_highlighted={highlighted_idx}")
                    try:
                        self._screen.refresh()
                    except (curses.error, OSError, EOFError):
                        pass
                    return -1

                # Timeout - redraw to refresh display
                try:
                    redraw(menu_win, highlighted_idx)
                except Exception as redraw_error:
                    logger.error(f"Redraw failed on timeout: {redraw_error}")

                # Small delay to prevent rapid redraws
                curses.napms(10) if hasattr(curses, 'napms') else None
                
        except (curses.error, OSError, EOFError, TypeError) as e:
            logger.error(f"Menu input loop error: {e}")
            # Clear screen and fall back to console
            logger.warning(f"Falling back to console mode due to error: {e}")
            try:
                curses.curs_set(1)
                curses.endwin()
            except:
                pass
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            try:
                choice = input(f"Choice [{highlighted if highlighted is not None else 0}]: ").strip()
                idx = int(choice)
                return idx if 0 <= idx < len(options) else -1
            except Exception as input_error:
                logger.error(f"Console fallback error: {input_error}")
                return -1
            try:
                self._cleanup_terminal()
            except:
                pass
            return -1
        except Exception as e:
            logger.error(f"Unexpected error during menu rendering: {e}")
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
        start_time = time.time()
        result = None
        logger.info(f"render_confirmation entry: message_len={len(message)}, default={default}")
        logger.debug(f"render_confirmation called with message={message[:50]}..., default={default}")
        
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
        
        # Clear screen and move cursor to top-left
        self._screen.erase()
        self._screen.move(0, 0)
        
        # Create window at bottom of screen
        msg_width = min(width - 4, max(width * self.MIN_WIDTH_PERCENT, 60))
        y_start = max(2, height - 6)
        x_start = max(2, (width - msg_width) // 2)
        
        # Create window
        try:
            prompt_win = curses.newwin(4, msg_width, y_start, x_start)
            prompt_win.box()
            prompt_win.keypad(True)
            
            # Title
            title = "Confirm"
            white_attr = self._get_white_attr()
            if white_attr is not None:
                prompt_win.attron(white_attr)
                prompt_win.addstr(0, 1, title.center(msg_width - 2))
                prompt_win.attroff(white_attr)
            prompt_win.addstr(1, 0, "-" * (msg_width - 2))
            
            # Message
            white_attr = self._get_white_attr()
            if white_attr is not None:
                prompt_win.attron(white_attr)
                truncated_msg = message[:msg_width - 4] if len(message) > msg_width - 4 else message
                prompt_win.addstr(2, 0, truncated_msg)
                prompt_win.attroff(white_attr)
            
            # Prompt
            prompt_str = "Proceed? [Y/n]: "
            prompt_win.attron(curses.A_REVERSE | curses.A_BOLD)
            prompt_win.addstr(3, 1, prompt_str)
            prompt_win.attroff(curses.A_REVERSE | curses.A_BOLD)
            
            prompt_win.refresh()
            self._screen.refresh()

            # Input handling
            logger.debug("Starting confirmation input loop")
            
            # Define redraw function
            def confirm_redraw():
                try:
                    prompt_win.erase()
                    white_attr = self._get_white_attr()
                    if white_attr is not None:
                        prompt_win.attron(white_attr)
                        prompt_win.addstr(0, 1, "Confirm".center(msg_width - 2))
                        prompt_win.attroff(white_attr)
                    prompt_win.addstr(1, 0, "-" * (msg_width - 2))
                    white_attr = self._get_white_attr()
                    if white_attr is not None:
                        prompt_win.attron(white_attr)
                        truncated_msg = message[:msg_width - 4] if len(message) > msg_width - 4 else message
                        prompt_win.addstr(2, 0, truncated_msg)
                        prompt_win.attroff(white_attr)
                    prompt_win.attron(curses.A_REVERSE | curses.A_BOLD)
                    prompt_win.addstr(3, 1, "Proceed? [Y/n]: ")
                    prompt_win.attroff(curses.A_REVERSE | curses.A_BOLD)
                    prompt_win.refresh()
                except Exception:
                    pass
            
            confirm_redraw()
            
            # Input loop with timeout
            while True:
                try:
                    key = prompt_win.getch()
                except (curses.error, OSError, EOFError) as e:
                    logger.error(f"Confirmation getch() error: {e}")
                    try:
                        self._cleanup_terminal()
                    except:
                        pass
                    # Fallback to console
                    print(f"\n{message}")
                    print("Proceed? [Y/n]: ", end="", flush=True)
                    response = sys.stdin.readline().strip().lower()
                
                # Handle key input
                if key is None:
                    # EOF/timeout - assume default (yes)
                    logger.debug("Confirmation: timeout, assuming default yes")
                    return True
                
                if key == 27 or key == curses.KEY_RESIZE or key == curses.KEY_BACKSPACE:
                    # Cancel
                    logger.debug("Confirmation: ESC/RESIZE/BACKSPACE pressed, cancelling")
                    self._screen.erase()
                    return False
                
                elif key in (10, 13, curses.KEY_ENTER):  # Enter
                    # Confirm (default yes)
                    logger.debug("Confirmation: ENTER pressed, confirming")
                    self._screen.erase()
                    self._screen.refresh()
                    return True
                
                elif key in (ord('y'), ord('Y')):
                    # Confirm
                    logger.debug("Confirmation: 'y' pressed, confirming")
                    self._screen.erase()
                    self._screen.refresh()
                    return True
                
                elif key in (ord('n'), ord('N')):
                    # Cancel
                    logger.debug("Confirmation: 'n' pressed, cancelling")
                    self._screen.erase()
                    self._screen.refresh()
                    return False
                
                # Timeout - assume default (yes)
                logger.debug("Confirmation: timeout, assuming default yes")
                self._screen.erase()
                self._screen.refresh()
                return True
            return False
        except curses.error as e:
            logger.error(f"Confirmation window error: {e}")
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
            # Fallback to console
            print(f"\n{message}")
            print("Proceed? [Y/n]: ", end="", flush=True)
            response = sys.stdin.readline().strip().lower()
            if response in ('', 'y', 'yes'):
                return True
            return False
        except Exception as e:
            logger.error(f"Unexpected error during confirmation: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            print(f"\n{message}")
            print("Proceed? [Y/n]: ", end="", flush=True)
            response = sys.stdin.readline().strip().lower()
            if response in ('', 'y', 'yes'):
                return True
            return False
        finally:
            elapsed = time.time() - start_time
            logger.debug(f"render_confirmation exit: returned={result}, elapsed={elapsed:.2f}s")

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
        start_time = time.time()
        logger.info(f"render_progress_bar entry: file={Path(filename).name}, current={current:,}, total={total:,}")
        if percent is not None:
            logger.debug(f"render_progress_bar called: file={Path(filename).name}, current={current:,}, total={total:,}, percent={percent:.1f}%")
        else:
            logger.debug(f"render_progress_bar called: file={Path(filename).name}, current={current:,}, total={total:,}")
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
                spinner_idx = int(time.time() / 100) % 4
                
                bar_win.attron(self._color_pair)
                bar_win.addstr(2, 0, f"Downloading {Path(filename).name}... ({spinner[spinner_idx]})")
                bar_win.attroff(self._color_pair)
            
            bar_win.addstr(4, 0, "Press any key to continue...", curses.A_REVERSE)
            bar_win.refresh()
            
            # Wait for key
            logger.debug("Progress bar: waiting for key press")
            self.refresh()
            try:
                key = self._screen.getch()
            except (curses.error, OSError, EOFError) as e:
                logger.error(f"Progress bar getch() error: {e}")
                try:
                    self._cleanup_terminal()
                except:
                    pass
                # Fallback to console
                print(f"\nDownloading {Path(filename).name}... {current}/{total} ({percent or (current/total*100 if total else 0.0):.1f}%)")
                input("Press Enter to continue...")
                key = -1  # Signal to break loop
            logger.debug(f"Progress bar: key received={key}")
            bar_win.erase()
        except curses.error as e:
            logger.error(f"Progress bar window error: {e}")
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
            # Fallback to console
            print(f"\nDownloading {Path(filename).name}... {current}/{total} ({percent or (current/total*100 if total else 0.0):.1f}%)")
            input("Press Enter to continue...")
        except Exception as e:
            logger.error(f"Unexpected error during progress bar: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            print(f"\nDownloading {Path(filename).name}... {current}/{total} ({percent or (current/total*100 if total else 0.0):.1f}%)")
            input("Press Enter to continue...")

    def render_success(self, message: str) -> None:
        """Render success message."""
        logger.debug(f"render_success called: {message[:60]}...")
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
            try:
                self._screen.getch()
            except (curses.error, OSError, EOFError) as e:
                logger.error(f"Success getch() error: {e}")
                try:
                    self._cleanup_terminal()
                except:
                    pass
                # Fallback to console
                print(f"\n{'='*60}\n{message.center(60)}\n{'='*60}")
                input("Press Enter to continue...")
            msg_win.erase()
        except curses.error as e:
            logger.error(f"Success window error: {e}")
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
            # Fallback to console
            print(f"\n{'='*60}\n{message.center(60)}\n{'='*60}")
            input("Press Enter to continue...")
        except Exception as e:
            logger.error(f"Unexpected error during success display: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            print(f"\n{'='*60}\n{message.center(60)}\n{'='*60}")
            input("Press Enter to continue...")

    def render_error(self, message: str) -> None:
        """Render error message."""
        logger.debug(f"render_error called: {message[:60]}...")
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
            try:
                self._screen.getch()
            except (curses.error, OSError, EOFError) as e:
                logger.error(f"Error getch() error: {e}")
                try:
                    self._cleanup_terminal()
                except:
                    pass
                # Fallback to console
                print(f"\n{'='*60}\nError: {message.center(60)}\n{'='*60}")
                input("Press Enter to continue...")
            msg_win.erase()
        except curses.error as e:
            logger.error(f"Error window error: {e}")
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
            # Fallback to console
            print(f"\n{'='*60}\nError: {message.center(60)}\n{'='*60}")
            input("Press Enter to continue...")
        except Exception as e:
            logger.error(f"Unexpected error during error display: {e}")
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
        logger.debug(f"print_simple_menu called with options={len(options)}, default={default}, highlighted={highlighted}")
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
                try:
                    key = self._screen.getch()
                except (curses.error, OSError, EOFError) as e:
                    logger.error(f"print_simple_menu getch() error: {e}")
                    try:
                        self._cleanup_terminal()
                    except:
                        pass
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
                
                if key is None or key == 27 or key == ord('q'):
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
                elif isinstance(key, int) and key >= ord('0') and key <= ord('9'):
                    try:
                        choice = int(chr(key)) - 1
                        if 0 <= choice < len(options):
                            highlighted = choice
                    except (ValueError, TypeError):
                        pass
                elif key is not None and not isinstance(key, int):
                    # Handle non-integer keys (e.g., mocked values)
                    try:
                        choice = int(key) - 1
                        if 0 <= choice < len(options):
                            highlighted = choice
                    except (ValueError, TypeError, AttributeError):
                        pass
                elif key == 343 or key == curses.KEY_ENTER:
                    return highlighted

                if highlighted is not None:
                    self._screen.refresh()

        except (curses.error, OSError, EOFError, TypeError) as e:
            logger.error(f"Simple menu input error: {e}")
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
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
        except Exception as e:
            logger.error(f"Unexpected error during simple menu: {e}")
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
        logger.debug(f"get_input called with prompt={prompt[:60]}...")
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
        except (curses.error, OSError, EOFError, TypeError) as e:
            logger.error(f"get_input error: {e}")
            # If curses fails during input, clean up and return
            try:
                self._cleanup_terminal()
            except:
                pass
            # Fallback to console
            print(f"{prompt}")
            response = sys.stdin.readline().strip()
            return response
        except Exception as e:
            # Log but don't fail
            logger.warning(f"Unexpected error during get_input: {e}")
            # Fallback to console
            print(f"{prompt}")
            response = sys.stdin.readline().strip()
            return response

    def get_numbered_input(self, options: List[str], 
                          default: Optional[int] = None) -> Optional[int]:
        """Get numbered input from user."""
        logger.debug(f"get_numbered_input called with options={len(options)}, default={default}")
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
        try:
            input_str = self._screen.getstr(x + len(f"\nChoice [{default if default is not None else 0}]: "), y + len(options) + 1, width).decode()
            idx = int(input_str) if input_str.isdigit() else None
            return idx if idx is not None and 0 <= idx < len(options) else None
        except (curses.error, OSError, EOFError, TypeError) as e:
            logger.error(f"get_numbered_input error: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            # Fallback to console
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            print(f"Choice [{default if default is not None else 0}]: ", end="", flush=True)
            choice = sys.stdin.readline().strip()
            try:
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except ValueError:
                return None
        except Exception as e:
            logger.error(f"Unexpected error during get_numbered_input: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            print(f"Choice [{default if default is not None else 0}]: ", end="", flush=True)
            choice = sys.stdin.readline().strip()
            try:
                idx = int(choice)
                return idx if 0 <= idx < len(options) else None
            except ValueError:
                return None