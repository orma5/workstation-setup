import sys
from pathlib import Path
from utils import log, success, warn, error_exit, run_command, PROJECT_ROOT

def ensure_git_config() -> None:
    """
    Ensure git configuration files are installed and git user is configured.
    This function is declarative and idempotent - it checks if files and config
    already exist before prompting or copying.
    """
    log("Ensuring git configuration is set up...")

    dotfiles_dir = PROJECT_ROOT / "dotfiles"

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
