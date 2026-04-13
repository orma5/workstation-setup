# Task: Dock Configuration

## Goal
Clear existing Dock items and configure the Dock with a specific set of apps and the Downloads folder.

## Prerequisites
- `dockutil` must be installed (from task 01-homebrew)
- Apps to be added should be installed (from task 01-homebrew)

## Idempotency Check
Run `dockutil --list` to see current Dock contents. If the Dock already contains exactly the expected apps (Chrome, VS Code, iTerm, IntelliJ, System Settings, Downloads), ask the user: "Dock is already configured. Reconfigure anyway?" Skip if user says no.

## Steps
1. Verify `dockutil` is installed: `which dockutil`. If not found, warn and skip.
2. Remove all existing Dock items:
   ```bash
   dockutil --remove all --no-restart
   ```
3. Add apps in order:
   ```bash
   dockutil --add "/Applications/Google Chrome.app" --no-restart
   dockutil --add "/Applications/Visual Studio Code.app" --no-restart
   dockutil --add "/Applications/iTerm.app" --no-restart
   dockutil --add "/Applications/IntelliJ IDEA.app" --no-restart
   dockutil --add "/Applications/System Settings.app" --no-restart
   ```
4. Add the Downloads folder to the right side:
   ```bash
   dockutil --add "~/Downloads" --section others --view auto --display folder --no-restart
   ```
5. Restart the Dock to apply changes:
   ```bash
   killall Dock
   ```

If any app path doesn't exist, warn and skip that item (don't abort the whole task).

## Completion Criteria
- `dockutil --list` shows the 5 apps and Downloads folder.
- The Dock has restarted (brief visual flicker is expected).
