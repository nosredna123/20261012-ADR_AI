"""Check overlap definitions and undefined denominators, not retrieval accuracy."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_rag_results.py"
SPEC = importlib.util.spec_from_file_location("rq_two", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load RQ2 generator: {SCRIPT}")
rq = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rq)


class RagResultsTests(unittest.TestCase):
    def test_frozen_counts_matches_and_determinism(self):
        audit = rq.audit_results()
        self.assertEqual((audit["positive_count"], audit["overlap_count"],
                          audit["outside_count"], audit["overlap_story_count"]), (36, 5, 31, 5))
        self.assertEqual(audit["pooled_overlap_percent"], "13.89")
        self.assertEqual([row["overlap_count"] for row in audit["stories"].values()],
                         [1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0])
        self.assertEqual(audit["stories"]["SYS01-US01"]["matched_pattern_ids"], ["016"])
        self.assertEqual(audit["stories"]["SYS01-US02"]["matched_pattern_ids"], ["003"])
        for uid in ("SYS02-US01", "SYS02-US02", "SYS02-US03"):
            self.assertEqual(audit["stories"][uid]["matched_pattern_ids"], ["002"])
        self.assertIsNone(audit["stories"]["SYS04-US01"]["overlap_percent"])
        outputs = rq.render_outputs(audit)
        self.assertEqual(json.loads(outputs[rq.AUDIT]), audit)
        self.assertEqual(outputs, rq.render_outputs(rq.audit_results()))
        self.assertIn("SYS04-US01 & 0 & 0 & 0 & --", outputs[rq.TABLE])
        self.assertIn(r"\StudyRagOverlapCount{}", outputs[rq.TABLE])

    def test_same_story_membership_and_pooled_not_mean_percentage(self):
        top = ["001", "002", "003", "004", "005"]
        result = rq.compare_sets(
            {"A": {"001"}, "B": {"006", "007", "008"}, "C": set()},
            {"A": top, "B": top, "C": top},
        )
        self.assertEqual(result["pooled_overlap_percent"], "25.00")
        self.assertEqual(result["stories"]["A"]["overlap_percent"], "100.00")
        self.assertEqual(result["stories"]["B"]["overlap_percent"], "0.00")
        self.assertIsNone(result["stories"]["C"]["overlap_percent"])
        self.assertEqual(rq.compare_sets({"A": set()}, {"A": top})["pooled_overlap_percent"], None)
        reordered = rq.compare_sets({"A": {"001"}}, {"A": list(reversed(top))})
        self.assertEqual(reordered["overlap_count"], 1)

    def test_invalid_coverage_rankings_and_pattern_ids_fail(self):
        top = ["001", "002", "003", "004", "005"]
        fixtures = [
            ({}, {}), ({"A": set()}, {"B": top}),
            ({"A": set()}, {"A": top[:4]}),
            ({"A": set()}, {"A": ["001"] * 5}),
            ({"A": {"1"}}, {"A": top}), ({"A": {"071"}}, {"A": top}),
        ]
        for positives, rankings in fixtures:
            with self.subTest(positives=positives, rankings=rankings), self.assertRaises(ValueError):
                rq.compare_sets(positives, rankings)

    def test_read_only_check_rejects_stale_and_missing_outputs(self):
        outputs = rq.render_outputs(rq.audit_results())
        with tempfile.TemporaryDirectory() as directory:
            relocated = {Path(directory) / path.name: text for path, text in outputs.items()}
            for path, text in relocated.items():
                path.write_text(text, encoding="utf-8")
            with patch.object(rq, "render_outputs", return_value=relocated), \
                    patch.object(rq, "audit_results", return_value={}), \
                    patch.object(rq.sys, "argv", ["prepare_rag_results.py", "--check"]):
                self.assertEqual(rq.main(), 0)
                path = next(iter(relocated))
                path.write_text("synthetic stale\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Stale"):
                    rq.main()
                self.assertEqual(path.read_text(encoding="utf-8"), "synthetic stale\n")
                path.unlink()
                with self.assertRaises(FileNotFoundError):
                    rq.main()
                self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
