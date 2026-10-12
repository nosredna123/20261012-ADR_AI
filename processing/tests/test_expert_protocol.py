"""Preparation audit tests; no evaluator responses or remote form execution."""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_expert_protocol.py"
SPEC = importlib.util.spec_from_file_location("expert_protocol", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load preparation audit: {SCRIPT}")
expert = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(expert)


class ExpertPreparationTests(unittest.TestCase):
    def test_complete_preparation_and_determinism(self):
        audit = expert.audit_preparation()
        self.assertEqual(audit["case_count"], 36)
        self.assertEqual(audit["mapping_count"], 324)
        self.assertEqual(audit["manual_correction_count"], 5)
        self.assertEqual(audit["language_categories"],
                         {"portuguese": 12, "non_portuguese": 289,
                          "mixed_portuguese_non_portuguese": 14, "empty": 9})
        self.assertEqual(audit["questionnaire"]["cases_per_system"], expert.SYSTEM_COUNTS)
        self.assertEqual(audit["questionnaire"]["required_rating_count_across_all_routes"], 180)
        self.assertEqual(len(audit["questionnaire"]["profile_questions_pt"]), 3)
        self.assertFalse(audit["results_inspected"])
        self.assertEqual(expert.render_outputs(audit),
                         expert.render_outputs(expert.audit_preparation()))

    def test_form_content_and_settings_drift_fail(self):
        compiler = expert.load_compiler()
        _, cases = compiler.read_csv(expert.RESULTS / "expert_evaluation_cases_pt.csv")
        original = expert.FORM.read_text(encoding="utf-8")
        changes = (
            ("const EVALUATION_CASES = [", "const EVALUATION_CASES = [];\nconst OLD_CASES = ["),
            ("form.setCollectEmail(false);", "form.setCollectEmail(true);"),
            ("const ALLOW_FORM_CREATION = false;", "const ALLOW_FORM_CREATION = true;"),
            ("sections[system].setGoToPage(finalSection);",
             "sections[system].setGoToPage(sections[system]);"),
            (".setBounds(1, 5).setLabels('Discordo totalmente'",
             ".setBounds(1, 7).setLabels('Discordo totalmente'"),
        )
        for before, after in changes:
            with self.subTest(before=before):
                with self.assertRaises(ValueError):
                    expert.validate_form(cases, original.replace(before, after))

    def test_missing_question_fails(self):
        with self.assertRaisesRegex(ValueError, "exactly five"):
            expert.question_wording("const EVALUATION_QUESTIONS = ['Synthetic'];")

    def test_unapproved_translation_change_fails(self):
        compiler = expert.load_compiler()
        rows = compiler.validate_source()
        labels = compiler.load_inventory(rows)
        _, mappings = compiler.read_csv(expert.RESULTS / "expert_evaluation_translations_pt.csv")
        altered = [dict(row) for row in mappings]
        target = next(row for row in altered if row["translation_action"] == "translated_non_portuguese")
        target["evaluation_text_pt"] += " synthetic unapproved change"
        with self.assertRaisesRegex(ValueError, "Unapproved presentation change"):
            compiler.load_review_provenance(rows, altered, labels)

    def test_source_requirement_change_fails(self):
        compiler = expert.load_compiler()
        _, cases = compiler.read_csv(expert.RESULTS / "expert_evaluation_cases_pt.csv")
        changed = [dict(row) for row in cases]
        changed[0]["user_story"] = "Synthetic changed requirement"
        with self.assertRaisesRegex(ValueError, "Embedded questionnaire cases differ"):
            expert.validate_form(changed, expert.FORM.read_text(encoding="utf-8"))

    def test_missing_form_fails(self):
        with patch.object(expert, "FORM", expert.FORM.with_name("missing.gs")):
            with self.assertRaises(FileNotFoundError):
                expert.audit_preparation()


if __name__ == "__main__":
    unittest.main()
