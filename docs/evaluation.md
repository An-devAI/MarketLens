# Evaluation protocol

Offline examples are SYNTHETIC fixtures. They validate plumbing and must never be presented as company facts or production quality measurements.

Build a frozen real-source corpus, then manually label 30 answerable queries with relevant chunk IDs: 10 dev and 20 held-out test. Add five unanswerable cases with empty relevant_ids. Questions are JSONL with query, company, relevant_ids and split. Tune only on dev. Evaluate BM25, dense and hybrid against identical evidence with `marketlens evaluate CORPUS QUESTIONS --all-modes --split test`.

Targets: Recall@5 >= 0.80; 100% reference integrity; >=90% factual claim citation coverage; >=90% human-reviewed claims supported by sources. Record at least 30 reviewed claims with verdict supported/unsupported/unclear and rationale. Unknown cases require manual abstention review and must not be counted in answerable retrieval averages. Also report unknown cell rate to prevent a system from achieving apparent precision by refusing everything.

Inspect claim meaning, scope, pricing currency/cadence/seats, source conflicts, age and inferred conclusions. Quote matching alone is not entailment. The generating model is not the sole judge. Store live results separately from synthetic results and include model/dependency versions, corpus hash, date, tokens, search calls, GPU and elapsed time.

Real-source labels, human verdicts, GPU timing and live benchmark results are pending. No production performance is claimed by this initial implementation.
