# %% Setup and declared experiment plan
import copy
import hashlib
import json
import os
import platform
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.model_selection import train_test_split
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

start = time.perf_counter()
torch.set_num_threads(2)
torch.use_deterministic_algorithms(True)
base = Path.cwd()
if base.name == 'question4':
    base = base.parent
elif not (base / 'question4').exists():
    base = base / 'Homework/Homework3/Homework 3 Solutions'
data_dir = base.parent / 'Homework3_revision/Homework3_revision'
out = base / 'question4/results'
out.mkdir(parents=True, exist_ok=True)
seeds = [11, 22, 33]
plan = {
    'hypothesis': 'Sequence order provides more classification information than nucleotide composition.',
    'motivation': 'DNA uses a shared alphabet; arrangements may carry more distinguishing information than overall letter frequencies.',
    'predictions': {'frequency': 'Near 50% accuracy', 'sequence_models': 'Above chance on intact sequences; substantially lower after shuffling',
                    'dinucleotides': 'Improvement over nucleotide frequencies alone'},
    'challenge': 'Frequency-only performance comparable to sequence models, little neural accuracy loss after shuffling, or no dinucleotide improvement.',
    'investigation': '4 nucleotide frequencies versus the same 4 plus 16 adjacent-pair frequencies',
    'held_fixed': 'Row splits, labels, logistic regression L2 C=1, no scaling, probability threshold 0.5, evaluation metrics',
    'split_seeds': seeds, 'split_sizes': [12000, 3000, 5000],
    'initialization_seed': 's+1000', 'loader_seed': 's+2000', 'perturbation_seed': 's+100',
    'neural_configurations': [{'optimizer': 'Adam', 'learning_rate': 0.001, 'batch_size': 128, 'weight_decay': 0.0}],
    'max_epochs': 100, 'patience': 10, 'checkpoint': 'Minimum validation BCE',
    'mlp': '1000 -> 64 ReLU -> 32 ReLU -> 1 logit',
    'cnn': '4x250 -> Conv1d(4,16,7,padding=3) ReLU -> MaxPool(2) -> Conv1d(16,32,7,padding=3) ReLU -> MaxPool(2) -> Flatten -> 32 ReLU -> 1 logit',
    'test_policy': 'Train and select every model for every split before any test evaluation.',
    'ai_decision': 'Accepted the suggestion to add dinucleotide frequencies as a direct low-cost test of neighboring-base information.',
    'checks': 'Hand-count features on ACGTA; verify row alignment and disjoint stratified splits; verify shuffled counts and invariant frequency predictions.'
}
cpu = platform.processor()
if Path('/proc/cpuinfo').exists():
    for line in Path('/proc/cpuinfo').read_text().splitlines():
        if line.startswith('model name'):
            cpu = line.split(':', 1)[1].strip()
            break
environment = {'cpu': cpu, 'logical_cpus': os.cpu_count(), 'torch_threads': 2, 'device': 'CPU',
               'os': platform.platform(), 'python': platform.python_version(), 'numpy': np.__version__,
               'pandas': pd.__version__, 'sklearn': sklearn.__version__, 'torch': torch.__version__, 'matplotlib': matplotlib.__version__}
(out / 'plan.json').write_text(json.dumps(plan, indent=2))
(out / 'environment.json').write_text(json.dumps(environment, indent=2))
print(json.dumps(plan, indent=2), flush=True)
print(json.dumps(environment, indent=2), flush=True)

# %% Data audit and features
cell_start = time.perf_counter()
seq_path = data_dir / 'humanvsran.seq.txt'
label_path = data_dir / 'humanvsran_label.txt'
sequences = seq_path.read_text().splitlines()
y = np.loadtxt(label_path, dtype=np.int64)
assert len(sequences) == len(y) == 20000
assert all(len(s) == 250 and set(s) <= set('ACGT') for s in sequences)
assert set(y) == {0, 1}
unique, counts = np.unique(y, return_counts=True)
assert list(counts) == [10000, 10000]
labels_by_sequence = {}
for sequence, label in zip(sequences, y):
    labels_by_sequence.setdefault(sequence, set()).add(int(label))
