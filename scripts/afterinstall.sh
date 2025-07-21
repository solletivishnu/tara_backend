#!/bin/bash
set -e

echo "[AfterInstall] ✅ Setting up Nginx..."

# 1. Move Nginx config to correct location
cp /tmp/http.conf /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/http.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 2. Test & restart Nginx
echo "[AfterInstall] 🔍 Validating Nginx config..."
nginx -t
systemctl restart nginx

# 3. Ensure .env exists (used by docker-compose or app)
echo "[AfterInstall] 🛡️ Ensuring .env exists with secure permissions..."
touch /home/ubuntu/tara_dev_backend/.env
chmod 600 /home/ubuntu/tara_dev_backend/.env
chown ubuntu:ubuntu /home/ubuntu/tara_dev_backend/.env

echo "[AfterInstall] ✅ Done"