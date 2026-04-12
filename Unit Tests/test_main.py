"""
Unit tests for main.py - CLI argument parsing and self-update functionality.
"""
import argparse
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add current directory to path for imports
sys.path.insert(0, str(Path.cwd()))

from main import Main
from llama_updater import LlamaUpdater


class TestMainClass(unittest.TestCase):
    """Test cases for the Main class."""

    def setUp(self):
        """Set up test fixtures."""
        self.main = Main()

    def tearDown(self):
        """Clean up test artifacts."""
        pass

    def test_init_initializes_attributes(self):
        """Test that __init__ initializes instance attributes."""
        self.assertEqual(self.main.args, None)
        self.assertEqual(self.main.config, None)
        self.assertEqual(self.main.logger, None)

    def test_parse_args_creates_parser(self):
        """Test that parse_args creates and configures ArgumentParser."""
        parser = self.main.parse_args([])
        self.assertIsInstance(parser, argparse.Namespace)

    def test_parse_args_sets_special_flags(self):
        """Test that parse_args recognizes special operation flags."""
        # Test --self-update
        args = self.main.parse_args(['--self-update'])
        self.assertTrue(args.self_update)

        # Test --install-llama
        args = self.main.parse_args(['--install-llama'])
        self.assertTrue(args.install_llama)

        # Test --update-llama
        args = self.main.parse_args(['--update-llama'])
        self.assertTrue(args.update_llama)

        # Test --stop-server
        args = self.main.parse_args(['--stop-server'])
        self.assertTrue(args.stop_server)

        # Test --foreground
        args = self.main.parse_args(['--foreground'])
        self.assertTrue(args.foreground)

        # Test -f alias
        args = self.main.parse_args(['-f'])
        self.assertTrue(args.foreground)

    def test_parse_args_sets_log_file_option(self):
        """Test that parse_args handles --log-file argument."""
        args = self.main.parse_args(['--log-file', 'custom.log'])
        self.assertEqual(args.log_file, 'custom.log')

    def test_parse_args_handles_llama_args(self):
        """Test that parse_args collects pass-through llama args."""
        args = self.main.parse_args(['--log-file', 'test.log', 'model1.gguf', 'model2.gguf'])
        self.assertEqual(len(args.llama_args), 2)
        self.assertEqual(args.llama_args, ['model1.gguf', 'model2.gguf'])

    def test_parse_args_with_empty_args(self):
        """Test that parse_args handles empty argument list."""
        args = self.main.parse_args([])
        self.assertFalse(args.self_update)
        self.assertFalse(args.install_llama)
        self.assertFalse(args.update_llama)
        self.assertFalse(args.stop_server)
        self.assertFalse(args.foreground)
        self.assertIsNone(args.log_file)
        self.assertEqual(args.llama_args, [])


class TestMainRunMethod(unittest.TestCase):
    """Test cases for the run method flow (integration tests)."""

    def setUp(self):
        """Set up test environment with temporary files."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.json"
        # Create default config
        self.config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": None
            }
        }
        self.main = Main()  # Create fresh instance

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_run_with_self_update(self):
        """Test that run method handles --self-update flag."""
        main = self.main
        main.args = main.parse_args(['--self-update'])
        main.config = self.config

        with patch('requests.get') as mock_get:
            mock_response = type('MockResponse', (), {
                'json': lambda self: {"zipball_url": "https://example.com/archive.zip"},
                'raise_for_status': lambda self: None,
                'content': b'fake content'
            })()
            mock_get.return_value = mock_response

            with self.assertRaises(SystemExit) as ctx:
                with patch.object(main, 'parse_args', return_value=main.args):
                    main.run()
            self.assertEqual(ctx.exception.code, 2)

    def test_run_with_install_llama(self):
        """Test that run method handles --install-llama flag."""
        main = self.main
        main.args = main.parse_args(['--install-llama'])
        main.config = self.config
        
        with patch.object(LlamaUpdater, 'install') as mock_install:
            with patch.object(main, 'parse_args', return_value=main.args):
                main.run()
            mock_install.assert_called_once()

    def test_run_with_update_llama(self):
        """Test that run method handles --update-llama flag."""
        main = self.main
        main.args = main.parse_args(['--update-llama'])
        main.config = self.config
        
        with patch.object(LlamaUpdater, 'update') as mock_update:
            with patch.object(main, 'parse_args', return_value=main.args):
                main.run()
            mock_update.assert_called_once()

    def test_run_with_stop_server(self):
        """Test that run method handles --stop-server flag."""
        main = self.main
        main.args = main.parse_args(['--stop-server'])
        main.config = self.config
        
        with patch('runner.stop_server') as mock_stop:
            mock_stop.return_value = 1  # No PID file exists
            with self.assertRaises(SystemExit) as ctx:
                with patch.object(main, 'parse_args', return_value=main.args):
                    main.run()
            self.assertEqual(ctx.exception.code, int(1))


class TestMainLoadConfig(unittest.TestCase):
    """Test cases for load_config method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.json"
        # Create default config
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
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_load_config_with_existing_file(self):
        """Test that load_config loads existing config.json."""
        # Write config to file
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        main = Main()
        main.config = main.load_config()
        
        # Verify basic structure (ignoring potentially added options)
        self.assertIn('options', main.config)
        self.assertIn('llama-server', main.config)
        self.assertIn('logging', main.config)
        self.assertEqual(main.config['logging']['enabled'], True)

    def test_load_config_auto_generates_default(self):
        """Test that load_config auto-generates default config if missing."""
        main = Main()
        main.config = main.load_config()
        
        self.assertIn('options', main.config)
        self.assertIn('llama-server', main.config)
        self.assertIn('logging', main.config)
        self.assertTrue(main.config['logging']['enabled'])


if __name__ == '__main__':
    unittest.main()
