from .models import AXES, Claim


def verify(claim, evidence):
    selected = [e for e in evidence if e.id in claim.evidence_ids]
    valid = (claim.kind != "unknown" and bool(claim.evidence_ids) and bool(claim.quote.strip())
             and set(claim.evidence_ids) == {e.id for e in selected}
             and all(e.company == claim.company for e in selected)
             and any(claim.quote in e.text for e in selected))
    if valid:
        return claim, True
    return Claim(company=claim.company, criterion=claim.criterion,
                 text="Insufficient verified evidence", kind="unknown"), False


def render(bundle):
    def escape(text):
        return text.replace("|", r"\|").replace("\n", " ")
    lines = ["# MarketLens comparison", "", f"Status: **{bundle.status}**", "",
             "Evidence reflects collection time, not guaranteed current availability.", "",
             "## Comparison", "", "| Criterion | " + " | ".join(escape(c.name) for c in bundle.request.companies) + " |",
             "|---|" + "---|" * len(bundle.request.companies)]
    for axis in AXES:
        cells = []
        for company in bundle.request.companies:
            claims = [c for c in bundle.claims if c.company == company.name and c.criterion == axis]
            cells.append("; ".join(escape(c.text) + (" [inference]" if c.kind == "inference" else "") +
                         " ".join(f"[{i}](#source-{i})" for i in c.evidence_ids) for c in claims)
                         or "Insufficient evidence")
        lines.append("| " + axis + " | " + " | ".join(cells) + " |")
    lines.extend(["", "## Evidence", ""])
    used = {i for c in bundle.claims for i in c.evidence_ids}
    for e in bundle.evidence:
        if e.id in used:
            lines.extend([f'<a id="source-{e.id}"></a>', f"### {e.title}",
                          f"Source: {e.url} · Collected: {e.fetched_at}", "", "> " + e.text.replace("\n", "\n> "), ""])
    lines.extend(["## Limitations", ""] + ["- " + x for x in bundle.warnings])
    return "\n".join(lines) + "\n"
