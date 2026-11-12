"""Read-only Colibri placement probe on the existing 14B checkpoint, no inference."""
from pathlib import Path
import json
import os
import subprocess
import sys

from prepare_intermediary_sources import BASE, ROOT, REPOS


def main():
    revision = REPOS['colibri'][1]
    source = BASE / ('colibri-' + revision)
    env = dict(os.environ)
    env['COLI_DENSE_I8'] = '0'
    command = [sys.executable, str(source / 'c/coli'), 'plan', '--model',
               str(ROOT / 'data/models/Qwen3-14B'), '--ram', '100', '--vram', '40',
               '--ctx', '4096', '--no-tune-profile', '--policy', 'quality', '--json']
    run = subprocess.run(command, env=env, text=True, encoding='utf-8', capture_output=True, check=True)
    result = json.loads(run.stdout)
    (BASE / 'colibri-plan-14b.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    summary = {'repository': REPOS['colibri'][0], 'revision': revision,
               'action': 'planner_only_no_inference_or_engine_build',
               'command': command, 'explicit_environment': {'COLI_DENSE_I8': '0'},
               'model': {key: result['model'][key] for key in ['model_type', 'family_id', 'model_bytes', 'expert_count']},
               'cpu': result['cpu'], 'memory': result['memory'], 'tiers': result['tiers'],
               'expected_bottleneck': result['expected_bottleneck'], 'warnings': result['warnings'],
               'caution': 'Placement estimates are not measured peak RAM/VRAM; code loads unquantized dense matrices as float32 unless another path is selected. No 32B feasibility or throughput measured.'}
    report = ROOT / 'reports/intermediary-sources-20261110'
    report.mkdir(parents=True, exist_ok=True)
    (report / 'colibri-planner.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'family': summary['model'], 'expected_bottleneck': summary['expected_bottleneck']}))


if __name__ == '__main__':
    main()
