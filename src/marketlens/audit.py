"""Source and model-assisted claim review, separate from human quality evaluation."""

import hashlib
import json
from collections import Counter, defaultdict
from typing import TypedDict

from .models import AXES, Claim
from .report import report_summary, verify
from .source_policy import POLICY_VERSION, source_decision


class AuditDecision(TypedDict):
    record: int
    verdict: str
    stage: str
    reason: str


def report_digest(bundle):
    return hashlib.sha256(json.dumps(bundle.model_dump(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def assess_claims(claims, evidence, companies, assessor, brief=''):
    """Fail closed on missing, duplicate, or mismatched assessment records."""
    sources = {e.id: e for e in evidence}
    websites = {c.name: c.website for c in companies}
    output: list[Claim] = []
    decisions: list[AuditDecision] = []
    pending: list[dict] = []
    for index, claim in enumerate(claims):
        checked, integrity = verify(claim, evidence)
        output.append(checked)
        reason = None
        if claim.kind == 'unknown':
            reason = 'No finding was available for assessment'
        elif not integrity:
            reason = 'Quote or citation integrity failed'
        elif claim.company not in websites:
            reason = 'Company is outside the requested comparison'
        else:
            for eid in claim.evidence_ids:
                policy = source_decision(sources[eid].url, websites[claim.company], claim.criterion)
                if not policy.allowed:
                    reason = policy.reason
                    break
        if reason:
            decisions.append({'record': index, 'verdict': 'withheld', 'stage': 'source_or_integrity', 'reason': reason})
        else:
            pending.append({'record': index, 'claim': claim.model_dump()})
    if pending:
        try:
            result = assessor.assess(pending, evidence, brief)
            by_record = defaultdict(list)
            for item in result.assessments:
                by_record[item.record].append(item)
            expected = {item['record'] for item in pending}
            unexpected = bool(set(by_record) - expected)
            for item in pending:
                index = item['record']
                findings = by_record[index]
                if not unexpected and len(findings) == 1:
                    finding = findings[0]
                    decisions.append({'record': index, 'verdict': finding.verdict,
                                      'stage': 'model_assessment', 'reason': finding.reason})
                else:
                    decisions.append({'record': index, 'verdict': 'uncertain',
                                      'stage': 'model_assessment', 'reason': 'Missing, duplicate or unexpected assessment record'})
        except Exception as exc:
            decisions.extend({'record': item['record'], 'verdict': 'uncertain',
                              'stage': 'model_assessment', 'reason': f'Assessor unavailable: {type(exc).__name__}'} for item in pending)
    for decision in decisions:
        if decision['verdict'] != 'supported':
            original = claims[decision['record']]
            output[decision['record']] = Claim(company=original.company, criterion=original.criterion,
                                             text='Insufficient reviewed evidence', kind='unknown')
    return output, sorted(decisions, key=lambda item: item['record'])


def audit_report(bundle, assessor):
    """Reassess fixed claims without rewriting or re-generating them."""
    grouped = defaultdict(list)
    for index, claim in enumerate(bundle.claims):
        grouped[(claim.company, claim.criterion)].append((index, claim))
    claims, decisions = list(bundle.claims), []
    for group in grouped.values():
        for start in range(0, len(group), 2):
            batch = group[start:start + 2]
            reviewed, findings = assess_claims([c for _, c in batch], bundle.evidence,
                                               bundle.request.companies, assessor, bundle.request.brief)
            for (index, _), claim in zip(batch, reviewed, strict=True):
                claims[index] = claim
            for finding in findings:
                decisions.append(dict(finding, record=batch[finding['record']][0]))
    covered = {(c.company, c.criterion) for c in claims if c.kind != 'unknown'}
    manifest = dict(bundle.manifest, parent_report_sha256=report_digest(bundle),
                    assessment_summary=dict(Counter(d["verdict"] for d in decisions)),
                    source_policy=POLICY_VERSION,
                    semantic_review='model-assisted; independent human review pending',
                    assessor_model_revision=getattr(assessor, 'model_revision', None),
                    assessment_input_tokens=getattr(assessor, 'input_tokens', 0),
                    assessment_output_tokens=getattr(assessor, 'output_tokens', 0))
    result = bundle.model_copy(update={'claims': claims, 'manifest': manifest,
        'status': 'complete' if len(covered) == len(bundle.request.companies) * len(AXES) else 'partial'})
    result.manifest['reviewed_summary'] = report_summary(result)
    return result, sorted(decisions, key=lambda item: item['record'])


def evaluate_review(original, reviewed, labels):
    """Measure retention against frozen agent judgments, not human accuracy."""
    if labels['report_sha256'] != report_digest(original):
        raise ValueError('Review labels belong to a different report')
    records = labels['records']
    if sorted(item['record'] for item in records) != list(range(len(original.claims))):
        raise ValueError('Review labels must cover every original record exactly once')
    if len(original.claims) != len(reviewed.claims):
        raise ValueError('The reviewed report must preserve record positions')
    for before, after in zip(original.claims, reviewed.claims, strict=True):
        if (before.company, before.criterion) != (after.company, after.criterion):
            raise ValueError('Claim identity changed during assessment')
        if after.kind != 'unknown' and after.model_dump() != before.model_dump():
            raise ValueError('Assessment may withhold claims, but must not rewrite or generate them')
    before_ids = {i for i, c in enumerate(original.claims) if c.kind != 'unknown'}
    after_ids = {i for i, c in enumerate(reviewed.claims) if c.kind != 'unknown'}
    supported = {item['record'] for item in records if item['verdict'] == 'supported'}
    flagged = before_ids - supported
    def score(ids):
        count = len(ids & supported)
        return {'retained': len(ids), 'agent_supported_retained': count,
                'agent_supported_retained_rate': count / len(ids) if ids else None}
    return {'parent_report_sha256': report_digest(original),
            'before': score(before_ids), 'after': score(after_ids),
            'original_summary': report_summary(original), 'reviewed_summary': report_summary(reviewed),
            'flagged_records_withheld': len(flagged - after_ids),
            'flagged_records_total': len(flagged),
            'supported_records_withheld': sorted(supported - after_ids),
            'retained_records': sorted(after_ids),
            'limitation': 'Frozen coding-agent judgments on previously observed cases; not independent human precision or an external benchmark.'}
