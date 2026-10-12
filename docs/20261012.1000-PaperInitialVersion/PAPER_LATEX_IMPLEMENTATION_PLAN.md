# ADR4AI Full Paper LaTeX Implementation Plan

## 1. Objective

Produce the complete English LaTeX source for a CAIN 2027 full research paper about **ADR4AI: LLM-Based Architectural Pattern Selection and ADR Generation for AI-Enabled Systems**.

The finished paper must:

- follow the classic software engineering full research paper structure;
- use the CAIN 2027 IEEE conference format recorded in the research artifacts;
- fit the full-paper limit of 10 content pages plus at most 2 pages of references;
- remain double-anonymous for review;
- distinguish current computational results from the expert-validation results that will be collected in the coming days;
- make only claims supported by traceable study evidence; and
- keep **all LaTeX source, bibliography data, tables, figures, and build configuration under `latex-code/`**.

This plan is ordered by research dependency rather than final reading order. It starts with Methodology, Results, and Discussion because the evidence and claims must stabilize before the Introduction and Abstract are written.

## 2. Inputs and authoritative evidence

The writing process must start from the following artifacts:

- `../20261012.0933-InitialArtifacts/RESEARCH_HANDOFF_GUIDE.md`: research-state synthesis, provenance map, open work, and interpretation guardrails.
- `../20261012.0933-InitialArtifacts/adr4ai_app/data/user_histories_orig.csv`: authoritative requirement sample.
- `../20261012.0933-InitialArtifacts/adr4ai_app/catalogs/patterns/`: 70-pattern catalog.
- `../20261012.0933-InitialArtifacts/adr4ai_app/experiments/pattern_selection/outputs/assessments.jsonl`: complete 840-pair applicability output.
- `../20261012.0933-InitialArtifacts/adr4ai_app/research_results/pattern_selection_summary.csv`: per-story applicability summary.
- `../20261012.0933-InitialArtifacts/adr4ai_app/experiments/rag/outputs/rag_baseline.csv`: frozen official RAG baseline.
- `../20261012.0933-InitialArtifacts/adr4ai_app/research_results/adr_generation_results.csv`: generated ADR dataset and generation metadata.
- `../20261012.0933-InitialArtifacts/adr4ai_app/research_results/expert_evaluation_cases_pt.csv`: evaluator-facing cases.
- `../20261012.0933-InitialArtifacts/adr4ai_app/research_results/expert_evaluation_preparation_report.md`: translation and preparation audit.
- `../20261012.0933-InitialArtifacts/adr4ai_app/research_results/google_forms/README.md`: expert questionnaire design and routing.
- `../20261012.0933-InitialArtifacts/related_works/`: collected related-work papers and literature matrix.
- `../20261012.0933-InitialArtifacts/CAIN 2027 - Research Track - CAIN 2027.pdf`: local snapshot of venue requirements.
- The future raw and analyzed expert-validation datasets, once collected and frozen.

The paper must not treat the 36 LLM-positive classifications as ground truth. Until expert responses are integrated, all human-validation values and conclusions must remain explicit placeholders.

## 3. Required LaTeX project structure

Create the following structure during implementation:

```text
docs/20261012.1000-PaperInitialVersion/
├── PAPER_LATEX_IMPLEMENTATION_PLAN.md
└── latex-code/
    ├── main.tex
    ├── preamble.tex
    ├── metadata.tex
    ├── README.md
    ├── latexmkrc
    ├── sections/
    │   ├── 00-abstract.tex
    │   ├── 01-introduction.tex
    │   ├── 02-background-related-work.tex
    │   ├── 03-methodology.tex
    │   ├── 04-results.tex
    │   ├── 05-discussion.tex
    │   ├── 06-threats-to-validity.tex
    │   ├── 07-conclusion.tex
    │   └── 08-artifact-availability.tex
    ├── data/
    │   ├── study-values.tex
    │   └── expert-values.tex
    ├── tables/
    │   ├── dataset-summary.tex
    │   ├── research-questions.tex
    │   ├── applicability-results.tex
    │   ├── rag-comparison.tex
    │   ├── expert-demographics.tex
    │   └── expert-evaluation-results.tex
    ├── figures/
    │   ├── approach-overview.pdf
    │   ├── study-design.pdf
    │   └── expert-results.pdf
    └── bibliography/
        └── references.bib
```

Rules for this structure:

