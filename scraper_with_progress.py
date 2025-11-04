"""
Basketball Reference Scraper with Progress Tracking
Scrapes game data with real-time progress reporting for web interface
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from nba_team_mappings import get_team_code, create_game_key, format_date_short

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProgressTracker:
    """Thread-safe progress tracker for multiple phases"""
    
    def __init__(self):
        self.lock = threading.Lock()
        
        # Phase 1: Schedule
        self.schedule_total = 0
        self.schedule_completed = 0
        self.schedule_status = "idle"
        self.schedule_task = ""
        self.schedule_start_time = None
        self.schedule_end_time = None
        
        # Phase 2: Rosters
        self.roster_total = 0
        self.roster_completed = 0
        self.roster_status = "idle"
        self.roster_task = ""
        self.roster_start_time = None
        self.roster_end_time = None
        
        # Phase 3: Play-by-play
        self.pbp_total = 0
        self.pbp_completed = 0
        self.pbp_status = "idle"
        self.pbp_task = ""
        self.pbp_start_time = None
        self.pbp_end_time = None
        
        # Phase 4: Upcoming Games
        self.upcoming_total = 0
        self.upcoming_completed = 0
        self.upcoming_status = "idle"
        self.upcoming_task = ""
        self.upcoming_start_time = None
        self.upcoming_end_time = None
        
        # Global
        self.games_found = 0
        self.error_message = ""
    
    def _calculate_progress(self, completed: int, total: int, start_time: Optional[datetime], end_time: Optional[datetime] = None) -> Dict:
        """Helper to calculate progress stats"""
        if start_time:
            # Use end_time if phase is completed, otherwise use current time
            if end_time:
                elapsed = (end_time - start_time).total_seconds()
            else:
                elapsed = (datetime.now() - start_time).total_seconds()
        else:
            elapsed = 0
        
        if completed > 0 and total > 0:
            progress_pct = (completed / total) * 100
            if progress_pct > 0 and elapsed > 0 and not end_time:
                eta_seconds = (elapsed / progress_pct) * (100 - progress_pct)
            else:
                eta_seconds = 0
        else:
            progress_pct = 0
            eta_seconds = 0
        
        return {
            'progress_percent': round(progress_pct, 2),
            'elapsed_seconds': round(elapsed, 2),
            'eta_seconds': round(eta_seconds, 2)
        }
    
    # Phase 1: Schedule methods
    def start_schedule(self, total: int):
        with self.lock:
            self.schedule_total = total
            self.schedule_completed = 0
            self.schedule_start_time = datetime.now()
            self.schedule_status = "running"
    
    def update_schedule(self, completed: int, task: str):
        with self.lock:
            self.schedule_completed = completed
            self.schedule_task = task
    
    def complete_schedule(self, games_found: int):
        with self.lock:
            self.schedule_status = "completed"
            self.schedule_task = f"Found {games_found} games"
            self.games_found = games_found
            self.schedule_end_time = datetime.now()
    
    # Phase 2: Roster methods
    def start_roster(self, total: int):
        with self.lock:
            self.roster_total = total
            self.roster_completed = 0
            self.roster_start_time = datetime.now()
            self.roster_status = "running"
    
    def update_roster(self, completed: int, task: str):
        with self.lock:
            self.roster_completed = completed
            self.roster_task = task
    
    def complete_roster(self):
        with self.lock:
            self.roster_status = "completed"
            self.roster_task = "All rosters collected"
            self.roster_end_time = datetime.now()
    
    # Phase 3: Play-by-play methods
    def start_pbp(self, total: int):
        with self.lock:
            self.pbp_total = total
            self.pbp_completed = 0
            self.pbp_start_time = datetime.now()
            self.pbp_status = "running"
    
    def update_pbp(self, completed: int, task: str):
        with self.lock:
            self.pbp_completed = completed
            self.pbp_task = task
    
    def complete_pbp(self):
        with self.lock:
            self.pbp_status = "completed"
            self.pbp_task = "All play-by-play data collected"
            self.pbp_end_time = datetime.now()
    
    # Phase 4: Upcoming games methods
    def start_upcoming(self, total: int):
        with self.lock:
            self.upcoming_total = total
            self.upcoming_completed = 0
            self.upcoming_start_time = datetime.now()
            self.upcoming_status = "running"
    
    def update_upcoming(self, completed: int, task: str):
        with self.lock:
            self.upcoming_completed = completed
            self.upcoming_task = task
    
    def complete_upcoming(self):
        with self.lock:
            self.upcoming_status = "completed"
            self.upcoming_task = "All upcoming games collected"
            self.upcoming_end_time = datetime.now()
    
    def error(self, phase: str, message: str):
        with self.lock:
            if phase == "schedule":
                self.schedule_status = "error"
            elif phase == "roster":
                self.roster_status = "error"
            elif phase == "pbp":
                self.pbp_status = "error"
            elif phase == "upcoming":
                self.upcoming_status = "error"
            self.error_message = message
    
    def get_status(self) -> Dict:
        with self.lock:
            schedule_progress = self._calculate_progress(
                self.schedule_completed, self.schedule_total, self.schedule_start_time, self.schedule_end_time
            )
            roster_progress = self._calculate_progress(
                self.roster_completed, self.roster_total, self.roster_start_time, self.roster_end_time
            )
            pbp_progress = self._calculate_progress(
                self.pbp_completed, self.pbp_total, self.pbp_start_time, self.pbp_end_time
            )
            upcoming_progress = self._calculate_progress(
                self.upcoming_completed, self.upcoming_total, self.upcoming_start_time, self.upcoming_end_time
            )
            
            return {
                'schedule': {
                    'status': self.schedule_status,
                    'total': self.schedule_total,
                    'completed': self.schedule_completed,
                    'task': self.schedule_task,
                    **schedule_progress
                },
                'roster': {
                    'status': self.roster_status,
                    'total': self.roster_total,
                    'completed': self.roster_completed,
                    'task': self.roster_task,
                    **roster_progress
                },
                'pbp': {
                    'status': self.pbp_status,
                    'total': self.pbp_total,
                    'completed': self.pbp_completed,
                    'task': self.pbp_task,
                    **pbp_progress
                },
                'upcoming': {
                    'status': self.upcoming_status,
                    'total': self.upcoming_total,
                    'completed': self.upcoming_completed,
                    'task': self.upcoming_task,
                    **upcoming_progress
                },
                'games_found': self.games_found,
                'error_message': self.error_message
            }


class BasketballReferenceScraperWithProgress:
    """Scraper with progress tracking"""
    
    BASE_URL = "https://www.basketball-reference.com"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    RATE_LIMIT = 3  # seconds between requests
    
    def __init__(self, progress_tracker: ProgressTracker):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.progress = progress_tracker
        self.games_list = []  # List of games from schedule
        self.games_data = []  # Games with rosters
        self.play_by_play_data = []  # Play-by-play data
        self.upcoming_games_data = []  # Upcoming games (today/tomorrow)
        
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """Make HTTP request with rate limiting and error handling"""
        try:
            time.sleep(self.RATE_LIMIT)
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout fetching {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None
    
    def get_season_schedule(self, season: str) -> List[Dict]:
        """Get all games for a season"""
        games = []
        months = ['october', 'november', 'december', 'january', 'february', 
                  'march', 'april', 'may', 'june']
        
        season_int = int(season)
        for month in months:
            url = f"{self.BASE_URL}/leagues/NBA_{season}_games-{month}.html"
            soup = self._make_request(url)
            
            if not soup:
                continue
            
            schedule_table = soup.find('table', {'id': 'schedule'})
            if not schedule_table:
                logger.warning(f"No schedule found for {month} {season}")
                continue
            
            tbody = schedule_table.find('tbody')
            if not tbody:
                continue
            
            for row in tbody.find_all('tr'):
                if row.get('class') and 'thead' in row.get('class'):
                    continue
                
                cells = row.find_all(['td', 'th'])
                if len(cells) < 7:
                    continue
                
                date_cell = cells[0]
                visitor_cell = cells[2]
                home_cell = cells[4]
                box_score_cell = cells[6] if len(cells) > 6 else None
                
                box_score_link = None
                if box_score_cell:
                    link = box_score_cell.find('a')
                    if link and link.get('href'):
                        box_score_link = link.get('href')
                
                if not box_score_link:
                    continue
                
                game_data = {
                    'date': date_cell.get_text(strip=True),
                    'visitor_team': visitor_cell.get_text(strip=True) if visitor_cell else '',
                    'home_team': home_cell.get_text(strip=True) if home_cell else '',
                    'box_score_url': f"{self.BASE_URL}{box_score_link}",
                    'season': season
                }
                
                games.append(game_data)
        
        return games
    
    def get_game_starters_and_injuries(self, box_score_url: str, game_data: Dict) -> Dict:
        """Extract starting lineup and injury information"""
        self.progress.update_roster(
            self.progress.roster_completed,
            f"Processing {game_data['visitor_team']} @ {game_data['home_team']} - Starters & Injuries"
        )
        
        soup = self._make_request(box_score_url)
        if not soup:
            return None
        
        game_id = box_score_url.split('/')[-1].replace('.html', '')
        
        # Get team codes and formatted date
        visitor_code = get_team_code(game_data['visitor_team'])
        home_code = get_team_code(game_data['home_team'])
        date_short = format_date_short(game_data['date'])
        game_key = create_game_key(game_data['visitor_team'], game_data['home_team'], game_data['date'])
        
        result = {
            'game_key': game_key,
            'date': date_short,
            'matchup': f"{visitor_code}@{home_code}",
            'visitor_team': visitor_code,
            'home_team': home_code,
            'visitor_team_full': game_data['visitor_team'],
            'home_team_full': game_data['home_team'],
            'game_id': game_id,
            'visitor_starters': [],
            'home_starters': [],
            'visitor_injuries': [],
            'home_injuries': []
        }
        
        tables = soup.find_all('table', {'class': 'stats_table'})
        
        team_count = 0
        for table in tables:
            if 'game-basic' not in table.get('id', ''):
                continue
            
            tbody = table.find('tbody')
            if not tbody:
                continue
            
            starters = []
            player_count = 0
            
            for row in tbody.find_all('tr'):
                if row.get('class') and 'thead' in row.get('class'):
                    break
                
                th = row.find('th')
                if not th:
                    continue
                
                player_link = th.find('a')
                if not player_link:
                    continue
                
                player_name = player_link.get_text(strip=True)
                
                if player_count < 5:
                    starters.append(player_name)
                    player_count += 1
            
            if team_count == 0:
                result['visitor_starters'] = starters
            elif team_count == 1:
                result['home_starters'] = starters
            
            team_count += 1
        
        # Look for injury information
        injury_divs = soup.find_all('div', {'class': 'section_content'})
        
        for div in injury_divs:
            text = div.get_text()
            if 'inactive' in text.lower() or 'injury' in text.lower() or 'out' in text.lower():
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and ('inactive' in line.lower() or 'out' in line.lower()):
                        if result['visitor_team'].lower() in line.lower():
                            result['visitor_injuries'].append(line)
                        elif result['home_team'].lower() in line.lower():
                            result['home_injuries'].append(line)
        
        return result
    
    def get_play_by_play_until_first_fg(self, box_score_url: str, game_data: Dict) -> List[Dict]:
        """Extract play-by-play until first field goal"""
        game_id = box_score_url.split('/')[-1].replace('.html', '')
        pbp_url = f"{self.BASE_URL}/boxscores/pbp/{game_id}.html"
        
        soup = self._make_request(pbp_url)
        if not soup:
            logger.warning(f"Failed to fetch PBP page for game {game_id}")
            return []
        
        plays = []
        first_fg_made = False
        
        # Basketball-Reference often hides tables in HTML comments
        pbp_table = soup.find('table', {'id': 'pbp'})
        
        # If table not found directly, try finding it in comments
        if not pbp_table:
            from bs4 import Comment
            comments = soup.find_all(string=lambda text: isinstance(text, Comment))
            for comment in comments:
                if 'id="pbp"' in comment or 'id=\'pbp\'' in comment:
                    comment_soup = BeautifulSoup(comment, 'html.parser')
                    pbp_table = comment_soup.find('table', {'id': 'pbp'})
                    if pbp_table:
                        logger.debug(f"Found PBP table in HTML comment for game {game_id}")
                        break
        
        if not pbp_table:
            logger.warning(f"No play-by-play table found for game {game_id} (checked both direct and comments)")
            return []
        
        # Try to find tbody, but if not present, use the table directly
        tbody = pbp_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            logger.debug(f"Found tbody with {len(rows)} rows for game {game_id}")
        else:
            rows = pbp_table.find_all('tr')
            logger.debug(f"No tbody found, using table directly - found {len(rows)} rows for game {game_id}")
        
        if not rows:
            logger.warning(f"No rows found in PBP table for game {game_id}")
            return []
        
        for row in rows:
            if first_fg_made:
                break
            
            # Skip header rows (they have class 'thead' or only contain 'th' elements)
            if row.get('class') and 'thead' in row.get('class'):
                continue
            
            cells = row.find_all(['td', 'th'])
            
            # Play-by-play table has 6 columns:
            # 0: Time, 1: Visitor Play, 2: Visitor Score Diff, 3: Game Score, 4: Home Score Diff, 5: Home Play
            # We only care about: Time (0), Visitor Play (1), Game Score (3), Home Play (5)
            if len(cells) < 6:
                continue
            
            # Skip rows that are all header cells
            if all(cell.name == 'th' for cell in cells):
                continue
            
            time_cell = cells[0]
            visitor_play_cell = cells[1]
            # cells[2] is visitor score diff (+2, -3, etc.) - we skip this
            score_cell = cells[3]  # Game score is column 3
            # cells[4] is home score diff (+2, -3, etc.) - we skip this
            home_play_cell = cells[5]  # Home play is column 5
            
            time_text = time_cell.get_text(strip=True)
            visitor_play = visitor_play_cell.get_text(strip=True)
            score = score_cell.get_text(strip=True)
            home_play = home_play_cell.get_text(strip=True)
            
            if not visitor_play and not home_play:
                continue
            
            # Get team codes and formatted date
            visitor_code = get_team_code(game_data['visitor_team'])
            home_code = get_team_code(game_data['home_team'])
            date_short = format_date_short(game_data['date'])
            game_key = create_game_key(game_data['visitor_team'], game_data['home_team'], game_data['date'])
            
            play_data = {
                'game_key': game_key,
                'date': date_short,
                'matchup': f"{visitor_code}@{home_code}",
                'visitor_team': visitor_code,
                'home_team': home_code,
                'time': time_text,
                'visitor_play': visitor_play,
                'home_play': home_play,
                'score': score,
                'game_id': game_id
            }
            
            plays.append(play_data)
            
            visitor_play_lower = visitor_play.lower()
            home_play_lower = home_play.lower()
            
            fg_made_keywords = ['makes 2-pt', 'makes 3-pt']
            for keyword in fg_made_keywords:
                if keyword in visitor_play_lower or keyword in home_play_lower:
                    first_fg_made = True
                    logger.debug(f"First FG found in game {game_id}: '{visitor_play or home_play}'")
                    break
        
        if len(plays) == 0:
            logger.warning(f"No plays collected for game {game_id} - checked {len(rows)} rows")
        else:
            logger.debug(f"Collected {len(plays)} plays for game {game_id} from {len(rows)} total rows")
        
        return plays
    
    # PHASE 1: Fetch Schedule
    def scrape_schedule(self, seasons: List[str] = ['2026']):
        """Phase 1: Fetch game schedules"""
        try:
            logger.info("="*60)
            logger.info("📅 PHASE 1: Fetching Game Schedule")
            logger.info("="*60)
            
            # Get current date to avoid fetching future games
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            
            months = ['october', 'november', 'december', 'january', 'february', 
                      'march', 'april', 'may', 'june']
            month_numbers = {'october': 10, 'november': 11, 'december': 12, 
                           'january': 1, 'february': 2, 'march': 3, 
                           'april': 4, 'may': 5, 'june': 6}
            
            # Filter months to only include those up to current date
            months_to_fetch = []
            for season in seasons:
                season_int = int(season)
                for month in months:
                    month_num = month_numbers[month]
                    # Determine which calendar year this month belongs to
                    if month_num >= 10:  # Oct, Nov, Dec are in the first year of season
                        year = season_int - 1
                    else:  # Jan-Jun are in the second year of season
                        year = season_int
                    
                    # Only fetch if this month is in the past or current
                    if year < current_year or (year == current_year and month_num <= current_month):
                        months_to_fetch.append((season, month))
            
            total_requests = len(months_to_fetch)
            self.progress.start_schedule(total_requests)
            self.games_list = []
            
            logger.info(f"Will fetch {total_requests} months (up to {current_date.strftime('%B %Y')})")
            
            completed = 0
            for season, month in months_to_fetch:
                season_int = int(season)
                self.progress.update_schedule(
                    completed,
                    f"Fetching {month} {season_int-1}-{season_int}..."
                )
                
                url = f"{self.BASE_URL}/leagues/NBA_{season}_games-{month}.html"
                soup = self._make_request(url)
                
                if soup:
                    schedule_table = soup.find('table', {'id': 'schedule'})
                    if schedule_table:
                        tbody = schedule_table.find('tbody')
                        if tbody:
                            for row in tbody.find_all('tr'):
                                if row.get('class') and 'thead' in row.get('class'):
                                    continue
                                
                                cells = row.find_all(['td', 'th'])
                                if len(cells) < 7:
                                    continue
                                
                                date_cell = cells[0]
                                visitor_cell = cells[2]
                                home_cell = cells[4]
                                box_score_cell = cells[6] if len(cells) > 6 else None
                                
                                box_score_link = None
                                if box_score_cell:
                                    link = box_score_cell.find('a')
                                    if link and link.get('href'):
                                        box_score_link = link.get('href')
                                
                                if not box_score_link:
                                    continue
                                
                                game_data = {
                                    'date': date_cell.get_text(strip=True),
                                    'visitor_team': visitor_cell.get_text(strip=True) if visitor_cell else '',
                                    'home_team': home_cell.get_text(strip=True) if home_cell else '',
                                    'box_score_url': f"{self.BASE_URL}{box_score_link}",
                                    'season': season
                                }
                                
                                self.games_list.append(game_data)
                
                completed += 1
            
            logger.info(f"✓ Found {len(self.games_list)} games")
            # Update to show completion correctly
            self.progress.update_schedule(completed, "Completed!")
            self.progress.complete_schedule(len(self.games_list))
            
        except Exception as e:
            logger.error(f"✗ Error in Phase 1: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.progress.error("schedule", str(e))
    
    # PHASE 2: Fetch Rosters & Injuries
    def scrape_rosters(self):
        """Phase 2: Fetch starting rosters and injuries"""
        try:
            if not self.games_list:
                logger.error("✗ No games found. Run Phase 1 first!")
                return
            
            logger.info("="*60)
            logger.info("👥 PHASE 2: Fetching Rosters & Injuries")
            logger.info("="*60)
            
            self.progress.start_roster(len(self.games_list))
            
            for idx, game in enumerate(self.games_list, 1):
                try:
                    if idx % 10 == 0:
                        logger.info(f"📊 Roster Progress: {idx}/{len(self.games_list)} ({(idx/len(self.games_list)*100):.1f}%)")
                    
                    self.progress.update_roster(
                        idx,
                        f"Game {idx}/{len(self.games_list)}: {game['visitor_team']} @ {game['home_team']}"
                    )
                    
                    game_info = self.get_game_starters_and_injuries(game['box_score_url'], game)
                    if game_info:
                        self.games_data.append(game_info)
                        
                except Exception as e:
                    logger.error(f"✗ Error getting rosters for game {idx}: {e}")
                    continue
            
            logger.info(f"✓ Collected rosters for {len(self.games_data)} games")
            self.progress.complete_roster()
            
        except Exception as e:
            logger.error(f"✗ Error in Phase 2: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.progress.error("roster", str(e))
    
    # PHASE 3: Fetch Play-by-Play
    def scrape_play_by_play(self):
        """Phase 3: Fetch play-by-play until first FG"""
        try:
            if not self.games_list:
                logger.error("✗ No games found. Run Phase 1 first!")
                return
            
            logger.info("="*60)
            logger.info("🏀 PHASE 3: Fetching Play-by-Play Data")
            logger.info("="*60)
            
            self.progress.start_pbp(len(self.games_list))
            
            for idx, game in enumerate(self.games_list, 1):
                try:
                    if idx % 10 == 0:
                        logger.info(f"📊 PBP Progress: {idx}/{len(self.games_list)} ({(idx/len(self.games_list)*100):.1f}%) - Total plays so far: {len(self.play_by_play_data)}")
                    
                    self.progress.update_pbp(
                        idx,
                        f"Game {idx}/{len(self.games_list)}: {game['visitor_team']} @ {game['home_team']}"
                    )
                    
                    pbp_data = self.get_play_by_play_until_first_fg(game['box_score_url'], game)
                    if pbp_data:
                        self.play_by_play_data.extend(pbp_data)
                        logger.info(f"✓ Game {idx}: Collected {len(pbp_data)} plays (Total: {len(self.play_by_play_data)})")
                    else:
                        logger.warning(f"⚠ Game {idx}: No play-by-play data found")
                        
                except Exception as e:
                    logger.error(f"✗ Error getting PBP for game {idx}: {e}")
                    continue
            
            logger.info("="*60)
            logger.info(f"✓ Collected {len(self.play_by_play_data)} total plays from {len(self.games_list)} games")
            logger.info("="*60)
            self.progress.complete_pbp()
            
        except Exception as e:
            logger.error(f"✗ Error in Phase 3: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.progress.error("pbp", str(e))
    
    def _get_most_recent_rosters(self) -> Dict[str, List[str]]:
        """Get the most recent starting roster for each team from historical data"""
        team_rosters = {}
        
        # If games_data is empty, try loading from CSV
        games_to_check = self.games_data
        if not games_to_check:
            logger.info("games_data is empty, attempting to load from CSV for roster data...")
            try:
                import os
                games_file = 'games_and_rosters.csv'
                if os.path.exists(games_file):
                    df = pd.read_csv(games_file).fillna('')
                    games_to_check = df.to_dict('records')
                    logger.info(f"Loaded {len(games_to_check)} games from CSV for roster lookup")
                else:
                    logger.warning(f"CSV file {games_file} not found. Cannot load rosters.")
                    return team_rosters
            except Exception as e:
                logger.error(f"Error loading games from CSV: {e}")
                return team_rosters
        
        # Go through games_data in reverse order (most recent first)
        for game in reversed(games_to_check):
            visitor_team = game.get('visitor_team', '')
            home_team = game.get('home_team', '')
            
            # Get visitor starters if we don't have them yet
            if visitor_team and visitor_team not in team_rosters:
                if 'visitor_starters' in game and isinstance(game['visitor_starters'], list):
                    team_rosters[visitor_team] = game['visitor_starters'][:5]
                else:
                    # Try to get from V_s columns
                    starters = []
                    for i in range(1, 6):
                        starter = game.get(f'V_s{i}', '')
                        if starter:
                            starters.append(starter)
                    if starters:
                        team_rosters[visitor_team] = starters
            
            # Get home starters if we don't have them yet
            if home_team and home_team not in team_rosters:
                if 'home_starters' in game and isinstance(game['home_starters'], list):
                    team_rosters[home_team] = game['home_starters'][:5]
                else:
                    # Try to get from H_s columns
                    starters = []
                    for i in range(1, 6):
                        starter = game.get(f'H_s{i}', '')
                        if starter:
                            starters.append(starter)
                    if starters:
                        team_rosters[home_team] = starters
        
        # Ensure each team has exactly 5 starters (pad with empty strings if needed)
        for team in team_rosters:
            while len(team_rosters[team]) < 5:
                team_rosters[team].append('')
            team_rosters[team] = team_rosters[team][:5]
        
        logger.info(f"Found rosters for {len(team_rosters)} teams from historical data")
        return team_rosters
    
    # PHASE 4: Fetch Upcoming Games (Today & Tomorrow)
    def scrape_upcoming(self, seasons: List[str] = ['2026']):
        """Phase 4: Fetch upcoming games (today and tomorrow)"""
        try:
            logger.info("="*60)
            logger.info("📅 PHASE 4: Fetching Upcoming Games (Today & Tomorrow)")
            logger.info("="*60)
            
            # Get today and tomorrow's dates
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            logger.info(f"Looking for games on {today} and {tomorrow}")
            
            self.progress.start_upcoming(1)
            self.progress.update_upcoming(0, "Fetching upcoming games...")
            
            upcoming_games = []
            season = seasons[0] if seasons else '2026'
            season_int = int(season)
            
            # Determine which months to check (today's and tomorrow's if they differ)
            months_to_check = set()
            months_to_check.add(today.strftime('%B').lower())
            if tomorrow.month != today.month:
                months_to_check.add(tomorrow.strftime('%B').lower())
                logger.info(f"Dates span multiple months, checking: {', '.join(months_to_check)}")
            
            # Check each relevant month
            for month_name in months_to_check:
                url = f"{self.BASE_URL}/leagues/NBA_{season}_games-{month_name}.html"
                logger.info(f"Fetching schedule from: {url}")
                soup = self._make_request(url)
                
                if soup:
                    schedule_table = soup.find('table', {'id': 'schedule'})
                    if schedule_table:
                        tbody = schedule_table.find('tbody')
                        if tbody:
                            for row in tbody.find_all('tr'):
                                if row.get('class') and 'thead' in row.get('class'):
                                    continue
                                
                                cells = row.find_all(['td', 'th'])
                                if len(cells) < 7:
                                    continue
                                
                                date_cell = cells[0]
                                visitor_cell = cells[2]
                                home_cell = cells[4]
                                box_score_cell = cells[6]
                                
                                # Parse date
                                date_text = date_cell.get_text(strip=True)
                                if not date_text:
                                    continue
                                
                                try:
                                    # Parse date like "Tue, Oct 29, 2025"
                                    game_date = datetime.strptime(date_text, '%a, %b %d, %Y').date()
                                except:
                                    try:
                                        # Try alternate format
                                        game_date = datetime.strptime(date_text, '%A, %B %d, %Y').date()
                                    except:
                                        continue
                                
                                # Only include games for today or tomorrow
                                if game_date not in [today, tomorrow]:
                                    continue
                                
                                # Check if game has started (has box score link)
                                box_score_link = box_score_cell.find('a')
                                if box_score_link and box_score_link.get('href'):
                                    # Game has started or finished, skip it
                                    continue
                                
                                visitor_team = visitor_cell.get_text(strip=True)
                                home_team = home_cell.get_text(strip=True)
                                
                                if visitor_team and home_team:
                                    upcoming_games.append({
                                        'date': date_text,
                                        'visitor_team': visitor_team,
                                        'home_team': home_team,
                                        'season': season
                                    })
                                    logger.info(f"Found upcoming game: {visitor_team} @ {home_team} on {date_text}")
            
            logger.info(f"Found {len(upcoming_games)} upcoming games")
            
            # Get most recent rosters from historical games_data
            team_recent_rosters = self._get_most_recent_rosters()
            
            self.upcoming_games_data = []
            
            for idx, game in enumerate(upcoming_games, 1):
                self.progress.update_upcoming(
                    idx,
                    f"Game {idx}/{len(upcoming_games)}: {game['visitor_team']} @ {game['home_team']}"
                )
                
                # Create game key
                visitor_code = get_team_code(game['visitor_team'])
                home_code = get_team_code(game['home_team'])
                date_short = format_date_short(game['date'])
                game_key = create_game_key(game['visitor_team'], game['home_team'], game['date'])
                
                # Get predicted rosters from recent games
                visitor_starters = team_recent_rosters.get(visitor_code, ['', '', '', '', ''])
                home_starters = team_recent_rosters.get(home_code, ['', '', '', '', ''])
                
                game_data = {
                    'game_key': game_key,
                    'date': date_short,
                    'matchup': f"{visitor_code}@{home_code}",
                    'visitor_team': visitor_code,
                    'home_team': home_code,
                    'visitor_team_full': game['visitor_team'],
                    'home_team_full': game['home_team'],
                    'status': 'upcoming',
                    'V_s1': visitor_starters[0],
                    'V_s2': visitor_starters[1],
                    'V_s3': visitor_starters[2],
                    'V_s4': visitor_starters[3],
                    'V_s5': visitor_starters[4],
                    'H_s1': home_starters[0],
                    'H_s2': home_starters[1],
                    'H_s3': home_starters[2],
                    'H_s4': home_starters[3],
                    'H_s5': home_starters[4]
                }
                
                self.upcoming_games_data.append(game_data)
            
            logger.info("="*60)
            logger.info(f"✓ Found {len(self.upcoming_games_data)} upcoming games")
            logger.info("="*60)
            self.progress.complete_upcoming()
            
        except Exception as e:
            logger.error(f"✗ Error in Phase 4: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.progress.error("upcoming", str(e))
    
    def save_to_csv(self):
        """Save data to CSV files"""
        logger.info("="*60)
        logger.info("💾 SAVING DATA TO CSV FILES")
        logger.info("="*60)
        
        if self.games_data:
            logger.info(f"Saving {len(self.games_data)} games to CSV...")
            df_games = pd.DataFrame(self.games_data)
            
            # Split visitor starters into separate columns
            for i in range(5):
                df_games[f'V_s{i+1}'] = df_games['visitor_starters'].apply(
                    lambda x: x[i] if isinstance(x, list) and len(x) > i else ''
                )
            
            # Split home starters into separate columns
            for i in range(5):
                df_games[f'H_s{i+1}'] = df_games['home_starters'].apply(
                    lambda x: x[i] if isinstance(x, list) and len(x) > i else ''
                )
            
            # Keep injuries as semicolon-separated
            df_games['visitor_injuries'] = df_games['visitor_injuries'].apply(lambda x: '; '.join(x) if x else '')
            df_games['home_injuries'] = df_games['home_injuries'].apply(lambda x: '; '.join(x) if x else '')
            
            # Drop the original list columns
            df_games = df_games.drop(['visitor_starters', 'home_starters'], axis=1)
            
            # Reorder columns for better readability
            column_order = ['game_key', 'date', 'matchup', 'visitor_team', 'home_team', 
                          'V_s1', 'V_s2', 'V_s3', 'V_s4', 'V_s5',
                          'H_s1', 'H_s2', 'H_s3', 'H_s4', 'H_s5',
                          'visitor_injuries', 'home_injuries', 'game_id', 'visitor_team_full', 'home_team_full']
            # Only include columns that exist
            column_order = [col for col in column_order if col in df_games.columns]
            df_games = df_games[column_order]
            
            output_file = 'games_and_rosters.csv'
            df_games.to_csv(output_file, index=False)
            logger.info(f"✓ Saved {len(df_games)} games to {output_file}")
        else:
            logger.warning("⚠ No game data to save (games_data is empty)")
        
        if self.play_by_play_data:
            logger.info(f"Saving {len(self.play_by_play_data)} plays to CSV...")
            df_pbp = pd.DataFrame(self.play_by_play_data)
            output_file = 'play_by_play_first_fg.csv'
            df_pbp.to_csv(output_file, index=False)
            logger.info(f"✓ Saved {len(df_pbp)} plays to {output_file}")
        else:
            logger.warning("⚠ No play-by-play data to save (play_by_play_data is empty)")
        
        # Save upcoming games data
        if hasattr(self, 'upcoming_games_data') and self.upcoming_games_data:
            logger.info(f"Saving {len(self.upcoming_games_data)} upcoming games to CSV...")
            df_upcoming = pd.DataFrame(self.upcoming_games_data)
            output_file = 'upcoming_games.csv'
            df_upcoming.to_csv(output_file, index=False)
            logger.info(f"✓ Saved {len(df_upcoming)} upcoming games to {output_file}")
        else:
            logger.info("ℹ No upcoming games data to save")
        
        logger.info("="*60)
    
    def get_preview_data(self) -> Dict:
        """Get preview of current data"""
        games_preview = []
        if self.games_data:
            # Get last 10 games
            for game in self.games_data[-10:]:
                preview_item = {
                    'game_key': game['game_key'],
                    'date': game['date'],
                    'matchup': game['matchup'],
                    'visitor_team': game['visitor_team'],
                    'home_team': game['home_team']
                }
                
                # Add individual starter columns
                starters = game.get('visitor_starters', [])
                for i in range(5):
                    preview_item[f'V_s{i+1}'] = starters[i] if i < len(starters) else ''
                
                starters = game.get('home_starters', [])
                for i in range(5):
                    preview_item[f'H_s{i+1}'] = starters[i] if i < len(starters) else ''
                
                games_preview.append(preview_item)
        
        pbp_preview = []
        if self.play_by_play_data:
            # Get last 20 plays
            for play in self.play_by_play_data[-20:]:
                pbp_preview.append({
                    'game_key': play['game_key'],
                    'date': play['date'],
                    'matchup': play['matchup'],
                    'visitor_team': play['visitor_team'],
                    'home_team': play['home_team'],
                    'time': play['time'],
                    'visitor_play': play['visitor_play'],
                    'home_play': play['home_play'],
                    'score': play['score']
                })
        
        return {
            'games_count': len(self.games_data),
            'plays_count': len(self.play_by_play_data),
            'games_preview': games_preview,
            'pbp_preview': pbp_preview
        }

