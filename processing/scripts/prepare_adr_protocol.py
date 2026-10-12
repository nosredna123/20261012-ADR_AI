"""Audit immutable ADRs and execution metadata offline; never generate or publish ADRs."""

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

PROJECT = Path(__file__).resolve().parents[2]
SOURCE = PROJECT / "docs/20261012.0933-InitialArtifacts/adr4ai_app"
EXPERIMENT = SOURCE / "experiments/adr_generation"
BACKUP = SOURCE / "research_results/pattern_selection_results_before_adr.csv"
OUTPUTS = EXPERIMENT / "outputs"
AUDIT = PROJECT / "processing/outputs/adr-protocol-audit.json"
MACROS = PROJECT / "latex-code/data/adr-values.tex"


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load ADR validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_protocol() -> tuple[ModuleType, ModuleType]:
    previous = sys.modules.get("generate_adr")
    try:
        generator = load_module(EXPERIMENT / "generate_adr.py", "generate_adr")
        sys.modules["generate_adr"] = generator
        runner = load_module(EXPERIMENT / "run_experiment.py", "original_adr_runner")
        return generator, runner
    finally:
        if previous is None:
            sys.modules.pop("generate_adr", None)
        else:
            sys.modules["generate_adr"] = previous


def validate_history(runner: ModuleType, expected: set) -> dict:
    claims = {}
    failures = []
    for path in sorted((OUTPUTS / "attempts").glob("*.json")):
        record = runner.read_json(path)
        pair = runner.pair_of(record)
        if pair not in expected or record.get("automatic_retry") is not False:
            raise ValueError(f"Unexpected attempt pair or automatic retry: {path.name}")
        if path.name.endswith(".failure.json"):
            if (record.get("state") != "failed"
                    or not isinstance(record.get("error"), str)
                    or not record["error"].strip()):
                raise ValueError(f"Invalid failure record: {path.name}")
            failures.append((path, record))
        else:
            if record.get("state") != "started":
                raise ValueError(f"Invalid attempt reservation: {path.name}")
            claims[path.name] = record
    retry_pair = ("SYS04-US03", "003")
    failure_name = "SYS04-US03_P003.failure.json"
    retry_name = "SYS04-US03_P003.retry-2.json"
    original_name = "SYS04-US03_P003.json"
    expected_claims = {
        runner.filename(pair) for pair in expected if pair != runner.PILOT_PAIR
    } | {retry_name}
    if set(claims) != expected_claims or len(failures) != 1:
        raise ValueError("ADR attempt history differs from the recorded single retry")
    path, failure = failures[0]
    if (path.name != failure_name or runner.pair_of(failure) != retry_pair
            or failure["error"] != "Connection error."):
        raise ValueError("Expected the recorded SYS04-US03/003 connection failure")
    retry = claims[retry_name]
    if (runner.pair_of(retry) != retry_pair
            or retry.get("manual_retry_authorized") is not True
            or retry.get("prior_attempt") != original_name):
        raise ValueError("Retry is not explicitly authorized or linked to its prior attempt")
    for name, claim in claims.items():
        if name != retry_name and claim.get("manual_retry_authorized", False) is not False:
            raise ValueError(f"Unexpected manual retry authorization: {name}")
    return {
        "claim_count": len(claims),
        "failure_count": len(failures),
        "manual_retry_pair": list(retry_pair),
        "original_claim": original_name,
        "failure_record": failure_name,
        "authorized_retry_claim": retry_name,
        "failed_request_dispatch_unknown": True,
    }


