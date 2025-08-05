#!/bin/bash

# Simple startup script for Texas Court Opinion Monitor
# Use this if systemd setup fails

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/court_opinion_monitor.py"
PID_FILE="$SCRIPT_DIR/court_monitor.pid"
LOG_FILE="$SCRIPT_DIR/court_monitor.log"

start_monitor() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Monitor is already running (PID: $PID)"
            return 1
        else
            rm "$PID_FILE"
        fi
    fi
    
    echo "🚀 Starting Texas Court Opinion Monitor..."
    nohup python3 "$MONITOR_SCRIPT" >> "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    echo "✅ Monitor started with PID: $PID"
    echo "📝 Logs: $LOG_FILE"
    echo "📊 Data: $SCRIPT_DIR/court_release_data.json"
}

stop_monitor() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "🛑 Stopping monitor (PID: $PID)..."
            kill "$PID"
            rm "$PID_FILE"
            echo "✅ Monitor stopped"
        else
            echo "Monitor not running"
            rm "$PID_FILE"
        fi
    else
        echo "Monitor not running (no PID file)"
    fi
}

status_monitor() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ Monitor is running (PID: $PID)"
            echo "📝 Logs: tail -f $LOG_FILE"
            echo "📊 Data: $SCRIPT_DIR/court_release_data.json"
        else
            echo "❌ Monitor not running (stale PID file)"
            rm "$PID_FILE"
        fi
    else
        echo "❌ Monitor not running"
    fi
}

case "$1" in
    start)
        start_monitor
        ;;
    stop)
        stop_monitor
        ;;
    restart)
        stop_monitor
        sleep 2
        start_monitor
        ;;
    status)
        status_monitor
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the court monitor"
        echo "  stop    - Stop the court monitor" 
        echo "  restart - Restart the court monitor"
        echo "  status  - Check if monitor is running"
        echo ""
        echo "View logs: tail -f $LOG_FILE"
        echo "View data: ./view_data.py"
        exit 1
        ;;
esac 