- `main.tex` must use `\documentclass[10pt,conference]{IEEEtran}` without `compsoc` or `compsocconf`.
- `main.tex` must orchestrate section files and contain no substantial section prose.
- `preamble.tex` must contain packages and reusable commands only.
- `metadata.tex` must contain the anonymized review title and anonymous author metadata. Camera-ready identities must not be inserted into the review branch/source version.
- Repeated quantitative values must be defined once in `data/study-values.tex` or `data/expert-values.tex` and referenced from prose and tables.
- Missing expert results must use visibly unresolved macros such as `\ExpertRespondentCountTBD`, not plausible-looking dummy numbers.
- Tables must be separate `.tex` fragments. Figures must be generated or curated as publication-ready vector PDFs whenever possible.
- Bibliography entries must be manually verified against the original publications. The draft literature worksheet is not itself a citable source.
- No paper source may depend on a path outside `latex-code/` at build time. External research artifacts are evidence inputs, not LaTeX build dependencies.

## 4. Target paper structure

The final paper should appear in this conventional order:

1. Abstract
2. Introduction
3. Background and Related Work
4. Methodology
5. Results
6. Discussion and Implications
7. Threats to Validity
8. Conclusion
9. Artifact Availability / Open Science statement
10. References

Within Methodology and Results, organize content by explicit research questions. Final wording must be locked in Phase 1, but the intended concerns are:

- **RQ1 — Pattern applicability:** What architectural patterns does the LLM identify as applicable to the requirement cases, and how are the classifications distributed?
- **RQ2 — Retrieval comparison:** To what extent do the LLM-positive patterns overlap with the frozen RAG Top-5 candidates?
- **RQ3 — Expert assessment:** How do experts assess the applicability of the recommended patterns and the quality of their generated ADRs?

These are planning formulations, not final protocol statements. They must be reconciled with the expert questionnaire and the claims the collected data can actually support.

---

## Phase 1 — Methodology

**Section produced:** `sections/03-methodology.tex`

**Priority:** Critical. Complete before drafting result interpretations or contribution claims.

### Task 1.1 — Freeze the research questions and claim boundaries

**Work**

- Reconstruct the implemented study protocol from code, frozen outputs, evaluation preparation, and researcher decisions.
- Finalize RQ wording so each question maps to available or scheduled evidence.
- Explicitly separate:
  - LLM applicability classification;
  - RAG retrieval/reranking overlap;
  - LLM-based ADR generation; and
  - expert assessment of pattern applicability and ADR quality.
- State that expert evaluation of only the 36 positive pairs cannot independently estimate recall over all 840 pairs unless additional negative/all-pattern evaluation data are collected.

**Deliverables**

- Final RQ text in `tables/research-questions.tex`.
- A claim-to-evidence matrix maintained in comments or working notes and reflected in the section.

**Completion criteria**

- Every RQ names its unit of analysis, evidence source, and intended analysis.
- No RQ requires data that the current protocol cannot produce.

### Task 1.2 — Describe the industrial requirement sample

**Work**

- Document the bounded sample: 4 anonymized systems, 12 user stories, 3 stories per system, and 35 acceptance criteria.
- Explain why systems use generic identifiers and state what data are excluded.
- Describe the requirement-case representation: system purpose, user story, and acceptance criteria.
- Clarify that system purpose is contextual, while applicability evidence must come from a user story or acceptance criterion.
- Avoid disclosing the source organization's identity if doing so would weaken double anonymity or violate data-use constraints.

**Deliverables**

- Dataset subsection.
- `tables/dataset-summary.tex`.
- Stable values in `data/study-values.tex`.

**Completion criteria**

- All counts agree with the authoritative dataset and validation scripts.
- The sample is described as bounded and non-representative rather than generalized to all AI-enabled systems.

### Task 1.3 — Describe the architectural pattern catalog

**Work**

- Explain the 70-pattern catalog and the fields supplied to the model: ID, name, motivation, solution, and consequences.
- Document catalog provenance using citable original sources where available.
- Explain preservation of three-digit IDs and empty source fields.
- Avoid implying that all patterns are equally mature, independent, or universally applicable unless the catalog evidence supports it.

**Deliverables**

- Pattern-catalog subsection.
- Verified bibliography entries for catalog sources.

**Completion criteria**

- Catalog size and field definitions match the stored JSON records.
- Every provenance statement has a verified citation or is presented as an artifact fact.

### Task 1.4 — Specify the exhaustive pattern-applicability experiment

**Work**

- Describe the full 12 × 70 factorial assessment design and its 840 independent calls.
- State the model identifier, reasoning effort, strict structured-output schema, sequential execution, and retry policy exactly as recorded.
- Explain the three labels: `applicable`, `not_applicable`, and `insufficient_information`.
- Document the grounding and evidence-reference rules.
- Explain validation, resume behavior, failure recording, and exclusion of pilot/test outputs from the official dataset.
- Include enough prompt detail for replication while moving a full prompt listing to the artifact if page space requires it.

