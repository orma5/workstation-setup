#!/bin/bash
set -euo pipefail

# ========================================
# macOS Workstation Setup Bootstrap Script
# ========================================
#
# This script bootstraps a fresh Mac to the point where Claude Code
# can take over and run the interactive setup agent.
#
# What this script does:
#   1. Installs Xcode Command Line Tools and Homebrew
#   2. Installs Node (required for MCP server runtime)
#   3. Installs Claude Code
#   4. Clones this repo from GitHub
#   5. Registers the 1Password MCP server at user scope
#   6. Prints instructions to start the agent
#
# Usage:
#   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/orma5/workstation-setup/main/init.sh)"
#
# ========================================
# CONFIG
# ========================================

GITHUB_REPO="orma5/workstation-setup"
GITHUB_BRANCH="main"
REPO_URL="https://github.com/${GITHUB_REPO}.git"
REPO_DIR="${HOME}/workstation-setup"

# ========================================
# UTILITIES
# ========================================

log()        { echo -e "\033[1;34m[INFO]\033[0m $1"; }
warn()       { echo -e "\033[1;33m[WARN]\033[0m $1"; }
success()    { echo -e "\033[1;32m[DONE]\033[0m $1"; }
error_exit() { echo -e "\033[1;31m[ERROR]\033[0m $1"; exit 1; }

require_sudo() {
    sudo -v
    # Keep sudo alive while script runs; cleaned up on EXIT
    while true; do sudo -n true; sleep 60; done 2>/dev/null &
    SUDO_KEEPALIVE_PID=$!
    trap 'kill "${SUDO_KEEPALIVE_PID}" 2>/dev/null || true' EXIT
}

# ========================================
# STEPS
# ========================================

ensure_xcode_and_homebrew() {
    log "Ensuring Xcode Command Line Tools and Homebrew are installed..."

    if ! xcode-select -p &>/dev/null; then
        log "Installing Xcode Command Line Tools..."
        xcode-select --install || true
        log "Waiting for Xcode CLT installation to complete..."
        until xcode-select -p &>/dev/null; do sleep 20; done
        success "Xcode Command Line Tools installed."
    else
        success "Xcode Command Line Tools already installed."
    fi

    if ! command -v brew &>/dev/null; then
        log "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Detect install path (Apple Silicon vs Intel)
        if [[ -f /opt/homebrew/bin/brew ]]; then
            BREW_BIN="/opt/homebrew/bin/brew"
        elif [[ -f /usr/local/bin/brew ]]; then
            BREW_BIN="/usr/local/bin/brew"
        else
            error_exit "Could not find brew after installation."
        fi

        eval "$("${BREW_BIN}" shellenv)"

        # Add to shell profile if not already present
        if ! grep -q 'brew shellenv' "${HOME}/.zprofile" 2>/dev/null; then
            echo "eval \"\$(${BREW_BIN} shellenv)\"" >> "${HOME}/.zprofile"
        fi

        success "Homebrew installed."
    else
        success "Homebrew already installed."
    fi
}

ensure_node() {
    log "Ensuring Node is installed (required for 1Password MCP server)..."
    if ! command -v node &>/dev/null; then
        brew install node
        success "Node installed."
    else
        success "Node already installed."
    fi
}

ensure_claude_code() {
    log "Ensuring Claude Code is installed..."
    if ! command -v claude &>/dev/null; then
        brew install --cask claude-code
        success "Claude Code installed."
    else
        success "Claude Code already installed."
    fi
}

clone_repo() {
    log "Cloning workstation-setup repo..."
    if [[ -d "${REPO_DIR}" ]]; then
        log "Repo already cloned at ${REPO_DIR}. Pulling latest..."
        git -C "${REPO_DIR}" pull --ff-only || warn "Could not update repo. Continuing with existing files."
    else
        git clone "${REPO_URL}" "${REPO_DIR}"
        success "Repo cloned to ${REPO_DIR}."
    fi
}

configure_mcp() {
    log "Registering 1Password MCP server (user scope)..."

    # Check if already registered
    if claude mcp list 2>/dev/null | grep -q "1password"; then
        success "1Password MCP server already registered."
        return
    fi

    claude mcp add --scope user 1password -- npx -y @1password/mcp-server
    success "1Password MCP server registered."
}

print_handoff() {
    echo ""
    echo -e "\033[1;32m============================================\033[0m"
    echo -e "\033[1;32m  Bootstrap complete!\033[0m"
    echo -e "\033[1;32m============================================\033[0m"
    echo ""
    echo "Before running the agent, make sure:"
    echo "  1. The 1Password desktop app is open and signed in"
    echo "  2. 1Password Settings > Developer > 'Integrate with 1Password CLI' is ENABLED"
    echo ""
    echo "Then start the setup agent:"
    echo ""
    echo -e "  \033[1;34mcd ${REPO_DIR} && claude\033[0m"
    echo ""
    echo "Claude will guide you through the rest of the Mac setup."
    echo ""
}

# ========================================
# MAIN
# ========================================

main() {
    log "Starting macOS workstation setup bootstrap..."

    require_sudo
    ensure_xcode_and_homebrew
    ensure_node
    ensure_claude_code
    clone_repo
    configure_mcp
    print_handoff
}

main "$@"
