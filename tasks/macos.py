import sys
from pathlib import Path
from typing import List
from utils import log, success, warn, run_command

def ensure_macos_settings() -> None:
    """
    Ensure macOS system preferences are configured according to best practices.
    This function applies numerous defaults write commands to configure:
    - General system settings
    - Input devices (trackpad, keyboard)
    - Power management
    - Security settings
    - Finder preferences
    - Dock configuration
    - Application-specific settings
    """
    log("Ensuring macOS system settings are configured...")

    # Track failed settings for summary
    failed_settings = []

    def apply_setting(description: str, command: List[str]) -> None:
        """Apply a single macOS setting and log the result."""
        try:
            result = run_command(command, check=False, capture=True)
            if result.returncode == 0:
                success(description)
            else:
                warn(f"{description} - Failed: {result.stderr.strip() if result.stderr else 'Unknown error'}")
                failed_settings.append(description)
        except Exception as e:
            warn(f"{description} - Error: {e}")
            failed_settings.append(description)

    # ========================================
    # GENERAL SYSTEM SETTINGS
    # ========================================
    log("\nConfiguring general system settings...")

    apply_setting(
        "Save to disk (not iCloud) by default",
        ["defaults", "write", "NSGlobalDomain", "NSDocumentSaveNewDocumentsToCloud", "-bool", "false"]
    )

    apply_setting(
        "Automatically quit printer app when jobs complete",
        ["defaults", "write", "com.apple.print.PrintingPrefs", "Quit When Finished", "-bool", "true"]
    )

    apply_setting(
        "Disable 'Are you sure you want to open?' dialog",
        ["defaults", "write", "com.apple.LaunchServices", "LSQuarantine", "-bool", "false"]
    )

    # ========================================
    # TRACKPAD SETTINGS
    # ========================================
    log("\nConfiguring trackpad settings...")

    apply_setting(
        "Enable tap to click (trackpad)",
        ["defaults", "write", "com.apple.driver.AppleBluetoothMultitouch.trackpad", "Clicking", "-bool", "true"]
    )

    apply_setting(
        "Enable tap to click (current user)",
        ["defaults", "-currentHost", "write", "NSGlobalDomain", "com.apple.mouse.tapBehavior", "-int", "1"]
    )

    apply_setting(
        "Enable tap to click (login screen)",
        ["defaults", "write", "NSGlobalDomain", "com.apple.mouse.tapBehavior", "-int", "1"]
    )

    # ========================================
    # BLUETOOTH AUDIO
    # ========================================
    log("\nConfiguring Bluetooth audio quality...")

    apply_setting(
        "Increase Bluetooth audio quality",
        ["defaults", "write", "com.apple.BluetoothAudioAgent", "Apple Bitpool Min (editable)", "-int", "40"]
    )

    # ========================================
    # KEYBOARD SETTINGS
    # ========================================
    log("\nConfiguring keyboard settings...")

    apply_setting(
        "Enable full keyboard access for all controls",
        ["defaults", "write", "NSGlobalDomain", "AppleKeyboardUIMode", "-int", "3"]
    )

    apply_setting(
        "Disable press-and-hold for keys (favor key repeat)",
        ["defaults", "write", "NSGlobalDomain", "ApplePressAndHoldEnabled", "-bool", "false"]
    )

    apply_setting(
        "Set fast keyboard repeat rate",
        ["defaults", "write", "NSGlobalDomain", "KeyRepeat", "-int", "1"]
    )

    apply_setting(
        "Set short initial key repeat delay",
        ["defaults", "write", "NSGlobalDomain", "InitialKeyRepeat", "-int", "10"]
    )

    # Stop iTunes from responding to media keys
    apply_setting(
        "Stop iTunes from responding to media keys",
        ["launchctl", "unload", "-w", "/System/Library/LaunchAgents/com.apple.rcd.plist"]
    )

    # ========================================
    # POWER MANAGEMENT SETTINGS
    # ========================================
    log("\nConfiguring power management settings...")

    apply_setting(
        "Enable lid wakeup",
        ["sudo", "pmset", "-a", "lidwake", "1"]
    )

    apply_setting(
        "Sleep display after 15 minutes",
        ["sudo", "pmset", "-a", "displaysleep", "15"]
    )

    apply_setting(
        "Disable sleep while charging",
        ["sudo", "pmset", "-c", "sleep", "0"]
    )

    apply_setting(
        "Set 5 minute sleep on battery",
        ["sudo", "pmset", "-b", "sleep", "5"]
    )

    apply_setting(
        "Set 24 hour standby delay",
        ["sudo", "pmset", "-a", "standbydelay", "86400"]
    )

    apply_setting(
        "Never go into computer sleep mode",
        ["sudo", "systemsetup", "-setcomputersleep", "Off"]
    )

    apply_setting(
        "Disable hibernation mode",
        ["sudo", "pmset", "-a", "hibernatemode", "0"]
    )

    # Remove sleep image file to save disk space
    log("Removing sleep image file...")
    sleepimage_path = Path("/private/var/vm/sleepimage")
    try:
        # Remove existing file
        if sleepimage_path.exists():
            run_command(["sudo", "rm", str(sleepimage_path)], check=False, capture=True)
        # Create zero-byte file
        run_command(["sudo", "touch", str(sleepimage_path)], check=False, capture=True)
        # Make it immutable
        result = run_command(["sudo", "chflags", "uchg", str(sleepimage_path)], check=False, capture=True)
        if result.returncode == 0:
            success("Sleep image file removed and locked")
        else:
            warn("Could not lock sleep image file")
    except Exception as e:
        warn(f"Error managing sleep image file: {e}")

    # ========================================
    # SECURITY SETTINGS
    # ========================================
    log("\nConfiguring security settings...")

    apply_setting(
        "Require password immediately after sleep/screensaver",
        ["defaults", "write", "com.apple.screensaver", "askForPassword", "-int", "1"]
    )

    apply_setting(
        "No delay for screensaver password",
        ["defaults", "write", "com.apple.screensaver", "askForPasswordDelay", "-int", "0"]
    )

    # ========================================
    # SCREENSHOT SETTINGS
    # ========================================
    log("\nConfiguring screenshot settings...")

    desktop_path = str(Path.home() / "Desktop")
    apply_setting(
        "Save screenshots to Desktop",
        ["defaults", "write", "com.apple.screencapture", "location", "-string", desktop_path]
    )

    apply_setting(
        "Save screenshots in PNG format",
        ["defaults", "write", "com.apple.screencapture", "type", "-string", "png"]
    )

    apply_setting(
        "Disable shadow in screenshots",
        ["defaults", "write", "com.apple.screencapture", "disable-shadow", "-bool", "true"]
    )

    # ========================================
    # DISPLAY SETTINGS
    # ========================================
    log("\nConfiguring display settings...")

    apply_setting(
        "Enable subpixel font rendering on non-Apple LCDs",
        ["defaults", "write", "NSGlobalDomain", "AppleFontSmoothing", "-int", "1"]
    )

    apply_setting(
        "Enable HiDPI display modes",
        ["sudo", "defaults", "write", "/Library/Preferences/com.apple.windowserver", "DisplayResolutionEnabled", "-bool", "true"]
    )

    # ========================================
    # FINDER SETTINGS
    # ========================================
    log("\nConfiguring Finder settings...")

    apply_setting(
        "Allow quitting Finder via Cmd+Q",
        ["defaults", "write", "com.apple.finder", "QuitMenuItem", "-bool", "true"]
    )

    apply_setting(
        "Disable Finder animations",
        ["defaults", "write", "com.apple.finder", "DisableAllAnimations", "-bool", "true"]
    )

    apply_setting(
        "Set Desktop as default location for new Finder windows",
        ["defaults", "write", "com.apple.finder", "NewWindowTarget", "-string", "PfDe"]
    )

    desktop_file_url = f"file://{Path.home()}/Desktop/"
    apply_setting(
        "Set Desktop path for new Finder windows",
        ["defaults", "write", "com.apple.finder", "NewWindowTargetPath", "-string", desktop_file_url]
    )

    apply_setting(
        "Show external hard drives on desktop",
        ["defaults", "write", "com.apple.finder", "ShowExternalHardDrivesOnDesktop", "-bool", "true"]
    )

    apply_setting(
        "Show hard drives on desktop",
        ["defaults", "write", "com.apple.finder", "ShowHardDrivesOnDesktop", "-bool", "true"]
    )

    apply_setting(
        "Show mounted servers on desktop",
        ["defaults", "write", "com.apple.finder", "ShowMountedServersOnDesktop", "-bool", "true"]
    )

    apply_setting(
        "Show removable media on desktop",
        ["defaults", "write", "com.apple.finder", "ShowRemovableMediaOnDesktop", "-bool", "true"]
    )

    apply_setting(
        "Show hidden files in Finder",
        ["defaults", "write", "com.apple.finder", "AppleShowAllFiles", "-bool", "true"]
    )

    apply_setting(
        "Show all filename extensions",
        ["defaults", "write", "NSGlobalDomain", "AppleShowAllExtensions", "-bool", "true"]
    )

    apply_setting(
        "Show Finder status bar",
        ["defaults", "write", "com.apple.finder", "ShowStatusBar", "-bool", "true"]
    )

    apply_setting(
        "Show Finder path bar",
        ["defaults", "write", "com.apple.finder", "ShowPathbar", "-bool", "true"]
    )

    apply_setting(
        "Display full POSIX path in Finder title",
        ["defaults", "write", "com.apple.finder", "_FXShowPosixPathInTitle", "-bool", "true"]
    )

    apply_setting(
        "Keep folders on top when sorting by name",
        ["defaults", "write", "com.apple.finder", "_FXSortFoldersFirst", "-bool", "true"]
    )

    apply_setting(
        "Search current folder by default",
        ["defaults", "write", "com.apple.finder", "FXDefaultSearchScope", "-string", "SCcf"]
    )

    apply_setting(
        "Disable file extension change warning",
        ["defaults", "write", "com.apple.finder", "FXEnableExtensionChangeWarning", "-bool", "false"]
    )

    apply_setting(
        "Enable spring loading for directories",
        ["defaults", "write", "NSGlobalDomain", "com.apple.springing.enabled", "-bool", "true"]
    )

    apply_setting(
        "Remove spring loading delay",
        ["defaults", "write", "NSGlobalDomain", "com.apple.springing.delay", "-float", "0"]
    )

    apply_setting(
        "Avoid creating .DS_Store on network volumes",
        ["defaults", "write", "com.apple.desktopservices", "DSDontWriteNetworkStores", "-bool", "true"]
    )

    apply_setting(
        "Avoid creating .DS_Store on USB volumes",
        ["defaults", "write", "com.apple.desktopservices", "DSDontWriteUSBStores", "-bool", "true"]
    )

    apply_setting(
        "Disable disk image verification",
        ["defaults", "write", "com.apple.frameworks.diskimages", "skip-verify", "-bool", "true"]
    )

    apply_setting(
        "Disable locked disk image verification",
        ["defaults", "write", "com.apple.frameworks.diskimages", "skip-verify-locked", "-bool", "true"]
    )

    apply_setting(
        "Disable remote disk image verification",
        ["defaults", "write", "com.apple.frameworks.diskimages", "skip-verify-remote", "-bool", "true"]
    )

    apply_setting(
        "Auto-open read-only disk images",
        ["defaults", "write", "com.apple.frameworks.diskimages", "auto-open-ro-root", "-bool", "true"]
    )

    apply_setting(
        "Auto-open read-write disk images",
        ["defaults", "write", "com.apple.frameworks.diskimages", "auto-open-rw-root", "-bool", "true"]
    )

    apply_setting(
        "Auto-open Finder for new removable disks",
        ["defaults", "write", "com.apple.finder", "OpenWindowForNewRemovableDisk", "-bool", "true"]
    )

    apply_setting(
        "Use list view in Finder by default",
        ["defaults", "write", "com.apple.finder", "FXPreferredViewStyle", "-string", "Nlsv"]
    )

    apply_setting(
        "Disable empty Trash warning",
        ["defaults", "write", "com.apple.finder", "WarnOnEmptyTrash", "-bool", "false"]
    )

    # Show ~/Library folder
    log("Showing ~/Library folder...")
    library_path = Path.home() / "Library"
    try:
        run_command(["chflags", "nohidden", str(library_path)], check=False, capture=True)
        run_command(["xattr", "-d", "com.apple.FinderInfo", str(library_path)], check=False, capture=True)
        success("~/Library folder is now visible")
    except Exception as e:
        warn(f"Could not show ~/Library folder: {e}")

    # Show /Volumes folder
    apply_setting(
        "Show /Volumes folder",
        ["sudo", "chflags", "nohidden", "/Volumes"]
    )

    # Expand File Info panes
    apply_setting(
        "Expand File Info panes in Finder",
        ["defaults", "write", "com.apple.finder", "FXInfoPanesExpanded", "-dict",
         "General", "-bool", "true",
         "OpenWith", "-bool", "true",
         "Privileges", "-bool", "true"]
    )

    # ========================================
    # DOCK SETTINGS
    # ========================================
    log("\nConfiguring Dock settings...")

    apply_setting(
        "Set Dock icon size to 36 pixels",
        ["defaults", "write", "com.apple.dock", "tilesize", "-int", "36"]
    )

    apply_setting(
        "Minimize windows into application icon",
        ["defaults", "write", "com.apple.dock", "minimize-to-application", "-bool", "true"]
    )

    apply_setting(
        "Show indicator lights for open apps",
        ["defaults", "write", "com.apple.dock", "show-process-indicators", "-bool", "true"]
    )

    apply_setting(
        "Disable Dashboard",
        ["defaults", "write", "com.apple.dashboard", "mcx-disabled", "-bool", "true"]
    )

    apply_setting(
        "Don't show Dashboard as a Space",
        ["defaults", "write", "com.apple.dock", "dashboard-in-overlay", "-bool", "true"]
    )

    apply_setting(
        "Don't automatically rearrange Spaces",
        ["defaults", "write", "com.apple.dock", "mru-spaces", "-bool", "false"]
    )

    apply_setting(
        "Don't show recent applications in Dock",
        ["defaults", "write", "com.apple.dock", "show-recents", "-bool", "false"]
    )

    # ========================================
    # APPLICATION-SPECIFIC SETTINGS
    # ========================================
    log("\nConfiguring application-specific settings...")

    # iTerm2
    apply_setting(
        "Don't prompt when quitting iTerm",
        ["defaults", "write", "com.googlecode.iterm2", "PromptOnQuit", "-bool", "false"]
    )

    # Activity Monitor
    apply_setting(
        "Show main window when launching Activity Monitor",
        ["defaults", "write", "com.apple.ActivityMonitor", "OpenMainWindow", "-bool", "true"]
    )

    apply_setting(
        "Visualize CPU usage in Activity Monitor Dock icon",
        ["defaults", "write", "com.apple.ActivityMonitor", "IconType", "-int", "5"]
    )

    apply_setting(
        "Show all processes in Activity Monitor",
        ["defaults", "write", "com.apple.ActivityMonitor", "ShowCategory", "-int", "0"]
    )

    apply_setting(
        "Sort Activity Monitor by CPU usage",
        ["defaults", "write", "com.apple.ActivityMonitor", "SortColumn", "-string", "CPUUsage"]
    )

    apply_setting(
        "Set Activity Monitor sort direction",
        ["defaults", "write", "com.apple.ActivityMonitor", "SortDirection", "-int", "0"]
    )

    # Disk Utility
    apply_setting(
        "Enable debug menu in Disk Utility",
        ["defaults", "write", "com.apple.DiskUtility", "DUDebugMenuEnabled", "-bool", "true"]
    )

    apply_setting(
        "Enable advanced image options in Disk Utility",
        ["defaults", "write", "com.apple.DiskUtility", "advanced-image-options", "-bool", "true"]
    )

    # Google Chrome
    apply_setting(
        "Disable backswipe navigation in Chrome (trackpad)",
        ["defaults", "write", "com.google.Chrome", "AppleEnableSwipeNavigateWithScrolls", "-bool", "false"]
    )

    apply_setting(
        "Disable backswipe navigation in Chrome Canary (trackpad)",
        ["defaults", "write", "com.google.Chrome.canary", "AppleEnableSwipeNavigateWithScrolls", "-bool", "false"]
    )

    apply_setting(
        "Disable backswipe navigation in Chrome (mouse)",
        ["defaults", "write", "com.google.Chrome", "AppleEnableMouseSwipeNavigateWithScrolls", "-bool", "false"]
    )

    apply_setting(
        "Disable backswipe navigation in Chrome Canary (mouse)",
        ["defaults", "write", "com.google.Chrome.canary", "AppleEnableMouseSwipeNavigateWithScrolls", "-bool", "false"]
    )

    apply_setting(
        "Use system print dialog in Chrome",
        ["defaults", "write", "com.google.Chrome", "DisablePrintPreview", "-bool", "true"]
    )

    apply_setting(
        "Use system print dialog in Chrome Canary",
        ["defaults", "write", "com.google.Chrome.canary", "DisablePrintPreview", "-bool", "true"]
    )

    apply_setting(
        "Expand print dialog in Chrome",
        ["defaults", "write", "com.google.Chrome", "PMPrintingExpandedStateForPrint2", "-bool", "true"]
    )

    apply_setting(
        "Expand print dialog in Chrome Canary",
        ["defaults", "write", "com.google.Chrome.canary", "PMPrintingExpandedStateForPrint2", "-bool", "true"]
    )

    # ========================================
    # INTERACTIVE MANUAL STEPS
    # ========================================
    log("\nMacOS settings have been applied.")

    # Check if running in interactive mode
    if sys.stdin.isatty():
        log("\n" + "="*60)
        log("Manual Configuration Steps")
        log("="*60)
        log("The following settings need to be configured manually:")
        log("  1. Top bar: Add sound, displays, and bluetooth controls")
        log("  2. Desktop background: Set your preferred wallpaper")
        log("")

        response = input("Press Enter when you've completed these manual steps (or 's' to skip): ").strip().lower()
        if response != 's':
            success("Manual configuration steps completed.")
        else:
            warn("Skipped manual configuration steps. You can do these later.")
    else:
        log("\nNote: Some settings need manual configuration:")
        log("  - Top bar: Add sound, displays, and bluetooth controls")
        log("  - Desktop background: Set your preferred wallpaper")

    # ========================================
    # SUMMARY
    # ========================================
    if failed_settings:
        warn(f"\n{len(failed_settings)} settings could not be applied:")
        for setting in failed_settings:
            warn(f"  - {setting}")
        log("\nNote: Some settings may require a logout/restart to take effect.")
        log("You can review and apply failed settings manually if needed.")
    else:
        success("\nAll macOS settings applied successfully!")
        log("Note: Some settings may require a logout/restart to take effect.")

    success("macOS system settings configuration completed.")