def audit_protocol() -> dict:
    generator, runner = load_protocol()
    compiler = load_module(SOURCE / "research_results/compile_adr_results.py",
                           "original_adr_compiler")
    selection = load_module(SOURCE / "research_results/compile_results.py",
                            "original_selection_compiler")
    original_bytes = BACKUP.read_bytes()
    columns, rows = compiler.csv_rows(original_bytes)
    if columns != compiler.ORIGINAL:
        raise ValueError("Preserved pre-ADR input schema differs")
    original_results, _, _ = selection.compile_results()
    if rows != original_results:
        raise ValueError("ADR source differs from official applicable-pair compilation")
    result, enriched = compiler.compile_data(original_bytes)
    if (result != (SOURCE / "research_results/adr_generation_results.csv").read_bytes()
            or enriched != generator.SOURCE.read_bytes()):
        raise ValueError("Frozen compiled ADR datasets differ from validated artifacts")
    if (generator.MODEL, generator.REASONING_EFFORT) != ("gpt-6-sol", "high"):
        raise ValueError("ADR configuration differs from the manuscript")
    source_hash = hashlib.sha256(original_bytes).hexdigest()
    prompts = {runner.pair_of(row): runner.prompt_for(row) for row in rows}
    records = []
    seen = set()
    for path in sorted(OUTPUTS.glob("*.json")):
        artifact = runner.read_json(path)
        pair = runner.validate_completed(artifact, prompts, source_hash)
        if pair in seen:
            raise ValueError(f"Duplicate completed ADR pair: {pair}")
        seen.add(pair)
        records.append({
            "file": path.name, "pair": list(pair),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "prompt_sha256": artifact["prompt_sha256"],
            "response_id": artifact["response_id"],
            "api_calls": artifact["api_calls"], "status": artifact["adr"]["status"],
        })
    if len(seen) != 36 or seen != set(prompts):
        raise ValueError("Expected exactly 36 unique completed applicable ADR pairs")
    history = validate_history(runner, seen)
    paths = [
        EXPERIMENT / "generate_adr.py", EXPERIMENT / "run_experiment.py",
        SOURCE / "research_results/compile_adr_results.py",
        SOURCE / "research_results/compile_results.py",
        SOURCE / "research_results/README.md", BACKUP, generator.SOURCE,
        SOURCE / "research_results/adr_generation_results.csv",
    ]
    paths.extend(sorted((OUTPUTS / "attempts").glob("*.json")))
    return {
        "task": "1.6", "adr_count": len(seen),
        "model": generator.MODEL, "reasoning_effort": generator.REASONING_EFFORT,
        "source_sha256_used_at_generation": source_hash,
        "source_hash_note": (
            "Artifacts refer to the original pre-ADR bytes now preserved in the "
            "backup; current pattern_selection_results.csv has an added ADR column."
        ),
        "input_fields": list(generator.INPUT_FIELDS), "schema": generator.SCHEMA,
        "prompt_template": generator.PROMPT_TEMPLATE,
        "prompt_template_sha256": hashlib.sha256(
            generator.PROMPT_TEMPLATE.encode("utf-8")
        ).hexdigest(),
        "pilot_pair": list(runner.PILOT_PAIR),
        "pilot_included_in_final_count": True,
        "history": history, "records": records,
        "inputs": [{"path": path.relative_to(PROJECT).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                   for path in paths],
        "validation_scope": (
            "Pair coverage, exact compiler outputs, structural validation, source/"
            "prompt hashes and execution metadata; not architectural adequacy."
        ),
    }


def render_outputs(audit: dict) -> dict[Path, str]:
    return {
        AUDIT: json.dumps(audit, indent=2, sort_keys=True) + "\n",
        MACROS: (
            "% !TeX root = ../main.tex\n"
            "% Generated by processing/scripts/prepare_adr_protocol.py.\n"
            "% StudyAdrCount is owned by data/study-values.tex.\n"
            f"\\newcommand{{\\AdrModel}}{{{audit['model']}}}\n"
            f"\\newcommand{{\\AdrReasoningEffort}}{{{audit['reasoning_effort']}}}\n"
        ),
    }


def main() -> int:
    if sys.argv[1:] not in ([], ["--check"]):
        raise ValueError("Usage: prepare_adr_protocol.py [--check]")
    outputs = render_outputs(audit_protocol())
    for path, content in outputs.items():
        if sys.argv[1:] == ["--check"]:
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Stale ADR protocol artifact: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"Wrote {path.relative_to(PROJECT)}")
    print("PASS: ADR pair coverage, frozen outputs, hashes and authorized retry")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, ImportError, KeyError) as error:
        print(f"ADR verification failed: {error}", file=sys.stderr)
        sys.exit(1)
