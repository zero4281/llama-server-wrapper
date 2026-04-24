#!/usr/bin/env python3
"""
uimanager.py — ncurses CLI user interface module.

This module provides ncurses-based UI rendering for menus, prompts,
progress bars, and other interactive elements with black background
and green text styling.

Key Code Reference
==================

All UIManager methods use standard curses key codes. Below is a quick reference:

### Navigation & Control Keys
| Key Code | Constant | Description | Used For |
|----------|----------|-------------|----------|
| `curses.KEY_UP` | KEY_UP | Move cursor up | Menu navigation, highlight selection |
| `curses.KEY_DOWN` | KEY_DOWN | Move cursor down | Menu navigation, highlight selection |
| `curses.KEY_LEFT` | KEY_LEFT | Move cursor left | Not used in menus |
| `curses.KEY_RIGHT` | KEY_RIGHT | Move cursor right | Not used in menus |
| `curses.KEY_PPAGE` | KEY_PPAGE | Page up | Jump to top of menu |
| `curses.KEY_NPAGE` | KEY_NPAGE | Page down | Jump to bottom of menu |
| `curses.KEY_ENTER` | KEY_ENTER | Enter key | Confirm selection, confirm actions |
| `curses.KEY_RESIZE` | KEY_RESIZE | Terminal resize | Cancel operation |
| `curses.KEY_BACKSPACE` | KEY_BACKSPACE | Backspace | Cancel operation |

### Cancel Keys (Escape, DEL, Backspace)
| Key Code | ASCII | Description |
|----------|-------|-------------|
| `curses.KEY_RESIZE` | 27 (Escape) | Cancel operation |
| `curses.KEY_BACKSPACE` | 127 (DEL) | Cancel operation |
| ASCII 27 | - | Escape key |
| ASCII 127 | - | DEL key |
| ASCII 8 | - | Backspace (alternative) |
| `ord('q')` | 113 | Cancel operation |

### Input Characters
| Character | ASCII | Description | Used For |
|-----------|-------|-------------|----------|
| `'0'` - `'9'` | 48-57 | Select option by number | Menu selection |
| `'y'` / `'Y'` | 121 | Confirm action | Confirmation dialogs |
| `'n'` / `'N'` | 110 | Cancel action | Confirmation dialogs |

### Other Control Keys
| Key Code | ASCII | Description | Used For |
|----------|-------|-------------|----------|
| ASCII 10 | - | LF/Enter | Confirm selection |
| ASCII 13 | - | CR/Enter | Confirm selection |

Main Methods:
- `render_menu(options, default, highlighted)`: Returns selected index or -1 (cancel)
- `render_confirmation(message, default)`: Returns True (confirm) or False (cancel)
- `render_progress_bar(filename, current, total)`: Waits for any key
- `render_success(message)`: Waits for any key
- `render_error(message)`: Waits for any key
- `print_simple_menu(options, default, highlighted)`: Returns selected index or None (cancel)
- `get_input(prompt)`: Returns input string
- `get_numbered_input(options, default)`: Returns selected index or None (cancel)

Usage Examples:
- Menu: Use arrow keys to navigate, type number to select, Enter to confirm, q/Esc to cancel
- Confirmation: Enter/Y to confirm, n/Esc to cancel, timeout defaults to yes
- Progress bars: Press any key to continue
"""

import curses
import sys
import time
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Logging configuration
UI_MANAGER_DEBUG = os.environ.get("UI_MANAGER_DEBUG", "0").lower() in ("1", "true")
UI_MANAGER_LOG_LEVEL = logging.DEBUG if UI_MANAGER_DEBUG else logging.INFO


def _configure_logging():
    """Configure logging for UIManager."""
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(UI_MANAGER_LOG_LEVEL)


