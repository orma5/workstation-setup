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
import json
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


def load_interactive_apps_config(config_path: Path) -> List[Dict]:
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
        # Check if running in an interactive terminal
        if not sys.stdin.isatty():
            warn("Not running in an interactive terminal. Cannot prompt for git user.name.")
            warn("Please configure manually with: git config --global user.name \"Your Name\"")
            return
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
        # Check if running in an interactive terminal
        if not sys.stdin.isatty():
            warn("Not running in an interactive terminal. Cannot prompt for git user.email.")
            warn("Please configure manually with: git config --global user.email \"your@email.com\"")
            return
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


def ensure_1password_signin() -> None:
    """
    Ensure user is signed in to 1Password CLI.
    This function is declarative and idempotent - it checks if already signed in
    before attempting authentication.
    """
    log("Ensuring 1Password CLI is authenticated...")

    # Check if op command is available
    result = run_command(["which", "op"], check=False, capture=True)
    if result.returncode != 0:
        warn("1Password CLI (op) is not installed. Skipping 1Password authentication.")
        warn("Install 1password-cli via Homebrew if you need 1Password integration.")
        return

    # Check if already signed in
    result = run_command(["op", "account", "list"], check=False, capture=True)
    if result.returncode == 0 and result.stdout.strip():
        # Check if we can actually use the CLI (authenticated session)
        whoami_result = run_command(["op", "whoami"], check=False, capture=True)
        if whoami_result.returncode == 0:
            account_info = whoami_result.stdout.strip()
            success(f"Already signed in to 1Password: {account_info}")
            return

    # Not signed in, need to authenticate
    log("1Password CLI is not authenticated. Starting sign-in process...")

    # First try: Authenticate via 1Password app integration
    log("Attempting to sign in via 1Password app integration...")
    log("Make sure 1Password app is installed and 'Integrate with 1Password CLI' is enabled in Settings > Developer")

    # Try to sign in using the app integration
    app_signin_result = run_command(["op", "signin"], check=False, capture=False)

    if app_signin_result.returncode == 0:
        # Verify the sign-in worked
        verify_result = run_command(["op", "whoami"], check=False, capture=True)
        if verify_result.returncode == 0:
            account_info = verify_result.stdout.strip()
            success(f"Successfully signed in to 1Password via app: {account_info}")
            success("1Password CLI setup completed.")
            return

    # App integration failed, fall back to manual sign-in
    warn("Could not sign in via 1Password app. Falling back to manual sign-in...")

    # Check if running in an interactive terminal
    if not sys.stdin.isatty():
        warn("Not running in an interactive terminal. Cannot complete manual 1Password sign-in.")
        warn("To complete 1Password setup, run: op signin")
        return

    log("Note: For a smoother experience next time:")
    log("  1. Install the 1Password desktop app")
    log("  2. Go to Settings > Developer")
    log("  3. Enable 'Integrate with 1Password CLI'")

    # Prompt for sign-in address
    print("\n1Password Manual Sign-In")
    print("-" * 50)
    signin_address = input("Enter your 1Password sign-in address [default: https://my.1password.com]: ").strip()
    if not signin_address:
        signin_address = "https://my.1password.com"

    log(f"Signing in to 1Password at {signin_address}...")
    log("You will be prompted for your email, Secret Key, and password.")

    # Run op account add interactively (it will prompt user for credentials)
    result = run_command(["op", "account", "add", "--address", signin_address], check=False, capture=False)

    if result.returncode == 0:
        # Verify the sign-in worked
        verify_result = run_command(["op", "whoami"], check=False, capture=True)
        if verify_result.returncode == 0:
            account_info = verify_result.stdout.strip()
            success(f"Successfully signed in to 1Password: {account_info}")
        else:
            success("1Password account added. You may need to sign in again when running commands.")
    else:
        warn("Failed to sign in to 1Password. You can sign in manually later with: op account add")

    success("1Password CLI setup completed.")


def ensure_interactive_application_setup() -> None:
    """
    Ensure interactive applications (Chrome, Slack) are set up by launching them
    and allowing the user to sign in through their GUI.
    This function is declarative and idempotent - it checks if apps are installed
    before attempting to launch them.
    """
    log("Ensuring interactive applications are set up...")

    # Check if running in an interactive terminal
    if not sys.stdin.isatty():
        warn("Not running in an interactive terminal. Skipping interactive application setup.")
        warn("To set up interactive applications, run this script directly: uv run main.py")
        return

    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    config_path = script_dir / "config" / "application-setup.yaml"

    # Load configuration
    interactive_apps = load_interactive_apps_config(config_path)

    if not interactive_apps:
        warn("No interactive applications specified in configuration.")
        return

    log(f"Found {len(interactive_apps)} interactive applications to set up...")

    for app in interactive_apps:
        display_name = app.get('display_name')
        bundle_id = app.get('bundle_id')
        app_type = app.get('type')
        instructions = app.get('instructions', 'Please complete the setup')

        # Skip automated apps (they have their own dedicated setup functions)
        if app_type == 'automated':
            continue

        if not display_name or not bundle_id:
            warn(f"Skipping app with incomplete configuration: {app}")
            continue

        # Check if app is installed
        if not is_app_installed(bundle_id):
            warn(f"{display_name} is not installed. Skipping setup.")
            warn(f"Install it first with: brew install --cask {app.get('name', 'app-name')}")
            continue

        # Launch app for interactive setup
        log(f"\n{'='*60}")
        log(f"Setting up: {display_name}")
        log(f"{'='*60}")
        log(instructions)
        log("")

        # Prompt user to continue
        response = input(f"Press Enter to open {display_name} (or 's' to skip): ").strip().lower()
        if response == 's':
            warn(f"Skipped {display_name} setup.")
            continue

        # Launch the application
        log(f"Opening {display_name}...")
        result = run_command(["open", "-a", display_name], check=False, capture=True)

        if result.returncode != 0:
            warn(f"Failed to open {display_name}: {result.stderr}")
            continue

        success(f"{display_name} opened.")

        # Wait for user to complete setup
        wait_for_user_confirmation(f"Press Enter when you've completed the setup for {display_name}...")
        success(f"{display_name} setup completed.")

    success("All interactive application setups processed.")


