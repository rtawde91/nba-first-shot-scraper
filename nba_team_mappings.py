"""
NBA Team Name to 3-Letter Code Mappings
Based on official NBA team abbreviations
"""

NBA_TEAM_MAPPINGS = {
    # Full team names to 3-letter codes
    'Atlanta Hawks': 'ATL',
    'Boston Celtics': 'BOS',
    'Brooklyn Nets': 'BRK',
    'Charlotte Hornets': 'CHA',
    'Chicago Bulls': 'CHI',
    'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL',
    'Denver Nuggets': 'DEN',
    'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW',
    'Houston Rockets': 'HOU',
    'Indiana Pacers': 'IND',
    'Los Angeles Clippers': 'LAC',
    'Los Angeles Lakers': 'LAL',
    'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA',
    'Milwaukee Bucks': 'MIL',
    'Minnesota Timberwolves': 'MIN',
    'New Orleans Pelicans': 'NOP',
    'New York Knicks': 'NYK',
    'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL',
    'Philadelphia 76ers': 'PHI',
    'Phoenix Suns': 'PHO',
    'Portland Trail Blazers': 'POR',
    'Sacramento Kings': 'SAC',
    'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR',
    'Utah Jazz': 'UTA',
    'Washington Wizards': 'WAS',
}

def get_team_code(team_name: str) -> str:
    """
    Convert full team name to 3-letter code
    Returns the code if found, otherwise returns the original name
    """
    return NBA_TEAM_MAPPINGS.get(team_name, team_name)

def create_game_key(visitor_team: str, home_team: str, date_str: str) -> str:
    """
    Create a unique game key in format: VIS@HOM_MMDDYYYY
    
    Args:
        visitor_team: Visitor team name (full or code)
        home_team: Home team name (full or code)
        date_str: Date string in format like "Mon, Oct 27, 2025"
    
    Returns:
        Game key like "OKC@DAL_10272025"
    """
    from datetime import datetime
    
    # Convert team names to codes
    visitor_code = get_team_code(visitor_team)
    home_code = get_team_code(home_team)
    
    # Parse the date string
    # Handle formats like "Mon, Oct 27, 2025" or "Tue, Oct 22, 2025"
    try:
        # Remove day of week if present
        if ',' in date_str:
            parts = date_str.split(',')
            if len(parts) >= 2:
                date_part = ','.join(parts[1:]).strip()
            else:
                date_part = date_str
        else:
            date_part = date_str
        
        # Try to parse the date
        parsed_date = datetime.strptime(date_part, '%b %d, %Y')
        date_formatted = parsed_date.strftime('%m%d%Y')
    except:
        # If parsing fails, try to extract numbers
        import re
        numbers = re.findall(r'\d+', date_str)
        if len(numbers) >= 3:
            month, day, year = numbers[0], numbers[1], numbers[2]
            date_formatted = f"{month.zfill(2)}{day.zfill(2)}{year}"
        else:
            date_formatted = "UNKNOWN"
    
    return f"{visitor_code}@{home_code}_{date_formatted}"

def format_date_short(date_str: str) -> str:
    """
    Convert date from "Mon, Oct 27, 2025" to "10/27/2025"
    
    Args:
        date_str: Date string like "Mon, Oct 27, 2025"
    
    Returns:
        Formatted date like "10/27/2025"
    """
    from datetime import datetime
    
    try:
        # Remove day of week if present
        if ',' in date_str:
            parts = date_str.split(',')
            if len(parts) >= 2:
                date_part = ','.join(parts[1:]).strip()
            else:
                date_part = date_str
        else:
            date_part = date_str
        
        # Parse and reformat
        parsed_date = datetime.strptime(date_part, '%b %d, %Y')
        return parsed_date.strftime('%m/%d/%Y')
    except:
        # If parsing fails, return original
        return date_str

