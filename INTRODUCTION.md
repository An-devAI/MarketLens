# MarketLens: introduction and provenance

## Verified reference checkouts

Both repositories are complete local Git clones outside the product repository, with clean working trees verified on 2026-11-13. Their origin remotes point to the original repositories; they are not personal GitHub forks. These clones replace the earlier web-retrieved snapshots.

| Reference | Repository | Checked-out commit |
|---|---|---|
| Research implementation | https://github.com/langchain-ai/open_deep_research | `1b7d2e80db9faa586165c60e09096dbbfd483a64` |
| Context workflow | https://github.com/coleam00/context-engineering-intro | `a2d84b021cee1e2f4e77ba854bba0be8cb319035` |

The checked-out revisions above identify the source used for comparison. Keep them recorded when updating a reference checkout. The product remains an independent Git repository; reference histories and checkouts are not included in its commits or package distributions.

## Reuse and original contributions

| Product material | Reference material | Actual reuse |
|---|---|---|
| `src/marketlens/pipeline.py::override_reducer` | Research reference `src/open_deep_research/state.py::override_reducer` | Adapted override/append behavior; uses `+` instead of `operator.add`. Verified against the checked-out implementation. |
| Bounded supervisor/researcher routing | Research reference `src/open_deep_research/deep_researcher.py` | Architecture adapted to company/criterion evidence gaps. The complete original agent loop has not been copied or integrated. |
| `INITIAL.md`, `AGENTS.md`, examples and implementation PRP | Context reference `INITIAL.md` and `PRPs/templates/prp_base.md` | Requirements/examples/context/validation workflow adapted for Codex. No Claude instruction files or slash commands are used in the product. |
| Search/model providers, hybrid retrieval, evidence storage, evaluation, report and viewer | Product implementation | New implementation; live model and GPU acceptance remain pending. |

The current implementation should not be described as integrating the full reference research engine. Further reuse must be recorded here with its original revision and affected product modules.

## Reference file integrity

- `src/open_deep_research/deep_researcher.py` SHA-256: `af128d5d8773008d021b6ef7562e9fb90a45f7eb5e886483d1e6e835223275e0`.
- `src/open_deep_research/state.py` SHA-256: `7a03f4a1d5132573ed306d403fd3478fe8916d955f3caa44a8d365877ac35d0e`.

## License notices

The following notices are reproduced from the verified checkouts for reused code and adapted workflow material. This document is included in package distributions. The isolated reference checkouts retain their original license files.

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
