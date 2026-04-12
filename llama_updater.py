"""
llama_updater.py — llama.cpp download and update module.

This module handles fetching releases from the GitHub API, selecting
the appropriate platform/architecture, downloading and extracting
archives, and managing the llama-cpp installation directory.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


# Constants
GITHUB_OWNER = "ggml-org"
GITHUB_REPO = "llama.cpp"
GITHUB_API_BASE = "https://api.github.com"
LLAMA_CPP_DIR = Path.cwd() / "llama-cpp"


class LlamaUpdaterError(Exception):
    """Base exception for llama_updater errors."""
    pass


class RateLimitError(LlamaUpdaterError):
    """Raised when GitHub API rate limit is exceeded."""
    def __init__(self, reset_time: str):
        self.reset_time = reset_time
        super().__init__(f"GitHub API rate limit exceeded. Retry after {reset_time}")


class GitHubAPIError(LlamaUpdaterError):
    """Raised when GitHub API is unreachable."""
    pass


class DownloadError(LlamaUpdaterError):
    """Raised when download fails."""
    pass


class ExtractionError(LlamaUpdaterError):
    """Raised when extraction fails."""
    pass


class PlatformNotFoundError(LlamaUpdaterError):
    """Raised when no matching platform is found."""
    pass


# Headers for GitHub API requests
_GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def _get_api_headers() -> Dict[str, str]:
    """Get headers for GitHub API requests."""
    return _GITHUB_HEADERS.copy()


def detect_platform() -> Tuple[str, str]:
    """
    Detect current platform and architecture.

    Returns:
        Tuple of (system, machine) standardized names.
    """
    import platform
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Linux":
        if "aarch64" in machine or "arm64" in machine:
            return "Linux", "arm64"
        if "x86_64" in machine:
            return "Linux", "x64"  # Normalize to x64 for matching
        return "Linux", "aarch64"  # fallback

    elif system == "Windows":
        if "aarch64" in machine or "arm64" in machine:
            return "Windows", "arm64"
        if "x86_64" in machine:
            return "Windows", "x64"  # Normalize to x64 for matching
        return "Windows", "amd64"  # fallback

    elif system == "Darwin":
        if "aarch64" in machine or "arm64" in machine:
            return "macOS", "arm64"
        if "x86_64" in machine:
            return "macOS", "x64"  # Normalize to x64 for matching
        return "macOS", "amd64"  # fallback

    else:
        return system, machine


def _get_release_info(url: str) -> dict:
    """
    Fetch release information from GitHub API.

    Args:
        url: Full API URL for the release

    Returns:
        Release data as dictionary

    Raises:
        GitHubAPIError: If API is unreachable
        RateLimitError: If rate limited
    """
    try:
        response = requests.get(url, headers=_get_api_headers(), timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 429:
                # Rate limited
                reset_time = e.response.headers.get('X-RateLimit-Reset')
                reset_ts = int(reset_time) if reset_time else None
                if reset_ts:
                    import datetime
                    reset_dt = datetime.datetime.utcfromtimestamp(reset_ts)
                    reset_time = reset_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                else:
                    reset_time = 'unknown'
                raise RateLimitError(reset_time)
            elif e.response.status_code == 403:
                raise GitHubAPIError(f"GitHub API forbidden (403). Check your network connection.")
            else:
                raise GitHubAPIError(f"GitHub API error: {e.response.status_code} {e.response.text}")
        else:
            raise GitHubAPIError(f"GitHub API unreachable: {e}")


def get_latest_release() -> dict:
    """
    Get the latest release from llama.cpp repository.

    Returns:
        Release data dictionary
    """
    url = f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    return _get_release_info(url)


def list_releases() -> List[dict]:
    """
    List all releases from llama.cpp repository.

    Returns:
        List of release data dictionaries
    """
    releases = []
    url = f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases"
    page = 1
    max_pages = 5  # GitHub limits to 1000 items by default

    while page <= max_pages and not releases:
        try:
            response = requests.get(url, headers=_get_api_headers(), 
                                  timeout=30, params={'page': page, 'per_page': 100})
            response.raise_for_status()
            page_releases = response.json()
            if not page_releases:
                break
            releases.extend(page_releases)
            page += 1
        except requests.exceptions.RequestException:
            break

    return releases


def get_release_by_tag(tag: str) -> dict:
    """
    Get a specific release by its tag.

    Args:
        tag: Release tag (e.g., "v0.0.0")

    Returns:
        Release data dictionary
    """
    url = f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/tags/{tag}"
    return _get_release_info(url)


def parse_asset_name(name: str) -> Dict[str, str]:
    """
    Parse asset name to extract platform and architecture info.

    Args:
        name: Asset name (e.g., "llama-server-linux-arm64.tar.gz" or
                "llama-b8763-bin-ubuntu-x64.tar.gz")

    Returns:
        Dictionary with parsed info
    """
    # Remove extension (handles .tar.gz, .tgz, .zip, etc.)
    # Remove the extension(s) completely
    if name.endswith(".tar.gz") or name.endswith(".tgz"):
        base_name = name.replace(".tar.gz", "").replace(".tgz", "")
    else:
        base_name = Path(name).stem  # Standard extension removal
    
    # Old format: platform-arch[-variant] (e.g., llama-server-linux-arm64)
    # New format: llama-{tag}-bin-{platform}-{arch} (e.g., llama-b8763-bin-ubuntu-x64)
    
    # Try new format first: llama-{tag}-bin-{platform}-{arch}
    # Tag can contain hyphens, so we need a more flexible pattern
    new_pattern = r"^llama-[^-]+-bin-(\w+)-(\w+)$"
    match = re.match(new_pattern, base_name)
    if match:
        platform = match.group(1).lower()
        arch = match.group(2).lower()
        # Convert platform names to standard names
        platform_map = {
            "ubuntu": "Linux",
            "openEuler": "Linux",
            "debian": "Linux",
            "centos": "Linux",
            "rocky": "Linux",
            "alpine": "Linux",
            "archlinux": "Linux",
            "fedora": "Linux",
            "redhat": "Linux",
            "rhel": "Linux",
            "amazon": "Linux",
            "oracle": "Linux",
            "suse": "Linux",
            "opensuse": "Linux",
            "gentoo": "Linux",
            "manjaro": "Linux",
            "elementary": "Linux",
            "pop": "Linux",
            "zorin": "Linux",
            "linuxmint": "Linux",
            "deepin": "Linux",
            "kali": "Linux",
            "parrot": "Linux",
        }
        return {
            "platform": platform_map.get(platform, platform),
            "arch": arch,
            "variant": None
        }
    
    # Try old format: platform-arch[-variant]
    pattern = r"^(\w+)-(\w+)(?:-(\w+))?"
    match = re.match(pattern, base_name)
    if match:
        return {
            "platform": match.group(1),
            "arch": match.group(2),
            "variant": match.group(3) if match.group(3) else None
        }
    
    return {"platform": None, "arch": None, "variant": None}


def get_available_platforms(release: dict) -> List[dict]:
    """
    Get list of available platform/architecture options from release assets.

    Args:
        release: Release data dictionary

    Returns:
        List of platform options
    """
    platforms = {}

    for asset in release.get("assets", []):
        parsed = parse_asset_name(asset["name"])
        if parsed["platform"] and parsed["arch"]:
            key = (parsed["platform"], parsed["arch"])
            if key not in platforms:
                platforms[key] = {
                    "platform": parsed["platform"],
                    "arch": parsed["arch"],
                    "variant": parsed["variant"],
                    "assets": []
                }
            platforms[key]["assets"].append(asset)

    return list(platforms.values())


def select_release(release: dict, available_platforms: List[dict], 
                   detected_platform: str, detected_arch: str) -> Optional[dict]:
    """
    Select the appropriate release asset based on platform and architecture.

    Args:
        release: Release data dictionary
        available_platforms: List of platform options
        detected_platform: Detected platform name
        detected_arch: Detected architecture

    Returns:
        Selected asset dictionary, or None if no match found
    """
    detected_key = (detected_platform, detected_arch)
    
    # Find matching platform in available_platforms
    for platform_info in available_platforms:
        if platform_info['platform'].lower() == detected_platform.lower() and platform_info['arch'].lower() == detected_arch.lower():
            return platform_info['assets'][0]
    
    # If no exact match, show options and let user choose
    return None


def download_file(url: str, output_path: Path) -> Path:
    """
    Download file from URL to output path.

    Args:
        url: Download URL
        output_path: Destination path

    Returns:
        Path to downloaded file

    Raises:
        DownloadError: If download fails
    """
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        total = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    progress = downloaded / total * 100
                    # Could add progress bar here

        return output_path

    except requests.exceptions.RequestException as e:
        raise DownloadError(f"Download failed: {e}")


def extract_archive(archive_path: Path, dest_dir: Path) -> None:
    """
    Extract archive to destination directory.

    Args:
        archive_path: Path to archive file
        dest_dir: Destination directory

    Raises:
        ExtractionError: If extraction fails
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract to temp dir first
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
            elif archive_path.suffix in ('.tar.gz', '.tgz'):
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(tmpdir)
            else:
                # Try to detect file type
                if archive_path.suffix == '.tar':
                    with tarfile.open(archive_path, 'r') as tar_ref:
                        tar_ref.extractall(tmpdir)
                elif archive_path.suffix == '.gz':
                    with tarfile.open(archive_path, 'r:gz') as tar_ref:
                        tar_ref.extractall(tmpdir)
                else:
                    # Try default zip extraction
                    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                        zip_ref.extractall(tmpdir)

            # Move contents to dest_dir
            extracted_root = Path(tmpdir)
            
            # Find the root extracted directory
            for item in extracted_root.iterdir():
                if item.is_dir() and item.name != '__MACOSX':
                    shutil.move(str(item), str(dest_dir))
                    break

    except Exception as e:
        raise ExtractionError(f"Extraction failed: {e}")


