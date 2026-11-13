"""Collect bounded public sources locally for reproducible remote inference."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from .models import AXES, ResearchRequest, Settings
from .storage import Cache, atomic_json


class SnapshotSearch:
    """Read a collected snapshot without credentials or outbound search calls."""

    def __init__(self, path):
        data = json.loads(Path(path).read_text())
        self.request = ResearchRequest.model_validate(data["request"])
        self.queries = data["queries"]
        self.pages = data["pages"]
        self.collection_search_calls = data["search_calls"]
        self.calls = 0
        self.collected_at = data["collected_at"]

    def search(self, query):
        return self.queries.get(query, [])

    def fetch(self, url):
        return self.pages[url]["text"]


def collect_sources(request, output, settings=None, search=None):
    settings = settings or Settings()
    target = Path(output)
    target.mkdir(parents=True, exist_ok=True)
    cache = Cache(target / "collection.sqlite")
    fingerprint = hashlib.sha256(request.model_dump_json().encode()).hexdigest()
    identity = cache.get("request_hash")
    if identity and identity != fingerprint:
        cache.close()
        raise ValueError("Collection directory belongs to another request")
    cache.put("request_hash", fingerprint)
    try:
        if search is None:
            from .providers import TavilySearch

            search = TavilySearch(cache, settings.max_searches)
        search.calls = cache.get("search_calls") or 0
        queries: dict[str, list[dict[str, str]]] = {}
        pages: dict[str, dict[str, str]] = {}
        errors: list[dict[str, str]] = []
        quota = max(1, settings.max_documents // len(request.companies))
        for company in request.companies:
            selected: set[str] = set()
            for axis in AXES:
                query = f"site:{urlsplit(company.website).hostname} {company.name} {axis}"
                queries[query] = []
                try:
                    for item in search.search(query):
                        url = item["url"]
                        if url not in selected and len(selected) >= quota:
                            continue
                        if url not in pages and len(pages) >= settings.max_documents:
                            continue
                        try:
                            if url not in pages:
                                pages[url] = {"text": search.fetch(url), "title": item.get("title", url)}
                            selected.add(url)
                            queries[query].append({"url": url, "title": pages[url]["title"]})
                        except Exception as exc:
                            errors.append({"url": url, "error": type(exc).__name__})
                except Exception as exc:
                    errors.append({"query": query, "error": type(exc).__name__})
                finally:
                    cache.put("search_calls", search.calls)
        data = {"schema_version": 1, "request": request.model_dump(), "queries": queries,
                "pages": pages, "search_calls": search.calls, "errors": errors,
                "collected_at": datetime.now(timezone.utc).isoformat()}
        atomic_json(target / "sources.json", data)
        return data
    finally:
        cache.close()
