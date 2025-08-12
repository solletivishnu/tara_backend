#!/bin/bash
set -e

# Log which slot is currently active
ACTIVE_SLOT=$(cat /home/ubuntu/active_color.txt | tr -d '[:space:]')

echo "[ApplicationStop] ℹ️ Current active slot is: $ACTIVE_SLOT"
echo "[ApplicationStop] ✅ No containers stopped. Preserving current deployment until new one is verified."
