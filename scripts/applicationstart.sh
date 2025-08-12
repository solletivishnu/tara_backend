#!/bin/bash
set -e

echo "[Start] 🚀 Starting Docker containers..."

APP_NAME="tara_prod_backend"
NETWORK_NAME="taranet"

# === Step 1: Read active deployment slot from deployment_slot.txt ===
DEPLOY_SLOT_FILE="/home/ubuntu/deployment_slot.txt"

if [[ ! -f "$DEPLOY_SLOT_FILE" ]]; then
    echo "❌ deployment_slot.txt not found at $DEPLOY_SLOT_FILE"
    exit 1
fi

DEPLOY_SLOT=$(cat "$DEPLOY_SLOT_FILE" | tr -d '[:space:]')

if [[ "$DEPLOY_SLOT" != "blue" && "$DEPLOY_SLOT" != "green" ]]; then
    echo "❌ Invalid DEPLOY_SLOT: $DEPLOY_SLOT (must be 'blue' or 'green')"
    exit 1
fi

IMAGE_VARS_FILE="/home/ubuntu/tara_prod_backend_${DEPLOY_SLOT}/image_vars.env"

if [[ ! -f "$IMAGE_VARS_FILE" ]]; then
    echo "❌ image_vars.env not found at $IMAGE_VARS_FILE"
    exit 1
fi

# === Step 2: Load env variablesss ===
set -a
source "$IMAGE_VARS_FILE"
set +a

if [[ -z "$DOCKER_IMAGE" || -z "$IMAGE_TAG" ]]; then
    echo "❌ DOCKER_IMAGE or IMAGE_TAG is missing in $IMAGE_VARS_FILE"
    exit 1
fi

DEPLOY_DIR="/home/ubuntu/${APP_NAME}_${DEPLOY_SLOT}"

echo "✅ Detected deploy slot: $DEPLOY_SLOT"
echo "✅ Using image: ${DOCKER_IMAGE}:${IMAGE_TAG}"

cd "$DEPLOY_DIR" || { echo "❌ Cannot cd to $DEPLOY_DIR"; exit 1; }

# === Start containers ===
docker-compose --env-file "$IMAGE_VARS_FILE" up -d
echo "[Start] ✅ Containers launched."

# === Connect containers to 'taranet' ==
CONTAINERS=(
  "redis_shared"
  "tara_backend_prod_${DEPLOY_SLOT}"
  "celery_worker_${DEPLOY_SLOT}"
  "celery_beat_${DEPLOY_SLOT}"
)

for container in "${CONTAINERS[@]}"; do
  if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
    if ! docker inspect "$container" | grep -q "$NETWORK_NAME"; then
      docker network connect "$NETWORK_NAME" "$container"
      echo "✅ Connected $container to $NETWORK_NAME"
    else
      echo "🔁 $container already connected to $NETWORK_NAME"
    fi
  else
    echo "❌ Container $container is not running"
  fi
done
