"""Protocol/inventory tests without response fixtures or empirical statistics."""

import importlib.util
import json
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_expert_analysis_plan.py"
SPEC = importlib.util.spec_from_file_location("expert_analysis_plan", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load analysis plan: {SCRIPT}")
plan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plan)


class ExpertAnalysisPlanTests(unittest.TestCase):
    def setUp(self):
        self.protocol = json.loads(plan.PROTOCOL.read_text(encoding="utf-8"))
        self.preparation = json.loads(plan.PREPARATION.read_text(encoding="utf-8"))

    def test_approved_choices_and_deterministic_inventory(self):
        plan.validate_protocol(self.protocol, self.preparation)
        self.assertEqual(plan.render_outputs(), plan.render_outputs())
        table = plan.render_outputs()[plan.TABLE]
        self.assertEqual(len(self.protocol["outputs"]), 8)
        self.assertIn("Phase 3", self.protocol["implementation_boundary"])
        self.assertEqual(self.protocol["agreement"]["method"], "Ordinal Krippendorff alpha")
        self.assertIn("Two researchers independently", self.protocol["qualitative"]["coding"])
        self.assertIn("Predeclared", table)
        audit = json.loads(plan.render_outputs()[plan.AUDIT])
        self.assertFalse(audit["response_data_read"])

    def test_success_cutoff_and_imputation_rejected(self):
        for key in ("binary_validated_threshold", "favorable_rating_cutoff"):
            with self.subTest(key=key):
                altered = json.loads(json.dumps(self.protocol))
                altered["interpretation"][key] = 4
                with self.assertRaisesRegex(ValueError, "cutoff"):
                    plan.validate_protocol(altered, self.preparation)
        self.protocol["cell_rules"]["no_imputation"] = False
        with self.assertRaisesRegex(ValueError, "missing-data"):
            plan.validate_protocol(self.protocol, self.preparation)

    def test_inventory_and_instrument_drift_rejected(self):
        for mutation in ("missing", "duplicate", "no_computation", "unsafe_target", "items"):
            with self.subTest(mutation=mutation):
                altered = json.loads(json.dumps(self.protocol))
                if mutation == "missing":
                    altered["outputs"].pop()
                elif mutation == "duplicate":
                    altered["outputs"][-1] = altered["outputs"][0]
                elif mutation == "no_computation":
                    altered["outputs"][0]["computation"] = ""
                elif mutation == "unsafe_target":
                    altered["outputs"][0]["target"] = "../outside.tex"
                else:
                    altered["items"].pop()
                with self.assertRaises(ValueError):
                    plan.validate_protocol(altered, self.preparation)

    def test_false_preregistration_rejected(self):
        self.protocol["timing"]["preregistered_before_collection"] = True
        with self.assertRaisesRegex(ValueError, "timing"):
            plan.validate_protocol(self.protocol, self.preparation)

    def test_tex_reserved_characters_escaped(self):
        self.assertEqual(plan.tex_text("Q1_50% & n"), r"Q1\_50\% \& n")


if __name__ == "__main__":
    unittest.main()
