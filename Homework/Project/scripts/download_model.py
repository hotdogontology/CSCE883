"""Download the selected public checkpoint at a recorded immutable revision."""
from pathlib import Path
import argparse
import fnmatch
import hashlib
import json
import shutil

from huggingface_hub import HfApi, snapshot_download

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo', default='Qwen/Qwen3-8B')
parser.add_argument('--manifest', type=Path, default=ROOT/'model-manifest.json')
parser.add_argument('--destination', type=Path)
args = parser.parse_args()
MANIFEST = args.manifest
REPO = args.repo
PATTERNS = ["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja",
            "README.md", "LICENSE", "LICENSE.*", "NOTICE"]
destination = args.destination or ROOT / 'data/models' / REPO.split('/')[-1]

previous = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
revision = previous.get("revision") if previous.get("repo_id") == REPO else None
info = HfApi().model_info(REPO, revision=revision, files_metadata=True, token=False)
files = [item for item in info.siblings
         if any(fnmatch.fnmatch(item.rfilename, pattern) for pattern in PATTERNS)]
required_bytes = sum(item.size or 0 for item in files)
assert shutil.disk_usage(ROOT).free > required_bytes + 5 * 2**30, "Insufficient free disk space"
manifest = {
    "repo_id": REPO, "revision": info.sha,
    "source": "https://huggingface.co/" + REPO,
    "local_directory": destination.relative_to(ROOT).as_posix(),
    "format": "safetensors", "license": "apache-2.0",
    "stage": "pinned base checkpoint; experiment state is recorded separately",
    "download_complete": False, "expected_bytes": required_bytes,
    "files": [{"path": item.rfilename, "bytes": item.size,
               "sha256": item.lfs.sha256 if item.lfs else None} for item in files],
}
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"repo": REPO, "revision": info.sha,
                  "download_gib": round(required_bytes / 2**30, 2),
                  "destination": str(destination)}), flush=True)
snapshot_download(REPO, revision=info.sha, local_dir=destination,
                  allow_patterns=PATTERNS, max_workers=2, token=False)
for item in manifest["files"]:
    path = destination / item["path"]
    assert path.is_file(), f"Missing file: {item['path']}"
    if item["bytes"] is not None:
        assert path.stat().st_size == item["bytes"], f"Size mismatch: {item['path']}"
    if item["sha256"]:
        print("Verifying " + item["path"], flush=True)
        with path.open("rb") as handle:
            actual = hashlib.file_digest(handle, "sha256").hexdigest()
        assert actual == item["sha256"], f"Hash mismatch: {item['path']}"
manifest["download_complete"] = True
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print("Download complete; file sizes and published LFS SHA-256 hashes verified.", flush=True)
