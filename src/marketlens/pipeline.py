import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, TypedDict
from urllib.parse import urlsplit

from .models import AXES, Claim, Evidence, ReportBundle, ResearchPlan, Settings
from .report import render, verify
from .retrieval import Retriever, chunk_document
from .storage import Cache, atomic_json


def override_reducer(current_value, new_value):
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    return current_value + new_value


class ResearchState(TypedDict):
    round: int
    missing: list
    notes: Annotated[list, override_reducer]


def run_research(request, settings=None, output="outputs/latest", search=None, model=None,
                 encoder=None, graph=True):
    settings = settings or Settings()
    target = Path(output)
    target.mkdir(parents=True, exist_ok=True)
    cache = Cache(target / "cache.sqlite")
    start = time.monotonic()
    fingerprint = hashlib.sha256(json.dumps({"request": request.model_dump(),
        "settings": settings.model_dump()}, sort_keys=True).encode()).hexdigest()
    checkpoint = cache.get("checkpoint")
    if checkpoint and checkpoint["fingerprint"] != fingerprint:
        cache.close()
        raise ValueError("Output contains a different request or configuration; use another folder")
    if search is None:
        from .providers import TavilySearch
        search = TavilySearch(cache, settings.max_searches)
    if model is None:
        from .providers import QwenModel
        model = QwenModel(settings.model)
    if encoder is None and settings.retrieval != "bm25":
        from sentence_transformers import SentenceTransformer
        encoder = SentenceTransformer(settings.embedding, device="cpu")
    evidence = [Evidence.model_validate(e) for e in (checkpoint or {}).get("evidence", [])]
    claims = [Claim.model_validate(c) for c in (checkpoint or {}).get("claims", [])]
    warnings = list((checkpoint or {}).get("warnings", []))
    documents = set((checkpoint or {}).get("documents", []))
    hashes = {(e.company, e.content_hash) for e in evidence}
    previous_calls = (checkpoint or {}).get("searches", 0)
    if hasattr(search, "calls"):
        search.calls = previous_calls
    traces = list((checkpoint or {}).get("traces", []))

    def supervisor(state):
        complete = {(c.company, c.criterion) for c in claims if c.kind != "unknown"}
        missing = [(c.name, axis) for c in request.companies for axis in AXES
                   if (c.name, axis) not in complete]
        traces.append({"node": "supervisor", "round": state["round"], "missing": missing})
        return {"missing": missing, "notes": [{"round": state["round"], "missing_count": len(missing)}]}

    def researcher(state):
        nonlocal claims
        for company_name, axis in state["missing"]:
            company = next(c for c in request.companies if c.name == company_name)
            domain = urlsplit(company.website).hostname
            query = f"site:{domain} {company.name} {axis}"
            if state["round"] > 0:
                try:
                    plan = model.structured(
                        "Choose one targeted search query for missing evidence. Prefer primary sources.",
                        {"company": company_name, "criterion": axis, "brief": request.brief}, ResearchPlan)
                    query = plan.queries[0]
                except (ValueError, RuntimeError) as exc:
                    warnings.append(f"Planning failed for {company_name}/{axis}: {exc}")
            try:
                results = search.search(query)
                for item in results:
                    url = item["url"]
                    key = company_name + ":" + url
                    if key in documents or len(documents) >= settings.max_documents:
                        continue
                    try:
                        text = search.fetch(url)
                        digest = hashlib.sha256(text.encode()).hexdigest()
                        documents.add(key)
                        if (company_name, digest) in hashes:
                            continue
                        hashes.add((company_name, digest))
                        tokenizer = getattr(encoder, "tokenizer", None)
                        evidence.extend(chunk_document(company_name, url, item.get("title", url),
                            text, datetime.now(timezone.utc).isoformat(), tokenizer))
                    except Exception as exc:
                        warnings.append(f"Source unavailable {url}: {type(exc).__name__}")
            except Exception as exc:
                warnings.append(f"Search failed {company_name}/{axis}: {type(exc).__name__}")
            retriever = Retriever(evidence, settings.retrieval, encoder)
            passages = retriever.search(axis + " " + request.brief, company_name)
            try:
                proposed = model.analyze(company_name, axis, passages) if passages else []
                accepted = []
                for claim in proposed:
                    if claim.company != company_name or claim.criterion != axis:
                        warnings.append(f"Rejected mismatched claim for {company_name}/{axis}")
                        continue
                    checked, valid = verify(claim, passages)
                    accepted.append(checked)
                    if not valid:
                        warnings.append(f"Rejected invalid citation for {company_name}/{axis}")
                claims = [c for c in claims if (c.company, c.criterion) != (company_name, axis)]
                claims.extend(accepted or [Claim(company=company_name, criterion=axis,
                    text="Insufficient verified evidence", kind="unknown")])
            except Exception as exc:
                warnings.append(f"Analysis failed {company_name}/{axis}: {type(exc).__name__}")
            traces.append({"node": "researcher", "company": company_name, "criterion": axis,
                           "retrieved": [e.id for e in passages]})
            cache.put("checkpoint", {"fingerprint": fingerprint,
                "evidence": [e.model_dump() for e in evidence],
                "claims": [c.model_dump() for c in claims], "warnings": warnings,
                "documents": sorted(documents), "searches": getattr(search, "calls", 0),
                "traces": traces, "round": state["round"]})
        return {"round": state["round"] + 1}

    def route(state):
        return "researcher" if state["missing"] and state["round"] <= settings.rounds else "end"

    initial = {"round": (checkpoint or {}).get("round", 0), "missing": [], "notes": []}
    try:
        if graph:
            from langgraph.graph import END, START, StateGraph
            builder = StateGraph(ResearchState)
            builder.add_node("supervisor", supervisor)
            builder.add_node("researcher", researcher)
            builder.add_edge(START, "supervisor")
            builder.add_conditional_edges("supervisor", route, {"researcher": "researcher", "end": END})
            builder.add_edge("researcher", "supervisor")
            builder.compile().invoke(initial, {"recursion_limit": 12})
        else:
            state = initial
            while True:
                state.update(supervisor(state))
                if route(state) == "end":
                    break
                state.update(researcher(state))
        complete = {(c.company, c.criterion) for c in claims if c.kind != "unknown"}
        bundle = ReportBundle(request=request, evidence=evidence, claims=claims,
            warnings=list(dict.fromkeys(warnings)),
            status="complete" if len(complete) == len(request.companies)*len(AXES) else "partial",
            manifest={"request_hash": fingerprint, "settings": settings.model_dump(),
                      "duration_seconds": round(time.monotonic()-start, 3),
                      "search_calls_total": getattr(search, "calls", 0),
                      "input_tokens": getattr(model, "input_tokens", 0),
                      "output_tokens": getattr(model, "output_tokens", 0),
                      "citation_check": "Reference and quote integrity only; semantic review required"})
        atomic_json(target / "report.json", bundle.model_dump())
        (target / "report.md").write_text(render(bundle))
        (target / "corpus.jsonl").write_text("".join(e.model_dump_json()+"\n" for e in evidence))
        (target / "traces.jsonl").write_text("".join(json.dumps(e)+"\n" for e in traces))
        index = Retriever(evidence, settings.retrieval, encoder)
        if index.vectors is not None:
            import faiss
            faiss.write_index(index.vectors, str(target / "index.faiss"))
        return bundle
    finally:
        cache.close()
