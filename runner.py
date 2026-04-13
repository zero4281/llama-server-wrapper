"""
runner.py — Process execution and management for llama-server.

This module handles launching llama-server, managing its lifecycle,
and implementing foreground/background modes with proper signal
handling and graceful shutdown.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


# Paths
PID_FILE = Path.cwd() / "llama-server.pid"
DEFAULT_LOG_FILE = Path.cwd() / "llama-server.log"


class Runner:
    """Manages the execution of llama-server process."""

    def __init__(self, args, config: dict):
        """
        Initialize Runner.

        Args:
            args: Parsed command-line arguments
            config: Configuration from config.json
        """
        self.args = args
        self.config = config
        self.pid_file = PID_FILE
        self.log_file = DEFAULT_LOG_FILE
        self.llama_server_path = Path.cwd() / "llama-cpp" / "llama-server"
        self.force_killed = False

    def run(self) -> None:
        """Main run method - launches llama-server."""
        # Load configuration options
        config_args = self._load_config_options()
        
        # Merge args and config options
        merged_args = self._merge_args(config_args)
        
        # Determine log file path
        log_path = self._resolve_log_file()
        
        # Build command
        command = self._build_command(log_path, merged_args)
        
        # Execute based on foreground flag
        if self.args.foreground:
            self._run_foreground(command, merged_args)
        else:
            self._run_background(command, merged_args)

    def _load_config_options(self) -> list:
        """
        Load options from config.json's llama-server.options section.

        Returns:
            List of command-line arguments
        """
        options = self.config.get("llama-server", {}).get("options", {})
        args = []
        for key, value in options.items():
            if value is not None and value != "":
                args.extend([f"--{key}", f"{value}"])
            else:
                args.append(f"--{key}")
        return args

    def _merge_args(self, config_args: list) -> list:
        """
        Merge configuration args with CLI args.

        CLI args take precedence over config args. This is a simple
        concatenation since argparse already handles duplicate handling.

        Args:
            config_args: Arguments from config.json

        Returns:
            Merged list of arguments
        """
        # Get pass-through args from main
        llama_args = getattr(self.args, 'llama_args', [])
        return config_args + llama_args

    def _resolve_log_file(self) -> Path:
        """
        Resolve the log file path based on priority.

        Priority order:
        1. --log-file CLI argument
        2. llama-server.options.log-file in config.json
        3. Default: llama-server.log

        Returns:
            Path to the log file
        """
        # 1. CLI argument
        if hasattr(self.args, 'log_file') and self.args.log_file:
            return Path(self.args.log_file)
        
        # 2. Config file
        config_log = self.config.get("llama-server", {}).get("options", {}).get("log-file")
        if config_log:
            return Path(config_log)
        
        # 3. Default
        return DEFAULT_LOG_FILE

    def _build_command(self, log_path: Path, merged_args: list) -> list:
        """
        Build the command to run llama-server.

        Args:
            log_path: Path to the log file
            merged_args: Merged arguments from config and CLI

        Returns:
            List of command arguments
        """
        cmd = [str(self.llama_server_path)]
        
        # Add merged args
        cmd.extend(merged_args)
        
        return cmd

    def _run_background(self, command: list, merged_args: list) -> None:
        """
        Run llama-server in the background as a daemon.

        Args:
            command: Command to execute
            merged_args: Merged arguments (kept for consistency with signature)
        """
        try:
            # Start process (no output capturing - llama-server writes to its own log)
            process = subprocess.Popen(command)

            # Write PID to file
            pid = process.pid
            with open(self.pid_file, "w") as f:
                f.write(str(pid))

            print(f"llama-server started with PID {pid}")
            print(f"PID file: {self.pid_file}")
            print(f"Log file: {self.log_file}")
            print("Press Ctrl+C to stop the server.")

        except Exception as e:
            self._cleanup()
            raise e

    def _run_foreground(self, command: list, merged_args: list) -> None:
        """
        Run llama-server in the foreground (blocking).

        Args:
            command: Command to execute
            merged_args: Merged arguments (kept for consistency with signature)
        """
        # Start process
        process = subprocess.Popen(command)

        # Write PID file
        pid = process.pid
        with open(self.pid_file, "w") as f:
            f.write(str(pid))
        print(f"llama-server started with PID {pid}")

        # Block until process exits (KeyboardInterrupt will propagate)
        process.wait()

    def _cleanup(self) -> None:
        """Clean up resources."""
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
            except OSError:
                pass


def stop_server() -> int:
    """
    Stop a running llama-server process.

    Returns:
        0 if clean shutdown, non-zero if force-killed
    """
    try:
        # Read PID file
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        print("No running llama-server found (no PID file).")
        return 1

    # Wait up to 60 seconds
        for i in range(60):
            try:
                if sys.platform == 'win32':
                    import ctypes
                    import ctypes.wintypes
                    kernel32 = ctypes.windll.kernel32
                    exit_code = ctypes.wintypes.DWORD()
                    result = kernel32.GetExitCodeProcess(
                        ctypes.c_int(pid), 
                        ctypes.byref(exit_code)
                    )
                    if result:
                        print(f"Process exited with code {exit_code.value}")
                        return 0
                else:
                    if not os.path.exists(PID_FILE):
                        print("Process exited cleanly")
                        return 0
                time.sleep(1)
            except OSError:
                break
        else:
            # Process didn't exit after 60 seconds, force kill
            print("Process did not exit cleanly, forcing termination...")
            
            if sys.platform == 'win32':
                import ctypes
                import ctypes.wintypes
                kernel32 = ctypes.windll.kernel32
                kernel32.TerminateProcess(ctypes.c_int(pid), 1)
            else:
                os.kill(pid, signal.SIGKILL)
            
            force_killed = True

        # Remove PID file
        if PID_FILE.exists():
            PID_FILE.unlink()

        if force_killed:
            print("llama-server force-terminated")
            return 1
        else:
            print("llama-server stopped")
            return 0

    except Exception as e:
        print(f"Error stopping llama-server: {e}")
        return 2


def main():
    """CLI entry point for runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Run llama-server")
    parser.add_argument("--foreground", "-f", action="store_true", 
                       help="Run in foreground mode")
    parser.add_argument("--log-file", type=str, help="Override log file path")
    parser.add_argument("--stop", action="store_true", help="Stop running server")
    parser.add_argument("args", nargs="*", help="Additional arguments for llama-server")

    args = parser.parse_args()

    if args.stop:
        exit_code = stop_server()
        sys.exit(exit_code)
    else:
        # In real implementation, this would create a Runner and call run()
        print("This is a standalone runner. Use via main.py.")


if __name__ == "__main__":
    main()