# Configure logging at module load time
_configure_logging()


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
        except AttributeError as e:
            # Handle partial initialization failures where curses attributes are missing
            try:
                logger.error(f"AttributeError during curses initialization: {e}")
                self._restore_terminal_state()
                print(f"AttributeError during initialization: {e}", file=sys.stderr)
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
            # Validate window if available before attempting operations
            if self._screen:
                if not self._validate_window(self._screen):
                    logger.warning("Screen window invalid, falling back to console")
                    self._using_curses = False
                    self._screen = None
                    self._color_pair = None
                    self._initialized = False
                    return
            
            # Reset terminal mode
            try:
                curses.echo()
                curses.nocbreak()
                curses.keypad(False)
            except (AttributeError, OSError) as e:
                logger.warning(f"Failed to reset terminal modes: {e}")
            
            # Reset terminal mode
            try:
                curses.echo()
                curses.nocbreak()
                curses.keypad(False)
            except (AttributeError, OSError) as e:
                logger.warning(f"Failed to reset terminal modes: {e}")
            
            try:
                curses.curs_set(1)  # Show cursor
            except (AttributeError, OSError) as e:
                logger.warning(f"Failed to set cursor: {e}")
            
            # Reset colors
            try:
                if hasattr(curses, 'reset_pair_matrix'):
                    curses.reset_pair_matrix()
            except (AttributeError, OSError) as e:
                logger.warning(f"Failed to reset color pairs: {e}")
            
            try:
                curses.endwin()
            except (AttributeError, OSError) as e:
                logger.warning(f"Failed to endwin: {e}")
        except (curses.error, OSError, EOFError, TypeError) as e:
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
            # Validate screen window before attempting cleanup
            if not self._validate_window(self._screen):
                logger.warning("Screen window invalid, forcing cleanup")
                self._screen = None
                self._color_pair = None
                self._using_curses = False
                self._initialized = False
            else:
                try:
                    self._restore_terminal_state()
                except (AttributeError, OSError) as e:
                    logger.warning(f"Failed to cleanup terminal: {e}")
                    # Force cleanup even if restoration fails
                    self._screen = None
                    self._color_pair = None
                    self._using_curses = False
                    self._initialized = False
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
            except (curses.error, OSError, EOFError, TypeError) as e:
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
    
    def _validate_window(self, win) -> bool:
        """
        Validate if a window is usable before operations.
        
        Args:
            win: Window to validate
            
        Returns:
            True if window is valid, False otherwise
        """
        if win is None:
            return False
        
        # Check if window has required methods
        required_methods = ['box', 'refresh', 'getch', 'addstr']
        for method in required_methods:
            if not hasattr(win, method) or not callable(getattr(win, method)):
                logger.warning(f"Window missing required method: {method}")
                return False
        
        # Try to refresh to verify window is valid
        try:
            win.refresh()
            return True
        except (curses.error, OSError, AttributeError):
            logger.warning("Window refresh failed, likely invalid")
            return False

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
        except (curses.error, OSError, EOFError, TypeError) as e:
            logger.error(f"Unexpected error during message rendering: {e}")
            print(text)

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
        except (curses.error, OSError, EOFError, TypeError) as e:
            logger.error(f"Unexpected error during window creation: {e}")
            return None

    def _is_terminal_in_cbreak(self) -> bool:
        """
        Check if terminal is already in cbreak mode without causing ERR.
        
        Returns:
            True if terminal is in cbreak mode, False otherwise
        """
        # Use non-blocking read to check terminal state
        try:
            self._screen.nodelay(True)
            key = self._screen.getch()
            self._screen.nodelay(False)
            # KEY_RESIZE (27) indicates cbreak mode
            return key == curses.KEY_RESIZE or key == 27
        except (curses.error, OSError, EOFError):
            return False
    
    def _safe_keypad(self, win, enable: bool) -> bool:
        """
        Safely enable/disable keypad mode with error handling.
        
        Args:
            win: Window to modify
            enable: True to enable keypad mode, False to disable
            
        Returns:
            True if operation succeeded, False otherwise
        """
        try:
            win.keypad(enable)
            return True
        except (curses.error, AttributeError, OSError, IOError) as e:
            logger.warning(f"Keypad operation failed: {e}")
            # Try to recover by refreshing the window
            try:
                win.refresh()
                return True
            except:
                return False
    
    def _ensure_terminal_ready(self) -> bool:
        """
        Ensure terminal is in proper state for curses operations.
        
        Returns:
            True if terminal is ready, False if we should fallback to console
        """
        # Check if terminal is in cbreak mode
        in_cbreak = self._is_terminal_in_cbreak()
        
        if not in_cbreak:
            try:
                curses.cbreak()
            except (curses.error, OSError, IOError, AttributeError):
                logger.warning("Failed to set cbreak mode, terminal may not be ready")
                return False
        
        # Enable keypad mode on the main screen for arrow keys, Page Up/Down, Escape
        if self._screen:
            try:
                self._screen.keypad(True)
            except (curses.error, OSError, IOError, AttributeError):
                logger.warning("Failed to enable keypad mode on main screen")
                return False
        
        return True
    
    def render_menu(self, options: List[Dict[str, Any]], 
                   default: Optional[int] = None,
                   highlighted: Optional[int] = None,
                   timeout: Optional[int] = None) -> int:
        """
        Render a numbered menu with options.
        
        Args:
            options: List of dictionaries with 'label' and optional 'description'
            default: Index of default option (appends '(default)')
            highlighted: Index of currently highlighted option
            timeout: Optional timeout in seconds (None = no timeout)
            
        Returns:
            Selected option index, or -1 if cancelled/timeout
        
        Supported Key Codes:
            - Navigation: KEY_UP (259), KEY_DOWN (258), KEY_PPAGE (339), KEY_NPAGE (338)
            - Enter: KEY_ENTER (343, 10, 13)
            - Cancel: 27 (Escape), ord('q') (113), KEY_RESIZE (410), KEY_BACKSPACE (263, 127, 8)
            - Selection: '0'-'9' (ASCII 48-57)
        """
        start_time = time.time()
        logger.info(f"render_menu: options_count={len(options)}, default={default}, highlighted={highlighted}, timeout={timeout}")
        
        # Check for non-interactive mode or curses failure at the start
        if (not sys.stdin.isatty() and not self._using_curses) or not self._screen:
            logger.warning(f"render_menu: stdin is not a TTY and curses not initialized, returning -1 with timeout={timeout}")
            return -1 if timeout is None else 0
        
        # Ensure terminal is ready before rendering
        if self._using_curses and self._screen:
            if not self._ensure_terminal_ready():
                logger.warning("Terminal not ready, falling back to console")
                # Force console fallback
                self._using_curses = False
                self._screen = None
        
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
                    # Use non-blocking read for fallback
                    import os
                    choice_str = ""
                    try:
                        data = os.read(0, 1)
                        if data:
                            choice_str = data.decode('utf-8').strip()
                    except (OSError, EOFError):
                        try:
                            data = sys.stdin.read(1)
                            if data:
                                choice_str = data.strip()
                        except (OSError, EOFError):
                            pass
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
                
                # Validate window before operations
                if not self._validate_window(win):
                    logger.warning("Window validation failed in redraw")
                    try:
                        self._cleanup_terminal()
                    except:
                        pass
                    raise Exception("Window invalid")
                
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
                    # Try to recover
                    if hasattr(win, 'refresh'):
                        try:
                            win.refresh()
                        except:
                            pass
                    self._screen.refresh()
                except:
                    pass
                # Continue with redraw - don't raise
                return
            except (curses.error, OSError, EOFError, TypeError) as e:
                logger.error(f"Unexpected error during redraw: {e}")
                # Don't raise - continue with current state
                return

        try:
            logger.debug(f"Creating menu window: size={menu_height}x{menu_width}, pos=({y_center},{x_center})")
            menu_win = curses.newwin(menu_height, menu_width, y_center, x_center)
            logger.debug(f"Window created: {menu_win}")
            
            menu_win.box()
            
            # Safely enable keypad mode with error handling
            if self._safe_keypad(menu_win, True):
                logger.debug("Keypad mode enabled successfully")
            else:
                logger.warning("Keypad mode failed to enable, attempting recovery")
                # Try to recover by refreshing
                try:
                    menu_win.refresh()
                    logger.debug("Window recovered after refresh")
                except:
                    logger.error("Window recovery failed, cleaning up")
                    try:
                        self._cleanup_terminal()
                    except:
                        pass
                    return -1
            
            logger.debug(f"Redrawing menu with highlighted index: {highlighted_idx}")
            redraw(menu_win, highlighted_idx)
            logger.debug(f"Menu redraw completed")
            
            # Log menu state for debugging
            logger.debug(f"Menu initialized: options_count={len(options)}, default={default}, highlighted={highlighted_idx}")
        except (curses.error, AttributeError, OSError) as e:
            logger.error(f"Menu window creation error: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            return -1
        except (curses.error, OSError, EOFError, TypeError) as e:
            logger.error(f"Unexpected error during menu rendering: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            return -1
        
        # Validate curses and terminal before input loop
        if not self._validate_window(menu_win):
            logger.warning("Menu window validation failed before input loop, returning -1")
            try:
                self._cleanup_terminal()
            except:
                pass
            return -1
        
        # Validate screen window before proceeding
        if not self._validate_window(self._screen):
            logger.warning("Screen window invalid, returning -1")
            try:
                self._cleanup_terminal()
            except:
                pass
            return -1
        
        # Input loop
        try:
            logger.debug("Starting render_menu input loop")
            while True:
                # Check if window is still valid before getting key
                if not hasattr(menu_win, 'getch') or not callable(menu_win.getch):
                    logger.warning(f"Window getch method not available, cleaning up and returning")
                    try:
                        self._cleanup_terminal()
                    except:
                        pass
                    return -1
                
                try:
                    key = menu_win.getch()
                    logger.debug(f"DEBUG: getch() returned key={key}")
                except (curses.error, AttributeError, OSError, EOFError, TypeError) as e:
                    logger.error(f"Menu getch() error: {e}")
                    # Try to recover before giving up
                    try:
                        # Attempt to refresh and recover
                        menu_win.refresh()
                        logger.debug("Attempted getch recovery via refresh")
                        # Retry once
                        key = menu_win.getch()
                        if key is not None:
                            logger.debug(f"Recovery successful, got key={key}")
                            # Continue with the key
                            if key is None:
                                logger.debug("Recovery got None, cleaning up")
                                try:
                                    self._cleanup_terminal()
                                except:
                                    pass
                                return -1
                    except:
                        logger.error("Recovery failed, cleaning up")
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
                # Use non-blocking read for fallback
                import os
                choice_str = ""
                try:
                    data = os.read(0, 1)
                    if data:
                        choice_str = data.decode('utf-8').strip()
                except (OSError, EOFError):
                    try:
                        data = sys.stdin.read(1)
                        if data:
                            choice_str = data.strip()
                    except (OSError, EOFError):
                        pass
                idx = int(choice_str)
                return idx if 0 <= idx < len(options) else -1
            except Exception as input_error:
                logger.error(f"Console fallback error: {input_error}")
                return -1
            try:
                self._cleanup_terminal()
            except:
                pass
            return -1
        except (curses.error, OSError, EOFError, TypeError) as e:
            logger.error(f"Unexpected error during menu rendering: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            return -1

    def _render_confirmation_fallback(self, message: str, default: bool = True) -> bool:
        """
        Consolidated fallback for confirmation prompts.
        
        Args:
            message: The message to display
            default: Default return value on timeout
            
        Returns:
            True if confirmed, False if cancelled
        """
        try:
            self._cleanup_terminal()
            import subprocess
            subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            subprocess.run(["stty", "-icanon", "echo", "cr"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            
            print(f"\n{message}")
            print("Proceed? [Y/n]: ", end="", flush=True)
            
            if sys.stdin.isatty():
                import select
                ready, _, _ = select.select([sys.stdin], [], [], 0.5)
                if ready:
                    response = sys.stdin.readline().strip().lower()
                else:
                    response = ""
            else:
                response = ""
            
            return response in ('', 'y', 'yes')
        except Exception:
            print(f"\n{message}")
            response = input(f"Proceed? [Y/n]: ").strip().lower()
            return response in ('', 'y', 'yes')
    
    def render_confirmation(self, message: str, default: bool = True, 
                           timeout: Optional[int] = None) -> bool:
        """
        Render a confirmation prompt.
        
        Args:
            message: The message to display
            default: If True, Enter = yes, 'n' = no
            timeout: Optional timeout in seconds (None = no timeout)
            
        Returns:
            True if confirmed, False if cancelled/timeout
        """
        try:
            start_time = time.time()
            
            # Validate screen and window upfront
            if not self._screen:
                return self._render_confirmation_fallback(message, default)
            
            height, width = self._screen.getmaxyx()
            
            # Clear screen and move cursor to top-left
            self._screen.erase()
            self._screen.move(0, 0)
            
            # Create window at bottom of screen
            width_int = int(width)
            msg_width = int(min(width_int - 4, max(width_int * self.MIN_WIDTH_PERCENT, 60)))
            y_start = max(2, height - 6)
            x_start = max(2, (width_int - msg_width) // 2)
            
            prompt_win = curses.newwin(4, msg_width, y_start, x_start)
            prompt_win.box()
            
            # Safely enable keypad mode
            if self._safe_keypad(prompt_win, True):
                logger.debug("Keypad mode enabled for confirmation window")
            else:
                logger.warning("Keypad mode failed for confirmation window")
            
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
            
            # Input loop with timeout
            while True:
                # Check for timeout
                elapsed = time.time() - start_time
                if timeout is not None and elapsed >= timeout:
                    logger.debug(f"Confirmation: timeout after {elapsed:.2f}s, assuming default yes")
                    return True
                
                try:
                    key = prompt_win.getch()
                except (curses.error, OSError, EOFError) as e:
                    logger.error(f"Confirmation getch() error: {e}")
                    raise

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
        except (curses.error, OSError, EOFError, TypeError) as e:
            logger.error(f"Unexpected error during confirmation: {e}")
            return self._render_confirmation_fallback(message, default)
        except Exception as e:
            logger.error(f"Unexpected error during confirmation: {e}")
            return self._render_confirmation_fallback(message, default)

    def render_progress_bar(self, filename: str, current: int, total: int, 
                          percent: Optional[float] = None) -> None:
        """
        Render a progress bar for downloads.
        
        Args:
            filename: Name of file being downloaded
            current: Current bytes downloaded
            total: Total bytes
            percent: Optional pre-calculated percentage
        
        Supported Key Codes:
            - Any key press (all valid curses key codes)
            - Console fallback: Enter (10, 13)
        """
        start_time = time.time()
        logger.info(f"render_progress_bar entry: file={Path(filename).name}, current={current:,}, total={total:,}")
        if percent is not None:
            logger.debug(f"render_progress_bar called: file={Path(filename).name}, current={current:,}, total={total:,}, percent={percent:.1f}%")
        else:
            logger.debug(f"render_progress_bar called: file={Path(filename).name}, current={current:,}, total={total:,}")
        if not self._using_curses:
            # Use console fallback with robust terminal reset
            import subprocess
            try:
                # Restore terminal state with comprehensive reset
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["stty", "-icanon", "echo", "cr"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass  # Ignore stty errors
            
            # Clear screen and move to beginning with explicit codes
            print("\033[2J\033[1;1H\n", end="")
            sys.stdout.flush()
            
            print(f"\nDownloading {Path(filename).name}... {current}/{total} ({percent or (current/total*100 if total else 0.0):.1f}%)")
            print("Press any key to continue...", end="", flush=True)
            
            try:
                # Use multiple input methods with short initial timeout
                if sys.stdin.isatty():
                    import select
                    
                    # First try with short timeout to detect immediate input
                    ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                    if ready:
                        sys.stdin.readline()  # Consume input
                    else:
                        # No immediate input, use longer timeout
                        ready, _, _ = select.select([sys.stdin], [], [], 1.0)
                        if ready:
                            sys.stdin.readline()  # Consume input
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
            
            # Safely enable keypad mode
            if self._safe_keypad(bar_win, True):
                logger.debug("Keypad mode enabled for progress bar")
            else:
                logger.warning("Keypad mode failed for progress bar")
            
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
            if self._validate_window(self._screen):
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
            else:
                logger.warning("Screen invalid in progress bar, using fallback")
                print(f"\nDownloading {Path(filename).name}... {current}/{total} ({percent or (current/total*100 if total else 0.0):.1f}%)")
                input("Press Enter to continue...")
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
        except (curses.error, OSError, EOFError, TypeError) as e:
            logger.error(f"Unexpected error during progress bar: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            print(f"\nDownloading {Path(filename).name}... {current}/{total} ({percent or (current/total*100 if total else 0.0):.1f}%)")
            input("Press Enter to continue...")

    def render_success(self, message: str) -> None:
        """Render success message.
        
        Supported Key Codes:
            - Any key press (all valid curses key codes)
            - Console fallback: Enter (10, 13)
        """
        logger.debug(f"render_success called: {message[:60]}...")
        if not self._using_curses:
            # Use console fallback with robust terminal reset
            import subprocess
            try:
                # Restore terminal state with comprehensive reset
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["stty", "-icanon", "echo", "cr"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass  # Ignore stty errors
            
            # Clear screen and move to beginning with explicit codes
            print("\033[2J\033[1;1H\n", end="")
            sys.stdout.flush()
            
            print(f"\n{'='*60}\n{message.center(60)}\n{'='*60}")
            print("Press any key to continue...", end="", flush=True)
            
            try:
                # Use multiple input methods with short initial timeout
                if sys.stdin.isatty():
                    import select
                    
                    # First try with short timeout to detect immediate input
                    ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                    if ready:
                        sys.stdin.readline()  # Consume input
                    else:
                        # No immediate input, use longer timeout
                        ready, _, _ = select.select([sys.stdin], [], [], 1.0)
                        if ready:
                            sys.stdin.readline()  # Consume input
                        # else: timeout - just continue
                else:
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
            
            # Safely enable keypad mode
            if self._safe_keypad(msg_win, True):
                logger.debug("Keypad mode enabled for success window")
            else:
                logger.warning("Keypad mode failed for success window")
            
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
            if self._validate_window(self._screen):
                self.refresh()
                try:
                    key = self._screen.getch()
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
            else:
                logger.warning("Screen invalid in success window, using fallback")
                print(f"\n{'='*60}\n{message.center(60)}\n{'='*60}")
                input("Press Enter to continue...")
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
        except (curses.error, OSError, EOFError, TypeError) as e:
            logger.error(f"Unexpected error during success display: {e}")
            try:
                self._cleanup_terminal()
            except:
                pass
            print(f"\n{'='*60}\n{message.center(60)}\n{'='*60}")
            input("Press Enter to continue...")

    def render_error(self, message: str) -> None:
        """Render error message.
        
        Supported Key Codes:
            - Any key press (all valid curses key codes)
            - Console fallback: Enter (10, 13)
        """
        logger.debug(f"render_error called: {message[:60]}...")
        if not self._using_curses:
            # Use console fallback with robust terminal reset
            import subprocess
            try:
                # Restore terminal state with comprehensive reset
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["stty", "-icanon", "echo", "cr"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass  # Ignore stty errors
            
            # Clear screen and move to beginning with explicit codes
            print("\033[2J\033[1;1H\n", end="")
            sys.stdout.flush()
            
            print(f"\n{'='*60}\nError: {message.center(60)}\n{'='*60}")
            print("Press any key to continue...", end="", flush=True)
            
            try:
                # Use multiple input methods with short initial timeout
                if sys.stdin.isatty():
                    import select
                    
                    # First try with short timeout to detect immediate input
                    ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                    if ready:
                        sys.stdin.readline()  # Consume input
                    else:
                        # No immediate input, use longer timeout
                        ready, _, _ = select.select([sys.stdin], [], [], 1.0)
                        if ready:
                            sys.stdin.readline()  # Consume input
                        # else: timeout - just continue
                else:
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
            
            # Safely enable keypad mode
            if self._safe_keypad(msg_win, True):
                logger.debug("Keypad mode enabled for error window")
            else:
                logger.warning("Keypad mode failed for error window")
            
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
            if self._validate_window(self._screen):
                self.refresh()
                try:
                    key = self._screen.getch()
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
            else:
                logger.warning("Screen invalid in error window, using fallback")
                print(f"\n{'='*60}\nError: {message.center(60)}\n{'='*60}")
                input("Press Enter to continue...")
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
        except (curses.error, OSError, EOFError, TypeError) as e:
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
        
        Supported Key Codes:
            - Navigation: KEY_UP (259), KEY_DOWN (258)
            - Enter: KEY_ENTER (343, 10, 13)
            - Cancel: 27 (Escape), ord('q') (113)
            - Selection: '0'-'9' (ASCII 48-57)
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
        except (curses.error, OSError, EOFError, TypeError) as e:
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
        """Get user input with confirmation styling.
        
        Supported Key Codes:
            - Console fallback: Enter (10, 13)
        """
        logger.debug(f"get_input called with prompt={prompt[:60]}...")
        if not self._using_curses:
            # Use console fallback with robust terminal reset
            import subprocess
            try:
                # Restore terminal state with comprehensive reset
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["stty", "-icanon", "echo", "cr"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass  # Ignore stty errors
            
            # Clear screen and move to beginning with explicit codes
            print("\033[2J\033[1;1H\n", end="")
            sys.stdout.flush()
            
            try:
                # Use multiple input methods with short initial timeout
                if sys.stdin.isatty():
                    import select
                    
                    # First try with short timeout to detect immediate input
                    ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                    if ready:
                        return sys.stdin.readline().strip()
                    else:
                        # No immediate input, use longer timeout
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
        except (curses.error, OSError, EOFError, TypeError) as e:
            # Log but don't fail
            logger.warning(f"Unexpected error during get_input: {e}")
            # Fallback to console
            print(f"{prompt}")
            response = sys.stdin.readline().strip()
            return response

    def get_numbered_input(self, options: List[str], 
                          default: Optional[int] = None) -> Optional[int]:
        """Get numbered input from user.
        
        Supported Key Codes:
            - Enter: KEY_ENTER (343, 10, 13)
            - Cancel: 27 (Escape)
            - Selection: '0'-'9' (ASCII 48-57)
        """
        logger.debug(f"get_numbered_input called with options={len(options)}, default={default}")
        if not self._using_curses:
            # Use console fallback with robust terminal reset
            import subprocess
            try:
                # Restore terminal state with comprehensive reset
                subprocess.run(["stty", "sane"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["stty", "-icanon", "echo", "cr"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except:
                pass  # Ignore stty errors
            
            # Clear screen and move to beginning with explicit codes
            print("\033[2J\033[1;1H\n", end="")
            sys.stdout.flush()
            
            for i, opt in enumerate(options):
                marker = " (default)" if default is not None and i == default else ""
                print(f"  {i}. {opt}{marker}")
            print(f"Choice [{default if default is not None else 0}]: ", end="", flush=True)
            
            try:
                # Use multiple input methods with short initial timeout
                if sys.stdin.isatty():
                    import select
                    
                    # First try with short timeout to detect immediate input
                    ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                    if ready:
                        choice = sys.stdin.readline().strip()
                    else:
                        # No immediate input, use longer timeout
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
        except (curses.error, OSError, EOFError, TypeError) as e:
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