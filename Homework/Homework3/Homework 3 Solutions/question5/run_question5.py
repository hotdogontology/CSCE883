# %% Dependencies, hardware, and declared plan
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
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

start = time.perf_counter()
torch.set_num_threads(2)
torch.use_deterministic_algorithms(True)
base = Path.cwd()
if base.name == 'question5':
    base = base.parent
elif not (base / 'question5').exists():
    base = base / 'Homework/Homework3/Homework 3 Solutions'
data_path = base.parent / 'Homework3_revision/Homework3_revision/superconductor.csv'
out = base / 'question5/results'
out.mkdir(parents=True, exist_ok=True)
seeds = [11, 22, 33]
plan = {
    'hypothesis': 'Useful nonlinear relationships between features and critical temperature will allow an MLP to outperform ridge regression.',
    'depth_prediction': 'Two hidden layers will improve on one; a third may give diminishing returns.',
    'challenge': 'Ridge matches or outperforms the MLP, or added depth improves only training error.',
    'investigation': 'One, two (reference), and three 64-unit ReLU hidden layers; depth and parameter count both change.',
    'held_fixed': 'Splits, preprocessing, target treatment, Adam, learning rate, batch size, no dropout, zero weight decay, stopping rules.',
    'split_seeds': seeds, 'split': 'Test 20%, then validation 20% of development (64/16/20 overall).',
    'initialization_seed': 's+1000', 'loader_seed': 's+2000', 'perturbation_seed': None,
    'ridge_alphas': [0.1, 1, 10, 100], 'ridge_selection': 'Minimum validation MSE separately per split.',
    'mlp_configurations': [{'optimizer': 'Adam', 'learning_rate': 0.001, 'batch_size': 128}],
    'max_epochs': 100, 'patience': 10, 'checkpoint': 'Minimum validation MSE separately for each depth and split.',
    'feature_scaling': 'StandardScaler fit on training features only, shared by all models.',
    'target_scaling': 'StandardScaler fit on training targets only for MLPs; inverse transform before metrics.',
    'subgroup': 'Target strictly above each split training-target median; fixed before test evaluation.',
    'test_policy': 'All training and model selection across all splits finish before any test evaluation.',
    'additional_strategy': 'Propose validation-tuned polynomial interaction features for ridge; do not run an additional experiment.',
    'ai_suggestion': 'Accepted Sol suggestion to use a capacity investigation; check parameter counts, training/validation behavior, and paired test results.',
    'implementation_checks': 'Train-only scaler moments and inverse transformation; hand-computed metrics; disjoint row splits.'
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

# %% Audit and implementation checks
cell_start = time.perf_counter()
data = pd.read_csv(data_path)
assert data.shape[1] == 82 and data.columns[-1] == 'critical_temp'
X = data.iloc[:, :-1].to_numpy(dtype=np.float64)
y = data.iloc[:, -1].to_numpy(dtype=np.float64)
assert X.shape[1] == 81 and np.isfinite(X).all() and np.isfinite(y).all()
_, feature_group = np.unique(X, axis=0, return_inverse=True)
audit = {'rows': len(y), 'features': 81, 'missing_values': int(data.isna().sum().sum()),
         'nonfinite_values': int((~np.isfinite(data.to_numpy())).sum()),
         'target_min_K': float(y.min()), 'target_max_K': float(y.max()),
         'duplicate_extra_rows': int(data.duplicated().sum()),
         'duplicate_feature_extra_rows': int(data.iloc[:, :-1].duplicated().sum()),
         'sha256': hashlib.sha256(data_path.read_bytes()).hexdigest(),
         'duplicate_policy': 'Keep all supplied rows; report cross-partition repeated features as a limitation.'}
(out / 'audit.json').write_text(json.dumps(audit, indent=2))
# For targets [1, 3] and predictions [2, 2], MAE=RMSE=1 and R2=0.
assert mean_absolute_error([1, 3], [2, 2]) == 1
assert np.sqrt(mean_squared_error([1, 3], [2, 2])) == 1
assert r2_score([1, 3], [2, 2]) == 0
print('Audit:', audit, flush=True)
print(f'Audit runtime: {time.perf_counter() - cell_start:.3f} s', flush=True)

# %% Neural architecture and training
class MLP(nn.Module):
    def __init__(self, depth):
        super().__init__()
        layers = []
        input_size = 81
        for _ in range(depth):
            layers.extend([nn.Linear(input_size, 64), nn.ReLU()])
            input_size = 64
        layers.append(nn.Linear(64, 1))
        self.layers = nn.Sequential(*layers)
    def forward(self, x):
        return self.layers(x).squeeze(1)

parameter_counts = {depth: sum(p.numel() for p in MLP(depth).parameters()) for depth in [1, 2, 3]}
assert parameter_counts == {1: 5313, 2: 9473, 3: 13633}
print('MLP parameters by hidden-layer count:', parameter_counts, flush=True)
criterion = nn.MSELoss()

def train_model(depth, seed, inputs, targets, train_idx, val_idx, target_scale):
    run_start = time.perf_counter()
    torch.manual_seed(seed + 1000)
    model = MLP(depth)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=0)
    generator = torch.Generator().manual_seed(seed + 2000)
    loader = DataLoader(TensorDataset(inputs[train_idx], targets[train_idx]), batch_size=128,
                        shuffle=True, generator=generator, num_workers=0)
    val_loader = DataLoader(TensorDataset(inputs[val_idx], targets[val_idx]), batch_size=512)
    best_loss, stale = float('inf'), 0
    history = []
    for epoch in range(1, 101):
        model.train()
        training_loss = 0.0
        for xb, yb in loader:
            optimizer.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()
            training_loss += loss.item() * len(yb)
        model.eval()
        validation_loss = 0.0
        with torch.no_grad():
            for xb, yb in val_loader:
                validation_loss += criterion(model(xb), yb).item() * len(yb)
        training_loss /= len(train_idx)
        validation_loss /= len(val_idx)
        history.append({'epoch': epoch, 'train_mse_K2': training_loss * target_scale**2,
                        'val_mse_K2': validation_loss * target_scale**2})
        if validation_loss < best_loss:
            best_loss, stale, best_epoch = validation_loss, 0, epoch
            best_state = copy.deepcopy(model.state_dict())
        else:
            stale += 1
        if epoch % 20 == 0:
            print(f'MLP depth {depth}, seed {seed}, epoch {epoch}: validation MSE {validation_loss * target_scale**2:.3f} K^2', flush=True)
        if stale >= 10:
            break
    model.load_state_dict(best_state)
    model.eval()
    # Evaluate the selected checkpoint on training rows without further updates.
    train_eval = DataLoader(TensorDataset(inputs[train_idx], targets[train_idx]), batch_size=512)
    train_mse = 0.0
    with torch.no_grad():
        for xb, yb in train_eval:
            train_mse += criterion(model(xb), yb).item() * len(yb)
    train_mse = train_mse / len(train_idx) * target_scale**2
    torch.save(best_state, out / f'MLP_depth{depth}_seed{seed}.pt')
    pd.DataFrame(history).to_csv(out / f'MLP_depth{depth}_seed{seed}_history.csv', index=False)
    record = {'seed': seed, 'depth': depth, 'parameters': parameter_counts[depth], 'best_epoch': best_epoch,
              'epochs_run': epoch, 'selected_train_mse_K2': train_mse, 'best_val_mse_K2': best_loss * target_scale**2,
              'updates': epoch * len(loader), 'runtime_seconds': time.perf_counter() - run_start}
    return model, record

