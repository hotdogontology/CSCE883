"""Download a pinned corpus, audit structure, and prepare UNLABELED review rows.

Run from any directory with the project virtual environment. No dataset-provided
pair is automatically labeled faithful. Generated Lean files are replay probes,
not proof-integrity certificates (imports can contain the original theorem).
"""
from pathlib import Path
import hashlib
import json

import pandas as pd
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
REPO = "FrenzyMath/Herald_proofs"
REVISION = "2d31b459df74d730bff85682de237d894b4eecfa"
FILE = "data/train-00000-of-00001.parquet"
destination = ROOT / "data" / "herald"
destination.mkdir(parents=True, exist_ok=True)
path = Path(hf_hub_download(REPO, FILE, repo_type="dataset", revision=REVISION,
                           local_dir=destination))
df = pd.read_parquet(path)
text_fields = ["formal_theorem", "informal_theorem", "formal_proof",
               "informal_proof", "header"]
assert set(text_fields + ["id", "name"]).issubset(df.columns)
report = {
    "repo": REPO, "revision": REVISION, "file": FILE,
    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "rows": len(df), "columns": list(df.columns),
    "nulls": {key: int(df[key].isna().sum()) for key in text_fields},
    "empty_strings": {key: int(df[key].fillna("").str.strip().eq("").sum())
                      for key in text_fields},
    "duplicate_names": int(df.name.duplicated().sum()),
    "duplicate_formal_proofs": int(df.formal_proof.duplicated().sum()),
    "formal_proof_admission_token_candidates": int(
        df.formal_proof.str.contains(r"\b(?:sorry|admit|sorryAx)\b", regex=True,
                                     na=False).sum()),
    "formal_theorem_admission_token_candidates": int(
        df.formal_theorem.str.contains(r"\b(?:sorry|admit|sorryAx)\b", regex=True,
                                       na=False).sum()),
    "character_lengths": {key: {str(q): int(value) for q, value in
        df[key].fillna("").str.len().quantile([.5, .9, .99, 1]).items()}
        for key in text_fields},
    "caveats": ["Token scans include comments; they do not audit elaborated axioms.",
                "Synthetic English is not a trusted positive label.",
                "The formal_theorem field can be an admitted statement template.",
                "Use header + formal_proof for complete-proof replay.",
                "Replaying with Mathlib imports can expose the target theorem."],
}
(destination / "audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
with (destination / "review-unlabeled.jsonl").open("w", encoding="utf-8") as out:
    for row in df.sample(n=min(30, len(df)), random_state=883).to_dict("records"):
        row.update({"source_revision": REVISION, "statement_match": None,
                    "argument_match": None, "review_notes": "",
                    "review_status": "unreviewed"})
        out.write(json.dumps(row, ensure_ascii=False) + "\n")

# Pick an observed short proof whose header and proof can be replayed together.
first = df.loc[df["id"] == 0].iloc[0]
proof = first.formal_proof
prefix = "theorem " + first["name"]
assert proof.startswith(prefix)
proof = "theorem herald_replay_0" + proof[len(prefix):]
generated = ROOT / "lean" / "generated"
generated.mkdir(parents=True, exist_ok=True)
(generated / "HeraldReplay.lean").write_text(
    first.header + "\n" + proof + "\n#print axioms herald_replay_0\n", encoding="utf-8")
print(json.dumps(report, indent=2))
