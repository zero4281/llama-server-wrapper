"""
main.py — Main entry point for llama-server-wrapper.

This is the central CLI tool that orchestrates all operations:
- Self-update
- Installing/updating llama.cpp
- Stopping a running server
- Running llama-server with configured options
"""

import argparse
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path.cwd()))

from wrapper_config import load_config, get_logger
from llama_updater import LlamaUpdater
from runner import stop_server, Runner


class Main:
    """Main wrapper application."""

    def __init__(self):
        self.args = None
        self.config = None
        self.logger = None

    def parse_args(self, args: list = None) -> argparse.Namespace:
        """
        Parse command-line arguments.

        Args:
            args: List of arguments (defaults to sys.argv[1:])

        Returns:
            Parsed arguments namespace
        """
        parser = argparse.ArgumentParser(
            prog="llama-server-wrapper",
            description="Wrapper for llama.cpp server operations"
        )

        # Special operations
        parser.add_argument("--self-update", action="store_true",
                          help="Pull latest code from GitHub and restart")
        parser.add_argument("--install-llama", action="store_true",
                          help="Download and install latest llama.cpp release")
        parser.add_argument("--update-llama", action="store_true",
                          help="Update existing llama.cpp to latest release")
        parser.add_argument("--stop-server", action="store_true",
                          help="Gracefully stop a running llama-server")

        # Run options
        parser.add_argument("--log-file", type=str, metavar="PATH",
                          help="Override llama-server log file path")

        # Pass-through arguments for llama-server
        parser.add_argument("llama_args", nargs="*",
                          help="Additional arguments passed to llama-server")

        return parser.parse_args(args)

    def load_config(self) -> dict:
        """
        Load or auto-generate configuration.

        Returns:
            Configuration dictionary
        """
        return load_config()

    def perform_self_update(self, args: argparse.Namespace) -> None:
        """
        Perform self-update from GitHub.

        Args:
            args: Parsed arguments
        """
        print("Performing self-update...")
        
        try:
            import requests
            import zipfile
            import tempfile
            from ui_manager import UIManager
            
            ui = UIManager("Self-Update")
            
            # Source selection menu
            source_options = [
                {"label": "Latest release (recommended)", "description": "Most recent official release"},
                {"label": "Previous release", "description": "Select from available releases"},
                {"label": "Repository HEAD", "description": "Main branch latest commit"},
            ]
            
            default_source = 0
            selected_source = ui.render_menu(source_options, default=default_source)
            
            if selected_source == -1:
                print("Update cancelled.")
                sys.exit(0)
            
            selected_zip_url = ""
            selected_tag = ""
            selected_name = ""
            
            if selected_source == 0:
                # Latest release
                url = "https://api.github.com/repos/zero4281/llama-server-wrapper/releases/latest"
                headers = {
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                release = response.json()
                selected_tag = release["tag_name"]
                selected_name = release["name"]
                selected_zip_url = release.get("zipball_url") or ""
            elif selected_source == 1:
                # Fetch previous releases
                url = "https://api.github.com/repos/zero4281/llama-server-wrapper/releases"
                headers = {
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                releases = response.json()
                
                # Show previous releases menu
                prev_releases = [
                    {"label": rel["tag_name"], "description": f"{rel['name']} ({rel['published_at']})"}
                    for rel in releases
                ]
                
                prev_choice = ui.render_menu(prev_releases)
                if prev_choice == -1:
                    print("Update cancelled.")
                    sys.exit(0)
                
                selected_release = releases[prev_choice]
                selected_tag = selected_release["tag_name"]
                selected_name = selected_release["name"]
                selected_zip_url = selected_release.get("zipball_url") or ""
            else:
                # Repository HEAD
                selected_zip_url = "https://github.com/zero4281/llama-server-wrapper/archive/refs/heads/main.zip"
                selected_tag = "HEAD"
                selected_name = "main branch HEAD"
            
            # Confirmation prompt
            confirm = ui.render_confirmation(
                f"Update {selected_tag if selected_tag != 'HEAD' else selected_name}"
            )
            
            if not confirm:
                print("Update cancelled.")
                sys.exit(0)
            
            # Download and extract
            with tempfile.TemporaryDirectory() as tmpdir:
                extract_path = Path(tmpdir) / "llama-server-wrapper"
                extract_path.mkdir()
                
                # Download the zip file
                headers = {
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
                zip_response = requests.get(selected_zip_url, headers=headers, timeout=60)
                zip_response.raise_for_status()
                zip_content = zip_response.content
                
                # Extract to temp directory
                with zipfile.ZipFile(Path(zip_content), 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                
                # Copy updated files
                project_root = Path.cwd()
                for file_path in extract_path.rglob("*"):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(extract_path)
                        target = project_root / rel_path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        # Only overwrite if different
                        if not target.exists() or file_path.stat().st_mtime != target.stat().st_mtime:
                            target.write_bytes(file_path.read_bytes())
                            print(f"Updated: {rel_path}")
                
                print("\nSelf-update complete!")
            
            # Restart with same arguments
            print(f"Restarting with original arguments: {args}")
            
            # Re-parse args to preserve llama_args
            new_args = [sys.argv[0]] + list(args)
            
            # Clear any cached modules to force reimport
            modules_to_clear = [
                'main', 'runner', 'llama_updater', 'logging'
            ]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]
            
            # Execute restart using subprocess
            import subprocess
            
            # Execute and replace current process
            subprocess.run([sys.executable] + new_args, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         text=True)
            
            # If we get here, something went wrong, exit with error
            print("Restart failed, exiting.")
            sys.exit(2)
            
        except Exception as e:
            print(f"Self-update failed: {e}")
            sys.exit(2)

    def run(self) -> None:
        """Main execution flow."""
        # Parse arguments
        self.args = self.parse_args()
        
        # Load config (auto-generate if missing)
        self.config = self.load_config()
        
        # Set up logging
        logging_config = self.config.get("logging", {})
        if logging_config.get("enabled", True):
            self.logger = get_logger(self.config, logging_config.get("level", "INFO"))
        else:
            self.logger = None

        # Handle special operations
        if self.args.self_update:
            print("\n[Self-Update Mode]\n")
            self.perform_self_update(self.args)
            return
        
        if self.args.install_llama:
            print("\n[Install llama.cpp]\n")
            try:
                LlamaUpdater().install()
            except SystemExit:
                raise
            except Exception as e:
                # Re-raise if it's a known updater error
                from llama_updater import (RateLimitError, GitHubAPIError, 
                                          DownloadError, ExtractionError, 
                                          PlatformNotFoundError, LlamaUpdaterError)
                if isinstance(e, (RateLimitError, GitHubAPIError, 
                                 DownloadError, ExtractionError, 
                                 PlatformNotFoundError, LlamaUpdaterError)):
                    raise
                print(f"Error: {e}")
                sys.exit(1)
            return
        
        if self.args.update_llama:
            print("\n[Update llama.cpp]\n")
            try:
                LlamaUpdater().update()
            except SystemExit:
                raise
            except Exception as e:
                # Re-raise if it's a known updater error
                from llama_updater import (RateLimitError, GitHubAPIError, 
                                          DownloadError, ExtractionError, 
                                          PlatformNotFoundError, LlamaUpdaterError)
                if isinstance(e, (RateLimitError, GitHubAPIError, 
                                 DownloadError, ExtractionError, 
                                 PlatformNotFoundError, LlamaUpdaterError)):
                    raise
                print(f"Error: {e}")
                sys.exit(1)
            return
        
        if self.args.stop_server:
            print("\n[Stop Server Mode]\n")
            exit_code = stop_server()
            sys.exit(exit_code)
        
        # Default: Run llama-server
        print("\n[Run llama-server]\n")
        
        # Check if llama-cpp is installed
        llama_cpp_path = Path.cwd() / "llama-cpp" / "llama-server"
        if not llama_cpp_path.exists():
            print("Error: llama-cpp is not installed. Please run with --install-llama first.")
            print("\nUsage: ./llama-server-wrapper --install-llama")
            sys.exit(1)
        
        runner = Runner(self.args, self.config)
        runner.run()


if __name__ == "__main__":
    app = Main()
    app.run()
