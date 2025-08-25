#!/usr/bin/bash
sudo cp /home/ubuntu/TaraFirst/gunicorn/gunicorn.socket  /etc/systemd/system/gunicorn.socket
sudo cp /home/ubuntu/TaraFirst/gunicorn/gunicorn.service  /etc/systemd/system/gunicorn.service
sudo chown ubuntu:ubuntu /home/ubuntu/TaraFirst
#sudo chown ubuntu:ubuntu /var/log/gunicorn
sudo systemctl start gunicorn.service
sudo systemctl enable gunicorn.service