# ☁️ Google Cloud Platform Deployment Guide

Deploy your NBA First Shot Scraper to Google Cloud Platform for 24/7 operation!

---

## 🎯 Deployment Option: Google Compute Engine (VM)

**Why Compute Engine?**
- ✅ Full control over the server
- ✅ Reliable 24/7 operation
- ✅ Free $300 credit for 90 days (new accounts)
- ✅ Always-free tier includes 1 e2-micro instance
- ✅ Perfect for scheduled jobs

**Cost:** ~$7-15/month (or FREE with always-free tier)

---

## 📋 Prerequisites

1. Google account
2. Credit card (for verification - won't be charged with free tier)
3. 15-20 minutes

---

## 🚀 Step-by-Step Deployment

### Step 1: Set Up Google Cloud Project

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com
   - Sign in with your Google account

2. **Create a New Project:**
   - Click "Select a project" dropdown at the top
   - Click "New Project"
   - Name: `nba-scraper` (or your choice)
   - Click "Create"

3. **Enable Billing:**
   - Go to "Billing" in the left menu
   - Link a billing account (needed even for free tier)
   - New users get $300 credit for 90 days!

4. **Enable Compute Engine API:**
   - Go to "APIs & Services" > "Library"
   - Search for "Compute Engine API"
   - Click "Enable"

---

### Step 2: Create a Virtual Machine

1. **Go to Compute Engine:**
   - In the left menu: Compute Engine > VM instances
   - Click "Create Instance"

2. **Configure Your VM:**

   **Name:** `nba-scraper-vm`
   
   **Region:** Choose closest to you (e.g., `us-central1`)
   
   **Machine Configuration:**
   - **Series:** E2
   - **Machine type:** `e2-micro` (FREE tier - 0.25-1 vCPU, 1GB RAM)
     - OR `e2-small` for better performance ($12/month - 2 vCPUs, 2GB RAM)
   
   **Boot Disk:**
   - Click "Change"
   - **Operating System:** Ubuntu
   - **Version:** Ubuntu 22.04 LTS
   - **Boot disk type:** Standard persistent disk
   - **Size:** 30 GB (included in free tier)
   - Click "Select"
   
   **Firewall:**
   - ✅ Check "Allow HTTP traffic"
   - ✅ Check "Allow HTTPS traffic"

3. **Click "Create"** (takes ~30 seconds)

---

### Step 3: Connect to Your VM

1. **From the VM instances page:**
   - Find your `nba-scraper-vm`
   - Click "SSH" button (opens a browser terminal)

---

### Step 4: Install Dependencies

Copy and paste these commands in the SSH terminal:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and tools
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor

# Install screen (optional, for monitoring)
sudo apt install -y screen
```

---

### Step 5: Upload Your Code

**Option A: Using Git (Recommended)**

First, push your code to GitHub (see instructions below), then:

```bash
# Create application directory
sudo mkdir -p /var/www/nba-scraper
cd /var/www/nba-scraper

# Clone your repository
sudo git clone https://github.com/YOUR_USERNAME/nba-scraper.git .

# Set permissions
sudo chown -R $USER:$USER /var/www/nba-scraper
```

**Option B: Upload Files Directly**

From your local machine:

```bash
# Install gcloud CLI first: https://cloud.google.com/sdk/docs/install

# Then upload files
gcloud compute scp --recurse /Users/rohantawde/PROJECTS/FIRSTSHOTSCRAPER/* nba-scraper-vm:/tmp/nba-scraper --zone=us-central1-a

# Then on the VM:
sudo mkdir -p /var/www/nba-scraper
sudo mv /tmp/nba-scraper/* /var/www/nba-scraper/
sudo chown -R $USER:$USER /var/www/nba-scraper
```

---

### Step 6: Set Up Python Environment

```bash
cd /var/www/nba-scraper

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Test that it works
python app.py
# Press Ctrl+C to stop after confirming it starts
```

---

### Step 7: Configure Supervisor (Keeps App Running)

Create supervisor configuration:

```bash
sudo nano /etc/supervisor/conf.d/nba-scraper.conf
```

Paste this content:

```ini
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
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

Create log directory and start service:

```bash
# Create log directory
sudo mkdir -p /var/log/nba-scraper
sudo chown -R $USER:$USER /var/log/nba-scraper

# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start nba-scraper

# Check status
sudo supervisorctl status nba-scraper
# Should show "RUNNING"
```

---

### Step 8: Configure Nginx (Web Server)

Create nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/nba-scraper
```

Paste this content:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

Enable the site:

```bash
# Enable your site
sudo ln -s /etc/nginx/sites-available/nba-scraper /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

### Step 9: Configure Firewall

Google Cloud firewall is managed via the Console, but let's set up UFW on the VM:

```bash
# Configure UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS (for future SSL)
sudo ufw --force enable

# Check status
sudo ufw status
```

---

### Step 10: Get Your External IP

1. **In Google Cloud Console:**
   - Go to Compute Engine > VM instances
   - Find your VM's "External IP" (e.g., `34.123.45.67`)

2. **Make IP Static (Optional but Recommended):**
   - Click on your VM name
   - Click "Edit"
   - Under "Network interfaces", click the pencil icon
   - External IP: Change from "Ephemeral" to "Create IP address"
   - Give it a name: `nba-scraper-ip`
   - Click "Reserve"
   - Click "Done" then "Save"

---

### Step 11: Access Your Application

1. **Open browser** to: `http://YOUR_EXTERNAL_IP`
2. You should see your NBA Scraper interface!

---

### Step 12: Enable the Scheduler

1. **In your web browser:**
   - Go to the scheduler card
   - Click **"▶️ Enable"**
   - Status should show: "✅ Enabled"
   - Next run should show: Tomorrow at 7:00 AM

2. **Test it:**
   - Click "⚡ Run Now" to test the full cycle
   - Watch the progress bars

**🎉 You're done! Your app is now running 24/7 on Google Cloud!**

---

## 🔒 Optional: Add SSL/HTTPS (Recommended)

### If you have a domain name:

1. **Point your domain to your VM's IP:**
   - In your domain registrar, create an A record
   - Point it to your VM's External IP

2. **Install Certbot:**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   ```

3. **Get SSL certificate:**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

4. **Auto-renewal is automatic!**

---

## 📊 Monitoring Your Deployment

### Check Application Status

```bash
# SSH into your VM
gcloud compute ssh nba-scraper-vm --zone=us-central1-a

# Check app status
sudo supervisorctl status nba-scraper

# View logs
tail -f /var/log/nba-scraper/out.log

# View errors
tail -f /var/log/nba-scraper/err.log

# Restart app
sudo supervisorctl restart nba-scraper
```

### Check Scheduler Status

```bash
curl http://localhost:8080/api/scheduler/status
```

### View CSV Files

```bash
cd /var/www/nba-scraper
ls -lh *.csv
```

---

## 🔄 Updating Your Code

### If using Git:

```bash
# SSH into VM
gcloud compute ssh nba-scraper-vm --zone=us-central1-a

# Update code
cd /var/www/nba-scraper
git pull

# Restart app
sudo supervisorctl restart nba-scraper
```

### Upload new files directly:

```bash
# From local machine
gcloud compute scp /Users/rohantawde/PROJECTS/FIRSTSHOTSCRAPER/app.py nba-scraper-vm:/var/www/nba-scraper/app.py --zone=us-central1-a

# Then restart on VM
sudo supervisorctl restart nba-scraper
```

---

## 💰 Cost Breakdown

### Free Tier (Always Free):
- ✅ 1 e2-micro instance (US regions only)
- ✅ 30 GB standard persistent disk
- ✅ 1 GB network egress per month

**This means:** Your app can run **completely FREE** if you:
- Use e2-micro instance
- Stay in US region (us-central1, us-east1, us-west1)
- Keep disk under 30 GB
- Network usage under 1 GB/month

### Paid Option (Better Performance):
- e2-small: ~$12/month
- e2-medium: ~$24/month

### Additional Costs:
- Network egress (after 1 GB free): ~$0.12/GB
- Static IP (if VM is stopped): $0.01/hour

---

## 🛡️ Security Best Practices

1. **Change SSH to key-only authentication:**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart sshd
   ```

2. **Regular updates:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Monitor logs:**
   ```bash
   sudo tail -f /var/log/nba-scraper/out.log
   ```

4. **Backup your data:**
   ```bash
   # Download CSV files to local machine
   gcloud compute scp nba-scraper-vm:/var/www/nba-scraper/*.csv ~/backups/ --zone=us-central1-a
   ```

---

## 🆘 Troubleshooting

### App Won't Start

```bash
# Check supervisor status
sudo supervisorctl status nba-scraper

# View error logs
sudo tail -50 /var/log/nba-scraper/err.log

# Check if port 8080 is in use
sudo lsof -i :8080

# Restart app
sudo supervisorctl restart nba-scraper
```

### Can't Access Web Interface

```bash
# Check nginx status
sudo systemctl status nginx

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Verify firewall
sudo ufw status

# Check if app is responding locally
curl http://localhost:8080
```

### Out of Memory

Upgrade to e2-small or e2-medium:
```bash
# Stop VM first in Cloud Console
# Then click Edit > Change machine type > e2-small
# Start VM again
```

---

## 📱 Google Cloud Console App

Download the Google Cloud Console app for mobile:
- iOS: https://apps.apple.com/app/id1005120374
- Android: https://play.google.com/store/apps/details?id=com.google.android.apps.cloudconsole

Monitor your VM and check logs from your phone!

---

## ✅ Post-Deployment Checklist

- [ ] VM is running and accessible
- [ ] Application responds on external IP
- [ ] Supervisor shows app as RUNNING
- [ ] Nginx is serving the application
- [ ] Scheduler is enabled
- [ ] Next run shows tomorrow at 7:00 AM
- [ ] Test "Run Now" button works
- [ ] CSV files are being generated
- [ ] Bookmark your external IP or domain

---

## 🎯 Quick Commands Reference

```bash
# SSH into VM
gcloud compute ssh nba-scraper-vm --zone=us-central1-a

# Check app status
sudo supervisorctl status nba-scraper

# View logs
tail -f /var/log/nba-scraper/out.log

# Restart app
sudo supervisorctl restart nba-scraper

# Update code (if using Git)
cd /var/www/nba-scraper && git pull && sudo supervisorctl restart nba-scraper

# Check disk space
df -h

# Check memory usage
free -h

# View running processes
top
```

---

**Your NBA Scraper is now running 24/7 on Google Cloud! 🎉**

Need help? Let me know which step you're on!

