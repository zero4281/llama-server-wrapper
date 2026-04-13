# Llama Server Wrapper — Software Requirements Document

**Version:** 1.3  
**Date:** April 2026  
**Repository:** https://github.com/zero4281/llama-server-wrapper

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Structure](#2-project-structure)
3. [Configuration File](#3-configuration-file-configjson)
4. [Start Script](#4-start-script-llama-server-wrapper)
5. [Main Entry Point](#5-main-entry-point-mainpy)
6. [llama.cpp Update/Download Module](#6-llamacpp-updatedownload-module-llama_updaterpy)
7. [Run Script](#7-run-script-runnerpy)
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [Out of Scope](#9-out-of-scope)
10. [Revision History](#revision-history)

---

## 1. Overview

This document defines the requirements for the Llama Server Wrapper project — a set of Python and Bash scripts that automate the download, installation, updating, and execution of `llama-server` from the llama.cpp project. It covers five components: the Bash start script, the Python entry point (`main.py`), the llama.cpp update/download module, the run script, and the shared configuration file.

| Property | Value |
|---|---|
| Repository | https://github.com/zero4281/llama-server-wrapper |
| Primary Language | Python 3.12+ |
| Secondary Language | Bash (start script only) |
| Minimum Python Version | 3.12 |
| Target Platforms | Linux, Windows, macOS (auto-detected at runtime) |
| llama.cpp Source | https://github.com/ggml-org/llama.cpp/releases |

---

## 2. Project Structure

```
llama-server-wrapper/
├── llama-server-wrapper   # Bash start script
├── main.py                # Entry point
├── llama_updater.py       # llama.cpp download/update module
├── runner.py              # Run script
├── requirements.txt       # Python dependencies
├── config.json            # Runtime configuration (auto-generated if missing)
├── .venv/                 # Python virtual environment (created by user)
│   └── bin/activate
├── llama-cpp/             # Extracted llama.cpp release binaries
│   └── llama-server       # (llama-server.exe on Windows)
└── llama-server.log       # llama-server output log (when enabled)
```

---

## 3. Configuration File (config.json)

`config.json` lives in the same directory as `main.py`. If the file does not exist when `main.py` is launched, a default `config.json` must be auto-generated before any other operations proceed.

The file has two top-level sections:

### 3.1 `options` — wrapper settings

Top-level `options` keys control the wrapper itself. The `llama-server.options` key-value pairs are passed as command-line arguments to `llama-server`. Example:

```json
{
  "options": {
    "logfile": "./llama-server-wrapper.log"
  },
  "llama-server": {
    "options": {
      "host": "0.0.0.0",
      "port": "11235",
      "models-max": "1",
      "log-file": "llama-server.log"
    }
  }
}
```

### 3.2 `logging` — wrapper logging settings

Controls verbosity and destination of the wrapper's own log output (separate from llama-server output).

| Key | Type | Default | Description |
|---|---|---|---|
| `enabled` | boolean | `true` | Whether wrapper logging is active |
| `level` | string | `"INFO"` | One of `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `file` | string\|null | `null` | Path to wrapper log file, or `null` to log to stdout only |

> **Note:** The llama-server output log is controlled separately via the `log-file` key in `config.json`'s `llama-server.options` section, or overridden at runtime via the `--log-file` CLI flag (see Section 7).

---

## 4. Start Script (llama-server-wrapper)

### 4.1 Language & purpose

- Written in Bash.
- Activates the Python virtual environment, then invokes `main.py` with all arguments forwarded.

### 4.2 Behaviour

- Before launching `main.py`, check whether `.venv/bin/activate` exists in the project directory.
  - If it **does not exist**, print a message prompting the user to create the virtual environment and exit without launching `main.py`:
    ```
    Virtual environment not found. Please create it first:
      python3 -m venv .venv
      source .venv/bin/activate
      pip install -r requirements.txt
    ```
  - If it **exists**, activate it with:
    ```bash
    source .venv/bin/activate
    ```
- After activation, call `main.py` using the Python interpreter, passing through all command-line arguments unchanged:
  ```bash
  python3 main.py "$@"
  ```
- Must be executable (`chmod +x`).

---

## 5. Main Entry Point (main.py)

### 5.1 Language & structure

- Written in Python 3.12+.
- All logic must be encapsulated in a class within an appropriate namespace (e.g. `llama_wrapper.Main`).
- The `if __name__ == '__main__'` block must only instantiate the class and call its `run` method.

### 5.2 Command-line arguments

| Argument | Type | Description |
|---|---|---|
| `--self-update` | Flag | Update the wrapper's own scripts from the project GitHub repository. Prompts the user to choose between the latest release, a previous release, or the repository `main` branch HEAD before proceeding. |
| `--install-llama` | Flag | Download and install the newest release of llama.cpp. Delegates to `LlamaUpdater` in `llama_updater.py`. |
| `--update-llama` | Flag | Update an existing llama.cpp installation to the latest release. Delegates to `LlamaUpdater`. |
| `--stop-server` | Flag | Signal `runner.py` to gracefully stop a running `llama-server` process. |
| `--log-file` | String | Path for llama-server output log. Overrides the `log-file` value in `config.json`. Defaults to `llama-server.log` in the project folder if not set in either place. |
| `<llama args>` | Pass-through | Any other arguments are collected and forwarded verbatim to `llama-server` via `runner.py`. |

### 5.3 Self-update behaviour (`--self-update`)

#### 5.3.1 Source selection

Before downloading anything, present the user with a numbered menu to choose the update source:

```
Select update source:
  1) Latest release (recommended)
  2) Previous release
  3) Repository HEAD (main branch)
Choice [1]:
```

- Pressing Enter without input selects the default (option 1, latest release).
- Selecting **option 2** fetches the list of available releases from the GitHub Releases API (same endpoints as Section 6.2, with `owner = zero4281`, `repo = llama-server-wrapper`) and presents a numbered list for the user to choose from.
- Selecting **option 3** downloads the current `main` branch HEAD as a ZIP archive from:
  ```
  https://github.com/zero4281/llama-server-wrapper/archive/refs/heads/main.zip
  ```

#### 5.3.2 Confirmation prompt

After the user selects a source, display the resolved version or commit reference and prompt for confirmation before modifying any local files:

```
Selected: v1.2.0 (llama-server-wrapper-v1.2.0.zip)
Proceed with update? [Y/n]:
```

For a HEAD update the label should reflect the branch rather than a release tag, e.g.:

```
Selected: main branch HEAD
Proceed with update? [Y/n]:
```

Pressing Enter confirms (default yes). Entering `n` cancels and exits with status code `0` without modifying any files.

#### 5.3.3 Update execution

- Download the selected archive or branch ZIP to a temporary location.
- Replace local project files with the downloaded versions.
- After a successful update, restart `main.py` with the same arguments that were originally passed.
- If the download or file replacement fails, print an error message and exit with a non-zero status code. Local files must not be left in a partially modified state; restore originals if replacement has already begun.

### 5.4 Startup sequence

1. Parse CLI arguments.
2. Check for `config.json`; auto-generate a default if missing.
3. If `--self-update`: perform update and restart; all other arguments are ignored.
4. If `--install-llama` or `--update-llama`: instantiate `LlamaUpdater` and call the appropriate method; exit on completion.
5. If `--stop-server`: signal `runner.py` to stop `llama-server`; exit on completion.
6. Otherwise: check whether the `./llama-cpp` directory exists.
   - If it **does not exist**, print a message prompting the user to install llama.cpp and exit with a non-zero status code:
     ```
     llama-cpp not found. Please install it first:
       llama-server-wrapper --install-llama
     ```
   - If it **exists**, load `config.json`, merge pass-through args, and invoke `Runner`.

---

## 6. llama.cpp Update/Download Module (llama_updater.py)

### 6.1 Language & structure

- Written in Python 3.12+.
- All logic must be encapsulated in a class (e.g. `llama_wrapper.updater.LlamaUpdater`).
- Never executed directly; always instantiated by `main.py`.

### 6.2 GitHub API usage

Release discovery must use the GitHub REST API (API version `2022-11-28`). Full reference:
https://docs.github.com/en/enterprise-server@3.17/rest/releases/releases?apiVersion=2022-11-28

All requests must include the following headers:

```
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
```

The following endpoints are used:

| Purpose | Method | Endpoint |
|---|---|---|
| Get the latest release | `GET` | `/repos/{owner}/{repo}/releases/latest` |
| List all releases (for version selection) | `GET` | `/repos/{owner}/{repo}/releases` |
| Get a specific release by tag | `GET` | `/repos/{owner}/{repo}/releases/tags/{tag}` |

For llama.cpp these map to `owner = ggml-org` and `repo = llama.cpp`. Example:

```
GET https://api.github.com/repos/ggml-org/llama.cpp/releases/latest
```

The `assets` array in each release response contains the downloadable files. Each asset includes a `browser_download_url`, `name`, and `size` field used for platform selection and download.

> **Note:** The GitHub API applies rate limits to unauthenticated requests (60 requests/hour). The module must handle `403` / `429` rate-limit responses gracefully, inform the user, and include the `X-RateLimit-Reset` time from the response headers where available.

### 6.3 Release selection

#### 6.3.1 Tag selection prompt

Present a numbered menu of release tags fetched from the GitHub Releases API. Option `0` allows the user to type a tag manually; options `1`–`5` are the five most recent release tags. Pressing Enter without a selection installs the most recent release (option `1`). Example:

```
Select a llama.cpp release to install:
  0) Enter a tag manually
  1) b8800 (latest)
  2) b8790
  3) b8780
  4) b8770
  5) b8760
