#!/usr/bin/bash

sudo systemctl daemon-reload

# Move the server configuration to /etc/nginx/sites-enabled/finance_box_be
sudo rm -f /etc/nginx/sites-enabled/Tara
sudo cp /home/ubuntu/TaraFirst/nginx/nginx.conf /etc/nginx/sites-available/Tara
sudo ln -s /etc/nginx/sites-available/Tara /etc/nginx/sites-enabled/

# Update the main nginx.conf file with the http configuration
sudo cp /home/ubuntu/TaraFirst/nginx/http.conf /etc/nginx/nginx.conf

# Set ownership and permissions for the proxy directory
sudo chown -R nobody:www-data /var/lib/nginx/proxy
sudo chmod -R 770 /var/lib/nginx/proxy

# Add www-data user to the ubuntu group
sudo gpasswd -a www-data ubuntu

# Restart Nginx
sudo systemctl restart nginx