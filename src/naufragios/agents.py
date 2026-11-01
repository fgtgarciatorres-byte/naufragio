from __future__ import annotations

import re
from html import unescape
from urllib.request import Request, urlopen
from collections import Counter
from dataclasses import asdict
from typing import Any

from .models import Evidence, SearchHit, Source
from .store import EvidenceStore


def _terms(query: str) -> list[str]:
    return [term.casefold() for term in re.findall(r"[\w����隥�������-]+", query) if len(term) > 2]


class SourceResearcher:
    name = "investigador_de_fuentes"

    def __init__(self, fetcher=None):
        self.fetcher = fetcher or self._fetch

    @staticmethod
    def _fetch(url: str) -> str:
        request = Request(url, headers={"User-Agent": "naufragios/0.1 source-researcher"})
        with urlopen(request, timeout=15) as response:
            return response.read().decode("utf-8", errors="replace")

    def scan(self, query: str, sources: list[Source]) -> list[dict[str, Any]]:
        terms = _terms(query)
        discovered = []
        for source in sources:
            haystack = " ".join((source.title, source.publisher, source.source_type, *source.languages, *source.keywords)).casefold()
            matches = [term for term in terms if term in haystack]
            if matches:
                discovered.append({"source": asdict(source), "matched_terms": sorted(set(matches)), "agent": self.name})
        return discovered

    def scan_online(self, query: str, sources: list[Source]) -> list[dict[str, Any]]:
        terms = _terms(query)
        findings = []
        for source in sources:
            try:
                raw = self.fetcher(source.url)
                text = unescape(re.sub(r"<[^>]+>", " ", raw)).casefold()
                matches = [term for term in terms if term in text]
                findings.append({"source": asdict(source), "matched_terms": sorted(set(matches)), "agent": self.name, "fetch_status": "ok"})
            except Exception as exc:  # network and access failures are evidence about the connector, not source content
                findings.append({"source": asdict(source), "matched_terms": [], "agent": self.name, "fetch_status": "error", "error_type": type(exc).__name__})
        return findings


class EvidenceSearcher:
    name = "buscador_de_evidencias"

    def search(self, query: str, store: EvidenceStore) -> list[SearchHit]:
        terms = _terms(query)
        hits = []
        for evidence in store.evidence:
            haystack = " ".join((evidence.title, evidence.text, evidence.quote, *(v for values in evidence.entities.values() for v in values))).casefold()
            matches = tuple(sorted({term for term in terms if term in haystack}))
            if matches:
                score = len(matches) / max(len(terms), 1)
                hits.append(SearchHit(evidence, store.source_for(evidence), score, matches))
        return sorted(hits, key=lambda hit: (-hit.score, hit.evidence.id))


class LegalRecordsAgent:
    """Detecta se�ales de pleito, p�rdida econ�mica o reclamaci�n.

    La etiqueta es una pista de investigaci�n. No convierte el expediente en
    prueba de naufragio: esa decisi�n exige leer el documento y contrastarlo.
    """

    name = "investigador_de_pleitos"
    TERMS = ("pleito", "litigio", "demanda", "autos", "acreedores", "dejaci�n", "p�rdida", "reclamaci�n", "arribada", "mercanc�as", "frutos", "rescate", "prorrateo", "consignatarios")

    def classify(self, hits: list[SearchHit]) -> list[dict[str, Any]]:
        records = []
        for hit in hits:
            text = " ".join((hit.evidence.title, hit.evidence.text, hit.evidence.quote)).casefold()
            signals = sorted({term for term in self.TERMS if term in text})
            if signals or hit.source.source_type == "pleitos de justicia":
                records.append({"evidence_id": hit.evidence.id, "source_id": hit.source.id, "signals": signals, "agent": self.name, "interpretation": "pista jur�dica; requiere lectura del expediente"})
        return records


class HistoricalPersonAgent:
    """Investigador independiente para una persona y su red documental.

    Separa las variantes nominales, los idiomas y las geograf�as de b�squeda.
    Las coincidencias son pistas documentales, no una biograf�a validada.
    """

    name = "investigador_persona_amaro_pargo"
    person = "Amaro Pargo"
    aliases = ("Amaro Pargo", "Amaro Rodr�guez Felipe", "Amaro Rodriguez Felipe", "Amaro Rodr�guez Phelipe", "Amaro Pargo de Barrios")
    lanes = {
        "es": ("Canarias", "La Laguna", "Tenerife", "Santo Domingo", "La Habana", "Caracas", "Cuba"),
        "fr": ("Antilles", "Martinique", "Guadeloupe", "corsaire", "prise", "navire"),
        "en": ("Caribbean", "Jamaica", "privateer", "prize", "ship", "admiralty"),
    }
    laguna_leads = [
        {"id": "amaro-siervita-protocolos-1738", "type": "primary_reference", "reference": "AHPSCT, Protocolos notariales, legajo 951, ff. 186r-191v, La Laguna, 8/07/1738", "subject": "memorias y aniversarios en Santa Catalina y Santo Domingo por sor Mar�a de Jes�s"},
        {"id": "amaro-siervita-exhumacion-1734", "type": "primary_reference", "reference": "AHPSCT, protocolos notariales sobre exhumaci�n de 1734; edici�n documental de Amaro Pargo. Documentos de una vida", "subject": "exhumaci�n, gastos funerarios y sarc�fago de sor Mar�a de Jes�s"},
        {"id": "laguna-amaro-ossuna", "type": "archive_route", "reference": "Fondo Ossuna, Archivo Municipal de La Laguna", "subject": "registro de bienes de Amaro Pargo"},
    ]

    def run(self, store: EvidenceStore) -> dict[str, Any]:
        selected = []
        aliases = {alias.casefold() for alias in self.aliases}
        for evidence in store.evidence:
            haystack = " ".join((evidence.title, evidence.text, evidence.quote, *(v for values in evidence.entities.values() for v in values))).casefold()
            matched = sorted(alias for alias in aliases if alias in haystack)
            if matched:
                selected.append({"evidence": asdict(evidence), "source": asdict(store.source_for(evidence)), "matched_aliases": matched, "agent": self.name})
        language_sources = {
            language: [asdict(source) for source in store.sources.values() if language in source.languages]
            for language in self.lanes
        }
        return {
            "agent": self.name,
            "person": self.person,
            "aliases": list(self.aliases),
            "geographies": ["Canarias", "Caribe", "Antillas francesas", "rutas brit�nicas del Caribe"],
            "source_lanes": self.lanes,
            "laguna_leads": self.laguna_leads,
            "language_sources": language_sources,
            "results": selected,
            "gaps": ["documentos franceses con coincidencia nominal directa", "registros ingleses de presas o tribunales del Almirantazgo", "nombres y fechas de todos los viajes caribe�os"],
            "verification_rule": "Una coincidencia nominal se conserva como pista; la biograf�a exige documento, signatura, contexto y contraste independiente.",
        }


