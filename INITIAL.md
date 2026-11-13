# FEATURE

Build a company research tool for an AI Engineer portfolio. Given 2–3 named companies and HTTPS websites, gather public pages, retrieve evidence, compare product, pricing, customers, integrations and positioning, and export an English report with inspectable citations. Research executes on Kaggle; local viewing needs no model.

# EXAMPLES

- examples/request.json: default research input.
- src/marketlens/demo.py: explicitly synthetic provider implementations for offline execution.
- tests/test_core.py: citation rejection, retrieval filters, failure and resume expectations.

# DOCUMENTATION

Read AGENTS.md, PRPs/company-research.md, docs/development.md, docs/evaluation.md and INTRODUCTION.md as appropriate to the change.

# OTHER CONSIDERATIONS

Zero paid LLM budget. Search is free tier with hard call limits. Claims need retained source evidence. Currency, billing cadence and seat constraints must remain attached to pricing. Missing evidence produces unknowns, not invented facts. Provenance belongs only in the introduction file. Use Codex with repository instructions; no tool-specific slash commands are required.
