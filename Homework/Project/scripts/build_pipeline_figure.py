"""Build the vector pipeline diagram used in the paper and presentation."""
from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / 'downloads/matplotlib-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.8, 2.2))
ax.set(xlim=(0, 10), ylim=(0, 4))
ax.axis('off')
def box(x, y, s, color):
    ax.text(x, y, s, ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=.5', facecolor=color, edgecolor='#31475d'))
def arrow(a, b):
    ax.annotate('', xy=b, xytext=a, arrowprops=dict(arrowstyle='->', color='#31475d', lw=1.5))
box(1.1, 2.8, 'Lean proof\n+ context', '#edf2f7')
box(4.0, 2.8, 'LoRA-trained\ninformalizer', '#d5e9f5')
box(7.1, 2.8, 'Generated\nEnglish', '#edf2f7')
box(1.6, .75, 'Original English proof', '#edf2f7')
box(6.1, .75, 'Original Qwen judge', '#dcebd8')
box(9.1, .75, 'Match /\nmismatch', '#edf2f7')
arrow((2.15, 2.8), (2.8, 2.8)); arrow((5.2, 2.8), (6.0, 2.8))
arrow((7.1, 2.1), (6.4, 1.3)); arrow((3.15, .75), (4.55, .75))
arrow((7.7, .75), (8.4, .75))
fig.subplots_adjust(left=.01, right=.99, top=.99, bottom=.01)
fig.savefig(ROOT / 'paper/figures/pipeline.pdf')
plt.close(fig)
