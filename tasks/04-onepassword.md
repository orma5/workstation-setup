# Task: 1Password CLI Integration

## Goal
Verify that the 1Password desktop app CLI integration is active and the MCP server is reachable, so all subsequent secret-fetching tasks can proceed.

## Prerequisites
- 1Password cask must be installed (from task 01-homebrew)
- 1Password desktop app must be open and signed in

## Idempotency Check
Attempt a test call to the 1Password MCP server (e.g., list vaults). If it responds successfully, the integration is already working — report success and skip the setup steps.

## Steps
1. Check that the 1Password app is installed: `mdfind "kMDItemKind == 'Application'" -name "1Password.app"`. If not found, tell the user to install it from `brew install --cask 1password` or re-run task 01.
2. Ask the user to open the 1Password desktop app and sign in if they haven't already.
3. Guide the user to enable CLI integration:
   - Open 1Password
   - Go to **Settings > Developer**
   - Enable **"Integrate with 1Password CLI"**
   - Click **"Set Up SSH Agent"** if prompted
4. Once the user confirms they've enabled it, attempt the MCP test call again.
5. If the MCP server responds, report success: "1Password CLI integration is active."
6. If it still does not respond, stop and display the hard-fail message:
   > "The 1Password MCP server is not responding. Please ensure: (1) the 1Password desktop app is open, (2) Settings > Developer > 'Integrate with 1Password CLI' is enabled. Then restart this Claude session and re-run this task."

## Completion Criteria
- The 1Password MCP server responds to a test call (e.g., list vaults returns without error).
- Do not proceed to Phase 3 tasks until this task passes.
