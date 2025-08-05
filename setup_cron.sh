#!/bin/bash

# Setup cron job to start court monitor after reboot
# Alternative to systemd when that's not available

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_LINE="@reboot cd $SCRIPT_DIR && ./start_monitor.sh start"

echo "🔧 Setting up cron job for automatic restart after reboot..."

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "start_monitor.sh"; then
    echo "⚠️  Cron job already exists"
    echo "Current cron jobs:"
    crontab -l 2>/dev/null | grep "start_monitor.sh"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
    echo "✅ Added cron job: $CRON_LINE"
fi

echo ""
echo "📋 To manage cron jobs:"
echo "  View all: crontab -l"
echo "  Edit:     crontab -e"
echo "  Remove:   crontab -e (then delete the line)"
echo ""
echo "🚀 The monitor will now start automatically after reboot" 