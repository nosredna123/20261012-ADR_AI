# Manuscript data processing

## Task 1.2: requirement sample

[prepare_dataset_summary.py](scripts/prepare_dataset_summary.py) reuses the
original `load_requirement_cases` validator without modifying the initial
artifacts. It additionally checks generic system/story mappings and criterion
ownership, aggregates counts by system, and writes:

- `../latex-code/tables/dataset-summary.tex`: an anonymized count table;
- `outputs/dataset-summary-audit.json`: totals and input/validator SHA-256 values.

Since Task 2.1, core count macros are owned exclusively by
[prepare_study_values.py](scripts/prepare_study_values.py), documented below.
The sample audit/table generator no longer overwrites that central file.

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

Generation replaces only the two outputs listed above after all input checks
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
The pattern-count macro moved to the central study-value generator in Task 2.1;
the catalog macro file retains only its field-inventory count.

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

## Task 1.7: translation and questionnaire preparation

[prepare_expert_protocol.py](scripts/prepare_expert_protocol.py) reuses the
original preparation compiler's validation and in-memory compilation functions,
without calling its publication entry point. It checks 324 mappings for the
36 source pairs, original requirement preservation, language categories,
preserved Portuguese spans, candidate/final provenance, and the five authorized
corrections. Both frozen presentation/audit CSVs must equal the in-memory
outputs byte-for-byte. No original file is overwritten.

It decodes the form script's JSON-embedded cases and checks exact equality with
the presentation CSV, extracts the five Portuguese evaluation statements and
three profile questions, and checks explicit static source contracts for
route exits, scale anchors, comments, omission of empty fields, creation guard,
and intended privacy settings. Static checks are **not** a new route simulation
or a Google execution test. The archived README's local simulation is reported
as implementation validation only, not deployment or empirical evidence.

Outputs:

- `outputs/expert-preparation-audit.json`: source hashes, verified category/
  correction/case counts, per-route item counts, exact Portuguese wording,
  English construct descriptions, validation limits, and pending procedures;
- `../latex-code/data/expert-preparation-values.tex`: preparation count macros.

Inputs are the original ADR results, translation inventory/mappings/candidates,
authorized-correction records, final evaluator CSV/audit, compiler/translation
scripts, preparation report, and form script/README. No expert responses,
Google account, form URL, API call, or translation generation is used.
The script requires Python 3.10+ and the standard library only. Portuguese
Unicode is retained in the audit to preserve exact source wording.

From this directory:

```sh
python -B scripts/prepare_expert_protocol.py
python -B scripts/prepare_expert_protocol.py --check
python -B -m unittest discover -s tests -p 'test_*.py'
```

Validation precedes generation; `--check` is read-only and rejects absent/stale
outputs. Tests cover deterministic outputs, form-value/settings drift, missing
questions, unapproved translation changes, changed requirements, and missing
form source; mutations remain in-memory, not empirical files.

On 2026-10-12, the researcher authorized explicit pending-protocol placeholders
for unconfirmed deployment, eligibility/recruitment, consent/ethics,
administration, and actual access/privacy arrangements. No such procedure is
asserted as completed. Profile questions are not eligibility rules; disabling
email collection does not prove anonymous live access. Response analysis
choices belong to Task 1.8 and are not implemented here.

## Task 1.8: pre-inspection analysis protocol

[expert-analysis.json](protocols/expert-analysis.json) is the versioned,
response-independent RQ3 analysis specification. On 2026-10-12 the researcher
approved exploratory descriptive analysis with no pass/fail cutoff; no numeric
expertise threshold; documented eligibility/consent/familiarity confirmation;
available-item primary analysis and complete-route sensitivity; conditional
within-system ordinal alpha; and independent dual coding/reconciliation.
Eligibility confirmations and actual administration remain unverified, not
invented. Collection may already have started; no pre-collection preregistration
claim is made. Record amendments and exposure to results rather than replacing
the decision history silently.

