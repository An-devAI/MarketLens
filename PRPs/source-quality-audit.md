# Source quality and fixed-report assessment

## Goal
Keep source eligibility, quote integrity, contextual model assessment and independent human review distinct. An exact quote must not certify an unsupported entity, price cadence or neighboring app capability.

## Context
Read the typed assessment models, source_policy.py, audit.py and tests/test_audit.py before changing this flow. The frozen review in docs/experiments/claim-review-v2-agent.json contains agent judgments, not human gold labels. Follow docs/evaluation.md when reporting results.

## Invariants
- Admit HTTPS URLs within the requested vendor domain boundary; withhold community and recruiting URLs. A vendor URL is not proof of authorship or factual truth.
- Keep unknowns and rejection reasons. Failed, missing, duplicate or unexpected model judgments withhold the finding.
- Fixed-report audit preserves record positions and cannot rewrite or generate assertions. Verify parent report digest before comparing review labels.
- Keep frozen agent judgments out of the assessor's input. Report coverage, retained findings and disagreements together; an empty retained set has an undefined supported-retained rate.
- Report counters are derived with report_summary. Never substitute model-assisted or coding-agent judgments for human acceptance.

## Validation
Run Ruff, mypy, unittest discovery and the offline CLI demo/evaluation with a fresh output folder. Build the package, run notebooks/audit on the private frozen report, and record wheel/report hashes and actual outcomes. The dataset and notebook must contain no API key or reference verdicts.

## Acceptance
Regression tests reject cross-domain/community inputs, mixed-application capability attribution when the assessor flags it, invalid assessment record mappings, rewritten claims and wrong report labels. A real CUDA audit must complete before claiming the assessor integration is verified. Human review remains a separate release gate.
