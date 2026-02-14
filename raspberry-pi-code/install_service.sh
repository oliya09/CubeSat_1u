#!/bin/bash
# Installation script for CubeSat Raspberry Pi service

echo "Installing CubeSat Flight Controller..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3-pip python3-opencv
sudo pip3 install -r requirements.txt

# Create log directory
sudo mkdir -p /var/log/cubesat
sudo chown pi:pi /var/log/cubesat

# Create service file
sudo tee /etc/systemd/system/cubesat.service > /dev/null << EOF
[Unit]
Description=CubeSat Flight Controller
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/raspberry-pi/flight_controller.py
WorkingDirectory=/home/pi/raspberry-pi
Restart=always
RestartSec=10
User=pi
StandardOutput=append:/var/log/cubesat/output.log
StandardError=append:/var/log/cubesat/error.log

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable cubesat.service
sudo systemctl start cubesat.service

echo "Installation complete!"
echo "Check status with: sudo systemctl status cubesat.service"
echo "View logs with: sudo journalctl -u cubesat.service -f"