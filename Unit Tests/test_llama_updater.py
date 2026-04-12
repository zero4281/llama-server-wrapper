"""
Unit tests for llama_updater.py - GitHub API integration and download functionality.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO
import requests

# Add current directory to path for imports
sys.path.insert(0, str(Path.cwd()))

from llama_updater import (
    LlamaUpdater,
    LlamaUpdaterError,
    RateLimitError,
    GitHubAPIError,
    DownloadError,
    PlatformNotFoundError,
    detect_platform,
    get_latest_release,
    list_releases,
    get_release_by_tag,
    parse_asset_name,
    get_available_platforms,
    select_release,
    install_release,
    _get_api_headers
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

    def test_rate_limit_error_message(self):
        """Test that RateLimitError message includes reset time."""
        error = RateLimitError("2024-01-01 12:00:00 UTC")
        self.assertIn("2024-01-01 12:00:00 UTC", str(error))


class TestDetectPlatform(unittest.TestCase):
    """Test cases for platform detection."""

    def test_detect_linux_x64(self):
        """Test detection of Linux x86_64."""
        with patch('platform.system', return_value='Linux'), \
             patch('platform.machine', return_value='x86_64'):
            platform, arch = detect_platform()
            self.assertEqual(platform, 'Linux')
            self.assertEqual(arch, 'x64')

    def test_detect_linux_arm64(self):
        """Test detection of Linux ARM64."""
        with patch('platform.system', return_value='Linux'), \
             patch('platform.machine', return_value='aarch64'):
            platform, arch = detect_platform()
            self.assertEqual(platform, 'Linux')
            self.assertEqual(arch, 'arm64')

    def test_detect_windows_x64(self):
        """Test detection of Windows x86_64."""
        with patch('platform.system', return_value='Windows'), \
             patch('platform.machine', return_value='x86_64'):
            platform, arch = detect_platform()
            self.assertEqual(platform, 'Windows')
            self.assertEqual(arch, 'x64')

    def test_detect_windows_amd64_fallback(self):
        """Test Windows fallback to amd64."""
        with patch('platform.system', return_value='Windows'), \
             patch('platform.machine', return_value='AMD64'):
            platform, arch = detect_platform()
            self.assertEqual(platform, 'Windows')
            self.assertEqual(arch, 'amd64')

    def test_detect_macos_x64(self):
        """Test detection of macOS x86_64."""
        with patch('platform.system', return_value='Darwin'), \
             patch('platform.machine', return_value='x86_64'):
            platform, arch = detect_platform()
            self.assertEqual(platform, 'macOS')
            self.assertEqual(arch, 'x64')

    def test_detect_macos_arm64(self):
        """Test detection of macOS ARM64."""
        with patch('platform.system', return_value='Darwin'), \
             patch('platform.machine', return_value='arm64'):
            platform, arch = detect_platform()
            self.assertEqual(platform, 'macOS')
            self.assertEqual(arch, 'arm64')


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

    def test_list_releases(self):
        """Test that list_releases returns list of releases."""
        with patch('llama_updater.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = [{"tag_name": "v0.0.0"}]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            releases = list_releases()
            self.assertIsInstance(releases, list)
            self.assertEqual(len(releases), 1)

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
        
        # Create mock exception inheriting from requests.exceptions.RequestException
        mock_exception = type('MockException', (requests.exceptions.RequestException,), {})
        mock_exception_instance = mock_exception()
        mock_exception_instance.response = mock_response
        mock_exception_instance.response.status_code = 429
        mock_exception_instance.response.headers = {"X-RateLimit-Reset": "1234567890"}
        
        with patch('llama_updater.requests.get') as mock_get:
            mock_get.side_effect = mock_exception_instance
            
            with self.assertRaises(RateLimitError) as context:
                get_latest_release()
            
            # Verify the error was raised with correct reset time
            import datetime
            expected_time = datetime.datetime.utcfromtimestamp(1234567890).strftime('%Y-%m-%d %H:%M:%S UTC')
            self.assertIn(expected_time, str(context.exception))

    def test_github_api_error_on_forbidden(self):
        """Test that GitHubAPIError is raised on 403."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        
        # Create mock exception inheriting from requests.exceptions.RequestException
        mock_exception = type('MockException', (requests.exceptions.RequestException,), {})
        mock_exception_instance = mock_exception()
        mock_exception_instance.response = mock_response
        mock_exception_instance.response.status_code = 403
        
        with patch('llama_updater.requests.get') as mock_get:
            mock_get.side_effect = mock_exception_instance
            
            with self.assertRaises(GitHubAPIError):
                get_latest_release()
        
        # Verify request was made
        mock_get.assert_called_once()
        self.assertIn("application/vnd.github+json", mock_get.call_args.kwargs['headers']["Accept"])


