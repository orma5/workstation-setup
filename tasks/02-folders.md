# Task: Development Folders

## Goal
Create the development directory structure defined in `config/folders.yaml`.

## Prerequisites
- None

## Idempotency Check
Check if each directory already exists with `[ -d <path> ]`. Skip directories that already exist.

## Steps
1. Read `config/folders.yaml`.
2. For each path in the `folders` list (paths are relative to `~`, prefixed with `~/`):
   a. Expand `~` to the actual home directory.
   b. If the directory does not exist, create it with `mkdir -p <path>`.
   c. If it already exists, log "already exists" and skip.

## Completion Criteria
- All directories in `folders.yaml` exist on disk.
- Verify with `ls -la ~/Development`.
