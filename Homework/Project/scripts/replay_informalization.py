"""Rerun a frozen informalization split in a NEW output directory (GPU required)."""
from pathlib import Path
import argparse
import shutil
import informalization_pipeline as pipeline

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('corpus', choices=['herald', 'proofnet'])
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('Choose a new output directory; existing experiments are never overwritten.')
    original = 'informalization-14b-20261112' if args.corpus == 'herald' else 'informalization-proofnet-14b-20261113'
    source = pipeline.ROOT / 'artifacts' / original / 'data'
    if not (source / 'manifest.json').is_file():
        raise SystemExit('Run scripts/restore_evidence.py first.')
    shutil.copytree(source, output / 'data')
    pipeline.OUT = output
    pipeline.run()

if __name__ == '__main__':
    main()
