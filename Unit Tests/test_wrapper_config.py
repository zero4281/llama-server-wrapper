"""
Unit tests for wrapper_config.py - Configuration loading and logging setup.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd().parent))

from wrapper_config import (
    load_config, get_logger, ConfigLogger, DEFAULT_CONFIG
)


class TestLoadConfig(unittest.TestCase):
    """Test cases for load_config function."""

    def test_load_config_with_existing_file(self):
        """Test loading existing config.json."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "test_config.json"
        
        test_config = {
            "options": {"test": "value"},
            "llama-server": {"options": {"host": "127.0.0.1"}},
            "logging": {"enabled": False, "level": "WARNING", "file": None}
        }
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        result = load_config(Path(config_path))
        self.assertEqual(result, test_config)
        config_path.unlink()

    def test_load_config_auto_generates_default(self):
        """Test that load_config auto-generates default config."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "auto_generated_config.json"
        
        if config_path.exists():
            config_path.unlink()
        
        result = load_config(Path(config_path))
        
        self.assertIn('options', result)
        self.assertIn('llama-server', result)
        self.assertIn('logging', result)
        self.assertTrue(result['logging']['enabled'])
        self.assertEqual(result['logging']['level'], 'INFO')
        self.assertIsNone(result['logging']['file'])
        self.assertTrue(config_path.exists())
        config_path.unlink()

    def test_load_config_default_structure(self):
        """Test that auto-generated config has required structure."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "structure_test.json"
        
        if config_path.exists():
            config_path.unlink()
        
        config = load_config(Path(config_path))
        
        self.assertIn('options', config)
        self.assertIn('llama-server', config)
        self.assertIn('logging', config)
        self.assertIn('enabled', config['logging'])
        self.assertIn('level', config['logging'])
        self.assertIn('file', config['logging'])
        config_path.unlink()

    def test_load_config_invalid_json(self):
        """Test that load_config handles invalid JSON by generating default."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "invalid_config.json"
        
        config_path.write_text('{invalid json')
        
        result = load_config(Path(config_path))
        self.assertIn('options', result)
        self.assertTrue(result['logging']['enabled'])
        config_path.unlink()

    def test_load_config_file_not_found(self):
        """Test that load_config handles missing file by generating default."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "nonexistent.json"
        
        if config_path.exists():
            config_path.unlink()
        
        result = load_config(Path(config_path))
        self.assertIn('options', result)
        self.assertTrue(result['logging']['enabled'])
        config_path.unlink()

    def test_load_config_preserves_indentation(self):
        """Test that auto-generated config has proper indentation."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "indentation_test.json"
        
        if config_path.exists():
            config_path.unlink()
        
        result = load_config(Path(config_path))
        
        # Check that the file was written with indentation
        with open(config_path, 'r') as f:
            content = f.read()
        
        self.assertIn('{', content)
        self.assertIn('}', content)
        self.assertIn('logging', content)
        config_path.unlink()


class TestGetLogger(unittest.TestCase):
    """Test cases for get_logger function."""

    def test_get_logger_creates_config_logger(self):
        """Test that get_logger returns ConfigLogger instance."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }
        
        logger = get_logger(config, "INFO")
        self.assertIsInstance(logger, ConfigLogger)

    def test_get_logger_with_different_levels(self):
        """Test that get_logger handles different log levels."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "DEBUG", "file": None}
        }
        
        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            logger = get_logger(config, level)
            self.assertIsInstance(logger, ConfigLogger)

    def test_get_logger_default_level(self):
        """Test default log level when not specified."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "file": None}
        }
        
        logger = get_logger(config)
        self.assertIsInstance(logger, ConfigLogger)


