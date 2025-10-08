#!/bin/bash
# Systemd Service Setup für MMM-UniAssignments Backend

set -e

# Prüfe ob als root ausgeführt
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo ./setup-systemd.sh)"
    exit 1
fi

MODULE_PATH=$(pwd)
USER=$(logname)

echo "🔧 Setting up systemd service for MMM-UniAssignments..."

# Erstelle systemd service file
cat > /etc/systemd/system/mmm-uni-assignments.service <<EOF
[Unit]
Description=MMM-UniAssignments Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$MODULE_PATH/backend
Environment="PATH=$MODULE_PATH/backend/venv/bin"
ExecStart=$MODULE_PATH/backend/venv/bin/python3 $MODULE_PATH/backend/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable service
systemctl enable mmm-uni-assignments.service

echo ""
echo "✅ Systemd service installed!"
echo ""
echo "📋 Service commands:"
echo "  sudo systemctl start mmm-uni-assignments    # Start service"
echo "  sudo systemctl stop mmm-uni-assignments     # Stop service"
echo "  sudo systemctl restart mmm-uni-assignments  # Restart service"
echo "  sudo systemctl status mmm-uni-assignments   # Check status"
echo "  sudo journalctl -u mmm-uni-assignments -f   # View logs"
echo ""
echo "Starting service now..."
systemctl start mmm-uni-assignments.service

sleep 2

systemctl status mmm-uni-assignments.service --no-pager
