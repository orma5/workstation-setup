import sys
import json
from pathlib import Path
from datetime import datetime
from utils import (
    log, success, warn, error_exit, run_command, 
    load_interactive_apps_config, is_app_installed, 
    wait_for_user_confirmation, PROJECT_ROOT
)

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

    config_path = PROJECT_ROOT / "config" / "application-setup.yaml"

    # Load configuration
    interactive_apps = load_interactive_apps_config(config_path)

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
