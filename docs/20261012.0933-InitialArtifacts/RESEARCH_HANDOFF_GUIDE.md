# ADR4AI Research Handoff Guide

**Purpose:** Help the research team resume the ADR4AI study, preserve the provenance of the existing evidence, and turn the collected artifacts into a CAIN 2027 research paper.

**Snapshot reviewed:** 12 October 2026. This guide describes the files present in this artifact collection on that date; it is not a claim that the experiments or conference requirements have been independently rerun or rechecked online.

## 1. Current state at a glance

The project already contains a complete first-pass experimental pipeline and substantial generated data, but it does **not** yet contain a paper manuscript, completed human-evaluation responses, or a live expert questionnaire.

| Workstream | State represented by the artifacts |
|---|---|
| Requirements and pattern catalog | 4 anonymized systems, 12 user stories, 35 acceptance criteria, and 70 architectural patterns. |
| Pattern applicability (Study 1) | An exhaustive LLM assessment of all 840 User Story × Pattern pairs: 36 `applicable`, 31 `not_applicable`, and 773 `insufficient_information`. These labels are model outputs, not ground truth. |
| Retrieval comparison | A frozen RAG baseline retrieves 15 candidates and reranks to 5 per story. It does not use an LLM to judge applicability or generate ADRs. |
| ADR generation | 36 ADRs, one for each pair classified as applicable, with status `Proposed`. The 36 output JSON files and provenance checks are present. |
| Expert-evaluation material | The 36 cases have been prepared in Portuguese, an evaluation-form generator is available, and local simulation checks are documented. The expert-validation phase is planned for the coming days; no Google Form creation or response collection is yet evidenced in the artifacts. |
| Analysis | Deterministic compilers create the study datasets. No separate expert-response analysis or inferential-statistics pipeline was found. |
| Paper | No `.tex`, `.bib`, or `IEEEtran.cls` file was found in the workspace snapshot. The CAIN call PDF gives IEEE conference formatting rules. |

### Main quantitative results currently represented

- The applicability set contains **36 pairs** across **11 of 12 stories**; `SYS04-US01` has no applicable patterns.
- The set sizes per story are **3, 1, 3, 5, 5, 2, 1, 5, 2, 0, 2, 7**, respectively, in story-ID order. There are **5** applicable-pair matches in the frozen final RAG Top-5, across five stories.
- The Top-5 match is a retrieval/ranking overlap only. It does not mean that a retrieved pattern was validated as applicable, and a non-match does not prove the RAG system failed to find an applicable pattern.
- The expert form is designed for one selected system per respondent. It contains 7, 12, 8, or 9 cases for SYS01–SYS04, respectively, with five required 1–5 ratings and one optional comment per case.

## 2. Study design and how it evolved

The three-page [initial research notes](Anota%C3%A7%C3%B5es%20-%20Artigo%20CAIN%202027.pdf) are useful as historical planning, not as the final protocol. They sketch several alternative flows: RAG-assisted pattern selection, LLM selection followed by ADR generation, and two separate forms (one for expert selections and one for AI-suggested patterns). They also leave the contribution and some questions open.

The implemented workflow is more specific:

1. Treat one user story plus its acceptance criteria as a requirement case. System purpose is context only.
2. Assess every one of the 70 patterns against every one of the 12 cases independently. A positive assessment must cite a user-story or acceptance-criterion ID; the prompt distinguishes `applicable`, `not_applicable`, and `insufficient_information`.
3. Generate one ADR for each of the 36 positive pairs, preserving a direct join key `(user_story_id, pattern_id)`.
4. Compare the 36 positive pairs with the final RAG Top-5 membership, as a preliminary retrieval baseline comparison.
5. Present the 36 generated ADR cases to domain/architecture evaluators using the current single-form design, rather than assuming the older two-form plan is still in force.