# %% All fitting and selection before testing
models, splits, scalers, thresholds = {}, {}, {}, {}
training_records, ridge_records, overlap_records = [], [], []
for seed in seeds:
    development, test_idx = train_test_split(np.arange(len(y)), test_size=0.2, random_state=seed)
    train_idx, val_idx = train_test_split(development, test_size=0.2, random_state=seed)
    assert not (set(train_idx) & set(val_idx) or set(train_idx) & set(test_idx) or set(val_idx) & set(test_idx))
    splits[seed] = (train_idx, val_idx, test_idx)
    np.savez(out / f'split_seed{seed}.npz', train=train_idx, validation=val_idx, test=test_idx)
    feature_scaler = StandardScaler().fit(X[train_idx])
    target_scaler = StandardScaler().fit(y[train_idx, None])
    np.testing.assert_allclose(feature_scaler.mean_, X[train_idx].mean(axis=0), rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(feature_scaler.var_, X[train_idx].var(axis=0), rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(target_scaler.mean_[0], y[train_idx].mean())
    scaled_X = feature_scaler.transform(X)
    scaled_y = target_scaler.transform(y[:, None]).ravel()
    np.testing.assert_allclose(target_scaler.inverse_transform(scaled_y[train_idx, None]).ravel(), y[train_idx], atol=1e-12)
    thresholds[seed] = float(np.median(y[train_idx]))
    scalers[seed] = (feature_scaler, target_scaler)
    np.savez(out / f'scalers_seed{seed}.npz', feature_mean=feature_scaler.mean_, feature_scale=feature_scaler.scale_,
             target_mean=target_scaler.mean_, target_scale=target_scaler.scale_)
    train_groups = set(feature_group[train_idx])
    overlap_records.append({'seed': seed, 'train_rows': len(train_idx), 'validation_rows': len(val_idx), 'test_rows': len(test_idx),
                            'subgroup_threshold_K': thresholds[seed],
                            'validation_rows_with_training_features': sum(int(g in train_groups) for g in feature_group[val_idx]),
                            'test_rows_with_training_features': sum(int(g in train_groups) for g in feature_group[test_idx])})
    run_start = time.perf_counter()
    best_ridge_mse = float('inf')
    for alpha in [0.1, 1, 10, 100]:
        ridge = Ridge(alpha=alpha).fit(scaled_X[train_idx], y[train_idx])
        mse = mean_squared_error(y[val_idx], ridge.predict(scaled_X[val_idx]))
        ridge_records.append({'seed': seed, 'alpha': alpha, 'validation_mse_K2': mse})
        if mse < best_ridge_mse:
            best_ridge, best_alpha, best_ridge_mse = ridge, alpha, mse
    models[seed] = {'Mean': float(y[train_idx].mean()), 'Ridge': best_ridge}
    np.savez(out / f'ridge_seed{seed}.npz', coefficients=best_ridge.coef_, intercept=best_ridge.intercept_, alpha=best_alpha)
    print(f'Seed {seed}: ridge alpha={best_alpha}, validation MSE={best_ridge_mse:.3f}, ridge fitting time={time.perf_counter() - run_start:.3f} s', flush=True)
    inputs = torch.from_numpy(scaled_X.astype(np.float32))
    targets = torch.from_numpy(scaled_y.astype(np.float32))
    # Train the two-layer reference first; variants use its same declared configuration.
    for depth in [2, 1, 3]:
        model, record = train_model(depth, seed, inputs, targets, train_idx, val_idx, float(target_scaler.scale_[0]))
        models[seed][f'MLP {depth}'] = model
        training_records.append(record)
        print('Selected:', record, flush=True)
pd.DataFrame(training_records).to_csv(out / 'training.csv', index=False)
pd.DataFrame(ridge_records).to_csv(out / 'ridge_validation.csv', index=False)
pd.DataFrame(overlap_records).to_csv(out / 'split_audit.csv', index=False)
print('All models, checkpoints, and subgroup thresholds fixed; beginning test evaluation.', flush=True)

# %% Metrics, subgroups, and paired comparisons
cell_start = time.perf_counter()
rows, subgroup_rows = [], []
for seed in seeds:
    test_idx = splits[seed][2]
    feature_scaler, target_scaler = scalers[seed]
    scaled_test = feature_scaler.transform(X[test_idx])
    test_y = y[test_idx]
    high = test_y > thresholds[seed]
    prediction_arrays = {'target': test_y}
    for name, model in models[seed].items():
        if name == 'Mean':
            predicted = np.full(len(test_idx), model)
        elif name == 'Ridge':
            predicted = model.predict(scaled_test)
        else:
            with torch.no_grad():
                standardized = np.concatenate([model(batch).numpy() for batch in torch.from_numpy(scaled_test.astype(np.float32)).split(512)])
            predicted = target_scaler.inverse_transform(standardized[:, None]).ravel().astype(np.float64)
        prediction_arrays[name.replace(' ', '_')] = predicted
        rows.append({'seed': seed, 'model': name, 'r2': r2_score(test_y, predicted),
                     'mae_K': mean_absolute_error(test_y, predicted), 'rmse_K': np.sqrt(mean_squared_error(test_y, predicted))})
        for group, mask in [('above_train_median', high), ('at_or_below_train_median', ~high)]:
            subgroup_rows.append({'seed': seed, 'model': name, 'group': group, 'threshold_K': thresholds[seed],
                                  'count': int(mask.sum()), 'mae_K': mean_absolute_error(test_y[mask], predicted[mask])})
    np.savez(out / f'predictions_seed{seed}.npz', **prediction_arrays)
results = pd.DataFrame(rows)
subgroups = pd.DataFrame(subgroup_rows)
results.to_csv(out / 'per_run.csv', index=False)
subgroups.to_csv(out / 'subgroups.csv', index=False)
summary = results.groupby('model')[['r2', 'mae_K', 'rmse_K']].agg(['mean', 'std'])
summary.to_csv(out / 'summary.csv')
paired = []
for seed in seeds:
    scores = results[results.seed == seed].set_index('model')
    for name, reference in [('MLP 2', 'Ridge'), ('MLP 1', 'MLP 2'), ('MLP 3', 'MLP 2'), ('MLP 2', 'Mean')]:
        row = {'seed': seed, 'comparison': name + ' minus ' + reference}
        for metric in ['r2', 'mae_K', 'rmse_K']:
            row[metric] = scores.loc[name, metric] - scores.loc[reference, metric]
        paired.append(row)
paired = pd.DataFrame(paired)
paired.to_csv(out / 'paired_differences.csv', index=False)
print(results.to_string(index=False), flush=True)
print('Summary:', summary.to_string(), flush=True)
print('Subgroup results:', subgroups[subgroups.model.isin(['Ridge', 'MLP 2'])].to_string(index=False), flush=True)
print('Paired differences:', paired.to_string(index=False), flush=True)
print(f'Test evaluation runtime: {time.perf_counter() - cell_start:.3f} s', flush=True)

# %% Required figures and runtime
fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
for depth in [1, 2, 3]:
    history = pd.read_csv(out / f'MLP_depth{depth}_seed11_history.csv')
    axes[0].plot(history.epoch, history.train_mse_K2, label=f'{depth} layer(s)')
    axes[1].plot(history.epoch, history.val_mse_K2, label=f'{depth} layer(s)')
for ax, title in zip(axes, ['Training, seed 11', 'Validation, seed 11']):
    ax.set(xlabel='Epoch', ylabel='MSE (K²)', title=title)
    ax.legend()
fig.tight_layout()
fig.savefig(out / 'learning_curves.png', dpi=180)
plt.close(fig)
fig, ax = plt.subplots(figsize=(6, 3.5))
for seed in seeds:
    scores = results[results.seed == seed].set_index('model')
    improvement = [scores.loc['Ridge', 'rmse_K'] - scores.loc[f'MLP {depth}', 'rmse_K'] for depth in [1, 2, 3]]
    ax.plot([1, 2, 3], improvement, marker='o', label=f'Seed {seed}')
ax.axhline(0, color='gray', linestyle='--')
ax.set(xlabel='Number of 64-unit hidden layers', ylabel='Ridge RMSE − MLP RMSE (K)', title='Does added depth improve the MLP advantage?')
ax.set_xticks([1, 2, 3])
ax.legend()
fig.tight_layout()
fig.savefig(out / 'capacity_investigation.png', dpi=180)
plt.close(fig)
pred = np.load(out / 'predictions_seed11.npz')
fig, ax = plt.subplots(figsize=(6, 3.5))
ax.scatter(pred['target'], pred['target'] - pred['MLP_2'], s=7, alpha=0.25)
ax.axhline(0, color='black', linestyle='--')
ax.set(xlabel='Observed critical temperature (K)', ylabel='Observed − predicted (K)', title='Base MLP residuals, seed 11')
fig.tight_layout()
fig.savefig(out / 'residuals_seed11.png', dpi=180)
plt.close(fig)
environment['total_runtime_seconds'] = time.perf_counter() - start
(out / 'environment.json').write_text(json.dumps(environment, indent=2))
print(f'Total runtime: {environment["total_runtime_seconds"]:.3f} s', flush=True)
