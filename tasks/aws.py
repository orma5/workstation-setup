import sys
import json
from pathlib import Path
from utils import (
    log, success, warn, error_exit, run_command, 
    load_interactive_apps_config, PROJECT_ROOT
)

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

    config_path = PROJECT_ROOT / "config" / "application-setup.yaml"

    # Load configuration
    interactive_apps = load_interactive_apps_config(config_path)

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
