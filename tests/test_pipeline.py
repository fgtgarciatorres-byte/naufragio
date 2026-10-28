import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.naufragios.agents import ResearchOrchestrator, SourceResearcher
from src.naufragios.store import EvidenceStore


ROOT = Path(__file__).parents[1]


def store():
    return EvidenceStore.from_files(ROOT / "data/sources.json", ROOT / "data/evidence.json")


class PipelineTests(unittest.TestCase):
    def test_autonomous_search_keeps_citations(self):
        result = ResearchOrchestrator(store()).run("Santa Ana Canarias")
        self.assertTrue(result["results"])
        first = result["results"][0]
        self.assertTrue(first["source"]["url"].startswith("https://"))
        self.assertTrue(first["evidence"]["quote"])
        self.assertEqual(first["evidence"]["verification"], "synthetic_fixture")


    def test_source_researcher_informs_orchestrator(self):
        result = ResearchOrchestrator(store()).run("Armadas Canarias")
        ids = {item["source"]["id"] for item in result["source_discoveries"]}
        self.assertIn("pares-agi", ids)
        self.assertTrue(result["results"])


    def test_agents_interoperate_and_export_map(self):
        result = ResearchOrchestrator(store()).run("Santa Ana")
        self.assertEqual(result["entities"][0]["entities"]["ship"], ["Santa Ana"])
        self.assertEqual(result["map"]["type"], "FeatureCollection")
        self.assertEqual(result["map"]["features"][0]["properties"]["uncertainty_m"], 25000)


    def test_json_contract_is_serializable(self):
        result = ResearchOrchestrator(store()).run("Canarias")
        json.dumps(result, ensure_ascii=False)

    def test_catalogue_date_ranges_are_not_event_conflicts(self):
        result = ResearchOrchestrator(store()).run("Armadas Canarias")
        self.assertEqual(result["contradictions"], [])

    def test_online_source_scanner_records_origin_and_status(self):
        source = next(iter(store().sources.values()))
        scanner = SourceResearcher(fetcher=lambda url: "Armadas y flotas Canarias")
        result = scanner.scan_online("Armadas Canarias", [source])
        self.assertEqual(result[0]["fetch_status"], "ok")
        self.assertEqual(result[0]["source"]["id"], "pares-agi")
        self.assertEqual(result[0]["matched_terms"], ["armadas", "canarias"])