audit = {'rows': len(y), 'length': 250, 'alphabet': 'ACGT', 'class_counts': dict(zip(map(str, unique), map(int, counts))),
         'duplicate_extra_rows': len(y) - len(labels_by_sequence),
         'conflicting_sequences': sum(len(v) > 1 for v in labels_by_sequence.values()),
         'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [seq_path, label_path]}}
lookup = {base: i for i, base in enumerate('ACGT')}
encoded = np.array([[lookup[b] for b in s] for s in sequences], dtype=np.int64)
one_hot = np.eye(4, dtype=np.float32)[encoded].transpose(0, 2, 1).copy()
assert np.all(one_hot.sum(axis=1) == 1)
assert np.array_equal(one_hot.argmax(axis=1), encoded)

def features(bases):
    frequency = np.stack([(bases == i).mean(axis=1) for i in range(4)], axis=1)
    pairs = 4 * bases[:, :-1] + bases[:, 1:]
    dinucleotide = np.stack([(pairs == i).mean(axis=1) for i in range(16)], axis=1)
    return frequency, np.concatenate([frequency, dinucleotide], axis=1)

# ACGTA contains A twice and AC, CG, GT, TA once each.
f_check, d_check = features(np.array([[0, 1, 2, 3, 0]]))
np.testing.assert_allclose(f_check[0], [0.4, 0.2, 0.2, 0.2])
expected = np.zeros(16)
expected[[1, 6, 11, 12]] = 0.25
np.testing.assert_allclose(d_check[0, 4:], expected)
frequency, neighbor = features(encoded)
np.testing.assert_allclose(frequency.sum(axis=1), 1)
np.testing.assert_allclose(neighbor[:, 4:].sum(axis=1), 1)
(out / 'audit.json').write_text(json.dumps(audit, indent=2))
print('Audit:', audit, flush=True)
print(f'Data preparation runtime: {time.perf_counter() - cell_start:.3f} s', flush=True)

# %% Architectures and training functions
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(nn.Flatten(), nn.Linear(1000, 64), nn.ReLU(), nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 1))
    def forward(self, x):
        return self.layers(x).squeeze(1)

class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(nn.Conv1d(4, 16, 7, padding=3), nn.ReLU(), nn.MaxPool1d(2),
                                    nn.Conv1d(16, 32, 7, padding=3), nn.ReLU(), nn.MaxPool1d(2),
                                    nn.Flatten(), nn.Linear(32 * 62, 32), nn.ReLU(), nn.Linear(32, 1))
    def forward(self, x):
        return self.layers(x).squeeze(1)

parameter_counts = {name: sum(p.numel() for p in cls().parameters()) for name, cls in [('MLP', MLP), ('CNN', CNN)]}
print('Trainable parameters:', parameter_counts, flush=True)
criterion = nn.BCEWithLogitsLoss()
X_tensor = torch.from_numpy(one_hot)
y_tensor = torch.from_numpy(y.astype(np.float32))

def train_model(cls, seed, train_idx, val_idx):
    run_start = time.perf_counter()
    torch.manual_seed(seed + 1000)
    model = cls()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=0)
    generator = torch.Generator().manual_seed(seed + 2000)
    loader = DataLoader(TensorDataset(X_tensor[train_idx], y_tensor[train_idx]), batch_size=128,
                        shuffle=True, generator=generator, num_workers=0)
    val_loader = DataLoader(TensorDataset(X_tensor[val_idx], y_tensor[val_idx]), batch_size=512)
    best_loss, stale = float('inf'), 0
    history = []
    for epoch in range(1, 101):
        model.train()
        train_loss = 0.0
        for xb, yb in loader:
            optimizer.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(yb)
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for xb, yb in val_loader:
                val_loss += criterion(model(xb), yb).item() * len(yb)
        train_loss /= len(train_idx)
        val_loss /= len(val_idx)
        history.append({'epoch': epoch, 'train_loss': train_loss, 'val_loss': val_loss})
        if val_loss < best_loss:
            best_loss, stale, best_epoch = val_loss, 0, epoch
            best_state = copy.deepcopy(model.state_dict())
        else:
            stale += 1
        if epoch % 10 == 0:
            print(f'{cls.__name__} seed {seed} epoch {epoch}: validation BCE {val_loss:.5f}', flush=True)
        if stale >= 10:
            break
    model.load_state_dict(best_state)
    model.eval()
    torch.save(best_state, out / f'{cls.__name__}_seed{seed}.pt')
    pd.DataFrame(history).to_csv(out / f'{cls.__name__}_seed{seed}_history.csv', index=False)
    return model, {'seed': seed, 'model': cls.__name__, 'best_epoch': best_epoch, 'epochs_run': epoch,
                   'best_validation_bce': best_loss, 'runtime_seconds': time.perf_counter() - run_start}

