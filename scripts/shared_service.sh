#!/bin/bash
set -e

echo "📦 Setting up shared Redis & PostgreSQL..."

SHARED_DIR="/home/ubuntu/shared_services"

# Ensure shared directory exists
if [ ! -d "$SHARED_DIR" ]; then
  mkdir -p "$SHARED_DIR"
  chown ubuntu:ubuntu "$SHARED_DIR"
fi

# Ensure taranet network exists
if ! docker network ls | grep -q "\btaranet\b"; then
  echo "🌐 Creating external Docker network 'taranet'..."
  docker network create --driver bridge taranet
else
  echo "🔁 Docker network 'taranet' already exists."
fi

# Write docker-compose.yml if it doesn't exist
if [ ! -f "$SHARED_DIR/docker-compose.yml" ]; then
  cat > "$SHARED_DIR/docker-compose.yml" <<EOF
services:
  redis:
    image: docker.io/sadanandtummuri/redis:7.0
    container_name: redis_shared
    restart: always
    ports:
      - "6379:6379"
    networks:
      - taranet

networks:
  taranet:
    external: true
    name: taranet
EOF
fi

cd "$SHARED_DIR"

# Start shared services
echo "🚀 Starting Redis shared services..."
docker-compose up -d
echo "✅ Redis is now running under 'taranet' network."
