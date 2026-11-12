"""Fetch pinned upstream dialect/engine sources into ignored project data."""
from pathlib import Path
import argparse
import hashlib
import json
import requests
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/intermediary-sources'
REPOS = {
    'verbose-lean4': ('PatrickMassot/verbose-lean4', 'ea52f4bf6c60d986cb3fa2a5b7d7a8429b886eed'),
    'natural_lean': ('medovina/natural_lean', 'd7d0d5de14c0404a9e4d900d76fac2f19d304a56'),
    'colibri': ('JustVugg/colibri', '0a5504a1dc64f86fcd0fe7db298b0448c730e7e6'),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', choices=list(REPOS), action='append')
    args = parser.parse_args()
    BASE.mkdir(parents=True, exist_ok=True)
    records = []
    for name in args.repo or REPOS:
        repo, revision = REPOS[name]
        archive = BASE / (name + '-' + revision + '.zip')
        url = f'https://codeload.github.com/{repo}/zip/{revision}'
        if not archive.exists():
            with requests.get(url, stream=True, timeout=120) as response:
                response.raise_for_status()
                with archive.with_suffix('.partial').open('wb') as handle:
                    for chunk in response.iter_content(1024 * 1024):
                        handle.write(chunk)
            archive.with_suffix('.partial').replace(archive)
        with archive.open('rb') as handle:
            digest = hashlib.file_digest(handle, 'sha256').hexdigest()
        source = BASE / (name + '-' + revision)
        if not source.exists():
            with zipfile.ZipFile(archive) as bundle:
                for member in bundle.infolist():
                    target = (BASE / member.filename).resolve()
                    if not target.is_relative_to(BASE.resolve()):
                        raise ValueError('Archive path escapes source directory')
                bundle.extractall(BASE)
        if not source.is_dir():
            raise ValueError(f'Expected source root absent: {source}')
        record = {'repository': repo, 'revision': revision, 'url': url,
                  'archive_sha256': digest, 'source': source.relative_to(ROOT).as_posix(),
                  'downloaded_only': True}
        if (source / 'lean-toolchain').exists():
            record['toolchain'] = (source / 'lean-toolchain').read_text().strip()
        records.append(record)
        print(json.dumps(record), flush=True)
    target = BASE / 'manifest.json'
    previous = json.loads(target.read_text()) if target.exists() else []
    merged = {item['repository']: item for item in previous + records}
    target.write_text(json.dumps(list(merged.values()), indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
