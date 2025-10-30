"""
Game Analyzer - Matches PBP data to rosters and highlights first shot makers/missers
"""
import re
from typing import Dict, List, Tuple, Optional


def normalize_name(name: str) -> str:
    """Normalize a name for comparison (remove extra spaces, lowercase)"""
    return ' '.join(name.lower().strip().split())


def extract_player_from_play(play_text: str) -> Optional[str]:
    """
    Extract player name from play text (e.g., 'D. Sabonismisses 2-pt...' -> 'D. Sabonis')
    Handles missing spaces between name and action verb
    """
    if not play_text:
        return None
    
    # Common action verbs in basketball plays
    action_verbs = [
        'makes', 'misses', 'missed', 'enters', 'offensive', 'defensive',
        'personal', 'shooting', 'technical', 'flagrant', 'traveling',
        'bad', 'lost', 'turnover', 'out', 'kicked', 'blocks', 'steals'
    ]
    
    # Try to find where the action verb starts
    play_lower = play_text.lower()
    earliest_verb_pos = len(play_text)
    found_verb = None
    
    for verb in action_verbs:
        pos = play_lower.find(verb)
        if pos != -1 and pos < earliest_verb_pos:
            earliest_verb_pos = pos
            found_verb = verb
    
    if found_verb:
        # Extract everything before the verb as the player name
        player_name = play_text[:earliest_verb_pos].strip()
        return player_name
    
    # Fallback: try to extract "X. LastName" pattern
    match = re.match(r'^([A-Z]\.\s*[A-Za-z]+)', play_text)
    if match:
        return match.group(1)
    
    return None


def match_player_to_roster(pbp_name: str, roster: List[str]) -> Optional[str]:
    """
    Match a PBP name (e.g., 'D. Sabonis') to a full roster name (e.g., 'Domantas Sabonis')
    
    Args:
        pbp_name: Name from play-by-play (First Initial. Last Name)
        roster: List of full player names
        
    Returns:
        Matched full name or None
    """
    if not pbp_name or not roster:
        return None
    
    # Normalize the PBP name
    pbp_normalized = normalize_name(pbp_name)
    
    # Extract initial and last name from PBP format
    # Handle cases like "D. Sabonis" or "D.Sabonis" or "D. De'Aaron"
    match = re.match(r'^([a-z])\.?\s*(.+)$', pbp_normalized)
    if not match:
        return None
    
    initial = match.group(1)
    last_name_part = match.group(2).strip()
    
    # Try to match with roster
    for full_name in roster:
        full_normalized = normalize_name(full_name)
        
        # Check if first initial matches and last name is in the full name
        if full_normalized.startswith(initial) and last_name_part in full_normalized:
            # Additional check: make sure it's actually the last name part
            parts = full_normalized.split()
            if len(parts) >= 2:
                # Check if last_name_part matches the actual last name
                if parts[-1].startswith(last_name_part) or last_name_part in ' '.join(parts[1:]):
                    return full_name
    
    return None


def analyze_game_first_shots(game_key: str, starters: List[str], pbp_plays: List[Dict]) -> Dict:
    """
    Analyze a game to determine detailed first shot information
    
    Args:
        game_key: Unique game identifier
        starters: List of all starters (visitor + home)
        pbp_plays: List of play-by-play dictionaries for this game
        
    Returns:
        Dict with player highlights: {player_name: [list of highlight_types]}
        Highlight types:
        - 'first_shot_made': Took and made the very first shot in the game
        - 'first_shot_missed': Took and missed the very first shot in the game
        - 'first_fg_made': Made the first field goal (but wasn't the first shot)
        - 'missed_shot': Missed a shot before the first FG (but wasn't the first shot)
        - 'free_throw': Took free throws before the first FG
    """
    highlights = {}
    first_shot_taken = False
    first_fg_made = False
    
    for play in pbp_plays:
        # Get the play text (could be from visitor or home)
        play_text = play.get('visitor_play') or play.get('home_play')
        if not play_text:
            continue
        
        # Extract player name from play
        pbp_player = extract_player_from_play(play_text)
        if not pbp_player:
            continue
        
        # Match to roster
        matched_player = match_player_to_roster(pbp_player, starters)
        if not matched_player:
            continue
        
        play_lower = play_text.lower()
        
        # Check if this is a field goal attempt (made or missed)
        is_made_fg = 'makes' in play_lower and ('jump shot' in play_lower or 'layup' in play_lower or 
                                                 'dunk' in play_lower or '3-pt' in play_lower or '2-pt' in play_lower)
        is_missed_fg = ('misses' in play_lower or 'missed' in play_lower) and ('jump shot' in play_lower or 'layup' in play_lower or 
                                                                                  'dunk' in play_lower or '3-pt' in play_lower or '2-pt' in play_lower)
        is_free_throw = 'free throw' in play_lower
        
        # Initialize player's highlights list if not exists
        if matched_player not in highlights:
            highlights[matched_player] = []
        
        # First shot of the game
        if not first_shot_taken and (is_made_fg or is_missed_fg):
            first_shot_taken = True
            if is_made_fg:
                highlights[matched_player].append('first_shot_made')
                first_fg_made = True
                break  # Game analysis done
            elif is_missed_fg:
                highlights[matched_player].append('first_shot_missed')
            continue
        
        # After first shot but before first FG
        if first_shot_taken and not first_fg_made:
            if is_made_fg:
                # This is the first made FG, but not the first shot
                highlights[matched_player].append('first_fg_made')
                first_fg_made = True
                break  # Game analysis done
            elif is_missed_fg:
                # Another missed shot
                highlights[matched_player].append('missed_shot')
            elif is_free_throw:
                # Free throw taken before first FG
                highlights[matched_player].append('free_throw')
    
    return highlights


def analyze_all_games(games_data: List[Dict], pbp_data: List[Dict]) -> List[Dict]:
    """
    Analyze all games and create a summary table with highlights
    
    Args:
        games_data: List of game dictionaries with roster information
        pbp_data: List of play-by-play dictionaries
        
    Returns:
        List of game analysis dictionaries
    """
    analysis_results = []
    
    # Group PBP data by game_key
    pbp_by_game = {}
    for play in pbp_data:
        game_key = play.get('game_key')
        if game_key:
            if game_key not in pbp_by_game:
                pbp_by_game[game_key] = []
            pbp_by_game[game_key].append(play)
    
    # Analyze each game
    for game in games_data:
        game_key = game.get('game_key')
        if not game_key:
            continue
        
        # Get all starters for this game
        all_starters = []
        visitor_starters = []
        home_starters = []
        
        for i in range(1, 6):
            v_starter = game.get(f'V_s{i}', '').strip()
            h_starter = game.get(f'H_s{i}', '').strip()
            
            if v_starter:
                visitor_starters.append(v_starter)
                all_starters.append(v_starter)
            if h_starter:
                home_starters.append(h_starter)
                all_starters.append(h_starter)
        
        # Get PBP plays for this game
        game_plays = pbp_by_game.get(game_key, [])
        
        # Analyze first shots
        highlights = analyze_game_first_shots(game_key, all_starters, game_plays)
        
        # Create analysis result
        analysis = {
            'game_key': game_key,
            'date': game.get('date', ''),
            'matchup': game.get('matchup', ''),
            'visitor_team': game.get('visitor_team', ''),
            'home_team': game.get('home_team', ''),
            'visitor_starters': visitor_starters,
            'home_starters': home_starters,
            'highlights': highlights,
            'pbp_count': len(game_plays)
        }
        
        analysis_results.append(analysis)
    
    return analysis_results

