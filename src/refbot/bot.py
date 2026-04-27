import asyncio
import logging

import discord
from discord import app_commands

from refbot.config import ConfigError, Settings, load_settings
from refbot.search import (
    ReferenceResult,
    SearchProviderError,
    YouTubeSearchClient,
)


LOGGER = logging.getLogger(__name__)
VALID_KINDS = {"video"}


class ReferencePicker(discord.ui.View):
    def __init__(
        self,
        results: list[ReferenceResult],
        *,
        requester_id: int,
        timeout: float = 600,
    ) -> None:
        super().__init__(timeout=timeout)
        self.requester_id = requester_id
        self.add_item(ReferenceSelect(results))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.requester_id:
            return True

        await interaction.response.send_message(
            "Only the person who ran this search can pick a video.",
            ephemeral=True,
        )
        return False


class ReferenceSelect(discord.ui.Select):
    def __init__(self, results: list[ReferenceResult]) -> None:
        options = [
            discord.SelectOption(
                label=_truncate(result.title, 100),
                description=_truncate(result.creator or result.source, 100),
                value=str(index),
            )
            for index, result in enumerate(results)
        ]
        super().__init__(
            placeholder="Pick a video to embed in chat",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.results = results

    async def callback(self, interaction: discord.Interaction) -> None:
        result = self.results[int(self.values[0])]
        await interaction.response.send_message(
            f"Selected: {result.title}\n{result.url}",
            allowed_mentions=discord.AllowedMentions.none(),
        )


class ReferenceBot(discord.Client):
    def __init__(self, settings: Settings) -> None:
        super().__init__(intents=discord.Intents.default())
        self.settings = settings
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        if self.settings.discord_guild_id:
            guild = discord.Object(id=self.settings.discord_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            LOGGER.info("Synced slash commands to guild %s", guild.id)
        else:
            await self.tree.sync()
            LOGGER.info("Synced global slash commands")


def build_result_embeds(results: list[ReferenceResult]) -> list[discord.Embed]:
    embeds: list[discord.Embed] = []
    for result in results:
        embed = discord.Embed(
            title=_truncate(result.title, 256),
            url=result.url,
            description=_truncate(result.snippet or "No description available.", 220),
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Source", value=result.source_label, inline=True)
        embed.add_field(name="Type", value=result.kind.title(), inline=True)
        if result.thumbnail_url:
            embed.set_thumbnail(url=result.thumbnail_url)
        embeds.append(embed)
    return embeds


async def search_references(
    settings: Settings,
    *,
    query: str,
    kind: str,
    count: int,
) -> list[ReferenceResult]:
    if kind not in VALID_KINDS:
        raise ValueError(f"Unsupported kind: {kind}")

    count = max(1, min(count, 5))

    async with YouTubeSearchClient(settings.youtube_api_key) as youtube:
        results = await youtube.search(query, count=count)

    return [result for result in results if result.url][:count]


def create_bot(settings: Settings) -> ReferenceBot:
    bot = ReferenceBot(settings)

    @bot.tree.command(name="ref", description="Find YouTube video references.")
    @app_commands.describe(
        query="What to search for.",
        kind="The kind of reference to return.",
        count="Number of results to return, capped at 5.",
    )
    @app_commands.choices(
        kind=[
            app_commands.Choice(name="video", value="video"),
        ],
    )
    async def ref(
        interaction: discord.Interaction,
        query: str,
        kind: str = "video",
        count: app_commands.Range[int, 1, 5] = 3,
    ) -> None:
        await interaction.response.defer(thinking=True)

        try:
            results = await search_references(
                settings,
                query=query,
                kind=kind,
                count=count,
            )
        except (SearchProviderError, ValueError) as error:
            await interaction.followup.send(f"Search failed: {error}", ephemeral=True)
            return

        if not results:
            await interaction.followup.send(
                f"No references found for `{query}`. Try a broader search.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "Pick a video to embed it natively in chat.",
            embeds=build_result_embeds(results),
            view=ReferencePicker(results, requester_id=interaction.user.id),
        )

    return bot


def _truncate(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return f"{value[: max_length - 3]}..."


async def run_bot() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    settings = load_settings()
    bot = create_bot(settings)
    await bot.start(settings.discord_token)


def main() -> None:
    try:
        asyncio.run(run_bot())
    except ConfigError as error:
        raise SystemExit(str(error)) from error
