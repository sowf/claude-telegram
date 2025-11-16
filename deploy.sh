#!/bin/bash

# Deployment script for Claude Telegram Bot
# This script automates the deployment process on Ubuntu (VPS, виртуалка, и т.д.)

set -e

echo "========================================"
echo "Claude Telegram Bot Deployment Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
if [ "$EUID" -eq 0 ]; then
    # Running as root
    CURRENT_USER="root"
    APP_DIR="/root/claude-telegram"
else
    # Running as regular user
    CURRENT_USER=$(whoami)
    APP_DIR="$HOME/claude-telegram"
fi

SERVICE_NAME="claude-telegram-bot"
LOG_DIR="/var/log/claude-telegram-bot"

# Update system packages
echo -e "${YELLOW}Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Install Python 3 and pip
echo -e "${YELLOW}Installing Python 3 and dependencies...${NC}"
apt-get install -y python3 python3-pip python3-venv

# Create application directory if it doesn't exist
if [ ! -d "$APP_DIR" ]; then
    echo -e "${YELLOW}Creating application directory...${NC}"
    mkdir -p "$APP_DIR"
fi

# Navigate to app directory
cd "$APP_DIR"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Check .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Please copy your .env file to $APP_DIR/"
    echo "Example: scp .env root@server:$APP_DIR/"
    exit 1
fi

echo -e "${GREEN}.env file found${NC}"

# Create log directory
echo -e "${YELLOW}Creating log directory...${NC}"
mkdir -p "$LOG_DIR"
chown $CURRENT_USER:$CURRENT_USER "$LOG_DIR"

# Setup systemd service (update User and paths)
echo -e "${YELLOW}Setting up systemd service...${NC}"

# Create temporary service file with correct user and paths
cat > /tmp/claude-telegram-bot.service << EOF
[Unit]
Description=Claude Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python bot.py
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/claude-telegram-bot/bot.log
StandardError=append:/var/log/claude-telegram-bot/error.log

[Install]
WantedBy=multi-user.target
EOF

# Install service
mv /tmp/claude-telegram-bot.service /etc/systemd/system/
systemctl daemon-reload

# Enable and start service
echo -e "${YELLOW}Enabling and starting service...${NC}"
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

# Check service status
echo -e "${GREEN}Checking service status...${NC}"
systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo -e "${GREEN}========================================"
echo "Deployment completed successfully!"
echo -e "========================================${NC}"
echo ""
echo "Useful commands:"
echo "  View logs:        journalctl -u $SERVICE_NAME -f"
echo "  Check status:     systemctl status $SERVICE_NAME"
echo "  Restart service:  systemctl restart $SERVICE_NAME"
echo "  Stop service:     systemctl stop $SERVICE_NAME"
echo "  Edit config:      nano $APP_DIR/.env"
echo ""
echo "Log files location: $LOG_DIR"
echo ""
