import argparse
import json
import subprocess
import sys
from pathlib import Path

from .models import Evidence, ResearchRequest, Settings


def main():
    parser = argparse.ArgumentParser(description="Evidence-linked company research")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("research")
    run.add_argument("request", type=Path)
    run.add_argument("--sources", type=Path, help="Use a precollected snapshot without search credentials")
    run.add_argument("--output", default="outputs/latest")
    run.add_argument("--demo", action="store_true", help="Synthetic offline fixture; no real research")
    collect = sub.add_parser("collect")
    collect.add_argument("request", type=Path)
    collect.add_argument("--output", default="outputs/collection")
    view = sub.add_parser("view")
    view.add_argument("bundle", type=Path)
    bench = sub.add_parser("evaluate")
    bench.add_argument("corpus", type=Path)
    bench.add_argument("questions", type=Path)
    bench.add_argument("--all-modes", action="store_true")
    bench.add_argument("--split", default="test", choices=["dev", "test"])
    bench.add_argument("--output", default="outputs/metrics.json")
    args = parser.parse_args()
    if args.command == "collect":
        from .collection import collect_sources
        request = ResearchRequest.model_validate_json(args.request.read_text())
        data = collect_sources(request, args.output)
        print(json.dumps({"pages": len(data["pages"]), "search_calls": data["search_calls"], "errors": len(data["errors"])}))
    elif args.command == "research":
        from .pipeline import run_research
        request = ResearchRequest.model_validate_json(args.request.read_text())
        if args.demo:
            from .demo import DemoModel, DemoSearch
            bundle = run_research(request, Settings(retrieval="bm25", rounds=0), args.output,
                                  DemoSearch(), DemoModel(), graph=False)
        elif args.sources:
            from .collection import SnapshotSearch
            search = SnapshotSearch(args.sources)
            if search.request != request:
                parser.error("Source snapshot belongs to another research request")
            bundle = run_research(request, output=args.output, search=search)
        else:
            bundle = run_research(request, output=args.output)
        print(json.dumps({"status": bundle.status, "output": args.output, "warnings": bundle.warnings}, indent=2))
    elif args.command == "evaluate":
        from .evaluation import evaluate
        evidence = [Evidence.model_validate_json(line) for line in args.corpus.read_text().splitlines() if line]
        questions = [json.loads(line) for line in args.questions.read_text().splitlines() if line]
        encoder = None
        if args.all_modes:
            from sentence_transformers import SentenceTransformer
            encoder = SentenceTransformer(Settings().embedding, device="cpu")
        result = evaluate(evidence, questions, ("bm25", "dense", "hybrid") if args.all_modes else ("bm25",), encoder, args.split)
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
    else:
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(Path(__file__).with_name("viewer.py")), "--", str(args.bundle)], check=True)


if __name__ == "__main__":
    main()
