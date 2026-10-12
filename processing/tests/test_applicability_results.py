"""RQ1 count and publication-output tests; no synthetic empirical results."""

import copy
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_applicability_results.py"
SPEC = importlib.util.spec_from_file_location("rq_one", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load RQ1 generator: {SCRIPT}")
rq = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rq)


class ApplicabilityResultsTests(unittest.TestCase):
    def test_empirical_totals_and_deterministic_outputs(self):
        audit = rq.audit_results()
        self.assertEqual(audit["labels"],
                         {"applicable": 36, "not_applicable": 31, "insufficient_information": 773})
        self.assertEqual(audit["denominator"], 840)
        self.assertEqual([row["labels"]["applicable"] for row in audit["stories"].values()],
                         [3, 1, 3, 5, 5, 2, 1, 5, 2, 0, 2, 7])
        self.assertEqual([row["labels"]["applicable"] for row in audit["systems"].values()],
                         [7, 12, 8, 9])
        self.assertEqual({row["denominator"] for row in audit["stories"].values()}, {70})
        self.assertEqual({row["denominator"] for row in audit["systems"].values()}, {210})
        for label in rq.LABELS:
            self.assertEqual(sum(row["labels"][label] for row in audit["stories"].values()),
                             audit["labels"][label])
            self.assertEqual(sum(row["labels"][label] for row in audit["systems"].values()),
                             audit["labels"][label])
        outputs = rq.render_outputs(audit)
        self.assertEqual(outputs, rq.render_outputs(rq.audit_results()))
        self.assertEqual(json.loads(outputs[rq.AUDIT]), audit)
        self.assertIn("SYS04-US01 & 0", outputs[rq.TABLE])
        self.assertIn(r"\newcommand{\RqOneApplicablePercent}{4.29}", outputs[rq.MACROS])
        self.assertIn(r"\newcommand{\RqOneNotApplicablePercent}{3.69}", outputs[rq.MACROS])
        self.assertIn(r"\newcommand{\RqOneInsufficientInformationPercent}{92.02}", outputs[rq.MACROS])
        names = re.findall(r"\\newcommand\{\\([^}]+)\}", outputs[rq.MACROS])
        self.assertTrue(all(re.fullmatch("[A-Za-z]+", name) for name in names))
        for sid, macro in rq.SYSTEM_MACROS.items():
            count = audit["systems"][sid]["labels"]["applicable"]
            self.assertIn(f"\\newcommand{{\\{macro}}}{{{count}}}", outputs[rq.MACROS])
            self.assertIn(f"\\{macro}{{}}", outputs[rq.TABLE])

    def test_synthetic_unequal_system_sizes_and_zero_positive_story(self):
        rows = [
            {"system": uid.split("-")[0], "user_story_id": uid,
             "pattern_id": pid, "classification": label}
            for uid in ("SYS01-US01", "SYS01-US02", "SYS02-US01")
            for pid, label in (("001", "not_applicable"), ("002", "insufficient_information"))
        ]
        audit = rq.aggregate(rows, ["SYS01-US01", "SYS01-US02", "SYS02-US01"], 2)
        self.assertEqual(audit["systems"]["SYS01"]["denominator"], 4)
        self.assertEqual(audit["systems"]["SYS02"]["denominator"], 2)
        self.assertEqual(audit["labels"]["applicable"], 0)
        self.assertEqual(len(audit["stories"]), 3)
        for mutation in ("missing", "duplicate", "label", "story", "pattern", "system"):
            altered = copy.deepcopy(rows)
            if mutation == "missing":
                altered.pop()
            elif mutation == "duplicate":
                altered.append(dict(rows[0]))
            else:
                field, value = {
                    "label": ("classification", "unknown"), "story": ("user_story_id", "unknown"),
                    "pattern": ("pattern_id", "003"), "system": ("system", "SYS99"),
                }[mutation]
                altered[0][field] = value
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                rq.aggregate(altered, ["SYS01-US01", "SYS01-US02", "SYS02-US01"], 2)

    def test_percentage_denominators_and_rounding(self):
        self.assertEqual(rq.percentage(7, 70), "10.00")
        self.assertEqual(rq.percentage(7, 210), "3.33")
        self.assertEqual(rq.percentage(0, 70), "0.00")
        for count, denominator in ((1, 0), (-1, 70), (71, 70)):
            with self.assertRaises(ValueError):
                rq.percentage(count, denominator)

    def test_check_rejects_stale_and_missing_outputs_without_writing(self):
        outputs = rq.render_outputs(rq.audit_results())
        with tempfile.TemporaryDirectory() as directory:
            relocated = {Path(directory) / path.name: text for path, text in outputs.items()}
            for path, text in relocated.items():
                path.write_text(text, encoding="utf-8")
            with patch.object(rq, "render_outputs", return_value=relocated), \
                    patch.object(rq, "audit_results", return_value={}), \
                    patch.object(rq.sys, "argv", ["prepare_applicability_results.py", "--check"]):
                self.assertEqual(rq.main(), 0)
                path = next(iter(relocated))
                path.write_text("synthetic stale output\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Stale"):
                    rq.main()
                self.assertEqual(path.read_text(encoding="utf-8"), "synthetic stale output\n")
                path.unlink()
                with self.assertRaises(FileNotFoundError):
                    rq.main()
                self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