**Deliverables**

- Applicability-experiment subsection.
- Concise algorithm or workflow figure in `figures/study-design.pdf`, if it communicates the design more efficiently than prose.

**Completion criteria**

- The paper makes clear that the classifications are generated predictions, not labels supplied by experts.
- The official output can be distinguished unambiguously from pilot outputs.

### Task 1.5 — Specify the RAG retrieval baseline

**Work**

- Describe the requirement-query construction and preservation of story/criterion identifiers.
- State the embedding model, vector Top-15 retrieval, cross-encoder reranking, and final Top-5.
- Explain that the baseline uses no external LLM for applicability classification or ADR generation.
- Define the comparison metric precisely: whether each LLM-positive pair appears in the frozen final Top-5 for the same story.
- State that this comparison measures candidate overlap, not precision, recall, or ground-truth applicability.
- Record reproducibility caveats: model revisions are not pinned and rebuilt approximate indices may vary.

**Deliverables**

- RAG-baseline subsection.
- Formal overlap definition or concise equation.

**Completion criteria**

- Top-15 and Top-5 roles are not conflated.
- No language treats the RAG output as validated applicability.

### Task 1.6 — Specify ADR generation

**Work**

- Explain that one ADR is generated for each of the 36 positive pairs.
- Describe the inputs: requirement case, selected pattern, evidence references/text, and applicability rationale.
- Describe the Nygard-inspired fields: title, fixed `Proposed` status, context, decision, and consequences.
- State the model configuration, one-call-per-ADR design, strict output validation, source/prompt hashes, and stored response metadata.
- Document the approved pilot and the explicitly authorized retry for the recorded technical connection failure without counting it as another ADR.

**Deliverables**

- ADR-generation subsection.
- Pipeline figure `figures/approach-overview.pdf` showing requirements → exhaustive applicability assessment → selected pairs → ADR generation → expert assessment, with the RAG baseline shown as a comparison branch.

**Completion criteria**

- The paper states that 36 ADRs correspond to 36 unique `(user_story_id, pattern_id)` pairs.
- Generated text is not described as architect-approved before expert results support that statement.

### Task 1.7 — Specify translation and expert-evaluation preparation

**Work**

- Describe translation of evaluator-facing material into Portuguese while preserving source requirements and auditability.
- Report the translation categories and five authorized manual corrections only if relevant to methodological transparency.
- Describe the questionnaire profile questions, one-system-per-evaluator routing, 1–5 response scale, five questions per case, and optional comments.
- Include the exact constructs measured by Q1–Q5 after verifying them in the form script.
- Document evaluator inclusion criteria, recruitment, consent/ethics process, administration procedure, and anonymity/privacy safeguards once approved.
- Clearly mark procedural details not yet finalized as protocol placeholders, not completed actions.

**Deliverables**

- Expert-evaluation subsection with pre-collection and post-collection portions clearly distinguished.
- No human-result values in Methodology.

**Completion criteria**

- Questionnaire simulation is described only as implementation validation, not empirical validation.
- The paper does not claim the form was deployed until deployment is evidenced.

### Task 1.8 — Define the analysis protocol before reading expert results

**Work**

- Define response inclusion/exclusion rules and treatment of route-dependent blank cells.
- Select appropriate descriptive statistics for ordinal Likert data: response distributions, median, and interquartile range; use means only with an explicit justification.
- Define aggregation levels: question, ADR case, user story, system, and respondent.
- Decide whether and how to measure inter-rater agreement, accounting for unequal/system-specific case assignment.
- Define treatment of optional comments and any qualitative coding protocol.
- Define the expert-validation criterion without creating an arbitrary post hoc threshold.
- State whether analyses are exploratory or confirmatory.

**Deliverables**

- Analysis subsection.
- A predeclared table/figure list for expert results.

**Completion criteria**

- Every planned Results table has a defined source and computation.
- Analysis choices are recorded before response inspection.

### Task 1.9 — Add ethics, data governance, and reproducibility procedures

**Work**

- Document authorization to use the bounded industrial requirement sample.
- Document expert-participation approval/consent and privacy practices.
- State model/API use and generated-content handling.
- Explain artifact versioning, immutable raw responses, derived datasets, and deterministic compilers.
- Define what can be shared openly and what must remain restricted.

**Deliverables**

- Methodology ethics/reproducibility paragraph.
- Inputs for the Artifact Availability section.

**Completion criteria**

- No unsupported statement of formal ethics-board approval.
- Confidential and anonymized material is consistently distinguished.

