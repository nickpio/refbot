import httpx
import pytest

from refbot.search.models import SearchProviderError
from refbot.search.youtube import YouTubeSearchClient


@pytest.mark.asyncio
async def test_youtube_search_normalizes_results(httpx_mock):
    httpx_mock.add_response(
        json={
            "items": [
                {
                    "id": {"videoId": "abc123"},
                    "snippet": {
                        "title": "Water splash reference",
                        "description": "Slow motion water splash.",
                        "channelTitle": "Reference Channel",
                        "thumbnails": {
                            "high": {"url": "https://img.example/high.jpg"}
                        },
                    },
                }
            ]
        }
    )

    async with httpx.AsyncClient() as http_client:
        client = YouTubeSearchClient("yt-key", client=http_client)
        results = await client.search("water splash", count=2)

    assert len(results) == 1
    assert results[0].title == "Water splash reference"
    assert results[0].url == "https://www.youtube.com/watch?v=abc123"
    assert results[0].source == "YouTube"
    assert results[0].kind == "video"
    assert results[0].thumbnail_url == "https://img.example/high.jpg"
    assert results[0].creator == "Reference Channel"

    request = httpx_mock.get_requests()[0]
    assert request.url.params["q"] == "water splash"
    assert request.url.params["maxResults"] == "2"
    assert request.url.params["key"] == "yt-key"


@pytest.mark.asyncio
async def test_youtube_search_raises_provider_error(httpx_mock):
    httpx_mock.add_response(status_code=403, json={"error": "forbidden"})

    async with httpx.AsyncClient() as http_client:
        client = YouTubeSearchClient("yt-key", client=http_client)
        with pytest.raises(SearchProviderError, match="YouTube search failed"):
            await client.search("explosion", count=1)
