# Project: Workstation Setup

## Overview
This project automates the setup of a macOS workstation for development. It ensures a consistent environment by installing applications, configuring system settings, and setting up development tools.

The project has evolved from a monolithic shell script (`setup_mac_for_work.sh`) to a more modular and declarative Python-based approach (`main.py` bootstrapped by `init.sh`).

## Architecture

### 1. Bootstrap (`init.sh`)
The entry point for the setup process.
- **Responsibilities:**
    - Installs Xcode Command Line Tools.
    - Installs Homebrew.
    - Installs `uv` (Python package manager).
    - Downloads the latest project files from GitHub (Production mode) or uses local files (Development mode).
    - Executing `main.py` using `uv`.

### 2. Core Logic (`main.py`)
A Python script that performs the actual setup steps in a declarative and idempotent manner.
- **Key Functions:**
    - `ensure_homebrew_applications()`: Installs apps defined in `config/applications.yaml`.
    - `ensure_folders()`: Creates directory structures defined in `config/folders.yaml`.
    - `ensure_git_config()`: Sets up `.gitconfig` and `.global-gitignore`.
    - `ensure_macos_settings()`: Applies macOS system defaults (dock, finder, input, etc.).
    - `ensure_1password_signin()`: Authenticates with 1Password CLI.
    - **Automated App Setup:** Configures complex apps like OpenVPN and AWS CLI by fetching credentials directly from 1Password.
    - **Interactive App Setup:** Launches GUI apps (Chrome, Slack, etc.) for manual sign-in as defined in `config/application-setup.yaml`.

### 3. Configuration (`config/`)
YAML files that drive the `main.py` script.
- `applications.yaml`: Lists Homebrew casks and formulae to install.
- `folders.yaml`: Lists directories to create.
- `application-setup.yaml`: Defines interactive and automated setup steps for specific applications (including 1Password item IDs).

### 4. Dotfiles (`dotfiles/`)
Contains source files for git configuration (`.gitconfig`, `.global-gitignore`) which are copied to the user's home directory.

## Usage

### Production (Fresh Install)
To run the setup on a new machine, execute the bootstrap script. It will download the latest version of the scripts and config from the GitHub repository.

```bash
./init.sh
```

### Development (Local Changes)
To test changes locally without downloading from GitHub, set the `LOCAL_DEV` environment variable.

```bash
LOCAL_DEV=1 ./init.sh
```

## Legacy
- `setup_mac_for_work.sh`: The original shell-based setup script. It is less structured than the Python implementation and contains manual prompts for many steps. It is preserved likely for reference or fallback.

## Prerequisites
- **OS:** macOS
- **Secrets:** Access to 1Password is required for automated setup of OpenVPN and AWS CLI.
