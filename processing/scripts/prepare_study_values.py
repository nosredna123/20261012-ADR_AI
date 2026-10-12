"""Reconcile frozen computational artifacts and centralize study-count macros offline."""

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Mapping, Sequence

PROJECT = Path(__file__).resolve().parents[2]
SOURCE = PROJECT / "docs/20261012.0933-InitialArtifacts/adr4ai_app"
SCRIPTS = Path(__file__).resolve().parent
MACROS = PROJECT / "latex-code/data/study-values.tex"
AUDIT = PROJECT / "processing/outputs/study-values-audit.json"
ASSESSMENTS = SOURCE / "experiments/pattern_selection/outputs"
RESULTS = SOURCE / "research_results"


def load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load frozen-artifact validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_csv(
    path: Path, columns: Sequence[str], expected: Sequence[Mapping[str, object]]
) -> None:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != list(columns):
            raise ValueError(f"Frozen CSV schema mismatch: {path.name}")
        rows = list(reader)
    normalized = [{field: str(row[field]) for field in columns} for row in expected]
    if rows != normalized:
        raise ValueError(f"Frozen CSV rows differ from official reconstruction: {path.name}")


def audit_values() -> dict:
    dataset = load_module(SCRIPTS / "prepare_dataset_summary.py")
    dataset_outputs = dataset.render_outputs()
    sample = json.loads(dataset_outputs[
        PROJECT / "processing/outputs/dataset-summary-audit.json"
    ])
    catalog = load_module(SCRIPTS / "prepare_catalog_summary.py").summarize_catalog()
    applicability = load_module(
        SCRIPTS / "prepare_applicability_protocol.py"
    ).audit_protocol()
    rag = load_module(SCRIPTS / "prepare_rag_protocol.py").audit_protocol()
    adr = load_module(SCRIPTS / "prepare_adr_protocol.py").audit_protocol()
    compiler = load_module(RESULTS / "compile_results.py")
    selected, summary, labels = compiler.compile_results()
    exporter = load_module(SOURCE / "experiments/pattern_selection/export_results.py")
    all_rows, exported_labels = exporter.load_rows(ASSESSMENTS / "assessments.jsonl")
    if exported_labels != labels or len(all_rows) != applicability["validated_official_records"]:
        raise ValueError("Official JSONL, export and compiler label totals disagree")
    verify_csv(ASSESSMENTS / "pattern_assessments.csv", exporter.COLUMNS, all_rows)
    verify_csv(
        ASSESSMENTS / "applicable_patterns.csv", exporter.COLUMNS,
        [row for row in all_rows if row["classification"] == "applicable"],
    )
    verify_csv(RESULTS / "pattern_selection_results_before_adr.csv",
               compiler.RESULT_FIELDS, selected)
    verify_csv(RESULTS / "pattern_selection_summary.csv", compiler.SUMMARY_FIELDS, summary)
    if (sample["story_count"] != applicability["story_count"]
            or sample["story_count"] != rag["story_count"]
            or catalog["pattern_count"] != applicability["pattern_count"]
            or catalog["pattern_count"] != rag["pattern_count"]
            or sample["criterion_count"] != rag["criterion_count"]
            or sum(labels.values()) != sample["story_count"] * catalog["pattern_count"]
            or len(selected) != labels["applicable"] or adr["adr_count"] != len(selected)):
        raise ValueError("Requirement, catalog, assessment, RAG or ADR counts disagree")

    story_sizes = {group["stories"] for group in sample["systems"].values()}
    if len(story_sizes) != 1:
        raise ValueError("Stories-per-system macro requires equal story counts")
    overlap = sum(row["rag_top5"] == "yes" for row in selected)
    if overlap != sum(row["rag_top5_overlap_count"] for row in summary):
        raise ValueError("Pair-level and summary overlap counts disagree")
    values = {
        "StudySystemCount": sample["system_count"],
        "StudyStoryCount": sample["story_count"],
        "StudyStoriesPerSystem": next(iter(story_sizes)),
        "StudyCriterionCount": sample["criterion_count"],
        "StudyPatternCount": catalog["pattern_count"],
        "StudyAssessmentCount": applicability["validated_official_records"],
        "StudyApplicableCount": labels["applicable"],
        "StudyNotApplicableCount": labels["not_applicable"],
        "StudyInsufficientInformationCount": labels["insufficient_information"],
        "StudyPositiveStoryCount": sum(row["applicable_count"] > 0 for row in summary),
        "StudyAdrCount": adr["adr_count"],
        "StudyRagOverlapCount": overlap,
        "StudyRagOutsideCount": len(selected) - overlap,
        "StudyRagOverlapStoryCount": sum(row["rag_top5_overlap_count"] > 0 for row in summary),
    }
    provenance = {
        "StudySystemCount": ("data/user_histories_orig.csv", "Distinct validated system IDs"),
        "StudyStoryCount": ("data/user_histories_orig.csv", "Distinct validated story IDs"),
        "StudyStoriesPerSystem": ("data/user_histories_orig.csv", "Common story count per system"),
        "StudyCriterionCount": ("data/user_histories_orig.csv", "Validated criterion rows"),
        "StudyPatternCount": ("catalogs/patterns/", "Unique validated pattern IDs"),
        "StudyAssessmentCount": ("experiments/pattern_selection/outputs/assessments.jsonl",
                                 "Unique complete story-pattern pairs; not API attempts"),
        "StudyApplicableCount": ("experiments/pattern_selection/outputs/assessments.jsonl",
                                "Records classified applicable; not ground truth"),
        "StudyNotApplicableCount": ("experiments/pattern_selection/outputs/assessments.jsonl",
                                   "Records classified not_applicable"),
        "StudyInsufficientInformationCount": (
            "experiments/pattern_selection/outputs/assessments.jsonl",
            "Records classified insufficient_information"),
        "StudyPositiveStoryCount": ("research_results/pattern_selection_summary.csv",
                                   "Stories with applicable_count > 0"),
        "StudyAdrCount": ("experiments/adr_generation/outputs/",
                         "Validated unique final ADR pairs, including approved pilot; not attempts"),
        "StudyRagOverlapCount": ("experiments/rag/outputs/rag_baseline.csv",
                                "Same-story final Top-5 membership among LLM-positive pairs"),
        "StudyRagOutsideCount": ("experiments/rag/outputs/rag_baseline.csv",
                                "LLM-positive pairs outside final Top-5; not false negatives"),
        "StudyRagOverlapStoryCount": ("research_results/pattern_selection_summary.csv",
                                     "Stories with rag_top5_overlap_count > 0"),
    }
    paths = {Path(item["path"]) for audit in (applicability, rag, adr)
             for item in audit["inputs"]}
    paths.update({
        Path(sample["source"]), Path(sample["validator"]), Path(catalog["validator"]),
    })
    paths.update(Path(catalog["source_directory"]) / record["file"]
                 for record in catalog["records"])
    paths.update(path.relative_to(PROJECT) for path in (
        ASSESSMENTS / "pattern_assessments.csv", ASSESSMENTS / "applicable_patterns.csv",
        RESULTS / "pattern_selection_summary.csv",
        SOURCE / "experiments/pattern_selection/export_results.py",
        Path(__file__).resolve(),
        *(SCRIPTS / f"prepare_{name}.py" for name in
          ("dataset_summary", "catalog_summary", "applicability_protocol",
           "rag_protocol", "adr_protocol")),
    ))
    paths.update(Path("docs/20261012.0933-InitialArtifacts/adr4ai_app")
                 / "experiments/adr_generation/outputs" / record["file"]
                 for record in adr["records"])
    return {
        "task": "2.1",
        "values": {
            name: {"value": value, "source": provenance[name][0],
                   "computation": provenance[name][1]}
            for name, value in values.items()
        },
        "source_base": SOURCE.relative_to(PROJECT).as_posix(),
        "inputs": [
            {"path": path.as_posix(),
             "sha256": hashlib.sha256((PROJECT / path).read_bytes()).hexdigest()}
            for path in sorted(paths)
        ],
        "reconciliation": {
            "all_assessment_csv_rows": len(all_rows),
            "positive_export_and_compiled_rows": len(selected),
            "summary_rows_including_zero_positive": len(summary),
            "adr_pair_set_equals_positive_pair_set": True,
            "adr_and_enriched_csv_match_frozen_compiler_outputs": True,
            "classification_totals": dict(labels),
            "positive_story_ids": [row["user_story_id"] for row in summary
                                   if row["applicable_count"] > 0],
            "zero_positive_story_ids": [row["user_story_id"] for row in summary
                                        if row["applicable_count"] == 0],
        },
        "scope": (
            "Offline structural/count reconciliation against frozen official records. "
            "No expert responses, API calls, retrieval execution, accuracy claims or "
            "new empirical results. Positive-only assessments are model predictions."
        ),
    }


