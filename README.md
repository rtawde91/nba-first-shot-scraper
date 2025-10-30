# Basketball Reference First Shot Scraper

A Python web scraper that extracts NBA game data from Basketball-Reference.com, focusing on starting lineups, injury information, and play-by-play data until the first field goal is made.

## 🎯 Features

- **3-Phase Scraping System** - Separate, controllable phases for different data types
- **Real-time Web Interface** - Beautiful dashboard with live progress tracking
- Scrapes all NBA games from the 2025-26 season
- Extracts starting lineups for each team
- Captures injury/inactive player information
- Records play-by-play data from tip-off until the first field goal is made
- **Auto-refresh every 30 seconds** with live data preview
- Shows elapsed time, ETA, and completion percentage for each phase
- Exports data to CSV files for easy analysis

## 🚀 Quick Start (Web Interface - Recommended)

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Start Web Interface
```bash
python3 app.py
```

### 3. Open Browser
Navigate to: **http://127.0.0.1:5000**

### 4. Run the Phases
- Click **"Start Phase 1"** to fetch game schedule
- Click **"Start Phase 2"** to collect rosters & injuries
- Click **"Start Phase 3"** to get play-by-play data

## 📋 3-Phase System

### Phase 1: 📅 Schedule Fetching
- Fetches list of all games from 2025-26 season
- Independent progress bar and stats
- Shows total games found

### Phase 2: 👥 Rosters & Injuries
- Collects starting lineups for each game
- Captures injury/inactive player information
- Independent progress tracking
- Requires Phase 1 to complete first

### Phase 3: 🏀 Play-by-Play
- Extracts play-by-play until first field goal
- Independent progress tracking
- Automatically saves to CSV when complete
- Requires Phase 1 to complete first

## 📊 Output Files

### 1. `games_and_rosters.csv`
Contains one row per game with the following columns:
- `date` - Game date
- `visitor_team` - Visiting team name
- `home_team` - Home team name
- `game_id` - Unique game identifier
- `visitor_starters` - Starting lineup for visiting team (semicolon-separated)
- `home_starters` - Starting lineup for home team (semicolon-separated)
- `visitor_injuries` - Injured/inactive players for visiting team (semicolon-separated)
- `home_injuries` - Injured/inactive players for home team (semicolon-separated)

### 2. `play_by_play_first_fg.csv`
Contains one row per play until the first field goal, with the following columns:
- `game_id` - Unique game identifier
- `date` - Game date
- `visitor_team` - Visiting team name
- `home_team` - Home team name
- `time` - Game clock time
- `visitor_play` - Description of visiting team's play
- `home_play` - Description of home team's play
- `score` - Current score

## 🎨 Web Interface Features

- **Three separate progress cards** - One for each phase
- **Independent start buttons** - Run each phase separately
- **Real-time progress bars** - Visual progress for each phase
- **Stats boxes** - Elapsed time, ETA, completion counts
- **Live data preview** - See collected data in table format
- **Auto-refresh** - Updates every 30 seconds (2 seconds while active)

## 📝 Important Considerations

### Rate Limiting
The scraper includes built-in rate limiting (3 seconds between requests) to be respectful to Basketball-Reference servers. Please do not reduce this delay.

### Terms of Service
This scraper is for educational and personal use only. Please review Basketball-Reference.com's Terms of Service before scraping.

### Data Accuracy
- Starting lineups are determined by the first 5 players listed in each team's box score
- Injury information may not always be complete
- Play-by-play data captures all plays until a 2-point or 3-point field goal is made

## 🛠️ Requirements

- Python 3.7+
- requests
- beautifulsoup4
- pandas
- lxml
- flask

## 🔧 Troubleshooting

### Access Denied (403)
If you get access denied errors, Basketball-Reference may be blocking automated requests. Try:
- Increasing the wait time between requests
- Running the scraper during off-peak hours
- Checking if your IP has been rate-limited

### Phases Won't Start
- Make sure Phase 1 completes successfully before running Phase 2 or 3
- Check the terminal for error messages
- Refresh the browser page

### Script Takes Too Long
- The script includes necessary delays to avoid being blocked
- Phase 2 and 3 take the longest (3-5 seconds per game)
- For ~60 games: expect 10-15 minutes per phase

## 📄 License

This project is provided as-is for educational purposes. Please respect Basketball-Reference.com's terms of service when using this scraper.

