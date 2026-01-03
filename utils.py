import subprocess
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import yaml

# Define project root relative to this file
PROJECT_ROOT = Path(__file__).parent.absolute()

# ========================================
# UTILITIES
# ========================================

def log(message: str) -> None:
    """Print an info message with blue color."""
    print(f"\033[1;34m[INFO]\033[0m {message}")


def success(message: str) -> None:
    """Print a success message with green color."""
    print(f"\033[1;32m[DONE]\033[0m {message}")


def warn(message: str) -> None:
    """Print a warning message with yellow color."""
    print(f"\033[1;33m[WARN]\033[0m {message}")


def error_exit(message: str) -> None:
    """Print an error message with red color and exit."""
    print(f"\033[1;31m[ERROR]\033[0m {message}")
    raise SystemExit(1)


def run_command(cmd: List[str], check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            error_exit(f"Command failed: {' '.join(cmd)}\n{e.stderr}")
        return e


def is_cask_installed(cask_name: str) -> bool:
    """Check if a Homebrew cask is already installed."""
    result = run_command(["brew", "list", "--cask", cask_name], check=False, capture=True)
    return result.returncode == 0


def is_formula_installed(formula_name: str) -> bool:
    """Check if a Homebrew formula is already installed."""
    result = run_command(["brew", "list", "--formula", formula_name], check=False, capture=True)
    return result.returncode == 0


def load_applications_config(config_path: Path) -> Dict[str, List[str]]:
    """Load the applications configuration from YAML file."""
    if not config_path.exists():
        error_exit(f"Applications config file not found: {config_path}")

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        error_exit(f"Failed to load applications config: {e}")


def load_folders_config(config_path: Path) -> List[str]:
    """Load the folders configuration from YAML file."""
    if not config_path.exists():
        error_exit(f"Folders config file not found: {config_path}")

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('folders', [])
    except Exception as e:
        error_exit(f"Failed to load folders config: {e}")


def load_interactive_apps_config(config_path: Path) -> List[Dict[str, Any]]:
    """Load the interactive applications setup configuration from YAML file."""
    if not config_path.exists():
        error_exit(f"Interactive apps config file not found: {config_path}")

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('interactive_apps', [])
    except Exception as e:
        error_exit(f"Failed to load interactive apps config: {e}")


def is_app_installed(app_name: str) -> bool:
    """Check if a macOS application is installed."""
    result = run_command(["mdfind", f"kMDItemCFBundleIdentifier == '{app_name}'"], check=False, capture=True)
    return result.returncode == 0 and result.stdout.strip() != ""


def wait_for_user_confirmation(prompt: str = "Press Enter when done...") -> None:
    """Wait for user to press Enter to continue."""
    input(prompt)