The protocol defines route-dependent opportunities and missingness, submission
versus evaluator identities, inverse-CDF median/interquartile category interval,
equal-case/equal-story/equal-system aggregation, alpha coincidence/distance
formula and gate, qualitative coding, and source/computation/display contracts
for eight planned outputs. No means, composites, success thresholds, imputation,
cross-system alpha, inferential tests, or population claims are planned.
Privacy review is required before publication; respondent-level summaries remain
restricted. No analytic eligibility confirmation is inferred from rating scores.

[prepare_expert_analysis_plan.py](scripts/prepare_expert_analysis_plan.py)
reads **only** that protocol and the Task 1.7 instrument audit. It validates
item alignment and approved scope, safe unique output paths, and complete
source/computation contracts. It writes:

- `../latex-code/tables/expert-analysis-outputs.tex`: planned-output inventory;
- `outputs/expert-analysis-plan-audit.json`: protocol/instrument-audit hashes,
  review status and explicit no-response-data validation scope.

From this directory:

```sh
python -B scripts/prepare_expert_analysis_plan.py
python -B scripts/prepare_expert_analysis_plan.py --check
python -B -m unittest discover -s tests -p 'test_*.py'
```

Python 3.10+ and the standard library suffice. Validation precedes writes;
`--check` rejects stale/absent outputs without writing. Tests check protocol
scope, inventory completeness/path safety, questionnaire alignment, escaping
and rejection of false preregistration, thresholds, or imputation.
They do **not** test the future statistics, response cleaning, or coding.
Their implementation and numerical tests belong to Phase 3, after raw export,
restricted provenance, consent/governance and instrument version are confirmed.
No actual or synthetic respondent-result dataset is opened or created here.

## Task 1.9: governance and Artifact Availability inputs

On 2026-10-12 the researcher authorized explicit pending confirmations and
restricted-by-default procedures where governance evidence is absent.
This records a handling policy for subsequent work, **not** organizational
permission, completed ethics review, participant consent, or evidence that
technical storage controls have already been implemented.
The researcher subsequently approved the Task 1.9 manuscript and proposed
procedures; this approval does not resolve the external governance gates below.

### Evidence and unresolved gates

- The supplied industrial scope PDF defines intended academic use, a bounded
  requirement sample and generic system names. It does not prove authority to
  process the sample externally or redistribute it. The original document
  identifies the source organization and must not enter an anonymous package.
- Existing computational audits document model identifiers/configuration,
  prompt and source hashes, response metadata and deterministic compiler
  checks. They do not establish provider retention/training policy or
  contractual permission. Do not issue new external generation requests
  before permission and account conditions are confirmed.
- The prepared questionnaire source and analysis protocol do not establish
  deployment, actual access policy, consent, ethics approval/exemption,
  voluntariness or unique evaluator identity. Resolve these before Phase 3.
  If collection has already occurred, record the actual timing and applicable
  determination; never recast retrospective confirmation as prior approval.
- Confirm authorized custodians, access controls, storage/processing location,
  platform/account terms, retention period, deletion responsibility and
  withdrawal limits. Record evidence in approved restricted administration
  storage, not in this public-facing documentation.

### Planned restricted-data lifecycle

1. Use approved restricted storage outside the manuscript/public repository
   for original response exports, administrative evidence and linking keys.
   Do not choose a repository subdirectory as a substitute for access control.
2. Preserve the original export read-only and record checksum, export time,
   instrument version and authorized provenance. Read-only preservation
   applies during the authorized retention period, not indefinite retention
   overriding withdrawal/deletion obligations.
3. Create a separately versioned analysis copy with generic submission IDs.
   Keep identity keys separately restricted. Pseudonymization is not irreversible
   anonymization; do not infer distinct people from identical profiles or
   rating vectors.
4. Keep disposition/cleaning logs, raw-to-derived mapping, protocol amendments,
   initial coding logs, reconciliation and analytic versions restricted.
   Never replace raw values with cleaned values or silently overwrite
   earlier decisions. Freeze each analysis input and retain its checksum.
5. Generate manuscript outputs only after eligibility/instrument/governance
   gates are satisfied. Review profiles, small cells, cross-table linkage,
   quotations and free text for deductive disclosure. Use consistent
   suppression/aggregation rules and report their impact without selecting
   favorable observations. Quotations require explicit authorization.
