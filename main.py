#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pyyaml",
# ]
# ///

"""
macOS Workstation Setup Helper
This script provides declarative functions for setting up a macOS workstation.
It is called by jumpstart.sh and inherits sudo privileges from it.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict
import yaml


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
    sys.exit(1)


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


# ========================================
# DECLARATIVE SETUP FUNCTIONS
# ========================================

def ensure_homebrew_applications() -> None:
    """
    Ensure all applications from applications.yaml are installed via Homebrew.
    This function is declarative and idempotent - it checks if each app is already
    installed before attempting installation.
    """
    log("Ensuring Homebrew applications are installed...")

    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    config_path = script_dir / "config" / "applications.yaml"

    # Load configuration
    config = load_applications_config(config_path)

    # Install cask applications
    casks = config.get('casks', [])
    if casks:
        log(f"Checking {len(casks)} cask applications...")
        for cask in casks:
            if is_cask_installed(cask):
                success(f"{cask} already installed.")
            else:
                log(f"Installing {cask}...")
                result = run_command(["brew", "install", "--cask", cask], check=False, capture=True)
                if result.returncode == 0:
                    success(f"{cask} installed.")
                else:
                    warn(f"Failed to install {cask}: {result.stderr}")

    # Install formula packages
    formulae = config.get('formulae', [])
    if formulae:
        log(f"Checking {len(formulae)} formula packages...")
        for formula in formulae:
            if is_formula_installed(formula):
                success(f"{formula} already installed.")
            else:
                log(f"Installing {formula}...")
                result = run_command(["brew", "install", formula], check=False, capture=True)
                if result.returncode == 0:
                    success(f"{formula} installed.")
                else:
                    warn(f"Failed to install {formula}: {result.stderr}")

    success("All Homebrew applications processed.")


def ensure_folders() -> None:
    """
    Ensure all folders from folders.yaml are created.
    This function is declarative and idempotent - it checks if each folder exists
    before attempting creation.
    """
    log("Ensuring folders are created...")

    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    config_path = script_dir / "config" / "folders.yaml"

    # Load configuration
    folders = load_folders_config(config_path)

    if not folders:
        warn("No folders specified in configuration.")
        return

    log(f"Checking {len(folders)} folders...")
    for folder_path_str in folders:
        # Expand ~ to user's home directory
        folder_path = Path(folder_path_str).expanduser()

        if folder_path.exists():
            if folder_path.is_dir():
                success(f"{folder_path} already exists.")
            else:
                warn(f"{folder_path} exists but is not a directory.")
        else:
            try:
                log(f"Creating {folder_path}...")
                folder_path.mkdir(parents=True, exist_ok=True)
                success(f"{folder_path} created.")
            except Exception as e:
                warn(f"Failed to create {folder_path}: {e}")

    success("All folders processed.")


def ensure_git_config() -> None:
    """
    Ensure git configuration files are installed and git user is configured.
    This function is declarative and idempotent - it checks if files and config
    already exist before prompting or copying.
    """
    log("Ensuring git configuration is set up...")

    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    dotfiles_dir = script_dir / "dotfiles"

    # Define source and destination paths
    gitconfig_source = dotfiles_dir / ".gitconfig"
    gitignore_source = dotfiles_dir / ".global-gitignore"
    gitconfig_dest = Path.home() / ".gitconfig"
    gitignore_dest = Path.home() / ".global-gitignore"

    # Check if source files exist
    if not gitconfig_source.exists():
        error_exit(f"Source .gitconfig not found at: {gitconfig_source}")
    if not gitignore_source.exists():
        error_exit(f"Source .global-gitignore not found at: {gitignore_source}")

    # Get or prompt for git user configuration
    result = run_command(["git", "config", "--global", "user.name"], check=False, capture=True)
    if result.returncode == 0 and result.stdout.strip():
        git_user_name = result.stdout.strip()
        success(f"Git user.name already configured: {git_user_name}")
    else:
        log("Git user.name is not configured.")
        git_user_name = input("Enter your full name for git commits: ").strip()
        while not git_user_name:
            warn("Name cannot be empty.")
            git_user_name = input("Enter your full name for git commits: ").strip()
        run_command(["git", "config", "--global", "user.name", git_user_name])
        success(f"Git user.name set to: {git_user_name}")

    result = run_command(["git", "config", "--global", "user.email"], check=False, capture=True)
    if result.returncode == 0 and result.stdout.strip():
        git_user_email = result.stdout.strip()
        success(f"Git user.email already configured: {git_user_email}")
    else:
        log("Git user.email is not configured.")
        git_user_email = input("Enter your email for git commits: ").strip()
        while not git_user_email:
            warn("Email cannot be empty.")
            git_user_email = input("Enter your email for git commits: ").strip()
        run_command(["git", "config", "--global", "user.email", git_user_email])
        success(f"Git user.email set to: {git_user_email}")

    # Install .gitconfig (merge with existing or create new)
    if gitconfig_dest.exists():
        log(f"{gitconfig_dest} already exists. Appending additional config...")
        try:
            # Read the source config and append it
            with open(gitconfig_source, 'r') as src:
                config_content = src.read()
            with open(gitconfig_dest, 'a') as dest:
                dest.write("\n# Added by workstation-setup\n")
                dest.write(config_content)
            success(f"Additional git config appended to {gitconfig_dest}")
        except Exception as e:
            warn(f"Failed to append git config: {e}")
    else:
        try:
            log(f"Installing .gitconfig to {gitconfig_dest}...")
            with open(gitconfig_source, 'r') as src:
                content = src.read()
            with open(gitconfig_dest, 'w') as dest:
                dest.write(content)
            success(f".gitconfig installed to {gitconfig_dest}")
        except Exception as e:
            warn(f"Failed to install .gitconfig: {e}")

    # Install .global-gitignore
    if gitignore_dest.exists():
        success(f"{gitignore_dest} already exists.")
    else:
        try:
            log(f"Installing .global-gitignore to {gitignore_dest}...")
            with open(gitignore_source, 'r') as src:
                content = src.read()
            with open(gitignore_dest, 'w') as dest:
                dest.write(content)
            success(f".global-gitignore installed to {gitignore_dest}")
        except Exception as e:
            warn(f"Failed to install .global-gitignore: {e}")

    success("Git configuration setup completed.")


# ========================================
# MAIN
# ========================================

def main() -> None:
    """Main entry point for the setup script."""
    log("Starting macOS workstation setup...")

    # Run setup steps
    ensure_homebrew_applications()
    ensure_folders()
    ensure_git_config()

    success("All setup steps completed successfully!")


if __name__ == "__main__":
    main()
