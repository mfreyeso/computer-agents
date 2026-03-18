#!/bin/bash
set -e

# Ensure pyenv is on PATH (the Anthropic image uses pyenv)
export HOME=/home/computeruse
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"

# Start tool execution server in background
DISPLAY=:1 PYTHONPATH=/home/computeruse python3 /opt/tool_server.py 8888 &

# Find and exec the original entrypoint
for entry in /entrypoint.sh /startup.sh /home/computeruse/entrypoint.sh; do
    if [ -x "$entry" ]; then
        exec "$entry" "$@"
    fi
done

echo "ERROR: Could not locate original entrypoint" >&2
exec sleep infinity