---

## Phase 2 — Results: Existing Computational Evidence

**Section produced:** first part of `sections/04-results.tex`

**Dependency:** Phase 1 RQs and analysis definitions.

### Task 2.1 — Validate and centralize all existing study values

**Work**

- Recompute or verify all reported counts from frozen official artifacts.
- Define stable LaTeX macros for:
  - 4 systems;
  - 12 stories;
  - 35 acceptance criteria;
  - 70 patterns;
  - 840 assessed pairs;
  - 36 applicable;
  - 31 not applicable;
  - 773 insufficient information;
  - 11 stories with at least one applicable pattern;
  - 36 generated ADRs; and
  - 5 positive pairs present in the final RAG Top-5.
- Ensure macros are used consistently in prose and tables.

**Deliverables**

- `data/study-values.tex`.
- A value-to-source audit table in implementation notes or LaTeX comments.

**Completion criteria**

- Values reconcile across JSONL, compiled CSVs, and summaries.
- No quantitative value is manually duplicated in multiple prose locations.

### Task 2.2 — Report applicability-classification outcomes

**Work**

- Present the overall three-label distribution.
- Present applicable counts by user story and system.
- Highlight `SYS04-US01` as a zero-positive case without treating zero as an error.
- Identify concentration or variation descriptively without causal speculation.
- Consider a compact stacked distribution or per-story bar chart if it communicates more efficiently than a wide table.

**Deliverables**

- RQ1 Results subsection.
- `tables/applicability-results.tex`.
- Optional publication-ready figure.

**Completion criteria**

- Every denominator is explicit.
- Results remain descriptive and do not imply expert-confirmed correctness.

### Task 2.3 — Report the RAG comparison

**Work**

- Report per-story and overall final Top-5 membership overlap.
- State that 5 of 36 LLM-positive pairs occur in the final Top-5 and that the matches span five stories.
- Report 31 positive pairs outside the final Top-5 without labeling them RAG false negatives.
- If useful, show the story-level overlap counts already present in the summary dataset.
- Do not calculate precision/recall without an independently established reference set.

**Deliverables**

- RQ2 Results subsection.
- `tables/rag-comparison.tex`.

**Completion criteria**

- The table and prose use identical definitions and totals.
- Conclusions are limited to retrieval overlap.

### Task 2.4 — Report ADR-generation completion and provenance

**Work**

- Report the number of unique generated ADRs, field completeness, proposed status, and one-to-one pair mapping.
- Report the technical retry as execution metadata, not an extra data point.
- Provide one short anonymized example only if it materially clarifies output structure and fits the page budget.
- Reserve ADR quality judgments for expert results.

**Deliverables**

- ADR-generation Results subsection.
- Optional compact example table or listing.

**Completion criteria**

- Generation success/completeness is not conflated with semantic quality.

### Task 2.5 — Install explicit expert-result placeholders

**Work**

- Create unresolved macros in `data/expert-values.tex` for participant count, experience, completed system evaluations, missing responses, rating summaries, agreement values, and qualitative themes.
- Create table shells with captions and defined intended content, but no invented numbers.
- Add visible LaTeX warnings or bold `TBD` output so the manuscript cannot silently appear complete.
- Draft the RQ3 prose as claim-neutral sentence templates whose subjects, statistics, direction, and interpretation are supplied only by verified macros after consolidation. For example: “For Q1, the response distribution was \ExpertQOneDistributionTBD{}; the median was \ExpertQOneMedianTBD{} (IQR \ExpertQOneIQRTBD{}).”
- If preliminary internal summaries are useful for coordinating the team, label them `PRELIMINARY—NOT VERIFIED`, keep them outside the submission manuscript, and never use them to select only favorable examples or conclusions.
- Do not mock favorable observations, respondent quotations, sample sizes, statistics, agreement values, or themes. Synthetic data may be used only to test analysis code or table layout, must be stored outside the empirical results, and must be unmistakably labeled `SYNTHETIC—NOT STUDY DATA`.
- Keep the draft Discussion conditional and direction-neutral: enumerate interpretations for favorable, mixed, and unfavorable outcomes, then retain only the branch supported by the frozen expert dataset.

**Deliverables**

- `data/expert-values.tex`.
- `tables/expert-demographics.tex`.
- `tables/expert-evaluation-results.tex`.

**Completion criteria**

- A draft build succeeds while making every unresolved human result unmistakable.
- No placeholder resembles a real observation.
- No preliminary or synthetic value can be included in the submission build without triggering an explicit unresolved-data marker.

---

## Phase 3 — Results: Expert-Validation Integration

