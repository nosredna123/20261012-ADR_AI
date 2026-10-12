"""Test count reconciliation without modifying empirical sources."""

import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_study_values.py"
SPEC = importlib.util.spec_from_file_location("study_values", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load study-value validator: {SCRIPT}")
study = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(study)


class StudyValuesTests(unittest.TestCase):
    def test_exact_totals_provenance_and_determinism(self):
        audit = study.audit_values()
        expected = {
            "StudySystemCount": 4, "StudyStoryCount": 12, "StudyStoriesPerSystem": 3,
            "StudyCriterionCount": 35, "StudyPatternCount": 70,
            "StudyAssessmentCount": 840, "StudyApplicableCount": 36,
            "StudyNotApplicableCount": 31, "StudyInsufficientInformationCount": 773,
            "StudyPositiveStoryCount": 11, "StudyAdrCount": 36,
            "StudyRagOverlapCount": 5, "StudyRagOutsideCount": 31,
            "StudyRagOverlapStoryCount": 5,
        }
        self.assertEqual({key: item["value"] for key, item in audit["values"].items()},
                         expected)
        self.assertTrue(all(item["source"] and item["computation"]
                            for item in audit["values"].values()))
        self.assertEqual(sum(audit["reconciliation"]["classification_totals"].values()), 840)
        self.assertEqual(audit["reconciliation"]["zero_positive_story_ids"], ["SYS04-US01"])
        self.assertEqual(len(audit["reconciliation"]["positive_story_ids"]), 11)
        outputs = study.render_outputs(audit)
        self.assertEqual(study.render_outputs(study.audit_values()), outputs)
        self.assertEqual(json.loads(outputs[study.AUDIT]), audit)
        for name, value in expected.items():
            self.assertIn(f"\\newcommand{{\\{name}}}{{{value}}}", outputs[study.MACROS])
        self.assertTrue(all(re.fullmatch("[0-9a-f]{64}", item["sha256"])
                            for item in audit["inputs"]))

    def test_csv_schema_values_duplicates_missing_and_extra_rows_fail(self):
        expected = [{"id": "001", "count": 2}, {"id": "002", "count": 0}]
        fixtures = (
            "id,count\n001,2\n002,0\n",
            "count,id\n2,001\n0,002\n",
            "id,count\n1,2\n002,0\n",
            "id,count\n001,3\n002,0\n",
            "id,count\n001,2\n001,2\n",
            "id,count\n001,2\n",
            "id,count\n001,2\n002,0\n003,0\n",
            "id,count\n001,2,extra\n002,0\n",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic-counts.csv"
            path.write_text(fixtures[0], encoding="utf-8")
            study.verify_csv(path, ("id", "count"), expected)
            for content in fixtures[1:]:
                with self.subTest(content=content):
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        study.verify_csv(path, ("id", "count"), expected)

    def test_frozen_summary_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pattern_selection_summary.csv"
            path.write_text(
                (study.RESULTS / path.name).read_text(encoding="utf-8").replace(
                    "SYS04,SYS04-US01,0,,0", "SYS04,SYS04-US01,1,001,0"
                ), encoding="utf-8",
            )
            original = study.verify_csv

            def verify(candidate, columns, expected):
                return original(path if candidate.name == path.name else candidate,
                                columns, expected)

            with patch.object(study, "verify_csv", side_effect=verify):
                with self.assertRaisesRegex(ValueError, "official reconstruction"):
                    study.audit_values()

    def test_missing_input_fails(self):
        with self.assertRaises(FileNotFoundError):
            study.verify_csv(study.PROJECT / "synthetic-missing.csv", ("id",), [])

    def test_core_macros_have_one_owner(self):
        names = study.audit_values()["values"]
        data = study.PROJECT / "latex-code/data"
        for name in names:
            owners = [path.name for path in data.glob("*.tex")
                      if f"\\newcommand{{\\{name}}}" in path.read_text(encoding="utf-8")]
            self.assertEqual(owners, ["study-values.tex"], name)

    def test_check_is_read_only_and_rejects_stale_artifacts(self):
        outputs = study.render_outputs(study.audit_values())
        with tempfile.TemporaryDirectory() as directory:
            relocated = {Path(directory) / path.name: text for path, text in outputs.items()}
            for path, text in relocated.items():
                path.write_text(text, encoding="utf-8")
            with patch.object(study, "render_outputs", return_value=relocated), \
                    patch.object(study, "audit_values", return_value={}), \
                    patch.object(study.sys, "argv", ["prepare_study_values.py", "--check"]):
                self.assertEqual(study.main(), 0)
                path = next(iter(relocated))
                path.write_text("synthetic stale output\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Stale"):
                    study.main()
                self.assertEqual(path.read_text(encoding="utf-8"), "synthetic stale output\n")


if __name__ == "__main__":
    unittest.main()
