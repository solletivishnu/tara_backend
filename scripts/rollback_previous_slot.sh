#!/bin/bash
set -e

echo "[Rollback] 🔁 Starting rollback to previous slot..."

# Active color file
ACTIVE_COLOR_FILE="/home/ubuntu/active_color.txt"

# Step 1: Get current active slot
if [[ ! -f "$ACTIVE_COLOR_FILE" ]]; then
  echo "❌ Active color file not found at $ACTIVE_COLOR_FILE"
  exit 1
fi

ACTIVE_SLOT=$(cat "$ACTIVE_COLOR_FILE" | tr -d '[:space:]')

if [[ "$ACTIVE_SLOT" == "blue" ]]; then
  PREVIOUS_SLOT="green"
elif [[ "$ACTIVE_SLOT" == "green" ]]; then
  PREVIOUS_SLOT="blue"
else
  echo "❌ Invalid active slot: $ACTIVE_SLOT"
  exit 1
fi

ROLLBACK_DIR="/home/ubuntu/tara_prod_backend_${PREVIOUS_SLOT}"
ENV_FILE="${ROLLBACK_DIR}/image_vars.env"
APP_NAME="tara_backend_prod_${PREVIOUS_SLOT}"

# Step 2: Verify rollback directory and env file
if [[ ! -d "$ROLLBACK_DIR" ]]; then
  echo "❌ Rollback directory $ROLLBACK_DIR does not exist."
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ image_vars.env not found at $ENV_FILE"
  exit 1
fi

echo "[Rollback] 📄 Loading image variables from $ENV_FILE"
set -o allexport
source "$ENV_FILE"
set +o allexport

if [[ -z "$IMAGE_NAME" || -z "$IMAGE_TAG" ]]; then
  echo "❌ IMAGE_NAME or IMAGE_TAG not defined in $ENV_FILE"
  exit 1
fi

echo "[Rollback] 💡 Rolling back to container: $APP_NAME"
cd "$ROLLBACK_DIR"

# Step 3: Start previous image using docker-compose
echo "[Rollback] 📦 Starting previous image..."
docker-compose --env-file "$ENV_FILE" start || {
  echo "❌ Failed to start container."
  exit 1
}

# Step 4: Wait for container to become healthy
echo "[Rollback] ⏳ Waiting for '$APP_NAME' to become healthy..."
for i in {1..20}; do
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$APP_NAME" 2>/dev/null || echo "not_found")

  if [[ "$STATUS" == "healthy" ]]; then
    echo "✅ Container '$APP_NAME' is healthy!"
    break
  elif [[ "$STATUS" == "unhealthy" ]]; then
    echo "❌ Container '$APP_NAME' is unhealthy."
    exit 1
  elif [[ "$STATUS" == "not_found" ]]; then
    echo "❗ Container '$APP_NAME' not found yet..."
  else
    echo "⏳ Container status: $STATUS"
  fi
  sleep 3
done

# Step 5: Stop the failed (current active) container
CURRENT_APP_NAME="tara_backend_prod_${ACTIVE_SLOT}"
CURRENT_DIR="/home/ubuntu/tara_prod_backend_${ACTIVE_SLOT}"
echo "[Rollback] 🔻 Stopping failed container: $CURRENT_APP_NAME"
cd "$CURRENT_DIR"
docker-compose stop || echo "⚠️ Could not stop failed container."

# Step 6: Update active color
echo "$PREVIOUS_SLOT" > "$ACTIVE_COLOR_FILE"
echo "✅ Rollback complete. Active slot is now: $PREVIOUS_SLOT"
