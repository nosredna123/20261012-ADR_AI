# Tasks 1.1--1.2 review draft

This is a minimal IEEEtran scaffold for reviewing the research questions and
claim boundaries and the industrial requirement sample. It is not the full
manuscript. Later sections, bibliography, result macros, and final metadata
configuration have not been implemented.

## Build

From this directory, run:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The build requires a local TeX installation with IEEEtran and latexmk. The
configuration writes the review PDF to `main.pdf` in this project-root
`latex-code/` directory, along with ignored intermediate build files.
The LaTeX build needs no external datasets, API access, or data processing.

## Review scope

- [Methodology fragment](sections/03-methodology.tex): protocol scope,
  questionnaire constructs, interpretation limits, and the claim-to-evidence
  matrix in source comments.
- [Research-question table](tables/research-questions.tex): question wording,
  units, evidence, and intended analysis.
- [Dataset table](tables/dataset-summary.tex) and
  [sample values](data/study-values.tex): generated from the validated source.
  Regeneration and verification are documented in
  [the processing README](../processing/README.md); the LaTeX build itself
  does not need the research data or processing scripts.

RQ3 is defined for the prepared questionnaire. Preliminary responses have been
reported by the researcher but have not been supplied as a consolidated dataset
for this task. No expert finding or statistic is asserted in this draft.
