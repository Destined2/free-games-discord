"""
Epic Games Store free games fetcher.
Uses the unofficial epicstore_api approach (direct API calls).
"""

import requests
from datetime import datetime
from typing import List, Dict, Any, Optional


EPIC_CATALOG_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
EPIC_STORE_URL = "https://store.epicgames.com/en-US/p/"


def fetch_epic_free_games(country: str = "US") -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch current and upcoming free games from Epic Games Store.
    
    Returns:
        Dict with 'current' and 'upcoming' lists of game dicts
    """
    result = {
        "current": [],
        "upcoming": []
    }
    
    try:
        response = requests.get(
            EPIC_CATALOG_URL,
            params={"country": country},
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[Epic] Error fetching games: {e}")
        return result
    
    elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
    
    for game in elements:
        promotions = game.get("promotions")
        if not promotions:
            continue
        
        title = game.get("title", "Unknown")
        game_id = game.get("id", "")
        product_slug = game.get("productSlug", game.get("urlSlug", ""))
        page_slug = product_slug.split("/")[0] if product_slug else game_id
        
        # Get price info
        price = game.get("price", {})
        original_price = price.get("totalPrice", {}).get("originalPrice", 0)
        current_price = price.get("totalPrice", {}).get("discountPrice", 0)
        
        # Get images
        images = game.get("keyImages", [])
        thumbnail = next((img["url"] for img in images if img.get("type") == "Thumbnail"), "")
        offer_image = next((img["url"] for img in images if img.get("type") == "OfferImageWide"), thumbnail)
        
        # Check current promotions (active now)
        current_promos = promotions.get("promotionalOffers", [])
        for promo_group in current_promos:
            for promo in promo_group.get("promotionalOffers", []):
                if _is_promo_active(promo):
                    result["current"].append({
                        "id": game_id,
                        "title": title,
                        "store": "Epic Games",
                        "url": f"{EPIC_STORE_URL}{page_slug}",
                        "original_price": original_price / 100 if original_price else 0,
                        "current_price": current_price / 100 if current_price else 0,
                        "image": offer_image,
                        "end_date": promo.get("endDate")
                    })
                    break
        
        # Check upcoming promotions
        upcoming_promos = promotions.get("upcomingPromotionalOffers", [])
        for promo_group in upcoming_promos:
            for promo in promo_group.get("promotionalOffers", []):
                if _is_promo_upcoming(promo):
                    result["upcoming"].append({
                        "id": f"{game_id}-upcoming",
                        "title": title,
                        "store": "Epic Games",
                        "url": f"{EPIC_STORE_URL}{page_slug}",
                        "original_price": original_price / 100 if original_price else 0,
                        "image": offer_image,
                        "start_date": promo.get("startDate")
                    })
                    break
    
    return result


def _is_promo_active(promo: Dict) -> bool:
    """Check if promotion is currently active and free."""
    now = datetime.utcnow()
    start = promo.get("startDate")
    end = promo.get("endDate")
    
    if not start or not end:
        return False
    
    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00")).replace(tzinfo=None)
    end_dt = datetime.fromisoformat(end.replace("Z", "+00:00")).replace(tzinfo=None)
    
    # Must be within promotion window and be 100% off
    discount = promo.get("discountSetting", {}).get("discountPercentage", 0)
    return start_dt <= now <= end_dt and discount == 0


def _is_promo_upcoming(promo: Dict) -> bool:
    """Check if promotion is upcoming and free."""
    now = datetime.utcnow()
    start = promo.get("startDate")
    
    if not start:
        return False
    
    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00")).replace(tzinfo=None)
    
    # Must be in the future and be 100% off
    discount = promo.get("discountSetting", {}).get("discountPercentage", 0)
    return start_dt > now and discount == 0


if __name__ == "__main__":
    # Test fetch
    games = fetch_epic_free_games()
    print(f"Current free: {len(games['current'])}")
    print(f"Upcoming free: {len(games['upcoming'])}")
    for game in games["current"]:
        print(f"  - {game['title']} ({game['store']})")
