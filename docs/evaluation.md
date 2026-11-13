# Evaluation protocol

Offline examples are SYNTHETIC fixtures. They validate plumbing and must never be presented as company facts or production quality measurements.

Build a frozen real-source corpus, then manually label 30 answerable queries with relevant chunk IDs: 10 dev and 20 held-out test. Add five unanswerable cases with empty relevant_ids. Questions are JSONL with query, company, relevant_ids and split. Tune only on dev. Evaluate BM25, dense and hybrid against identical evidence with `marketlens evaluate CORPUS QUESTIONS --all-modes --split test`.

Targets: Recall@5 >= 0.80; 100% reference integrity; >=90% factual claim citation coverage; >=90% human-reviewed claims supported by sources. Record at least 30 reviewed claims with verdict supported/unsupported/unclear and rationale. Unknown cases require manual abstention review and must not be counted in answerable retrieval averages. Also report unknown cell rate to prevent a system from achieving apparent precision by refusing everything.

Inspect claim meaning, scope, pricing currency/cadence/seats, source conflicts, age and inferred conclusions. Quote matching alone is not entailment. The generating model is not the sole judge. Store live results separately from synthetic results and include model/dependency versions, corpus hash, date, tokens, search calls, GPU and elapsed time.

Real-source diagnostic labels and GPU timing are recorded below. Independent human verdicts and production-quality validation remain pending.

## Initial real-source diagnostic

The checked-in examples/real-questions.jsonl contains 10 Notion development questions, 20 Asana/monday.com test questions and 5 unanswerable controls. Passages were inspected and labels were curated by the coding agent, not a human expert. Each question has one known supporting chunk; judgments are not exhaustive. Paraphrases are kept within the same company split. Do not tune against these test labels or describe them as an independently curated benchmark.

Rebuild the corpus from the exact private snapshot with `python scripts/build_benchmark_corpus.py SNAPSHOT --output outputs/label-corpus.jsonl`, then run `marketlens evaluate outputs/label-corpus.jsonl examples/real-questions.jsonl --all-modes --output outputs/diagnostic.json`. Verify the source and corpus hashes in docs/experiments/retrieval-diagnostic.json before comparing scores. The raw website corpus remains private; recollecting live pages can change chunk identifiers and invalidate labels.

Measured labeled-chunk Recall@5: BM25 0.75, dense 0.90, hybrid 0.95 on n=20. With one positive label per query this is also a known-positive hit rate. These retrieval scores do not establish report faithfulness or generator abstention. Unknown controls are provided for subsequent generator review, not counted as passed cases.

## Model-report review

The second GPU run retained 22 non-unknown records and rejected or withheld 8; it covered 12 of 15 company/criterion cells. Identifier/quote integrity is not sufficient for subject attribution: some retrieved sources are community posts or comparison articles discussing other vendors. Inspect whether every part of a claim is supported, whether pricing includes the right plan and cadence, and whether a vendor self-report is presented as such. The private `outputs/kaggle-v2/claim-review.csv` provides 30 rows with blank human verdicts; it must not be reported as a completed human audit.

The 20 diagnostic test-query retrieval inputs for Asana and monday.com are byte-for-byte identical in title/text/ID order between the 202-chunk diagnostic corpus and the 200-chunk second GPU corpus. Their difference is two duplicate Notion development chunks removed by the pipeline. The artifact hashes identify the exact evaluated corpus.

## Frozen source-quality regression review

`claim-review-v2-agent.json` records 30 coding-agent judgments against a canonical report digest: 10 supported in context, 7 partial, 4 inconclusive sources, 1 unsupported attribution and 8 original unknowns. Vendor statements are evaluated as source statements, not independently verified facts. This is a review of observed failures, not a new held-out human benchmark.

The private fixed-report audit excludes ineligible URLs first, then asks a bounded model assessor to check every proposition against the cited context. It cannot rewrite claims. The model is from the generator's family, so it cannot establish independent correctness. `evaluate_review` verifies input identity and compares retention against frozen agent labels, reporting both supported findings lost and flagged findings withheld. Unknown original records are not counted as successful factual claims; zero retained findings yield a null supported-retained rate.

The generated GPU input contains only a wheel and original report, not the frozen verdicts. Source and model rejection reasons are saved in assessments.json. Independent human acceptance remains issue #7.

### Fixed-report GPU result

The assessment completed on T4 in 195.3 seconds. The same 30 record positions were preserved; no new claims were generated. Source filtering withheld four community-derived assertions before model assessment. Final retention was 13 versus 22 originally; unknowns increased from 8 to 17 and coverage dropped from 12/15 to 9/15 cells.

Against the frozen coding-agent labels, retained supported findings changed from 10/22 to 9/13. Eight of twelve flagged records were withheld, one supported record was lost (record 7), and four flagged records remained (1, 17, 25, 28). The assessor caught the cross-app attribution case (16), the extra unsupported customer (14), and ambiguous pricing scope (22). It still missed several compound or weakly supported inferences. These observed-case diagnostics do not establish independent human accuracy. The generator and assessor use the same model family; the separate source-context agent review is also not human review.

The exact original-report digest and uploaded implementation-wheel hash accompany the result. Do not modify the frozen judgments to improve agreement after observing these outcomes. Issue #7 remains open.
