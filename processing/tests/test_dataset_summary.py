"""Check Task 1.2 sample aggregation and fail-closed identifier handling."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_dataset_summary.py"
SPEC = importlib.util.spec_from_file_location("dataset_summary", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load dataset summary script: {SCRIPT}")
summary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(summary)


class DatasetSummaryTests(unittest.TestCase):
    def test_totals_and_generated_macros(self):
        outputs = summary.render_outputs()
        audit = json.loads(outputs[
            summary.PROJECT / "processing/outputs/dataset-summary-audit.json"
        ])
        self.assertEqual(
            (audit["system_count"], audit["story_count"], audit["criterion_count"]),
            (4, 12, 35),
        )
        self.assertEqual(sum(g["criteria"] for g in audit["systems"].values()), 35)
        self.assertTrue(all(g["stories"] == 3 for g in audit["systems"].values()))
        self.assertIn(
            r"\newcommand{\StudyCriterionCount}{35}",
            outputs[summary.LATEX / "data/study-values.tex"],
        )
        self.assertEqual(summary.render_outputs(), outputs)

    def test_missing_input_is_rejected(self):
        with patch.object(summary, "SOURCE", summary.SOURCE.with_name("missing.csv")):
            with self.assertRaises(FileNotFoundError):
                summary.render_outputs()

    def test_missing_validator_is_rejected(self):
        with patch.object(summary, "LOADER", summary.LOADER.with_name("missing.py")):
            with self.assertRaises(FileNotFoundError):
                summary.render_outputs()

    def test_mismatched_system_identifier_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            invalid_source = Path(directory) / "synthetic-invalid.csv"
            invalid_source.write_text(
                summary.SOURCE.read_text(encoding="utf-8").replace(
                    "System_01", "System_99"
                ),
                encoding="utf-8",
            )
            with patch.object(summary, "SOURCE", invalid_source):
                with self.assertRaisesRegex(ValueError, "System/story identifier mismatch"):
                    summary.render_outputs()


if __name__ == "__main__":
    unittest.main()
