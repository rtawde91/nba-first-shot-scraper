"""
Flask Web Application for Basketball Reference Scraper
Provides web interface with real-time progress tracking
"""

from flask import Flask, render_template, jsonify, send_from_directory, request
import threading
import pandas as pd
import os
import numpy as np
from datetime import datetime
from scraper_with_progress import BasketballReferenceScraperWithProgress, ProgressTracker
from game_analyzer import analyze_all_games
from nba_team_mappings import get_team_code, create_game_key, format_date_short
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global progress tracker and scraper instance
progress_tracker = ProgressTracker()
scraper_instance = None
scraper_thread = None


def load_data_from_csv():
    """Load game and PBP data from CSV files"""
    games_file = 'games_and_rosters.csv'
    pbp_file = 'play_by_play_first_fg.csv'
    
    if not os.path.exists(games_file) or not os.path.exists(pbp_file):
        raise FileNotFoundError("CSV files not found. Please run the scraper first.")
    
    # Load games data - replace NaN with empty strings
    df_games = pd.read_csv(games_file).fillna('')
    games_data = []
    
    for _, row in df_games.iterrows():
        game = row.to_dict()
        
        # Check if we have the new format (V_s1, V_s2, etc.) or old format (visitor_starters, home_starters)
        if 'V_s1' not in game and 'visitor_starters' in game:
            # Old format - split semicolon-separated strings into individual columns
            visitor_starters_str = str(game.get('visitor_starters', '')).strip()
            home_starters_str = str(game.get('home_starters', '')).strip()
            
            # Split and clean
            if visitor_starters_str:
                visitor_starters = [s.strip() for s in visitor_starters_str.split(';') if s.strip()]
            else:
                visitor_starters = []
            
            if home_starters_str:
                home_starters = [s.strip() for s in home_starters_str.split(';') if s.strip()]
            else:
                home_starters = []
            
            # Add individual starter columns
            for i in range(5):
                game[f'V_s{i+1}'] = visitor_starters[i] if i < len(visitor_starters) else ''
                game[f'H_s{i+1}'] = home_starters[i] if i < len(home_starters) else ''
        else:
            # New format - ensure all columns exist
            for i in range(1, 6):
                if f'V_s{i}' not in game:
                    game[f'V_s{i}'] = ''
                if f'H_s{i}' not in game:
                    game[f'H_s{i}'] = ''
        
        # Generate missing fields for old format CSVs
        if 'game_key' not in game or not game.get('game_key'):
            visitor_team = str(game.get('visitor_team', '')).strip()
            home_team = str(game.get('home_team', '')).strip()
            date_str = str(game.get('date', '')).strip()
            
            if visitor_team and home_team and date_str:
                # Create game_key
                game['game_key'] = create_game_key(visitor_team, home_team, date_str)
                
                # Create matchup (short form)
                visitor_code = get_team_code(visitor_team)
                home_code = get_team_code(home_team)
                game['matchup'] = f"{visitor_code}@{home_code}"
                
                # Format date
                game['date'] = format_date_short(date_str)
                
                # Store full names for reference
                game['visitor_team_full'] = visitor_team
                game['home_team_full'] = home_team
                
                # Update team codes
                game['visitor_team'] = visitor_code
                game['home_team'] = home_code
        
        games_data.append(game)
    
    # Load PBP data - replace NaN with empty strings
    df_pbp = pd.read_csv(pbp_file).fillna('')
    pbp_data = df_pbp.to_dict('records')
    
    logger.info(f"Loaded {len(games_data)} games and {len(pbp_data)} plays from CSV files")
    
    return games_data, pbp_data


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/analysis')
def analysis_page():
    """Serve the analysis page"""
    return render_template('analysis.html')


@app.route('/test_api')
def test_api_page():
    """Serve the API test page"""
    return render_template('test_api.html')


@app.route('/api/status')
def get_status():
    """Get current scraping status"""
    status = progress_tracker.get_status()
    
    # Add file modification timestamps for each phase
    csv_files = {
        'schedule': 'games_and_rosters.csv',
        'roster': 'games_and_rosters.csv',
        'pbp': 'play_by_play_first_fg.csv',
        'upcoming': 'upcoming_games.csv'
    }
    
    for phase, filename in csv_files.items():
        if os.path.exists(filename):
            try:
                mod_time = os.path.getmtime(filename)
                # Format as readable timestamp
                dt = datetime.fromtimestamp(mod_time)
                status[f'{phase}_last_updated'] = dt.strftime('%m/%d/%Y %I:%M:%S %p')
            except Exception as e:
                logger.error(f"Error getting file modification time for {filename}: {e}")
                status[f'{phase}_last_updated'] = None
        else:
            status[f'{phase}_last_updated'] = None
    
    return jsonify(status)