# %% Fit and select all models before test evaluation
models, splits, training_records = {}, {}, []
for seed in seeds:
    development, test_idx = train_test_split(np.arange(len(y)), test_size=5000, stratify=y, random_state=seed)
    train_idx, val_idx = train_test_split(development, test_size=3000, stratify=y[development], random_state=seed)
    assert [len(train_idx), len(val_idx), len(test_idx)] == [12000, 3000, 5000]
    assert not (set(train_idx) & set(val_idx) or set(train_idx) & set(test_idx) or set(val_idx) & set(test_idx))
    for idx in [train_idx, val_idx, test_idx]:
        assert np.sum(y[idx] == 0) == len(idx) // 2
    np.savez(out / f'split_seed{seed}.npz', train=train_idx, validation=val_idx, test=test_idx)
    splits[seed] = (train_idx, val_idx, test_idx)
    models[seed] = {}
    for name, inputs in [('Frequency LR', frequency), ('Frequency + dinucleotide LR', neighbor)]:
        run_start = time.perf_counter()
        model = LogisticRegression(C=1, penalty='l2', solver='lbfgs', max_iter=1000, random_state=seed)
        model.fit(inputs[train_idx], y[train_idx])
        assert model.n_iter_[0] < 1000
        models[seed][name] = model
        training_records.append({'seed': seed, 'model': name, 'runtime_seconds': time.perf_counter() - run_start})
    for name, cls in [('MLP', MLP), ('CNN', CNN)]:
        model, record = train_model(cls, seed, train_idx, val_idx)
        models[seed][name] = model
        training_records.append(record)
        print('Selected:', record, flush=True)
pd.DataFrame(training_records).to_csv(out / 'training.csv', index=False)
print('All models and checkpoints fixed; beginning test evaluation.', flush=True)

# %% Original and shuffled test evaluation
cell_start = time.perf_counter()
def neural_probabilities(model, inputs):
    probabilities = []
    with torch.no_grad():
        for batch in torch.from_numpy(inputs).split(512):
            probabilities.append(torch.sigmoid(model(batch)).numpy())
    return np.concatenate(probabilities)

rows = []
for seed in seeds:
    test_idx = splits[seed][2]
    original = encoded[test_idx]
    rng = np.random.default_rng(seed + 100)
    shuffled = np.stack([rng.permutation(row) for row in original])
    np.testing.assert_array_equal(np.sort(original, axis=1), np.sort(shuffled, axis=1))
    orig_f, orig_d = features(original)
    shuffle_f, shuffle_d = features(shuffled)
    np.testing.assert_array_equal(orig_f, shuffle_f)
    condition_inputs = {'original': (one_hot[test_idx], orig_f, orig_d),
                        'shuffled': (np.eye(4, dtype=np.float32)[shuffled].transpose(0, 2, 1).copy(), shuffle_f, shuffle_d)}
    predictions = {}
    for condition, (hot, freq, dinuc) in condition_inputs.items():
        for name, model in models[seed].items():
            if name in ['MLP', 'CNN']:
                probability = neural_probabilities(model, hot)
            else:
                probability = model.predict_proba(freq if name == 'Frequency LR' else dinuc)[:, 1]
            predicted = (probability >= 0.5).astype(np.int64)
            predictions[(condition, name)] = predicted
            rows.append({'seed': seed, 'model': name, 'condition': condition,
                         'accuracy': accuracy_score(y[test_idx], predicted),
                         'balanced_accuracy': balanced_accuracy_score(y[test_idx], predicted)})
    np.testing.assert_array_equal(predictions[('original', 'Frequency LR')], predictions[('shuffled', 'Frequency LR')])
    np.savez(out / f'predictions_seed{seed}.npz', labels=y[test_idx],
             **{condition + '_' + name.replace(' ', '_'): pred for (condition, name), pred in predictions.items()})