def ensure_openvpn_setup() -> None:
    """
    Ensure OpenVPN Connect is set up with credentials from 1Password and profile from server.
    This function automates the OpenVPN setup by:
    1. Fetching credentials from 1Password CLI
    2. Downloading the VPN profile from a user-specified server
    3. Applying the profile to OpenVPN Connect
    """
    log("Ensuring OpenVPN Connect is set up...")

    # Check if running in an interactive terminal
    if not sys.stdin.isatty():
        warn("Not running in an interactive terminal. Skipping OpenVPN setup.")
        warn("To set up OpenVPN, run this script directly: uv run main.py")
        return

    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    config_path = script_dir / "config" / "application-setup.yaml"

    # Load configuration
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        interactive_apps = config.get('interactive_apps', [])
    except Exception as e:
        error_exit(f"Failed to load application-setup config: {e}")

    # Find OpenVPN configuration
    openvpn_config = None
    for app in interactive_apps:
        if app.get('name') == 'openvpn-connect' and app.get('type') == 'automated':
            openvpn_config = app
            break

    if not openvpn_config:
        warn("OpenVPN configuration not found in application-setup.yaml. Skipping.")
        return

    bundle_id = openvpn_config.get('bundle_id')
    onepassword_item_id = openvpn_config.get('onepassword_item_id')

    # Check if OpenVPN Connect is installed
    if not is_app_installed(bundle_id):
        warn("OpenVPN Connect is not installed. Skipping setup.")
        warn("Install it first with: brew install --cask openvpn-connect")
        return

    # Check if 1Password CLI is available and authenticated
    result = run_command(["which", "op"], check=False, capture=True)
    if result.returncode != 0:
        warn("1Password CLI (op) is not installed. Cannot fetch OpenVPN credentials.")
        warn("Install 1password-cli via Homebrew and sign in first.")
        return

    # Verify 1Password CLI is authenticated
    whoami_result = run_command(["op", "whoami"], check=False, capture=True)
    if whoami_result.returncode != 0:
        warn("1Password CLI is not authenticated. Please sign in first with: op signin")
        return

    log("\n" + "="*60)
    log("Setting up: OpenVPN Connect (Automated)")
    log("="*60)

    # Fetch credentials and profile URL from 1Password
    log("\nStep 1: Fetching OpenVPN credentials and profile URL from 1Password...")
    log("-" * 40)
    try:
        # Fetch the item in JSON format
        result = run_command(["op", "item", "get", onepassword_item_id, "--format", "json"], check=True, capture=True)

        if result.returncode == 0:
            success("Successfully fetched OpenVPN credentials from 1Password")

            # Parse JSON to extract username and password
            credentials = json.loads(result.stdout)

            # Extract username, password, and profile-download URL from fields
            username = None
            password = None
            profile_download_url = None

            for field in credentials.get('fields', []):
                field_id = field.get('id', '')
                field_label = field.get('label', '')
                field_value = field.get('value', '')

                # Extract specific fields by ID or label
                if field_id == 'username':
                    username = field_value
                elif field_id == 'password':
                    password = field_value
                elif field_label == 'profile-download':
                    profile_download_url = field_value

            if not username or not password:
                warn("Could not find username or password in 1Password item")
                warn("Please ensure the item has 'username' and 'password' fields")
                return

            if not profile_download_url:
                warn("Could not find profile-download URL in 1Password item")
                warn("Please ensure the item has a 'profile-download' field with the download URL")
                return

            log("Credentials and profile URL extracted successfully.")
        else:
            warn(f"Failed to fetch credentials from 1Password: {result.stderr}")
            return
    except json.JSONDecodeError as e:
        warn(f"Failed to parse 1Password JSON response: {e}")
        return
    except Exception as e:
        warn(f"Error fetching credentials from 1Password: {e}")
        return

    # Download VPN profile
    log("\nStep 2: Downloading OpenVPN profile from server...")
    log("-" * 40)

    # Download to ~/Downloads with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    downloads_dir = Path.home() / "Downloads"
    profile_path = downloads_dir / f"openvpn-profile-{timestamp}.ovpn"

    # Use wget to download the profile with authentication
    download_result = run_command([
        "wget",
        "-O", str(profile_path),
        f"--user={username}",
        f"--password={password}",
        "--no-check-certificate",
        profile_download_url
    ], check=False, capture=True)

    if download_result.returncode != 0:
        warn(f"Failed to download OpenVPN profile: {download_result.stderr}")
        warn("Please check the server URL and try again.")
        return

    if not profile_path.exists() or profile_path.stat().st_size == 0:
        warn("Downloaded profile is empty or does not exist.")
        return

    success(f"OpenVPN profile downloaded to: {profile_path}")

    # Interactive step: Open OpenVPN Connect for manual profile import
    log("\nStep 3: Import profile in OpenVPN Connect...")
    log("-" * 40)
    log("The OpenVPN profile has been downloaded to your Downloads folder.")
    log(f"Profile location: {profile_path}")
    log("")
    log("Next steps:")
    log("  1. OpenVPN Connect will be opened for you")
    log("  2. In the OpenVPN Connect app, import the profile:")
    log("     - Click on 'Import Profile' or the '+' button")
    log("     - Navigate to Downloads folder and select the profile")
    log("     - Or drag and drop the profile into OpenVPN Connect")
    log("  3. Complete the profile setup in the GUI")
    log("")

    # Prompt to open OpenVPN Connect
    response = input("Press Enter to open OpenVPN Connect (or 's' to skip): ").strip().lower()
    if response == 's':
        warn("Skipped opening OpenVPN Connect.")
        log(f"You can manually import the profile from: {profile_path}")
        return

    # Open OpenVPN Connect
    log("Opening OpenVPN Connect...")
    open_result = run_command(["open", "-a", "OpenVPN Connect"], check=False, capture=True)

    if open_result.returncode != 0:
        warn(f"Failed to open OpenVPN Connect: {open_result.stderr}")
        log(f"Please manually open OpenVPN Connect and import the profile from: {profile_path}")
        return

    success("OpenVPN Connect opened.")
    log("")

    # Wait for user to complete the import
    wait_for_user_confirmation("Press Enter when you've imported the profile in OpenVPN Connect...")

    success("OpenVPN setup completed!")
    log(f"Note: The profile file is still available at: {profile_path}")


