# Workstation Setup — Agent Run-Book

You are a Claude Code agent executing a macOS workstation setup. Read this file first, then work through the task checklist below. Use your built-in tools (Bash, Read, Write, Edit) and the 1Password MCP server to execute each task.

## Before You Start

Confirm the following with the user before proceeding:
- [ ] 1Password desktop app is installed and signed in
- [ ] 1Password Settings > Developer > "Integrate with 1Password CLI" is **enabled**
- [ ] Connected to the internet
- [ ] Running on a Mac with admin privileges (sudo available)

If 1Password CLI integration is not yet enabled, stop and walk the user through enabling it before proceeding to any 1Password-dependent tasks.

## How to Run

When the user runs `claude` in this directory, read this file and begin executing tasks in phase order. Check each task's idempotency instructions before running — skip or ask the user about tasks that appear already complete.

At the end of each phase, report what succeeded, what was skipped, and what failed before moving on.

## Repo Layout

```
config/
  applications.yaml       — Homebrew casks and formulae to install
  folders.yaml            — directories to create under ~/
  application-setup.yaml  — 1Password item IDs and app metadata
dotfiles/
  .gitconfig              — git config template
  .global-gitignore       — global gitignore template
tasks/
  01-homebrew.md          — install Homebrew packages
  02-folders.md           — create development directories
  03-git.md               — configure git identity and dotfiles
  04-onepassword.md       — verify 1Password CLI integration
  05-interactive-apps.md  — launch apps for manual sign-in
  06-openvpn.md           — configure OpenVPN
  07-aws.md               — configure AWS CLI and kubectl
  08-ssh.md               — write SSH config and agent.toml
  09-macos.md             — apply macOS system defaults
  10-dock.md              — configure Dock
  11-development.md       — clone GitLab repositories
  12-terminal.md          — install Oh My Zsh, Powerlevel10k, iTerm2 theme
```

## Setup Checklist

Work through tasks in phase order. Read each task file before executing it. Mark tasks complete as you go using `[x]`. If a task fails, note the error, mark it `[!]`, and continue to the next task.

### Phase 1 — No dependencies (run in parallel)
- [ ] `tasks/01-homebrew.md`
- [ ] `tasks/02-folders.md`
- [ ] `tasks/09-macos.md`
- [ ] `tasks/10-dock.md`

### Phase 2 — Sequential (requires Phase 1 complete)
- [ ] `tasks/03-git.md`
- [ ] `tasks/04-onepassword.md` ← **must succeed before Phase 3**

### Phase 3 — Requires 1Password authenticated
Run automated tasks in parallel; interactive tasks are user-gated and run separately.

**Automated (run in parallel):**
- [ ] `tasks/06-openvpn.md`
- [ ] `tasks/07-aws.md`
- [ ] `tasks/08-ssh.md`

**Interactive (run sequentially after automated tasks):**
- [ ] `tasks/05-interactive-apps.md`

### Phase 4 — Requires SSH and git configured
- [ ] `tasks/11-development.md`
- [ ] `tasks/12-terminal.md`

## Resuming a Partial Run

If setup was interrupted, check off tasks that are already complete with `[x]` and skip them. For tasks marked `[!]`, read the task file and re-attempt before proceeding.

To re-run a single task: tell Claude "re-run task 08-ssh" and it will read that task file and execute it in isolation.

## 1Password MCP

This setup uses the 1Password MCP server for all secret retrieval. The MCP server communicates through the 1Password desktop app — no `op signin` step is needed.

**If the MCP server is unavailable during a task**, stop and tell the user:
> "The 1Password MCP server is not responding. Please ensure: (1) the 1Password desktop app is open, (2) Settings > Developer > 'Integrate with 1Password CLI' is enabled. Then restart this Claude session."

Do not attempt to fall back to the `op` CLI.
