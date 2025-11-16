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
CURRENT_USER=$(whoami)
APP_DIR="$HOME/claude-telegram"
SERVICE_NAME="claude-telegram-bot"
LOG_DIR="/var/log/claude-telegram-bot"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run this script as root or with sudo${NC}"
    echo "The script will ask for sudo password when needed"
    exit 1
fi

# Update system packages
echo -e "${YELLOW}Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip
echo -e "${YELLOW}Installing Python 3 and dependencies...${NC}"
sudo apt-get install -y python3 python3-pip python3-venv

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

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${RED}IMPORTANT: Please edit .env file with your credentials:${NC}"
    echo "nano $APP_DIR/.env"
    read -p "Press Enter after you've configured .env file..."
fi

# Create log directory
echo -e "${YELLOW}Creating log directory...${NC}"
sudo mkdir -p "$LOG_DIR"
sudo chown $CURRENT_USER:$CURRENT_USER "$LOG_DIR"

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
sudo mv /tmp/claude-telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start service
echo -e "${YELLOW}Enabling and starting service...${NC}"
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

# Check service status
echo -e "${GREEN}Checking service status...${NC}"
sudo systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo -e "${GREEN}========================================"
echo "Deployment completed successfully!"
echo -e "========================================${NC}"
echo ""
echo "Useful commands:"
echo "  View logs:        sudo journalctl -u $SERVICE_NAME -f"
echo "  Check status:     sudo systemctl status $SERVICE_NAME"
echo "  Restart service:  sudo systemctl restart $SERVICE_NAME"
echo "  Stop service:     sudo systemctl stop $SERVICE_NAME"
echo ""
echo "Log files location: $LOG_DIR"
echo ""
