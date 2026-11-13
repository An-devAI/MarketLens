# Company research implementation PRP

## Goal
A reproducible package that researches a named company set, retains evidence and exports a comparison bundle inspectable on CPU.

## Context
When changing source eligibility or claim assessment, read PRPs/source-quality-audit.md.
Read INITIAL.md, the typed models, demo providers and tests/test_core.py before editing the pipeline. Read INTRODUCTION.md before adapting reference code. Read docs/evaluation.md before interpreting benchmark results.

## Execution order
1. Validate request and budgets. Done when invalid input and duplicate companies are rejected.
2. Collect and cache public HTTPS pages. Done when duplicate text is indexed once and failures remain visible.
3. Retrieve company-scoped evidence. Done when BM25/dense/hybrid operate against the same corpus and labeled IDs.
4. Run bounded supervisor/researcher steps. Done when checkpoint identity prevents resuming a different request and budget survives resume.
5. Verify citations and render comparison. Done when invented IDs, mismatched companies and fabricated quotes become unknowns.
6. Run offline checks, then Kaggle live acceptance. Done when actual execution results and untested capabilities are recorded separately.

## Validation
`python -m unittest discover -s tests -v`
`ruff check .`
`mypy src/marketlens`
`marketlens research examples/request.json --demo --output outputs/demo`
`marketlens evaluate outputs/demo/corpus.jsonl examples/synthetic-questions.jsonl`

## Live acceptance
Run notebooks/kaggle_research.ipynb with Internet and GPU enabled. Confirm CUDA model load, structured plan/claim outputs, evidence integrity, saved artifacts and a resumed run. Human-review at least 30 claims. Use the quality targets in docs/evaluation.md; report actual values even when targets are missed.
