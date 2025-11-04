# 📦 Push Your Code to GitHub

Before deploying to Google Cloud, let's get your code on GitHub for easy management.

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create GitHub Repository

1. **Go to GitHub:** https://github.com
2. **Sign in** (or create account if needed)
3. **Click the "+" icon** in top-right > "New repository"
4. **Configure:**
   - Repository name: `nba-first-shot-scraper`
   - Description: `NBA First Shot Analysis & Scraper with Automatic Daily Updates`
   - Make it **Private** (recommended) or Public
   - ❌ Don't check "Add a README" (we have one)
   - Click "Create repository"

---

### Step 2: Prepare Your Local Code

Open Terminal and run these commands:

```bash
# Navigate to your project
cd /Users/rohantawde/PROJECTS/FIRSTSHOTSCRAPER

# Initialize Git (if not already done)
git init

# Add all files
git add .

# Make first commit
git commit -m "Initial commit: NBA First Shot Scraper with cloud deployment support"
```

---

### Step 3: Connect to GitHub

GitHub will show you commands like these (use YOUR username):

```bash
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/nba-first-shot-scraper.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

**Note:** You may need to authenticate with GitHub. If prompted:
- Use your GitHub username
- For password, use a **Personal Access Token** (not your actual password)

---

### Step 4: Create Personal Access Token (If Needed)

If GitHub asks for authentication:

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" > "Generate new token (classic)"
3. Note: `GCP deployment`
4. Expiration: `90 days` (or longer)
5. Select scopes: ✅ **repo** (all)
6. Click "Generate token"
7. **Copy the token** (you won't see it again!)
8. Use this token as your password when pushing

---

### Step 5: Verify Upload

1. Go to your GitHub repository page
2. You should see all your files!
3. ✅ Ready for GCP deployment

---

## 📝 Files That Will Be Uploaded

Your `.gitignore` will exclude:
- ❌ `*.csv` (data files - too large)
- ❌ `*.log` (log files)
- ❌ `__pycache__/` (Python cache)
- ❌ `.DS_Store` (Mac files)
- ✅ All Python code
- ✅ `requirements.txt`
- ✅ Deployment configs

---

## 🔄 Future Updates

When you make changes:

```bash
# Save changes
git add .
git commit -m "Description of changes"
git push
```

Then on your GCP VM:

```bash
cd /var/www/nba-scraper
git pull
sudo supervisorctl restart nba-scraper
```

---

## 🎯 Next Step

Now that your code is on GitHub, you can easily deploy to GCP using:

```bash
# On your GCP VM:
sudo git clone https://github.com/YOUR_USERNAME/nba-first-shot-scraper.git .
```

Much easier than uploading files manually!

---

**Ready for GCP deployment!** 🚀

