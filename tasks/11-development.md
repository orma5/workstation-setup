# Task: Development Projects

## Goal
Authenticate `glab` CLI with GitLab using credentials from 1Password, then clone all repositories from the group that have been active in the last 2 years.

## Prerequisites
- Task 04 (1Password) must be complete — MCP server must be responding
- Task 08 (SSH) must be complete — SSH config must be written so git clone via SSH works
- `glab` and `git` must be installed (from task 01-homebrew)
- `~/Development/Projects/` must exist (from task 02-folders)

## Idempotency Check
Check how many repos already exist in `~/Development/Projects/`. If repos are already cloned, ask the user: "Found X repos already cloned. Clone new ones only, re-clone all, or skip?" Default to cloning new ones only (skip directories that already exist).

## Steps
1. Read `config/application-setup.yaml`. Find the entry where `name == "gitlab"`. Note the `onepassword_item_id`.
2. Use the 1Password MCP `get_vault_item` tool with that item ID to fetch the item.
   - If the MCP is unavailable, stop with the hard-fail message (see CLAUDE.md).
3. Extract:
   - Field with label/id `hostname` — the GitLab hostname
   - Field with label/id `access_token` — the GitLab personal access token
4. Authenticate `glab`:
   ```bash
   glab auth login --hostname "<hostname>" --token "<access_token>" -a "<hostname>" -p http -g ssh
   ```
   If authentication fails, warn and stop this task.
5. Set the default `glab` host:
   ```bash
   glab config -g set host "<hostname>"
   ```
6. Fetch repository list (group `bo`, up to 100 results, JSON format):
   ```bash
   glab repo list -a -g bo -P 100 -F json
   ```
   Parse the JSON output to get repo names, SSH URLs, and last activity timestamps.
7. Filter to repos with `last_activity_at` within the last 2 years (cutoff = today minus 730 days).
8. For each active repo:
   - Target directory: `~/Development/Projects/<repo-name>`
   - If directory already exists: log "skipping (already exists)"
   - If not: `git clone <ssh_url> ~/Development/Projects/<repo-name>`
   - If clone fails: warn with the error and continue
9. Report summary: X cloned, Y skipped (already existed), Z inactive (filtered out), W failed.

## Completion Criteria
- `glab auth status` succeeds.
- New repos from the last 2 years are cloned to `~/Development/Projects/`.
- Summary is reported to the user.
