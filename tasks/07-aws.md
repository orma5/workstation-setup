# Task: AWS CLI and kubectl Configuration

## Goal
Fetch AWS credentials from 1Password and configure the AWS CLI and kubectl for EKS cluster access.

## Prerequisites
- Task 04 (1Password) must be complete — MCP server must be responding
- `aws` CLI and `kubectl` must be installed (from task 01-homebrew)

## Idempotency Check
Check if `~/.aws/credentials` already exists and contains an `[default]` profile. If it does, ask the user: "AWS credentials file already exists. Reconfigure, or skip?"

## Steps
1. Read `config/application-setup.yaml`. Find the entry where `name == "awscli"`. Note the `onepassword_item_id`.
2. Use the 1Password MCP `get_vault_item` tool with that item ID to fetch the item.
   - If the MCP is unavailable, stop with the hard-fail message (see CLAUDE.md).
3. Extract the following fields from the item:
   - Field with label/id `access key` — AWS access key ID
   - Field with label/id `access secret` or similar secret field — AWS secret access key
   - Field with label/id `eks` or `cluster` — EKS cluster name
4. Create `~/.aws/` if it doesn't exist (`mkdir -p ~/.aws`).
5. Configure AWS CLI credentials:
   ```
   aws configure set aws_access_key_id "<access_key>"
   aws configure set aws_secret_access_key "<secret_key>"
   ```
6. Ask the user for their preferred AWS region: "What is your AWS region? (e.g. eu-west-1)"
7. Set the region: `aws configure set region "<region>"`
8. Verify credentials work: `aws sts get-caller-identity`. If this fails, warn the user and continue.
9. Configure kubectl for EKS:
   ```
   aws eks update-kubeconfig --name "<cluster_name>" --region "<region>"
   ```
   If this fails (cluster not found, permissions issue), warn and continue.

## Completion Criteria
- `~/.aws/credentials` exists and contains the `[default]` profile.
- `aws sts get-caller-identity` returns a valid identity (or failure is explicitly noted).
- `~/.kube/config` is updated with EKS cluster context (or failure is explicitly noted).
