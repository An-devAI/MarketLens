import sys
from pathlib import Path

import streamlit as st

from marketlens.models import ReportBundle
from marketlens.report import render

st.set_page_config(page_title="MarketLens", layout="wide")
st.title("MarketLens")
st.caption("Company research with inspectable source evidence")
path = Path(sys.argv[1])
if path.is_dir():
    path = path / "report.json"
bundle = ReportBundle.model_validate_json(path.read_text())
if any("SYNTHETIC" in e.title for e in bundle.evidence):
    st.warning("Synthetic demonstration — not a real company analysis")
else:
    label = "Curated source excerpts" if "sample_origin" in bundle.manifest else "Generated report"
    st.caption(label + " · semantic review pending")
company_metric, source_metric, finding_metric = st.columns(3)
company_metric.metric("Companies", len(bundle.request.companies))
source_metric.metric("Source pages", len({e.url for e in bundle.evidence}))
finding_metric.metric("Documented findings", sum(c.kind != "unknown" for c in bundle.claims))
report, evidence, execution = st.tabs(["Comparison", "Evidence", "Execution"])
with report:
    st.markdown(render(bundle).split("\n", 2)[2], unsafe_allow_html=False)
    st.download_button("Download report", render(bundle), file_name="marketlens-report.md")
with evidence:
    company = st.selectbox("Company", [c.name for c in bundle.request.companies])
    for claim in bundle.claims:
        if claim.company != company:
            continue
        with st.expander(f"{claim.criterion}: {claim.text}"):
            st.write({"kind": claim.kind, "quote": claim.quote})
            for item in bundle.evidence:
                if item.id in claim.evidence_ids:
                    st.text(item.text)
                    st.write(item.url)
                    st.caption(f"Collected {item.fetched_at} · {item.id}")
with execution:
    st.json(bundle.manifest)
    st.write(bundle.warnings)
    traces = path.parent / "traces.jsonl"
    if traces.exists():
        st.code(traces.read_text(), language="json")
