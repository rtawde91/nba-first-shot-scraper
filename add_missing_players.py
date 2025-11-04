"""
Add missing players to the mapping by scraping Basketball Reference
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd
import re

def get_player_id_from_bbref(player_name):
    """
    Search Basketball Reference for a player and extract their NBA.com ID
    """
    try:
        # Format name for search
        search_name = player_name.replace(' ', '+')
        search_url = f"https://www.basketball-reference.com/search/search.fcgi?search={search_name}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10, allow_redirects=True)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check if we landed directly on a player page
        if '/players/' in response.url:
            # We're on a player page, look for NBA.com link or ID
            # Try to find the player's NBA ID from various sources on the page
            
            # Method 1: Look for data-id attributes
            player_header = soup.find('div', {'id': 'meta'})
            if player_header:
                # Sometimes NBA ID is in data attributes
                links = player_header.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    # Look for NBA.com links
                    if 'nba.com/player/' in href:
                        match = re.search(r'/player/(\d+)', href)
                        if match:
                            return match.group(1)
                    # Look for stats.nba.com links
                    if 'stats.nba.com' in href and 'player/' in href:
                        match = re.search(r'[?&]PlayerID=(\d+)', href)
                        if match:
                            return match.group(1)
            
            # Method 2: Try to extract from the page source (sometimes embedded in JavaScript)
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    match = re.search(r'"nba_player_id"\s*:\s*"?(\d+)"?', script.string)
                    if match:
                        return match.group(1)
        
        # If search results page, look for the first result
        search_results = soup.find('div', {'id': 'players'})
        if search_results:
            first_result = search_results.find('div', {'class': 'search-item'})
            if first_result:
                link = first_result.find('a', href=True)
                if link and '/players/' in link['href']:
                    # Follow the link to the player page
                    player_url = f"https://www.basketball-reference.com{link['href']}"
                    return get_player_id_from_bbref_url(player_url, headers)
        
    except Exception as e:
        print(f"    Error searching for {player_name}: {e}")
    
    return None

def get_player_id_from_bbref_url(url, headers):
    """Get NBA ID from a specific Basketball Reference player page"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for NBA.com links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if 'nba.com/player/' in href:
                match = re.search(r'/player/(\d+)', href)
                if match:
                    return match.group(1)
            if 'stats.nba.com' in href and 'PlayerID=' in href:
                match = re.search(r'PlayerID=(\d+)', href)
                if match:
                    return match.group(1)
        
        # Check scripts
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                match = re.search(r'"nba_player_id"\s*:\s*"?(\d+)"?', script.string)
                if match:
                    return match.group(1)
    
    except Exception as e:
        print(f"    Error fetching {url}: {e}")
    
    return None

def add_missing_players():
    """Add missing players to the mapping"""
    print("\n" + "="*60)
    print("Adding Missing Players to Mapping")
    print("="*60 + "\n")
    
    # Load existing mapping
    with open('player_image_mapping.json', 'r') as f:
        mapping = json.load(f)
    
    print(f"Current mapping has {len(mapping)} players")
    
    # Load our players
    games_df = pd.read_csv('games_and_rosters.csv')
    our_players = set()
    for col in ['V_s1', 'V_s2', 'V_s3', 'V_s4', 'V_s5', 'H_s1', 'H_s2', 'H_s3', 'H_s4', 'H_s5']:
        our_players.update(games_df[col].dropna().unique())
    our_players = sorted([p for p in our_players if p and len(p.strip()) > 0])
    
    # Find unmapped players
    unmapped = [p for p in our_players if p not in mapping]
    print(f"Found {len(unmapped)} unmapped players\n")
    
    if not unmapped:
        print("✓ All players already mapped!")
        return
    
    print(f"Attempting to find NBA IDs for unmapped players...")
    print("(This may take a while...)\n")
    
    added = 0
    failed = []
    
    for i, player in enumerate(unmapped, 1):
        print(f"[{i}/{len(unmapped)}] Searching for {player}...")
        
        nba_id = get_player_id_from_bbref(player)
        
        if nba_id:
            parts = player.split()
            first_name = parts[0] if parts else player
            last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
            
            mapping[player] = {
                'nba_id': nba_id,
                'nba_url': f"https://cdn.nba.com/headshots/nba/latest/1040x760/{nba_id}.png",
                'first_name': first_name,
                'last_name': last_name,
                'source': 'basketball_reference'
            }
            added += 1
            print(f"  ✓ Found NBA ID: {nba_id}")
        else:
            failed.append(player)
            print(f"  ✗ Could not find NBA ID")
        
        time.sleep(1)  # Rate limiting - be respectful
    
    # Save updated mapping
    with open('player_image_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  Added: {added} new players")
    print(f"  Total mapped: {len(mapping)}/{len(our_players)} ({len(mapping)/len(our_players)*100:.1f}%)")
    print(f"  Still unmapped: {len(failed)}")
    
    if failed:
        print(f"\nPlayers still unmapped:")
        for p in failed[:20]:
            print(f"    - {p}")
        if len(failed) > 20:
            print(f"    ... and {len(failed)-20} more")
    
    print(f"{'='*60}\n")
    print(f"✓ Saved updated mapping to player_image_mapping.json")

if __name__ == '__main__':
    add_missing_players()


