# MarketLens: introduction and provenance

## References and reuse

- https://github.com/langchain-ai/open_deep_research — supervisor/researcher orchestration reference. The override_reducer function in src/marketlens/pipeline.py is copied from state.py; bounded supervisor/researcher routing is adapted to company-scoped evidence. Search, model inference, storage, evaluation and report rendering are new implementations, not a copy of the entire original engine.
- https://github.com/coleam00/context-engineering-intro — requirements/examples/PRP/validation workflow adapted for Codex using AGENTS.md. No Claude command files are used.

## Reference checkout status

The reference directory is a source snapshot retrieved through the web reader, not a completed Git clone or GitHub fork. Shell DNS access and GitHub authentication are unavailable. Original commit SHA is unverified; source snapshot content hashes can be calculated locally. Do not claim a pinned upstream revision until the authenticated checkout has been completed and compared. Preserve snapshot files until that comparison is complete.

To complete setup outside the product repository: authenticate with gh, run `gh repo fork langchain-ai/open_deep_research --clone=false`, clone your fork into a separate temporary sibling, compare it with the snapshot, then use that checkout as the reference directory. Record `git rev-parse HEAD` here and update the reuse table when adapting additional code.

The product is a separate Git repository. Its contribution history begins with the actual product bootstrap and integrations; it does not relabel original commit history as personal work.

## License notices

The following notices are included intact for reused code and adapted materials. This document is included in package distributions.

### Research reference

MIT License

Copyright (c) 2025 LangChain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### Context workflow reference

MIT License

Copyright (c) 2025 Cole Medin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Snapshot integrity

- `deep_researcher.py` SHA-256: `3659eeb818d0b6407b42334bd87980f5108be106f41869c84fed96fd7a8e4515`.
- `state.py` SHA-256: `0b0b0516f7fdbb2bf823c59d7f5d1964a5d691886bcef392727a1578cd70f39a`.
