# Validation record — 2026-11-13

## Executed

- Eight unittest cases passed: request validation, company-filtered retrieval, invalid citation rejection, offline end-to-end execution, resume/configuration identity, partial failures, retrieval metric calculation, source-state reducer and retry/cache budget handling (some cases cover multiple behaviors).
- Offline CLI generated a three-company synthetic report with 15 comparison cells; rerun resumed its checkpoint.
- Synthetic BM25 evaluation ran on 20 held-out fixture queries (Recall@5 and MRR@5 = 1.0). This only demonstrates metric plumbing: it is not a real-source research benchmark and is unsuitable as a CV quality claim.
- Streamlit AppTest executed the viewer against the generated bundle with zero exceptions.
- Python compileall passed. Source-attribution scan found no reference-project URLs or copyright-holder names outside the introduction document in the product tree.

## Environment limitations

Python dependencies used for executed checks were loaded from the existing local package cache. PyPI DNS resolution prevented installation of additional tooling. Ruff, mypy, Commitizen and package-build commands could not run locally; their workflow is configured but not yet verified in GitHub Actions.

The sandbox cannot bind a web-server socket. Viewer validation used AppTest rather than a browser session. No screenshot or video is claimed.

GitHub authentication is invalid and shell DNS access is unavailable. The product has local Conventional Commits; GitHub creation, push, Issues, PRs, branch rules and release are pending. The reference folder is a web-retrieved source snapshot, not an authenticated GitHub fork.

Live LangGraph orchestration, FAISS/dense retrieval and CUDA model inference are implemented but untested here because their dependencies and GPU runtime are unavailable. Real-source labels, human semantic review, dependency locking against a successful Kaggle environment and live performance measurements remain required before releasing v0.1.0 or using numeric quality claims on a CV.
