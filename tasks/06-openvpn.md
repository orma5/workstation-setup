# Task: OpenVPN Configuration

## Goal
Fetch VPN credentials and profile URL from 1Password, download the OpenVPN profile, and guide the user to import it into OpenVPN Connect.

## Prerequisites
- Task 04 (1Password) must be complete — MCP server must be responding
- OpenVPN Connect must be installed (from task 01-homebrew)

## Idempotency Check
Ask the user: "Have you already imported your OpenVPN profile?" If yes, skip.

## Steps
1. Read `config/application-setup.yaml`. Find the entry where `name == "openvpn-connect"`. Note the `onepassword_item_id`.
2. Use the 1Password MCP `get_vault_item` tool with that item ID to fetch the item.
   - If the MCP is unavailable, stop with the hard-fail message (see CLAUDE.md).
3. Extract the following fields from the item:
   - Field with label/id `username` — the VPN username
   - Field with label/id `password` — the VPN password
   - Field with label/id `target` or similar — the profile download URL
4. Download the profile:
   ```
   wget --user="<username>" --password="<password>" -O ~/Downloads/openvpn-profile.ovpn "<profile_url>"
   ```
   Verify the downloaded file is non-empty.
5. Open OpenVPN Connect: `open -a "OpenVPN Connect"`
6. Tell the user: "Please import the OpenVPN profile from ~/Downloads/openvpn-profile.ovpn. In OpenVPN Connect: File > Import > From File."
7. Wait for user confirmation that the profile has been imported.

## Completion Criteria
- `~/Downloads/openvpn-profile.ovpn` exists and is non-empty.
- User has confirmed the profile was imported into OpenVPN Connect.
