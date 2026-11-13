# Validation record — 2026-11-13

## Verified locally

- Ruff passes; mypy passes for all 12 package modules.
- Fourteen unittest cases pass, including actual LangGraph execution/resume, actual FAISS dense/hybrid retrieval with deterministic test embeddings, company filters, citation rejection, failure handling, cache/retry budgets, collection quotas and credential-free snapshots.
- Wheel and source distribution build successfully. Both include INTRODUCTION.md with the license notices; neither includes .env or generated corpora.
- Commitizen validates the feature-branch commit messages. The uv lockfile defines the reproducible local/CI environment.
- The earlier viewer AppTest passed with zero exceptions. Headless Chrome also rendered the local viewer and synthetic-data notice successfully.

## Live source collection

The initial collection saved 30 pages with 15 Basic calls. Revised criterion-focused queries and balanced quotas produced 27 pages with 30 cumulative Basic calls; six fetch failures were recorded. The 30-attempt collection budget was retained across revisions. The source snapshot and runtime wheel were uploaded to a private Kaggle Dataset after a credential scan. Neither dataset nor notebook contains the Tavily API key. Raw collected sources stay outside Git.

## Remote checks

PR #2 merged after both feature checks passed. The locked workflow also passed on main. Required quality checks and linear history protect main; no external reviewer is required for the solo workflow.

Private Kaggle version 1 completed on Tesla T4, producing 29 claim records and 129 chunks in 623.6 seconds of pipeline time. Three invalid claim records became unknowns; execution is not semantic validation. Version 2 is running the revised retrieval, source allocation and citation handling. Actual runtime versions and the separate 20-question, agent-curated retrieval diagnostic are recorded in docs/experiments/.

## Remaining release acceptance

Independent review of the diagnostic labels, human review of at least 30 claim/source pairs, a review of revised-run artifacts, and the demo video remain required before releasing v0.1.0. Synthetic fixture scores must not be presented as research quality on a CV.
