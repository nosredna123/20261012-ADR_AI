"""Offline RAG checks with altered rankings confined to synthetic test fixtures."""

import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_rag_protocol.py"
SPEC = importlib.util.spec_from_file_location("rag_protocol", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load RAG script: {SCRIPT}")
rag = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rag)


class RagProtocolTests(unittest.TestCase):
    def test_frozen_protocol_and_determinism(self):
        audit = rag.audit_protocol()
        self.assertEqual(audit["validated_frozen_ranking_rows"], 12)
        self.assertEqual(audit["criterion_count"], 35)
        self.assertEqual(audit["pattern_count"], 70)
        self.assertTrue(audit["same_catalog_field_values"])
        self.assertEqual(len(audit["queries"]), 12)
        self.assertEqual(rag.render_outputs(audit),
                         rag.render_outputs(rag.audit_protocol()))

    def test_query_format_preserves_ids_and_text(self):
        runner = rag.load_module(rag.RAG / "src/run_baseline.py", "test_rag_runner")
        query = runner.build_query([{
            "system_purpose": "Synthetic purpose", "user_story_id": "SYNTHETIC-US01",
            "user_story": "Synthetic story",
            "acceptance_criterion_id": "SYNTHETIC-US01-AC01",
            "acceptance_criterion": "Synthetic criterion",
        }])
        self.assertEqual(query, "System Purpose:\nSynthetic purpose\n\n"
                         "User Story:\n[SYNTHETIC-US01] Synthetic story\n\n"
                         "Acceptance Criteria:\n[SYNTHETIC-US01-AC01] Synthetic criterion")

    def test_invalid_rankings_fail(self):
        runner = rag.load_module(rag.RAG / "src/run_baseline.py", "test_rag_runner")
        cases = runner.load_cases(rag.QUERY_SOURCE)
        patterns = rag.read_catalog()
        with rag.BASELINE.open(encoding="utf-8-sig", newline="") as source:
            rows = list(csv.DictReader(source))
        for mutation in ("missing_story", "duplicate_story", "wrong_system",
                         "short_top15", "duplicate_top5", "unknown_id",
                         "wrong_name", "top5_outside_top15"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                altered = [dict(row) for row in rows]
                if mutation == "missing_story":
                    altered.pop()
                elif mutation == "duplicate_story":
                    altered.append(dict(altered[0]))
                elif mutation == "wrong_system":
                    altered[0]["system"] = "Synthetic-invalid-system"
                elif mutation == "short_top15":
                    altered[0]["top15_ids"] = ";".join(altered[0]["top15_ids"].split(";")[:-1])
                elif mutation == "duplicate_top5":
                    altered[0]["top5_ids"] = ";".join(["002"] * 5)
                elif mutation == "unknown_id":
                    altered[0]["top5_ids"] = "999;" + ";".join(
                        altered[0]["top5_ids"].split(";")[1:])
                elif mutation == "wrong_name":
                    altered[0]["top5_names"] = "Synthetic-invalid-name"
                else:
                    ids = altered[0]["top5_ids"].split(";")
                    ids[0] = next(pid for pid in patterns
                                  if pid not in altered[0]["top15_ids"].split(";"))
                    altered[0]["top5_ids"] = ";".join(ids)
                    altered[0]["top5_names"] = ";".join(patterns[pid]["name"] for pid in ids)
                fixture = Path(directory) / "synthetic-invalid-rankings.csv"
                with fixture.open("w", encoding="utf-8", newline="") as target:
                    writer = csv.DictWriter(target, fieldnames=runner.COLUMNS)
                    writer.writeheader()
                    writer.writerows(altered)
                with patch.object(rag, "BASELINE", fixture):
                    with self.assertRaises(ValueError):
                        rag.validate_rankings(cases, patterns, runner.COLUMNS)

    def test_configuration_drift_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "synthetic-retrieval.py"
            fixture.write_text(rag.RETRIEVAL.read_text(encoding="utf-8").replace(
                "VECTOR_CANDIDATES = 15", "VECTOR_CANDIDATES = 5"), encoding="utf-8")
            with patch.object(rag, "RETRIEVAL", fixture):
                with self.assertRaisesRegex(ValueError, "configuration differs"):
                    rag.configuration()

    def test_missing_frozen_baseline_does_not_use_reproduction(self):
        with patch.object(rag, "BASELINE", rag.BASELINE.with_name("missing.csv")):
            with self.assertRaises(FileNotFoundError):
                rag.audit_protocol()


if __name__ == "__main__":
    unittest.main()
