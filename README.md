# Texas Court Opinion Release Monitor

Monitors 14 Texas Courts of Appeals for opinion releases 24/7 on weekdays. Automatically detects when courts release opinions by checking for `-CV` or `-CR` text patterns every 5 minutes and records the exact time.

## Quick Setup

### Option 1: Systemd (Recommended)
```bash
./setup_court_monitor.sh
```

### Option 2: Manual (if systemd fails)
```bash
pip3 install --user -r requirements.txt
./start_monitor.sh start
./setup_cron.sh  # For auto-restart after reboot
```

This will:
- Install dependencies
- Start monitoring automatically
- Enable restart after reboots

## Files Created

- `court_release_data.json` - Raw data with release times
- `court_monitor.log` - Application logs
- `~/.config/systemd/user/court-monitor.service` - Service configuration

## Usage

### View Current Status
```bash
systemctl --user status court-monitor.service
```

### View Live Logs
```bash
journalctl --user -u court-monitor.service -f
```

### Control Service

**Systemd version:**
```bash
systemctl --user start court-monitor.service    # Start
systemctl --user stop court-monitor.service     # Stop
systemctl --user restart court-monitor.service  # Restart
```

**Manual version:**
```bash
./start_monitor.sh start      # Start
./start_monitor.sh stop       # Stop
./start_monitor.sh restart    # Restart
./start_monitor.sh status     # Check status
```

### View Collected Data
```bash
./view_data.py                # All data
./view_data.py summary        # Summary only
./view_data.py daily          # Daily breakdown
./view_data.py times          # Time analysis
```

## How It Works

1. **Court Monitoring**: Checks 14 courts (coa01-coa14) at `https://search.txcourts.gov/Docket.aspx`
2. **Opinion Detection**: Looks for `-CV` (civil) or `-CR` (criminal) case indicators
3. **Time Recording**: Records exact timestamp when opinions first appear
4. **Daily Cycle**: Stops checking each court once opinions are found for that day
5. **Business Hours**: Monitors 24/7, Monday-Friday

## Data Structure

```json
{
  "2025-01-27": {
    "coa01": {
      "release_time": "2025-01-27T09:15:32.123456",
      "status": "released"
    },
    "coa02": {
      "release_time": "2025-01-27T10:30:45.789012", 
      "status": "released"
    }
  }
}
```

## Requirements

- Python 3.6+
- `requests` library
- `schedule` library
- systemd (for persistence)

## Troubleshooting

### Service Won't Start
```bash
# Check service status
systemctl --user status court-monitor.service

# View detailed logs
journalctl --user -u court-monitor.service --no-pager
```

### Network Issues
The script includes retry logic and will log connection errors while continuing to run.

### Permission Issues
Ensure the script has read/write access to the project directory.

## Manual Operation

Run directly without systemd:
```bash
python3 court_opinion_monitor.py
```

Stop with Ctrl+C. Data is saved continuously. 