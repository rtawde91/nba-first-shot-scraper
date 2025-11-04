# ☁️ Cloud Deployment Guide

Deploy your NBA First Shot Scraper to the cloud for 24/7 operation!

---

## 🚀 Option 1: Railway (Recommended - Easiest)

**Pros:**
- ✅ Free tier available ($5 credit/month)
- ✅ Automatic deployments from Git
- ✅ Built-in monitoring
- ✅ Simple setup (5 minutes)

**Cons:**
- ⚠️ Free tier may be limited for heavy scraping

### Step-by-Step Setup:

#### 1. Prepare Your Project

First, create necessary deployment files:

**Create `runtime.txt`:**
```txt
python-3.9
```

**Create `Procfile`:**
```
web: python app.py
```

**Update `app.py` to use PORT environment variable:**

Change the last line from:
```python
app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)
```

To:
```python
port = int(os.environ.get('PORT', 8080))
app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
```

#### 2. Initialize Git Repository

```bash
cd /Users/rohantawde/PROJECTS/FIRSTSHOTSCRAPER
git init
git add .
git commit -m "Initial commit for deployment"
```

#### 3. Deploy to Railway

1. Go to https://railway.app and sign up (free with GitHub)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Connect your GitHub account and create a new repo from your project
5. Railway will auto-detect Python and deploy!

#### 4. Enable Scheduler

Once deployed:
1. Open your Railway app URL (e.g., `https://yourapp.railway.app`)
2. Go to the scheduler card
3. Click **"▶️ Enable"**
4. Done! It will run at 7 AM daily

---

## 🌊 Option 2: DigitalOcean (Most Reliable)

**Pros:**
- ✅ Full control
- ✅ Very reliable
- ✅ $6/month basic droplet
- ✅ Great documentation

**Cons:**
- ⚠️ Requires basic Linux knowledge
- ⚠️ Manual setup required

### Step-by-Step Setup:

#### 1. Create a DigitalOcean Droplet

1. Sign up at https://www.digitalocean.com (get $200 credit for 60 days)
2. Click **"Create Droplet"**
3. Choose:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic ($6/month - 1GB RAM)
   - **Datacenter:** Choose closest to you
   - **Authentication:** SSH key (recommended) or password
4. Click **"Create Droplet"**

#### 2. Connect to Your Server

```bash
ssh root@your_droplet_ip
```

#### 3. Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python and pip
apt install python3 python3-pip python3-venv git -y

# Install nginx (web server)
apt install nginx -y

# Install supervisor (keeps app running)
apt install supervisor -y
```

#### 4. Set Up Your Application

```bash
# Create app directory
mkdir -p /var/www/nba-scraper
cd /var/www/nba-scraper

# Clone your code (or upload via scp)
git clone https://github.com/yourusername/FIRSTSHOTSCRAPER.git .

# Or upload via scp from your local machine:
# scp -r /Users/rohantawde/PROJECTS/FIRSTSHOTSCRAPER/* root@your_droplet_ip:/var/www/nba-scraper/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

#### 5. Configure Supervisor (Keeps App Running)

Create supervisor config:

```bash
nano /etc/supervisor/conf.d/nba-scraper.conf
```

Add this content:

```ini
[program:nba-scraper]
directory=/var/www/nba-scraper
command=/var/www/nba-scraper/venv/bin/python app.py
user=root
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/nba-scraper/err.log
stdout_logfile=/var/log/nba-scraper/out.log
environment=PYTHONUNBUFFERED=1
```

Create log directory:

```bash
mkdir -p /var/log/nba-scraper
```

Start the service:

```bash
supervisorctl reread
supervisorctl update
supervisorctl start nba-scraper
```

Check status:

```bash
supervisorctl status nba-scraper
```

#### 6. Configure Nginx (Web Server)

Create nginx config:

```bash
nano /etc/nginx/sites-available/nba-scraper
```

Add this content:

```nginx
server {
    listen 80;
    server_name your_droplet_ip;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
ln -s /etc/nginx/sites-available/nba-scraper /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 7. Configure Firewall

```bash
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS (for future SSL)
ufw enable
```

#### 8. Enable the Scheduler

1. Open browser to `http://your_droplet_ip`
2. Click **"▶️ Enable"** in the scheduler card
3. Done!

---

## 🔒 Optional: Add SSL/HTTPS (Recommended)

For DigitalOcean deployment:

```bash
# Install certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate (requires a domain name)
certbot --nginx -d yourdomain.com
```

---

## 📊 Monitoring Your Cloud Deployment

### Check Application Status

**Railway:**
- Dashboard shows logs and metrics automatically

**DigitalOcean:**
```bash
# Check if app is running
supervisorctl status nba-scraper

# View logs
tail -f /var/log/nba-scraper/out.log

# Restart app
supervisorctl restart nba-scraper
```

### Check Scheduler Status

Via API:
```bash
curl http://your_server_url/api/scheduler/status
```

### View CSV Files

```bash
cd /var/www/nba-scraper
ls -lh *.csv
```

---

## 🔧 Updating Your Code

### Railway:
Just push to GitHub - auto-deploys!
```bash
git add .
git commit -m "Update code"
git push origin main
```

### DigitalOcean:
```bash
# SSH into server
ssh root@your_droplet_ip

# Pull latest code
cd /var/www/nba-scraper
git pull

# Restart app
supervisorctl restart nba-scraper
```

---

## 💰 Cost Comparison

| Provider | Monthly Cost | Free Tier |
|----------|-------------|-----------|
| Railway | $5-20 | $5/month credit |
| DigitalOcean | $6+ | $200 credit (60 days) |
| AWS EC2 | $0-10 | Free for 1 year (t2.micro) |
| Heroku | $7+ | Limited free tier |

---

## 🆘 Troubleshooting

### App Won't Start

**Railway:**
- Check logs in Railway dashboard
- Verify `requirements.txt` is complete

**DigitalOcean:**
```bash
supervisorctl status nba-scraper
tail -f /var/log/nba-scraper/err.log
```

### Scheduler Not Running

1. Check app is running: `supervisorctl status nba-scraper`
2. Enable via web UI
3. Check logs for errors

### Out of Memory

Upgrade your server plan or optimize scraping:
- Process fewer games at once
- Add delays between requests

---

## 📝 Maintenance Tips

1. **Monitor disk space:** CSV files can grow large
   ```bash
   df -h
   ```

2. **Archive old data:** Move old CSVs to backup
   ```bash
   mkdir -p backups/$(date +%Y-%m)
   cp *.csv backups/$(date +%Y-%m)/
   ```

3. **Check logs regularly:**
   ```bash
   tail -100 /var/log/nba-scraper/out.log
   ```

4. **Update dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

## 🎯 Which Option Should You Choose?

- **Choose Railway if:** You want the easiest setup and don't mind paying $5-10/month
- **Choose DigitalOcean if:** You want full control and reliability for $6/month
- **Choose AWS EC2 if:** You want free hosting for 1 year and have AWS experience

---

Need help with deployment? Let me know which provider you choose!