6. Approve each release separately; log version, authorization, restrictions,
   disclosure review and license. Execute retention/deletion under confirmed
   arrangements, including derived copies and backups where applicable.

No respondent data is ingested, moved, transformed or published in Task 1.9.
No new processing script is required: this task specifies procedures, not
statistics or a new derivation. Existing offline auditors remain the source
of computational lineage evidence.

### Release matrix for Phase 10

The entries below are **release candidates**, not declarations of open access.
The source collection and current Git history are not an anonymous package.

| Material | Default treatment | Conditions before release |
|---|---|---|
| Manuscript, processing code/tests, analysis protocol | Candidate for curated release | Review identities, local paths, fixtures, comments, dependencies and licensing; do not assume current files/history are anonymous. |
| Public pattern catalog | Public upstream provenance; local redistribution unconfirmed | Verify license/reuse rights and attribution; use a pinned upstream reference if redistribution is not permitted. |
| Industrial requirements and identifying scope document | Restricted | Organizational authorization for each proposed use/release; remove identifying document/metadata and review contextual disclosure. Generic system names alone are insufficient. |
| Prompts and evaluator instrument | Requirement-free templates are candidates; instantiated material restricted | Sanitize embedded requirements, examples, cases and identifying context; verify permission and instrument provenance. |
| Assessments, ADRs, retrieval queries/rankings, translated cases and provenance audits | Restricted when requirement-bearing or source-linking | Apply inherited source restrictions; review model response IDs, hashes/links and contextual identification before release. |
| Raw expert exports, administrative evidence, profiles, comments and identity keys | Restricted | No raw public release planned; approved access policy and retention/withdrawal terms required. |
| Cleaned respondent data, coding logs and respondent-level summaries | Restricted | No automatic public release after replacing IDs; consider separately approved de-identified derivatives only with consent, permission and disclosure review. |
| Aggregate computational/expert tables and figures | Candidate for release | Authorization, small-cell/linkage and confidentiality review; documented disclosure rules with coverage effects. |

Phase 10 must state what is actually available, its version/license/access
conditions and what remains restricted with reasons. A review URL or archive DOI
must be supplied only when a curated, tested release exists. Do not label the
current repository anonymous, invent an open-data commitment, or release raw
responses to satisfy reproducibility. Stored-output/ compiler reproducibility
must be distinguished from model reruns: model revisions, unpinned dependencies,
approximate indexing and hardware differences limit exact regeneration.

## Task 2.1: centralized computational study values

On 2026-10-12 the researcher approved the centralized count definitions,
reconciliation audit, processing changes and verified manuscript PDF.

[prepare_study_values.py](scripts/prepare_study_values.py) is the sole owner of
the core-count definitions in
[study-values.tex](../latex-code/data/study-values.tex). It reuses the offline
requirement/catalog/applicability/RAG/ADR validators and the original frozen
selection compiler/exporter; it does not invoke their write/experiment entry
points. No model, retrieval index, Google service, or expert-response dataset
is executed or opened.

It verifies exact column order and reconstructed row equality for both
assessment exports, the preserved pre-ADR positive CSV, and the 12-story
summary (including the zero-positive story). The ADR validator also verifies
the final ADR CSV and current ADR-enriched positive CSV against the frozen
compiler, including their one-to-one positive-pair mapping and approved pilot.
The richer RAG validator verifies final Top-5 IDs/names, subset membership and
story coverage. Positive-set overlap is then recomputed by the original
selection compiler from the frozen baseline, never from a reproduced ranking.

It writes only:

- `../latex-code/data/study-values.tex`: stable macros and inline
  value/source/computation audit comments;
- `outputs/study-values-audit.json`: the same values, reconciliation checks,
  zero/positive story IDs, and source/validator SHA-256 fingerprints.

### Value-to-source audit

Source paths here are relative to the initial `adr4ai_app/` directory.
The numbers are verification targets for this frozen sample, not population
estimates or API-attempt counts.