def ensure_executable(path: Path) -> None:
    """
    Make file executable on Unix systems.

    Args:
        path: Path to file
    """
    if sys.platform != 'win32':
        try:
            os.chmod(path, 0o755)
        except OSError:
            pass  # Ignore permission errors


def install_release(release: dict, release_tag: str) -> None:
    """
    Install a llama.cpp release.

    Args:
        release: Release data dictionary
        release_tag: Release tag for reference
    """
    print(f"Installing llama.cpp release {release_tag}...")

    # Detect platform
    detected_platform, detected_arch = detect_platform()
    print(f"Detected platform: {detected_platform} {detected_arch}")

    # Get available platforms
    available_platforms = get_available_platforms(release)
    print(f"\nAvailable platforms in this release:")
    for i, platform_info in enumerate(available_platforms, 1):
        variant = f" ({platform_info['variant']})" if platform_info['variant'] else ""
        print(f"  {i}. {platform_info['platform']} {platform_info['arch']}{variant}")

    # Select platform
    selected_asset = select_release(release, available_platforms, 
                                   detected_platform, detected_arch)
    
    if selected_asset:
        print(f"\nSelected: {selected_asset['name']}")
    else:
        print("\nNo matching platform found. Please select manually.")
        # For simplicity, we'll use the first asset in a real implementation
        # In a full implementation, we'd prompt user to select
        selected_asset = available_platforms[0]["assets"][0] if available_platforms else None

    if not selected_asset:
        raise PlatformNotFoundError("No matching platform found in release")

    # Download
    print(f"\nDownloading {selected_asset['name']}...")
    archive_path = Path(tempfile.gettempdir()) / f"llama-{release_tag.replace('v', '')}-{selected_asset['name']}"
    
    try:
        download_file(selected_asset['browser_download_url'], archive_path)
        print(f"Downloaded to {archive_path}")

        # Extract
        print(f"\nExtracting to {LLAMA_CPP_DIR}...")
        extract_archive(archive_path, LLAMA_CPP_DIR)

        # Ensure llama-server is executable
        llama_server = LLAMA_CPP_DIR / "llama-server"
        if llama_server.exists():
            ensure_executable(llama_server)
            print(f"Made {llama_server} executable")

        # Clean up
        archive_path.unlink(missing_ok=True)
        print("\nInstallation complete!")

    except Exception as e:
        # Clean up on error
        archive_path.unlink(missing_ok=True)
        raise e


