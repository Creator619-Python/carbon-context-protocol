#!/bin/bash
# carbon-cron: Carbon-aware cron wrapper
# Usage: carbon-cron [options] <command>
#   --threshold N   Carbon intensity threshold (default: 250)
#   --max-wait N    Maximum wait time in minutes (default: 240)
#   --check-interval N  Check interval in minutes (default: 15)

set -e

# Defaults
THRESHOLD=250
MAX_WAIT=240  # 4 hours
CHECK_INTERVAL=15

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --threshold)
            THRESHOLD="$2"
            shift 2
            ;;
        --max-wait)
            MAX_WAIT="$2"
            shift 2
            ;;
        --check-interval)
            CHECK_INTERVAL="$2"
            shift 2
            ;;
        *)
            COMMAND="$*"
            break
            ;;
    esac
done

if [ -z "$COMMAND" ]; then
    echo "Usage: carbon-cron [options] <command>" >&2
    exit 1
fi

echo "[carbon-cron] Starting with threshold=$THRESHOLD, max-wait=$MAX_WAIT minutes"

# Wait for good conditions
WAIT_MINUTES=0
while [ $WAIT_MINUTES -lt $MAX_WAIT ]; do
    # Check carbon intensity
    if CARBON_THRESHOLD=$THRESHOLD /usr/bin/carbon-ok; then
        echo "[carbon-cron] Conditions favorable, executing command"
        exec $COMMAND
    fi
    
    # Wait before checking again
    echo "[carbon-cron] Waiting for better conditions ($WAIT_MINUTES/$MAX_WAIT minutes)"
    sleep $((CHECK_INTERVAL * 60))
    WAIT_MINUTES=$((WAIT_MINUTES + CHECK_INTERVAL))
done

# Timeout - run anyway with warning
echo "[carbon-cron] Timeout after $MAX_WAIT minutes, running anyway"
exec $COMMAND
