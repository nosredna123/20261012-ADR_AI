# Manuscript data processing

## Task 1.2: requirement sample

[prepare_dataset_summary.py](scripts/prepare_dataset_summary.py) reuses the
original `load_requirement_cases` validator without modifying the initial
artifacts. It additionally checks generic system/story mappings and criterion
ownership, aggregates counts by system, and writes:

- `../latex-code/data/study-values.tex`: the four sample-count macros;
- `../latex-code/tables/dataset-summary.tex`: an anonymized count table;
- `outputs/dataset-summary-audit.json`: totals and input/validator SHA-256 values.

Inputs are the original requirement CSV and validator under
`../docs/20261012.0933-InitialArtifacts/adr4ai_app/`. No translated requirement
copy, pilot output, expert response, or model API is used. These scripts require
Python 3.10 or later and only the standard library; no dependency installation
is needed. Generated output contains generic IDs and aggregate counts, not
requirement text. Original inputs are read-only.

From this directory:

```sh
python -B scripts/prepare_dataset_summary.py
python -B scripts/prepare_dataset_summary.py --check
python -B -m unittest discover -s tests -p 'test_dataset_summary.py'
```

Generation replaces only the three outputs listed above after all input checks
pass. `--check` does not write files and fails on absent or stale outputs.
The output is deterministic for unchanged inputs and validator.

The expected 4 systems, 12 stories, 3 stories per system, and 35 criteria describe
this bounded sample; they are validation constraints, not population estimates.

## Task 1.3: pattern catalog

[prepare_catalog_summary.py](scripts/prepare_catalog_summary.py) reuses the
original catalog loader, checks filenames/IDs 001--070 and the five string-valued
model-input fields, and preserves explicitly empty fields. It writes:

- `../latex-code/data/catalog-values.tex`: catalog-count macros;
- `outputs/catalog-summary-audit.json`: input field definitions, empty-field
  IDs, resource IDs, and SHA-256/Git-blob hashes for all 70 records.

Inputs are read-only records under
`../docs/20261012.0933-InitialArtifacts/adr4ai_app/catalogs/patterns/` and the
original validator. No model calls or input normalization are performed.
Generation and freshness checks are offline and use only the standard library.

From this directory:

```sh
python -B scripts/prepare_catalog_summary.py
python -B scripts/prepare_catalog_summary.py --check
python -B -m unittest discover -s tests -p 'test_*summary.py'
```

The optional command below makes one read-only HTTPS request for the public
GitHub Git tree at the pinned revision. It transmits no local dataset or hashes:
comparison is local. It writes `outputs/catalog-upstream-verification.json`
and fails explicitly on missing/mismatched records or an incomplete response.
This provenance report is separate from normal offline regeneration.

```sh
python -B scripts/prepare_catalog_summary.py --verify-upstream
```

On 2026-10-12, all 70 local records matched the public Git blob hashes at revision
`9ff3e611583b7d0f71032c62f9a9812ce93e2fd0` (2023-05-12). The comparison proves
exact-byte identity with that source snapshot, not pattern effectiveness.

### Citation verification

- Heiland, Hauser, and Bogner's publication metadata (title, full author names,
  CAIN 2023 venue, IEEE publisher, pages 184--196, and DOI) were checked against
  [the Crossref DOI record](https://api.crossref.org/works/10.1109/CAIN58948.2023.00035).
  The collected CAIN 2026 paper also identifies that publication and repository.
- The repository title and literature-study origin were checked in its public
  README; the cited URL fixes the verified revision:
  [SWE4AI/ai-patterns](https://github.com/SWE4AI/ai-patterns/tree/9ff3e611583b7d0f71032c62f9a9812ce93e2fd0).
- Local numeric resource IDs are retained in the audit, not converted into
  guessed citations. No claim is made that every individual pattern's original
  source or maturity has been independently evaluated.

## Task 1.4: exhaustive applicability protocol

[prepare_applicability_protocol.py](scripts/prepare_applicability_protocol.py)
loads the original input, assessment, and runner modules without executing
their entry points. It uses their validators to check all 12 x 70 official
pairs, response fields, model metadata, references, uniqueness, JSONL
termination, and failure state. It makes **no API or network calls**, requires
no API key or OpenAI SDK installation, and writes:

- `outputs/applicability-protocol-audit.json`: input/source/catalog SHA-256
  hashes, official coverage by story, configuration, exact instructions and
  schema, a placeholder-only input template, and explicit pilot exclusions;
- `../latex-code/data/applicability-values.tex`: assessment-count and model/
  reasoning/attempt-budget macros.

Inputs are the original pattern-selection scripts, requirement CSV, catalog,
and **top-level** `outputs/assessments.jsonl` and `outputs/failures.jsonl`.
No pilot/test record contributes to coverage; no classified distribution or
later-task result table is generated here. Requirement text and model
rationales are not copied into the audit. The full prompt is the original
`INSTRUCTIONS` string plus `build_prompt` input template; the authoritative
source files and their hashes are recorded. Inspect the originals for the
execution/SDK-retry mechanics; the audit does not infer those from outcome
counts. Modules' temporary sibling-import registrations are restored afterward.

From this directory:

```sh
python -B scripts/prepare_applicability_protocol.py
python -B scripts/prepare_applicability_protocol.py --check
python -B -m unittest discover -s tests -p 'test_*.py'
```

Generation validates all inputs before writing either output. `--check` is
read-only and fails on absent/stale artifacts. Frozen inputs remain untouched.
Tests use temporary, explicitly synthetic altered logs and a mock API client;
they do not execute the experiment or contact a model.

The final empty failure log contains no unresolved state. It is **not** a
complete attempt history: successful records omit attempt counts and successful
requests remove their failure entries. The audit therefore records total API
attempts as unknown (`null`), rather than assuming 840 issued requests or no
retries. Per-pair requests contain no previous assessment history, but outcomes
are not statistically independent because they share requirements and a model.

No separate workflow figure is added in Task 1.4: prose suffices for the
single-pair sequential workflow without introducing a figure dependency.
