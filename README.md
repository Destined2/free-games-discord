# Free Games Discord Announcements

Daily GitHub Actions workflow that checks for paid games that are currently free, plus upcoming free games, and posts Discord announcements with rich previews.

## Stores

- Epic Games Store: current and upcoming free games from Epic's public promotions endpoint.
- Steam: current free game giveaways via SteamDB-style endpoint with GamerPower fallback.
- GOG: current free game giveaways via GamerPower.

> Note: Store promotion APIs are mostly unofficial or community-backed, so occasional source changes can require maintenance.

## Discord Setup

1. In Discord, open your announcements channel.
2. Go to **Edit Channel → Integrations → Webhooks**.
3. Create a webhook and copy its URL.
4. In GitHub, add repository secrets:
   - `DISCORD_WEBHOOK_URL_CURRENT`
   - `DISCORD_WEBHOOK_URL_UPCOMING`

You can use the same webhook URL for both secrets if both message types should go to the same channel.

## GitHub Actions Setup

The workflow is in:

```text
.github/workflows/free-games.yml
```

It runs daily at **10:00 UTC** and can also be started manually from the **Actions** tab using `workflow_dispatch`.

## Local Test

```bash
cd free-games-discord
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export DISCORD_WEBHOOK_URL_CURRENT="https://discord.com/api/webhooks/..."
export DISCORD_WEBHOOK_URL_UPCOMING="https://discord.com/api/webhooks/..."
python src/main.py
```

## Duplicate Prevention

`posted-games.json` stores posted game IDs so the bot does not spam duplicates. The GitHub Action commits changes to this file after successful posts.

## Behavior

- Posts **@everyone** for new currently-free games.
- Posts **@everyone** for new upcoming-free games.
- Separates current and upcoming games into different Discord messages.
- Limits each Discord message to 10 embeds, matching Discord's webhook limit.