class EntityExtractor:
    name = "extractor_de_entidades"

    PATTERNS = {
        "date": r"\b(?:14|15|16|17)\d{2}\b",
        "ship": r"(?:nav[i�]o|fragata|gale[o�]n|bergant[i�]n)\s+([A-Z�����][\w����隥�������-]*(?:\s+[A-Z�����][\w����隥�������-]*){0,3})",
        "place": r"\b(Canarias|Tenerife|Gran Canaria|La Gomera|Lanzarote|Fuerteventura|El Hierro|La Palma)\b",
    }

    def extract(self, hit: SearchHit) -> dict[str, Any]:
        text = f"{hit.evidence.title}. {hit.evidence.text}. {hit.evidence.quote}"
        result: dict[str, Any] = {"evidence_id": hit.evidence.id, "agent": self.name, "entities": {}}
        for kind, pattern in self.PATTERNS.items():
            flags = 0 if kind == "ship" else re.IGNORECASE
            found = re.findall(pattern, text, flags=flags)
            result["entities"][kind] = sorted(set(item if isinstance(item, str) else item[0] for item in found))
        return result


class EntityResolver:
    name = "resolutor_de_entidades"

    def resolve(self, extracted: list[dict[str, Any]]) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = {}
        for item in extracted:
            for kind, values in item["entities"].items():
                for value in values:
                    key = re.sub(r"[^a-z0-9]", "", value.casefold())
                    groups.setdefault(f"{kind}:{key}", []).append(value)
        return {key: sorted(set(values)) for key, values in groups.items()}


class ContradictionDetector:
    name = "contraste"

    def compare(self, hits: list[SearchHit]) -> list[dict[str, Any]]:
        # Los rangos del cat�logo describen fondos, no fechas de naufragios.
        # Solo se contrastan a�os exactos ligados a una entidad barco.
        event_hits = [
            hit for hit in hits
            if hit.evidence.date
            and re.fullmatch(r"\d{4}", hit.evidence.date)
            and hit.evidence.entities.get("ship")
        ]
        dates = Counter(hit.evidence.date for hit in event_hits)
        if len(dates) < 2:
            return []
        return [{"agent": self.name, "type": "date_conflict", "values": dict(dates), "evidence_ids": [hit.evidence.id for hit in event_hits]}]


class CartographyAgent:
    name = "cartografia"

    def geojson(self, hits: list[SearchHit]) -> dict[str, Any]:
        features = []
        for hit in hits:
            if not hit.evidence.location:
                continue
            location = hit.evidence.location
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [location["lon"], location["lat"]]},
                "properties": {"evidence_id": hit.evidence.id, "title": hit.evidence.title, "uncertainty_m": location.get("uncertainty_m"), "verification": hit.evidence.verification},
            })
        return {"type": "FeatureCollection", "features": features}


class ResearchOrchestrator:
    name = "orquestador"

    def __init__(self, store: EvidenceStore):
        self.store = store
        self.sources = SourceResearcher()
        self.searcher = EvidenceSearcher()
        self.legal = LegalRecordsAgent()
        self.person = HistoricalPersonAgent()
        self.extractor = EntityExtractor()
        self.resolver = EntityResolver()
        self.contraster = ContradictionDetector()
        self.map = CartographyAgent()

    def run(self, query: str) -> dict[str, Any]:
        hits = self.searcher.search(query, self.store)
        extracted = [self.extractor.extract(hit) for hit in hits]
        return {
            "query": query,
            "source_discoveries": self.sources.scan(query, list(self.store.sources.values())),
            "results": [
                {"evidence": asdict(hit.evidence), "source": asdict(hit.source), "score": hit.score, "matched_terms": hit.matched_terms}
                for hit in hits
            ],
            "legal_records": self.legal.classify(hits),
            "person_research": self.person.run(self.store) if any(term in query.casefold() for term in ("amaro", "pargo", "rodr�guez felipe", "rodriguez felipe")) else None,
            "entities": extracted,
            "resolved_entities": self.resolver.resolve(extracted),
            "contradictions": self.contraster.compare(hits),
            "map": self.map.geojson(hits),
            "verification_rule": "Cada resultado conserva fuente, URL, cita y estado de verificaci�n.",
        }

