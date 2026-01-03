import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from utils import (
    log, success, warn, error_exit, run_command, 
    load_interactive_apps_config, wait_for_user_confirmation, PROJECT_ROOT
)

def ensure_development_projects() -> None:
    """
    Ensure development projects are cloned from GitLab.
    1. Fetches GitLab credentials from 1Password.
    2. Authenticates glab CLI (automating SSH protocol selection).
    3. Lists repositories from the 'bo' group.
    4. Clones projects active in the last 2 years to ~/Development/Projects/.
    """
    log("Ensuring development projects are cloned...")

    # Check if glab is installed
    result = run_command(["which", "glab"], check=False, capture=True)
    if result.returncode != 0:
        warn("glab CLI is not installed. Skipping project cloning.")
        warn("Install it first with: brew install glab")
        return

    # Check if 1Password CLI is available
    result = run_command(["which", "op"], check=False, capture=True)
    if result.returncode != 0:
        warn("1Password CLI (op) is not installed. Cannot fetch GitLab credentials.")
        return

    # Verify 1Password CLI is authenticated
    whoami_result = run_command(["op", "whoami"], check=False, capture=True)
    if whoami_result.returncode != 0:
        warn("1Password CLI is not authenticated. Please sign in first with: op signin")
        return

    config_path = PROJECT_ROOT / "config" / "application-setup.yaml"

    # Load configuration
    interactive_apps = load_interactive_apps_config(config_path)

    # Find GitLab configuration
    gitlab_config = None
    for app in interactive_apps:
        if app.get("name") == "gitlab":
            gitlab_config = app
            break

    if not gitlab_config:
        warn("GitLab configuration not found in application-setup.yaml. Skipping.")
        return

    onepassword_item_id = gitlab_config.get("onepassword_item_id")
    if not onepassword_item_id:
        warn("GitLab item ID not found in configuration.")
        return

    log("\n" + "="*60)
    log("Setting up: Development Projects (GitLab)")
    log("="*60)

    # Fetch credentials from 1Password
    log("\nStep 1: Fetching GitLab credentials from 1Password...")
    hostname = None
    access_token = None

    try:
        result = run_command(
            ["op", "item", "get", onepassword_item_id, "--format", "json"],
            check=True,
            capture=True,
        )
        item_data = json.loads(result.stdout)

        for field in item_data.get("fields", []):
            field_label = field.get("label", "").lower()
            field_id = field.get("id", "").lower()
            field_value = field.get("value", "")

            if field_label == "hostname" or field_id == "hostname":
                hostname = field_value
            elif field_label == "access_token" or field_id == "access_token":
                access_token = field_value

        if not hostname or not access_token:
            warn(
                "Could not find 'hostname' or 'access_token' fields in 1Password item."
            )
            return

        success("GitLab credentials fetched.")

    except Exception as e:
        warn(f"Failed to fetch credentials: {e}")
        return

    # Authenticate glab
    log("\nStep 2: Authenticating glab CLI...")
    try:
        # glab auth login --hostname <hostname> -a <hostname> -p http -g ssh -t <access_token>
        auth_cmd = run_command(
            [
                "glab",
                "auth",
                "login",
                "--hostname",
                hostname,
                "--token",
                access_token,
                "-a",
                hostname,
                "-p",
                "http",
                "-g",
                "ssh",
            ],
            capture=True,
            check=False,
        )

        if auth_cmd.returncode == 0:
            success(f"Authenticated with {hostname}")
        else:
            warn(f"Failed to authenticate glab: {auth_cmd.stderr}")
            return
    except Exception as e:
        warn(f"Error during glab authentication: {e}")
        return

    # Fetch repos
    log("\nStep 3: Fetching repository list...")
    repos = []
    try:
        # configure glab to use hostname as host
        run_command(
            ["glab", "config", "-g", "set", "host", hostname],
            check=True,
            capture=False,
        )

        # glab repo list -a -g bo -P 100 -F json
        result = run_command(
            ["glab", "repo", "list", "-a", "-g", "bo", "-P", "100", "-F", "json"],
            check=True,
            capture=True,
        )
        repos = json.loads(result.stdout)
        success(f"Fetched {len(repos)} repositories.")
    except Exception as e:
        warn(f"Failed to fetch repositories: {e}")
        return

    # Clone repos
    log("\nStep 4: Cloning active repositories (last 2 years)...")
    projects_dir = Path.home() / "Development" / "Projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    # Calculate cutoff date (2 years ago)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=365 * 2)

    count_cloned = 0
    count_skipped = 0
    count_inactive = 0

    for repo in repos:
        name = repo.get("name")
        ssh_url = repo.get("ssh_url_to_repo")
        last_activity_str = repo.get("last_activity_at")

        if not name or not ssh_url or not last_activity_str:
            continue

        try:
            # Parse date (handle 'Z' if present for UTC)
            if last_activity_str.endswith("Z"):
                last_activity_str = last_activity_str[:-1] + "+00:00"
            last_activity = datetime.fromisoformat(last_activity_str)

            if last_activity < cutoff_date:
                count_inactive += 1
                continue

            target_dir = projects_dir / name

            if target_dir.exists():
                log(f"Skipping {name} (already exists)")
                count_skipped += 1
            else:
                log(f"Cloning {name}...")
                clone_result = run_command(
                    ["git", "clone", ssh_url, str(target_dir)],
                    check=False,
                    capture=True,
                )
                if clone_result.returncode == 0:
                    success(f"Cloned {name}")
                    count_cloned += 1
                else:
                    warn(f"Failed to clone {name}: {clone_result.stderr}")

        except ValueError as e:
            warn(f"Error parsing date for {name}: {e}")
            continue

    success(
        f"Clone process completed: {count_cloned} cloned, {count_skipped} skipped, {count_inactive} inactive ignored."
    )


def ensure_development_environments() -> None:
    """
    Ensure Development environments are set up.
    This is a manual placeholder function that prompts the user to perform the step.
    """
    log("Ensuring Development environments are set up...")

    # Check if running in an interactive terminal
    if not sys.stdin.isatty():
        warn(
            "Not running in an interactive terminal. Skipping Development environments setup."
        )
        warn("Please set up your Development environments manually.")
        return

    log("\n" + "="*60)
    log("Manual Step: Setup Development Environments")
    log("="*60)
    log("Please set up your Development environments for your projects.")
    log(
        "This may include installing SDKs, configuring IDEs, setting up virtual environments, etc."
    )
    log("Refer to your project documentation for specific requirements.")
    log("")
    # Wait for user to complete the manual step
    wait_for_user_confirmation(
        "Press Enter when you've set up all Development environments..."
    )
    success("Development environments setup completed.")
