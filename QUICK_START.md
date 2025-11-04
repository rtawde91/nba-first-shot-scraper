# 🚀 Quick Start - Cloud Deployment

Choose your deployment method:

---

## 🌈 Railway (Easiest - 5 Minutes)

### Prerequisites:
- GitHub account
- Railway account (free): https://railway.app

### Steps:

1. **Push code to GitHub:**
   ```bash
   cd /Users/rohantawde/PROJECTS/FIRSTSHOTSCRAPER
   
   # If not already a git repo:
   git init
   git add .
   git commit -m "Initial commit for deployment"
   
   # Create a new repo on GitHub, then:
   git remote add origin https://github.com/YOUR_USERNAME/nba-scraper.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy to Railway:**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `nba-scraper` repository
   - Railway auto-detects Python and deploys!

3. **Get your URL:**
   - Railway will give you a URL like: `https://nba-scraper-production.up.railway.app`
   - Open it in your browser

4. **Enable scheduler:**
   - Click "▶️ Enable" in the scheduler card
   - Done! Runs at 7 AM daily ✅

**Cost:** $5-10/month (includes $5 free credit)

---

## 🌊 DigitalOcean (Most Reliable - 15 Minutes)

### Prerequisites:
- DigitalOcean account: https://www.digitalocean.com
- $6/month for basic droplet

### Quick Deploy Script:

1. **Create a droplet** (Ubuntu 22.04, Basic $6/month)

2. **Run this one-liner on the server:**
   ```bash
   curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/nba-scraper/main/deploy.sh | bash
   ```

3. **Or manual setup:**
   ```bash
   # SSH into your server
   ssh root@YOUR_DROPLET_IP
   
   # Run setup
   apt update && apt upgrade -y
   apt install -y python3 python3-pip python3-venv git nginx supervisor
   
   # Clone your code
   mkdir -p /var/www/nba-scraper
   cd /var/www/nba-scraper
   git clone https://github.com/YOUR_USERNAME/nba-scraper.git .
   
   # Install dependencies
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Set up supervisor (keeps app running)
   cat > /etc/supervisor/conf.d/nba-scraper.conf <<EOF
[program:nba-scraper]
directory=/var/www/nba-scraper
command=/var/www/nba-scraper/venv/bin/python app.py
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/nba-scraper/err.log
stdout_logfile=/var/log/nba-scraper/out.log
EOF
   
   mkdir -p /var/log/nba-scraper
   supervisorctl reread
   supervisorctl update
   supervisorctl start nba-scraper
   
   # Configure nginx
   cat > /etc/nginx/sites-available/nba-scraper <<EOF
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
   
   ln -s /etc/nginx/sites-available/nba-scraper /etc/nginx/sites-enabled/
   rm /etc/nginx/sites-enabled/default
   systemctl restart nginx
   
   # Open firewall
   ufw allow 22
   ufw allow 80
   ufw --force enable
   ```

4. **Open your server IP** in browser: `http://YOUR_DROPLET_IP`

5. **Enable scheduler:** Click "▶️ Enable"

**Cost:** $6/month

---

## 📋 Files Created for Deployment:

✅ `Procfile` - Tells cloud how to run the app  
✅ `runtime.txt` - Specifies Python version  
✅ `.gitignore` - Excludes unnecessary files  
✅ `app.py` - Updated to use PORT environment variable  
✅ `DEPLOYMENT_GUIDE.md` - Full detailed guide  

---

## 🎯 Recommendation:

**For you, I recommend: Railway**

**Why?**
- ✅ Easiest setup (literally 5 minutes)
- ✅ Automatic deployments from Git
- ✅ Free $5 credit per month
- ✅ Built-in monitoring
- ✅ No server management needed

**DigitalOcean** is better if:
- You want full control
- You're comfortable with Linux
- You want guaranteed performance

---

## 🆘 Need Help?

I can help you:
1. Create the GitHub repository
2. Set up Railway deployment
3. Configure DigitalOcean server

Just let me know which option you prefer!

---

## ✅ After Deployment Checklist:

- [ ] App is accessible via URL
- [ ] Scheduler shows "Enabled"
- [ ] Next run shows tomorrow at 7:00 AM
- [ ] Test "Run Now" button works
- [ ] Check that CSV files are being created
- [ ] Bookmark your cloud URL

**Your app will now run 24/7 independently! 🎉**

