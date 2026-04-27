from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ReferenceKind = Literal["video"]


class SearchProviderError(RuntimeError):
    """Raised when a search provider request fails."""


@dataclass(frozen=True)
class ReferenceResult:
    title: str
    url: str
    source: str
    kind: ReferenceKind
    snippet: str | None = None
    thumbnail_url: str | None = None
    creator: str | None = None

    @property
    def source_label(self) -> str:
        if self.creator:
            return f"{self.source} - {self.creator}"
        return self.source