The executable pattern-selection prompt and validation rules are in [`assess_pattern.py`](adr4ai_app/experiments/pattern_selection/assess_pattern.py); the official resumable runner is [`run_experiment.py`](adr4ai_app/experiments/pattern_selection/run_experiment.py). The separate RAG approach is documented in [`experiments/rag/README.md`](adr4ai_app/experiments/rag/README.md). ADR-generation rules and the one-shot pilot are in [`generate_adr.py`](adr4ai_app/experiments/adr_generation/generate_adr.py), with the full runner in [`experiments/adr_generation/run_experiment.py`](adr4ai_app/experiments/adr_generation/run_experiment.py).

## 3. Artifact map and source-of-truth guidance

Paths below are relative to this guide.

### Requirements and patterns

- [`[INPUT] user_histories_orig.csv`](%5BINPUT%5D%20user_histories_orig.csv) is a top-level mirror of [`adr4ai_app/data/user_histories_orig.csv`](adr4ai_app/data/user_histories_orig.csv). Their SHA-256 values matched during this review.
- [`Escopo_Dados_Estudo_Cagece_v4.pdf`](Escopo_Dados_Estudo_Cagece_v4.pdf) describes the bounded sample and states that generic system identifiers are used to preserve the source organization's confidentiality. Keep the anonymized IDs in any paper, slides, and shared artifact.
- [`adr4ai_app/catalogs/patterns/`](adr4ai_app/catalogs/patterns/) contains the 70 individual pattern JSON records (`P001.json`–`P070.json`). The RAG package has a separate consolidated catalog at [`experiments/rag/catalogs/all-patterns.json`](adr4ai_app/experiments/rag/catalogs/all-patterns.json).

### Experiment outputs

- [`pattern_selection/outputs/assessments.jsonl`](adr4ai_app/experiments/pattern_selection/outputs/assessments.jsonl) is the primary 840-record assessment log; `failures.jsonl` records runner failure state. `pattern_assessments.csv` is the all-pairs export and `applicable_patterns.csv` is the 36-positive subset.
- `pattern_selection/outputs/pilot_SYS01-US01*` contains several earlier isolated pilot runs. The official output is the top-level `assessments.jsonl`, not the pilot directories or `test_assessment*.json` files. Do not merge pilot records into the official dataset.
- [`experiments/rag/outputs/rag_baseline.csv`](adr4ai_app/experiments/rag/outputs/rag_baseline.csv) and `rag_baseline.md` are the frozen official baseline. `rag_baseline_reproduced.csv` and `rag_baseline_reproduced.md` are separate reproduction outputs, not the official input to the compiler.
- [`adr_generation/outputs/`](adr4ai_app/experiments/adr_generation/outputs/) contains 36 top-level final ADR JSON files. `outputs/attempts/` contains 37 attempt/claim records, including failure metadata; these are execution history, not 37 additional ADRs.

### Compiled and translated results

- [`research_results/README.md`](adr4ai_app/research_results/README.md) explains the data lineage and compilation sequence.
- [`research_results/pattern_selection_results.csv`](adr4ai_app/research_results/pattern_selection_results.csv) is the current 36-row Study 1 dataset enriched with a formatted `adr` column. The top-level [`[OUTPUT] pattern_selection_results.csv`](%5BOUTPUT%5D%20pattern_selection_results.csv) is a byte-identical mirror as checked on 12 October 2026.
- [`pattern_selection_results_before_adr.csv`](adr4ai_app/research_results/pattern_selection_results_before_adr.csv) is the preserved pre-ADR Study 1 file; [`pattern_selection_summary.csv`](adr4ai_app/research_results/pattern_selection_summary.csv) has one row for each of the 12 stories.
- [`adr_generation_results.csv`](adr4ai_app/research_results/adr_generation_results.csv) retains ADR fields and generation metadata in separate columns. [`compile_adr_results.py`](adr4ai_app/research_results/compile_adr_results.py) joins by story and pattern IDs, verifies source/prompt hashes and structured-output metadata, and regenerates the final datasets without API calls.
- [`expert_evaluation_cases_pt.csv`](adr4ai_app/research_results/expert_evaluation_cases_pt.csv) is the 36-case, evaluator-facing Portuguese material. Research-only preparation records include `expert_evaluation_translations_pt.csv`, `expert_evaluation_translation_audit.csv`, `expert_evaluation_manual_corrections.csv`, `expert_evaluation_language_classification.csv`, and `expert_evaluation_translation_run/`.
- The translation preparation report records 324 translated/mapped fields, 12 Portuguese-preserved fields, 289 translated non-Portuguese fields, 14 mixed-language fields, 9 preserved empty fields, and five explicitly authorized manual language corrections. The report says requirements were retained literally and that the translations do not constitute architectural evaluation. See [`expert_evaluation_preparation_report.md`](adr4ai_app/research_results/expert_evaluation_preparation_report.md) and [`expert_evaluation_mixed_language_review.md`](adr4ai_app/research_results/expert_evaluation_mixed_language_review.md).
- [`adr_output.pdf`](adr_output.pdf) is a 37-page evaluation-case document. Treat it as a presentation artifact, not as a record of evaluator ratings.

