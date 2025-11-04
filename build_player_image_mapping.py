"""
Build a mapping of player names to image URLs
Attempts to find player images from ESPN and NBA CDN
"""

import pandas as pd
import requests
import json
import time
from unidecode import unidecode
import re

def normalize_name_for_id(name):
    """Convert player name to a potential ID format"""
    # Remove accents and special characters
    try:
        name = unidecode(name)
    except:
        pass
    
    # Remove suffixes like Jr., Sr., II, III, IV
    name = re.sub(r'\s+(Jr\.?|Sr\.?|II|III|IV|V)$', '', name, flags=re.IGNORECASE)
    
    # Split into parts
    parts = name.lower().strip().split()
    if len(parts) < 2:
        return None
    
    first = parts[0]
    last = parts[-1]  # Use last part as last name
    
    # Common ID patterns:
    # Pattern 1: first initial + last name (no spaces/hyphens)
    last_clean = last.replace('-', '').replace("'", '').replace('.', '')
    pattern1 = f"{first[0]}{last_clean}"
    
    # Pattern 2: first name + last name
    pattern2 = f"{first}{last_clean}"
    
    return [pattern1, pattern2, last_clean]

def check_espn_image(player_id):
    """Check if ESPN image exists for a player ID"""
    url = f"https://a.espncdn.com/i/headshots/nba/players/full/{player_id}.png"
    try:
        response = requests.head(url, timeout=3, allow_redirects=True)
        # ESPN returns 200 even for missing images, but they redirect to a default
        # Check content-length or if it's a very small file (default image)
        if response.status_code == 200:
            content_length = response.headers.get('content-length', 0)
            if int(content_length) > 5000:  # Real player images are larger
                return url
    except:
        pass
    return None

def check_nba_image(player_id):
    """Check if NBA CDN image exists for a player ID"""
    url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
    try:
        response = requests.head(url, timeout=3, allow_redirects=True)
        if response.status_code == 200:
            return url
    except:
        pass
    return None

def try_find_espn_id_via_search(player_name):
    """Try to find ESPN player ID by searching ESPN API"""
    # ESPN has various API endpoints, try a few
    search_name = player_name.replace(' ', '%20')
    
    try:
        # Try ESPN's player search
        url = f"http://site.api.espn.com/apis/common/v3/search?query={search_name}&limit=1"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                for result in data['results']:
                    if result.get('type') == 'athlete' and 'athlete' in result:
                        athlete = result['athlete']
                        if athlete.get('league', {}).get('abbreviation') == 'NBA':
                            return athlete.get('id')
    except Exception as e:
        print(f"  Search API failed for {player_name}: {e}")
    
    return None

def build_player_mapping():
    """Build a mapping file for all players in our dataset"""
    print("Loading player names from dataset...")
    games_df = pd.read_csv('games_and_rosters.csv')
    
    players = set()
    for col in ['V_s1', 'V_s2', 'V_s3', 'V_s4', 'V_s5', 'H_s1', 'H_s2', 'H_s3', 'H_s4', 'H_s5']:
        players.update(games_df[col].dropna().unique())
    
    players = sorted([p for p in players if p and len(p.strip()) > 0])
    print(f"Found {len(players)} unique players\n")
    
    mapping = {}
    found_count = 0
    
    for i, player in enumerate(players, 1):
        print(f"[{i}/{len(players)}] Processing {player}...")
        
        # First try to find via ESPN search API
        espn_id = try_find_espn_id_via_search(player)
        
        if espn_id:
            # Verify the image exists
            espn_url = check_espn_image(espn_id)
            if espn_url:
                mapping[player] = {
                    'espn_id': espn_id,
                    'espn_url': espn_url,
                    'source': 'espn_api'
                }
                found_count += 1
                print(f"  ✓ Found via ESPN API: {espn_id}")
                time.sleep(0.2)  # Rate limiting
                continue
        
        # If API search didn't work, try ID patterns
        id_patterns = normalize_name_for_id(player)
        if not id_patterns:
            print(f"  ✗ Could not generate ID patterns")
            continue
        
        # Try each pattern
        for pattern in id_patterns:
            # Try as ESPN numeric ID (try common ranges)
            for potential_id in [pattern, f"{pattern}01", f"{pattern}1"]:
                espn_url = check_espn_image(potential_id)
                if espn_url:
                    mapping[player] = {
                        'espn_id': potential_id,
                        'espn_url': espn_url,
                        'source': 'pattern_match'
                    }
                    found_count += 1
                    print(f"  ✓ Found via pattern: {potential_id}")
                    break
            
            if player in mapping:
                break
            
            time.sleep(0.1)  # Small delay between attempts
        
        if player not in mapping:
            print(f"  ✗ No image found")
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"\n{'='*60}")
    print(f"Mapping complete!")
    print(f"Found images for {found_count}/{len(players)} players ({found_count/len(players)*100:.1f}%)")
    print(f"{'='*60}\n")
    
    # Save to JSON file
    output_file = 'player_image_mapping.json'
    with open(output_file, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"Saved mapping to {output_file}")
    
    return mapping

if __name__ == '__main__':
    mapping = build_player_mapping()