**Section produced:** final RQ3 part of `sections/04-results.tex`

**Dependency:** Expert validation completed; raw response export frozen; Task 1.8 analysis protocol approved.

### Task 3.1 — Freeze and document the expert-response dataset

**Work**

- Save an immutable raw export and record collection dates, form version, response count, and checksum.
- Remove or protect accidental identifiers according to the approved privacy protocol.
- Create a clean analysis dataset while preserving raw-to-derived traceability.
- Verify routing blanks versus genuinely missing required responses.

**Deliverables**

- Documented raw and clean dataset versions outside the LaTeX tree.
- Dataset metadata summarized in Methodology.

**Completion criteria**

- Every analyzed response can be traced to a raw row without exposing respondent identity.

### Task 3.2 — Validate respondent eligibility and sample composition

**Work**

- Apply predeclared inclusion/exclusion rules.
- Summarize professional, software-architecture, and evaluated-system experience.
- Report respondent distribution across SYS01–SYS04.
- Avoid reporting small-cell details that risk re-identification.

**Deliverables**

- Final `tables/expert-demographics.tex`.
- Respondent/sample paragraph in Results.

**Completion criteria**

- Included and excluded counts reconcile with the raw response count.

### Task 3.3 — Compute case- and question-level expert results

**Work**

- Compute predeclared ordinal summaries and response distributions for Q1–Q5.
- Report results by case and aggregated at justified levels.
- Separate pattern-applicability judgments from ADR-quality dimensions.
- Compute agreement only if the sample design and response density make it meaningful.
- Record all transformations in a reproducible analysis script before transferring values into LaTeX macros.

**Deliverables**

- Final `data/expert-values.tex`.
- Final `tables/expert-evaluation-results.tex`.
- `figures/expert-results.pdf` if a figure improves readability.
- RQ3 quantitative Results text.

**Completion criteria**

- Every paper value is reproducible from the frozen clean dataset.
- Aggregation does not overweight systems or cases merely because they have more recommended patterns.

### Task 3.4 — Analyze optional comments

**Work**

- Apply the predeclared qualitative procedure.
- Develop and audit codes/themes relevant to applicability, ADR grounding, clarity, feasibility, novelty, or missing context.
- Select short anonymized quotations only with appropriate consent and without identifying systems or respondents.
- Integrate qualitative findings as explanation or nuance, not as numerical confirmation.

**Deliverables**

- Qualitative RQ3 Results subsection.
- Theme definitions and counts where appropriate.

**Completion criteria**

- Themes are grounded in comments and counterexamples/negative cases are retained.

### Task 3.5 — Remove all result placeholders and run consistency checks

**Work**

- Replace every `TBD` expert macro.
- Search LaTeX sources for placeholder markers and unresolved notes.
- Cross-check Results text, tables, figures, and Methodology sample counts.
- Update RQ3 wording if the actual sample cannot support the originally planned analysis.

**Deliverables**

- Complete expert Results section with no unresolved empirical placeholders.

**Completion criteria**

- Zero placeholder markers remain.
- All human-evidence claims are supported by the final analysis outputs.

---

## Phase 4 — Discussion and Implications

**Section produced:** `sections/05-discussion.tex`

**Dependency:** Phases 2 and 3.

### Task 4.1 — Answer each research question directly

**Work**

- Start with concise evidence-based answers to RQ1–RQ3.
- Separate observations, interpretations, and speculation.
- Explain whether expert results corroborate, qualify, or challenge LLM-positive classifications and generated ADRs.
- Avoid generalizing beyond the bounded sample and catalog.

**Deliverables**

- RQ-organized discussion opening.

**Completion criteria**

- Each answer cites the relevant Results table/figure.
- No new numerical result appears for the first time in Discussion.

### Task 4.2 — Interpret the LLM-versus-RAG relationship

**Work**

- Explain why exhaustive pairwise applicability assessment and semantic Top-5 retrieval answer different questions.
- Discuss the observed overlap without declaring one method superior on unsupported metrics.
- Identify whether RAG may be useful as a cost-reduction candidate-generation stage for future controlled study.
- Separate evidence from proposed future pipeline designs.

**Deliverables**

- Comparative interpretation subsection.

**Completion criteria**

- Discussion does not relabel retrieval non-overlap as error.

### Task 4.3 — Discuss practical implications for architects

**Work**

- Interpret the approach as decision support rather than autonomous architectural authority.
- Discuss traceable requirement evidence, explicit pattern rationale, and ADR drafts as review aids.
- Incorporate expert feedback on usefulness, grounding, clarity, feasibility, and effort.
- Identify human-review checkpoints and unsafe uses.

