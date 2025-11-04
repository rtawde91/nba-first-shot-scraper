# 🏀 NBA First Shot Scraper & Analysis

Automatically scrape and analyze NBA first shot data with a beautiful web interface and automatic daily updates.

---

## ✨ Features

- 📅 **4-Phase Scraping System**
  - Phase 1: Game schedules
  - Phase 2: Rosters & injuries
  - Phase 3: Play-by-play data (until first FG)
  - Phase 4: Upcoming games (today & tomorrow)

- ⏰ **Automatic Daily Updates**
  - Runs at 7:00 AM every day
  - No manual intervention needed
  - Cloud-ready for 24/7 operation

- 📊 **Advanced Analysis Dashboard**
  - Historical Game Analysis (HGA)
  - Player view, Team view, Game view
  - Upcoming game predictions
  - Custom scoring metrics
  - Real-time filtering

- 🎯 **First Shot Tracking**
  - Track who takes the first shot
  - Analyze success rates
  - Historical performance metrics
  - Player-specific insights

---

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open browser:**
   ```
   http://localhost:8080
   ```

4. **Enable scheduler:**
   - Click "▶️ Enable" in the scheduler card
   - Done! Runs at 7 AM daily

---

## ☁️ Cloud Deployment

Deploy to Google Cloud for 24/7 operation (FREE tier available!)

### Quick Deploy:

1. **Push to GitHub** → See `GITHUB_SETUP.md`
2. **Deploy to GCP** → See `GCP_DEPLOYMENT.md`
3. **Enable Scheduler** → Click "▶️ Enable"

**Time:** ~20 minutes  
**Cost:** FREE (with GCP free tier)

### Deployment Guides:

- 📖 **`DEPLOYMENT_SUMMARY.md`** - Start here!
- 📖 **`GCP_DEPLOYMENT.md`** - Complete GCP guide
- 📖 **`GITHUB_SETUP.md`** - GitHub setup
- 📖 **`SCHEDULER_SETUP.md`** - Scheduler details

**Also supports:** Railway, DigitalOcean, AWS - see `DEPLOYMENT_GUIDE.md`

---

## 📁 Project Structure

```
FIRSTSHOTSCRAPER/
├── app.py                      # Main Flask application
├── scraper_with_progress.py   # 4-phase scraper with progress tracking
├── game_analyzer.py            # Game analysis logic
├── nba_team_mappings.py        # Team name mappings
├── requirements.txt            # Python dependencies
├── templates/
│   ├── index.html             # Scraper control panel
│   └── analysis.html          # Analysis dashboard
├── games_and_rosters.csv      # Historical game data
├── play_by_play_first_fg.csv  # Play-by-play data
└── upcoming_games.csv         # Today/tomorrow games

Deployment Files:
├── Procfile                   # Cloud deployment config
├── runtime.txt                # Python version
├── .gitignore                 # Git exclusions
└── Deployment Guides:
    ├── DEPLOYMENT_SUMMARY.md  # 👈 START HERE
    ├── GCP_DEPLOYMENT.md      # Google Cloud guide
    ├── GITHUB_SETUP.md        # GitHub guide
    ├── DEPLOYMENT_GUIDE.md    # All platforms
    └── SCHEDULER_SETUP.md     # Scheduler details
```

---

## 🎯 Usage

### 1. Run Scraper (Manual)

1. Go to `http://localhost:8080`
2. Click "⚡ Run Full Cycle (All 4 Phases)"
3. Wait for completion (~15-20 minutes)

### 2. View Analysis

1. Go to `http://localhost:8080/analysis`
2. Switch between views:
   - **By Game:** See all games
   - **By Team:** Team-specific analysis
   - **By Player:** Player rankings
3. Filter by upcoming game
4. Customize scoring metrics

### 3. Automatic Updates (Recommended)

1. Enable scheduler: Click "▶️ Enable"
2. Runs at 7:00 AM daily
3. Data always fresh!

---

## 📊 Analysis Views

### By Game View
- All historical games
- Expandable play-by-play details
- Player highlights
- First shot outcomes

### By Team View
- Team-level aggregations
- Player frequency analysis
- Game-by-game breakdowns
- Roster tracking

### By Player View
- Player rankings by score
- Historical performance
- First shot statistics
- Per-game details

---

## ⚙️ Configuration

### Scoring Metrics

Customize in the Analysis page:
- **First Shot Made:** +2.0 (default)
- **First Shot Missed:** +1.0 (default)
- **First FG Made:** +0.75 (default)
- **Missed Shot:** +0.5 (default)
- **Free Throw:** +0.25 (default)

### Scheduler

Change schedule time in `app.py`:
```python
scheduler.add_job(
    func=scheduled_daily_update,
    trigger=CronTrigger(hour=7, minute=0),  # Change here
    ...
)
```

---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Scraper:** BeautifulSoup4, Requests
- **Data:** Pandas, CSV
- **Scheduler:** APScheduler
- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Deployment:** Cloud-ready (GCP, Railway, DigitalOcean, AWS)

---

## 📦 Dependencies

```
Flask>=2.3.0
requests>=2.31.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
lxml>=4.9.0
APScheduler>=3.10.0
```

Install all:
```bash
pip install -r requirements.txt
```

---

## 🔒 Security

- No API keys required
- All data scraped from public sources (basketball-reference.com)
- Rate limiting built-in (respects site)
- No personal data stored

---

## 📈 Performance

- **Scraping Time:** 15-20 minutes for full cycle
- **Memory:** ~200-500 MB
- **Disk:** ~50 MB for CSVs
- **Network:** Minimal (respects rate limits)

---

## 🌐 API Endpoints

### Status
- `GET /api/status` - Scraper progress
- `GET /api/analysis` - Analysis data
- `GET /api/scheduler/status` - Scheduler status

### Control
- `POST /api/scheduler/start` - Enable scheduler
- `POST /api/scheduler/stop` - Disable scheduler
- `POST /api/scheduler/run_now` - Trigger immediately
- `POST /api/start/full_cycle` - Run full scrape

---

## 🆘 Troubleshooting

### App won't start
```bash
# Check dependencies
pip install -r requirements.txt

# Check port availability
lsof -i :8080
```

### Scraper fails
- Check internet connection
- Verify basketball-reference.com is accessible
- Check logs in terminal

### Scheduler not running
- Verify APScheduler is installed
- Check logs for errors
- Enable via web UI

---

## 📝 Contributing

This is a personal project, but suggestions are welcome!

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 🙏 Acknowledgments

- Data source: [Basketball Reference](https://www.basketball-reference.com)
- Built for NBA first shot analysis

---

## 🚀 Next Steps

1. **For Local Use:**
   - Run `python app.py`
   - Enable scheduler
   - Enjoy!

2. **For Cloud Deployment:**
   - Read `DEPLOYMENT_SUMMARY.md`
   - Choose platform (GCP recommended)
   - Deploy in 20 minutes
   - Access from anywhere!

---

**Built with ❤️ for NBA analytics**

Questions? Check the deployment guides or reach out!