### Expert questionnaire

[`research_results/google_forms/`](adr4ai_app/research_results/google_forms/) contains `create_expert_evaluation_form.gs` and its [`README.md`](adr4ai_app/research_results/google_forms/README.md). The script embeds the 36 translated cases. It is guarded by `ALLOW_FORM_CREATION = false`; setup requires a researcher to review and deliberately run it in their own Google Apps Script account. The preparation report says local stand-ins were used to test item construction and routing; no Google account or API was used. Confirm whether a form was created outside this artifact directory before recruiting or claiming that evaluation is underway.

## 4. Safe reproduction and continuation

Run any commands from the application directory:

```sh
cd docs/20261012.0933-InitialArtifacts/adr4ai_app
```

### First: verify, do not regenerate

1. Keep the current artifacts unchanged and take a separate backup/versioned copy before any operation that writes files.
2. Run the applicability runner without `--run` to perform its preflight only:

   ```sh
   python experiments/pattern_selection/run_experiment.py
   ```

   The runner documents that `--run` is required to launch API assessments. Do **not** pass it merely to inspect the current study.
3. Inspect the frozen counts and pair sets in `research_results/pattern_selection_summary.csv`, `experiments/pattern_selection/outputs/assessments.jsonl`, and `research_results/README.md`. Confirm the 12 × 70 pair coverage before any interpretation.
4. If you need to rebuild the integrated CSVs from the stored evidence, run:

   ```sh
   python -B research_results/compile_adr_results.py
   ```

   This reads the backup and stored ADR JSONs, validates them, and writes the two compiled result datasets. It does not call a model API.

**Important:** `python research_results/compile_results.py` restores the pre-ADR Study 1 version of `pattern_selection_results.csv`. To reconstruct the final ADR-integrated version after that operation, run `python -B research_results/compile_adr_results.py` afterward. Avoid running the first compiler casually against the current final file.

### Experiments that should require explicit approval

- Re-running pattern applicability with `--run` can make up to 840 external model calls, subject to the runner's resume/failure state. It uses `OPENAI_API_KEY`, has a maximum of three attempts per pair, and disables SDK retries. Inspect current state and approve cost/model/prompt changes before doing this.
- ADR generation also has API-backed execution, persistent attempt records, and explicit handling for failed attempts. The existing 36 completed ADRs are validated by the compiler. Do not regenerate or overwrite them to reproduce the published dataset; use the stored outputs.
- Rebuilding the RAG baseline can download embedding/reranking models and an approximate vector index may yield rankings that differ across environments. Its README specifies Python 3.12 and warns that model download revisions are not pinned. No isolated end-to-end reproduction test is recorded as complete.
- The Portuguese translation artifacts already include a documented authorization and audit trail. Do not retranslate or silently normalize them; keep edits to evaluator-facing text separate from the archived audit and source values.
- Creating the Google Form is an external, persistent action. Review the script and respondent access settings first. The script intentionally blocks creation by default and protects against accidental repeat creation.

