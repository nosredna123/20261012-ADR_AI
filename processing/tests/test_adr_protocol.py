"""Offline ADR audit tests; synthetic mutations never modify frozen artifacts."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_adr_protocol.py"
SPEC = importlib.util.spec_from_file_location("adr_protocol", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load ADR audit: {SCRIPT}")
adr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adr)


class AdrProtocolTests(unittest.TestCase):
    def test_complete_frozen_outputs_and_determinism(self):
        audit = adr.audit_protocol()
        self.assertEqual(audit["adr_count"], 36)
        self.assertEqual(len({tuple(record["pair"]) for record in audit["records"]}), 36)
        self.assertEqual(audit["history"]["claim_count"], 36)
        self.assertEqual(audit["history"]["failure_count"], 1)
        self.assertEqual(audit["pilot_pair"], ["SYS01-US01", "001"])
        self.assertEqual({record["status"] for record in audit["records"]}, {"Proposed"})
        self.assertNotIn("rag_top5", audit["input_fields"])
        self.assertIn("synthetic", audit["prompt_template"])
        self.assertEqual(adr.render_outputs(audit),
                         adr.render_outputs(adr.audit_protocol()))

    def test_invalid_completed_metadata_and_fields_fail(self):
        generator, runner = adr.load_protocol()
        compiler = adr.load_module(adr.SOURCE / "research_results/compile_adr_results.py",
                                   "test_adr_compiler")
        _, rows = compiler.csv_rows(adr.BACKUP.read_bytes())
        prompts = {runner.pair_of(row): runner.prompt_for(row) for row in rows}
        source_hash = runner.digest(adr.BACKUP.read_bytes())
        original = runner.read_json(generator.OUTPUT)
        for mutation in ("source_sha256", "prompt_sha256", "api_calls",
                         "status", "empty_field", "extra_field"):
            with self.subTest(mutation=mutation):
                record = json.loads(json.dumps(original))
                if mutation in ("source_sha256", "prompt_sha256"):
                    record[mutation] = "synthetic-invalid-hash"
                elif mutation == "api_calls":
                    record["api_calls"] = 2
                elif mutation == "status":
                    record["adr"]["status"] = "Accepted"
                elif mutation == "empty_field":
                    record["adr"]["decision"] = ""
                else:
                    record["adr"]["synthetic_extra_field"] = "Invalid"
                with self.assertRaises(ValueError):
                    runner.validate_completed(record, prompts, source_hash)

    def test_unapproved_retry_fails(self):
        _, runner = adr.load_protocol()
        expected = {tuple(record["pair"]) for record in adr.audit_protocol()["records"]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "attempts").mkdir()
            for path in (adr.OUTPUTS / "attempts").glob("*.json"):
                record = runner.read_json(path)
                if ".retry-" in path.name:
                    record["manual_retry_authorized"] = False
                (root / "attempts" / path.name).write_text(
                    json.dumps(record), encoding="utf-8")
            with patch.object(adr, "OUTPUTS", root):
                with self.assertRaisesRegex(ValueError, "not explicitly authorized"):
                    adr.validate_history(runner, expected)

    def test_duplicate_json_keys_fail(self):
        generator, _ = adr.load_protocol()
        with self.assertRaisesRegex(ValueError, "Duplicate generated JSON field"):
            json.loads('{"title":"synthetic","title":"duplicate"}',
                       object_pairs_hook=generator.reject_duplicate_keys)

    def test_missing_backup_fails(self):
        with patch.object(adr, "BACKUP", adr.BACKUP.with_name("missing.csv")):
            with self.assertRaises(FileNotFoundError):
                adr.audit_protocol()


if __name__ == "__main__":
    unittest.main()
