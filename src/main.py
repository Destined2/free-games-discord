"""
Main orchestrator for free games Discord bot.
Fetches games from Epic, Steam, and GOG, then posts to Discord.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Set

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from epic_fetcher import fetch_epic_free_games
from steam_fetcher import fetch_steam_free_games
from gog_fetcher import fetch_gog_free_games
from discord_poster import post_current_free_games, post_upcoming_free_games


STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "posted-games.json")


def load_state() -> Dict[str, List[str]]:
    """Load previously posted game IDs."""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"epic": [], "steam": [], "gog": []}


def save_state(state: Dict[str, List[str]]) -> None:
    """Save posted game IDs to state file."""
    state["last_updated"] = datetime.utcnow().isoformat() + "Z"
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def filter_new_games(
    games: List[Dict[str, Any]],
    posted_ids: List[str]
) -> List[Dict[str, Any]]:
    """Filter out already-posted games."""
    posted_set = set(posted_ids)
    return [g for g in games if g.get("id") not in posted_set]


def main():
    """Main entry point."""
    print("=" * 50)
    print(f"Free Games Bot - {datetime.utcnow().isoformat()}")
    print("=" * 50)
    
    # Load state
    state = load_state()
    print(f"[State] Loaded: {len(state.get('epic', []))} Epic, {len(state.get('steam', []))} Steam, {len(state.get('gog', []))} GOG posted")
    
    # Get webhook URLs from environment
    webhook_current = os.environ.get("DISCORD_WEBHOOK_URL_CURRENT")
    webhook_upcoming = os.environ.get("DISCORD_WEBHOOK_URL_UPCOMING")
    
    if not webhook_current:
        print("[Error] DISCORD_WEBHOOK_URL_CURRENT not set")
        sys.exit(1)
    
    # Fetch from all stores
    print("\n[Fetch] Epic Games Store...")
    epic_games = fetch_epic_free_games("US")
    print(f"  Current: {len(epic_games['current'])}, Upcoming: {len(epic_games['upcoming'])}")
    
    print("\n[Fetch] Steam...")
    steam_games = fetch_steam_free_games()
    print(f"  Current: {len(steam_games['current'])}, Upcoming: {len(steam_games['upcoming'])}")
    
    print("\n[Fetch] GOG...")
    gog_games = fetch_gog_free_games()
    print(f"  Current: {len(gog_games['current'])}, Upcoming: {len(gog_games['upcoming'])}")
    
    # Combine all games
    all_current = (
        epic_games.get("current", []) +
        steam_games.get("current", []) +
        gog_games.get("current", [])
    )
    
    all_upcoming = (
        epic_games.get("upcoming", []) +
        steam_games.get("upcoming", []) +
        gog_games.get("upcoming", [])
    )
    
    # Filter out already posted
    all_posted_ids = (
        state.get("epic", []) +
        state.get("steam", []) +
        state.get("gog", [])
    )
    
    new_current = filter_new_games(all_current, all_posted_ids)
    new_upcoming = filter_new_games(all_upcoming, all_posted_ids)
    
    print(f"\n[Filter] New current: {len(new_current)}, New upcoming: {len(new_upcoming)}")
    
    # Post to Discord
    posted_ids = []
    
    if new_current:
        print(f"\n[Post] Posting {len(new_current)} current free games...")
        success = post_current_free_games(
            new_current,
            webhook_current,
            ping_everyone=True
        )
        if success:
            posted_ids.extend([g["id"] for g in new_current])
    
    if new_upcoming and webhook_upcoming:
        print(f"\n[Post] Posting {len(new_upcoming)} upcoming free games...")
        success = post_upcoming_free_games(
            new_upcoming,
            webhook_upcoming,
            ping_everyone=True
        )
        if success:
            posted_ids.extend([g["id"] for g in new_upcoming])
    
    # Update state
    if posted_ids:
        # Add to appropriate store lists
        for game_id in posted_ids:
            if game_id.startswith("steam"):
                state["steam"].append(game_id)
            elif game_id.startswith("gog"):
                state["gog"].append(game_id)
            else:
                state["epic"].append(game_id)
        
        # Keep only last 100 IDs per store
        for store in ["epic", "steam", "gog"]:
            state[store] = list(set(state[store]))[-100:]
        
        save_state(state)
        print(f"\n[State] Saved {len(posted_ids)} new game IDs")
    
    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
