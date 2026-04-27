from __future__ import annotations

from typing import Any

import httpx

from refbot.search.models import ReferenceResult, SearchProviderError


YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


class YouTubeSearchClient:
    def __init__(
        self,
        api_key: str,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> YouTubeSearchClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10)
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    async def search(self, query: str, *, count: int = 3) -> list[ReferenceResult]:
        client = self._require_client()
        response = await client.get(
            YOUTUBE_SEARCH_URL,
            params={
                "part": "snippet",
                "type": "video",
                "maxResults": count,
                "q": query,
                "key": self._api_key,
                "safeSearch": "moderate",
            },
        )

        if response.status_code >= 400:
            raise SearchProviderError(
                f"YouTube search failed with status {response.status_code}"
            )

        return [_item_to_result(item) for item in response.json().get("items", [])]

    def _require_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Use YouTubeSearchClient as an async context manager.")
        return self._client


def _item_to_result(item: dict[str, Any]) -> ReferenceResult:
    video_id = item.get("id", {}).get("videoId", "")
    snippet = item.get("snippet", {})
    thumbnails = snippet.get("thumbnails", {})
    thumbnail = (
        thumbnails.get("high")
        or thumbnails.get("medium")
        or thumbnails.get("default")
        or {}
    )

    return ReferenceResult(
        title=snippet.get("title", "Untitled YouTube result"),
        url=f"https://www.youtube.com/watch?v={video_id}",
        source="YouTube",
        kind="video",
        snippet=snippet.get("description") or None,
        thumbnail_url=thumbnail.get("url"),
        creator=snippet.get("channelTitle") or None,
    )
