import sys
import os
import re
import subprocess
from pathlib import Path
from utils import log, success, warn, run_command, wait_for_user_confirmation

def ensure_terminal_configuration() -> None:
    """
    Ensure terminal is configured with Oh My Zsh, Powerlevel10k, and fonts/colors.
    """
    log("Ensuring terminal is configured...")

    # Check if running in an interactive terminal
    if not sys.stdin.isatty():
        warn("Not running in an interactive terminal. Skipping terminal configuration.")
        return

    home = Path.home()
    oh_my_zsh_dir = home / ".oh-my-zsh"
    zshrc_path = home / ".zshrc"

    # 1. Install Oh My Zsh
    if oh_my_zsh_dir.exists():
        success("Oh My Zsh is already installed.")
    else:
        log("Installing Oh My Zsh...")
        # RUNZSH=no prevents it from starting zsh; KEEP_ZSHRC=yes prevents backing up existing rc
        install_cmd = 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"'
        # We need to run this with environment variables
        env = os.environ.copy()
        env["RUNZSH"] = "no"
        env["CHSH"] = "no"

        try:
             subprocess.run(install_cmd, shell=True, check=True, env=env)
             success("Oh My Zsh installed.")
        except subprocess.CalledProcessError as e:
            warn(f"Failed to install Oh My Zsh: {e}")

    # 2. Install Powerlevel10k
    p10k_dir = oh_my_zsh_dir / "custom" / "themes" / "powerlevel10k"
    if p10k_dir.exists():
        success("Powerlevel10k is already installed.")
    else:
        log("Installing Powerlevel10k...")
        try:
            run_command(["git", "clone", "--depth=1", "https://github.com/romkatv/powerlevel10k.git", str(p10k_dir)], check=True)
            success("Powerlevel10k installed.")
        except Exception as e:
            warn(f"Failed to install Powerlevel10k: {e}")

    # 3. Configure .zshrc
    log("Configuring .zshrc theme...")
    if zshrc_path.exists():
        try:
            content = zshrc_path.read_text()
            new_theme = 'ZSH_THEME="powerlevel10k/powerlevel10k"'

            # Use regex to find and replace ZSH_THEME line
            if re.search(r'^ZSH_THEME=', content, re.MULTILINE):
                new_content = re.sub(r'^ZSH_THEME=.*', new_theme, content, flags=re.MULTILINE)
                if new_content != content:
                    zshrc_path.write_text(new_content)
                    success("Updated ZSH_THEME in .zshrc")
                else:
                    success("ZSH_THEME already set to Powerlevel10k")
            else:
                # Append if not found
                with open(zshrc_path, "a") as f:
                    f.write(f"\n{new_theme}\n")
                success("Appended ZSH_THEME to .zshrc")
        except Exception as e:
            warn(f"Failed to configure .zshrc: {e}")
    else:
        warn(f"{zshrc_path} not found. Skipping theme configuration.")

    # 4. Download iTerm2 Colors
    log("Downloading iTerm2 color scheme...")
    downloads_dir = home / "Downloads"
    color_scheme_path = downloads_dir / "MaterialDesignColors.itermcolors"

    if not color_scheme_path.exists():
        try:
            run_command(
                [
                    "curl",
                    "-fsSL",
                    "-o",
                    str(color_scheme_path),
                    "https://raw.githubusercontent.com/MartinSeeler/iterm2-material-design/master/material-design-colors.itermcolors",
                ],
                check=True,
            )
            success(f"Downloaded color scheme to {color_scheme_path}")
        except Exception as e:
            warn(f"Failed to download color scheme: {e}")
    else:
        success("Color scheme already downloaded.")

    # 5. Manual Instructions
    log("\n" + "="*60)
    log("Manual Step: Finalize Terminal Setup")
    log("="*60)
    log("1. Open iTerm2.")
    log(f"2. Import the color scheme from: {color_scheme_path}")
    log("   (iTerm2 > Preferences > Profiles > Colors > Color Presets > Import)")
    log("3. Configure fonts (recommended: MesloLGS NF for Powerlevel10k).")
    log("4. Restart iTerm2 to see the changes.")
    log("")

    wait_for_user_confirmation("Press Enter when you've reviewed the manual steps...")
    success("Terminal configuration completed.")
