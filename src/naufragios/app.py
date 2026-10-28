from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agents import ResearchOrchestrator
from .store import EvidenceStore


ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "data" / "sources.json"
EVIDENCE = ROOT / "data" / "evidence.json"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="naufragios")
    p.add_argument("--health", action="store_true", help="Comprueba el nucleo local")
    sub = p.add_subparsers(dest="command")
    for name in ("buscar", "investigar-fuentes", "expediente"):
        command = sub.add_parser(name)
        command.add_argument("query")
        if name == "investigar-fuentes":
            command.add_argument("--online", action="store_true", help="Consulta las URL de la lista blanca")
    return p


def main() -> int:
    args = parser().parse_args()
    if args.health:
        print(json.dumps({"status": "ok", "agents": ["investigador_de_fuentes", "buscador_de_evidencias", "extractor_de_entidades", "resolutor_de_entidades", "contraste", "cartografia", "orquestador"]}))
        return 0
    if not args.command:
        parser().error("indica un comando o usa --health")
    store = EvidenceStore.from_files(SOURCES, EVIDENCE)
    result = ResearchOrchestrator(store).run(args.query)
    if args.command == "investigar-fuentes":
        discoveries = result["source_discoveries"]
        if args.online:
            discoveries = ResearchOrchestrator(store).sources.scan_online(args.query, list(store.sources.values()))
        result = {"query": args.query, "source_discoveries": discoveries}
    elif args.command == "buscar":
        result = {"query": args.query, "results": result["results"]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

