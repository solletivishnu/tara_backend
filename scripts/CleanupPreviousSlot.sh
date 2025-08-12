#!/bin/bash
set -e

# Read the new slot (where the new version is deployed)
NEW_SLOT=$(cat /home/ubuntu/deployment_slot.txt | tr -d '[:space:]')

# Define OLD_SLOT as the other slot (the one not being deployed)
if [ "$NEW_SLOT" = "blue" ]; then
  NEW_PORT=8001
  OLD_SLOT="green"
else
  NEW_PORT=8002
  OLD_SLOT="blue"
fi

echo "[ValidateService] 🔍 Checking health at port: $NEW_PORT"
if curl -s --fail "http://localhost:${NEW_PORT}/user_management/happy-coder/"; then
  echo "[ValidateService] ✅ Health check passed on $NEW_SLOT"

  # Mark this slot as active
  echo "$NEW_SLOT" > /home/ubuntu/active_color.txt

  # Reload nginx to switch traffic
  sudo systemctl reload nginx
  echo "[ValidateService] 🔁 Nginx reloaded to route to $NEW_SLOT"

  # Stop old slot containers
  echo "[ValidateService] 🛑 Stopping OLD_SLOT: $OLD_SLOT"
  docker-compose -f /home/ubuntu/tara_dev_backend_${OLD_SLOT}/docker-compose.yml stop

  echo "[ValidateService] 🎉 Switched to slot: $NEW_SLOT"
else
  echo "[ValidateService] ❌ Health check failed for $NEW_SLOT. Aborting switch."
  exit 1
fi
