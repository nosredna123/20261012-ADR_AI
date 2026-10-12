"""Verify frozen RAG inputs and rankings offline, without loading retrieval models."""

import ast
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

PROJECT = Path(__file__).resolve().parents[2]
SOURCE = PROJECT / "docs/20261012.0933-InitialArtifacts/adr4ai_app"
RAG = SOURCE / "experiments/rag"
BASELINE = RAG / "outputs/rag_baseline.csv"
QUERY_SOURCE = RAG / "data/user_histories_EN.csv"
CATALOG = RAG / "catalogs/all-patterns.json"
RETRIEVAL = RAG / "src/retrieval.py"
AUDIT = PROJECT / "processing/outputs/rag-protocol-audit.json"
MACROS = PROJECT / "latex-code/data/rag-values.tex"


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load original validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def configuration() -> dict:
    names = {"EMBEDDING_MODEL", "RERANKER_MODEL", "VECTOR_CANDIDATES", "FINAL_CANDIDATES"}
    values = {}
    tree = ast.parse(RETRIEVAL.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    if target.id in values:
                        raise ValueError(f"Duplicate retrieval constant: {target.id}")
                    values[target.id] = ast.literal_eval(node.value)
    if values != {
        "EMBEDDING_MODEL": "BAAI/bge-small-en-v1.5",
        "RERANKER_MODEL": "BAAI/bge-reranker-base",
        "VECTOR_CANDIDATES": 15, "FINAL_CANDIDATES": 5,
    }:
        raise ValueError("Retrieval configuration differs from the manuscript")
    return values


def read_catalog() -> dict:
    text = CATALOG.read_text(encoding="utf-8")
    decoder = json.JSONDecoder()
    if text.lstrip().startswith("["):
        records = json.loads(text)
    else:
        records = []
        position = 0
        while position < len(text):
            if text[position].isspace():
                position += 1
                continue
            record, position = decoder.raw_decode(text, position)
            records.append(record)
    if not isinstance(records, list) or len(records) != 70:
        raise ValueError("RAG catalog must contain exactly 70 records")
    by_id = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            raise ValueError("Invalid RAG catalog record")
        pid = record["id"]
        if pid in by_id or pid not in {f"{number:03d}" for number in range(1, 71)}:
            raise ValueError(f"Duplicate or unknown RAG catalog ID: {pid}")
        original = json.loads((SOURCE / "catalogs/patterns" / f"P{pid}.json")
                              .read_text(encoding="utf-8"))
        if record != original:
            raise ValueError(f"RAG/source catalog fields differ: {pid}")
        by_id[pid] = record
    return by_id


def validate_rankings(cases: dict, patterns: dict, columns: list[str]) -> list[dict]:
    with BASELINE.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != columns:
            raise ValueError("Frozen baseline columns differ from the recorded schema")
        rows = list(reader)
    seen = set()
    for row in rows:
        if None in row or any(not isinstance(row[field], str) for field in columns):
            raise ValueError("Malformed frozen baseline row")
        uid = row["user_story_id"]
        if uid not in cases or uid in seen:
            raise ValueError(f"Unknown or duplicate baseline story: {uid}")
        seen.add(uid)
        if row["system"] != cases[uid][0]["system"]:
            raise ValueError(f"Baseline system/story mismatch: {uid}")
        rankings = {}
        for prefix, size in (("top15", 15), ("top5", 5)):
            ids = row[prefix + "_ids"].split(";")
            if len(ids) != size or len(set(ids)) != size or any(
                pid not in patterns for pid in ids
            ):
                raise ValueError(f"Invalid {prefix} IDs: {uid}")
            names = row[prefix + "_names"].split(";")
            if names != [patterns[pid]["name"] for pid in ids]:
                raise ValueError(f"Misaligned {prefix} names: {uid}")
            rankings[prefix] = ids
        if not set(rankings["top5"]).issubset(rankings["top15"]):
            raise ValueError(f"Final Top-5 is not a subset of vector Top-15: {uid}")
    if seen != set(cases):
        raise ValueError("Frozen baseline must cover all 12 stories")
    return rows


def audit_protocol() -> dict:
    config = configuration()
    runner = load_module(RAG / "src/run_baseline.py", "original_rag_runner")
    loader = load_module(SOURCE / "experiments/pattern_selection/prepare_data.py",
                         "original_rag_requirement_validator")
    cases = runner.load_cases(QUERY_SOURCE)
    originals = {case["user_story_id"]: case for case in
                 loader.load_requirement_cases(SOURCE / "data/user_histories_orig.csv")}
    if set(cases) != set(originals):
        raise ValueError("RAG and original requirement story IDs differ")
    queries = {}
    differing_text = {"system_purpose": 0, "user_story": 0, "acceptance_criterion": 0}
    for uid, rows in cases.items():
        original = originals[uid]
        original_ids = [criterion["acceptance_criterion_id"]
                        for criterion in original["acceptance_criteria"]]
        if ([row["acceptance_criterion_id"] for row in rows] != original_ids
                or rows[0]["system"] != original["system"]):
            raise ValueError(f"RAG requirement identifiers/ownership differ: {uid}")
        for field in ("system_purpose", "user_story"):
            differing_text[field] += rows[0][field] != original[field]
        differing_text["acceptance_criterion"] += sum(
            row["acceptance_criterion"] != criterion["acceptance_criterion"]
            for row, criterion in zip(rows, original["acceptance_criteria"])
        )
        query = runner.build_query(rows)
        if any(f"[{identifier}]" not in query for identifier in [uid, *original_ids]):
            raise ValueError(f"Query omits requirement identifiers: {uid}")
        queries[uid] = {
            "criterion_ids": original_ids,
            "query_sha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
        }
    patterns = read_catalog()
    rankings = validate_rankings(cases, patterns, runner.COLUMNS)
    paths = [
        RAG / "src/run_baseline.py", RETRIEVAL, RAG / "src/pattern_catalog.py",
        RAG / "README.md", RAG / "requirements.txt", QUERY_SOURCE, CATALOG, BASELINE,
        SOURCE / "data/user_histories_orig.csv",
        SOURCE / "experiments/pattern_selection/prepare_data.py",
        SOURCE / "research_results/compile_results.py",
    ]
    return {
        "task": "1.5",
        "inputs": [{"path": path.relative_to(PROJECT).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                   for path in paths],
        "configuration": config,
        "story_count": len(cases), "pattern_count": len(patterns),
        "criterion_count": sum(len(rows) for rows in cases.values()),
        "validated_frozen_ranking_rows": len(rankings),
        "same_catalog_field_values": True,
        "text_values_differing_from_original": differing_text,
        "queries": queries,
        "query_template": runner.build_query([{
            "system_purpose": "<system_purpose>", "user_story_id": "<user_story_id>",
            "user_story": "<user_story>", "acceptance_criterion_id": "<criterion_id>",
            "acceptance_criterion": "<criterion_text>",
        }]),
        "excluded_reproduction_output": (
            RAG / "outputs/rag_baseline_reproduced.csv"
        ).relative_to(PROJECT).as_posix(),
        "validation_scope": (
            "Frozen-input and ranking structure, not model/index execution or "
            "translation equivalence. No overlap results calculated in Task 1.5."
        ),
    }


def render_outputs(audit: dict) -> dict[Path, str]:
    config = audit["configuration"]
    return {
        AUDIT: json.dumps(audit, indent=2, sort_keys=True) + "\n",
        MACROS: (
            "% !TeX root = ../main.tex\n"
            "% Generated by processing/scripts/prepare_rag_protocol.py.\n"
            f"\\newcommand{{\\RagVectorCount}}{{{config['VECTOR_CANDIDATES']}}}\n"
            f"\\newcommand{{\\RagFinalCount}}{{{config['FINAL_CANDIDATES']}}}\n"
        ),
    }


def main() -> int:
    if sys.argv[1:] not in ([], ["--check"]):
        raise ValueError("Usage: prepare_rag_protocol.py [--check]")
    outputs = render_outputs(audit_protocol())
    for path, content in outputs.items():
        if sys.argv[1:] == ["--check"]:
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Stale RAG protocol artifact: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"Wrote {path.relative_to(PROJECT)}")
    print("PASS: frozen RAG query, catalog, configuration and ranking validation")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, ImportError) as error:
        print(f"RAG verification failed: {error}", file=sys.stderr)
        sys.exit(1)
