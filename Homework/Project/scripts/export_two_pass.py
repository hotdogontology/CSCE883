"""Export small, credential-free aggregate results; never export datasets or weights."""
from datetime import datetime, timezone
import json
from pathlib import Path

from two_pass import ROOT, metadata

OUT = ROOT/'artifacts/two-pass'
DEST = ROOT/'reports/two-pass'


def optional(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (FileNotFoundError,json.JSONDecodeError):
        return {}


def export():
    DEST.mkdir(parents=True,exist_ok=True)
    runs={}
    for path in sorted(OUT.glob('*/run.json')):
        run=optional(path)
        result={k:run.get(k) for k in ['status','rows','accuracy','labeled_coverage','confusion','status_counts','predictions']}
        predictions=path.parent/'predictions.jsonl'
        if predictions.exists():
            # Last line can be in flight; count only valid, complete JSON records.
            counts={}; completed=0
            with predictions.open(encoding='utf-8') as f:
                for line in f:
                    try:r=json.loads(line)
                    except json.JSONDecodeError:continue
                    completed+=1
                    key=r.get('status','unknown');counts[key]=counts.get(key,0)+1
            result.update(records_written=completed,observed_status_counts=counts)
        spec=run.get('spec',{})
        result['settings']={k:spec.get(k) for k in ['input_sha256','adapter_sha256','base_revision',
            'prompt_sha256','max_tokens','inference','batch_size','label_scope']}
        runs[path.parent.name]=result
    training={}
    for name in ['first-pass-statement-v2','second-pass-statement']:
        data=optional(OUT/name/'training.json')
        if data:
            training[name]={k:data.get(k) for k in ['status','input_sha256','prompt_sha256','epochs',
                'learning_rate','gradient_accumulation','lora','quantization','max_tokens','used',
                'trainable_parameters','optimizer_steps','peak_vram_gib','seconds','progress','packages']}
    job=optional(OUT/'job.json')
    consensus=optional(OUT/'consensus/summary.json')
    snapshot={'observed_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'statement_fidelity_only', 'job':{k:job.get(k) for k in ['status','current_stage','stages','updated_utc']},
        'runs':runs,'training':training,'pseudo_labels':{k:consensus.get(k) for k in ['counts','labels','policy','trusted_ground_truth']},
        'interpretation':'Agreement is not accuracy. External flags are unreviewed. No argument-fidelity ground truth used.'}
    metadata(DEST/'latest.json',snapshot)
    table=['# Two-pass experiment: latest observed results','',
        f"Observed UTC: {snapshot['observed_utc']}", '',
        f"Job: **{job.get('status','unknown')}**; stage: `{job.get('current_stage','unknown')}`.", '',
        'Scope: statement correspondence, not proof-argument fidelity.','',
        '| Run | State | Records written | Labeled accuracy |',
        '| --- | --- | ---: | ---: |']
    for name,data in runs.items():
        accuracy=data.get('accuracy')
        table.append(f"| {name} | {data.get('status')} | {data.get('records_written',0)} | "
            +(f'{accuracy:.2%}' if accuracy is not None else 'not available')+' |')
    table += ['', 'First-pass validation: 79/112 correct versus 70/112 untuned; mismatch detection',
        'fell from 21/39 to 13/39. A higher YES rate alone is not improvement.', '',
        'Herald labels are predictions, including agreement-only pseudo-labels. External NO',
        'outputs are review leads; context, theorem scope and PDF formatting need review.', '',
        'Full local outputs: `artifacts/two-pass/`. Data, logs, weights and credentials',
        'are excluded from this published snapshot. See `../../two-pass-experiment.md`.']
    (DEST/'README.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
    # Six-row prediction table contains IDs, decisions and scope notes, no source text.
    external=OUT/'external-comparison.csv'
    if external.exists():
        (DEST/'external-comparison.csv').write_bytes(external.read_bytes())
    return snapshot


if __name__=='__main__':
    state=export()
    print(json.dumps({'destination':str(DEST),'job':state['job']}))