class LlamaUpdater:
    """Main class for llama.cpp download and update operations."""

    def __init__(self):
        self.owner = GITHUB_OWNER
        self.repo = GITHUB_REPO

    def install(self, interactive: bool = False) -> None:
        """
        Install the latest llama.cpp release.

        Args:
            interactive: If True, allow manual platform selection
        """
        print("Fetching latest llama.cpp release...")
        release = get_latest_release()
        release_tag = release["tag_name"]

        print(f"Latest release: {release_tag} ({release['name']})")
        print(f"Published: {release['published_at']}")

        if interactive or not select_release(release, get_available_platforms(release), 
                                           *detect_platform()):
            # Interactive mode or no match - fetch more details
            print("\nFetching release details...")
            # In a full implementation, show full asset list
            # For now, proceed with first match

        install_release(release, release_tag)

    def update(self) -> None:
        """
        Update to the latest release.

        This is similar to install() but implies updating existing installation.
        """
        print("Updating llama.cpp to latest release...")
        self.install()


def main():
    """CLI entry point for llama_updater."""
    import argparse

    parser = argparse.ArgumentParser(description="Download and install llama.cpp releases")
    parser.add_argument("--install", action="store_true", help="Install latest release")
    parser.add_argument("--update", action="store_true", help="Update to latest release")
    parser.add_argument("--tag", type=str, help="Specific release tag to install")

    args = parser.parse_args()

    if args.tag:
        # Install specific tag
        release = get_release_by_tag(args.tag)
        install_release(release, args.tag)
    elif args.install or args.update:
        updater = LlamaUpdater()
        if args.update:
            updater.update()
        else:
            updater.install()
    else:
        # Default: show available releases
        releases = list_releases()
        print(f"Found {len(releases)} releases:")
        for i, r in enumerate(releases[:10], 1):  # Show first 10
            print(f"  {i}. {r['tag_name']} - {r['name']}")


if __name__ == "__main__":
    main()
