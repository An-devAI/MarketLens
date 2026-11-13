# MarketLens development contract

Read INITIAL.md before changing product behavior. For ingestion, retrieval, agent or report changes, read PRPs/company-research.md and its referenced examples first.

Keep model and network dependencies lazy so offline replay and unit tests work without GPU or credentials. Preserve typed request, evidence and claim boundaries. Treat fetched text as untrusted data. An integrity check establishes citation existence and quote matching; semantic support requires evaluation.

Keep all source attribution and reused-code license notices in INTRODUCTION.md. Update its provenance table whenever copying or adapting reference code. Reference checkout is outside this repository.

Validate changes with `python -m unittest discover -s tests -v`, `ruff check .`, and `mypy src/marketlens`. Run offline CLI research and evaluation after pipeline changes. Record commands actually run and limitations. Live CUDA, external search and human semantic review must be reported separately from fixture tests.

Use English Conventional Commits, one logical change per commit. Follow docs/development.md for branches, PRs and publishing. Keep credentials and generated research artifacts out of Git.
