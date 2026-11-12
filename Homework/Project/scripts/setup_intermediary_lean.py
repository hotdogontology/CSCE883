"""Install isolated official Lean toolchains and build the pinned dialect sources."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
import requests

from prepare_intermediary_sources import ROOT, BASE, REPOS

GIT = r'C:\Program Files\Git\cmd\git.exe'


def setup(name):
    repo, revision = REPOS[name]
    pinned_source = BASE / (name + '-' + revision)
    source = pinned_source
    # Lean's cache extractor still encounters Windows path-length limits deep
    # under a revision-named checkout. Keep an isolated shorter build copy.
    if name == 'verbose-lean4':
        source = ROOT / 'data/vl431'
        if not source.exists():
            shutil.copytree(pinned_source, source, ignore=shutil.ignore_patterns('.lake', '.git'))
    version = (source / 'lean-toolchain').read_text().strip().split(':v')[1]
    home = BASE / 'toolchains' / version
    home.mkdir(parents=True, exist_ok=True)
    state_path = BASE / (name + '-setup.json')
    log_path = BASE / (name + '-setup.log')
    state = {'status': 'running', 'repository': repo, 'revision': revision,
             'version': version, 'source': str(source), 'stage': 'release_metadata'}
    def save(stage):
        state['stage'] = stage
        state_path.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
        print(name + ': ' + stage, flush=True)
    try:
        save('release_metadata')
        response = requests.get(f'https://api.github.com/repos/leanprover/lean4/releases/tags/v{version}', timeout=60)
        response.raise_for_status()
        asset = next(a for a in response.json()['assets'] if a['name'] == f'lean-{version}-windows.zip')
        digest = asset.get('digest', '')
        if not digest.startswith('sha256:'):
            raise ValueError('Official release lacks SHA256 digest')
        archive = home / asset['name']
        if not archive.exists():
            save('download_official_lean')
            with requests.get(asset['browser_download_url'], stream=True, timeout=120) as download:
                download.raise_for_status()
                with archive.with_suffix('.partial').open('wb') as handle:
                    for chunk in download.iter_content(8 * 1024 * 1024):
                        handle.write(chunk)
            archive.with_suffix('.partial').replace(archive)
        with archive.open('rb') as handle:
            actual = hashlib.file_digest(handle, 'sha256').hexdigest()
        if digest != 'sha256:' + actual:
            raise ValueError('Official Lean SHA256 mismatch')
        state['lean_archive_sha256'] = actual
        lean_root = home / f'lean-{version}-windows'
        if not (lean_root / 'bin/lake.exe').exists():
            save('extract_lean')
            with zipfile.ZipFile(archive) as bundle:
                for member in bundle.infolist():
                    if not (home / member.filename).resolve().is_relative_to(home.resolve()):
                        raise ValueError('Unsafe archive member')
                bundle.extractall(home)
        env = dict(os.environ)
        env['PATH'] = str(lean_root / 'bin') + os.pathsep + str(Path(GIT).parent) + os.pathsep + env['PATH']
        env['GIT_CONFIG_COUNT'] = '2'
        env['GIT_CONFIG_KEY_0'] = 'safe.directory'
        env['GIT_CONFIG_VALUE_0'] = (ROOT / 'data').as_posix() + '/*'
        env['GIT_CONFIG_KEY_1'] = 'core.longpaths'
        env['GIT_CONFIG_VALUE_1'] = 'true'
        env['GIT_TERMINAL_PROMPT'] = '0'
        env['LEAN_NUM_THREADS'] = '4'
        lake = str(lean_root / 'bin/lake.exe')
        state['lean_executable'] = str(lean_root / 'bin/lean.exe')
        state['lake_executable'] = lake
        with log_path.open('a', encoding='utf-8') as log:
            def run(args):
                subprocess.run([lake] + args, cwd=source, env=env, stdout=log,
                               stderr=subprocess.STDOUT, check=True)
            if name == 'verbose-lean4':
                save('dependencies_mathlib_cache')
                run(['exe', 'cache', 'get'])
            save('build_library')
            run(['build'])
            save('build_examples')
            run(['build', 'Verbose.English.Examples' if name == 'verbose-lean4' else 'Natural.Examples'])
        state['lean_path'] = subprocess.check_output([lake, 'env', sys.executable, '-c',
            'import os;print(os.environ.get("LEAN_PATH",""))'], cwd=source, env=env,
            text=True).strip()
        state['status'] = 'complete'
        save('complete')
    except BaseException as error:
        state['status'] = 'failed'
        state['error'] = repr(error)
        save(state['stage'])
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dialect', choices=['verbose-lean4', 'natural_lean'], required=True)
    setup(parser.parse_args().dialect)


if __name__ == '__main__':
    main()
