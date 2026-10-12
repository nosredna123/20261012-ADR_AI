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
