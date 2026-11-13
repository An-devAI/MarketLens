# Development and GitHub workflow

Use Python 3.11 or newer. Install with `uv pip install -e '.[dev]'`; research and viewer extras are separate. Install the commit hook using `git config core.hooksPath .githooks` after installing dev dependencies.

Write English commit messages as `type(scope): description`. Allowed types: feat, fix, refactor, test, docs, ci, build, perf, chore. Examples: `feat(rag): add company-scoped hybrid retrieval`, `fix(report): reject invented evidence identifiers`.

Create one Issue per feature with a concrete acceptance criterion. Branch as `feat/<issue-id>-<slug>` or `fix/<issue-id>-<slug>`. Push that branch and open a PR to this repository. Describe the problem, resulting behavior and checks. Use rebase merge after CI passes. Require status checks on main, with no mandatory reviewer for solo work. Bootstrap may be pushed directly once.

GitHub setup is pending authenticated network access. Run `gh auth login -h github.com`, then from the product directory `gh repo create MarketLens --public --source=. --remote=origin --push`. Use the GitHub UI to enable Issues and branch rules, and pin this repository on your profile. Create Issues for source collection, Kaggle inference, hybrid retrieval, citation integrity, evaluation and viewer improvements.

Before a release: run offline CI checks; complete the Kaggle smoke run and human review; update measured results and package version; create an annotated v0.1.0 tag and GitHub Release with report, metrics and demo video. Initial development version is 0.1.0.dev0; do not publish a completed release until live acceptance passes.

A separate reference checkout lives outside this repository. Fork/clone setup and provenance are documented only in INTRODUCTION.md. Do not commit model weights, API keys, caches, full checkpoint databases or generated live corpora. Use release artifacts for reviewed output bundles.