def render_outputs(audit: dict) -> dict[Path, str]:
    lines = [
        "% !TeX root = ../main.tex",
        "% Generated by processing/scripts/prepare_study_values.py.",
        "% Sole owner of core study counts; configuration/preparation macros stay separate.",
        "% Value-to-source audit (paths relative to the initial adr4ai_app directory):",
    ]
    for name, item in audit["values"].items():
        lines.append(f"% {name} = {item['value']} | {item['source']} | {item['computation']}")
        lines.append(f"\\newcommand{{\\{name}}}{{{item['value']}}}")
    return {
        MACROS: "\n".join(lines) + "\n",
        AUDIT: json.dumps(audit, indent=2, sort_keys=True) + "\n",
    }


def main() -> int:
    if sys.argv[1:] not in ([], ["--check"]):
        raise ValueError("Usage: prepare_study_values.py [--check]")
    outputs = render_outputs(audit_values())
    for path, content in outputs.items():
        if sys.argv[1:] == ["--check"]:
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Stale study-value artifact: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"Wrote {path.relative_to(PROJECT)}")
    print("PASS: centralized study counts and frozen JSONL/CSV/ADR reconciliation")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, ImportError, KeyError) as error:
        print(f"Study-value verification failed: {error}", file=sys.stderr)
        sys.exit(1)
