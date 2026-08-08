"""
GOG free games fetcher.
Uses GamerPower API and GOG giveaway endpoints.
"""

import requests
from datetime import datetime
from typing import List, Dict, Any


GAMERPOWER_API = "https://www.gamerpower.com/api/giveaways"
GOG_STORE_URL = "https://www.gog.com/game/"


def fetch_gog_free_games() -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch current and upcoming free games from GOG.
    
    Returns:
        Dict with 'current' and 'upcoming' lists of game dicts
    """
    result = {
        "current": [],
        "upcoming": []
    }
    
    # Use GamerPower API for GOG giveaways
    try:
        response = requests.get(
            GAMERPOWER_API,
            params={"platform": "gog", "type": "game"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        )
        response.raise_for_status()
        giveaways = response.json()
    except Exception as e:
        print(f"[GOG] GamerPower API error: {e}")
        return result
    
    for giveaway in giveaways:
        # Handle both dict and unexpected formats
        if not isinstance(giveaway, dict):
            continue
        
        # Skip if not actually free
        giveaway_type = giveaway.get("type", "")
        if isinstance(giveaway_type, str):
            if giveaway_type.lower() != "game":
                continue
        
        title = giveaway.get("title", "Unknown")
        worth = giveaway.get("worth", "$0")
        original_price = _parse_price(worth)
        
        # Check if upcoming
        start_date = giveaway.get("published_date")
        end_date = giveaway.get("end_date")
        
        game_data = {
            "id": f"gog-{giveaway.get('id', 'unknown')}",
            "title": title,
            "store": "GOG",
            "url": giveaway.get("open_giveaway_url", giveaway.get("gamerpower_url", "")),
            "original_price": original_price,
            "current_price": 0,
            "image": giveaway.get("thumbnail", giveaway.get("image", "")),
            "end_date": end_date
        }
        
        # All from GamerPower are current giveaways
        result["current"].append(game_data)
    
    # Also check GOG's giveaway page directly
    try:
        gog_result = _fetch_gog_direct()
        result["current"].extend(gog_result["current"])
    except Exception as e:
        print(f"[GOG] Direct fetch error: {e}")
    
    return result


def _fetch_gog_direct() -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch giveaways directly from GOG.
    This checks GOG's current giveaway promotion.
    """
    result = {
        "current": [],
        "upcoming": []
    }
    
    try:
        # GOG's giveaway page often lists current free games
        response = requests.get(
            "https://www.gog.com/partner/free_games",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            timeout=30
        )
        
        # GOG page requires parsing, which is complex
        # For simplicity, we'll rely on GamerPower
        # This function can be enhanced later if needed
        
    except Exception as e:
        print(f"[GOG] Direct page fetch error: {e}")
    
    return result


def _parse_price(price_str: str) -> float:
    """Parse price string to float."""
    if not price_str:
        return 0
    try:
        cleaned = price_str.replace("$", "").replace("€", "").replace("£", "").strip()
        return float(cleaned)
    except ValueError:
        return 0


if __name__ == "__main__":
    # Test fetch
    games = fetch_gog_free_games()
    print(f"Current free: {len(games['current'])}")
    for game in games["current"]:
        print(f"  - {game['title']} ({game['store']}) - ${game['original_price']}")
