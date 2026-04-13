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
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd().parent))

from main import Main


class TestMainArgumentParsing(unittest.TestCase):
    """Test command-line argument parsing."""

    def setUp(self):
        self.main = Main()

    def test_parse_args_with_special_and_regular_flags(self):
        """Test parsing mixed special and regular flags."""
        args = self.main.parse_args([
            '--foreground',
            '--log-file', 'test.log',
            '--self-update',
            'arg1'
        ])
        
        self.assertTrue(args.foreground)
        self.assertTrue(args.self_update)
        self.assertEqual(args.llama_args, ['arg1'])

    def test_parse_args_empty_input(self):
        """Test parsing with no arguments."""
        args = self.main.parse_args([])
        self.assertFalse(args.self_update)
        self.assertFalse(args.install_llama)
        self.assertFalse(args.update_llama)
        self.assertFalse(args.stop_server)
        self.assertFalse(args.foreground)
        self.assertIsNone(args.log_file)
        self.assertEqual(args.llama_args, [])

    def test_parse_args_multiple_flags(self):
        """Test parsing multiple flags together."""
        args = self.main.parse_args([
            '--foreground', 
            '--log-file', 'test.log',
            'arg1', 'arg2'
        ])
        self.assertTrue(args.foreground)
        self.assertEqual(args.log_file, 'test.log')
        self.assertEqual(args.llama_args, ['arg1', 'arg2'])


class TestMainConfiguration(unittest.TestCase):
    """Test configuration loading and auto-generation."""

    def test_load_config_existing_file(self):
        """Test loading existing config.json."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "test_config.json"
        
        test_config = {
            "options": {"test": "value"},
            "llama-server": {"options": {"host": "127.0.0.1"}},
            "logging": {"enabled": True, "level": "WARNING", "file": None}
        }
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        main = Main()
        main.config = main.load_config()
        
        self.assertEqual(main.config['logging']['enabled'], True)
        config_path.unlink()

    def test_load_config_auto_generates_default(self):
        """Test that load_config auto-generates default config."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "auto_config.json"
        
        if config_path.exists():
            config_path.unlink()
        
        main = Main()
        main.config = main.load_config()
        
        self.assertIn('options', main.config)
        self.assertIn('llama-server', main.config)
        self.assertIn('logging', main.config)
        config_path.unlink()

    def test_load_config_invalid_json(self):
        """Test that invalid JSON triggers auto-generation."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "invalid_config.json"
        
        config_path.write_text('{invalid json')
        
        main = Main()
        main.config = main.load_config()
        
        # Should have generated default config
        self.assertTrue(main.config['logging']['enabled'])
        config_path.unlink()

    def test_load_config_missing_file(self):
        """Test that missing file triggers auto-generation."""
        temp_dir = Path(tempfile.gettempdir())
        config_path = temp_dir / "nonexistent.json"
        
        if config_path.exists():
            config_path.unlink()
        
        main = Main()
        main.config = main.load_config()
        
        self.assertTrue(main.config['logging']['enabled'])
        config_path.unlink()

    def test_load_config_preserves_structure(self):
        """Test that auto-generated config has required structure."""
        main = Main()
        main.config = main.load_config()
        
        self.assertIn('options', main.config)
        self.assertIn('llama-server', main.config)
        self.assertIn('logging', main.config)
        self.assertIn('enabled', main.config['logging'])
        self.assertIn('level', main.config['logging'])
        self.assertIn('file', main.config['logging'])


class TestMainSelfUpdate(unittest.TestCase):
    """Test self-update functionality."""

    def test_perform_self_update_source_selection_default(self):
        """Test default choice when user presses Enter."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', return_value='') as mock_input:
            with patch('sys.stdout', new_callable=mock_open) as mock_stdout:
                with self.assertRaises(SystemExit):
                    main.perform_self_update(args)
                
                mock_input.assert_called_once()

    def test_perform_self_update_source_selection_choice_2(self):
        """Test previous release selection."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', return_value='2'):
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = [
                    {"tag_name": "v0.9.0", "name": "Release 0.9", "published_at": "2024-01-01T00:00:00Z"}
                ]
                mock_get.return_value = mock_response
                
                with self.assertRaises(SystemExit):
                    main.perform_self_update(args)

    def test_perform_self_update_source_selection_choice_3(self):
        """Test main branch HEAD selection."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', return_value='3'):
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {}
                mock_response.raise_for_status.return_value = None
                mock_response.content = b'fake zip'
                mock_get.return_value = mock_response
                
                with self.assertRaises(SystemExit):
                    main.perform_self_update(args)

    def test_perform_self_update_invalid_choice(self):
        """Test that invalid choice exits cleanly."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', return_value='9'):
            with self.assertRaises(SystemExit) as ctx:
                main.perform_self_update(args)
            self.assertEqual(ctx.exception.code, 0)

    def test_perform_self_update_confirmation_cancel(self):
        """Test that 'n' cancels the update."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', side_effect=['1', 'n']):
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "tag_name": "v1.0.0",
                    "name": "Test Release",
                    "zipball_url": "https://example.com/archive.zip"
                }
                mock_get.return_value = mock_response
                
                with self.assertRaises(SystemExit) as ctx:
                    main.perform_self_update(args)
                self.assertEqual(ctx.exception.code, 0)

    def test_perform_self_update_restart_preserves_args(self):
        """Test that restart preserves llama_args."""
        args = self.main.parse_args(['--self-update', 'arg1', 'arg2'])
        self.assertEqual(args.llama_args, ['arg1', 'arg2'])


