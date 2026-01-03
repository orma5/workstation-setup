from pathlib import Path
from utils import (
    log, success, warn, run_command, 
    load_applications_config, is_cask_installed, 
    is_formula_installed, PROJECT_ROOT
)

def ensure_homebrew_applications() -> None:
    """
    Ensure all applications from applications.yaml are installed via Homebrew.
    This function is declarative and idempotent - it checks if each app is already
    installed before attempting installation.
    """
    log("Ensuring Homebrew applications are installed...")

    config_path = PROJECT_ROOT / "config" / "applications.yaml"

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
