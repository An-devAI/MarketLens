import unittest
from types import SimpleNamespace

from marketlens.audit import assess_claims, audit_report, evaluate_review, report_digest
from marketlens.models import (
    AssessmentBatch,
    Claim,
    ClaimAssessment,
    Company,
    ReportBundle,
    ResearchRequest,
)
from marketlens.report import report_summary
from marketlens.retrieval import chunk_document
from marketlens.source_policy import source_decision


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.company = Company(name='Asana', website='https://asana.com')
        self.evidence = chunk_document('Asana', 'https://asana.com/apps', 'Apps',
                                       'Alpha sends alerts. Beta creates tasks.', 'today')
        self.claim = Claim(company='Asana', criterion='integrations', text='Alpha creates tasks.',
                           quote='Alpha sends alerts. Beta creates tasks.',
                           evidence_ids=[self.evidence[0].id])

    def test_summary_distinguishes_records_from_covered_cells(self):
        unknown = self.claim.model_copy(update={'criterion': 'product', 'kind': 'unknown'})
        inference = self.claim.model_copy(update={'kind': 'inference'})
        bundle = ReportBundle(request=ResearchRequest(companies=[self.company, Company(name='B', website='https://b.example')]),
                              claims=[self.claim, inference, unknown], evidence=self.evidence, warnings=[], manifest={}, status='partial')
        summary = report_summary(bundle)
        self.assertEqual((summary['records'], summary['retained'], summary['unknown']), (3, 2, 1))
        self.assertEqual((summary['covered_cells'], summary['total_cells']), (1, 10))

    def test_review_metrics_reject_wrong_labels_and_new_claims(self):
        bundle = ReportBundle(request=ResearchRequest(companies=[self.company, Company(name='B', website='https://b.example')]),
                              claims=[self.claim], evidence=self.evidence, warnings=[], manifest={}, status='partial')
        labels = {'report_sha256': report_digest(bundle), 'records': [{'record': 0, 'verdict': 'unsupported'}]}
        withheld = self.claim.model_copy(update={'kind': 'unknown', 'evidence_ids': [], 'quote': ''})
        reviewed = bundle.model_copy(update={'claims': [withheld]})
        metrics = evaluate_review(bundle, reviewed, labels)
        self.assertIsNone(metrics['after']['agent_supported_retained_rate'])
        self.assertEqual(metrics['flagged_records_withheld'], 1)
        with self.assertRaisesRegex(ValueError, 'different report'):
            evaluate_review(bundle, reviewed, dict(labels, report_sha256='wrong'))
        rewritten = bundle.model_copy(update={'claims': [self.claim.model_copy(update={'text': 'A new assertion'})]})
        with self.assertRaisesRegex(ValueError, 'must not rewrite'):
            evaluate_review(bundle, rewritten, labels)

    def test_source_policy_uses_domain_boundaries_and_page_purpose(self):
        for url in ['https://forum.asana.com/topic', 'https://community.asana.com/a',
                    'https://asana.com.evil.test/a', 'https://evil-asana.com/a',
                    'https://asana.com/jobs/engineer', 'http://asana.com/apps']:
            self.assertFalse(source_decision(url, self.company.website).allowed, url)
        self.assertTrue(source_decision('https://help.asana.com/apps', self.company.website).allowed)
        url = 'https://www.notion.com/templates/company-mission'
        self.assertFalse(source_decision(url, 'https://notion.com', 'positioning').allowed)
        self.assertTrue(source_decision(url, 'https://notion.com', 'product').allowed)

    def test_matching_quote_does_not_override_unsupported_assessment(self):
        assessor = SimpleNamespace(assess=lambda *args: AssessmentBatch(assessments=[
            ClaimAssessment(record=0, verdict='unsupported', reason='Task creation belongs to Beta, not Alpha')]))
        result, decisions = assess_claims([self.claim], self.evidence, [self.company], assessor)
        self.assertEqual(result[0].kind, 'unknown')
        self.assertEqual(decisions[0]['stage'], 'model_assessment')
        self.assertEqual(self.claim.kind, 'fact')

    def test_community_source_is_withheld_before_model_call(self):
        evidence = [e.model_copy(update={'url': 'https://forum.asana.com/t/prices'}) for e in self.evidence]
        def fail(*args):
            self.fail('The assessor must not be called for an ineligible source')
        result, decisions = assess_claims([self.claim], evidence, [self.company], SimpleNamespace(assess=fail))
        self.assertEqual(result[0].kind, 'unknown')
        self.assertEqual(decisions[0]['stage'], 'source_or_integrity')

    def test_missing_duplicate_and_unexpected_record_ids_fail_closed(self):
        supported = ClaimAssessment(record=0, verdict='supported', reason='fixture')
        for results in [[], [supported, supported], [supported.model_copy(update={'record': 9})]]:
            assessor = SimpleNamespace(assess=lambda *args: AssessmentBatch(assessments=results))
            output, decisions = assess_claims([self.claim], self.evidence, [self.company], assessor)
            self.assertEqual(output[0].kind, 'unknown')
            self.assertEqual(decisions[0]['verdict'], 'uncertain')

    def test_assessor_failure_retains_reason_without_accepting_claim(self):
        def fail(*args):
            raise RuntimeError('unavailable')
        output, decisions = assess_claims([self.claim], self.evidence, [self.company], SimpleNamespace(assess=fail))
        self.assertEqual(output[0].kind, 'unknown')
        self.assertIn('RuntimeError', decisions[0]['reason'])

    def test_report_assessment_preserves_global_record_indices(self):
        second = self.claim.model_copy(update={'criterion': 'product'})
        assessor = SimpleNamespace(assess=lambda records, *args: AssessmentBatch(assessments=[
            ClaimAssessment(record=item['record'], verdict='supported', reason='fixture') for item in records]))
        bundle = ReportBundle(request=ResearchRequest(companies=[self.company, Company(name='B', website='https://b.example')]),
                              claims=[self.claim, second], evidence=self.evidence, warnings=[], manifest={}, status='partial')
        result, decisions = audit_report(bundle, assessor)
        self.assertEqual([item['record'] for item in decisions], [0, 1])
        self.assertEqual(len(result.claims), 2)
        self.assertIn('human review pending', result.manifest['semantic_review'])