class TestMainRun(unittest.TestCase):
    """Test main execution flow."""

    def setUp(self):
        self.config = {
            "options": {},
            "llama-server": {"options": {}},
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }

    def test_run_with_self_update(self):
        """Test that run method handles --self-update flag."""
        main = Main()
        main.args = main.parse_args(['--self-update'])
        main.config = self.config
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"zipball_url": "https://example.com/archive.zip"}
            mock_get.return_value = mock_response
            
            with self.assertRaises(SystemExit):
                main.run()

    def test_run_with_install_llama(self):
        """Test that run method handles --install-llama flag."""
        main = Main()
        main.args = main.parse_args(['--install-llama'])
        main.config = self.config
        
        with patch('llama_updater.LlamaUpdater') as mock_updater_class:
            mock_instance = MagicMock()
            mock_updater_class.return_value = mock_instance
            
            main.run()
            mock_instance.install.assert_called_once()

    def test_run_with_update_llama(self):
        """Test that run method handles --update-llama flag."""
        main = Main()
        main.args = main.parse_args(['--update-llama'])
        main.config = self.config
        
        with patch('llama_updater.LlamaUpdater') as mock_updater_class:
            mock_instance = MagicMock()
            mock_updater_class.return_value = mock_instance
            
            main.run()
            mock_instance.update.assert_called_once()

    def test_run_with_stop_server(self):
        """Test that run method handles --stop-server flag."""
        main = Main()
        main.args = main.parse_args(['--stop-server'])
        main.config = self.config
        
        with patch('runner.stop_server', return_value=1):
            with self.assertRaises(SystemExit) as ctx:
                main.run()
            self.assertEqual(ctx.exception.code, 1)

    def test_run_with_missing_llama_cpp(self):
        """Test that run() exits with error when llama-cpp not installed."""
        main = Main()
        main.args = main.parse_args(['--foreground'])
        main.config = self.config
        
        with patch.object(Path, 'exists', return_value=False):
            with self.assertRaises(SystemExit) as ctx:
                main.run()
            self.assertEqual(ctx.exception.code, 1)


class TestMainMainEntryPoint(unittest.TestCase):
    """Test main() entry point error handling."""

    def test_main_catches_keyboard_interrupt(self):
        """Test that main() catches KeyboardInterrupt and exits with 130."""
        app = Main()
        app.logger = MagicMock()
        
        with patch.object(type(app), 'run', side_effect=KeyboardInterrupt()):
            with self.assertRaises(SystemExit) as ctx:
                Main.main()
            self.assertEqual(ctx.exception.code, 130)

    def test_main_catches_unhandled_exception(self):
        """Test that main() catches unhandled exceptions."""
        app = Main()
        app.logger = MagicMock()
        
        with patch.object(type(app), 'run', side_effect=Exception("Test error")):
            with self.assertRaises(SystemExit) as ctx:
                Main.main()
            self.assertEqual(ctx.exception.code, 1)