**Deliverables**

- Practitioner implications subsection.

**Completion criteria**

- Recommendations are proportional to expert evidence and do not imply production readiness.

### Task 4.4 — Discuss research implications

**Work**

- Explain the value and limitations of requirement-grounded, pattern-by-pattern assessment.
- Discuss how the work relates architectural pattern recommendation to ADR generation.
- Identify follow-up experiments: additional systems, catalogs, models, prompt variants, expert-selected negatives/all-pattern baselines, and cost/latency evaluation.
- Include spec-driven development or other future directions only when connected to the study findings.

**Deliverables**

- Research implications and future work subsection.

**Completion criteria**

- Future work is clearly separated from contributions already evaluated.

---

## Phase 5 — Threats to Validity

**Section produced:** `sections/06-threats-to-validity.tex`

**Dependency:** Final Methodology and Results.

### Task 5.1 — Address construct validity

**Work**

- Discuss whether user stories and acceptance criteria contain enough architectural information.
- Discuss the operational definitions of applicability, RAG overlap, and ADR quality.
- Discuss whether Q1–Q5 adequately capture the intended expert constructs.
- Explain limitations of evaluating only LLM-positive pairs.

**Deliverables**

- Construct-validity subsection with concrete mitigations.

### Task 5.2 — Address internal validity

**Work**

- Discuss prompt design, single-model configuration, model nondeterminism, translation, manual corrections, retry handling, and potential evaluator learning/fatigue.
- Explain safeguards: independent calls, structured outputs, evidence references, immutable outputs, audit trails, routing, and predeclared analysis.

**Deliverables**

- Internal-validity subsection.

### Task 5.3 — Address external validity

**Work**

- Discuss the small industrial sample, four systems, 12 stories, 70-pattern catalog, language/context, organization-specific requirements, and expert sample.
- Avoid population-wide claims about AI-enabled systems or professional architects.

**Deliverables**

- External-validity subsection.

### Task 5.4 — Address conclusion and reproducibility validity

**Work**

- Discuss descriptive/exploratory analysis, sample size, ordinal responses, multiple aggregation levels, and agreement limits.
- Discuss external API/model evolution and unpinned RAG model revisions.
- Explain the preserved artifacts and deterministic compilation strengths.

**Deliverables**

- Conclusion/reliability subsection.

**Completion criteria for Phase 5**

- Every major design limitation has both an impact statement and, where applicable, a mitigation.
- Threats are not written as generic boilerplate.

---

## Phase 6 — Background and Related Work

**Section produced:** `sections/02-background-related-work.tex`

**Dependency:** Stable study contribution and Discussion positioning.

### Task 6.1 — Establish necessary background

**Work**

- Define architecture design decisions and ADRs.
- Introduce architectural/design patterns for AI-enabled systems.
- Explain LLM assistance in software architecture and distinction between retrieval and generation.
- Keep background limited to concepts needed to understand the method.

**Deliverables**

- Concise Background subsection with verified foundational citations.

### Task 6.2 — Synthesize LLM-assisted software architecture research

**Work**

- Compare studies on architectural knowledge, design-concept identification, ADD-assisted design, and architecture assistants.
- Extract differences in inputs, model role, outputs, and human oversight.
- Cite original publications, not only PDFs or worksheet notes.

**Deliverables**

- Thematic related-work subsection.
- Verified BibTeX entries in `bibliography/references.bib`.

### Task 6.3 — Synthesize LLM-based ADR and design-rationale research

**Work**

- Compare prior ADR-generation and design-rationale studies with this requirement-and-pattern-grounded workflow.
- Discuss prompting, generated ADR fields, evaluation strategies, and known limitations.
- Avoid claiming novelty until a defensible comparison is complete.

**Deliverables**

- ADR-generation related-work subsection.

### Task 6.4 — Position against AI-system pattern research

**Work**

- Closely compare the CAIN 2026 “LLMs as Design Partners for AI-Based System Patterns” paper with ADR4AI.
- Explain whether the same researchers/artifacts are involved in third person to preserve double anonymity.
- Distinguish pattern generation/equivalence evaluation from requirement-specific pattern applicability and ADR generation.
- Include rule-based pattern-recognition work as a related but different task.

**Deliverables**

- Positioning subsection ending in the precise research gap.

**Completion criteria for Phase 6**

- Every citation is verified for title, authors, venue, year, pages, DOI/URL as appropriate.
- Related work is synthesized by research problem, not listed paper by paper.
- The final paragraph establishes the gap without overstating novelty.

---

## Phase 7 — Introduction

**Section produced:** `sections/01-introduction.tex`

