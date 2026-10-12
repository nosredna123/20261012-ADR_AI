"""Offline protocol checks; altered records exist only in temporary test fixtures."""

import importlib.util
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_applicability_protocol.py"
SPEC = importlib.util.spec_from_file_location("applicability_protocol", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load applicability script: {SCRIPT}")
protocol = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(protocol)


class ApplicabilityProtocolTests(unittest.TestCase):
    def test_complete_official_log_and_deterministic_outputs(self):
        audit = protocol.audit_protocol()
        self.assertEqual(audit["planned_pair_count"], 840)
        self.assertEqual(audit["validated_official_records"], 840)
        self.assertEqual(set(audit["records_per_story"].values()), {70})
        self.assertEqual(len(audit["records_per_story"]), 12)
        self.assertEqual(audit["model"], "gpt-6-sol")
        self.assertEqual(audit["reasoning_effort"], "high")
        self.assertEqual(audit["max_attempts_per_pair"], 3)
        self.assertIsNone(audit["total_api_attempts"])
        self.assertEqual(len(audit["excluded_pilot_and_test_paths"]), 5)
        self.assertEqual(protocol.render_outputs(audit),
                         protocol.render_outputs(protocol.audit_protocol()))

    def test_original_imports_are_restored(self):
        sentinel = SimpleNamespace()
        with patch.dict(sys.modules, {"prepare_data": sentinel}):
            protocol.load_protocol()
            self.assertIs(sys.modules["prepare_data"], sentinel)

    def test_invalid_official_records_fail(self):
        records = protocol.OFFICIAL.read_text(encoding="utf-8").splitlines()
        mutations = ("missing_pair", "duplicate_pair", "configuration", "bad_ref",
                     "missing_positive_ref", "missing_newline", "invalid_label",
                     "extra_field")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                altered = list(records)
                if mutation == "missing_pair":
                    altered.pop()
                elif mutation == "duplicate_pair":
                    altered.append(altered[0])
                elif mutation in ("configuration", "bad_ref", "missing_positive_ref",
                                  "invalid_label", "extra_field"):
                    record = json.loads(altered[0])
                    if mutation == "configuration":
                        record["model"] = "synthetic-invalid-model"
                    elif mutation == "bad_ref":
                        record["requirement_refs"] = ["synthetic-unknown-reference"]
                    elif mutation == "invalid_label":
                        record["classification"] = "synthetic-invalid-label"
                    elif mutation == "extra_field":
                        record["synthetic_extra_field"] = True
                    else:
                        record["classification"] = "applicable"
                        record["requirement_refs"] = []
                    altered[0] = json.dumps(record)
                path = Path(directory) / "synthetic-invalid.jsonl"
                path.write_text("\n".join(altered)
                                + ("" if mutation == "missing_newline" else "\n"),
                                encoding="utf-8")
                with patch.object(protocol, "OFFICIAL", path):
                    with self.assertRaises(ValueError):
                        protocol.audit_protocol()

    def test_missing_failure_log_fails(self):
        with patch.object(protocol, "FAILURES", protocol.FAILURES.with_name("missing.jsonl")):
            with self.assertRaisesRegex(ValueError, "Both frozen official"):
                protocol.audit_protocol()

    def test_invalid_attempt_budget_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            record = {
                "user_story_id": "SYS01-US01", "pattern_id": "001",
                "attempts": 4, "error_type": "SyntheticFailure",
                "error_message": "Synthetic invalid attempt budget",
            }
            path = Path(directory) / "synthetic-failures.jsonl"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            with patch.object(protocol, "FAILURES", path):
                with self.assertRaisesRegex(ValueError, "invalid attempt count"):
                    protocol.audit_protocol()

    def test_resume_skips_all_valid_pairs_without_requests(self):
        _, runner = protocol.load_protocol()
        cases, patterns = runner.load_inputs()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            assessment = output / "assessments.jsonl"
            original = protocol.OFFICIAL.read_bytes()
            assessment.write_bytes(original)
            (output / "failures.jsonl").write_text("", encoding="utf-8")
            with patch.object(runner, "assess_pattern") as request:
                with redirect_stdout(io.StringIO()):
                    self.assertTrue(runner.run_experiment(Mock(), cases, patterns, output))
                request.assert_not_called()
            self.assertEqual(assessment.read_bytes(), original)
            self.assertEqual(len(list((output / "selected_patterns").glob("*.json"))), 12)

    def test_strict_request_shape_without_network(self):
        assessor, _ = protocol.load_protocol()
        case = {"user_story_id": "SYNTHETIC-US01", "requirement_text": "Synthetic test",
                "acceptance_criteria": []}
        pattern = {field: f"synthetic-{field}" for field in
                   ("id", "name", "motivation", "solution", "consequences")}
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(
            status="completed", output=[],
            output_text=json.dumps({"classification": "insufficient_information",
                                    "requirement_refs": [], "rationale": "Synthetic test"}),
        )
        assessor.assess_pattern(client, case, pattern)
        client.responses.create.assert_called_once()
        arguments = client.responses.create.call_args.kwargs
        self.assertEqual(arguments["model"], "gpt-6-sol")
        self.assertEqual(arguments["reasoning"], {"effort": "high"})
        self.assertEqual(arguments["instructions"], assessor.INSTRUCTIONS)
        self.assertEqual(arguments["text"]["format"]["type"], "json_schema")
        self.assertIs(arguments["text"]["format"]["strict"], True)
        self.assertEqual(arguments["text"]["format"]["schema"], assessor.ASSESSMENT_SCHEMA)


if __name__ == "__main__":
    unittest.main()
