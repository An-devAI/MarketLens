# Evaluation protocol

Offline examples are SYNTHETIC fixtures. They validate plumbing and must never be presented as company facts or production quality measurements.

Build a frozen real-source corpus, then manually label 30 answerable queries with relevant chunk IDs: 10 dev and 20 held-out test. Add five unanswerable cases with empty relevant_ids. Questions are JSONL with query, company, relevant_ids and split. Tune only on dev. Evaluate BM25, dense and hybrid against identical evidence with `marketlens evaluate CORPUS QUESTIONS --all-modes --split test`.

Targets: Recall@5 >= 0.80; 100% reference integrity; >=90% factual claim citation coverage; >=90% human-reviewed claims supported by sources. Record at least 30 reviewed claims with verdict supported/unsupported/unclear and rationale. Unknown cases require manual abstention review and must not be counted in answerable retrieval averages. Also report unknown cell rate to prevent a system from achieving apparent precision by refusing everything.

Inspect claim meaning, scope, pricing currency/cadence/seats, source conflicts, age and inferred conclusions. Quote matching alone is not entailment. The generating model is not the sole judge. Store live results separately from synthetic results and include model/dependency versions, corpus hash, date, tokens, search calls, GPU and elapsed time.

Real-source labels, human verdicts, GPU timing and live benchmark results are pending. No production performance is claimed by this initial implementation.

## Initial real-source diagnostic

The checked-in examples/real-questions.jsonl contains 10 Notion development questions, 20 Asana/monday.com test questions and 5 unanswerable controls. Passages were inspected and labels were curated by the coding agent, not a human expert. Each question has one known supporting chunk; judgments are not exhaustive. Paraphrases are kept within the same company split. Do not tune against these test labels or describe them as an independently curated benchmark.

Rebuild the corpus from the exact private snapshot with `python scripts/build_benchmark_corpus.py SNAPSHOT --output outputs/label-corpus.jsonl`, then run `marketlens evaluate outputs/label-corpus.jsonl examples/real-questions.jsonl --all-modes --output outputs/diagnostic.json`. Verify the source and corpus hashes in docs/experiments/retrieval-diagnostic.json before comparing scores. The raw website corpus remains private; recollecting live pages can change chunk identifiers and invalidate labels.

Measured labeled-chunk Recall@5: BM25 0.75, dense 0.90, hybrid 0.95 on n=20. With one positive label per query this is also a known-positive hit rate. These retrieval scores do not establish report faithfulness or generator abstention. Unknown controls are provided for subsequent generator review, not counted as passed cases.
