#!/bin/bash
set -e

echo "[Start] Starting Docker containers..."
cd /home/ubuntu/tara_dev_backend

if [ -f "image_vars.env" ]; then
    set -a
    source image_vars.env
    set +a
else
    echo "❌ image_vars.env not found!"
    exit 1
fi

if [[ -z "$DOCKER_IMAGE" || -z "$IMAGE_TAG" ]]; then
    echo "❌ DOCKER_IMAGE or IMAGE_TAG is missing"
    exit 1
fi

if [[ -z "$REDIS_IMAGE" ]]; then
    echo "❌ REDIS_IMAGE is missing"
    exit 1
fi

echo "✅ Using image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
echo "✅ Using Redis image: ${REDIS_IMAGE}"

# 🚀 Since images are already pulled in pull_images.sh, just start containers
docker-compose --env-file image_vars.env up -d --no-build --no-recreate

echo "[Start] ✅ Containers launched."