@app.route('/api/preview')
def get_preview():
    """Get preview of scraped data"""
    from_csv = request.args.get('from_csv', 'false').lower() == 'true'
    
    # Load from CSV if requested
    if from_csv:
        try:
            games_data, pbp_data = load_data_from_csv()
            
            # Create games preview (limit to last 50)
            games_preview = []
            for game in games_data[-50:]:
                games_preview.append({
                    'game_key': game.get('game_key', ''),
                    'date': game.get('date', ''),
                    'matchup': game.get('matchup', ''),
                    'visitor_team': game.get('visitor_team', ''),
                    'home_team': game.get('home_team', ''),
                    'V_s1': game.get('V_s1', ''),
                    'V_s2': game.get('V_s2', ''),
                    'V_s3': game.get('V_s3', ''),
                    'V_s4': game.get('V_s4', ''),
                    'V_s5': game.get('V_s5', ''),
                    'H_s1': game.get('H_s1', ''),
                    'H_s2': game.get('H_s2', ''),
                    'H_s3': game.get('H_s3', ''),
                    'H_s4': game.get('H_s4', ''),
                    'H_s5': game.get('H_s5', '')
                })
            
            # Create PBP preview (limit to last 100)
            pbp_preview = []
            for play in pbp_data[-100:]:
                pbp_preview.append({
                    'game_key': play.get('game_key', ''),
                    'date': play.get('date', ''),
                    'matchup': play.get('matchup', ''),
                    'visitor_team': play.get('visitor_team', ''),
                    'home_team': play.get('home_team', ''),
                    'time': play.get('time', ''),
                    'visitor_play': play.get('visitor_play', ''),
                    'home_play': play.get('home_play', ''),
                    'score': play.get('score', '')
                })
            
            return jsonify({
                'games_count': len(games_data),
                'plays_count': len(pbp_data),
                'games_preview': games_preview,
                'pbp_preview': pbp_preview
            })
        except Exception as e:
            logger.error(f"Error loading preview from CSV: {e}")
            return jsonify({
                'games_count': 0,
                'plays_count': 0,
                'games_preview': [],
                'pbp_preview': []
            })
    
    # Otherwise load from scraper instance
    if scraper_instance:
        preview = scraper_instance.get_preview_data()
        return jsonify(preview)
    return jsonify({
        'games_count': 0,
        'plays_count': 0,
        'games_preview': [],
        'pbp_preview': []
    })


@app.route('/api/pbp')
def get_all_pbp():
    """Get all play-by-play data from CSV"""
    try:
        _, pbp_data = load_data_from_csv()
        
        # Convert all PBP data to simplified format
        pbp_all = []
        for play in pbp_data:
            pbp_all.append({
                'game_key': play.get('game_key', ''),
                'date': play.get('date', ''),
                'matchup': play.get('matchup', ''),
                'visitor_team': play.get('visitor_team', ''),
                'home_team': play.get('home_team', ''),
                'time': play.get('time', ''),
                'visitor_play': play.get('visitor_play', ''),
                'home_play': play.get('home_play', ''),
                'score': play.get('score', '')
            })
        
        return jsonify({
            'plays_count': len(pbp_all),
            'pbp_data': pbp_all
        })
    except Exception as e:
        logger.error(f"Error loading PBP data from CSV: {e}")
        return jsonify({'error': str(e), 'plays_count': 0, 'pbp_data': []}), 500


