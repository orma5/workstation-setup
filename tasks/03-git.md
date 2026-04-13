# Task: Git Configuration

## Goal
Copy dotfiles to the home directory and configure git user identity.

## Prerequisites
- git must be installed (available after Xcode CLT)

## Idempotency Check
- Check if `~/.gitconfig` already exists and contains a `[user]` section with `name` and `email`.
- Check if `~/.global-gitignore` already exists.
- If both exist and `~/.gitconfig` already has a user identity, ask the user: "Git is already configured for <name> <email>. Re-configure, or skip?"

## Steps
1. Read `dotfiles/.gitconfig` and `dotfiles/.global-gitignore` from the repo.
2. Copy `dotfiles/.global-gitignore` to `~/.global-gitignore` (overwrite).
3. If `~/.gitconfig` does not exist, copy `dotfiles/.gitconfig` to `~/.gitconfig`.
   If it does exist, merge by appending the dotfile contents only if the relevant sections are absent — do not overwrite an existing git config.
4. Ask the user for their git identity:
   - "What is your full name for git commits?"
   - "What is your email address for git commits?"
5. Set the identity:
   ```
   git config --global user.name "<name>"
   git config --global user.email "<email>"
   ```
6. Verify: `git config --global user.name` and `git config --global user.email` return the entered values.

## Completion Criteria
- `~/.gitconfig` exists and `git config --global user.name` returns a non-empty value.
- `~/.global-gitignore` exists.
