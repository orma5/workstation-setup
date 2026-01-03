import sys
from utils import log, success, warn, run_command, wait_for_user_confirmation

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
    wait_for_user_confirmation(
        "Press Enter to continue after enabling 1Password CLI integration..."
    )

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