| Macro | Verified value | Source and computation |
|---|---:|---|
| `StudySystemCount` | 4 | `data/user_histories_orig.csv`: distinct validated systems |
| `StudyStoryCount` | 12 | Same CSV: distinct validated stories |
| `StudyStoriesPerSystem` | 3 | Same CSV: equal story count in each system |
| `StudyCriterionCount` | 35 | Same CSV: validated acceptance-criterion rows |
| `StudyPatternCount` | 70 | `catalogs/patterns/`: unique validated catalog IDs |
| `StudyAssessmentCount` | 840 | Official `assessments.jsonl`: complete unique story-pattern pairs; reconciled with all-pair CSV |
| `StudyApplicableCount` | 36 | Same JSONL: applicable labels, reconciled with positive exports and compiled CSV |
| `StudyNotApplicableCount` | 31 | Same JSONL: not-applicable labels |
| `StudyInsufficientInformationCount` | 773 | Same JSONL: insufficient-information labels |
| `StudyPositiveStoryCount` | 11 | `research_results/pattern_selection_summary.csv`: stories with positive count |
| `StudyAdrCount` | 36 | `experiments/adr_generation/outputs/`: unique completed final ADRs; exact compiled/enriched CSV equality |
| `StudyRagOverlapCount` | 5 | Frozen `experiments/rag/outputs/rag_baseline.csv` joined with positive pairs by story and pattern ID: final Top-5 membership |
| `StudyRagOutsideCount` | 31 | Positive count minus overlap; not false negatives |
| `StudyRagOverlapStoryCount` | 5 | Verified summary: stories containing a positive Top-5 match |

Core macro names already used by Methodology remain stable, but catalog,
applicability and ADR macro files no longer redefine their counts.
They retain configuration or field-inventory macros. Expert-preparation
macros describe a distinct prepared instrument, not actual respondents, and
remain with their preparation validator. Equal numeric values for different
quantities must not be interpreted as identical concepts.

From this directory (Python 3.10+, standard library only):

```sh
python -B scripts/prepare_study_values.py
python -B scripts/prepare_study_values.py --check
python -B -m unittest discover -s tests -p 'test_*.py'
```

Generation validates every input before writing. `--check` rejects stale or
missing outputs and never writes. Tests cover exact totals/reconciliation,
determinism, source metadata, leading-zero IDs, schema/value/row drift,
zero-positive summary preservation, missing inputs, read-only freshness checks,
and unique ownership of core macros.

After changing count macros, rebuild the standalone pipeline figure **before**
the manuscript, using the commands in the LaTeX README. The figure now imports
the same central values instead of repeating core counts manually.
The bounded-sample table uses the central totals; individual system rows are
generated from source, not hand-maintained.

These checks establish structural consistency and computational provenance,
not expert-confirmed accuracy. Task 2.1 creates no Results subsection/table:
distribution, overlap and generation findings will be written in Tasks 2.2--2.4.
Original empirical artifacts are never overwritten. The audit contains source
links/hashes and is not automatically cleared for anonymous/public release;
Task 1.9 disclosure-review restrictions still apply.

## Task 2.2: RQ1 applicability outcomes

On 2026-10-12 the researcher approved the RQ1 text, generated table,
processing artifacts and verified manuscript PDF.

[prepare_applicability_results.py](scripts/prepare_applicability_results.py)
reuses Task 2.1's offline reconciliation, then loads the official all-pair
JSONL through the original exporter in memory. It validates the complete
unique story-pattern grid, known labels and system/story ownership, aggregates
all three labels by story and system, and checks positive counts against the
frozen 12-story summary. It never runs the exporter's write entry point.
Original artifacts remain read-only; no API/model/index or expert data is used.

Outputs:

- `outputs/applicability-results-audit.json`: all label counts by story,
  system and overall, explicit denominators, rounding policy and source/script
  hashes inherited from the central reconciliation;
- `../latex-code/data/applicability-results-values.tex`: generated percentages,
  story minimum/maximum and maximum-story IDs, and system positive counts;
