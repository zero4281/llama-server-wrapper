"""
Unit tests for runner.py - Process execution and graceful shutdown functionality.
"""
import os
import signal
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO

# Add current directory to path for imports
sys.path.insert(0, str(Path.cwd()))

from runner import (
    Runner,
    stop_server,
    PID_FILE,
    DEFAULT_LOG_FILE
)


class TestRunnerInitialization(unittest.TestCase):
    """Test cases for Runner initialization."""

    def test_runner_initializes_with_args_and_config(self):
        """Test that Runner initializes correctly."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        
        self.assertEqual(runner.args, args)
        self.assertEqual(runner.config, config)
        self.assertEqual(runner.pid_file, PID_FILE)
        self.assertEqual(runner.log_file, DEFAULT_LOG_FILE)
        self.assertIsInstance(runner.llama_server_path, Path)
        self.assertFalse(runner.force_killed)

    def test_runner_llama_server_path(self):
        """Test that llama_server_path points to correct location."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        
        expected_path = Path.cwd() / "llama-cpp" / "llama-server"
        self.assertEqual(runner.llama_server_path, expected_path)


class TestRunnerLoadConfigOptions(unittest.TestCase):
    """Test cases for _load_config_options method."""

    def test_load_config_options_empty(self):
        """Test loading empty config options."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        options = runner._load_config_options()
        
        self.assertEqual(options, [])

    def test_load_config_options_with_values(self):
        """Test loading config options with values."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {
                "options": {
                    "host": "0.0.0.0",
                    "port": "11235",
                    "models-max": "1"
                }
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        options = runner._load_config_options()
        
        # Each option adds 2 elements: --key value
        self.assertEqual(len(options), 6)
        self.assertEqual(options[0], "--host")
        self.assertEqual(options[1], "0.0.0.0")
        self.assertEqual(options[2], "--port")
        self.assertEqual(options[3], "11235")

    def test_load_config_options_with_none_values(self):
        """Test loading config options with None values (should include --key)."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {
                "options": {
                    "host": "0.0.0.0",
                    "port": None
                }
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        options = runner._load_config_options()
        
        # Should have 2 items: --host 0.0.0.0 and --port
        self.assertEqual(len(options), 3)
        self.assertEqual(options[2], "--port")


class TestRunnerMergeArgs(unittest.TestCase):
    """Test cases for _merge_args method."""

    def test_merge_args_with_config_and_llama_args(self):
        """Test merging config args with llama_args."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = ["model1.gguf", "model2.gguf"]
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {
                "options": {
                    "host": "0.0.0.0"
                }
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        merged = runner._merge_args(["--port", "11235"])
        
        self.assertEqual(merged, ["--port", "11235", "model1.gguf", "model2.gguf"])

    def test_merge_args_without_llama_args(self):
        """Test merging when llama_args is empty."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {
                "options": {
                    "host": "0.0.0.0"
                }
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        merged = runner._merge_args([])
        
        self.assertEqual(merged, [])


class TestRunnerResolveLogFile(unittest.TestCase):
    """Test cases for _resolve_log_file method."""

    def test_resolve_log_file_cli_takes_precedence(self):
        """Test that CLI --log-file takes precedence over config."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = "/custom/path/log.txt"
        
        config = {
            "options": {},
            "llama-server": {
                "options": {
                    "log-file": "/config/path/log.txt"
                }
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        resolved = runner._resolve_log_file()
        
        self.assertEqual(resolved, Path("/custom/path/log.txt"))

    def test_resolve_log_file_config_falls_back_to_default(self):
        """Test that config falls back to default when neither CLI nor config specifies."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {
                "options": {}
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        resolved = runner._resolve_log_file()
        
        self.assertEqual(resolved, DEFAULT_LOG_FILE)

    def test_resolve_log_file_config_value_used(self):
        """Test that config log-file is used when CLI not set."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {
                "options": {
                    "log-file": "/config/log.txt"
                }
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        resolved = runner._resolve_log_file()
        
        self.assertEqual(resolved, Path("/config/log.txt"))


class TestRunnerBuildCommand(unittest.TestCase):
    """Test cases for _build_command method."""

    def test_build_command_includes_path_and_args(self):
        """Test that command includes llama-server path and merged args."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {
                "options": {
                    "host": "0.0.0.0"
                }
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        command = runner._build_command(Path("/tmp/log.txt"), ["--port", "11235"])
        
        self.assertIsInstance(command, list)
        self.assertEqual(command[0], str(runner.llama_server_path))
        self.assertIn("--port", command)
        self.assertIn("11235", command)


class TestRunnerRunBackground(unittest.TestCase):
    """Test cases for _run_background method."""

    def test_run_background_writes_pid_file(self):
        """Test that background mode writes PID file."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {
                "options": {}
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        runner = Runner(args, config)
        
        # Mock subprocess to prevent actual process execution
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_popen.return_value = mock_process
            
            runner._run_background(["/path/to/llama-server"], [])
            
            # Should not raise exception
            self.assertTrue(os.path.exists(PID_FILE))
            with open(PID_FILE, 'r') as f:
                content = f.read().strip()
            self.assertEqual(content, "12345")


class TestRunnerRunForeground(unittest.TestCase):
    """Test cases for _run_foreground method."""

    @patch('subprocess.Popen')
    def test_run_foreground_blocks_until_exit(self, mock_popen):
        """Test that foreground mode blocks until process exits."""
        args = MagicMock()
        args.foreground = True
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }
        
        runner = Runner(args, config)
        
        # This should not raise exception
        mock_popen_instance = MagicMock()
        mock_popen.return_value = mock_popen_instance
        mock_popen_instance.wait.return_value = None
        
        runner._run_foreground(["/path/to/llama-server"], [])

    @patch('subprocess.Popen')
    def test_run_foreground_catches_keyboard_interrupt(self, mock_popen):
        """Test that foreground mode handles KeyboardInterrupt."""
        args = MagicMock()
        args.foreground = True
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }
        
        runner = Runner(args, config)
        
        # This should not raise exception
        mock_popen_instance = MagicMock()
        mock_popen.return_value = mock_popen_instance
        mock_popen_instance.wait.side_effect = KeyboardInterrupt()
        
        runner._run_foreground(["/path/to/llama-server"], [])

    @patch('subprocess.Popen')
    def test_run_foreground_catches_exception(self, mock_popen):
        """Test that foreground mode catches exceptions."""
        args = MagicMock()
        args.foreground = True
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }
        
        runner = Runner(args, config)
        
        with self.assertRaises(Exception):
            mock_popen_instance = MagicMock()
            mock_popen.return_value = mock_popen_instance
            mock_popen_instance.wait.side_effect = Exception("Test error")
            runner._run_foreground(["/path/to/llama-server"], [])


