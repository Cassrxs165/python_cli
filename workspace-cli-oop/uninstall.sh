#!/usr/bin/env bash
set -euo pipefail

sudo rm -f /usr/local/bin/workspace
sudo rm -rf /opt/workspace-cli

echo "[+] WORKSPACE CLI removed."
echo "[i] Config user masih ada di ~/.workspace-cli"
