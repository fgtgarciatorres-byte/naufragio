from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Evidence, Source, evidence_from_dict, source_from_dict


class EvidenceStore:
    def __init__(self, sources: list[Source], evidence: list[Evidence]):
        self.sources = {item.id: item for item in sources}
        self.evidence = evidence

    @classmethod
    def from_files(cls, sources_path: Path, evidence_path: Path) -> "EvidenceStore":
        sources = [source_from_dict(row) for row in json.loads(sources_path.read_text(encoding="utf-8"))]
        evidence = [evidence_from_dict(row) for row in json.loads(evidence_path.read_text(encoding="utf-8"))]
        return cls(sources, evidence)

    def source_for(self, evidence: Evidence) -> Source:
        return self.sources[evidence.source_id]

    def export(self) -> dict[str, Any]:
        return {"sources": list(self.sources.values()), "evidence_count": len(self.evidence)}