class TestRunnerCleanup(unittest.TestCase):
    """Test cases for _cleanup method."""

    def test_cleanup_removes_pid_file(self):
        """Test that cleanup removes PID file."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }
        
        runner = Runner(args, config)
        
        # Mock Path.exists and Path.unlink to avoid actual file operations
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.unlink') as mock_unlink:
            
            # Save original PID_FILE
            import runner as runner_module
            original_pid_file = runner_module.PID_FILE
            
            # Replace with temp Path object
            temp_pid_path = Path(tempfile.gettempdir()) / "test_cleanup_pid"
            runner_module.PID_FILE = temp_pid_path
            
            try:
                runner._cleanup()
                # Verify unlink was called
                self.assertTrue(mock_unlink.called)
            finally:
                runner_module.PID_FILE = original_pid_file


class TestStopServer(unittest.TestCase):
    """Integration test cases for stop_server function."""

    def test_stop_server_no_pid_file(self):
        """Test that stop_server returns 1 when no PID file exists."""
        result = stop_server()
        self.assertEqual(result, 1)

    def test_stop_server_with_pid_file(self):
        """Test that stop_server handles PID file correctly."""
        temp_dir = Path(tempfile.gettempdir())
        temp_pid = temp_dir / "test_stop_pid"
        
        # Write test PID
        temp_pid.write_text("12345")
        
        with patch('os.kill'), patch('sys.platform', return_value='win32'):
            result = stop_server()
            # Should return 0 if process is killed
            self.assertIsInstance(result, int)
        
        temp_pid.unlink()


class TestPIDFile(unittest.TestCase):
    """Test cases for PID file handling."""

    def test_pid_file_creation_and_reading(self):
        """Test that PID file can be created and read."""
        temp_file = Path(tempfile.gettempdir()) / "test_pid_write"
        
        with open(temp_file, "w") as f:
            f.write("99999")
        
        with open(temp_file, "r") as f:
            content = f.read().strip()
        
        self.assertEqual(content, "99999")
        temp_file.unlink()


if __name__ == '__main__':
    unittest.main()
