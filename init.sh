#!/bin/bash
set -euo pipefail

# ========================================
# CONFIG
# ========================================

GITHUB_REPO="orma5/workstation-setup"
GITHUB_BRANCH="main"
GITHUB_RAW_BASE="https://github.com/$GITHUB_REPO/$GITHUB_BRANCH"
TEMP_DIR="/tmp/workstation-setup"
PYTHON_SCRIPT_PATH="$TEMP_DIR/main.py"
UV_LOCAL_BIN="$HOME/.local/bin"

# ========================================
# UTILITIES
# ========================================

log() { echo -e "\033[1;34m[INFO]\033[0m $1"; }
warn() { echo -e "\033[1;33m[WARN]\033[0m $1"; }
success() { echo -e "\033[1;32m[DONE]\033[0m $1"; }
error_exit() { echo -e "\033[1;31m[ERROR]\033[0m $1"; exit 1; }

require_sudo() {
    sudo -v
    # Keep sudo alive while script runs
    while true; do sudo -n true; sleep 60; done 2>/dev/null &
}

update_path_for_uv() {
    if [[ ":$PATH:" != *":$UV_LOCAL_BIN:"* ]]; then
        log "Adding uv Python binaries to PATH..."
        echo "export PATH=\"$UV_LOCAL_BIN:\$PATH\"" >> ~/.zprofile
        export PATH="$UV_LOCAL_BIN:$PATH"
        success "PATH updated for uv Python."
    fi
}

download_file() {
    local url="$1"
    local destination="$2"

    log "Downloading $(basename "$destination")..."
    if curl -fsSL "$url" -o "$destination"; then
        success "Downloaded $(basename "$destination")."
        return 0
    else
        error_exit "Failed to download from $url"
    fi
}

download_setup_files() {
    log "Downloading setup files from GitHub..."

    # Create temp directory structure
    mkdir -p "$TEMP_DIR/config"
    mkdir -p "$TEMP_DIR/dotfiles"

    # Download main.py
    download_file "$GITHUB_RAW_BASE/main.py" "$TEMP_DIR/main.py"

    # Download config files
    download_file "$GITHUB_RAW_BASE/config/applications.yaml" "$TEMP_DIR/config/applications.yaml"
    download_file "$GITHUB_RAW_BASE/config/folders.yaml" "$TEMP_DIR/config/folders.yaml"

    # Download dotfiles
    download_file "$GITHUB_RAW_BASE/dotfiles/.gitconfig" "$TEMP_DIR/dotfiles/.gitconfig"
    download_file "$GITHUB_RAW_BASE/dotfiles/.global-gitignore" "$TEMP_DIR/dotfiles/.global-gitignore"

    success "All setup files downloaded successfully."
}

# ========================================
# DECLARATIVE STEPS
# ========================================

ensure_xcode_and_homebrew() {
    log "Ensuring Xcode Command Line Tools and Homebrew are installed..."

    # Check Xcode CLT
    if ! xcode-select -p &>/dev/null; then
        log "Installing Xcode Command Line Tools..."
        xcode-select --install || true
        log "Waiting for user to finish Xcode installation..."
        until xcode-select -p &>/dev/null; do sleep 20; done
        success "Xcode Command Line Tools installed."
    else
        success "Xcode Command Line Tools already installed."
    fi

    # Check Homebrew
    if ! command -v brew &>/dev/null; then
        log "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
        success "Homebrew installed."
    else
        success "Homebrew already installed."
    fi
}

ensure_uv_and_python() {
    log "Ensuring uv and latest stable Python are installed..."

    # Install uv if missing
    if ! command -v uv &>/dev/null; then
        log "Installing uv via Homebrew..."
        brew install uv
        success "uv installed."
    else
        success "uv already installed."
    fi

    # Ensure uv Python PATH
    update_path_for_uv

    # Install latest Python (idempotent - does nothing if already installed)
    log "Ensuring latest Python is installed..."
    local output
    output=$(uv python install 2>&1 || true)

    # Filter out the "already installed" message and show appropriate feedback
    if echo "$output" | grep -q "Python is already installed"; then
        success "Latest stable Python already installed."
    elif echo "$output" | grep -q "Installed Python"; then
        success "Latest stable Python installed."
    else
        success "Python is ready."
    fi
}

run_python_setup() {
    log "Running Python setup helper via uv..."
    uv run "$PYTHON_SCRIPT_PATH"
    success "Python setup helper completed."
}

# ========================================
# MAIN
# ========================================

main() {
    log "Starting initial Mac setup bootstrap..."
    require_sudo

    ensure_xcode_and_homebrew
    ensure_uv_and_python
    download_setup_files
    run_python_setup

    success "All bootstrap steps completed successfully!"
}

main "$@"