- `../latex-code/tables/applicability-results.tex`: compact single-column
  overall distribution plus story rows and system subtotals.

Each percentage is `100 * label count / assessed pairs in that row`, rounded
to two decimal places for display without adjusting rounded values to force
100%. Overall denominator: 840; story denominator: 70; system denominator:
210 (3 stories times 70 patterns). System percentages are **not** shares of
the 36-positive set. All stories, including SYS04-US01 with zero positives,
are retained. Story positives sum to system positives and system totals sum
to the study totals for every label. The public-facing table reports all
labels overall and only applicable counts by story/system, as required;
the audit retains the complete label breakdown.

From this directory (Python 3.10+, standard library only):

```sh
python -B scripts/prepare_applicability_results.py
python -B scripts/prepare_applicability_results.py --check
python -B -m unittest discover -s tests -p 'test_*.py'
```

All validation precedes output writes. `--check` is read-only and rejects
stale/missing artifacts. Tests verify the exact frozen distributions,
story/system totals and denominators, retained zero-positive story, generated
percentages, deterministic outputs, unequal synthetic system sizes,
invalid/missing/duplicate pairs, label/ownership errors, and freshness failures.
Synthetic test fixtures are temporary and never written as empirical outputs.

The manuscript reports model-label frequencies and descriptive variation,
not accuracy, missed-pattern recall, causal explanations or expert-confirmed
adequacy. No RAG or ADR-result subsection is implemented in Task 2.2.
The table is sufficient for this result, so no duplicate chart is generated.
The new audit inherits internal source links and remains subject to the
Task 1.9 disclosure/release review.

## Task 2.3: RQ2 retrieval overlap

On 2026-10-12 the researcher approved the RQ2 text, comparison table,
processing artifacts and verified manuscript PDF.

[prepare_rag_results.py](scripts/prepare_rag_results.py) reuses the central
offline reconciliation, including the frozen ranking validator. It independently
intersects each story's compiled LLM-positive pattern set with that same story's
final Top-5 IDs in the official `rag_baseline.csv`, then verifies every story
count against the frozen summary and totals against the central macros.
Reproduced rankings, vector Top-15, positions and scores are not used for
the intersection. Neither models nor indexes nor expert responses are accessed.

Outputs:

- `outputs/rag-results-audit.json`: per-story positive/inside/outside counts,
  matched IDs, frozen final Top-5 IDs, percentages, definitions and source hashes;
- `../latex-code/data/rag-results-values.tex`: pooled percentage macro;
- `../latex-code/tables/rag-comparison.tex`: every story, including the
  zero-positive story, and pooled totals using central count macros.

The pooled ratio is 5/36 (13.89%); matches occur in five of the 12 stories,
and 31 positive pairs are outside final Top-5. Story percentages divide
intersections by that story's LLM-positive count, not by five retrieved
candidates. The pooled ratio is not the mean of story percentages.
For SYS04-US01, positive/inside/outside counts are zero, but the percentage
is undefined (`null` in the audit, `--` in the table). Empty sets are never
silently converted to a zero percentage. Display rounding is two decimals.

From this directory (Python 3.10+, standard library only):

```sh
python -B scripts/prepare_rag_results.py
python -B scripts/prepare_rag_results.py --check
python -B -m unittest discover -s tests -p 'test_*.py'
```

Validation precedes all writes. `--check` is read-only and rejects stale/missing
outputs. Tests cover the exact empirical intersection IDs/counts, deterministic
outputs, undefined zero denominators, pooled rather than averaged percentages,
rank-order independence, same-story membership, malformed ranking/coverage/IDs,
and read-only freshness failures. Synthetic fixtures remain in tests or temporary
directories, not empirical outputs.

The paper interprets only candidate-set overlap. Model positives are not an
independent ground-truth reference; outside candidates are not false negatives.
English query versus Portuguese applicability input and richer retrieval
catalog fields remain comparison limitations, not causally tested explanations.
Task 2.4's generation findings are not implemented here. Internal hashes/links
and ranking IDs in this audit remain subject to Task 1.9 release review.