results = pd.DataFrame(rows)
results.to_csv(out / 'per_run.csv', index=False)
summary = results.groupby(['model', 'condition'])[['accuracy', 'balanced_accuracy']].agg(['mean', 'std'])
summary.to_csv(out / 'summary.csv')
wide = results.pivot(index='seed', columns=['model', 'condition'], values='accuracy')
paired = pd.DataFrame(index=seeds)
paired.index.name = 'seed'
paired['CNN_minus_MLP_original'] = wide[('CNN', 'original')] - wide[('MLP', 'original')]
paired['dinucleotide_minus_frequency_original'] = wide[('Frequency + dinucleotide LR', 'original')] - wide[('Frequency LR', 'original')]
for name in models[seeds[0]]:
    paired[name + '_shuffle_minus_original'] = wide[(name, 'shuffled')] - wide[(name, 'original')]
paired.to_csv(out / 'paired_differences.csv')
print(results.to_string(index=False), flush=True)
print(summary.to_string(), flush=True)
print('Paired differences:', paired.to_string(), flush=True)
print(f'Test evaluation runtime: {time.perf_counter() - cell_start:.3f} s', flush=True)

# %% Figures and total runtime
fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
for ax, name in zip(axes, ['MLP', 'CNN']):
    history = pd.read_csv(out / f'{name}_seed11_history.csv')
    ax.plot(history.epoch, history.train_loss, label='Training')
    ax.plot(history.epoch, history.val_loss, label='Validation')
    ax.set(xlabel='Epoch', ylabel='Binary cross-entropy', title=f'{name}, seed 11')
    ax.legend()
fig.tight_layout()
fig.savefig(out / 'learning_curves.png', dpi=180)
plt.close(fig)
fig, ax = plt.subplots(figsize=(6, 3.5))
for seed in seeds:
    ax.plot([0, 1], [wide.loc[seed, ('Frequency LR', 'original')], wide.loc[seed, ('Frequency + dinucleotide LR', 'original')]],
            marker='o', label=f'Seed {seed}')
ax.set_xticks([0, 1], ['4 nucleotide frequencies', '+ 16 dinucleotide frequencies'])
ax.set(ylabel='Test accuracy', title='Does neighboring-base information improve classification?')
ax.legend()
fig.tight_layout()
fig.savefig(out / 'neighbor_investigation.png', dpi=180)
plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 3.5))
names = ['Frequency LR', 'MLP', 'CNN', 'Frequency + dinucleotide LR']
for offset, condition in [(-0.18, 'original'), (0.18, 'shuffled')]:
    means = [results[(results.model == n) & (results.condition == condition)].accuracy.mean() for n in names]
    deviations = [results[(results.model == n) & (results.condition == condition)].accuracy.std(ddof=1) for n in names]
    ax.bar(np.arange(4) + offset, means, width=0.36, yerr=deviations, label=condition, capsize=3)
ax.set_xticks(np.arange(4), ['Frequency LR', 'MLP', 'CNN', 'Frequency + pairs LR'])
ax.set(ylabel='Test accuracy', ylim=(0, 1), title='Original and shuffled sequences (mean and sample SD)')
ax.legend()
fig.tight_layout()
fig.savefig(out / 'shuffle_control.png', dpi=180)
plt.close(fig)
environment['total_runtime_seconds'] = time.perf_counter() - start
(out / 'environment.json').write_text(json.dumps(environment, indent=2))
print(f'Total runtime: {environment["total_runtime_seconds"]:.3f} s', flush=True)
