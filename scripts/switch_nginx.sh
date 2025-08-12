#!/bin/bash
set -e

echo "[SwitchNginx] 🚦 Starting health check & routing..."

# Determine active colorrrr
ACTIVE_COLOR=$(cat /home/ubuntu/active_color.txt 2>/dev/null || echo "blue")

# Set next color and target port
if [[ "$ACTIVE_COLOR" == "blue" ]]; then
  NEXT_COLOR="green"
  TARGET_PORT=8002
  DEPLOY_DIR="/home/ubuntu/tara_prod_backend_green"
else
  NEXT_COLOR="blue"
  TARGET_PORT=8001
  DEPLOY_DIR="/home/ubuntu/tara_prod_backend_blue"
fi

# Run health check
HEALTH_ENDPOINT="http://localhost:$TARGET_PORT/user_management/happy-coder/"
echo "🔍 Checking health at $HEALTH_ENDPOINT..."
RETRY=5
SUCCESS=false

for i in $(seq 1 $RETRY); do
  sleep 5
  if curl -s "$HEALTH_ENDPOINT" | grep -q '"message": *"Happy Coder, blue deployment succeeded"'; then
    SUCCESS=true
    echo "✅ Health check passed on port $TARGET_PORT"
    break
  else
    echo "⏳ Retry $i/$RETRY..."
  fi
done

if [ "$SUCCESS" != "true" ]; then
  echo "❌ Health check failed. Aborting switch."
  exit 1
fi

# Replace Nginx configuration
sed "s/__PORT__/$TARGET_PORT/" /tmp/http_template.conf > /etc/nginx/sites-available/http.conf
ln -sf /etc/nginx/sites-available/http.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Reload Nginx
nginx -t && systemctl reload nginx

# Update active_color.txt
echo "$NEXT_COLOR" > /home/ubuntu/active_color.txt

echo "✅ Nginx is now routing to $NEXT_COLOR ($TARGET_PORT)"


