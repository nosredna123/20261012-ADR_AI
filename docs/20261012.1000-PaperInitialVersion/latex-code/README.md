# Task 1.1 review draft

This is a minimal IEEEtran scaffold for reviewing the research questions and
claim boundaries. It is not the full manuscript. Later sections, bibliography,
data macros, and final metadata configuration have not been implemented.

## Build

From this directory, run:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The build requires a local TeX installation with IEEEtran and latexmk. The
configuration writes the review PDF and intermediate files to `build/`.
The LaTeX build needs no external datasets, API access, or data processing.

## Review scope

- [Methodology fragment](sections/03-methodology.tex): protocol scope,
  questionnaire constructs, interpretation limits, and the claim-to-evidence
  matrix in source comments.
- [Research-question table](tables/research-questions.tex): question wording,
  units, evidence, and intended analysis.

RQ3 is defined for the prepared questionnaire. Preliminary responses have been
reported by the researcher but have not been supplied as a consolidated dataset
for this task. No expert finding or statistic is asserted in this draft.
