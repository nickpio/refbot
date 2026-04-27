from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


@dataclass(frozen=True)
class Settings:
    discord_token: str
    youtube_api_key: str
    discord_guild_id: int | None = None


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def load_settings() -> Settings:
    load_dotenv(Path.cwd() / ".env")

    guild_id = os.getenv("DISCORD_GUILD_ID")
    return Settings(
        discord_token=_required_env("DISCORD_TOKEN"),
        youtube_api_key=_required_env("YOUTUBE_API_KEY"),
        discord_guild_id=int(guild_id) if guild_id else None,
    )
