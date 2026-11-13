from collections import Counter

from .models import AXES, Claim


def report_summary(bundle):
    kinds = dict(Counter(claim.kind for claim in bundle.claims))
    retained = sum(claim.kind != 'unknown' for claim in bundle.claims)
    covered = {(claim.company, claim.criterion) for claim in bundle.claims if claim.kind != 'unknown'}
    return {'records': len(bundle.claims), 'retained': retained,
            'unknown': len(bundle.claims) - retained, 'claim_kinds': kinds,
            'covered_cells': len(covered), 'total_cells': len(bundle.request.companies) * len(AXES)}


def verify(claim, evidence):
    selected = [e for e in evidence if e.id in claim.evidence_ids]
    valid = (claim.kind != "unknown" and bool(claim.evidence_ids) and bool(claim.quote.strip())
             and set(claim.evidence_ids) == {e.id for e in selected}
             and all(e.company == claim.company for e in selected)
             and all(claim.quote in e.text for e in selected))
    if valid:
        return claim, True
    return Claim(company=claim.company, criterion=claim.criterion,
                 text="Insufficient verified evidence", kind="unknown"), False


def render(bundle):
    def escape(text):
        return text.replace("|", r"\|").replace("\n", " ")
    sources = {e.id: e for e in bundle.evidence}
    numbering = {eid: i + 1 for i, eid in enumerate(dict.fromkeys(
        eid for claim in bundle.claims for eid in claim.evidence_ids if eid in sources))}
    lines = ["# MarketLens comparison", "", f"Evidence coverage: **{bundle.status}**", "",
             "Evidence reflects collection time, not guaranteed current availability.", "",
             "## Comparison", "", "| Criterion | " + " | ".join(escape(c.name) for c in bundle.request.companies) + " |",
             "|---|" + "---|" * len(bundle.request.companies)]
    for axis in AXES:
        cells = []
        for company in bundle.request.companies:
            claims = [c for c in bundle.claims if c.company == company.name and c.criterion == axis]
            cells.append("; ".join(escape(c.text) + (" [inference]" if c.kind == "inference" else "") +
                         " " + " ".join(f"[{numbering[i]}]({sources[i].url})" for i in c.evidence_ids if i in numbering) for c in claims)
                         or "Insufficient evidence")
        lines.append("| " + axis + " | " + " | ".join(cells) + " |")
    lines.extend(["", "## Evidence", ""])
    used = {i for c in bundle.claims for i in c.evidence_ids}
    for e in bundle.evidence:
        if e.id in used:
            lines.extend([f"### [{numbering[e.id]}] {e.title}",
                          f"Source: {e.url} · Collected: {e.fetched_at}", "", "> " + e.text.replace("\n", "\n> "), ""])
    lines.extend(["## Limitations", ""] + ["- " + x for x in bundle.warnings])
    return "\n".join(lines) + "\n"
