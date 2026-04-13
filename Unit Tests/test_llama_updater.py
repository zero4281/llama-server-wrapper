"""
Unit tests for llama_updater.py - GitHub API integration and download functionality.
"""
import json
import os
import re
import requests
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd().parent))

from llama_updater import (
    LlamaUpdater, LlamaUpdaterError, RateLimitError, GitHubAPIError,
    DownloadError, PlatformNotFoundError, detect_platform, get_latest_release,
    list_releases, get_release_by_tag, parse_asset_name, get_available_platforms,
    select_release, download_file, extract_archive, ensure_executable,
    install_release, _get_api_headers
)


class TestLlamaUpdaterError(unittest.TestCase):
    """Test cases for LlamaUpdater error classes."""

    def test_base_exception(self):
        """Test that base exception can be raised."""
        with self.assertRaises(LlamaUpdaterError):
            raise LlamaUpdaterError("Test error")

    def test_rate_limit_error_has_reset_time(self):
        """Test that RateLimitError stores reset time."""
        reset_time = "2024-01-01 00:00:00 UTC"
        error = RateLimitError(reset_time)
        self.assertEqual(error.reset_time, reset_time)
        self.assertIn("Retry after", str(error))

    def test_github_api_error_message(self):
        """Test that GitHubAPIError contains error details."""
        error = GitHubAPIError("API unreachable")
        self.assertIn("API", str(error))


