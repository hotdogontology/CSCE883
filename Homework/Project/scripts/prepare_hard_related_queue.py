"""Freeze source-hashed inputs and the ordered overnight model queue."""
import argparse
import json
from pathlib import Path

from run_hard_related_experiment import ROOT, OUT, REPORT, digest, read, save, validate_queue


def relative(path):
    return path.relative_to(ROOT).as_posix()


def combine(path, sources):
    rows = [r for source in sources for r in read(source)]
    assert len({r['id'] for r in rows}) == len(rows)
    text = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
    if path.exists() and path.read_text(encoding='utf-8') != text:
        raise ValueError('Combined input changed; preserve old file and version outputs')
    path.write_text(text, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-unstarted', action='store_true')
    args = parser.parse_args()
    data = OUT / 'data'
    core = ROOT / 'artifacts/argument-14b/core/test.jsonl'
    manifest = json.loads((data / 'manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['files'].items():
        assert digest(data / name) == expected
    direct = OUT / 'direct-evaluation.jsonl'
    intermediary = OUT / 'intermediary-evaluation.jsonl'
    combine(direct, [data / 'validation.jsonl', data / 'test.jsonl', core])
    combine(intermediary, [data / 'test.jsonl', core])
    base_files = ['scripts/argument_model.py', 'scripts/argument_data.py',
                  'prompts/argument-v1.txt', 'model-manifest-14b.json']
    stages = []
    evaluation = {'validation': relative(data / 'validation.jsonl'), 'test': relative(data / 'test.jsonl'),
                  'previous_same_theorem_diagnostic': relative(core)}
    for name, action, input_path in [('untuned-direct', 'predict', direct),
                                     ('fine-tuned', 'train', data / 'train.jsonl'),
                                     ('tuned-direct', 'predict', direct)]:
        output = OUT / name
        command = ['scripts/argument_model.py', action, '--input', relative(input_path),
                   '--output', relative(output), '--max-tokens', '4096']
        files = base_files + [relative(input_path)]
        if name == 'tuned-direct':
            adapter = OUT / 'fine-tuned/adapter'
            command += ['--adapter', relative(adapter)]
            files += [relative(adapter / 'adapter_model.safetensors'), relative(adapter / 'adapter_config.json')]
        stages.append({'name': name, 'command': command, 'output': relative(output),
                       'marker': relative(output / ('training.json' if action == 'train' else 'run.json')),
                       'fingerprint_files': files, 'depends_on': ['fine-tuned'] if name == 'tuned-direct' else [],
                       'evaluation_sets': evaluation if action == 'predict' else {}, 'timeout_seconds': 4 * 3600})
    for architecture in ['nl_to_lean', 'lean_to_nl', 'verbose_lean', 'natural_lean']:
        output = OUT / architecture
        command = ['scripts/intermediary_model.py', '--architecture', architecture,
                   '--input', relative(intermediary), '--output', relative(output),
                   '--cache-dir', relative(OUT / 'generation-cache'), '--max-tokens', '4096', '--max-new-tokens', '1536']
        files = base_files + ['scripts/intermediary_model.py', relative(intermediary)]
        if architecture in ['verbose_lean', 'natural_lean']:
            guide = 'prompts/intermediary-' + architecture.replace('_', '-') + '.txt'
            command += ['--guide', guide]
            files += [guide]
        stages.append({'name': architecture, 'command': command, 'output': relative(output),
                       'marker': relative(output / 'run.json'), 'fingerprint_files': files,
                       'depends_on': [], 'evaluation_sets': {k: v for k, v in evaluation.items() if k != 'validation'},
                       'timeout_seconds': 6 * 3600})
    compiler_out = OUT / 'compilation'
    stages.append({'name': 'compilation',
                   'command': ['scripts/check_intermediary_compilation.py', '--cache-dir', relative(OUT / 'generation-cache'),
                               '--output', relative(compiler_out), '--timeout', '60'],
                   'output': relative(compiler_out), 'marker': relative(compiler_out / 'summary.json'),
                   'fingerprint_files': ['scripts/check_intermediary_compilation.py', 'scripts/argument_data.py'],
                   'fingerprint_directories': [relative(OUT / 'generation-cache')],
                   'depends_on': [], 'evaluation_sets': {}, 'timeout_seconds': 4 * 3600})
    inputs = {relative(p): digest(p) for p in [data / 'manifest.json', data / 'train.jsonl',
              data / 'validation.jsonl', data / 'test.jsonl', direct, intermediary, core]}
    for stage in stages:
        for filename in stage['fingerprint_files']:
            if (ROOT / filename).exists():
                inputs[filename] = digest(ROOT / filename)
    for filename in ['scripts/run_hard_related_experiment.py', 'scripts/classification_metrics.py']:
        inputs[filename] = digest(ROOT / filename)
    config = {'label_policy': manifest['positive_policy'] + ' ' + manifest['negative_policy'],
              'inputs': inputs, 'stages': stages}
    validate_queue(config)
    dest = OUT / 'queue.json'
    if dest.exists() and json.loads(dest.read_text(encoding='utf-8')) != config:
        if not args.refresh_unstarted or (OUT / 'job.json').exists() or list(OUT.glob('*.provenance.json')):
            raise ValueError('Queue already frozen with different contents')
        old = digest(dest)
        archive = OUT / ('queue-preflight-' + old[:12] + '.json')
        if not archive.exists():
            archive.write_bytes(dest.read_bytes())
    save(dest, config)
    save(REPORT / 'queue.json', config)
    print(json.dumps({'status': 'frozen', 'stages': len(stages), 'direct_rows': len(read(direct)),
                      'intermediary_rows': len(read(intermediary))}))


if __name__ == '__main__':
    main()