## 5. What remains before a defensible paper

### A. Finish the empirical evaluation

1. Confirm organizational permission and the appropriate consent/ethics process for expert participation. The data-scope PDF limits the research sample; it does not itself document approval for a particular recruitment or questionnaire procedure.
2. Review and, if approved, create the form using its instructions. Confirm that the four system routes, item content, privacy settings, and signed-out respondent access behave as intended in the actual Google environment.
3. Recruit qualified evaluators, record the inclusion/experience criteria and response count, collect the response spreadsheet, and preserve a read-only raw export.
4. Write and validate the missing response-analysis workflow: handle route-dependent blank cells correctly, summarize ordinal ratings by question/case/system, explain missingness and respondent-level clustering, and define any inter-rater agreement or qualitative-comment analysis before inspecting results. Do not treat the form's local simulation report as human evidence.
5. Decide whether reviewing only the 36 AI-positive pairs supports the intended claims. This design can assess the quality/acceptability of generated positives, but by itself it cannot estimate missed-pattern recall or compare the AI's selections against experts' full selections over all 70 patterns.

### B. Lock the study protocol and claims

- State research questions and the contribution precisely. The notes leave “contribution” blank; a useful draft question in the related-work spreadsheet asks how far LLMs can identify appropriate architectural pattern solutions, but it is not yet a finalized RQ.
- Describe the experimental unit and denominators explicitly: 840 possible applicability pairs, 36 LLM-positive pairs, 12 user stories from four systems, and 70 patterns.
- Separate the three distinct things measured: (1) model classification of pattern applicability, (2) retrieval/reranking overlap, and (3) human assessment of generated ADRs/pattern recommendations.
- Report the baseline as a retrieval baseline, not as a competing applicability oracle. The compiled comparison uses final Top-5 membership, excludes Top-15 ranks, and finds 5/36 overlaps.
- Treat LLM applicability labels as predictions. Expert review has not yet established their correctness; avoid “ground truth,” “validated pattern,” or effectiveness claims until supported by human results.
- Discuss external validity limits: this is a small, bounded sample of 12 stories from four systems and one 70-pattern catalog. Also document model, prompt, reasoning effort, retries, translation handling, and the one recorded ADR connection-failure retry.

### C. Start the manuscript

There is currently no TeX/Bib project in the workspace. Create a separate manuscript directory and establish an anonymized IEEE conference LaTeX build before drafting the camera-ready version.

The downloaded [CAIN 2027 Research Track call](CAIN%202027%20-%20Research%20Track%20-%20CAIN%202027.pdf) states:

- Full research papers: up to **10 pages plus 2 pages of references**; short research: up to **5 pages plus 2 pages of references**.
- IEEE conference proceedings format; LaTeX must use `\documentclass[10pt,conference]{IEEEtran}` without `compsoc` or `compsocconf`.
- Double-anonymous review, including anonymized linked artifact repositories; refer to authors' prior work in third person rather than removing the citation.
- Submission deadline shown in the downloaded page: **Friday, 30 October 2026 (AoE / UTC-12)**.
- The call encourages anonymized, curated, reproducible artifacts and long-term archival. It also prohibits simultaneous submission elsewhere while under review.

The deadline and formatting above are transcribed from the local PDF snapshot, whose page print timestamp is 12 October 2026. Reconfirm the live CAIN page and submission-system requirements before submission.

Suggested paper structure to adapt after the RQs and human evaluation are settled:

1. Abstract and contributions.
2. Introduction and motivation.
3. Background and related work.
4. Study design: data, pattern catalog, applicability prompt/protocol, RAG baseline, ADR generation, and human evaluation.
5. Results, separated by research question and evidence source.
6. Discussion, implications, limitations, and threats to validity.
7. Reproducibility/artifact availability, ethics and data-permission statement, and conclusion.

## 6. Related-work reading set

The directory [`related_works/`](related_works/) contains eight papers plus a two-page literature worksheet. Read and cite the originals rather than relying on the worksheet's draft annotations.

