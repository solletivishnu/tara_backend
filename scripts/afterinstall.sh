#!/bin/bash
set -e

# Redirect all output to a log file
exec &> >(tee -a /var/log/afterinstall.log)

echo "[AfterInstall] ✅ Setting up Nginx..."

# Check if Nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "[AfterInstall] ❌ Nginx is not installed. Aborting..."
    exit 1
fi

# Ensure the http.conf exists before proceeding
if [ ! -f /tmp/http.conf ]; then
    echo "[AfterInstall] ❌ /tmp/http.conf not found. Aborting..."
    exit 1
fi

# 1. Move Nginx config to the correct location
cp /tmp/http.conf /etc/nginx/sites-available/ || { echo "[AfterInstall] ❌ Failed to copy http.conf. Exiting..."; exit 1; }
ln -sf /etc/nginx/sites-available/http.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 2. Test Nginx config
echo "[AfterInstall] 🔍 Validating Nginx config..."
nginx -t || { echo "[AfterInstall] ❌ Nginx config test failed. Exiting..."; exit 1; }

# 3. Check if Nginx is already running and skip restart if it is
if ! systemctl is-active --quiet nginx; then
    echo "[AfterInstall] ❌ Nginx is not running. Attempting to restart..."
    systemctl restart nginx || { echo "[AfterInstall] ❌ Nginx service failed to start. Exiting..."; exit 1; }
else
    echo "[AfterInstall] ✅ Nginx is already running. Skipping restart."
fi

# 4. Ensure .env exists (used by docker-compose or app)
echo "[AfterInstall] 🛡️ Ensuring .env exists with secure permissions..."
touch /home/ubuntu/tara_dev_backend/.env
chmod 600 /home/ubuntu/tara_dev_backend/.env
chown ubuntu:ubuntu /home/ubuntu/tara_dev_backend/.env

echo "[AfterInstall] ✅ Done"