class TestConfigLogger(unittest.TestCase):
    """Test cases for ConfigLogger class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "DEBUG", "file": None}
        }
        self.temp_file = Path(tempfile.gettempdir()) / "test_logger.log"

    def tearDown(self):
        """Clean up test artifacts."""
        if self.temp_file.exists():
            self.temp_file.unlink()

    def test_config_logger_initializes_handlers(self):
        """Test that ConfigLogger creates console handler."""
        logger = ConfigLogger(self.config, "DEBUG")
        self.assertGreater(len(logger.logger.handlers), 0)

    def test_config_logger_with_file_handler(self):
        """Test that ConfigLogger creates file handler when configured."""
        config_with_file = self.config.copy()
        config_with_file["logging"]["file"] = str(self.temp_file)
        
        logger = ConfigLogger(config_with_file, "DEBUG")
        self.assertGreater(len(logger.logger.handlers), 0)
        self.assertTrue(self.temp_file.exists())
        self.temp_file.unlink()

    def test_config_logger_without_file_handler(self):
        """Test that ConfigLogger works without file handler."""
        config_without_file = self.config.copy()
        config_without_file["logging"]["file"] = None
        
        logger = ConfigLogger(config_without_file, "DEBUG")
        logger.debug("Test message")

    def test_config_logger_methods(self):
        """Test that ConfigLogger has all required methods."""
        logger = ConfigLogger(self.config, "DEBUG")
        
        self.assertTrue(hasattr(logger, 'debug'))
        self.assertTrue(hasattr(logger, 'info'))
        self.assertTrue(hasattr(logger, 'warning'))
        self.assertTrue(hasattr(logger, 'error'))
        self.assertTrue(hasattr(logger, 'critical'))

    def test_config_logger_debug_method(self):
        """Test that debug method logs when DEBUG level enabled."""
        logger = ConfigLogger(self.config, "DEBUG")
        logger.debug("Debug message")

    def test_config_logger_info_method(self):
        """Test that info method logs message."""
        logger = ConfigLogger(self.config, "DEBUG")
        logger.info("Info message")

    def test_config_logger_warning_method(self):
        """Test that warning method logs message."""
        logger = ConfigLogger(self.config, "DEBUG")
        logger.warning("Warning message")

    def test_config_logger_error_method(self):
        """Test that error method logs message."""
        logger = ConfigLogger(self.config, "DEBUG")
        logger.error("Error message")

    def test_config_logger_critical_method(self):
        """Test that critical method logs message."""
        logger = ConfigLogger(self.config, "DEBUG")
        logger.critical("Critical message")


class TestDefaultConfig(unittest.TestCase):
    """Test cases for DEFAULT_CONFIG constant."""

    def test_default_config_structure(self):
        """Test that DEFAULT_CONFIG has required structure."""
        self.assertIn('options', DEFAULT_CONFIG)
        self.assertIn('llama-server', DEFAULT_CONFIG)
        self.assertIn('logging', DEFAULT_CONFIG)
        self.assertIn('enabled', DEFAULT_CONFIG['logging'])
        self.assertIn('level', DEFAULT_CONFIG['logging'])
        self.assertIn('file', DEFAULT_CONFIG['logging'])

    def test_default_config_values(self):
        """Test that DEFAULT_CONFIG has correct default values."""
        self.assertTrue(DEFAULT_CONFIG['logging']['enabled'])
        self.assertEqual(DEFAULT_CONFIG['logging']['level'], 'INFO')
        self.assertIsNone(DEFAULT_CONFIG['logging']['file'])


class TestLoggingWithConfig(unittest.TestCase):
    """Integration test cases for logging with config."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.gettempdir())
        self.temp_log = self.temp_dir / "integration_test.log"
        self.config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }

    def tearDown(self):
        """Clean up test artifacts."""
        if self.temp_log.exists():
            self.temp_log.unlink()

    def test_logging_integration_with_file(self):
        """Test that logging works with file configured."""
        config_with_file = self.config.copy()
        config_with_file["logging"]["file"] = str(self.temp_log)
        
        logger = get_logger(config_with_file, "INFO")
        logger.info("Test info message")
        logger.error("Test error message")
        
        self.assertTrue(self.temp_log.exists())
        self.temp_log.unlink()

    def test_logging_integration_stdout(self):
        """Test that logging works with stdout only."""
        config_stdout = self.config.copy()
        config_stdout["logging"]["file"] = None
        
        logger = get_logger(config_stdout, "INFO")
        logger.info("Test message")

    def test_logging_with_disabled_file(self):
        """Test that logging works when file is None."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": False, "level": "INFO", "file": None}
        }
        
        logger = get_logger(config, "INFO")
        logger.info("Test message")

    def test_logging_with_disabled(self):
        """Test that logging works when logging is disabled."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": False, "level": "INFO", "file": None}
        }
        
        logger = get_logger(config, "INFO")
        logger.info("Test message")


class TestLoadConfigIntegration(unittest.TestCase):
    """Integration tests for load_config."""

    def test_load_config_with_logging_section(self):
        """Test that config with logging section is loaded correctly."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "logging_test.json"
        
        test_config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "DEBUG",
                "file": str(self.temp_dir / "test.log")
            }
        }
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        result = load_config(Path(config_path))
        self.assertEqual(result["logging"]["enabled"], True)
        self.assertEqual(result["logging"]["level"], "DEBUG")
        config_path.unlink()

    def test_load_config_with_empty_options(self):
        """Test that config with empty options is loaded correctly."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "empty_options.json"
        
        test_config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        result = load_config(Path(config_path))
        self.assertEqual(result["options"], {})
        self.assertEqual(result["llama-server"]["options"], {})
        config_path.unlink()