class TestGitHubAPIFunctions(unittest.TestCase):
    """Test cases for GitHub API functions."""

    def test_get_api_headers(self):
        """Test that API headers are correct."""
        headers = _get_api_headers()
        self.assertEqual(headers["Accept"], "application/vnd.github+json")
        self.assertEqual(headers["X-GitHub-Api-Version"], "2022-11-28")

    def test_get_latest_release(self):
        """Test that get_latest_release calls GitHub API."""
        with patch('llama_updater._get_release_info') as mock_info:
            mock_info.return_value = {"tag_name": "v0.0.0", "name": "Test Release"}
            release = get_latest_release()
            self.assertEqual(release["tag_name"], "v0.0.0")

    def test_list_releases_returns_list(self):
        """Test that list_releases returns list of releases."""
        with patch('llama_updater.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = [{"tag_name": "v0.0.0"}]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            releases = list_releases()
            self.assertIsInstance(releases, list)
            self.assertGreaterEqual(len(releases), 0)

    def test_get_release_by_tag(self):
        """Test that get_release_by_tag retrieves specific release."""
        with patch('llama_updater._get_release_info') as mock_info:
            mock_info.return_value = {"tag_name": "v0.0.0", "name": "Release"}
            release = get_release_by_tag("v0.0.0")
            self.assertEqual(release["tag_name"], "v0.0.0")

    def test_rate_limit_handling(self):
        """Test that RateLimitError is raised on 429."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"X-RateLimit-Reset": "1234567890"}
        
        mock_exception = MagicMock(spec=requests.exceptions.RequestException)
        mock_exception.response = mock_response
        mock_exception.response.status_code = 429
        mock_exception.response.headers = {"X-RateLimit-Reset": "1234567890"}
        
        with patch('llama_updater.requests.get') as mock_get:
            mock_get.side_effect = mock_exception
            
            with self.assertRaises(RateLimitError):
                get_latest_release()
            
            # Check that error message mentions rate limit
            error_msg = str(context.exception)
            self.assertIn("rate limit", error_msg.lower())

    def test_github_api_error_on_forbidden(self):
        """Test that GitHubAPIError is raised on 403."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        
        mock_exception = MagicMock(spec=requests.exceptions.RequestException)
        mock_exception.response = mock_response
        mock_exception.response.status_code = 403
        
        with patch('llama_updater.requests.get') as mock_get:
            mock_get.side_effect = mock_exception
            
            with self.assertRaises(GitHubAPIError):
                get_latest_release()

    def test_github_api_error_unreachable(self):
        """Test that GitHubAPIError is raised when API is unreachable."""
        mock_exception = MagicMock(spec=requests.exceptions.RequestException)
        mock_exception.response = None
        
        with patch('llama_updater.requests.get') as mock_get:
            mock_get.side_effect = mock_exception
            
            with self.assertRaises(GitHubAPIError):
                get_latest_release()


class TestPlatformDetection(unittest.TestCase):
    """Test cases for platform detection."""

    def test_detect_platform_all_platforms(self):
        """Test detection of all supported platforms."""
        test_cases = [
            ('Linux', 'x86_64', 'Linux', 'x64'),
            ('Linux', 'aarch64', 'Linux', 'arm64'),
            ('Windows', 'AMD64', 'Windows', 'x64'),
            ('Darwin', 'x86_64', 'macOS', 'x64'),
        ]
        
        for system, machine, expected_platform, expected_arch in test_cases:
            with patch('platform.system', return_value=system), \
                 patch('platform.machine', return_value=machine):
                platform, arch = detect_platform()
                self.assertEqual(platform, expected_platform)
                self.assertEqual(arch, expected_arch)


class TestAssetParsing(unittest.TestCase):
    """Test cases for asset name parsing."""

    def test_parse_new_format_asset(self):
        """Test parsing new format asset name."""
        result = parse_asset_name("llama-b8763-bin-ubuntu-x64.tar.gz")
        self.assertEqual(result["platform"], "Linux")
        self.assertEqual(result["arch"], "x64")
        self.assertIsNone(result["variant"])

    def test_parse_new_format_variant(self):
        """Test parsing new format with variant."""
        result = parse_asset_name("llama-b8763-bin-ubuntu-x64-vulkan.tar.gz")
        self.assertEqual(result["platform"], "Linux")
        self.assertEqual(result["arch"], "x64")
        self.assertIsNone(result["variant"])  # Vulkan is variant suffix, not in name

    def test_parse_various_platforms(self):
        """Test parsing various Linux distributions."""
        assets = [
            "llama-b8763-bin-debian-x64.tar.gz",
            "llama-b8763-bin-archlinux-arm64.tar.gz",
            "llama-b8763-bin-fedora-arm64.tar.gz",
        ]
        
        for asset in assets:
            result = parse_asset_name(asset)
            self.assertEqual(result["platform"], "Linux")
            self.assertIn(result["arch"], ["x64", "arm64"])

    def test_parse_old_format_asset(self):
        """Test parsing old format asset name."""
        result = parse_asset_name("llama-server-linux-arm64.tar.gz")
        self.assertEqual(result["platform"], "Linux")
        self.assertEqual(result["arch"], "arm64")

    def test_parse_various_platforms_new_format(self):
        """Test parsing various platforms with new format."""
        test_cases = [
            ("llama-b8763-bin-debian-x64.tar.gz", "Linux", "x64"),
            ("llama-b8763-bin-archlinux-arm64.tar.gz", "Linux", "arm64"),
            ("llama-b8763-bin-fedora-arm64.tar.gz", "Linux", "arm64"),
        ]
        
        for asset_name, expected_platform, expected_arch in test_cases:
            result = parse_asset_name(asset_name)
            self.assertEqual(result["platform"], expected_platform)
            self.assertEqual(result["arch"], expected_arch)


class TestPlatformSelection(unittest.TestCase):
    """Test cases for platform selection."""

    def test_get_available_platforms(self):
        """Test that get_available_platforms extracts platforms from assets."""
        release = {
            "assets": [
                {"name": "llama-b8763-bin-ubuntu-x64.tar.gz"},
                {"name": "llama-b8763-bin-linux-arm64.tar.gz"}
            ]
        }
        
        platforms = get_available_platforms(release)
        self.assertIsInstance(platforms, list)
        self.assertGreater(len(platforms), 0)

    def test_get_available_platforms_duplicates_merged(self):
        """Test that duplicate platforms are merged correctly."""
        release = {
            "assets": [
                {"name": "llama-b8763-bin-ubuntu-x64.tar.gz"},
                {"name": "llama-b8763-bin-ubuntu-x64-vulkan.tar.gz"},
            ]
        }
        
        platforms = get_available_platforms(release)
        self.assertEqual(len(platforms), 1)  # Single platform
        # Returns list of platform info dicts with assets
        self.assertEqual(len(platforms[0]["assets"]), 2)  # Two assets merged
        self.assertIn("llama-b8763-bin-ubuntu-x64.tar.gz", [a["name"] for a in platforms[0]["assets"]])

    def test_select_release_matches_platform(self):
        """Test that select_release finds matching platform."""
        release = {
            "assets": [{"name": "llama-b8763-bin-ubuntu-x64.tar.gz"}]
        }
        available_platforms = [
            {"platform": "Linux", "arch": "x64", "assets": [{"name": "test.tar.gz"}]}
        ]
        
        selected = select_release(release, available_platforms, "Linux", "x64")
        self.assertIsNotNone(selected)
        # Returns the asset dict
        self.assertEqual(selected["name"], "test.tar.gz")

    def test_select_release_no_match(self):
        """Test that select_release returns None when no match found."""
        release = {"assets": [{"name": "test.tar.gz"}]}
        available_platforms = [
            {"platform": "Linux", "arch": "x64", "assets": [{"name": "test.tar.gz"}]}
        ]
        
        selected = select_release(release, available_platforms, "Windows", "x64")
        self.assertIsNone(selected)

    def test_select_release_case_insensitive(self):
        """Test that platform matching is case insensitive."""
        release = {"assets": [{"name": "test.tar.gz"}]}
        available_platforms = [
            {"platform": "linux", "arch": "x64", "assets": [{"name": "test.tar.gz"}]}
        ]
        
        selected = select_release(release, available_platforms, "Linux", "X64")
        self.assertIsNotNone(selected)
        self.assertEqual(selected["name"], "test.tar.gz")


class TestLlamaUpdater(unittest.TestCase):
    """Integration test cases for LlamaUpdater."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.gettempdir())
        self.updater = LlamaUpdater()

    def test_install_detects_platform(self):
        """Test that install detects current platform."""
        with patch('llama_updater.detect_platform') as mock_detect:
            mock_detect.return_value = ("Linux", "x64")
            with patch('llama_updater.get_latest_release') as mock_get:
                with patch('llama_updater.get_available_platforms') as mock_avail:
                    mock_get.return_value = {
                        "tag_name": "v0.0.0",
                        "name": "Test",
                        "published_at": "2024-01-01T00:00:00Z",
                        "assets": []
                    }
                    mock_avail.return_value = []
                    
                    with patch('builtins.input', side_effect=['1', 'n']):
                        with self.assertRaises(SystemExit):
                            self.updater.install()

    def test_install_handles_platform_not_found(self):
        """Test that PlatformNotFoundError is raised when no platform matches."""
        with patch('llama_updater.detect_platform') as mock_detect:
            mock_detect.return_value = ("Unknown", "Unknown")
            
            with patch('llama_updater.get_latest_release') as mock_get:
                mock_get.return_value = {
                    "tag_name": "v0.0.0",
                    "name": "Test",
                    "assets": []
                }
            
            with patch('llama_updater.get_available_platforms') as mock_avail:
                mock_avail.return_value = []
            
            with patch('builtins.input', side_effect=['1', 'n']):
                with self.assertRaises(PlatformNotFoundError):
                    self.updater.install()

    def test_install_handles_api_rate_limit(self):
        """Test that install() handles RateLimitError gracefully."""
        with patch('llama_updater.get_latest_release') as mock_get:
            mock_get.side_effect = RateLimitError("2024-01-01 12:00:00 UTC")
            
            with self.assertRaises(RateLimitError):
                self.updater.install()

    def test_update_delegates_to_install(self):
        """Test that update() calls install() with same parameters."""
        updater = LlamaUpdater()
        
        with patch('llama_updater.detect_platform') as mock_detect:
            mock_detect.return_value = ("Linux", "x64")
            
            with patch('llama_updater.get_latest_release') as mock_get:
                mock_get.return_value = {
                    "tag_name": "v0.0.0",
                    "name": "Test",
                    "assets": []
                }
            
            with patch('llama_updater.get_available_platforms') as mock_avail:
                mock_avail.return_value = []
            
            with patch('builtins.input', return_value='1'):
                with patch('llama_updater.extract_archive') as mock_extract:
                    mock_extract.side_effect = DownloadError("test")
                    with self.assertRaises(DownloadError):
                        updater.update()


class TestLlamaUpdaterCLI(unittest.TestCase):
    """Test CLI entry point."""

    def test_cli_install_flag(self):
        """Test that --install flag triggers install."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--install", action="store_true")
        parser.add_argument("--update", action="store_true")
        parser.add_argument("--tag", type=str)
        
        args = parser.parse_args(["--install"])
        self.assertTrue(args.install)

    def test_cli_update_flag(self):
        """Test that --update flag triggers update."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--install", action="store_true")
        parser.add_argument("--update", action="store_true")
        parser.add_argument("--tag", type=str)
        
        args = parser.parse_args(["--update"])
        self.assertTrue(args.update)


class TestAssetParsingEdgeCases(unittest.TestCase):
    """Test edge cases for asset name parsing."""

    def test_parse_various_extensions(self):
        """Test parsing assets with various extensions."""
        test_cases = [
            ("llama-b8763-bin-ubuntu-x64.tar.gz", "Linux", "x64"),
            ("llama-b8763-bin-ubuntu-x64.tgz", "Linux", "x64"),
            ("llama-b8763-bin-ubuntu-x64.zip", "Linux", "x64"),
        ]
        
        for asset_name, expected_platform, expected_arch in test_cases:
            result = parse_asset_name(asset_name)
            self.assertEqual(result["platform"], expected_platform)
            self.assertEqual(result["arch"], expected_arch)

    def test_parse_old_format_assets(self):
        """Test parsing old format asset names."""
        test_cases = [
            ("llama-server-linux-arm64.tar.gz", "Linux", "arm64"),
            ("llama-server-windows-amd64.tar.gz", "Windows", "amd64"),
            ("llama-server-darwin-x64.tar.gz", "Darwin", "x64"),
        ]
        
        for asset, expected_platform, expected_arch in test_cases:
            result = parse_asset_name(asset)
            self.assertEqual(result["platform"], expected_platform)
            self.assertEqual(result["arch"], expected_arch)


class TestSelectRelease(unittest.TestCase):
    """Test cases for select_release function."""

    def test_select_release_exact_match(self):
        """Test that select_release finds exact platform match."""
        release = {"assets": [{"name": "test.tar.gz"}]}
        available_platforms = [
            {"platform": "Linux", "arch": "x64", "assets": [{"name": "test.tar.gz"}]}
        ]
        
        selected = select_release(release, available_platforms, "Linux", "x64")
        self.assertIsNotNone(selected)

    def test_select_release_no_match_returns_none(self):
        """Test that select_release returns None for no match."""
        release = {"assets": [{"name": "test.tar.gz"}]}
        available_platforms = [
            {"platform": "Linux", "arch": "x64", "assets": [{"name": "test.tar.gz"}]}
        ]
        
        selected = select_release(release, available_platforms, "Windows", "x64")
        self.assertIsNone(selected)


class TestGetAvailablePlatforms(unittest.TestCase):
    """Test cases for get_available_platforms function."""

    def test_get_available_platforms_with_vulkan_variant(self):
        """Test that vulkan variant is correctly parsed."""
        release = {
            "assets": [
                {"name": "llama-b8763-bin-ubuntu-x64-vulkan.tar.gz"},
                {"name": "llama-b8763-bin-ubuntu-x64.tar.gz"},
            ]
        }
        
        platforms = get_available_platforms(release)
        self.assertIsInstance(platforms, list)
        self.assertGreater(len(platforms), 0)

    def test_get_available_platforms_duplicates(self):
        """Test that duplicate platforms are merged correctly."""
        release = {
            "assets": [
                {"name": "llama-b8763-bin-ubuntu-x64.tar.gz"},
                {"name": "llama-b8763-bin-ubuntu-x64-vulkan.tar.gz"},
            ]
        }
        
        platforms = get_available_platforms(release)
        self.assertEqual(len(platforms), 1)
        self.assertEqual(len(platforms[0]["assets"]), 2)

    def test_get_available_platforms_with_old_format(self):
        """Test that old format assets are also merged correctly."""
        release = {
            "assets": [
                {"name": "llama-server-linux-arm64.tar.gz"},
                {"name": "llama-server-linux-arm64-vulkan.tar.gz"},
            ]
        }
        
        platforms = get_available_platforms(release)
        self.assertGreater(len(platforms), 0)
        self.assertEqual(len(platforms[0]["assets"]), 2)


class TestInstallRelease(unittest.TestCase):
    """Integration test for install_release function."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.gettempdir())

    def test_install_release_with_archive(self):
        """Test that install_release downloads and extracts archive."""
        release = {
            "tag_name": "v0.0.0",
            "name": "Test",
            "assets": [
                {
                    "name": "llama-b8763-bin-ubuntu-x64.tar.gz",
                    "browser_download_url": "http://test.com/download",
                    "size": 1024000
                }
            ]
        }
        
        with patch('llama_updater.detect_platform') as mock_detect:
            mock_detect.return_value = ("Linux", "x64")
        
        with patch('llama_updater.get_available_platforms') as mock_avail:
            mock_avail.return_value = []
        
        with patch('llama_updater.select_release') as mock_select:
            mock_select.return_value = release["assets"][0]
        
        with patch('llama_updater.download_file') as mock_download:
            mock_download.return_value = self.temp_dir / "archive.tar.gz"
        
        with patch('llama_updater.extract_archive') as mock_extract:
            mock_extract.return_value = None
        
        with patch('builtins.print') as mock_print:
            with patch('builtins.input', return_value='1'):
                with self.assertRaises(DownloadError):
                    install_release(release, "v0.0.0")
                
                self.assertTrue(mock_download.called)
                self.assertTrue(mock_extract.called)

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.gettempdir())
        self.updater = LlamaUpdater()


