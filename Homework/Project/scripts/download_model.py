"""Download the selected public checkpoint at a recorded immutable revision."""
from pathlib import Path
import fnmatch
import hashlib
import json
import shutil

from huggingface_hub import HfApi, snapshot_download

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "model-manifest.json"
REPO = "Qwen/Qwen3-8B"
PATTERNS = ["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja",
            "README.md", "LICENSE", "LICENSE.*", "NOTICE"]
destination = ROOT / "data" / "models" / "Qwen3-8B"

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
    "local_directory": "data/models/Qwen3-8B",
    "format": "safetensors", "license": "apache-2.0",
    "stage": "zero-shot and unlabeled exploration; no task fine-tuning",
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
