# Refbot

Refbot is a Discord bot for finding video references for animation, visual effects, art, and related creative work.

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install the project:

   ```bash
   pip install -e ".[dev]"
   ```

3. Copy the environment template and fill in secrets:

   ```bash
   cp .env.example .env
   ```

   Required variables:

   - `DISCORD_TOKEN`: Bot token from the Discord Developer Portal.
   - `YOUTUBE_API_KEY`: YouTube Data API key.

   Optional variables:

   - `DISCORD_GUILD_ID`: Development server ID. When set, slash commands sync to that guild immediately.

4. Invite the bot to a Discord server with the `bot` and `applications.commands` scopes.

5. Run the bot:

   ```bash
   refbot
   ```

## Commands

Use `/ref` to search for references:

```text
/ref query:"explosion smoke slow motion" kind:video count:3
```

Options:

- `query`: Search terms.
- `kind`: `video`.
- `count`: Number of results to return, capped at 5.

The bot returns a short list with a picker. Choose a result from the picker to post the YouTube URL into chat so Discord can render its native playable embed.

## Development

Run tests with:

```bash
pytest
```