| File | Why it belongs in the review |
|---|---|
| [`llms as design patterns for ai-based system patterns an empirical evaluation.pdf`](related_works/llms%20as%20design%20patterns%20for%20ai-based%20system%20patterns%20an%20empirical%20evaluation.pdf) | Closest prior work in the bundle: AI-system design patterns, model-generated solutions, mixed-method and human evaluation. The worksheet identifies it as CAIN 2026 work; verify the final bibliographic record and clearly position the new study relative to it. |
| [`Can_LLMs_Generate_Architectural_Design_Decisions_An_Exploratory_Empirical_Study.pdf`](related_works/Can_LLMs_Generate_Architectural_Design_Decisions_An_Exploratory_Empirical_Study.pdf) | Direct precedent on LLM generation of ADRs under different prompting/model settings. |
| [`An_LLM_assisted_approach_to_designing_software_architectures_using_add.pdf`](related_works/An_LLM_assisted_approach_to_designing_software_architectures_using_add.pdf) | LLM assistance within Attribute-Driven Design and architect-in-the-loop case studies. |
| [`Large_Language_Models_as_Assistants_in_Software_Architecture_Design.pdf`](related_works/Large_Language_Models_as_Assistants_in_Software_Architecture_Design.pdf) | Broader human/LLM software-architecture design-assistant framing. |
| [`Do_Large_Language_Models_Contain_Software_Architectural_Knowledge.pdf`](related_works/Do_Large_Language_Models_Contain_Software_Architectural_Knowledge.pdf) | Evaluates architectural-knowledge answers and highlights expert review and precision/recall concerns. |
| [`using_llms_in_generating_design_rationale_for_software_architecture_decisions.pdf`](related_works/using_llms_in_generating_design_rationale_for_software_architecture_decisions.pdf) | Relevant to rationale and decision-record generation; inspect its study design and evaluation measures. |
| [`Rule_based_architectural_design_pattern_recognition_with_gpt_models.pdf`](related_works/Rule_based_architectural_design_pattern_recognition_with_gpt_models.pdf) | Pattern recognition with GPT under explicit rules, but its setting is web/MVW patterns rather than requirement-driven selection of AI-system patterns. |
| [`Trabalhos Relacionados - Página1.pdf`](related_works/Trabalhos%20Relacionados%20-%20P%C3%A1gina1.pdf) | Draft literature matrix with candidate RQs, links, search notes, and comments; it is a working document, not a verified bibliography. |

## 7. Evidence and interpretation guardrails

- Preserve stable IDs as text, especially three-digit pattern IDs and criterion IDs. All joins should use `(user_story_id, pattern_id)`, never row position or pattern name.
- Keep source requirement text, pattern-catalog fields, assessment rationales, generated ADRs, and translated evaluator material as separate evidence layers. The translation compiler and reports document which changes were linguistic only.
- Preserve attempt/failure files for provenance. A failed attempt is not an extra experimental outcome or ADR.
- Distinguish the 36-row “applicable only” dataset from the complete 840-row assessment record; a zero-positive story is still in the study summary.
- Do not expose internal preparation/audit files in the evaluator packet. The form README explicitly says to present only `expert_evaluation_cases_pt.csv`.
- Before sharing data/code for review, anonymize both paper and artifact repository. The generic system names are intentional and should remain so.

## 8. Recommended immediate sequence

1. Freeze and back up this artifact snapshot; verify the current official outputs and hashes.
2. Confirm permissions/ethics, whether a Google Form already exists, and the intended evaluator recruitment plan.
3. Finalize RQs, the interpretation of the RAG comparison, and whether the current expert-evaluation sampling can answer those RQs.
4. Run the expert evaluation only after protocol approval, then implement and validate the response-analysis pipeline.
5. Draft the methods and results directly from the frozen artifacts; write claims only after human ratings are analyzed.
6. Create the IEEEtran manuscript and anonymized artifact package, then recheck CAIN requirements and deadline against the live venue pages.
