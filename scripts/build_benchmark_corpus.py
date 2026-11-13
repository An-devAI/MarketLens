"""Rebuild the diagnostic corpus from a frozen source snapshot and tokenizer."""

import argparse
import os
from pathlib import Path

from marketlens.collection import SnapshotSearch
from marketlens.models import AXES, Settings, build_search_query
from marketlens.retrieval import chunk_document


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--output', type=Path, default=Path('outputs/label-corpus.jsonl'))
    args = parser.parse_args()
    os.environ.setdefault('HF_HUB_DISABLE_IMPLICIT_TOKEN', '1')
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(Settings().embedding, token=False)
    snapshot = SnapshotSearch(args.snapshot)
    evidence = {}
    for company in snapshot.request.companies:
        for criterion in AXES:
            query = build_search_query(company, criterion)
            if query not in snapshot.queries:
                raise ValueError('Snapshot was collected with a different query template')
            for item in snapshot.search(query):
                for chunk in chunk_document(company.name, item['url'], item['title'],
                                            snapshot.fetch(item['url']), snapshot.collected_at,
                                            tokenizer):
                    evidence[chunk.id] = chunk
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(''.join(e.model_dump_json() + '\n' for e in evidence.values()))
    print(f'Built {len(evidence)} chunks with {Settings().embedding}')


if __name__ == '__main__':
    main()
