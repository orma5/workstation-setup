# Task: Homebrew Applications

## Goal
Install all casks and formulae defined in `config/applications.yaml` using Homebrew.

## Prerequisites
- Homebrew must be installed (handled by `init.sh`)

## Idempotency Check
Run `brew list --casks` and `brew list --formula` to see what's already installed. Skip packages that are already present and note them as "already installed". Do not reinstall.

For casks, also check if the `.app` bundle exists in `/Applications/` using `mdfind` as a fallback since some casks may have been installed outside Homebrew.

## Steps
1. Read `config/applications.yaml`.
2. Run `brew update` to refresh package index.
3. For each cask in the `casks` list:
   a. Check if already installed: `brew list --cask <name>` or `mdfind "kMDItemKind == 'Application'" -name "<AppName>.app"`.
   b. If not installed: `brew install --cask <name>`.
   c. If the install fails, warn and continue to the next cask (do not abort).
4. For each formula in the `formulae` list:
   a. Check if already installed: `brew list <name>`.
   b. If not installed: `brew install <name>`.
   c. If the install fails, warn and continue.
5. After all packages are processed, report a summary: X installed, Y already present, Z failed.

## Completion Criteria
- All packages in `applications.yaml` are either installed or reported as failed.
- No hard failure — partial success is acceptable (failed packages are noted for the user).
