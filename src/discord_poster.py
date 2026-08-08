"""
Discord webhook poster for free game announcements.
"""

import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional


def post_current_free_games(
    games: List[Dict[str, Any]],
    webhook_url: str,
    ping_everyone: bool = True
) -> bool:
    """
    Post current free games to Discord via webhook.
    
    Args:
        games: List of game dicts with title, url, store, etc.
        webhook_url: Discord webhook URL
        ping_everyone: Whether to @everyone
    
    Returns:
        True if successful
    """
    if not games:
        print("[Discord] No current games to post")
        return True
    
    # Build embeds (max 10 per message)
    embeds = []
    for game in games[:10]:
        embed = {
            "title": game.get("title", "Unknown Game"),
            "url": game.get("url", ""),
            "description": f"**Store:** {game.get('store', 'Unknown')}\n**Original Price:** ${game.get('original_price', 0):.2f}",
            "color": 3066993,  # Green
            "thumbnail": {"url": game.get("image", "")} if game.get("image") else None,
            "footer": {"text": "Free Game Alert"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if game.get("end_date"):
            embed["description"] += f"\n**Ends:** {game['end_date']}"
        
        # Remove None values
        embed = {k: v for k, v in embed.items() if v is not None}
        embeds.append(embed)
    
    payload = {
        "content": "🎮 **NOW FREE - GRAB THEM NOW!**" + ("\n\n@everyone" if ping_everyone else ""),
        "embeds": embeds,
        "username": "Free Games Bot",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3612/3612569.png"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        print(f"[Discord] Posted {len(embeds)} current free games")
        return True
    except Exception as e:
        print(f"[Discord] Error posting current games: {e}")
        return False


def post_upcoming_free_games(
    games: List[Dict[str, Any]],
    webhook_url: str,
    ping_everyone: bool = True
) -> bool:
    """
    Post upcoming free games to Discord via webhook.
    
    Args:
        games: List of game dicts with title, url, store, etc.
        webhook_url: Discord webhook URL
        ping_everyone: Whether to @everyone
    
    Returns:
        True if successful
    """
    if not games:
        print("[Discord] No upcoming games to post")
        return True
    
    # Build embeds
    embeds = []
    for game in games[:10]:
        embed = {
            "title": game.get("title", "Unknown Game"),
            "url": game.get("url", ""),
            "description": f"**Store:** {game.get('store', 'Unknown')}\n**Original Price:** ${game.get('original_price', 0):.2f}",
            "color": 15844367,  # Gold/Yellow
            "thumbnail": {"url": game.get("image", "")} if game.get("image") else None,
            "footer": {"text": "Upcoming Free Game"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if game.get("start_date"):
            embed["description"] += f"\n**Free Starting:** {game['start_date']}"
        
        embed = {k: v for k, v in embed.items() if v is not None}
        embeds.append(embed)
    
    payload = {
        "content": "📅 **UPCOMING FREE GAMES**" + ("\n\n@everyone" if ping_everyone else ""),
        "embeds": embeds,
        "username": "Free Games Bot",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3612/3612569.png"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        print(f"[Discord] Posted {len(embeds)} upcoming free games")
        return True
    except Exception as e:
        print(f"[Discord] Error posting upcoming games: {e}")
        return False


def post_summary(
    current_count: int,
    upcoming_count: int,
    webhook_url: str
) -> bool:
    """
    Post a summary when no new games found.
    """
    if current_count == 0 and upcoming_count == 0:
        print("[Discord] No games to report")
        return True
    
    payload = {
        "content": f"📊 **Daily Check Complete**\n{current_count} current free games | {upcoming_count} upcoming",
        "username": "Free Games Bot",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3612/3612569.png"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[Discord] Error posting summary: {e}")
        return False


if __name__ == "__main__":
    # Test posting (replace with actual webhook URL)
    test_games = [{
        "id": "test-1",
        "title": "Test Game",
        "store": "Test Store",
        "url": "https://example.com",
        "original_price": 19.99,
        "current_price": 0,
        "image": "https://via.placeholder.com/150"
    }]
    print("Discord poster module loaded")
