import hashlib
import math
import re
from collections import Counter

from .models import Evidence


def tokens(text):
    return re.findall(r"\w+", text.casefold())


def chunk_document(company, url, title, text, fetched_at, tokenizer=None):
    """Keep headings/paragraphs; split oversized paragraphs with tokenizer when available."""
    result = []
    digest = hashlib.sha256(text.encode()).hexdigest()
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if tokenizer:
            ids = tokenizer.encode(paragraph, add_special_tokens=False)
            pieces = [tokenizer.decode(ids[i:i+350]) for i in range(0, len(ids), 320)]
        else:
            words = paragraph.split()
            pieces = [" ".join(words[i:i+200]) for i in range(0, len(words), 180)]
        for piece in pieces:
            identifier = hashlib.sha256((company + url + piece).encode()).hexdigest()[:16]
            result.append(Evidence(id=identifier, company=company, url=url, title=title,
                                   text=piece, fetched_at=fetched_at, content_hash=digest))
    return result


class Retriever:
    def __init__(self, evidence, mode="bm25", encoder=None):
        self.evidence = evidence
        self.mode = mode
        self.encoder = encoder
        self.docs = [tokens(e.text) for e in evidence]
        self.length = sum(map(len, self.docs)) / max(len(self.docs), 1)
        self.vectors = None
        if mode != "bm25" and evidence:
            import faiss
            import numpy as np
            vectors = np.asarray(encoder.encode(["passage: " + e.text for e in evidence],
                                  normalize_embeddings=True), dtype="float32")
            self.vectors = faiss.IndexFlatIP(vectors.shape[1])
            self.vectors.add(vectors)

    def search(self, query, company=None, k=6):
        candidates = [i for i, e in enumerate(self.evidence)
                      if company is None or e.company == company]
        if not candidates:
            return []
        q = tokens(query)
        scores = {}
        for i in candidates:
            counts = Counter(self.docs[i])
            score = 0.0
            for word in set(q):
                df = sum(word in self.docs[j] for j in candidates)
                idf = math.log(1 + (len(candidates)-df+0.5)/(df+0.5))
                tf = counts[word]
                score += idf * tf * 2.5 / (tf + 1.5 * (0.25 + 0.75 *
                         len(self.docs[i])/max(self.length, 1)))
            if score > 0:
                scores[i] = score
        sparse = sorted(scores, key=lambda i: (-scores[i], i))
        if self.mode == "bm25":
            ranking = sparse
        else:
            import numpy as np
            if self.vectors is None:
                raise RuntimeError("Dense index is unavailable")
            vector = np.asarray(self.encoder.encode(["query: " + query],
                                normalize_embeddings=True), dtype="float32")
            _, indexes = self.vectors.search(vector, len(self.evidence))
            dense = [int(i) for i in indexes[0] if int(i) in candidates]
            if self.mode == "dense":
                ranking = dense
            else:
                fused: dict[int, float] = {}
                for ordered in (sparse, dense):
                    for rank, i in enumerate(ordered):
                        fused[i] = fused.get(i, 0.0) + 1 / (60 + rank + 1)
                ranking = sorted(fused, key=lambda i: (-fused[i], i))
        return [self.evidence[i] for i in ranking[:k]]


class CachedEncoder:
    """Reuse passage embeddings across growing indexes within one research run."""

    def __init__(self, encoder):
        self.encoder = encoder
        self.tokenizer = getattr(encoder, "tokenizer", None)
        self.cache: dict[tuple[str, bool], object] = {}

    def encode(self, texts, normalize_embeddings=True):
        import numpy as np

        missing = list(dict.fromkeys(text for text in texts
                                    if (text, normalize_embeddings) not in self.cache))
        if missing:
            vectors = self.encoder.encode(missing, normalize_embeddings=normalize_embeddings)
            for text, vector in zip(missing, vectors, strict=True):
                self.cache[(text, normalize_embeddings)] = vector
        return np.asarray([self.cache[(text, normalize_embeddings)] for text in texts],
                          dtype="float32")
