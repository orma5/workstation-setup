#!/bin/bash

# Check if ansible-playbook is installed
if ! command -v ansible-playbook &>/dev/null; then
  echo "ansible-playbook is not installed. Please install Ansible before running this script."
  exit 1
fi

# Run ansible-playbook with --ask-become-pass option
ansible-playbook -vv -i ../inventory ../main.yml --ask-become-pass
