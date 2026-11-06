"""Exploratory local judgments; never edits source rows or human review labels."""
import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("informal_theorem", "informal_proof", "header", "formal_proof")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def pair_payload(row):
    """Whitelist evidence: exclude admitted templates, annotations, and labels."""
    for key in FIELDS:
        if not isinstance(row.get(key), str):
            raise ValueError(f"Missing or non-text field: {key}")
        if key != "header" and not row[key].strip():
            raise ValueError(f"Empty field: {key}")
    return {key: row[key] for key in FIELDS}


def parse_decision(reply):
    """Malformed responses are missing predictions, never coerced to NO."""
    value = reply.strip().upper()
    return {"YES": True, "NO": False}.get(value)


def build_messages(row, system_prompt):
    return [{"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(pair_payload(row), ensure_ascii=False)}]


def write_summary(destination):
    """Create a compact table while retaining exact inputs in predictions.jsonl."""
    with (destination / "predictions.jsonl").open(encoding="utf-8") as source, \
            (destination / "summary.csv").open("x", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["source_index", "source_id", "source_name",
                                "prediction", "status", "input_tokens", "seconds"])
        writer.writeheader()
        for line in source:
            record = json.loads(line)
            summary = {key: record.get(key) for key in writer.fieldnames}
            summary["prediction"] = ("YES" if record["prediction"] is True else
                                     "NO" if record["prediction"] is False else "")
            writer.writerow(summary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/herald/review-unlabeled.jsonl")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--max-input-tokens", type=int, default=8192)
    parser.add_argument("--max-new-tokens", type=int, default=8)
    args = parser.parse_args()
    if min(args.limit, args.max_input_tokens, args.max_new_tokens) <= 0 or args.offset < 0:
        parser.error("limits must be positive and offset nonnegative")
    source_bytes = args.input.read_bytes()
    rows = [json.loads(line) for line in source_bytes.decode("utf-8-sig").splitlines()
            if line.strip()]
    selected = rows[args.offset:args.offset + args.limit]
    if not selected:
        parser.error("No rows selected")
    manifest = json.loads((ROOT / "model-manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("download_complete"):
        parser.error("Model download is incomplete")
    prompt_path = ROOT / "prompts/fidelity-v1.txt"
    prompt = prompt_path.read_text(encoding="utf-8")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = args.output_dir or ROOT / "artifacts" / "zero-shot" / stamp
    destination.mkdir(parents=True, exist_ok=False)  # Never overwrite an earlier run.

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for this configuration")
    torch.manual_seed(883)
    started = time.perf_counter()
    path = ROOT / manifest["local_directory"]
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        path, local_files_only=True, trust_remote_code=False, use_safetensors=True,
        dtype=torch.bfloat16, device_map={"": 0}, attn_implementation="sdpa")
    model.eval()
    load_seconds = time.perf_counter() - started
    if args.max_input_tokens + args.max_new_tokens > model.config.max_position_embeddings:
        raise ValueError("Requested input/output budget exceeds model context")
    metadata = {
        "status": "running", "run_id": stamp, "model": manifest,
        "input_path": str(args.input.resolve()), "input_sha256": digest(source_bytes),
        "selected_rows": len(selected), "offset": args.offset,
        "prompt_path": "prompts/fidelity-v1.txt", "system_prompt": prompt,
        "prompt_sha256": digest(prompt.encode("utf-8")),
        "seed": 883, "enable_thinking": False, "do_sample": False,
        "dtype": "bfloat16", "attention": "sdpa", "batch_size": 1,
        "max_input_tokens": args.max_input_tokens, "max_new_tokens": args.max_new_tokens,
        "truncation": False, "gpu": torch.cuda.get_device_name(0),
        "packages": {key: importlib.metadata.version(key) for key in ("torch", "transformers")},
        "load_seconds": round(load_seconds, 3), "lean_verification": "not_run",
        "label_status": "unvalidated_model_predictions", "training": "none",
        "context_limitations": "Imported definition/lemma bodies not expanded; supplied header only",
    }
    metadata_path = destination / "run.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    counts = Counter()
    labels = Counter()
    lengths = []
    finished = False
    try:
        with (destination / "predictions.jsonl").open("x", encoding="utf-8") as output:
            for index, row in enumerate(selected, start=args.offset):
                row_started = time.perf_counter()
                record = {
                    "source_index": index, "source_id": row.get("id"),
                    "source_name": row.get("name"), "source_revision": row.get("source_revision"),
                    "source_row_sha256": digest(json.dumps(row, sort_keys=True,
                        ensure_ascii=False).encode("utf-8")),
                    "run_id": stamp, "prediction": None, "raw_response": None,
                    "label_status": "unvalidated_model_prediction", "lean_verification": "not_run",
                }
                try:
                    messages = build_messages(row, prompt)
                except ValueError as error:
                    record.update(status="missing_evidence", error=str(error))
                else:
                    record["messages"] = messages  # Exact evidence and prompt, without review labels.
                    inputs = tokenizer.apply_chat_template(messages, tokenize=True,
                        add_generation_prompt=True, enable_thinking=False,
                        return_dict=True, return_tensors="pt")
                    length = inputs["input_ids"].shape[-1]
                    record["input_tokens"] = length
                    lengths.append(length)
                    if length > args.max_input_tokens:
                        record["status"] = "input_too_long"  # Never silently truncate a proof.
                    else:
                        inputs = inputs.to("cuda")
                        try:
                            with torch.inference_mode():
                                generated = model.generate(**inputs,
                                    max_new_tokens=args.max_new_tokens, do_sample=False,
                                    pad_token_id=tokenizer.eos_token_id)
                            torch.cuda.synchronize()
                            reply = tokenizer.decode(generated[0, length:], skip_special_tokens=True).strip()
                            decision = parse_decision(reply)
                            record.update(raw_response=reply, prediction=decision,
                                status="predicted" if decision is not None else "invalid_response",
                                output_tokens=generated.shape[-1] - length)
                        except torch.OutOfMemoryError:
                            record["status"] = "cuda_out_of_memory"
                            torch.cuda.empty_cache()
                record["seconds"] = round(time.perf_counter() - row_started, 3)
                counts[record["status"]] += 1
                if record["prediction"] is not None:
                    labels["yes" if record["prediction"] else "no"] += 1
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                output.flush()
                print(json.dumps({"row": index, "status": record["status"],
                                  "prediction": record["prediction"]}), flush=True)
        finished = True
    finally:
        metadata.update(status="complete" if finished else "interrupted_or_failed",
            status_counts=dict(counts), prediction_counts=dict(labels),
            total_seconds=round(time.perf_counter() - started, 3),
            peak_allocated_vram_gib=round(torch.cuda.max_memory_allocated() / 2**30, 3),
            input_token_min=min(lengths) if lengths else None,
            input_token_max=max(lengths) if lengths else None,
            accuracy=None, calibration=None)
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(destination), "status_counts": dict(counts),
                      "prediction_counts": dict(labels)}, indent=2), flush=True)
    write_summary(destination)


if __name__ == "__main__":
    main()