**Dependency:** Stable RQs, results, contribution, and related-work gap.

### Task 7.1 — Motivate the problem

**Work**

- Explain why translating requirements for AI-enabled systems into architectural decisions is difficult.
- Motivate pattern reuse and ADR documentation without implying that LLMs solve the problem reliably.
- Establish the need for traceable, expert-reviewed decision support.

**Deliverables**

- Opening motivation and problem statement.

### Task 7.2 — Present the research gap and approach

**Work**

- Connect the Related Work gap to the implemented pipeline.
- Summarize requirement-grounded exhaustive applicability assessment, ADR generation, RAG comparison, and expert validation.
- Use one paragraph and the approach figure where helpful.

**Deliverables**

- Approach overview paragraph.

### Task 7.3 — State research questions and contributions

**Work**

- Present final RQs exactly as in Methodology.
- State only contributions supported by the final paper, such as:
  - a traceable requirement-to-pattern-to-ADR approach;
  - an empirical study over the bounded 840-pair design;
  - comparison with a frozen retrieval baseline; and
  - expert evidence about recommendations and ADR drafts.
- Include the reproducibility package as a contribution only if it is anonymized, curated, and available at submission.

**Deliverables**

- RQ and contribution paragraphs.

### Task 7.4 — Summarize results and paper organization

**Work**

- Add only the most important final quantitative findings.
- Avoid introducing unvalidated expert results or broad effectiveness claims.
- End with a compact paper roadmap if space permits.

**Deliverables**

- Complete Introduction.

**Completion criteria for Phase 7**

- Introduction claims match Results and Discussion exactly.
- Contributions are distinct from future work.

---

## Phase 8 — Conclusion

**Section produced:** `sections/07-conclusion.tex`

**Dependency:** Final Results and Discussion.

### Task 8.1 — Synthesize the study outcome

**Work**

- Restate the problem, approach, and strongest evidence in compact form.
- Summarize what is known from computational outputs and what expert validation adds.
- Avoid repeating the Abstract verbatim.

### Task 8.2 — State bounded implications and future work

**Work**

- Present the practical/research implication at the level supported by the data.
- Mention only the highest-priority future studies.
- End with a measured statement about LLM-supported architectural decision work, retaining human oversight.

**Deliverables**

- Complete Conclusion.

**Completion criteria**

- No new claims, citations, or results appear in the Conclusion.

---

## Phase 9 — Abstract

**Section produced:** `sections/00-abstract.tex`

**Dependency:** All substantive sections complete.

### Task 9.1 — Write the structured narrative

**Work**

- Cover context/problem, objective, method, results, and conclusion in one self-contained abstract.
- Include key denominators and the most informative final results.
- Mention expert validation only with final participant/evidence values.
- Avoid citations, unexplained abbreviations, promises, and future tense.

**Deliverables**

- Final Abstract within a concise conference-paper length.

**Completion criteria**

- Every number and claim is present and supported elsewhere in the paper.
- The Abstract reflects the paper's final contribution, not the initial project intention.

---

## Phase 10 — Artifact Availability and Open Science

**Section produced:** `sections/08-artifact-availability.tex`

**Dependency:** Submission artifact package prepared.

### Task 10.1 — Define the anonymized artifact package

**Work**

- Include only shareable, curated requirements, pattern data, prompts, code, stored outputs, deterministic compilers, analysis scripts, and documentation.
- Remove author identities, organization-identifying metadata, API response identifiers if sensitive, credentials, local paths, and repository history that breaks anonymity.
- Distinguish open artifacts from restricted expert/raw data and explain restrictions.

### Task 10.2 — Write the availability statement

**Work**

- Provide an anonymized review URL only when the package is actually available.
- State reproducibility limitations for external models and approximate retrieval.
- Plan a long-term DOI archive for the accepted version.

**Deliverables**

- Artifact Availability section.
- Verified anonymous artifact URL placeholder replaced before submission.

**Completion criteria**

- The paper and linked artifact do not reveal author identity.
- Every claimed artifact is present at the linked location.

---

## Phase 11 — LaTeX Assembly, Compliance, and Final Quality

**Files produced:** `main.tex`, `preamble.tex`, `metadata.tex`, `README.md`, `latexmkrc`, final tables/figures/bibliography.

**Dependency:** All writing phases.

### Task 11.1 — Assemble the IEEEtran project

**Work**

- Configure `main.tex`, section includes, bibliography style, PDF metadata, and anonymous author block.
- Keep packages minimal and IEEE-compatible.
- Add robust commands for IDs, model names, RQs, and study values.
- Document build commands in `latex-code/README.md`.

