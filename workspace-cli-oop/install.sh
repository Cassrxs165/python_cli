#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/workspace-cli"
BIN="/usr/local/bin/workspace"

if [[ ! -f "workspace.py" || ! -d "workspace_cli" ]]; then
  echo "[!] Jalankan install.sh dari folder repo workspace-cli-oop"
  exit 1
fi

sudo mkdir -p "$APP_DIR"
sudo cp -r workspace.py workspace_cli "$APP_DIR/"
sudo chmod +x "$APP_DIR/workspace.py"

sudo tee "$BIN" >/dev/null <<'EOF'
#!/usr/bin/env bash
python3 /opt/workspace-cli/workspace.py "$@"
EOF

sudo chmod +x "$BIN"

echo "[+] WORKSPACE CLI OOP installed."
echo "[+] Jalankan dengan command:"
echo "    workspace"
