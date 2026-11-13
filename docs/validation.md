# Validation record — 2026-11-13

## Verified locally

- Ruff passes; mypy passes for all 12 package modules.
- Twelve unittest cases pass, including actual LangGraph execution/resume, actual FAISS dense/hybrid retrieval with deterministic test embeddings, company filters, citation rejection, failure handling, cache/retry budgets, collection quotas and credential-free snapshots.
- Wheel and source distribution build successfully. Both include INTRODUCTION.md with the license notices; neither includes .env or generated corpora.
- Commitizen validates the feature-branch commit messages. The uv lockfile defines the reproducible local/CI environment.
- The earlier viewer AppTest passed with zero exceptions. Local server/browser validation is now possible and remains separate from that earlier test.

## Live source collection

Collected 30 pages for the three-company demo using 15 Basic search calls on the free tier. Three source-fetch errors were recorded. The source snapshot and runtime wheel were uploaded to a private Kaggle Dataset after a credential scan. Neither dataset nor notebook contains the Tavily API key. Raw collected sources stay outside Git.

## Remote checks

The repository is now published and a feature PR will run the locked validation workflow. The first bootstrap main workflow exposed the lint/type issues fixed in this feature branch; it is not a successful CI result.

The private Kaggle notebook was submitted with T4 GPU, Internet, and a 3600-second limit. Completion, model inference, real-source retrieval behavior and report quality are pending. A submitted run is not proof of a successful run.

## Remaining release acceptance

Real-source retrieval labels, a held-out BM25/dense/hybrid benchmark, review of at least 30 claim/source pairs, measured GPU runtime and the demo video remain required before releasing v0.1.0. Synthetic fixture scores must not be presented as research quality on a CV.
