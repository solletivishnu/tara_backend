#!/bin/bash
set -e

ACTIVE_FILE="/home/ubuntu/active_color.txt"
DEPLOY_FILE="/home/ubuntu/deployment_slot.txt"

# Create active_color.txt if missing
if [ ! -f "$ACTIVE_FILE" ]; then
  echo "green" > "$ACTIVE_FILE"
fi

CURRENT_SLOT=$(cat "$ACTIVE_FILE" | tr -d '[:space:]')

if [ "$CURRENT_SLOT" = "blue" ]; then
  NEW_SLOT="green"
else
  NEW_SLOT="blue"
fi

echo "[prepare_new_slot] Current active: $CURRENT_SLOT"
echo "[prepare_new_slot] Next deploy slot: $NEW_SLOT"

echo "$NEW_SLOT" > "$DEPLOY_FILE"

# Check write success
if [ "$(cat "$DEPLOY_FILE" | tr -d '[:space:]')" = "$NEW_SLOT" ]; then
  echo "[prepare_new_slot] ✅ Successfully wrote $NEW_SLOT to $DEPLOY_FILE"
else
  echo "[prepare_new_slot] ❌ Failed to update $DEPLOY_FILE"
fi
