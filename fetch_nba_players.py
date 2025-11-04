"""
Fetch NBA player data and build image URL mapping
"""

import requests
import json
import pandas as pd
import time

def fetch_nba_players():
    """Fetch all NBA players from stats.nba.com API"""
    url = "https://stats.nba.com/stats/commonallplayers"
    params = {
        'LeagueID': '00',
        'Season': '2024-25',
        'IsOnlyCurrentSeason': '1'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com',
        'x-nba-stats-origin': 'stats',
        'x-nba-stats-token': 'true'
    }
    
    try:
        print("Fetching NBA player data...")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract player data
        headers_list = data['resultSets'][0]['headers']
        rows = data['resultSets'][0]['rowSet']
        
        # Find column indices
        id_idx = headers_list.index('PERSON_ID')
        name_idx = headers_list.index('DISPLAY_LAST_COMMA_FIRST')
        
        players = {}
        for row in rows:
            player_id = str(row[id_idx])
            # Name is in format "Last, First" - convert to "First Last"
            name_parts = row[name_idx].split(', ')
            if len(name_parts) == 2:
                player_name = f"{name_parts[1]} {name_parts[0]}"
            else:
                player_name = row[name_idx]
            
            players[player_name] = {
                'nba_id': player_id,
                'nba_url': f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
            }
        
        print(f"✓ Fetched {len(players)} NBA players")
        return players
        
    except Exception as e:
        print(f"✗ Error fetching NBA player data: {e}")
        return None

def build_mapping():
    """Build mapping for players in our dataset"""
    print("\n" + "="*60)
    print("Building Player Image Mapping")
    print("="*60 + "\n")
    
    # Get our players
    print("Loading players from dataset...")
    games_df = pd.read_csv('games_and_rosters.csv')
    
    our_players = set()
    for col in ['V_s1', 'V_s2', 'V_s3', 'V_s4', 'V_s5', 'H_s1', 'H_s2', 'H_s3', 'H_s4', 'H_s5']:
        our_players.update(games_df[col].dropna().unique())
    
    our_players = sorted([p for p in our_players if p and len(p.strip()) > 0])
    print(f"Found {len(our_players)} unique players in our dataset\n")
    
    # Fetch NBA player data
    nba_players = fetch_nba_players()
    
    if not nba_players:
        print("Failed to fetch NBA player data. Cannot build mapping.")
        return
    
    # Match our players to NBA players
    mapping = {}
    matched = 0
    unmatched = []
    
    print("\nMatching players...")
    for player in our_players:
        if player in nba_players:
            mapping[player] = nba_players[player]
            matched += 1
        else:
            # Try fuzzy matching (case-insensitive, accent-insensitive)
            player_lower = player.lower().replace('.', '')
            found = False
            
            for nba_name, nba_data in nba_players.items():
                nba_name_lower = nba_name.lower().replace('.', '')
                if player_lower == nba_name_lower:
                    mapping[player] = nba_data
                    matched += 1
                    found = True
                    break
            
            if not found:
                unmatched.append(player)
    
    print(f"\n{'='*60}")
    print(f"Matching Results:")
    print(f"  Matched: {matched}/{len(our_players)} ({matched/len(our_players)*100:.1f}%)")
    if unmatched:
        print(f"  Unmatched: {len(unmatched)}")
        print(f"\nUnmatched players:")
        for p in unmatched[:20]:  # Show first 20
            print(f"    - {p}")
        if len(unmatched) > 20:
            print(f"    ... and {len(unmatched)-20} more")
    print(f"{'='*60}\n")
    
    # Save mapping
    output_file = 'player_image_mapping.json'
    with open(output_file, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"✓ Saved mapping to {output_file}")
    print(f"\nSample mappings:")
    for player, data in list(mapping.items())[:5]:
        print(f"  {player}: {data['nba_url']}")

if __name__ == '__main__':
    build_mapping()


