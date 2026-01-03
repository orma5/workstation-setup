import sys
import json
import os
import re
from pathlib import Path
from utils import (
    log, success, warn, error_exit, run_command, 
    load_interactive_apps_config, wait_for_user_confirmation, PROJECT_ROOT
)

def ensure_ssh_config() -> None:
    """
    Ensure SSH configuration is set up.
    1. Create ~/.ssh folder if not exists (0700).
    2. Fetch config content from 1Password (notesPlain).
    3. Create ~/.ssh/config with content (0600).
    4. Ask user to enable SSH agent in 1Password.
    """
    log("Ensuring SSH configuration is set up...")

    # Check if running in an interactive terminal
    if not sys.stdin.isatty():
        warn("Not running in an interactive terminal. Skipping SSH setup.")
        warn("To set up SSH, run this script directly: uv run main.py")
        return

    config_path = PROJECT_ROOT / "config" / "application-setup.yaml"

    # Load configuration
    interactive_apps = load_interactive_apps_config(config_path)

    # Find SSH configuration
    ssh_config = None
    for app in interactive_apps:
        if app.get("name") == "ssh configuration":
            ssh_config = app
            break

    if not ssh_config:
        warn("SSH configuration not found in application-setup.yaml. Skipping.")
        return

    onepassword_item_id = ssh_config.get("onepassword_item_id")
    if not onepassword_item_id:
        warn(
            "SSH configuration in application-setup.yaml is missing onepassword_item_id. Skipping."
        )
        return

    # Check if 1Password CLI is available and authenticated
    result = run_command(["which", "op"], check=False, capture=True)
    if result.returncode != 0:
        warn("1Password CLI (op) is not installed. Cannot fetch SSH config.")
        warn("Install 1password-cli via Homebrew and sign in first.")
        return

    # Verify 1Password CLI is authenticated
    whoami_result = run_command(["op", "whoami"], check=False, capture=True)
    if whoami_result.returncode != 0:
        warn("1Password CLI is not authenticated. Please sign in first with: op signin")
        return

    log("\n" + "=" * 60)
    log("Setting up: SSH Configuration")
    log("=" * 60)

    # Fetch credentials from 1Password
    log("\nStep 1: Fetching SSH config from 1Password...")
    log("-" * 40)

    ssh_config_content = ""
    try:
        # Fetch the item in JSON format
        result = run_command(
            ["op", "item", "get", onepassword_item_id, "--format", "json"],
            check=True,
            capture=True,
        )

        if result.returncode == 0:
            success("Successfully fetched SSH config item from 1Password")

            # Parse JSON to extract notesPlain
            item_data = json.loads(result.stdout)

            # Search in fields
            found = False
            for field in item_data.get("fields", []):
                if (
                    field.get("id") == "notesPlain"
                    or field.get("label") == "notesPlain"
                ):
                    ssh_config_content = field.get("value", "")
                    found = True
                    break

            if not found:
                warn("Could not find 'notesPlain' field in the 1Password item.")
                return

            if not ssh_config_content:
                warn("SSH config content (notesPlain) is empty.")
                return

            log("SSH config content extracted successfully.")
        else:
            warn(f"Failed to fetch item from 1Password: {result.stderr}")
            return
    except json.JSONDecodeError as e:
        warn(f"Failed to parse 1Password JSON response: {e}")
        return
    except Exception as e:
        warn(f"Error fetching item from 1Password: {e}")
        return

    # Setup SSH files
    log("\nStep 2: Setting up ~/.ssh files...")
    log("-" * 40)

    ssh_dir = Path.home() / ".ssh"
    config_file = ssh_dir / "config"

    try:
        # Create directory if it doesn't exist
        if not ssh_dir.exists():
            log(f"Creating {ssh_dir}...")
            ssh_dir.mkdir(parents=True, exist_ok=True)

        # Set directory permissions to 0700 (rwx------)
        os.chmod(ssh_dir, 0o700)
        success(f"Ensured {ssh_dir} has 0700 permissions.")

        # Write config file
        log(f"Writing SSH config to {config_file}...")
        with open(config_file, "w") as f:
            f.write(ssh_config_content)

        # Set file permissions to 0600 (rw-------)
        os.chmod(config_file, 0o600)
        success("Written SSH config and ensured 0600 permissions.")

    except Exception as e:
        warn(f"Failed to setup SSH files: {e}")
        return

    # Fetch SSH keys and configure 1Password SSH Agent
    log("\nStep 3: Configure 1Password SSH Agent keys...")
    log("-" * 40)

    # Create 1Password config directory
    op_ssh_dir = Path.home() / ".config" / "1password" / "ssh"
    try:
        if not op_ssh_dir.exists():
            log(f"Creating {op_ssh_dir}...")
            op_ssh_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        warn(f"Failed to create directory {op_ssh_dir}: {e}")

    agent_toml_lines = []

    # Fetch all SSH keys
    log("Fetching list of SSH keys from 1Password...")
    result = run_command(
        ["op", "item", "list", "--categories", "SSH Key", "--format", "json"],
        check=False,
        capture=True,
    )

    if result.returncode != 0:
        warn(f"Failed to list SSH keys: {result.stderr}")
    else:
        try:
            items = json.loads(result.stdout)
            log(f"Found {len(items)} SSH keys. Processing...")

            for item in items:
                item_id = item.get("id")
                vault_id = item.get("vault", {}).get("id")
                title = item.get("title", "untitled")

                if not item_id or not vault_id:
                    continue

                # Add to agent.toml content
                agent_toml_lines.append(f"[[ssh-keys]]")
                agent_toml_lines.append(f'item = "{item_id}"')
                agent_toml_lines.append(f'vault = "{vault_id}"')
                agent_toml_lines.append("")

                # Fetch full item details to get public key
                detail_result = run_command(
                    ["op", "item", "get", item_id, "--format", "json"],
                    check=False,
                    capture=True,
                )

                if detail_result.returncode == 0:
                    try:
                        details = json.loads(detail_result.stdout)
                        public_key = None

                        # Look for public key field
                        for field in details.get("fields", []):
                            if (
                                field.get("label") == "public key"
                                or field.get("id") == "public_key"
                            ):
                                public_key = field.get("value")
                                break

                        if public_key:
                            # Sanitize filename: replace unsafe chars with underscore
                            safe_title = re.sub(r'[\\/:*?"<>|]', "_", title)
                            pub_key_path = ssh_dir / f"{safe_title}.pub"

                            try:
                                with open(pub_key_path, "w") as f:
                                    f.write(public_key)
                                os.chmod(pub_key_path, 0o644)
                                # success(f"Saved {safe_title}.pub") # Optional: reduce verbosity
                            except Exception as e:
                                warn(f"Failed to save public key for '{title}': {e}")
                    except Exception:
                        pass  # specific warnings handled by loop flow or ignored to reduce noise

            # Write agent.toml
            if agent_toml_lines:
                agent_toml_path = op_ssh_dir / "agent.toml"
                try:
                    with open(agent_toml_path, "w") as f:
                        f.write("\n".join(agent_toml_lines))
                    success(f"Generated {agent_toml_path} with {len(items)} keys.")
                except Exception as e:
                    warn(f"Failed to write agent.toml: {e}")

        except json.JSONDecodeError:
            warn("Failed to parse SSH key list from 1Password.")

    # Prompt user for 1Password SSH Agent
    log("\nStep 4: Enable SSH Agent in 1Password...")
    log("-" * 40)
    log(
        "To complete the SSH setup, you need to enable the SSH Agent in the 1Password application."
    )
    log("1. Open 1Password Settings")
    log("2. Go to Developer > SSH Agent")
    log("3. Check 'Use the SSH Agent'")
    log("")

    wait_for_user_confirmation(
        "Press Enter when you have enabled the SSH Agent in 1Password..."
    )
    success("SSH configuration setup completed!")
