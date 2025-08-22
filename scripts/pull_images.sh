#!/bin/bash
set -e

echo "[BeforeInstall] Pulling Docker images..."
cd /home/ubuntu/tara_dev_backend

if [ -f "image_vars.env" ]; then
    set -a
    source image_vars.env
    set +a
else
    echo "❌ image_vars.env not founddddd!"
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

echo "✅ Pulling app image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
docker pull ${DOCKER_IMAGE}:${IMAGE_TAG}

echo "✅ Pulling Redis image: ${REDIS_IMAGE}"
docker pull ${REDIS_IMAGE}

echo "[BeforeInstall] ✅ Images pulled successfully."
