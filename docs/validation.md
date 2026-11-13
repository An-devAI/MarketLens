# Validation record — 2026-11-13

## Verified locally

- Ruff passes; mypy passes for all 12 package modules.
- Twenty-three unittest cases pass, including actual LangGraph execution/resume, actual FAISS dense/hybrid retrieval with deterministic test embeddings, company filters, citation rejection, failure handling, cache/retry budgets, collection quotas and credential-free snapshots.
- Wheel and source distribution build successfully. Both include INTRODUCTION.md with the license notices; neither includes .env or generated corpora.
- Commitizen validates the feature-branch commit messages. The uv lockfile defines the reproducible local/CI environment.
- The earlier viewer AppTest passed with zero exceptions. Headless Chrome also rendered the local viewer and synthetic-data notice successfully.

## Live source collection

The initial collection saved 30 pages with 15 Basic calls. Revised criterion-focused queries and balanced quotas produced 27 pages with 30 cumulative Basic calls; six fetch failures were recorded. The 30-attempt collection budget was retained across revisions. The source snapshot and runtime wheel were uploaded to a private Kaggle Dataset after a credential scan. Neither dataset nor notebook contains the Tavily API key. Raw collected sources stay outside Git.

## Remote checks

PR #2 merged after both feature checks passed. The locked workflow also passed on main. Required quality checks and linear history protect main; no external reviewer is required for the solo workflow.

Private Kaggle version 1 completed on Tesla T4, producing 29 claim records and 129 chunks in 623.6 seconds of pipeline time. Three invalid claim records became unknowns; execution is not semantic validation. Version 2 also completed: 30 records, 200 chunks, 659.1 seconds; 22 records retained and 8 unknown, covering 12/15 cells. The public example contains 12 agent-curated excerpt claims and three unknown cells, not the raw model report. Actual runtime versions and the separate 20-question, agent-curated retrieval diagnostic are recorded in docs/experiments/.

## Remaining release acceptance

Independent review of the diagnostic labels, human review of at least 30 claim/source pairs, and independent review of revised-run artifacts remain required before releasing v0.1.0. Synthetic fixture scores must not be presented as research quality on a CV.

## Demo artifacts

The public sample passes quote/identifier checks and a per-page quotation budget test. Four actual browser states were captured for a silent two-minute walkthrough, with optional English captions. The walkthrough holds each state for 30 seconds and is not a continuous screen recording. Raw model claims still require semantic review, especially community-source assertions, comparisons involving other vendors, attribution, and pricing conditions.

## Source-quality revision

Added vendor-domain URL eligibility, source-purpose exclusions, contextual model assessment, strict record mapping, fixed-report audit, and report-derived summary counters. Regression fixtures cover neighboring-app attribution, failed/ambiguous assessments and unchanged claim identity. Offline demo and metric plumbing pass using explicit synthetic sources. The fixed-report CUDA audit completed on T4 in 195.3 seconds. It preserved all 30 record positions, retained 13 findings, withheld 17, and covered 9/15 cells. Against frozen agent judgments it withheld eight flagged findings and lost one supported finding; four flagged findings remain. No human-accuracy claim is made.

Correction: the authoritative v2 kind counts are 12 fact, 10 inference and 8 unknown, totaling 30. Earlier narrative counts of 21 retained / 9 unknown were a counting error, not the artifact values. They were corrected to 22 retained / 8 unknown; draft release notes were corrected too.
