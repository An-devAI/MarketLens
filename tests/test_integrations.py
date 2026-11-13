import json
import tempfile
import unittest
from pathlib import Path

from marketlens.collection import SnapshotSearch, collect_sources
from marketlens.demo import DemoModel, DemoSearch
from marketlens.models import AXES, ResearchRequest, Settings
from marketlens.pipeline import run_research
from marketlens.report import render
from marketlens.retrieval import Retriever, chunk_document


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.request = ResearchRequest.model_validate_json(Path('examples/request.json').read_text())

    def test_langgraph_execution_and_resume(self):
        with tempfile.TemporaryDirectory() as output:
            settings = Settings(retrieval='bm25', rounds=0)
            first = run_research(self.request, settings, output, DemoSearch(), DemoModel())
            resumed = run_research(self.request, settings, output, DemoSearch(), DemoModel())
            self.assertEqual(first.claims, resumed.claims)
            self.assertEqual(first.status, 'complete')
            report = render(first)
            self.assertIn('[1](https://example.com/', report)
            self.assertNotIn(first.evidence[0].id, report)
            self.assertEqual(len(first.claims), 15)
            for claim in first.claims:
                self.assertIn(f'{claim.company} {claim.criterion}', claim.text)

    def test_collection_snapshot_is_credential_free(self):
        with tempfile.TemporaryDirectory() as output:
            data = collect_sources(self.request, output, search=DemoSearch())
            self.assertEqual(len(data['pages']), 15)
            search = SnapshotSearch(Path(output) / 'sources.json')
            query = next(iter(data['queries']))
            self.assertEqual(search.search(query), data['queries'][query])
            self.assertEqual(search.search('uncollected query'), [])
            self.assertEqual(search.calls, 0)
            self.assertTrue(search.fetch(data['queries'][query][0]['url']))

    def test_resume_rejects_changed_source_snapshot(self):
        with tempfile.TemporaryDirectory() as output:
            collect_sources(self.request, output, search=DemoSearch())
            snapshot = Path(output) / 'sources.json'
            run_path = str(Path(output) / 'research')
            settings = Settings(retrieval='bm25', rounds=0)
            run_research(self.request, settings, run_path, SnapshotSearch(snapshot), DemoModel())
            data = json.loads(snapshot.read_text())
            next(iter(data['pages'].values()))['text'] += ' Changed content.'
            snapshot.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'different request or configuration'):
                run_research(self.request, settings, run_path, SnapshotSearch(snapshot), DemoModel())

    def test_real_faiss_and_fusion_respect_company_scope(self):
        import numpy as np

        class Encoder:
            def encode(self, texts, normalize_embeddings=True):
                return np.asarray([[float('pricing' in text), float('product' in text)]
                                   for text in texts], dtype='float32')

        evidence = (chunk_document('A', 'https://a.example', 'a', 'pricing dollars', 'today')
                    + chunk_document('B', 'https://b.example', 'b', 'pricing dollars', 'today')
                    + chunk_document('A', 'https://a.example/features', 'features', 'product features', 'today'))
        for mode in ['dense', 'hybrid']:
            index = Retriever(evidence, mode, Encoder())
            found = index.search('pricing', 'A', k=1)
            self.assertEqual(found[0].id, evidence[0].id)
            self.assertEqual(index.search('pricing', 'unknown'), [])

    def test_each_criterion_receives_sources_before_quota_exhaustion(self):
        class ManyPages(DemoSearch):
            def search(self, query):
                item = super().search(query)[0]
                return [dict(item, url=item['url'] + f'/{i}') for i in range(5)]

        with tempfile.TemporaryDirectory() as output:
            data = collect_sources(self.request, output, search=ManyPages())
            self.assertEqual(len(data['pages']), 30)
            self.assertEqual(len(data['queries']), 3 * len(AXES))
            self.assertTrue(all(len(items) == 2 for items in data['queries'].values()))

    def test_company_document_budget_is_balanced(self):
        class ManyPages(DemoSearch):
            def search(self, query):
                item = super().search(query)[0]
                return [dict(item, url=item['url'] + f'/{i}') for i in range(10)]

        with tempfile.TemporaryDirectory() as output:
            data = collect_sources(self.request, output, Settings(max_documents=6), ManyPages())
            self.assertEqual(len(data['pages']), 6)
            for company in self.request.companies:
                self.assertEqual(sum(company.name in url for url in data['pages']), 2)
