"""Descriptive Herald training/judge plot; does not treat judgments as truth."""
import json
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'downloads/matplotlib-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

RUN=ROOT/'artifacts/informalization-14b-20261112'
loss=[json.loads(x) for x in (RUN/'training-loss.jsonl').read_text().splitlines()]
judge=[json.loads(x) for x in (RUN/'judgments.jsonl').read_text().splitlines()]
window=128
y=np.convolve([r['loss'] for r in loss],np.ones(window)/window,mode='valid')
with plt.rc_context({'font.size':9,'pdf.fonttype':42}):
    fig,ax=plt.subplots(1,2,figsize=(7,2.1),layout='constrained')
    ax[0].plot(np.arange(window,len(loss)+1),y,color='#24557a',lw=1.6)
    ax[0].set(xlabel='Training examples processed',ylabel='Completion loss (NLL)',title='Herald informalizer: training')
    ax[0].grid(alpha=.2)
    values=[sum(r['match'] is True for r in judge),sum(r['match'] is False for r in judge)]
    bars=ax[1].bar(['MATCH','MISMATCH'],values,color=['#24557a','#c67c38'],width=.55)
    ax[1].bar_label(bars,padding=3)
    ax[1].set(ylabel='Number of model judgments',ylim=(0,64),title='Held-out Herald: acceptance only')
    fig.savefig(ROOT/'paper/figures/informalization-herald.pdf')
    plt.close(fig)
print('Wrote Herald descriptive figure; counts',values)
