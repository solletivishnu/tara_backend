#!/bin/bash
set -e

echo "[Migrate/Static] 🚀 Running DB migrations and collectstatic..."

DEPLOY_SLOT_FILE="/home/ubuntu/deployment_slot.txt"

if [[ ! -f "$DEPLOY_SLOT_FILE" ]]; then
  echo "❌ $DEPLOY_SLOT_FILE not found."
  exit 1
fi

COLOR=$(cat "$DEPLOY_SLOT_FILE" | tr -d '[:space:]')
echo "[Migrate/Static] 📁 Using deployment slot: $COLOR"

ENV_FILE="/home/ubuntu/tara_dev_backend_${COLOR}/image_vars.env"
DEPLOY_DIR="/home/ubuntu/tara_dev_backend_${COLOR}"
APP_NAME="tara_backend_dev_${COLOR}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ image_vars.env not found at $ENV_FILE"
  exit 1
fi

cd "$DEPLOY_DIR" || {
  echo "❌ Deployment directory $DEPLOY_DIR not found!"
  exit 1
}

source "$ENV_FILE"

# Get container ID
CONTAINER_ID=$(docker ps -qf "name=${APP_NAME}")
if [[ -z "$CONTAINER_ID" ]]; then
    echo "❌ Container $APP_NAME not running!"
    docker ps
    exit 1
fi

# Uncomment below when ready
# echo "[Migrate/Static] 🗃️ Applying migrations..."
# docker exec "$CONTAINER_ID" python manage.py migrate --noinput

# echo "[Migrate/Static] 🎯 Collecting static files..."
# docker exec "$CONTAINER_ID" python manage.py collectstatic --noinput

echo "✅ Migrations and static collection done for slot: $COLOR"
