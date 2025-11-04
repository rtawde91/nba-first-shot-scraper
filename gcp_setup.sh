#!/bin/bash

# NBA Scraper - GCP VM Setup Script
# Run this script on your Google Cloud VM after SSH connection

set -e  # Exit on error

echo "========================================"
echo "🏀 NBA Scraper - GCP Setup"
echo "========================================"
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "🔧 Installing Python, Git, Nginx, Supervisor..."
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /var/www/nba-scraper
cd /var/www/nba-scraper

# Clone repository
echo "📥 Cloning your GitHub repository..."
sudo git clone https://github.com/rtawde91/nba-first-shot-scraper.git .

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R $USER:$USER /var/www/nba-scraper

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create log directory
echo "📝 Creating log directory..."
sudo mkdir -p /var/log/nba-scraper
sudo chown -R $USER:$USER /var/log/nba-scraper

# Configure Supervisor
echo "⚙️  Configuring Supervisor..."
sudo tee /etc/supervisor/conf.d/nba-scraper.conf > /dev/null <<EOF
[program:nba-scraper]
directory=/var/www/nba-scraper
command=/var/www/nba-scraper/venv/bin/python app.py
user=$USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/nba-scraper/err.log
stdout_logfile=/var/log/nba-scraper/out.log
environment=PYTHONUNBUFFERED=1,FLASK_ENV=production
EOF

# Update Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start nba-scraper

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/nba-scraper > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/nba-scraper /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Check status
echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "📊 Application Status:"
sudo supervisorctl status nba-scraper
echo ""
echo "🌐 Web Server Status:"
sudo systemctl status nginx --no-pager -l
echo ""
echo "========================================"
echo "🎉 Your NBA Scraper is now running!"
echo "========================================"
echo ""
echo "📍 Access your application at:"
echo "   http://YOUR_VM_EXTERNAL_IP"
echo ""
echo "📝 View logs:"
echo "   tail -f /var/log/nba-scraper/out.log"
echo ""
echo "🔄 Restart app:"
echo "   sudo supervisorctl restart nba-scraper"
echo ""
echo "⏰ Enable scheduler:"
echo "   1. Open http://YOUR_VM_EXTERNAL_IP in browser"
echo "   2. Click '▶️ Enable' in scheduler card"
echo ""
echo "========================================"

