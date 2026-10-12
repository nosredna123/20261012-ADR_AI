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

## Task 1.5: frozen retrieval baseline

[prepare_rag_protocol.py](scripts/prepare_rag_protocol.py) reuses the original
standard-library `load_cases`, `build_query`, and original-requirement loader.
It reads retrieval constants with Python's AST without importing the
model/Chroma dependencies. It validates the 12 frozen ranking rows, 35
criterion IDs and their story ownership, matching catalog field values,
unique known Top-15/Top-5 IDs, aligned names, and final Top-5 inclusion in
vector Top-15. It accepts the archived catalog's concatenated JSON records
without rewriting them.

Outputs:

- `outputs/rag-protocol-audit.json`: configuration, source/input SHA-256
  hashes, query hashes and ID mappings, placeholder-only query template, and
  counts of text values differing from the original requirements;
- `../latex-code/data/rag-values.tex`: vector/final candidate-count macros.

Inputs are the original `experiments/rag/` source, English requirement CSV,
catalog, dependency manifest, README, and frozen `outputs/rag_baseline.csv`,
plus the original requirement CSV/loader and results compiler as provenance.
The compiler is not executed; it provides the existing final-Top-5 membership
definition. `rag_baseline_reproduced.csv` is explicitly excluded: missing
official input fails rather than substituting reproduction output.

This script requires only Python 3.10+ and the standard library. No dependency
installation, network request, model download, embedding, reranking, or index
rebuild is performed. It neither writes into the original artifacts nor copies
requirement text into the audit. The hashes establish traceability, not semantic
translation equivalence. No empirical overlap counts or result tables are
generated in this methodology task.

From this directory:

```sh
python -B scripts/prepare_rag_protocol.py
python -B scripts/prepare_rag_protocol.py --check
python -B -m unittest discover -s tests -p 'test_*.py'
```

All input checks precede output generation. `--check` fails on absent/stale
outputs without writing. Tests cover preserved query formatting/identifiers,
invalid ranking lengths, duplicate/unknown IDs, misaligned names, incorrect
system/story mappings, Top-5 outside Top-15, configuration drift, and missing
frozen input. Altered fixtures exist only in temporary synthetic test files.

The manuscript measure is pooled final-Top-5 membership among LLM-positive
pairs, not precision/recall or a macro-average over stories. Zero-positive
stories have zero overlap count but no defined story-level proportion; if
there are no positive pairs at all, the pooled proportion is undefined.
Baseline ranks and their computational reproducibility are not verified by
these offline structural checks.

## Task 1.6: immutable ADR-generation protocol

[prepare_adr_protocol.py](scripts/prepare_adr_protocol.py) imports the original
standard-library validators and compiler functions without invoking their
generation, execution, or publication entry points. It:

- checks the preserved pre-ADR rows against the official applicable-pair
  compilation, and validates all 36 unique completed ADR pairs;
- validates model/response/call metadata, strict-output flags, nonempty ADR
  fields, fixed Proposed status, and source/rendered-prompt SHA-256 values;
- compares in-memory compilation with both frozen final CSVs without writing
  or regenerating them;
- validates attempt claims, the single recorded connection failure, and its
  linked, manually authorized retry; includes the approved pilot exactly once.

Outputs are `outputs/adr-protocol-audit.json` (exact prompt template and schema,
input field names, source/output hashes, response IDs, pair inventory, and
retry linkage) and `../latex-code/data/adr-values.tex` (count/configuration
macros). The audit does not copy requirement or generated ADR prose.
Original input paths and hashes are recorded. The historical source hash uses
`pattern_selection_results_before_adr.csv`, which retains the exact bytes used
at generation; the current source CSV has the added ADR column.

From this directory:

```sh
python -B scripts/prepare_adr_protocol.py
python -B scripts/prepare_adr_protocol.py --check
python -B -m unittest discover -s tests -p 'test_*.py'
```

Python 3.10+ and the standard library suffice. No SDK import, API call, model
download, original-artifact write, or generation is performed. `--check` is
read-only; all validation precedes writing manuscript outputs. Tests alter
only in-memory copies or explicitly synthetic temporary metadata and cover
provenance mismatch, extra/empty fields, non-Proposed status, call metadata,
unauthorized retry, duplicate JSON keys, and missing preserved input.

The exact prompt contains an explicitly synthetic one-shot example, not
expert evidence. Prompt compliance is not proven by structural output checks.
The failure does not establish dispatch or a completed additional response.
Protocol pilot approval and manual retry authorization are supported by the
research README and archived claims, not treated as expert architectural
approval.

The Nygard citation was checked against the original Cognitect article
“Documenting Architecture Decisions” (2011-11-15), including its title,
context, decision, status, and consequences description. The pipeline figure
is maintained as standalone LaTeX under `../latex-code/figures/`; its build
commands are in the manuscript README, not a data-processing script.
