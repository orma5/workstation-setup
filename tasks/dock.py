from utils import log, success, warn, run_command

def ensure_dock_setup() -> None:
    """
    Ensure the macOS Dock is configured with specific applications.
    This function uses 'dockutil' to remove all existing items and add the desired ones.
    """
    log("Ensuring macOS Dock is configured...")

    # Check if dockutil is installed
    result = run_command(["which", "dockutil"], check=False, capture=True)
    if result.returncode != 0:
        warn("dockutil is not installed. Skipping Dock setup.")
        warn("Install it first with: brew install dockutil")
        return

    # Define Dock items to add
    dock_items = [
        "/Applications/Google Chrome.app",
        "/Applications/Visual Studio Code.app",
        "/Applications/iterm.app",
        "/Applications/Intellij IDEA.app",
        "/Applications/System Settings.app",
    ]

    log("Clearing existing Dock items...")
    run_command(
        ["dockutil", "--remove", "all", "--no-restart"], check=False, capture=True
    )

    log(f"Adding {len(dock_items)} items to Dock...")
    for item in dock_items:
        run_command(
            ["dockutil", "--add", item, "--no-restart"], check=False, capture=True
        )

    # Add Downloads folder
    log("Adding Downloads folder to Dock...")
    run_command(
        [
            "dockutil",
            "--add",
            "~/Downloads",
            "--section",
            "others",
            "--view",
            "auto",
            "--display",
            "folder",
            "--no-restart",
        ],
        check=False,
        capture=True,
    )

    # Restart Dock to apply changes
    log("Restarting Dock...")
    run_command(["killall", "Dock"], check=False, capture=True)

    success("Dock setup completed.")
