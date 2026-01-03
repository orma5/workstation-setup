import sys
from pathlib import Path
from utils import (
    log, success, warn, run_command, 
    load_interactive_apps_config, is_app_installed, 
    wait_for_user_confirmation, PROJECT_ROOT
)

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

    config_path = PROJECT_ROOT / "config" / "application-setup.yaml"

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
        log(f"{ '='*60}")
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
