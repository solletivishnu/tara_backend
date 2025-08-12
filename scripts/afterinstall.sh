#!/bin/bash
set -e

echo "[AfterInstall] ✅ Starting AfterInstall script..."

APP_ROOT_BASE="/home/ubuntu"
APP_NAME="tara_prod_backend"

# Read currently active slot
ACTIVE_SLOT=$(cat /home/ubuntu/active_color.txt | tr -d '[:space:]')

# Determine new slot and port
if [ "$ACTIVE_SLOT" = "blue" ]; then
  NEW_SLOT="green"
  NEW_PORT=8002
else
  NEW_SLOT="blue"
  NEW_PORT=8001
fi

DEPLOY_DIR="${APP_ROOT_BASE}/${APP_NAME}_${NEW_SLOT}"
echo "[AfterInstall] 📂 Deploy directory: $DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# 🧹 Remove old files except .env
echo "[AfterInstall] 🧹 Cleaning old files in $DEPLOY_DIR (except .env)..."
find "$DEPLOY_DIR" -mindepth 1 -not -name '.env' -exec rm -rf {} +

# 🧼 Remove stopped containers related to the NEW_SLOT
echo "[AfterInstall] 🧼 Removing stopped containers for $NEW_SLOT..."
docker ps -a --filter "name=tara_backend_prod_${NEW_SLOT}" --filter "status=exited" -q | xargs -r docker rm

# 🧼 Remove dangling images
echo "[AfterInstall] 🧼 Removing dangling Docker images..."
docker image prune -f

# 🔍 (Optional) Remove old images related to NEW_SLOT (if tagged with slot name)
# This assumes your image tags include slot info, like tara_dev_backend_green
echo "[AfterInstall] 🧼 Removing old images tagged with $NEW_SLOT..."
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep "tara_backend_prod_${NEW_SLOT}" | awk '{print $2}' | xargs -r docker rmi

# 📦 Copy new app files into deployment directory
echo "[AfterInstall] 📦 Copying new artifacts to $DEPLOY_DIR..."
cp -r /home/ubuntu/tara_backend_staging/* "$DEPLOY_DIR"


# # # Recreate nginx template file safely
rm -f /tmp/http.conf
cp /tmp/http_template.conf /tmp/http.conf

# ✅ Permissions
chmod 600 "$DEPLOY_DIR/.env"
chown ubuntu:ubuntu "$DEPLOY_DIR/.env"

echo "[AfterInstall] ✅ AfterInstall script completed for $NEW_SLOT."