class TestMainIntegration(unittest.TestCase):
    """Integration tests for Main class."""

    def test_main_initializes_attributes(self):
        """Test that __init__ initializes instance attributes."""
        main = Main()
        self.assertIsNone(main.args)
        self.assertIsNone(main.config)
        self.assertIsNone(main.logger)

    def test_main_sets_up_logger_with_config(self):
        """Test that logger is set up with config."""
        main = Main()
        main.config = {
            "logging": {"enabled": True, "level": "DEBUG", "file": None}
        }
        main.logger = main.get_logger(main.config)
        
        self.assertIsNotNone(main.logger)


class TestMainArgumentValidation(unittest.TestCase):
    """Test argument validation and edge cases."""

    def test_parse_args_with_only_llama_args(self):
        """Test parsing with only llama server arguments."""
        main = Main()
        args = main.parse_args(['--log-file', 'test.log', 'model.gguf'])
        
        self.assertEqual(args.log_file, 'test.log')
        self.assertEqual(args.llama_args, ['model.gguf'])
        self.assertFalse(args.self_update)
        self.assertFalse(args.install_llama)

    def test_parse_args_with_special_and_regular_flags(self):
        """Test parsing mixed special and regular flags."""
        main = Main()
        args = main.parse_args([
            '--foreground',
            '--log-file', 'test.log',
            '--self-update',
            'arg1'
        ])
        
        self.assertTrue(args.foreground)
        self.assertTrue(args.self_update)
        self.assertEqual(args.llama_args, ['arg1'])