@app.route('/api/analysis')
def get_analysis():
    """Get first shot analysis for all games"""
    from_csv = request.args.get('from_csv', 'false').lower() == 'true'
    
    try:
        # Load from CSV if requested
        if from_csv:
            try:
                games_data, pbp_data = load_data_from_csv()
                analysis = analyze_all_games(games_data, pbp_data)
                
                # Calculate player scores from historical data
                player_scores = calculate_player_scores(analysis)
                
                # Load upcoming games
                upcoming_games = load_upcoming_games()
                
                return jsonify({
                    'analysis': analysis,
                    'player_scores': player_scores,
                    'upcoming_games': upcoming_games
                })
            except FileNotFoundError as e:
                return jsonify({'error': str(e), 'analysis': [], 'player_scores': {}, 'upcoming_games': []}), 404
            except Exception as e:
                logger.error(f"Error loading from CSV: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return jsonify({'error': f"Error loading CSV files: {str(e)}", 'analysis': [], 'player_scores': {}, 'upcoming_games': []}), 500
        
        # Otherwise load from scraper instance
        if scraper_instance and scraper_instance.games_data and scraper_instance.play_by_play_data:
            # Convert games_data to include split starters
            games_with_starters = []
            for game in scraper_instance.games_data:
                game_copy = game.copy()
                # Split starters into individual columns if they're still in list format
                if 'visitor_starters' in game_copy and isinstance(game_copy['visitor_starters'], list):
                    for i, starter in enumerate(game_copy['visitor_starters'][:5], 1):
                        game_copy[f'V_s{i}'] = starter
                if 'home_starters' in game_copy and isinstance(game_copy['home_starters'], list):
                    for i, starter in enumerate(game_copy['home_starters'][:5], 1):
                        game_copy[f'H_s{i}'] = starter
                games_with_starters.append(game_copy)
            
            analysis = analyze_all_games(games_with_starters, scraper_instance.play_by_play_data)
            player_scores = calculate_player_scores(analysis)
            upcoming_games = []
            if hasattr(scraper_instance, 'upcoming_games_data'):
                upcoming_games = scraper_instance.upcoming_games_data
            
            return jsonify({
                'analysis': analysis,
                'player_scores': player_scores,
                'upcoming_games': upcoming_games
            })
        
        return jsonify({'analysis': [], 'player_scores': {}, 'upcoming_games': []})
        
    except Exception as e:
        logger.error(f"Error generating analysis: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e), 'analysis': [], 'player_scores': {}, 'upcoming_games': []}), 500


def calculate_player_scores(analysis):
    """
    Calculate player scores based on first shot performance
    
    Scoring:
    - first_shot_made: +2.0 (took and made the first shot of the game)
    - first_shot_missed: +1.0 (took and missed the first shot of the game)
    - first_fg_made: +0.75 (made first FG but wasn't the first shot)
    - missed_shot: +0.5 (missed a shot before first FG, but wasn't the first shot)
    - free_throw: +0.25 (took free throws before first FG - counts once per game)
    """
    player_scores = {}
    
    # Score values for each action type
    score_values = {
        'first_shot_made': 2.0,
        'first_shot_missed': 1.0,
        'first_fg_made': 0.75,
        'missed_shot': 0.5,
        'free_throw': 0.25
    }
    
    for game in analysis:
        highlights = game.get('highlights', {})
        visitor_starters = game.get('visitor_starters', [])
        home_starters = game.get('home_starters', [])
        game_key = game.get('game_key', '')
        game_date = game.get('date', '')
        game_matchup = game.get('matchup', '')
        
        all_starters = visitor_starters + home_starters
        
        for player in all_starters:
            if not player or player == '':
                continue
            
            if player not in player_scores:
                player_scores[player] = {
                    'shot_score': 0.0,
                    'games_started': 0,
                    'game_details': []  # Track individual game contributions
                }
            
            player_scores[player]['games_started'] += 1
            
            # Get the list of highlight actions for this player in this game
            game_score = 0.0
            actions = []
            
            if player in highlights:
                highlight_list = highlights[player]  # This is a list of actions
                
                # Deduplicate free throws - only count once per game
                unique_highlights = []
                has_free_throw = False
                for hl in highlight_list:
                    if hl == 'free_throw':
                        if not has_free_throw:
                            unique_highlights.append(hl)
                            has_free_throw = True
                    else:
                        unique_highlights.append(hl)
                
                # Calculate score for each unique action
                for highlight_type in unique_highlights:
                    if highlight_type in score_values:
                        action_score = score_values[highlight_type]
                        game_score += action_score
                        actions.append({
                            'type': highlight_type,
                            'score': action_score
                        })
                
                player_scores[player]['shot_score'] += game_score
            
            # Record game details for this player
            player_scores[player]['game_details'].append({
                'game_key': game_key,
                'date': game_date,
                'matchup': game_matchup,
                'actions': actions,
                'game_score': game_score
            })
    
    return player_scores


def load_upcoming_games():
    """Load upcoming games from CSV"""
    upcoming_file = 'upcoming_games.csv'
    
    if not os.path.exists(upcoming_file):
        return []
    
    try:
        df_upcoming = pd.read_csv(upcoming_file).fillna('')
        upcoming_games = df_upcoming.to_dict('records')
        return upcoming_games
    except Exception as e:
        logger.error(f"Error loading upcoming games: {e}")
        return []


@app.route('/api/start/schedule', methods=['POST'])
def start_schedule():
    """Start Phase 1: Schedule fetching"""
    global scraper_instance, scraper_thread
    
    if progress_tracker.schedule_status == "running":
        return jsonify({'error': 'Schedule scraping already in progress'}), 400
    
    def run_schedule():
        global scraper_instance
        if not scraper_instance:
            scraper_instance = BasketballReferenceScraperWithProgress(progress_tracker)
        scraper_instance.scrape_schedule(seasons=['2026'])
    
    scraper_thread = threading.Thread(target=run_schedule, daemon=True)
    scraper_thread.start()
    
    return jsonify({'message': 'Phase 1: Schedule scraping started'})


@app.route('/api/start/roster', methods=['POST'])
def start_roster():
    """Start Phase 2: Roster fetching"""
    global scraper_instance, scraper_thread
    
    if not scraper_instance or not scraper_instance.games_list:
        return jsonify({'error': 'Run Phase 1 (Schedule) first!'}), 400
    
    if progress_tracker.roster_status == "running":
        return jsonify({'error': 'Roster scraping already in progress'}), 400
    
    def run_roster():
        scraper_instance.scrape_rosters()
    
    scraper_thread = threading.Thread(target=run_roster, daemon=True)
    scraper_thread.start()
    
    return jsonify({'message': 'Phase 2: Roster scraping started'})


@app.route('/api/start/pbp', methods=['POST'])
def start_pbp():
    """Start Phase 3: Play-by-play fetching"""
    global scraper_instance, scraper_thread
    
    if not scraper_instance or not scraper_instance.games_list:
        return jsonify({'error': 'Run Phase 1 (Schedule) first!'}), 400
    
    if progress_tracker.pbp_status == "running":
        return jsonify({'error': 'Play-by-play scraping already in progress'}), 400
    
    def run_pbp():
        scraper_instance.scrape_play_by_play()
        scraper_instance.save_to_csv()
    
    scraper_thread = threading.Thread(target=run_pbp, daemon=True)
    scraper_thread.start()
    
    return jsonify({'message': 'Phase 3: Play-by-play scraping started'})


@app.route('/api/start/upcoming', methods=['POST'])
def start_upcoming():
    """Start Phase 4: Upcoming games fetching"""
    global scraper_instance, scraper_thread
    
    if not scraper_instance:
        scraper_instance = BasketballReferenceScraperWithProgress(progress_tracker)
    
    if progress_tracker.upcoming_status == "running":
        return jsonify({'error': 'Upcoming games scraping already in progress'}), 400
    
    def run_upcoming():
        scraper_instance.scrape_upcoming(seasons=['2026'])
        scraper_instance.save_to_csv()
    
    scraper_thread = threading.Thread(target=run_upcoming, daemon=True)
    scraper_thread.start()
    
    return jsonify({'message': 'Phase 4: Upcoming games scraping started'})


@app.route('/api/start/full_cycle', methods=['POST'])
def start_full_cycle():
    """Start all 4 phases in sequence"""
    global scraper_instance, scraper_thread
    
    if (progress_tracker.schedule_status == "running" or 
        progress_tracker.roster_status == "running" or 
        progress_tracker.pbp_status == "running" or
        progress_tracker.upcoming_status == "running"):
        return jsonify({'error': 'A phase is already running'}), 400
    
    def run_full_cycle():
        global scraper_instance
        scraper_instance = BasketballReferenceScraperWithProgress(progress_tracker)
        
        # Phase 1: Schedule
        scraper_instance.scrape_schedule(seasons=['2026'])
        
        # Phase 2: Rosters (only if Phase 1 succeeded)
        if scraper_instance.games_list:
            scraper_instance.scrape_rosters()
        
        # Phase 3: Play-by-Play (only if Phase 1 succeeded)
        if scraper_instance.games_list:
            scraper_instance.scrape_play_by_play()
        
        # Phase 4: Upcoming Games
        scraper_instance.scrape_upcoming(seasons=['2026'])
        
        # Save all data
        scraper_instance.save_to_csv()
    
    scraper_thread = threading.Thread(target=run_full_cycle, daemon=True)
    scraper_thread.start()
    
    return jsonify({'message': 'Full cycle started - all 4 phases will run sequentially'})


@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    if scraper_instance:
        return jsonify({
            'total_games': len(scraper_instance.games_data),
            'total_plays': len(scraper_instance.play_by_play_data),
            'upcoming_games': len(scraper_instance.upcoming_games_data) if hasattr(scraper_instance, 'upcoming_games_data') else 0
        })
    return jsonify({'total_games': 0, 'total_plays': 0, 'upcoming_games': 0})


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏀 Basketball Reference Scraper - 4-Phase System + Full Cycle")
    print("="*70)
    print("\n📅 Season: 2025-26 NBA Season")
    print("\nStarting server...")
    print("\n📊 Open your browser and go to: http://localhost:8080")
    print("\n   4-Phase Scraping System:")
    print("   Phase 1: 📅 Fetch game schedule")
    print("   Phase 2: 👥 Collect rosters & injuries")
    print("   Phase 3: 🏀 Get play-by-play until first FG")
    print("   Phase 4: 🔮 Get upcoming games (today & tomorrow)")
    print("\n   Features:")
    print("   - Separate progress bars for each phase")
    print("   - Independent start buttons")
    print("   - Full Cycle button (runs all 4 phases)")
    print("   - Real-time progress tracking")
    print("   - Live data preview in tables")
    print("   - Auto-refresh every 30 seconds")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)