**Completion criteria**

- A clean checkout of `latex-code/` builds without accessing files outside the directory.

### Task 11.2 — Enforce traceability and internal consistency

**Work**

- Verify every table/figure is introduced, interpreted, and referenced.
- Check every number against its macro and evidence source.
- Check RQ wording across Introduction, Methodology, Results, and Discussion.
- Check consistent terminology: requirement case, pattern applicability, retrieved candidate, selected pair, generated ADR, and expert assessment.
- Search for `TBD`, `TODO`, draft comments, duplicated labels, broken references, and missing citations.

**Completion criteria**

- Zero unresolved placeholders or references.
- No inconsistent totals, denominators, or research-question wording.

### Task 11.3 — Enforce scientific-writing quality

**Work**

- Remove causal language unsupported by the study.
- Replace “proves,” “ground truth,” “validated,” and “effective” where evidence supports only descriptive or expert-assessed findings.
- Ensure Results report evidence and Discussion interprets it.
- Check that limitations accompany claims where needed.
- Perform an English technical edit for clarity, concision, and terminology.

**Completion criteria**

- Claims are calibrated to the design and evidence.
- Each paragraph has one clear function and avoids unnecessary repetition.

### Task 11.4 — Enforce double anonymity and policy compliance

**Work**

- Remove names, affiliations, acknowledgments, self-identifying repository links, and identifying PDF metadata.
- Refer to prior work by the authors in third person and retain normal citations.
- Verify artifact repository anonymity.
- Add any required generative-AI disclosure according to current ACM/IEEE/CAIN policy without naming the authors.
- Recheck the live CAIN 2027 call before submission.

**Completion criteria**

- No identity leak remains in source, compiled PDF, metadata, figures, acknowledgments, or artifact links.

### Task 11.5 — Validate bibliography and source integrity

**Work**

- Verify each BibTeX entry against the publisher or official record.
- Remove uncited entries and resolve missing citations.
- Check DOI and URL formatting.
- Ensure all copied/adapted figures, scales, and definitions have appropriate attribution and permissions.

**Completion criteria**

- All citations compile and every reference is accurate.

### Task 11.6 — Validate build and page budget

**Work**

- Build with a reproducible LaTeX command such as `latexmk -pdf main.tex`.
- Treat LaTeX errors, undefined references, multiply defined labels, and missing citations as blocking.
- Inspect overfull/underfull boxes and figure/table legibility.
- Confirm IEEEtran 10pt conference format.
- Confirm no more than 10 content pages plus 2 reference pages.
- Reduce length by removing redundancy and low-value content before shrinking figures or typography.

**Completion criteria**

- Clean final build with no blocking warnings.
- Compliant page count and readable two-column layout.

### Task 11.7 — Conduct final evidence and reviewer-readiness checks

**Work**

- Have one researcher independently audit all quantitative claims.
- Have one software-architecture researcher review methodological correctness.
- Have one uninvolved reader assess clarity and contribution.
- Resolve review comments while preserving the frozen evidence.
- Produce the submission PDF from the reviewed source tree.

**Completion criteria**

- All high-priority review findings are resolved or explicitly accepted with rationale.
- The submitted PDF hash and corresponding source snapshot are recorded.

## 5. Phase dependency summary

```text
Phase 1 Methodology
  ├── Phase 2 Existing Results
  └── Expert study execution
        └── Phase 3 Expert Results
              ├── Phase 4 Discussion
              └── Phase 5 Threats to Validity
                    └── Phase 6 Background and Related Work
                          └── Phase 7 Introduction
                                └── Phase 8 Conclusion
                                      └── Phase 9 Abstract

Phase 10 Artifact Availability depends on the curated submission artifact.
Phase 11 Assembly and validation runs throughout, with final checks after all phases.
```

## 6. Definition of done

The paper-writing task is complete only when:

- every source file needed to build the paper is under `latex-code/`;
- the paper builds in IEEEtran 10pt conference format;
- the final structure includes Abstract, Introduction, Background and Related Work, Methodology, Results, Discussion, Threats to Validity, Conclusion, and Artifact Availability;
- all computational values are traceable to frozen official artifacts;
- all expert values are traceable to a frozen response dataset and reproducible analysis;
- no expert-result placeholder remains;
- RAG overlap is not misrepresented as applicability accuracy;
- LLM classifications are not misrepresented as ground truth;
- all citations and bibliography records are verified;
- the PDF and linked artifact are double-anonymous;
- the content fits 10 pages plus at most 2 pages of references;
- the live CAIN 2027 requirements have been rechecked; and
- a final independent evidence audit has passed.
