"""Punto de entrada inicial para la herramienta naufragios.

Este archivo define una interfaz mínima para conectar agentes, fuentes y
busquedas. Las fuentes externas se incorporaran mediante adaptadores separados.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceRecord:
    """Referencia documental trazable."""

    title: str
    source_type: str
    url: str
    language: str
    date: str | None = None
    notes: str | None = None


class SourceResearcher:
    """Agente inicial que registra fuentes nuevas para el resto del sistema."""

    name = "investigador_de_fuentes"

    def discover(self, query: str, sources: list[SourceRecord]) -> list[dict[str, Any]]:
        query_terms = {term.casefold() for term in query.split() if term.strip()}
        results: list[dict[str, Any]] = []

        for source in sources:
            searchable = " ".join(
                [source.title, source.source_type, source.language, source.notes or ""]
            ).casefold()
            matched_terms = sorted(term for term in query_terms if term in searchable)
            if matched_terms:
                results.append(
                    {
                        "agent": self.name,
                        "source": asdict(source),
                        "matched_terms": matched_terms,
                        "verification": "requires_human_review",
                    }
                )

        return results


def load_sources(path: Path) -> list[SourceRecord]:
    if not path.exists():
        return []

    raw_records = json.loads(path.read_text(encoding="utf-8"))
    return [SourceRecord(**record) for record in raw_records]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Investigacion historica de naufragios")
    parser.add_argument("query", nargs="?", help="Terminos que se quieren buscar")
    parser.add_argument(
        "--sources",
        type=Path,
        default=Path("data/sources.json"),
        help="Archivo JSON con fuentes documentales",
    )
    parser.add_argument("--health", action="store_true", help="Comprueba el nucleo local")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.health:
        print(json.dumps({"status": "ok", "agents": [SourceResearcher.name]}))
        return 0

    if not args.query:
        print("Indica una consulta o usa --health.")
        return 2

    results = SourceResearcher().discover(args.query, load_sources(args.sources))
    print(json.dumps({"query": args.query, "results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