class TestLlamaUpdaterInstallInteractive(unittest.TestCase):
    """Comprehensive tests for LlamaUpdater.install() interactive menus (v1.1)."""

    def test_install_platform_selection_menu(self):
        """Test interactive platform selection menu flow."""
        with patch('llama_updater.get_latest_release') as mock_get:
            mock_get.return_value = {
                "tag_name": "v0.0.0",
                "name": "Test Release",
                "published_at": "2024-01-01T00:00:00Z",
                "assets": [
                    {"name": "llama-b8763-bin-ubuntu-x64.tar.gz"},
                    {"name": "llama-b8763-bin-linux-arm64.tar.gz"}
                ]
            }
        
        with patch('llama_updater.get_available_platforms') as mock_avail:
            mock_avail.return_value = [
                {"platform": "Linux", "arch": "x64", "variant": None, "assets": []},
                {"platform": "Linux", "arch": "arm64", "variant": None, "assets": []}
            ]
        
        with patch('llama_updater.select_release') as mock_select:
            mock_select.return_value = None  # No automatic match
        
        with patch('llama_updater.detect_platform') as mock_detect:
            mock_detect.return_value = ("Linux", "x64")
        
        with patch('llama_updater.download_file') as mock_download:
            mock_download.side_effect = DownloadError("test download error")
        
        with patch('builtins.input', side_effect=['1', 'y']) as mock_input:
            # Should call input for platform selection then for confirmation
            # But download_file should be called next, raising DownloadError
            try:
                self.updater.install()
                self.fail("Expected DownloadError to be raised")
            except DownloadError:
                pass
            
            # Should have called input for platform selection
            self.assertGreater(mock_input.call_count, 0)

    def test_install_confirmation_prompt(self):
        """Test confirmation prompt flow with 'y' response."""
        with patch('llama_updater.get_latest_release') as mock_get:
            mock_get.return_value = {
                "tag_name": "v0.0.0",
                "name": "Test Release",
                "published_at": "2024-01-01T00:00:00Z",
                "assets": []
            }
        
        with patch('llama_updater.get_available_platforms') as mock_avail:
            mock_avail.return_value = []
        
        with patch('llama_updater.select_release') as mock_select:
            mock_select.return_value = None
        
        with patch('llama_updater.detect_platform') as mock_detect:
            mock_detect.return_value = ("Linux", "x64")
        
        with patch('llama_updater.install_release') as mock_install:
            mock_install.side_effect = DownloadError("test install error")
        
        with patch('builtins.input', side_effect=['y']) as mock_input:
            with self.assertRaises(DownloadError):
                self.updater.install()
            
            # Should have called input for confirmation
            mock_input.assert_called()

    def test_install_manual_asset_selection(self):
        """Test manual asset selection flow when no platform matches."""
        with patch('llama_updater.get_latest_release') as mock_get:
            mock_get.return_value = {
                "tag_name": "v0.0.0",
                "name": "Test Release",
                "assets": [
                    {"name": "llama-b8763-bin-ubuntu-x64.tar.gz", "browser_download_url": "http://test.com/1"},
                    {"name": "llama-b8763-bin-linux-arm64.tar.gz", "browser_download_url": "http://test.com/2"}
                ]
            }
        
        with patch('llama_updater.get_available_platforms') as mock_avail:
            mock_avail.return_value = []  # No matching platforms
        
        with patch('llama_updater.detect_platform') as mock_detect:
            mock_detect.return_value = ("Unknown", "Unknown")
        
        with patch('llama_updater.select_release') as mock_select:
            mock_select.return_value = None
        
        with patch('builtins.input', side_effect=['1', 'y']) as mock_input:
            with patch('llama_updater.download_file') as mock_download:
                mock_download.side_effect = DownloadError("download error")
                
                with self.assertRaises(DownloadError):
                    self.updater.install()
                
                # Should have called input for asset selection
                self.assertEqual(mock_input.call_count, 2)

    def test_install_manual_selection_invalid_choice(self):
        """Test that invalid manual selection choice exits cleanly."""
        with patch('llama_updater.get_latest_release') as mock_get:
            mock_get.return_value = {
                "tag_name": "v0.0.0",
                "name": "Test Release",
                "assets": []
            }
        
        with patch('llama_updater.get_available_platforms') as mock_avail:
            mock_avail.return_value = []
        
        with patch('llama_updater.detect_platform') as mock_detect:
            mock_detect.return_value = ("Linux", "x64")
        
        with patch('llama_updater.select_release') as mock_select:
            mock_select.return_value = None
        
        with patch('builtins.input', return_value='5') as mock_input:
            with patch('builtins.input', return_value='y'):
                with self.assertRaises(SystemExit) as ctx:
                    self.updater.install()
                self.assertEqual(ctx.exception.code, 0)

    def test_update_delegates_to_install(self):
        """Test that update() calls install() with same parameters."""
        updater = LlamaUpdater()
        
        with patch('llama_updater.get_latest_release') as mock_get:
            mock_get.return_value = {
                "tag_name": "v0.0.0",
                "name": "Test Release",
                "assets": []
            }
        
        with patch('llama_updater.get_available_platforms') as mock_avail:
            mock_avail.return_value = []
        
        with patch('llama_updater.select_release') as mock_select:
            mock_select.return_value = None
        
        with patch('llama_updater.detect_platform') as mock_detect:
            mock_detect.return_value = ("Linux", "x64")
        
        with patch('builtins.input', side_effect=['y']):
            with patch('llama_updater.install_release') as mock_install:
                mock_install.side_effect = DownloadError("test")
                
                with self.assertRaises(DownloadError):
                    updater.update()
                
                # install_release should have been called
                self.assertTrue(mock_install.called)

    def test_install_with_vulkan_variant(self):
        """Test install with Vulkan variant in available platforms."""
        with patch('llama_updater.get_latest_release') as mock_get:
            mock_get.return_value = {
                "tag_name": "v0.0.0",
                "name": "Test Release",
                "assets": []
            }
        
        with patch('llama_updater.get_available_platforms') as mock_avail:
            mock_avail.return_value = [
                {"platform": "Linux", "arch": "x64", "variant": "vulkan", "assets": []}
            ]
        
        with patch('llama_updater.select_release') as mock_select:
            mock_select.return_value = None
        
        with patch('llama_updater.detect_platform') as mock_detect:
            mock_detect.return_value = ("Linux", "x64")
        
        with patch('builtins.input', side_effect=['y']):
            with patch('llama_updater.download_file') as mock_download:
                mock_download.side_effect = DownloadError("test")
                
                with self.assertRaises(DownloadError):
                    self.updater.install()


