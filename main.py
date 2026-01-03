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

from utils import log, success, warn

# Import tasks
from tasks.homebrew import ensure_homebrew_applications
from tasks.folders import ensure_folders
from tasks.git import ensure_git_config
from tasks.onepassword import ensure_1password_signin
from tasks.interactive import ensure_interactive_application_setup
from tasks.openvpn import ensure_openvpn_setup
from tasks.aws import ensure_aws_cli_setup
from tasks.ssh import ensure_ssh_config
from tasks.macos import ensure_macos_settings
from tasks.dock import ensure_dock_setup
from tasks.development import ensure_development_projects, ensure_development_environments
from tasks.terminal import ensure_terminal_configuration


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
        ("SSH configuration", ensure_ssh_config),
        ("macOS system settings", ensure_macos_settings),
        ("Dock setup", ensure_dock_setup),
        ("Clone development projects", ensure_development_projects), # use glab
        ("Setup Development environments", ensure_development_environments), # use uv
        ("Configure terminal", ensure_terminal_configuration),
    ]

    failed_steps = []

    for step_name, step_func in steps:
        try:
            log(f"\n{'='*60}")
            log(f"Step: {step_name}")
            log(f"{ '='*60}")
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