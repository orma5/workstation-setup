# Task: Interactive App Setup

## Goal
Launch each GUI application that requires manual sign-in or configuration, and wait for the user to complete each one before moving on.

## Prerequisites
- Apps must be installed (task 01-homebrew)
- Running in an interactive terminal session

## Idempotency Check
For each app, check if it's already been set up by asking the user: "Have you already signed in to [App Name]?" If yes, skip it.

## Steps
Read `config/application-setup.yaml`. For each entry in `interactive_apps` where there is **no** `type: automated` field, work through them one at a time:

1. **Google Chrome** (`bundle_id: com.google.Chrome`)
   - Open: `open -a "Google Chrome"`
   - Tell the user: "Please sign in to your Google account and sync your settings (bookmarks, extensions, etc.)."
   - Wait for user confirmation before continuing.

2. **IntelliJ IDEA** (`bundle_id: com.jetbrains.intellij`)
   - Open: `open -a "IntelliJ IDEA"`
   - Tell the user: "Please activate your licence, install your preferred theme, and set your keymap."
   - Wait for user confirmation before continuing.

3. **Visual Studio Code** (`bundle_id: com.microsoft.VSCode`)
   - Open: `open -a "Visual Studio Code"`
   - Tell the user: "Please sync your profiles (Settings Sync > Sign In)."
   - Wait for user confirmation before continuing.

4. **Windows App** (`bundle_id: com.microsoft.rdc.macos`)
   - Open: `open -a "Windows App"`
   - Tell the user: "Please add your remote desktops."
   - Wait for user confirmation before continuing.

5. **Slack** (`bundle_id: com.tinyspeck.slackmacgap`)
   - Open: `open -a "Slack"`
   - Tell the user: "Please sign in to your workspace(s)."
   - Wait for user confirmation before continuing.

If an app is not installed (not found by `mdfind`), warn and skip it.

## Completion Criteria
- User has confirmed completion (or skip) for each app in the list.