Choice [1]:
```

If the user selects option `0`, prompt for the tag string:

```
Enter release tag: 
```

#### 6.3.2 Asset (zip file) selection prompt

After a release tag is resolved, fetch its asset list from the GitHub API and present all available zip files as a numbered list. Auto-detect the current platform and architecture using Python's `platform` module and highlight the recommended asset. The recommended option is also the default if the user presses Enter without a selection. Example:

```
Select a zip file to install:
  1) llama-b8800-bin-ubuntu-x64.zip  ← recommended
  2) llama-b8800-bin-win-avx2-x64.zip
  3) llama-b8800-bin-macos-arm64.zip
  4) llama-b8800-bin-macos-x64.zip
  ...
Choice [1]:
```

If auto-detection fails (platform or architecture cannot be determined), no option is highlighted and no default is pre-selected; the user must choose explicitly.

#### 6.3.3 Confirmation prompt

After the user selects a release tag and asset, display both and prompt for confirmation before downloading anything:

```
Selected release: b8800 (llama-b8800-bin-ubuntu-x64.zip)
Proceed with installation? [Y/n]:
```

Pressing Enter confirms (default yes). Entering `n` cancels and exits with status code `0` without modifying any files.

### 6.4 Platform & architecture detection

- Auto-detect the current platform (Linux, Windows, macOS) and architecture (`x86_64`, `arm64`, etc.) using Python's `platform` module.
- Use the detected platform/architecture to determine and highlight the recommended asset in the selection list (see Section 6.3.2).
- If detection fails, display all assets without a highlighted recommendation and require the user to select explicitly.

### 6.5 Download & extraction

- Download the selected release archive (`.zip` or `.tar.gz`) using the asset's `browser_download_url`.
- Display a progress bar or spinner during the download so the user can track progress.
- **Checksum verification:** After the download completes, check whether the release provides a checksum file (e.g. `sha256sum.txt` or a similarly named asset). If one is present, download it and verify the archive before proceeding. If verification fails, delete the downloaded archive, print a clear error message, and exit with a non-zero status code.
- If no checksum asset is available for the release, skip verification and proceed directly to extraction.
- Decompress and extract the full archive contents — all binaries and supporting files — into the `./llama-cpp/` folder in the **same directory as the script**.
- If a `./llama-cpp/` folder already exists, delete it entirely before extraction without prompting or creating a backup.
- Ensure `llama-server` (or `llama-server.exe` on Windows) is executable after extraction.
- Remove the downloaded archive file after successful extraction.
- After a successful install, print a success message and run a quick sanity check by executing `llama-server --version` and displaying its output. If the sanity check fails, print a warning but still exit with status code `0` (the binaries were installed; the version check is informational).

### 6.6 Error handling

- Handle `403` and `429` responses from the GitHub API as rate-limit errors; print a clear message including the `X-RateLimit-Reset` time if present in the response headers.
- If the GitHub API is otherwise unreachable, print a clear error and exit with a non-zero status.
- If the download fails or the archive is corrupt, clean up any partial files and report the error.

---

## 7. Run Script (runner.py)

### 7.1 Language & structure

- Written in Python 3.12+.
- All logic must be encapsulated in a class (e.g. `llama_wrapper.runner.Runner`).
- Never executed directly; always instantiated by `main.py`.

### 7.2 Configuration loading

- Read `config.json` from the project directory.
- Extract key-value pairs from the `llama-server.options` section and convert them to CLI arguments for `llama-server`.
- Merge any pass-through arguments received from `main.py`, with CLI arguments taking precedence over `config.json` values on conflict.

### 7.3 Process execution

- Launch `./llama-cpp/llama-server` (`./llama-cpp/llama-server.exe` on Windows) with the assembled argument list.
- Record the PID of the launched `llama-server` process.

### 7.4 Daemon mode

- Write the PID to `llama-server.pid` in the project directory.
- `main.py` returns control to the shell immediately after launch.

### 7.5 Logging (llama-server output)

The log file path is resolved in the following order of precedence:

1. `--log-file` CLI argument
2. `llama-server.options.log-file` in `config.json`
3. Default: `llama-server.log` in the project folder

The resolved path is passed to `llama-server` via its `--log-file` flag.

### 7.6 Graceful shutdown

Shutdown is triggered by either a `SIGINT` / `KeyboardInterrupt` (Ctrl+C) or the `--stop-server` argument passed to `main.py`.

1. Send `SIGTERM` (or the platform equivalent) to the `llama-server` process.
2. Wait up to **60 seconds** for the process to exit cleanly.
3. If the process has not exited after 60 seconds, send `SIGKILL` (`TerminateProcess` on Windows) to forcibly terminate it.
4. Remove the PID file after the process has been stopped.
5. Exit the wrapper with status code `0` on clean shutdown, non-zero if a force-kill was required.

---

## 8. Non-Functional Requirements

### 8.1 Cross-platform compatibility

- All Python code must run on Linux, Windows 10+, and macOS without modification.
- Path handling must use `pathlib.Path` throughout to avoid OS-specific separator issues.
- Signal handling must use platform-appropriate mechanisms (`SIGTERM`/`SIGKILL` on POSIX; `TerminateProcess` on Windows).

### 8.2 Dependencies

- Standard library only where possible.
- The `requests` library (or `urllib`) may be used for GitHub API calls and file downloads.
- No third-party dependency should be required for core start/stop/run operations.

### 8.3 Error handling & exit codes

- All external calls (GitHub API, subprocess launches, file I/O) must be wrapped in `try/except` blocks.
- Errors must be logged (according to the logging config) and result in a non-zero exit code.
- The wrapper must never silently swallow exceptions.

### 8.4 Code style

- Follow PEP 8 conventions.
- Each module must include a module-level docstring describing its purpose.
- Each class and public method must include a docstring.

---

## 9. Out of Scope

- Model file management (downloading, converting, or organising GGUF model files).
- A graphical user interface.
- Authentication or access control for `llama-server`.
- Automatic selection of quantisation level or GPU layers.

---

## Revision History

| Version | Date | Author | Notes |
|---|---|---|---|
| 1.3 | April 2026 | zero4281 | Removed `--foreground` command-line option |
| 1.2 | April 2026 | zero4281 | Expanded Section 6 install workflow: interactive release tag + asset selection with auto-detected recommendation, all-assets display, checksum verification, download progress bar, delete-and-replace of existing llama-cpp folder, post-install success message and sanity check |
| 1.1 | April 2026 | zero4281 | Added user confirmation and source selection for `--self-update`; added user confirmation prompt to llama.cpp install/update |
| 1.0 | April 2026 | zero4281 | Initial draft |