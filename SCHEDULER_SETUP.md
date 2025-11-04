# ⏰ Automatic Daily Updates - Setup Guide

## Overview

The Basketball Reference Scraper now includes an **automatic daily scheduler** that runs the full scraping cycle every day at **7:00 AM** to keep your data fresh without manual intervention.

## Features

✅ **Automatic Daily Updates** - Runs at 7:00 AM every day  
✅ **Full Cycle Execution** - Runs all 4 phases automatically:
  - Phase 1: Schedule
  - Phase 2: Rosters & Injuries
  - Phase 3: Play-by-Play
  - Phase 4: Upcoming Games

✅ **Web UI Controls** - Enable/disable/trigger from the main page  
✅ **Status Monitoring** - See when the next run is scheduled  
✅ **Manual Trigger** - Run the scheduled job immediately if needed

## Installation

1. **Install the new dependency:**
```bash
pip install APScheduler>=3.10.0
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

2. **Start the application:**
```bash
python app.py
```

The scheduler is now ready to use!

## How to Use

### Enable Daily Updates

1. Open your browser to `http://localhost:8080`
2. Find the **"⏰ Automatic Daily Updates"** card at the top
3. Click the **"▶️ Enable"** button
4. The scheduler is now active!

The status will show:
- **Status:** ✅ Enabled
- **Next Run:** (timestamp of next scheduled run at 7:00 AM)

### Disable Daily Updates

Click the **"⏸️ Disable"** button to stop automatic updates.

### Manual Trigger

Click the **"⚡ Run Now"** button to immediately trigger the full cycle (useful for testing or when you need fresh data right away).

## How It Works

1. **Scheduler runs at 7:00 AM daily**
   - Automatically executes the full 4-phase cycle
   - No manual intervention needed

2. **Data is automatically updated:**
   - Game schedules refreshed
   - Current rosters and injuries updated
   - Play-by-play data collected
   - Upcoming games (today/tomorrow) fetched

3. **Safe execution:**
   - Won't start if another scraping job is already running
   - Logs all activity for troubleshooting
   - Continues running even if the server restarts (scheduler state persists)

## API Endpoints

The scheduler exposes the following REST API endpoints:

### Get Scheduler Status
```bash
GET /api/scheduler/status
```
Returns:
```json
{
  "enabled": true,
  "next_run": "2025-11-02 07:00:00",
  "schedule": "7:00 AM daily"
}
```

### Enable Scheduler
```bash
POST /api/scheduler/start
```

### Disable Scheduler
```bash
POST /api/scheduler/stop
```

### Trigger Manual Run
```bash
POST /api/scheduler/run_now
```

## Customization

To change the scheduled time, edit the `hour` and `minute` parameters in `app.py`:

```python
scheduler.add_job(
    func=scheduled_daily_update,
    trigger=CronTrigger(hour=7, minute=0),  # Change these values
    id='daily_update',
    name='Daily Full Cycle Update',
    replace_existing=True
)
```

For example, to run at 6:30 AM instead:
```python
trigger=CronTrigger(hour=6, minute=30)
```

## Troubleshooting

### Scheduler Not Running

1. Check if the scheduler is enabled in the UI
2. Verify APScheduler is installed: `pip list | grep APScheduler`
3. Check server logs for error messages

### Missed Scheduled Run

- The scheduler only runs while the Flask application is running
- Make sure your server is running continuously
- Consider using a process manager like `systemd`, `supervisor`, or `pm2` to keep the app running

### Keep Server Running 24/7

For production use, you'll want to keep the Flask app running continuously:

#### Option 1: Using `nohup` (Simple)
```bash
nohup python app.py > app.log 2>&1 &
```

#### Option 2: Using `screen` or `tmux`
```bash
screen -S scraper
python app.py
# Press Ctrl+A then D to detach
```

#### Option 3: Using `systemd` (Recommended for Linux)
Create a service file at `/etc/systemd/system/nba-scraper.service`:
```ini
[Unit]
Description=NBA First Shot Scraper
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/FIRSTSHOTSCRAPER
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable nba-scraper
sudo systemctl start nba-scraper
```

## Logs

The scheduler logs all activities:
- ✅ When daily updates start
- ✅ Each phase completion
- ✅ Any errors that occur
- ✅ When scheduler is enabled/disabled

Check the console output or application logs for details.

## Benefits

- **Always Fresh Data** - Your analysis always uses the latest information
- **No Manual Work** - Set it and forget it
- **Reliable** - Runs automatically every day
- **Flexible** - Can still run manual updates anytime
- **Transparent** - Full visibility into when updates will run

---

**Need Help?** Check the server logs or open an issue on GitHub.




