"""
Steam free games fetcher.
Uses SteamDB data via third-party API and Steam store.
"""

import requests
from datetime import datetime
from typing import List, Dict, Any


STEAMDB_API_URL = "https://steamdb.info/api/FreeGames/"
STEAM_STORE_URL = "https://store.steampowered.com/app/"


def fetch_steam_free_games() -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch current and upcoming free games from Steam.
    
    Returns:
        Dict with 'current' and 'upcoming' lists of game dicts
    """
    result = {
        "current": [],
        "upcoming": []
    }
    
    try:
        response = requests.get(
            "https://api.steamdb.info/api/FreeGames/",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            timeout=30
        )
        
        # If SteamDB API fails, try alternative approach
        if response.status_code != 200:
            return _fetch_via_gamerpower("steam")
        
        data = response.json()
    except Exception as e:
        print(f"[Steam] SteamDB API error: {e}, trying GamerPower...")
        return _fetch_via_gamerpower("steam")
    
    # Parse SteamDB response
    # Structure varies, adapt as needed
    games = data.get("games", data.get("apps", []))
    
    for game in games:
        app_id = game.get("appid", game.get("id", ""))
        title = game.get("name", game.get("title", "Unknown"))
        
        # Determine if free to keep or free weekend
        is_free_to_keep = game.get("is_free_to_keep", True)
        
        result["current"].append({
            "id": f"steam-{app_id}",
            "title": title,
            "store": "Steam",
            "url": f"{STEAM_STORE_URL}{app_id}",
            "original_price": game.get("original_price", 0),
            "current_price": 0,
            "image": game.get("header_image", f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"),
            "end_date": game.get("end_date")
        })
    
    return result


def _fetch_via_gamerpower(platform: str) -> Dict[str, List[Dict[str, Any]]]:
    """Fallback: fetch Steam games via GamerPower API."""
    result = {
        "current": [],
        "upcoming": []
    }
    
    try:
        response = requests.get(
            "https://www.gamerpower.com/api/giveaways",
            params={"platform": "steam", "type": "game"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        )
        response.raise_for_status()
        giveaways = response.json()
    except Exception as e:
        print(f"[Steam] GamerPower API error: {e}")
        return result
    
    for giveaway in giveaways:
        # Skip if not actually free (some are just discounts)
        if giveaway.get("type", "").lower() != "game":
            continue
            
        worth = giveaway.get("worth", "$0")
        original_price = _parse_price(worth)
        
        result["current"].append({
            "id": f"steam-{giveaway.get('id')}",
            "title": giveaway.get("title", "Unknown"),
            "store": "Steam",
            "url": giveaway.get("open_giveaway_url", giveaway.get("gamerpower_url", "")),
            "original_price": original_price,
            "current_price": 0,
            "image": giveaway.get("thumbnail", giveaway.get("image", "")),
            "end_date": giveaway.get("end_date")
        })
    
    return result


def _parse_price(price_str: str) -> float:
    """Parse price string to float."""
    if not price_str:
        return 0
    try:
        # Remove currency symbols and parse
        cleaned = price_str.replace("$", "").replace("€", "").replace("£", "").strip()
        return float(cleaned)
    except ValueError:
        return 0


if __name__ == "__main__":
    # Test fetch
    games = fetch_steam_free_games()
    print(f"Current free: {len(games['current'])}")
    for game in games["current"]:
        print(f"  - {game['title']} ({game['store']}) - ${game['original_price']}")