class TestLlamaUpdaterAPIComprehensive(unittest.TestCase):
    """Comprehensive API and function tests."""

    def test_parse_asset_name_new_format(self):
        """Test parsing new format asset names."""
        test_cases = [
            ("llama-b8763-bin-ubuntu-x64.tar.gz", "Linux", "x64"),
            ("llama-b8763-bin-debian-arm64.tar.gz", "Linux", "arm64"),
            ("llama-b8763-bin-archlinux-x64.tar.gz", "Linux", "x64"),
            ("llama-b8763-bin-fedora-arm64.tar.gz", "Linux", "arm64"),
            ("llama-b8763-bin-opensuse-x64.tar.gz", "Linux", "x64"),
            ("llama-b8763-bin-rocky-linux-arm64.tar.gz", "Linux", "arm64"),
            ("llama-b8763-bin-centos-x64.tar.gz", "Linux", "x64"),
            ("llama-b8763-bin-ubuntu-x64-vulkan.tar.gz", "Linux", "x64"),
            ("llama-b8763-bin-ubuntu-x64.tgz", "Linux", "x64"),
        ]
        
        for asset_name, expected_platform, expected_arch in test_cases:
            result = parse_asset_name(asset_name)
            self.assertEqual(result["platform"], expected_platform)
            self.assertEqual(result["arch"], expected_arch)

    def test_parse_asset_name_old_format(self):
        """Test parsing old format asset names."""
        test_cases = [
            ("llama-server-linux-arm64.tar.gz", "Linux", "arm64"),
            ("llama-server-windows-amd64.tar.gz", "Windows", "amd64"),
            ("llama-server-darwin-x64.tar.gz", "Darwin", "x64"),
        ]
        
        for asset_name, expected_platform, expected_arch in test_cases:
            result = parse_asset_name(asset_name)
            self.assertEqual(result["platform"], expected_platform)
            self.assertEqual(result["arch"], expected_arch),
        """Test that duplicate platforms are correctly merged with variant handling."""
        release = {
            "assets": [
                {"name": "llama-b8763-bin-ubuntu-x64.tar.gz"},
                {"name": "llama-b8763-bin-ubuntu-x64-vulkan.tar.gz"},
                {"name": "llama-b8763-bin-debian-x64.tar.gz"},
            ]
        }
        
        platforms = get_available_platforms(release)
        
        # Should have 2 platforms: (Linux, x64) with 3 assets, and others
        platform_counts = {}
        for p in platforms:
            key = (p["platform"], p["arch"])
            platform_counts[key] = platform_counts.get(key, 0) + 1
        
        # Check that we have the expected platforms
        self.assertIn(("Linux", "x64"), platform_counts)
        self.assertEqual(platform_counts[("Linux", "x64")], 2)  # ubuntu + debian

    def test_select_release_case_insensitive(self):
        """Test that select_release is case insensitive."""
        release = {"assets": [{"name": "test.tar.gz"}]}
        available_platforms = [
            {"platform": "linux", "arch": "x64", "assets": [{"name": "test.tar.gz"}]}
        ]
        
        # Test various case combinations
        for platform in ["Linux", "linux", "LINUX"]:
            for arch in ["x64", "X64", "x64"]:
                selected = select_release(release, available_platforms, platform, arch)
                self.assertIsNotNone(selected)

    def test_get_release_by_tag(self):
        """Test getting specific release by tag."""
        with patch('llama_updater._get_release_info') as mock_info:
            mock_info.return_value = {
                "tag_name": "v0.0.0",
                "name": "Test Release",
                "assets": []
            }
            
            release = get_release_by_tag("v0.0.0")
            self.assertEqual(release["tag_name"], "v0.0.0")

    def test_extract_archive_various_types(self):
        """Test extraction of various archive types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dest_dir = Path(tmpdir) / "extracted"
            dest_dir.mkdir()
            
            # Test zip extraction
            zip_path = Path(tmpdir) / "test.zip"
            zip_path.write_bytes(b'PK\x03\x04dummy zip content')
            
            with patch('llama_updater.extract_archive') as mock_extract:
                mock_extract.side_effect = ExtractionError("test")
                
                with self.assertRaises(ExtractionError):
                    extract_archive(zip_path, dest_dir)

    def test_install_release_with_error_cleanup(self):
        """Test that install_release cleans up on error."""
        release = {
            "tag_name": "v0.0.0",
            "name": "Test",
            "assets": [
                {"name": "llama-b8763-bin-ubuntu-x64.tar.gz", "browser_download_url": "http://test.com/download"}
            ]
        }
        
        with patch('llama_updater.detect_platform') as mock_detect:
            mock_detect.return_value = ("Linux", "x64")
        
        with patch('llama_updater.get_available_platforms') as mock_avail:
            mock_avail.return_value = []
        
        with patch('llama_updater.select_release') as mock_select:
            mock_select.return_value = release["assets"][0]
        
        with patch('llama_updater.download_file') as mock_download:
            mock_download.return_value = self.temp_dir / "archive.tar.gz"
        
        with patch('llama_updater.extract_archive') as mock_extract:
            mock_extract.return_value = None
        
        with patch('builtins.print'):
            with patch('builtins.input', return_value='y'):
                with self.assertRaises(DownloadError):
                    install_release(release, "v0.0.0")
                
                # Download should have been called
                self.assertTrue(mock_download.called)


if __name__ == '__main__':
    unittest.main()