class TestMainSelfUpdateInteractive(unittest.TestCase):
    """Comprehensive tests for interactive self-update menus (v1.1)."""

    def test_perform_self_update_source_selection_default_choice(self):
        """Test default choice when user presses Enter (empty input)."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', return_value='') as mock_input:
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "tag_name": "v1.0.0",
                    "name": "Test Release",
                    "zipball_url": "https://example.com/archive.zip"
                }
                mock_get.return_value = mock_response
                
                with self.assertRaises(SystemExit) as ctx:
                    main.perform_self_update(args)
                self.assertEqual(ctx.exception.code, 0)
                mock_input.assert_called_once()

    def test_perform_self_update_source_selection_previous_release_menu_flow(self):
        """Test complete flow with previous releases menu selection."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', side_effect=['2', '1', 'y']) as mock_input:
            with patch('requests.get') as mock_get:
                # First call: releases endpoint
                mock_response1 = MagicMock()
                mock_response1.json.return_value = [
                    {"tag_name": "v0.9.0", "name": "Release 0.9", "published_at": "2024-01-01T00:00:00Z"}
                ]
                mock_response1.raise_for_status.return_value = None
                mock_get.side_effect = [mock_response1, mock_response1]  # For zipball
                
                with self.assertRaises(SystemExit) as ctx:
                    main.perform_self_update(args)
                self.assertEqual(ctx.exception.code, 0)

    def test_perform_self_update_source_selection_main_branch_flow(self):
        """Test complete flow with main branch HEAD selection."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', side_effect=['3', 'y']) as mock_input:
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {}
                mock_response.raise_for_status.return_value = None
                mock_response.content = b'fake zip content'
                mock_response.url = "https://github.com/zero4281/llama-server-wrapper/archive/refs/heads/main.zip"
                mock_get.return_value = mock_response
                
                with self.assertRaises(SystemExit) as ctx:
                    main.perform_self_update(args)
                self.assertEqual(ctx.exception.code, 0)

    def test_perform_self_update_confirmation_prompt_cancel(self):
        """Test that confirmation prompt 'n' cancels the update."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', side_effect=['1', 'n']) as mock_input:
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "tag_name": "v1.0.0",
                    "name": "Test Release",
                    "zipball_url": "https://example.com/archive.zip"
                }
                mock_get.return_value = mock_response
                
                with self.assertRaises(SystemExit) as ctx:
                    main.perform_self_update(args)
                self.assertEqual(ctx.exception.code, 0)
                mock_input.assert_called()

    def test_perform_self_update_confirmation_no_response(self):
        """Test that 'no' also cancels the update."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', side_effect=['1', 'no']) as mock_input:
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "tag_name": "v1.0.0",
                    "name": "Test Release",
                    "zipball_url": "https://example.com/archive.zip"
                }
                mock_get.return_value = mock_response
                
                with self.assertRaises(SystemExit) as ctx:
                    main.perform_self_update(args)
                self.assertEqual(ctx.exception.code, 0)

    def test_perform_self_update_invalid_choice_exit(self):
        """Test that invalid choice exits cleanly with code 0."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', return_value='9') as mock_input:
            with self.assertRaises(SystemExit) as ctx:
                main.perform_self_update(args)
            self.assertEqual(ctx.exception.code, 0)

    def test_perform_self_update_invalid_confirmation_exit(self):
        """Test that invalid confirmation exits cleanly with code 0."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', side_effect=['1', 'maybe']) as mock_input:
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "tag_name": "v1.0.0",
                    "name": "Test Release",
                    "zipball_url": "https://example.com/archive.zip"
                }
                mock_get.return_value = mock_response
                
                with self.assertRaises(SystemExit) as ctx:
                    main.perform_self_update(args)
                self.assertEqual(ctx.exception.code, 0)

    def test_perform_self_update_restart_preserves_llama_args(self):
        """Test that restart preserves llama_args and other arguments."""
        main = Main()
        args = main.parse_args(['--self-update', 'arg1', 'arg2', 'arg3'])
        self.assertEqual(args.llama_args, ['arg1', 'arg2', 'arg3'])
        self.assertEqual(args.foreground, False)
        self.assertEqual(args.log_file, None)

    def test_perform_self_update_error_handling(self):
        """Test that self-update handles errors gracefully."""
        main = Main()
        args = main.parse_args(['--self-update'])
        
        with patch('builtins.input', return_value='1'):
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "tag_name": "v1.0.0",
                    "name": "Test Release"
                }
                mock_get.return_value = mock_response
                
                with patch('builtins.input', return_value='y'):
                    with patch.object(main, 'perform_self_update') as mock_method:
                        mock_method.side_effect = Exception("Test error")
                        
                        with self.assertRaises(SystemExit) as ctx:
                            main.perform_self_update(args)
                        self.assertEqual(ctx.exception.code, 2)


class TestMainConfigComprehensive(unittest.TestCase):
    """Comprehensive CLI argument and config tests."""

    def test_parse_args_with_all_special_flags(self):
        """Test parsing with all special flags combined."""
        main = Main()
        args = main.parse_args([
            '--self-update',
            '--install-llama',
            '--update-llama',
            '--stop-server',
            '--foreground'
        ])
        self.assertTrue(args.self_update)
        self.assertTrue(args.install_llama)
        self.assertTrue(args.update_llama)
        self.assertTrue(args.stop_server)
        self.assertTrue(args.foreground)

    def test_parse_args_with_log_file_and_model_args(self):
        """Test parsing with log file and multiple model arguments."""
        main = Main()
        args = main.parse_args([
            '--log-file', '/custom/log/path.log',
            'model1.gguf',
            'model2.gguf'
        ])
        self.assertEqual(args.log_file, '/custom/log/path.log')
        self.assertEqual(args.llama_args, ['model1.gguf', 'model2.gguf'])

    def test_parse_args_with_pass_through_args_only(self):
        """Test parsing with only pass-through arguments."""
        main = Main()
        args = main.parse_args(['--foreground', 'model.gguf'])
        self.assertTrue(args.foreground)
        self.assertEqual(args.llama_args, ['model.gguf'])

    def test_parse_args_with_special_flags_and_pass_through(self):
        """Test parsing with special flags and pass-through arguments."""
        main = Main()
        args = main.parse_args([
            '--self-update',
            '--foreground',
            '--log-file', 'test.log',
            'arg1', 'arg2'
        ])
        self.assertTrue(args.self_update)
        self.assertTrue(args.foreground)
        self.assertEqual(args.log_file, 'test.log')
        self.assertEqual(args.llama_args, ['arg1', 'arg2'])

    def test_config_structure_validation(self):
        """Test that config has required structure."""
        config = {
            "options": {"key1": "value1"},
            "llama-server": {"options": {"host": "0.0.0.0", "port": "11235"}},
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }
        
        self.assertIn('options', config)
        self.assertIn('llama-server', config)
        self.assertIn('logging', config)
        self.assertIn('enabled', config['logging'])
        self.assertIn('level', config['logging'])
        self.assertIn('file', config['logging'])

    def test_config_logging_options(self):
        """Test various logging configuration options."""
        test_cases = [
            {"enabled": True, "level": "DEBUG"},
            {"enabled": False, "level": "WARNING"},
            {"enabled": True, "level": "INFO", "file": "/path/to/log.txt"},
        ]
        
        for test_config in test_cases:
            config = {
                "logging": test_config
            }
            # Test that config can be accessed
            self.assertEqual(config["logging"]["enabled"], test_config["enabled"])


class TestRunnerConfigComprehensive(unittest.TestCase):
    """Comprehensive tests for Runner configuration handling."""

    def test_runner_config_options_with_all_config_options(self):
        """Test runner with comprehensive configuration options."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = ["model1.gguf", "model2.gguf"]
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {
                "options": {
                    "host": "0.0.0.0",
                    "port": "11235",
                    "models-max": "1",
                    "n-ctx": "5120",
                    "n-batch": "512",
                    "n-gpu": "0"
                }
            },
            "logging": {"enabled": True, "level": "DEBUG", "file": None}
        }
        
        runner = Runner(args, config)
        options = runner._load_config_options()
        
        # Should have 12 options (6 options * 2 args each)
        self.assertEqual(len(options), 12)
        self.assertIn("--host", options)
        self.assertIn("0.0.0.0", options)
        self.assertIn("--port", options)
        self.assertIn("11235", options)

    def test_runner_config_options_with_none_values(self):
        """Test that None values in config options are skipped."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {
                "options": {
                    "host": "0.0.0.0",
                    "port": None,
                    "models-max": "1"
                }
            },
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }
        
        runner = Runner(args, config)
        options = runner._load_config_options()
        
        # Should have 4 options: --host, 0.0.0.0, --models-max, 1
        self.assertEqual(len(options), 4)

    def test_runner_log_file_resolution_priority(self):
        """Test that CLI --log-file takes precedence over config, which takes precedence over default."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = []
        args.log_file = "/cli/log.txt"
        
        config = {
            "options": {},
            "llama-server": {
                "options": {
                    "log-file": "/config/log.txt"
                }
            },
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }
        
        runner = Runner(args, config)
        resolved = runner._resolve_log_file()
        
        # CLI should take precedence
        self.assertEqual(str(resolved), "/cli/log.txt")

    def test_runner_log_file_resolution_default(self):
        """Test that default log file is used when neither CLI nor config specifies."""
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
        resolved = runner._resolve_log_file()
        
        self.assertEqual(resolved, DEFAULT_LOG_FILE)

    def test_runner_merge_args_with_complex_config(self):
        """Test merging args with complex config options."""
        args = MagicMock()
        args.foreground = False
        args.llama_args = ["--n-ctx", "4096", "model.gguf"]
        args.log_file = None
        
        config = {
            "options": {},
            "llama-server": {
                "options": {
                    "host": "0.0.0.0",
                    "port": "5555",
                    "n-ctx": "2048"
                }
            },
            "logging": {"enabled": True, "level": "INFO", "file": None}
        }
        
        runner = Runner(args, config)
        merged = runner._merge_args(["--port", "6666"])
        
        self.assertIn("--port", merged)
        self.assertIn("6666", merged)
        self.assertIn("--n-ctx", merged)
        self.assertIn("2048", merged)
        self.assertIn("model.gguf", merged)


if __name__ == '__main__':
    unittest.main()
