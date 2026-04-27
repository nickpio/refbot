from refbot.bot import ReferencePicker, build_result_embeds
from refbot.search.models import ReferenceResult


def test_build_result_embeds_formats_reference_results():
    embeds = build_result_embeds(
        [
            ReferenceResult(
                title="Explosion plume slow motion",
                url="https://youtube.com/watch?v=abc123",
                source="YouTube",
                kind="video",
                snippet="A useful explosion plume reference.",
                thumbnail_url="https://example.com/thumb.jpg",
                creator="Reference Channel",
            )
        ]
    )

    assert len(embeds) == 1
    assert embeds[0].title == "Explosion plume slow motion"
    assert embeds[0].url == "https://youtube.com/watch?v=abc123"
    assert embeds[0].description == "A useful explosion plume reference."
    assert embeds[0].fields[0].name == "Source"
    assert embeds[0].fields[0].value == "YouTube - Reference Channel"
    assert embeds[0].fields[1].name == "Type"
    assert embeds[0].fields[1].value == "Video"
    assert embeds[0].thumbnail.url == "https://example.com/thumb.jpg"


def test_build_result_embeds_truncates_long_values():
    embeds = build_result_embeds(
        [
            ReferenceResult(
                title="T" * 300,
                url="https://example.com/long",
                source="YouTube",
                kind="video",
                snippet="S" * 400,
            )
        ]
    )

    assert len(embeds[0].title) <= 256
    assert embeds[0].title.endswith("...")
    assert len(embeds[0].description) <= 220
    assert embeds[0].description.endswith("...")


def test_reference_picker_builds_select_options():
    results = [
        ReferenceResult(
            title="Explosion plume slow motion",
            url="https://youtube.com/watch?v=abc123",
            source="YouTube",
            kind="video",
            creator="Reference Channel",
        ),
        ReferenceResult(
            title="Water splash",
            url="https://youtube.com/watch?v=def456",
            source="YouTube",
            kind="video",
        ),
    ]

    picker = ReferencePicker(results, requester_id=123)
    select = picker.children[0]

    assert select.placeholder == "Pick a video to embed in chat"
    assert len(select.options) == 2
    assert select.options[0].label == "Explosion plume slow motion"
    assert select.options[0].description == "Reference Channel"
    assert select.options[0].value == "0"
    assert select.options[1].label == "Water splash"
    assert select.options[1].description == "YouTube"
    assert select.options[1].value == "1"