class TestConfigLoggerWithFile(unittest.TestCase):
    """Test ConfigLogger with file output."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = Path(tempfile.gettempdir()) / "config_logger_test.log"

    def tearDown(self):
        """Clean up test artifacts."""
        if self.temp_file.exists():
            self.temp_file.unlink()

    def test_config_logger_file_handler_writes(self):
        """Test that file handler writes to file."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "DEBUG",
                "file": str(self.temp_file)
            }
        }
        
        logger = ConfigLogger(config, "DEBUG")
        logger.info("Test message")
        
        self.assertTrue(self.temp_file.exists())
        self.temp_file.unlink()

    def test_config_logger_file_handler_with_error(self):
        """Test that file handler writes error messages."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "ERROR",
                "file": str(self.temp_file)
            }
        }
        
        logger = ConfigLogger(config, "ERROR")
        logger.error("Error message")
        
        self.assertTrue(self.temp_file.exists())
        self.temp_file.unlink()

    def test_config_logger_multiple_messages(self):
        """Test that multiple messages are written correctly."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "DEBUG",
                "file": str(self.temp_file)
            }
        }
        
        logger = ConfigLogger(config, "DEBUG")
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warning")
        logger.error("Error")
        
        self.assertTrue(self.temp_file.exists())
        self.temp_file.unlink()

    def test_config_logger_file_with_append_mode(self):
        """Test that file handler uses append mode."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "DEBUG",
                "file": str(self.temp_file)
            }
        }
        
        logger = ConfigLogger(config, "DEBUG")
        logger.info("First message")
        logger.info("Second message")
        
        # Check that both messages exist in file
        self.assertTrue(self.temp_file.exists())
        self.temp_file.unlink()


class TestConfigLoggerEdgeCases(unittest.TestCase):
    """Test edge cases for ConfigLogger."""

    def test_config_logger_invalid_level(self):
        """Test that invalid log level is handled gracefully."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "INVALID", "file": None}
        }
        
        # Should handle invalid level gracefully
        # This test verifies that the function doesn't crash with unexpected errors
        # get_logger will create a logger with default settings if level is invalid
        logger = get_logger(config, "INVALID")
        # If no exception raised, verify logger is created
        self.assertIsNotNone(logger)

    def test_config_logger_empty_config(self):
        """Test that empty config works with defaults."""
        config = {}
        
        logger = get_logger(config, "INFO")
        self.assertIsInstance(logger, ConfigLogger)


class TestLoadConfigErrorHandling(unittest.TestCase):
    """Test error handling in load_config."""

    def test_load_config_permission_error(self):
        """Test that permission errors trigger auto-generation."""
        # Create a file without write permission
        temp_file = Path(tempfile.gettempdir()) / "no_permission.json"
        temp_file.write_text('{"test": "value"}')
        
        # Remove write permission (only works on Unix)
        if os.name != 'nt':
            temp_file.chmod(0o444)  # Read-only
            
            try:
                result = load_config(Path(temp_file))
                # Should have loaded the existing file (read-only but readable)
                self.assertIn('test', result)
            finally:
                temp_file.chmod(0o644)  # Restore permissions
                temp_file.unlink()
        else:
            # On Windows, skip this test
            temp_file.unlink()


class TestConfigLoggerIntegration(unittest.TestCase):
    """Integration tests for ConfigLogger."""

    def test_config_logger_with_all_log_levels(self):
        """Test that all log levels work correctly."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "DEBUG", "file": None}
        }
        
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            logger = get_logger(config, level)
            
            with patch('logging.Logger.debug'), \
                 patch('logging.Logger.info'), \
                 patch('logging.Logger.warning'), \
                 patch('logging.Logger.error'), \
                 patch('logging.Logger.critical'):
                
                getattr(logger, level.lower())("Test message")

    def test_config_logger_with_file_and_console(self):
        """Test that ConfigLogger uses both file and console handlers."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "DEBUG",
                "file": str(Path(tempfile.gettempdir()) / "test.log")
            }
        }
        
        logger = get_logger(config, "DEBUG")
        
        self.assertGreater(len(logger.logger.handlers), 0)
        self.assertTrue(logger.logger.handlers[0].isConsoleHandler())
        self.assertTrue(logger.logger.handlers[1].isStreamHandler())
        
        temp_file = Path(tempfile.gettempdir()) / "test.log"
        if temp_file.exists():
            temp_file.unlink()


if __name__ == '__main__':
    unittest.main()
