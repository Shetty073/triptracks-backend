#!/usr/bin/env bash

set -e

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8001}
WORKERS=${WORKERS:-4}
LOG_LEVEL=${LOG_LEVEL:-info}

echo "Starting Triptracks API (Production Setup)..."
echo "=> Host: $HOST"
echo "=> Port: $PORT"
echo "=> Workers: $WORKERS"
echo "=> Log Level: $LOG_LEVEL"

# Activate virtual environment (cross-platform)
if [ -d "venv" ]; then
    echo "=> Activating virtual environment..."

    if [ -f "venv/bin/activate" ]; then
        # Linux / macOS
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        # Windows (Git Bash)
        source venv/Scripts/activate
    else
        echo "WARNING: Could not find activate script in venv."
    fi
else
    echo "WARNING: No virtual environment found at ./venv. Assuming dependencies are globally installed."
fi

# Start the application
exec uvicorn app.main:app \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    --log-level $LOG_LEVEL \
    --proxy-headers \
    --forwarded-allow-ips='*' \
    --timeout-keep-alive 65