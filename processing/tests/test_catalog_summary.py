"""Test catalog counts, field preservation, and invalid-input rejection."""

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_catalog_summary.py"
SPEC = importlib.util.spec_from_file_location("catalog_summary", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load catalog script: {SCRIPT}")
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


class CatalogSummaryTests(unittest.TestCase):
    def test_complete_catalog_and_deterministic_outputs(self):
        audit = catalog.summarize_catalog()
        self.assertEqual(audit["pattern_count"], 70)
        self.assertEqual(len(audit["records"]), 70)
        self.assertEqual(audit["records"][0]["id"], "001")
        self.assertEqual(audit["records"][-1]["id"], "070")
        self.assertEqual(audit["model_input_fields"], list(catalog.FIELDS))
        self.assertEqual(audit["empty_fields"]["motivation"],
                         ["044", "045", "046", "047", "069"])
        self.assertEqual(len(audit["empty_fields"]["consequences"]), 31)
        self.assertEqual(catalog.render_outputs(audit),
                         catalog.render_outputs(catalog.summarize_catalog()))

    def test_empty_catalog_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(catalog, "CATALOG", Path(directory)):
                with self.assertRaisesRegex(ValueError, "expected 70 JSON files"):
                    catalog.summarize_catalog()

    def test_missing_validator_fails(self):
        with patch.object(catalog, "LOADER", catalog.LOADER.with_name("missing.py")):
            with self.assertRaises(FileNotFoundError):
                catalog.summarize_catalog()

    def test_missing_and_non_string_input_fields_fail(self):
        for invalid in ("missing", None):
            with self.subTest(invalid=invalid):
                with tempfile.TemporaryDirectory() as directory:
                    fixture = Path(directory) / "synthetic-invalid"
                    shutil.copytree(catalog.CATALOG, fixture)
                    path = fixture / "P001.json"
                    record = json.loads(path.read_text(encoding="utf-8"))
                    if invalid == "missing":
                        del record["motivation"]
                    else:
                        record["motivation"] = invalid
                    path.write_text(json.dumps(record), encoding="utf-8")
                    with patch.object(catalog, "CATALOG", fixture):
                        with self.assertRaisesRegex(ValueError, "missing or non-string"):
                            catalog.summarize_catalog()


if __name__ == "__main__":
    unittest.main()
