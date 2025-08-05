#!/bin/bash

# Texas Court Opinion Monitor Setup Script

set -e

echo "🚀 Setting up Texas Court Opinion Monitor..."

# Check if running as root for systemd operations
if [[ $EUID -eq 0 ]]; then
    echo "❌ Don't run this script as root. Run as your user account."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Make the script executable
chmod +x court_opinion_monitor.py

# Copy service file to systemd user directory
echo "🔧 Setting up systemd service..."
mkdir -p ~/.config/systemd/user
cp court-monitor.service ~/.config/systemd/user/

# Enable systemd user services to run at boot
sudo loginctl enable-linger $USER

# Reload systemd user daemon
systemctl --user daemon-reload

# Enable the service
systemctl --user enable court-monitor.service

# Start the service
systemctl --user start court-monitor.service

echo "✅ Setup complete!"
echo ""
echo "📋 Useful commands:"
echo "  Check status:    systemctl --user status court-monitor.service"
echo "  View logs:       journalctl --user -u court-monitor.service -f"
echo "  Stop service:    systemctl --user stop court-monitor.service"
echo "  Start service:   systemctl --user start court-monitor.service"
echo "  Restart service: systemctl --user restart court-monitor.service"
echo ""
echo "📊 Data will be saved to: court_release_data.json"
echo "📝 Logs will be saved to: court_monitor.log"
echo ""
echo "🔄 The service will automatically restart after reboots." 