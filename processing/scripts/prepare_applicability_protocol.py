"""Audit the frozen applicability protocol and official records without API calls."""

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

PROJECT = Path(__file__).resolve().parents[2]
EXPERIMENT = (
    PROJECT / "docs/20261012.0933-InitialArtifacts/adr4ai_app"
    / "experiments/pattern_selection"
)
OFFICIAL = EXPERIMENT / "outputs/assessments.jsonl"
FAILURES = EXPERIMENT / "outputs/failures.jsonl"
AUDIT = PROJECT / "processing/outputs/applicability-protocol-audit.json"
MACROS = PROJECT / "latex-code/data/applicability-values.tex"


def load_protocol() -> tuple[ModuleType, ModuleType]:
    """Resolve the original sibling imports without changing global import state."""
    names = ("prepare_data", "assess_pattern", "run_experiment")
    previous = {name: sys.modules.get(name) for name in names}
    modules = {}
    try:
        for name in names:
            path = EXPERIMENT / f"{name}.py"
            spec = importlib.util.spec_from_file_location(name, path)
            if spec is None or spec.loader is None:
                raise ValueError(f"Cannot load original protocol: {path}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            modules[name] = module
        return modules["assess_pattern"], modules["run_experiment"]
    finally:
        for name, module in previous.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def fingerprint(path: Path) -> dict[str, str]:
    return {
        "path": path.relative_to(PROJECT).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def audit_protocol() -> dict:
    assessor, runner = load_protocol()
    cases, patterns = runner.load_inputs()
    expected = {(case["user_story_id"], pattern["id"])
                for case in cases for pattern in patterns}
    if not OFFICIAL.is_file() or not FAILURES.is_file():
        raise ValueError("Both frozen official assessment and failure logs are required")
    completed = runner.load_assessments(OFFICIAL, cases, patterns)
    if set(completed) != expected:
        raise ValueError("Official log does not cover exactly all 840 expected pairs")
    unresolved = runner.load_failures(FAILURES, expected, completed)
    if unresolved:
        raise ValueError("Official experiment has unresolved failures")

    # These placeholders expose the exact input template without requirement text.
    template = assessor.build_prompt(
        {"requirement_text": "<system purpose, identified story and criteria>"},
        {field: f"<{field}>" for field in
         ("id", "name", "motivation", "solution", "consequences")},
    )
    catalog_hashes = {
        f"P{pattern['id']}.json": hashlib.sha256(
            (runner.REPOSITORY_ROOT / "catalogs/patterns"
             / f"P{pattern['id']}.json").read_bytes()
        ).hexdigest()
        for pattern in patterns
    }
    inputs = [
        EXPERIMENT / f"{name}.py"
        for name in ("prepare_data", "assess_pattern", "run_experiment", "run_pilot")
    ]
    inputs.extend([
        runner.REPOSITORY_ROOT / "data/user_histories_orig.csv", OFFICIAL, FAILURES,
    ])
    excluded = sorted(
        path.relative_to(PROJECT).as_posix()
        for path in (EXPERIMENT / "outputs").iterdir()
        if path.name.startswith(("pilot_", "test_assessment"))
    )
    return {
        "task": "1.4",
        "inputs": [fingerprint(path) for path in inputs],
        "catalog_file_sha256": catalog_hashes,
        "story_count": len(cases),
        "pattern_count": len(patterns),
        "planned_pair_count": len(expected),
        "validated_official_records": len(completed),
        "records_per_story": {
            case["user_story_id"]: sum(pair[0] == case["user_story_id"]
                                      for pair in completed)
            for case in cases
        },
        "model": assessor.MODEL,
        "reasoning_effort": assessor.REASONING_EFFORT,
        "max_attempts_per_pair": runner.MAX_ATTEMPTS,
        "classifications": list(assessor.CLASSIFICATIONS),
        "assessment_schema": assessor.ASSESSMENT_SCHEMA,
        "instructions": assessor.INSTRUCTIONS,
        "instructions_sha256": hashlib.sha256(
            assessor.INSTRUCTIONS.encode("utf-8")
        ).hexdigest(),
        "input_template_with_placeholders": template,
        "unresolved_failures": len(unresolved),
        "recorded_failure_state_entries": len(runner.read_jsonl(FAILURES)),
        "total_api_attempts": None,
        "attempt_history_limit": (
            "Successful records do not contain attempt counts. Failure state is "
            "removed on success; an empty final file is not evidence of no retries."
        ),
        "excluded_pilot_and_test_paths": excluded,
    }


def render_outputs(audit: dict) -> dict[Path, str]:
    if (audit["model"], audit["reasoning_effort"],
            audit["max_attempts_per_pair"]) != ("gpt-6-sol", "high", 3):
        raise ValueError("Protocol configuration differs from the manuscript")
    return {
        AUDIT: json.dumps(audit, indent=2, sort_keys=True) + "\n",
        MACROS: (
            "% !TeX root = ../main.tex\n"
            "% Generated by processing/scripts/prepare_applicability_protocol.py.\n"
            "% StudyAssessmentCount is owned by data/study-values.tex.\n"
            f"\\newcommand{{\\ApplicabilityModel}}{{{audit['model']}}}\n"
            f"\\newcommand{{\\ApplicabilityReasoningEffort}}{{{audit['reasoning_effort']}}}\n"
            f"\\newcommand{{\\ApplicabilityMaxAttempts}}{{{audit['max_attempts_per_pair']}}}\n"
        ),
    }


def main() -> int:
    if sys.argv[1:] not in ([], ["--check"]):
        raise ValueError("Usage: prepare_applicability_protocol.py [--check]")
    outputs = render_outputs(audit_protocol())
    for path, content in outputs.items():
        if sys.argv[1:] == ["--check"]:
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Stale applicability artifact: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"Wrote {path.relative_to(PROJECT)}")
    print("PASS: exhaustive official pair coverage, protocol and artifact validation")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, ImportError) as error:
        print(f"Applicability verification failed: {error}", file=sys.stderr)
        sys.exit(1)
