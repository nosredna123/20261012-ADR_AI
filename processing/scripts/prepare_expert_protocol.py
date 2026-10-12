"""Verify frozen evaluator preparation offline; no form creation or response analysis."""

import ast
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

PROJECT = Path(__file__).resolve().parents[2]
RESULTS = PROJECT / "docs/20261012.0933-InitialArtifacts/adr4ai_app/research_results"
FORM = RESULTS / "google_forms/create_expert_evaluation_form.gs"
AUDIT = PROJECT / "processing/outputs/expert-preparation-audit.json"
MACROS = PROJECT / "latex-code/data/expert-preparation-values.tex"
SYSTEM_COUNTS = {"SYS01": 7, "SYS02": 12, "SYS03": 8, "SYS04": 9}
CONSTRUCTS = (
    "Decision adequacy for the stated requirements",
    "Decision grounding and comprehensibility of its rationale",
    "Presentation of relevant consequences, benefits and trade-offs",
    "Perceived usefulness as a decision record in the evaluator's system",
    "Pattern applicability to the stated requirements",
)


def load_compiler():
    path = RESULTS / "compile_expert_evaluation.py"
    spec = importlib.util.spec_from_file_location("original_expert_compiler", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load evaluator-preparation validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def question_wording(text: str) -> list[str]:
    match = re.search(r"const EVALUATION_QUESTIONS = (\[.*?\]);", text, re.DOTALL)
    if match is None:
        raise ValueError("Questionnaire question array not found")
    questions = ast.literal_eval(match.group(1))
    if (not isinstance(questions, list) or len(questions) != 5
            or any(not isinstance(question, str) or not question.strip()
                   for question in questions)):
        raise ValueError("Expected exactly five nonempty questionnaire statements")
    return questions


def validate_form(cases: list[dict], text: str) -> dict:
    marker = "const EVALUATION_CASES = "
    if text.count(marker) != 1:
        raise ValueError("Expected one embedded case declaration")
    embedded, _ = json.JSONDecoder().raw_decode(text.split(marker, 1)[1])
    if embedded != cases:
        raise ValueError("Embedded questionnaire cases differ from frozen presentation CSV")
    counts = dict(sorted(Counter(case["system_id"] for case in cases).items()))
    if counts != SYSTEM_COUNTS:
        raise ValueError("Questionnaire system counts differ from protocol")
    expected_contract = (
        "const ALLOW_FORM_CREATION = false;",
        "form.setCollectEmail(false);",
        "form.setLimitOneResponsePerUser(false);",
        "form.setShuffleQuestions(false);",
        "form.setPublishingSummary(false);",
        "selection.createChoice(system, sections[system])",
        "systems.slice(1).forEach(function (system)",
        "sections[system].setGoToPage(finalSection);",
        "finalSection.setGoToPage(FormApp.PageNavigationType.CONTINUE);",
        ".setBounds(1, 5).setLabels('Discordo totalmente', 'Concordo totalmente').setRequired(true);",
        ".setTitle(prefix + 'COMMENT] ' + COMMENT_QUESTION).setRequired(false);",
        "if (entry[pair[1]] !== '')",
    )
    for fragment in expected_contract:
        if fragment not in text:
            raise ValueError(f"Questionnaire source contract changed: {fragment}")
    start = text.index("function createEvaluatorProfile(form)")
    end = text.index("function createSystemSelection(form)", start)
    profile_text = text[start:end]
    titles = re.findall(r"\.setTitle\('([^']+)'\)", profile_text)
    if len(titles) != 4 or titles[0] != "Perfil do Avaliador":
        raise ValueError("Expected a profile heading and three profile questions")
    questions = question_wording(text)
    return {
        "cases_per_system": counts,
        "required_ratings_per_system": {key: count * 5 for key, count in counts.items()},
        "optional_comments_per_system": counts,
        "profile_questions_pt": titles[1:],
        "evaluation_questions": [
            {"id": f"Q{index}", "wording_pt": question, "construct_en": construct}
            for index, (question, construct) in
            enumerate(zip(questions, CONSTRUCTS), start=1)
        ],
        "required_rating_count_across_all_routes": len(cases) * 5,
        "form_creation_enabled_in_archive": False,
        "verification_scope": (
            "Embedded-value equality and static source contracts only; not Google "
            "execution, route simulation, deployment, permissions or respondent access."
        ),
    }


def audit_preparation() -> dict:
    compiler = load_compiler()
    rows = compiler.validate_source(RESULTS / "adr_generation_results.csv")
    labels = compiler.load_inventory(rows)
    columns, mappings = compiler.read_csv(RESULTS / "expert_evaluation_translations_pt.csv")
    if tuple(columns) != compiler.MAPPING_COLUMNS:
        raise ValueError("Translation mapping column order differs")
    provenance = compiler.load_review_provenance(rows, mappings, labels)
    cases_bytes, audit_bytes = compiler.compile_data(rows, mappings, labels, provenance)
    if (cases_bytes != (RESULTS / "expert_evaluation_cases_pt.csv").read_bytes()
            or audit_bytes != (RESULTS / "expert_evaluation_translation_audit.csv").read_bytes()):
        raise ValueError("Frozen presentation or translation audit differs from validated compilation")
    _, cases = compiler.read_csv(RESULTS / "expert_evaluation_cases_pt.csv")
    text = FORM.read_text(encoding="utf-8")
    form = validate_form(cases, text)
    paths = [
        RESULTS / name for name in (
            "compile_expert_evaluation.py", "translate_expert_evaluation.py",
            "adr_generation_results.csv", "expert_evaluation_language_classification.csv",
            "expert_evaluation_translations_pt.csv", "expert_evaluation_manual_corrections.csv",
            "expert_evaluation_cases_pt.csv", "expert_evaluation_translation_audit.csv",
            "expert_evaluation_preparation_report.md",
            "expert_evaluation_translation_run/translations_candidate.csv",
            "expert_evaluation_translation_run/manual_authorization.txt",
            "google_forms/README.md",
        )
    ] + [FORM]
    return {
        "task": "1.7", "case_count": len(cases), "mapping_count": len(mappings),
        "language_categories": dict(sorted(Counter(labels.values()).items())),
        "manual_correction_count": sum(
            item["manual_correction_authorized"] == "yes" for item in provenance.values()),
        "requirements_preserved": True, "questionnaire": form,
        "inputs": [{"path": path.relative_to(PROJECT).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                   for path in paths],
        "pending_procedures": [
            "Deployment and exact administered instrument version",
            "Evaluator eligibility and recruitment",
            "Consent and ethics approval/exemption",
            "Administration dates and instructions",
            "Account-level access, privacy, storage/access/retention arrangements",
            "Post-collection procedural confirmation and consolidated responses",
        ],
        "results_inspected": False,
    }


def render_outputs(audit: dict) -> dict[Path, str]:
    return {
        AUDIT: json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        MACROS: (
            "% !TeX root = ../main.tex\n"
            "% Generated by processing/scripts/prepare_expert_protocol.py.\n"
            f"\\newcommand{{\\ExpertPreparedCaseCount}}{{{audit['case_count']}}}\n"
            f"\\newcommand{{\\ExpertMappingCount}}{{{audit['mapping_count']}}}\n"
            f"\\newcommand{{\\ExpertCorrectionCount}}{{{audit['manual_correction_count']}}}\n"
        ),
    }


def main() -> int:
    if sys.argv[1:] not in ([], ["--check"]):
        raise ValueError("Usage: prepare_expert_protocol.py [--check]")
    outputs = render_outputs(audit_preparation())
    for path, content in outputs.items():
        if sys.argv[1:] == ["--check"]:
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Stale expert-preparation artifact: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"Wrote {path.relative_to(PROJECT)}")
    print("PASS: frozen translation provenance and questionnaire source verification")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, ImportError) as error:
        print(f"Expert-preparation verification failed: {error}", file=sys.stderr)
        sys.exit(1)