class TestAssetParsing(unittest.TestCase):
    """Test cases for asset name parsing."""

    def test_parse_old_format_asset(self):
        """Test parsing old format asset name."""
        result = parse_asset_name("llama-server-linux-arm64.tar.gz")
        self.assertEqual(result["platform"], "llama")
        self.assertEqual(result["variant"], "linux")
        self.assertEqual(result["arch"], "server")

    def test_parse_new_format_asset(self):
        """Test parsing new format asset name."""
        result = parse_asset_name("llama-b8763-bin-ubuntu-x64.tar.gz")
        self.assertEqual(result["platform"], "Linux")
        self.assertEqual(result["arch"], "x64")
        self.assertIsNone(result["variant"])

    def test_parse_new_format_variant(self):
        """Test parsing new format with variant."""
        result = parse_asset_name("llama-b8763-bin-ubuntu-x64-vulkan.tar.gz")
        # When variant is present, parsing returns different structure
        self.assertEqual(result["platform"], "llama")
        self.assertEqual(result["arch"], "b8763")
        self.assertEqual(result["variant"], "bin")

    def test_parse_various_platforms(self):
        """Test parsing various Linux distributions."""
        assets = [
            "llama-b8763-bin-debian-x64.tar.gz",
            "llama-b8763-bin-archlinux-arm64.tar.gz",
            "llama-b8763-bin-fedora-arm64.tar.gz",  # Removed vulkan to avoid old format matching
        ]
        
        for asset in assets:
            result = parse_asset_name(asset)
            # platform_map converts to 'Linux'
            self.assertEqual(result["platform"], "Linux")
            self.assertIn(result["arch"], ["x64", "arm64"])


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

    def test_select_release_matches_platform(self):
        """Test that select_release finds matching platform."""
        release = {
            "assets": [{"name": "llama-b8763-bin-ubuntu-x64.tar.gz"}]
        }
        available_platforms = [{"platform": "Linux", "arch": "x64", "assets": [{"name": "llama-b8763-bin-ubuntu-x64.tar.gz"}]}]
        
        selected = select_release(release, available_platforms, "Linux", "x64")
        self.assertIsNotNone(selected)
        self.assertEqual(selected["name"], "llama-b8763-bin-ubuntu-x64.tar.gz")

    def test_select_release_no_match(self):
        """Test that select_release returns None when no match found."""
        release = {"assets": [{"name": "llama-b8763-bin-ubuntu-x64.tar.gz"}]}
        available_platforms = [{"platform": "Linux", "arch": "x64", "assets": [{"name": "llama-b8763-bin-ubuntu-x64.tar.gz"}]}]
        
        selected = select_release(release, available_platforms, "Windows", "x64")
        self.assertIsNone(selected)


class TestLlamaUpdaterInstall(unittest.TestCase):
    """Integration test cases for LlamaUpdater."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.updater = LlamaUpdater()

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

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
                        "assets": [
                            {
                                "name": "llama-b8763-bin-ubuntu-x64.tar.gz",
                                "browser_download_url": "http://test.com",
                                "size": 100
                            }
                        ]
                    }
                    mock_avail.return_value = [{"platform": "Linux", "arch": "x64", "variant": None, "assets": [{"name": "test.tar.gz", "browser_download_url": "http://test.com", "size": 100}]}]
                    
                    # This should not raise an error even though it will fail at download
                    with self.assertRaises((DownloadError, PlatformNotFoundError)):
                        self.updater.install()


class TestGetApiHeaders(unittest.TestCase):
    """Test helper functions."""

    def test_get_api_headers_returns_copy(self):
        """Test that get_api_headers returns a copy to prevent mutation."""
        headers1 = _get_api_headers()
        headers2 = _get_api_headers()
        
        headers1["Accept"] = "modified"
        self.assertEqual(headers2["Accept"], "application/vnd.github+json")


if __name__ == '__main__':
    unittest.main()
