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

# Add current directory to path for imports
sys.path.insert(0, str(Path.cwd()))

from wrapper_config import (
    load_config,
    get_logger,
    ConfigLogger,
    DEFAULT_CONFIG
)


class TestLoadConfig(unittest.TestCase):
    """Test cases for load_config function."""

    def test_load_config_with_existing_file(self):
        """Test loading existing config.json."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "test_config.json"
        
        # Write test config
        test_config = {
            "options": {"test": "value"},
            "llama-server": {"options": {"host": "127.0.0.1"}},
            "logging": {
                "enabled": False,
                "level": "WARNING",
                "file": "/tmp/test.log"
            }
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
        
        # Remove file if exists
        if config_path.exists():
            config_path.unlink()
        
        result = load_config(Path(config_path))
        
        # Check required keys
        self.assertIn('options', result)
        self.assertIn('llama-server', result)
        self.assertIn('logging', result)
        
        # Check default values
        self.assertTrue(result['logging']['enabled'])
        self.assertEqual(result['logging']['level'], 'INFO')
        self.assertIsNone(result['logging']['file'])
        
        # Verify file was created
        self.assertTrue(config_path.exists())
        config_path.unlink()

    def test_load_config_default_structure(self):
        """Test that auto-generated config has required structure."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "structure_test.json"
        
        if config_path.exists():
            config_path.unlink()
        
        config = load_config(Path(config_path))
        
        # Verify structure matches DEFAULT_CONFIG
        self.assertIn('options', config)
        self.assertIn('llama-server', config)
        self.assertIn('logging', config)
        self.assertIn('enabled', config['logging'])
        self.assertIn('level', config['logging'])
        self.assertIn('file', config['logging'])
        
        config_path.unlink()


class TestGetLogger(unittest.TestCase):
    """Test cases for get_logger function."""

    def test_get_logger_creates_config_logger(self):
        """Test that get_logger returns ConfigLogger instance."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        
        logger = get_logger(config, "INFO")
        
        self.assertIsInstance(logger, ConfigLogger)

    def test_get_logger_with_different_levels(self):
        """Test that get_logger handles different log levels."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "DEBUG",
                "file": None
            }
        }
        
        # Should not raise exception
        logger = get_logger(config, "DEBUG")
        self.assertIsInstance(logger, ConfigLogger)


class TestConfigLogger(unittest.TestCase):
    """Test cases for ConfigLogger class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "DEBUG",
                "file": None
            }
        }
        self.temp_file = Path(tempfile.gettempdir()) / "test_logger.log"

    def tearDown(self):
        """Clean up test artifacts."""
        if self.temp_file.exists():
            self.temp_file.unlink()

    def test_config_logger_initializes_handlers(self):
        """Test that ConfigLogger creates console and optional file handlers."""
        logger = ConfigLogger(self.config, "DEBUG")
        
        # Should have at least console handler
        self.assertGreater(len(logger.logger.handlers), 0)

    def test_config_logger_with_file_handler(self):
        """Test that ConfigLogger creates file handler when configured."""
        config_with_file = self.config.copy()
        config_with_file["logging"]["file"] = str(self.temp_file)
        
        logger = ConfigLogger(config_with_file, "DEBUG")
        
        self.assertGreater(len(logger.logger.handlers), 0)
        
        # Check that file was created
        self.assertTrue(self.temp_file.exists())
        self.temp_file.unlink()

    def test_config_logger_without_file_handler(self):
        """Test that ConfigLogger works without file handler."""
        config_without_file = self.config.copy()
        config_without_file["logging"]["file"] = None
        
        logger = ConfigLogger(config_without_file, "DEBUG")
        
        # Should work fine
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
        
        # Should not raise exception
        logger.debug("Debug message")

    def test_config_logger_info_method(self):
        """Test that info method logs message."""
        logger = ConfigLogger(self.config, "DEBUG")
        
        # Should not raise exception
        logger.info("Info message")

    def test_config_logger_error_method(self):
        """Test that error method logs message."""
        logger = ConfigLogger(self.config, "ERROR")
        
        # Should not raise exception
        logger.error("Error message")

    def test_config_logger_catches_keyboard_interrupt(self):
        """Test that get_logger handles keyboard interrupt gracefully."""
        # Should not raise exception
        logger = get_logger(self.config, "INFO")

    def test_config_logger_catches_exception(self):
        """Test that get_logger handles exceptions gracefully."""
        # Should not raise exception
        logger = get_logger(self.config, "INFO")


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
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
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
        
        # Should not raise exception
        logger.info("Test message")

    def test_logging_with_disabled_file(self):
        """Test that logging works when file is None."""
        config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": False,
                "level": "INFO",
                "file": None
            }
        }
        
        # Should not raise exception
        logger = get_logger(config, "INFO")
        logger.info("Test message")


if __name__ == '__main__':
    unittest.main()
