import tempfile
import unittest
from unittest.mock import patch

from marketlens.demo import DemoModel, DemoSearch
from marketlens.evaluation import evaluate
from marketlens.models import Claim, Company, ResearchRequest, Settings
from marketlens.pipeline import override_reducer, run_research
from marketlens.report import verify
from marketlens.retrieval import Retriever, chunk_document


def request():
    return ResearchRequest(companies=[Company(name="Notion", website="https://www.notion.com"),
                                      Company(name="Asana", website="https://asana.com")])


class CoreTests(unittest.TestCase):
    def test_validation(self):
        with self.assertRaises(ValueError):
            ResearchRequest(companies=[request().companies[0]] * 2)
        with self.assertRaises(ValueError):
            Company(name="Bad", website="http://localhost")

    def test_company_filter_and_empty_retrieval(self):
        a = chunk_document("A", "https://a.example", "a", "pricing monthly dollars", "today")
        b = chunk_document("B", "https://b.example", "b", "pricing monthly dollars", "today")
        r = Retriever(a+b)
        self.assertEqual([e.company for e in r.search("pricing", "B")], ["B"])
        self.assertEqual(r.search("absent", "A"), [])
        self.assertEqual(Retriever([]).search("pricing"), [])

    def test_citation_rejection(self):
        evidence = chunk_document("A", "https://a.example", "a", "A costs ten dollars", "today")
        claim = Claim(company="A", criterion="pricing", text="ten dollars",
                      evidence_ids=[evidence[0].id], quote="ten dollars")
        self.assertTrue(verify(claim, evidence)[1])
        for update in ({"evidence_ids": ["invented"]}, {"quote": "free forever"}, {"company": "B"}):
            self.assertFalse(verify(claim.model_copy(update=update), evidence)[1])

    def test_offline_pipeline_resume_and_identity(self):
        with tempfile.TemporaryDirectory() as output:
            cfg = Settings(retrieval="bm25", rounds=0)
            bundle = run_research(request(), cfg, output, DemoSearch(), DemoModel(), graph=False)
            self.assertEqual(bundle.status, "complete")
            self.assertEqual(len(bundle.claims), 10)
            search = DemoSearch()
            second = run_research(request(), cfg, output, search, DemoModel(), graph=False)
            self.assertEqual(second.claims, bundle.claims)
            self.assertEqual(search.calls, bundle.manifest["search_calls_total"])
            with self.assertRaises(ValueError):
                run_research(request(), Settings(retrieval="bm25", rounds=1), output,
                             search, DemoModel(), graph=False)

    def test_search_failure_is_partial(self):
        with tempfile.TemporaryDirectory() as output:
            search = DemoSearch()
            with patch.object(search, "search", side_effect=RuntimeError("quota")):
                bundle = run_research(request(), Settings(retrieval="bm25", rounds=0), output,
                                      search, DemoModel(), graph=False)
            self.assertEqual(bundle.status, "partial")
            self.assertTrue(bundle.warnings)
            self.assertTrue(all(c.kind == "unknown" for c in bundle.claims))

    def test_metric_definition(self):
        evidence = chunk_document("A", "https://a.example", "a", "pricing dollars", "today")
        questions = [{"query": "pricing", "company": "A", "relevant_ids": [evidence[0].id], "split": "test"}]
        self.assertEqual(evaluate(evidence, questions)["results"]["bm25"]["recall_at_5"], 1)
        questions[0]["relevant_ids"] = ["missing"]
        with self.assertRaises(ValueError):
            evaluate(evidence, questions)

    def test_override_reducer(self):
        self.assertEqual(override_reducer([1], [2]), [1, 2])
        self.assertEqual(override_reducer([1], {"type": "override", "value": [3]}), [3])


if __name__ == "__main__":
    unittest.main()
