"""Stage an allowlisted, credential-free private Kaggle runtime dataset."""

import argparse
import json
import shutil
from pathlib import Path

from dotenv import dotenv_values

parser = argparse.ArgumentParser()
parser.add_argument('--sources', type=Path, default=Path('outputs/live-collection/sources.json'))
parser.add_argument('--destination', type=Path, default=Path('/tmp/marketlens-kaggle-data'))
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
args.destination.mkdir(parents=True, exist_ok=True)
wheel = max((root / 'dist').glob('*.whl'), key=lambda p: p.stat().st_mtime)
expected = {wheel.name, 'sources.json', 'request.json', 'dataset-metadata.json'}
if any(path.name not in expected for path in args.destination.iterdir()):
    raise SystemExit('Staging contains unexpected files; choose a fresh destination')
for source, name in [(wheel, wheel.name), (args.sources, 'sources.json'),
                     (root / 'examples/request.json', 'request.json')]:
    shutil.copy2(source, args.destination / name)
metadata = {'title': 'MarketLens Runtime', 'id': 'truongan16/marketlens-runtime',
            'licenses': [{'name': 'other'}]}
(args.destination / 'dataset-metadata.json').write_text(json.dumps(metadata, indent=2))
secret = dotenv_values(root / '.env').get('TAVILY_API_KEY')
for path in args.destination.iterdir():
    if path.is_file() and secret and secret.encode() in path.read_bytes():
        raise SystemExit('Credential detected in staging; upload aborted')
print('Staged wheel, public-source snapshot and request. Credential scan passed.')