def ensure_aws_cli_setup() -> None:
    """
    Ensure AWS CLI is set up with credentials from 1Password and configure kubectl for EKS.
    This function automates the AWS CLI and kubectl setup by:
    1. Fetching credentials from 1Password CLI (including EKS cluster name from "EKS" field)
    2. Configuring AWS CLI with access key, secret key, and region
    3. Configuring kubectl for EKS cluster if "EKS" field is present in 1Password
    """
    log("Ensuring AWS CLI is set up...")

    # Check if running in an interactive terminal
    if not sys.stdin.isatty():
        warn("Not running in an interactive terminal. Skipping AWS CLI setup.")
        warn("To set up AWS CLI, run this script directly: uv run main.py")
        return

    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    config_path = script_dir / "config" / "application-setup.yaml"

    # Load configuration
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        interactive_apps = config.get('interactive_apps', [])
    except Exception as e:
        error_exit(f"Failed to load application-setup config: {e}")

    # Find AWS CLI configuration
    aws_config = None
    for app in interactive_apps:
        if app.get('name') == 'awscli' and app.get('type') == 'automated':
            aws_config = app
            break

    if not aws_config:
        warn("AWS CLI configuration not found in application-setup.yaml. Skipping.")
        return

    onepassword_item_id = aws_config.get('onepassword_item_id')

    # Check if AWS CLI is installed
    result = run_command(["which", "aws"], check=False, capture=True)
    if result.returncode != 0:
        warn("AWS CLI is not installed. Skipping setup.")
        warn("Install it first with: brew install awscli")
        return

    # Check if 1Password CLI is available and authenticated
    result = run_command(["which", "op"], check=False, capture=True)
    if result.returncode != 0:
        warn("1Password CLI (op) is not installed. Cannot fetch AWS credentials.")
        warn("Install 1password-cli via Homebrew and sign in first.")
        return

    # Verify 1Password CLI is authenticated
    whoami_result = run_command(["op", "whoami"], check=False, capture=True)
    if whoami_result.returncode != 0:
        warn("1Password CLI is not authenticated. Please sign in first with: op signin")
        return

    log("\n" + "="*60)
    log("Setting up: AWS CLI (Automated)")
    log("="*60)

    # Check if AWS is already configured
    aws_credentials_file = Path.home() / ".aws" / "credentials"
    aws_config_file = Path.home() / ".aws" / "config"

    if aws_credentials_file.exists() and aws_credentials_file.stat().st_size > 0:
        log("AWS CLI appears to be already configured.")
        response = input("Do you want to reconfigure AWS CLI? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            success("Skipping AWS CLI configuration.")
            return

    # Fetch credentials from 1Password
    log("\nStep 1: Fetching AWS credentials from 1Password...")
    log("-" * 40)
    try:
        # Fetch the item in JSON format
        result = run_command(["op", "item", "get", onepassword_item_id, "--reveal","--format", "json"], check=True, capture=True)

        if result.returncode == 0:
            success("Successfully fetched AWS credentials from 1Password")

            # Parse JSON to extract credentials
            credentials = json.loads(result.stdout)

            # Extract fields
            access_key_id = None
            secret_access_key = None
            eks_cluster_name = None
            region = ""
            output_format = "json"

            for field in credentials.get('fields', []):
                field_label = field.get('label', '').lower()
                field_value = field.get('value', '')

                # Look for access key
                if field_label == 'access key':
                    access_key_id = field_value
                # Look for secret key
                elif field_label == 'access secret':
                    secret_access_key = field_value
                # Look for EKS cluster name
                elif field_label == 'eks':
                    eks_cluster_name = field_value

            if not access_key_id or not secret_access_key:
                warn("Could not find access key or secret key in 1Password item")
                warn("Please ensure the item has fields for AWS access key and secret key")
                return

            log("Credentials extracted successfully.")
            if eks_cluster_name:
                log(f"Found EKS cluster configuration: {eks_cluster_name}")

            # Set default values if not found
            region = input("Enter AWS region (default: eu-west-1): ").strip()
            if not region:
                region = "eu-west-1"

        else:
            warn(f"Failed to fetch credentials from 1Password: {result.stderr}")
            return
    except json.JSONDecodeError as e:
        warn(f"Failed to parse 1Password JSON response: {e}")
        return
    except Exception as e:
        warn(f"Error fetching credentials from 1Password: {e}")
        return

    # Configure AWS CLI
    log("\nStep 2: Configuring AWS CLI...")
    log("-" * 40)

    try:
        # Create .aws directory if it doesn't exist
        aws_dir = Path.home() / ".aws"
        aws_dir.mkdir(parents=True, exist_ok=True)

        # Configure AWS CLI using environment variables and aws configure set
        log("Setting AWS access key ID...")
        result = run_command(["aws", "configure", "set", "aws_access_key_id", access_key_id], check=False, capture=True)
        if result.returncode != 0:
            warn(f"Failed to set AWS access key ID: {result.stderr}")
            return

        log("Setting AWS secret access key...")
        result = run_command(["aws", "configure", "set", "aws_secret_access_key", secret_access_key], check=False, capture=True)
        if result.returncode != 0:
            warn(f"Failed to set AWS secret access key: {result.stderr}")
            return

        log(f"Setting default region to {region}...")
        result = run_command(["aws", "configure", "set", "region", region], check=False, capture=True)
        if result.returncode != 0:
            warn(f"Failed to set AWS region: {result.stderr}")
            return

        log(f"Setting output format to {output_format}...")
        result = run_command(["aws", "configure", "set", "output", output_format], check=False, capture=True)
        if result.returncode != 0:
            warn(f"Failed to set AWS output format: {result.stderr}")
            return

        success("AWS CLI configured successfully!")

        # Verify configuration
        log("\nStep 3: Verifying AWS CLI configuration...")
        log("-" * 40)
        verify_result = run_command(["aws", "sts", "get-caller-identity"], check=False, capture=True)
        if verify_result.returncode == 0:
            success("AWS CLI is working correctly!")
            log(f"Account information:\n{verify_result.stdout}")
        else:
            warn("Could not verify AWS credentials. You may need to check your configuration.")
            warn(f"Error: {verify_result.stderr}")

    except Exception as e:
        warn(f"Error configuring AWS CLI: {e}")
        return

    # Configure kubectl for EKS if cluster name is available
    if eks_cluster_name:
        log("\nStep 4: Configuring kubectl for EKS cluster...")
        log("-" * 40)

        # Check if kubectl is installed
        kubectl_check = run_command(["which", "kubectl"], check=False, capture=True)
        if kubectl_check.returncode != 0:
            warn("kubectl is not installed. Skipping EKS kubectl setup.")
            warn("Install it with: brew install kubernetes-cli")
        else:
            log(f"Configuring kubectl for EKS cluster: {eks_cluster_name}")
            log(f"Using region: {region}")

            # Run aws eks update-kubeconfig
            kubectl_result = run_command([
                "aws", "eks", "update-kubeconfig",
                "--name", eks_cluster_name,
                "--region", region
            ], check=False, capture=True)

            if kubectl_result.returncode == 0:
                success(f"kubectl configured successfully for cluster: {eks_cluster_name}")
                if kubectl_result.stdout.strip():
                    log(kubectl_result.stdout.strip())
                log("You can now use kubectl to interact with your EKS cluster.")
                log("Use 'kubectl config get-contexts' to see configured contexts.")
            else:
                warn(f"Failed to configure kubectl for cluster: {eks_cluster_name}")
                if kubectl_result.stderr.strip():
                    warn(f"Error: {kubectl_result.stderr.strip()}")
                log("\nCommon reasons for failure:")
                log("  - Cluster does not exist in the specified region")
                log("  - Insufficient AWS permissions to access the cluster")
                log("  - Incorrect cluster name in 1Password")

    success("AWS CLI setup completed!")


def ensure_macos_settings() -> None:
    """
    Ensure macOS system preferences are configured according to best practices.
    This function applies numerous defaults write commands to configure:
    - General system settings
    - Input devices (trackpad, keyboard)
    - Power management
    - Security settings
    - Finder preferences
    - Dock configuration
    - Application-specific settings
    """
    log("Ensuring macOS system settings are configured...")

    # Track failed settings for summary
    failed_settings = []

    def apply_setting(description: str, command: List[str]) -> None:
        """Apply a single macOS setting and log the result."""
        try:
            result = run_command(command, check=False, capture=True)
            if result.returncode == 0:
                success(description)
            else:
                warn(f"{description} - Failed: {result.stderr.strip() if result.stderr else 'Unknown error'}")
                failed_settings.append(description)
        except Exception as e:
            warn(f"{description} - Error: {e}")
            failed_settings.append(description)

    # ========================================
    # GENERAL SYSTEM SETTINGS
    # ========================================
    log("\nConfiguring general system settings...")

    apply_setting(
        "Save to disk (not iCloud) by default",
        ["defaults", "write", "NSGlobalDomain", "NSDocumentSaveNewDocumentsToCloud", "-bool", "false"]
    )

    apply_setting(
        "Automatically quit printer app when jobs complete",
        ["defaults", "write", "com.apple.print.PrintingPrefs", "Quit When Finished", "-bool", "true"]
    )

    apply_setting(
        "Disable 'Are you sure you want to open?' dialog",
        ["defaults", "write", "com.apple.LaunchServices", "LSQuarantine", "-bool", "false"]
    )

    # ========================================
    # TRACKPAD SETTINGS
    # ========================================
    log("\nConfiguring trackpad settings...")

    apply_setting(
        "Enable tap to click (trackpad)",
        ["defaults", "write", "com.apple.driver.AppleBluetoothMultitouch.trackpad", "Clicking", "-bool", "true"]
    )

    apply_setting(
        "Enable tap to click (current user)",
        ["defaults", "-currentHost", "write", "NSGlobalDomain", "com.apple.mouse.tapBehavior", "-int", "1"]
    )

    apply_setting(
        "Enable tap to click (login screen)",
        ["defaults", "write", "NSGlobalDomain", "com.apple.mouse.tapBehavior", "-int", "1"]
    )

    # ========================================
    # BLUETOOTH AUDIO
    # ========================================
    log("\nConfiguring Bluetooth audio quality...")

    apply_setting(
        "Increase Bluetooth audio quality",
        ["defaults", "write", "com.apple.BluetoothAudioAgent", "Apple Bitpool Min (editable)", "-int", "40"]
    )

    # ========================================
    # KEYBOARD SETTINGS
    # ========================================
    log("\nConfiguring keyboard settings...")

    apply_setting(
        "Enable full keyboard access for all controls",
        ["defaults", "write", "NSGlobalDomain", "AppleKeyboardUIMode", "-int", "3"]
    )

    apply_setting(
        "Disable press-and-hold for keys (favor key repeat)",
        ["defaults", "write", "NSGlobalDomain", "ApplePressAndHoldEnabled", "-bool", "false"]
    )

    apply_setting(
        "Set fast keyboard repeat rate",
        ["defaults", "write", "NSGlobalDomain", "KeyRepeat", "-int", "1"]
    )

    apply_setting(
        "Set short initial key repeat delay",
        ["defaults", "write", "NSGlobalDomain", "InitialKeyRepeat", "-int", "10"]
    )

    # Stop iTunes from responding to media keys
    apply_setting(
        "Stop iTunes from responding to media keys",
        ["launchctl", "unload", "-w", "/System/Library/LaunchAgents/com.apple.rcd.plist"]
    )

    # ========================================
    # POWER MANAGEMENT SETTINGS
    # ========================================
    log("\nConfiguring power management settings...")

    apply_setting(
        "Enable lid wakeup",
        ["sudo", "pmset", "-a", "lidwake", "1"]
    )

    apply_setting(
        "Sleep display after 15 minutes",
        ["sudo", "pmset", "-a", "displaysleep", "15"]
    )

    apply_setting(
        "Disable sleep while charging",
        ["sudo", "pmset", "-c", "sleep", "0"]
    )

    apply_setting(
        "Set 5 minute sleep on battery",
        ["sudo", "pmset", "-b", "sleep", "5"]
    )

    apply_setting(
        "Set 24 hour standby delay",
        ["sudo", "pmset", "-a", "standbydelay", "86400"]
    )

    apply_setting(
        "Never go into computer sleep mode",
        ["sudo", "systemsetup", "-setcomputersleep", "Off"]
    )

    apply_setting(
        "Disable hibernation mode",
        ["sudo", "pmset", "-a", "hibernatemode", "0"]
    )

    # Remove sleep image file to save disk space
    log("Removing sleep image file...")
    sleepimage_path = Path("/private/var/vm/sleepimage")
    try:
        # Remove existing file
        if sleepimage_path.exists():
            run_command(["sudo", "rm", str(sleepimage_path)], check=False, capture=True)
        # Create zero-byte file
        run_command(["sudo", "touch", str(sleepimage_path)], check=False, capture=True)
        # Make it immutable
        result = run_command(["sudo", "chflags", "uchg", str(sleepimage_path)], check=False, capture=True)
        if result.returncode == 0:
            success("Sleep image file removed and locked")
        else:
            warn("Could not lock sleep image file")
    except Exception as e:
        warn(f"Error managing sleep image file: {e}")

    # ========================================
    # SECURITY SETTINGS
    # ========================================
    log("\nConfiguring security settings...")

    apply_setting(
        "Require password immediately after sleep/screensaver",
        ["defaults", "write", "com.apple.screensaver", "askForPassword", "-int", "1"]
    )

    apply_setting(
        "No delay for screensaver password",
        ["defaults", "write", "com.apple.screensaver", "askForPasswordDelay", "-int", "0"]
    )

    # ========================================
    # SCREENSHOT SETTINGS
    # ========================================
    log("\nConfiguring screenshot settings...")

    desktop_path = str(Path.home() / "Desktop")
    apply_setting(
        "Save screenshots to Desktop",
        ["defaults", "write", "com.apple.screencapture", "location", "-string", desktop_path]
    )

    apply_setting(
        "Save screenshots in PNG format",
        ["defaults", "write", "com.apple.screencapture", "type", "-string", "png"]
    )

    apply_setting(
        "Disable shadow in screenshots",
        ["defaults", "write", "com.apple.screencapture", "disable-shadow", "-bool", "true"]
    )

    # ========================================
    # DISPLAY SETTINGS
    # ========================================
    log("\nConfiguring display settings...")

    apply_setting(
        "Enable subpixel font rendering on non-Apple LCDs",
        ["defaults", "write", "NSGlobalDomain", "AppleFontSmoothing", "-int", "1"]
    )

    apply_setting(
        "Enable HiDPI display modes",
        ["sudo", "defaults", "write", "/Library/Preferences/com.apple.windowserver", "DisplayResolutionEnabled", "-bool", "true"]
    )

    # ========================================
    # FINDER SETTINGS
    # ========================================
    log("\nConfiguring Finder settings...")

    apply_setting(
        "Allow quitting Finder via Cmd+Q",
        ["defaults", "write", "com.apple.finder", "QuitMenuItem", "-bool", "true"]
    )

    apply_setting(
        "Disable Finder animations",
        ["defaults", "write", "com.apple.finder", "DisableAllAnimations", "-bool", "true"]
    )

    apply_setting(
        "Set Desktop as default location for new Finder windows",
        ["defaults", "write", "com.apple.finder", "NewWindowTarget", "-string", "PfDe"]
    )

    desktop_file_url = f"file://{Path.home()}/Desktop/"
    apply_setting(
        "Set Desktop path for new Finder windows",
        ["defaults", "write", "com.apple.finder", "NewWindowTargetPath", "-string", desktop_file_url]
    )

    apply_setting(
        "Show external hard drives on desktop",
        ["defaults", "write", "com.apple.finder", "ShowExternalHardDrivesOnDesktop", "-bool", "true"]
    )

    apply_setting(
        "Show hard drives on desktop",
        ["defaults", "write", "com.apple.finder", "ShowHardDrivesOnDesktop", "-bool", "true"]
    )

    apply_setting(
        "Show mounted servers on desktop",
        ["defaults", "write", "com.apple.finder", "ShowMountedServersOnDesktop", "-bool", "true"]
    )

    apply_setting(
        "Show removable media on desktop",
        ["defaults", "write", "com.apple.finder", "ShowRemovableMediaOnDesktop", "-bool", "true"]
    )

    apply_setting(
        "Show hidden files in Finder",
        ["defaults", "write", "com.apple.finder", "AppleShowAllFiles", "-bool", "true"]
    )

    apply_setting(
        "Show all filename extensions",
        ["defaults", "write", "NSGlobalDomain", "AppleShowAllExtensions", "-bool", "true"]
    )

    apply_setting(
        "Show Finder status bar",
        ["defaults", "write", "com.apple.finder", "ShowStatusBar", "-bool", "true"]
    )

    apply_setting(
        "Show Finder path bar",
        ["defaults", "write", "com.apple.finder", "ShowPathbar", "-bool", "true"]
    )

    apply_setting(
        "Display full POSIX path in Finder title",
        ["defaults", "write", "com.apple.finder", "_FXShowPosixPathInTitle", "-bool", "true"]
    )

    apply_setting(
        "Keep folders on top when sorting by name",
        ["defaults", "write", "com.apple.finder", "_FXSortFoldersFirst", "-bool", "true"]
    )

    apply_setting(
        "Search current folder by default",
        ["defaults", "write", "com.apple.finder", "FXDefaultSearchScope", "-string", "SCcf"]
    )

    apply_setting(
        "Disable file extension change warning",
        ["defaults", "write", "com.apple.finder", "FXEnableExtensionChangeWarning", "-bool", "false"]
    )

    apply_setting(
        "Enable spring loading for directories",
        ["defaults", "write", "NSGlobalDomain", "com.apple.springing.enabled", "-bool", "true"]
    )

    apply_setting(
        "Remove spring loading delay",
        ["defaults", "write", "NSGlobalDomain", "com.apple.springing.delay", "-float", "0"]
    )

    apply_setting(
        "Avoid creating .DS_Store on network volumes",
        ["defaults", "write", "com.apple.desktopservices", "DSDontWriteNetworkStores", "-bool", "true"]
    )

    apply_setting(
        "Avoid creating .DS_Store on USB volumes",
        ["defaults", "write", "com.apple.desktopservices", "DSDontWriteUSBStores", "-bool", "true"]
    )

    apply_setting(
        "Disable disk image verification",
        ["defaults", "write", "com.apple.frameworks.diskimages", "skip-verify", "-bool", "true"]
    )

    apply_setting(
        "Disable locked disk image verification",
        ["defaults", "write", "com.apple.frameworks.diskimages", "skip-verify-locked", "-bool", "true"]
    )

    apply_setting(
        "Disable remote disk image verification",
        ["defaults", "write", "com.apple.frameworks.diskimages", "skip-verify-remote", "-bool", "true"]
    )

    apply_setting(
        "Auto-open read-only disk images",
        ["defaults", "write", "com.apple.frameworks.diskimages", "auto-open-ro-root", "-bool", "true"]
    )

    apply_setting(
        "Auto-open read-write disk images",
        ["defaults", "write", "com.apple.frameworks.diskimages", "auto-open-rw-root", "-bool", "true"]
    )

    apply_setting(
        "Auto-open Finder for new removable disks",
        ["defaults", "write", "com.apple.finder", "OpenWindowForNewRemovableDisk", "-bool", "true"]
    )

    apply_setting(
        "Use list view in Finder by default",
        ["defaults", "write", "com.apple.finder", "FXPreferredViewStyle", "-string", "Nlsv"]
    )

    apply_setting(
        "Disable empty Trash warning",
        ["defaults", "write", "com.apple.finder", "WarnOnEmptyTrash", "-bool", "false"]
    )

    # Show ~/Library folder
    log("Showing ~/Library folder...")
    library_path = Path.home() / "Library"
    try:
        run_command(["chflags", "nohidden", str(library_path)], check=False, capture=True)
        run_command(["xattr", "-d", "com.apple.FinderInfo", str(library_path)], check=False, capture=True)
        success("~/Library folder is now visible")
    except Exception as e:
        warn(f"Could not show ~/Library folder: {e}")

    # Show /Volumes folder
    apply_setting(
        "Show /Volumes folder",
        ["sudo", "chflags", "nohidden", "/Volumes"]
    )

    # Expand File Info panes
    apply_setting(
        "Expand File Info panes in Finder",
        ["defaults", "write", "com.apple.finder", "FXInfoPanesExpanded", "-dict",
         "General", "-bool", "true",
         "OpenWith", "-bool", "true",
         "Privileges", "-bool", "true"]
    )

    # ========================================
    # DOCK SETTINGS
    # ========================================
    log("\nConfiguring Dock settings...")

    apply_setting(
        "Set Dock icon size to 36 pixels",
        ["defaults", "write", "com.apple.dock", "tilesize", "-int", "36"]
    )

    apply_setting(
        "Minimize windows into application icon",
        ["defaults", "write", "com.apple.dock", "minimize-to-application", "-bool", "true"]
    )

    apply_setting(
        "Show indicator lights for open apps",
        ["defaults", "write", "com.apple.dock", "show-process-indicators", "-bool", "true"]
    )

    apply_setting(
        "Disable Dashboard",
        ["defaults", "write", "com.apple.dashboard", "mcx-disabled", "-bool", "true"]
    )

    apply_setting(
        "Don't show Dashboard as a Space",
        ["defaults", "write", "com.apple.dock", "dashboard-in-overlay", "-bool", "true"]
    )

    apply_setting(
        "Don't automatically rearrange Spaces",
        ["defaults", "write", "com.apple.dock", "mru-spaces", "-bool", "false"]
    )

    apply_setting(
        "Don't show recent applications in Dock",
        ["defaults", "write", "com.apple.dock", "show-recents", "-bool", "false"]
    )

    # ========================================
    # APPLICATION-SPECIFIC SETTINGS
    # ========================================
    log("\nConfiguring application-specific settings...")

    # iTerm2
    apply_setting(
        "Don't prompt when quitting iTerm",
        ["defaults", "write", "com.googlecode.iterm2", "PromptOnQuit", "-bool", "false"]
    )

    # Activity Monitor
    apply_setting(
        "Show main window when launching Activity Monitor",
        ["defaults", "write", "com.apple.ActivityMonitor", "OpenMainWindow", "-bool", "true"]
    )

    apply_setting(
        "Visualize CPU usage in Activity Monitor Dock icon",
        ["defaults", "write", "com.apple.ActivityMonitor", "IconType", "-int", "5"]
    )

    apply_setting(
        "Show all processes in Activity Monitor",
        ["defaults", "write", "com.apple.ActivityMonitor", "ShowCategory", "-int", "0"]
    )

    apply_setting(
        "Sort Activity Monitor by CPU usage",
        ["defaults", "write", "com.apple.ActivityMonitor", "SortColumn", "-string", "CPUUsage"]
    )

    apply_setting(
        "Set Activity Monitor sort direction",
        ["defaults", "write", "com.apple.ActivityMonitor", "SortDirection", "-int", "0"]
    )

    # Disk Utility
    apply_setting(
        "Enable debug menu in Disk Utility",
        ["defaults", "write", "com.apple.DiskUtility", "DUDebugMenuEnabled", "-bool", "true"]
    )

    apply_setting(
        "Enable advanced image options in Disk Utility",
        ["defaults", "write", "com.apple.DiskUtility", "advanced-image-options", "-bool", "true"]
    )

    # Google Chrome
    apply_setting(
        "Disable backswipe navigation in Chrome (trackpad)",
        ["defaults", "write", "com.google.Chrome", "AppleEnableSwipeNavigateWithScrolls", "-bool", "false"]
    )

    apply_setting(
        "Disable backswipe navigation in Chrome Canary (trackpad)",
        ["defaults", "write", "com.google.Chrome.canary", "AppleEnableSwipeNavigateWithScrolls", "-bool", "false"]
    )

    apply_setting(
        "Disable backswipe navigation in Chrome (mouse)",
        ["defaults", "write", "com.google.Chrome", "AppleEnableMouseSwipeNavigateWithScrolls", "-bool", "false"]
    )

    apply_setting(
        "Disable backswipe navigation in Chrome Canary (mouse)",
        ["defaults", "write", "com.google.Chrome.canary", "AppleEnableMouseSwipeNavigateWithScrolls", "-bool", "false"]
    )

    apply_setting(
        "Use system print dialog in Chrome",
        ["defaults", "write", "com.google.Chrome", "DisablePrintPreview", "-bool", "true"]
    )

    apply_setting(
        "Use system print dialog in Chrome Canary",
        ["defaults", "write", "com.google.Chrome.canary", "DisablePrintPreview", "-bool", "true"]
    )

    apply_setting(
        "Expand print dialog in Chrome",
        ["defaults", "write", "com.google.Chrome", "PMPrintingExpandedStateForPrint2", "-bool", "true"]
    )

    apply_setting(
        "Expand print dialog in Chrome Canary",
        ["defaults", "write", "com.google.Chrome.canary", "PMPrintingExpandedStateForPrint2", "-bool", "true"]
    )

    # ========================================
    # INTERACTIVE MANUAL STEPS
    # ========================================
    log("\nMacOS settings have been applied.")

    # Check if running in interactive mode
    if sys.stdin.isatty():
        log("\n" + "="*60)
        log("Manual Configuration Steps")
        log("="*60)
        log("The following settings need to be configured manually:")
        log("  1. Top bar: Add sound, displays, and bluetooth controls")
        log("  2. Desktop background: Set your preferred wallpaper")
        log("")

        response = input("Press Enter when you've completed these manual steps (or 's' to skip): ").strip().lower()
        if response != 's':
            success("Manual configuration steps completed.")
        else:
            warn("Skipped manual configuration steps. You can do these later.")
    else:
        log("\nNote: Some settings need manual configuration:")
        log("  - Top bar: Add sound, displays, and bluetooth controls")
        log("  - Desktop background: Set your preferred wallpaper")

    # ========================================
    # SUMMARY
    # ========================================
    if failed_settings:
        warn(f"\n{len(failed_settings)} settings could not be applied:")
        for setting in failed_settings:
            warn(f"  - {setting}")
        log("\nNote: Some settings may require a logout/restart to take effect.")
        log("You can review and apply failed settings manually if needed.")
    else:
        success("\nAll macOS settings applied successfully!")
        log("Note: Some settings may require a logout/restart to take effect.")

    success("macOS system settings configuration completed.")


def ensure_development_projects() -> None:
    """
    Ensure development projects are cloned.
    This is a manual placeholder function that prompts the user to perform the step.
    """
    log("Ensuring development projects are cloned...")

    # Check if running in an interactive terminal
    if not sys.stdin.isatty():
        warn("Not running in an interactive terminal. Skipping development projects setup.")
        warn("Please clone your development projects manually.")
        return

    log("\n" + "="*60)
    log("Manual Step: Clone Development Projects")
    log("="*60)
    log("Please clone your development projects to the appropriate directories.")
    log("")
    log("Example steps:")
    log("  1. Navigate to your projects folder")
    log("  2. Clone repositories using: git clone <repository-url>")
    log("  3. Repeat for all required projects")
    log("")

    # Wait for user to complete the manual step
    wait_for_user_confirmation("Press Enter when you've cloned all development projects...")
    success("Development projects setup completed.")


def ensure_python_development_environments() -> None:
    """
    Ensure Python development environments are set up.
    This is a manual placeholder function that prompts the user to perform the step.
    """
    log("Ensuring Python development environments are set up...")

    # Check if running in an interactive terminal
    if not sys.stdin.isatty():
        warn("Not running in an interactive terminal. Skipping Python development environments setup.")
        warn("Please set up your Python development environments manually.")
        return

    log("\n" + "="*60)
    log("Manual Step: Setup Python Development Environments")
    log("="*60)
    log("Please set up your Python development environments for your projects.")
    log("")
    log("Example steps:")
    log("  1. Navigate to each Python project directory")
    log("  2. Create virtual environments: python -m venv venv")
    log("  3. Activate virtual environments: source venv/bin/activate")
    log("  4. Install dependencies: pip install -r requirements.txt")
    log("  5. Configure IDE/editor Python interpreters")
    log("")

    # Wait for user to complete the manual step
    wait_for_user_confirmation("Press Enter when you've set up all Python development environments...")
    success("Python development environments setup completed.")


def ensure_terminal_configuration() -> None:
    """
    Ensure terminal is configured.
    This is a manual placeholder function that prompts the user to perform the step.
    """
    log("Ensuring terminal is configured...")

    # Check if running in an interactive terminal
    if not sys.stdin.isatty():
        warn("Not running in an interactive terminal. Skipping terminal configuration.")
        warn("Please configure your terminal manually.")
        return

    log("\n" + "="*60)
    log("Manual Step: Configure Terminal")
    log("="*60)
    log("Please configure your terminal preferences and settings.")
    log("")
    log("Example steps:")
    log("  1. Configure terminal theme/colors")
    log("  2. Set up shell profile (.zshrc, .bashrc, etc.)")
    log("  3. Install and configure shell plugins (oh-my-zsh, etc.)")
    log("  4. Set up command aliases and environment variables")
    log("  5. Configure terminal font and appearance")
    log("")

    # Wait for user to complete the manual step
    wait_for_user_confirmation("Press Enter when you've configured the terminal...")
    success("Terminal configuration completed.")


# ========================================
# MAIN
# ========================================

def main() -> None:
    """Main entry point for the setup script."""
    log("Starting macOS workstation setup...")

    # Run setup steps with error handling to ensure all steps are attempted
    steps = [
        ("Homebrew applications", ensure_homebrew_applications),
        ("Folders", ensure_folders),
        ("Git configuration", ensure_git_config),
        ("1Password sign-in", ensure_1password_signin),
        ("Interactive application setup", ensure_interactive_application_setup),
        ("OpenVPN setup", ensure_openvpn_setup),
        ("AWS CLI setup", ensure_aws_cli_setup),
        ("macOS system settings", ensure_macos_settings),
        ("Clone development projects", ensure_development_projects),
        ("Setup Python development environments", ensure_python_development_environments),
        ("Configure terminal", ensure_terminal_configuration),
    ]

    failed_steps = []

    for step_name, step_func in steps:
        try:
            log(f"\n{'='*60}")
            log(f"Step: {step_name}")
            log(f"{'='*60}")
            step_func()
        except SystemExit:
            # Catch sys.exit() calls from error_exit()
            warn(f"Step '{step_name}' failed with critical error. Continuing with remaining steps...")
            failed_steps.append(step_name)
        except Exception as e:
            warn(f"Step '{step_name}' failed: {e}. Continuing with remaining steps...")
            failed_steps.append(step_name)

    if failed_steps:
        warn(f"\nThe following steps failed: {', '.join(failed_steps)}")
        warn("Please review the errors above and re-run the script or fix issues manually.")
    else:
        success("All setup steps completed successfully!")


if __name__ == "__main__":
    main()
