"""Conservative source eligibility; eligibility does not establish factual truth."""

from dataclasses import dataclass
from urllib.parse import unquote, urlsplit

POLICY_VERSION = 'vendor-sources-v1'


@dataclass(frozen=True)
class SourceDecision:
    allowed: bool
    category: str
    reason: str


def source_decision(url, website, criterion=None):
    source = urlsplit(url)
    vendor = urlsplit(website).hostname or ''
    vendor = vendor.lower().removeprefix('www.')
    host = (source.hostname or '').lower().rstrip('.')
    if source.scheme != 'https' or source.username or not vendor:
        return SourceDecision(False, 'invalid', 'A public vendor HTTPS URL is required')
    if host != vendor and not host.endswith('.' + vendor):
        return SourceDecision(False, 'external', 'Source is outside the requested vendor domain')
    labels = host.removesuffix(vendor).strip('.').split('.')
    if any(label in {'forum', 'forums', 'community', 'discuss', 'discourse'} for label in labels):
        return SourceDecision(False, 'community', 'Community posts are not authoritative vendor statements')
    parts = set(unquote(source.path).lower().split('/'))
    if parts.intersection({'jobs', 'careers'}):
        return SourceDecision(False, 'recruiting', 'Recruiting material is outside the comparison criteria')
    if criterion == 'positioning' and 'templates' in parts:
        return SourceDecision(False, 'template', 'Customer mission templates do not establish vendor positioning')
    return SourceDecision(True, 'vendor_url', 'Vendor-domain URL; authorship, scope and freshness still need review')
