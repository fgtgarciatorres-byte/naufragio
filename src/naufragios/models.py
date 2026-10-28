from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    publisher: str
    source_type: str
    url: str
    languages: tuple[str, ...]
    keywords: tuple[str, ...]
    access_date: str
    status: str = "catalogued"


@dataclass(frozen=True)
class Evidence:
    id: str
    source_id: str
    title: str
    text: str
    quote: str
    date: str | None = None
    entities: dict[str, list[str]] = field(default_factory=dict)
    location: dict[str, Any] | None = None
    verification: str = "unreviewed"


@dataclass(frozen=True)
class SearchHit:
    evidence: Evidence
    source: Source
    score: float
    matched_terms: tuple[str, ...]


def source_from_dict(row: dict[str, Any]) -> Source:
    return Source(
        id=row["id"], title=row["title"], publisher=row["publisher"],
        source_type=row["source_type"], url=row["url"],
        languages=tuple(row.get("languages", [])), access_date=row["access_date"],
        keywords=tuple(row.get("keywords", [])),
        status=row.get("status", "catalogued"),
    )


def evidence_from_dict(row: dict[str, Any]) -> Evidence:
    return Evidence(
        id=row["id"], source_id=row["source_id"], title=row["title"],
        text=row["text"], quote=row["quote"], date=row.get("date"),
        entities=row.get("entities", {}), location=row.get("location"),
        verification=row.get("verification", "unreviewed"),
    )

