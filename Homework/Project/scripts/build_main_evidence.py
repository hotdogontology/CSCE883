"""Compact main-paper evidence; retains every classification row and ROC/PR panel."""
import json
import math
from collections import defaultdict
from build_paper_results import ROOT, PAPER, TABLES, FIGURES, table, tex
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, precision_recall_curve

snapshot=json.loads((PAPER/'results-snapshot.json').read_text())
records=snapshot['results']
names={'statements':'8B statements','random-swap':'14B random swaps','forest':'Paired forest',
       'related-swap':'14B related swaps','intermediaries':'Intermediaries',
       'pilot32':'32B pilot','informalization-proofnet':'ProofNet informalizer',
       'english-control':'English-only control','masked-control':'Lean-withheld control'}
groups=defaultdict(list)
for r in records: groups[r['family']].append(r)
ordered=[r for family in names for r in groups[family]]
def highlight(r, key):
    peers=[p for p in ordered if (p['family'],p['split'])==(r['family'],r['split'])]
    value=r[key]
    rendered=f'{value:.3f}'
    if len(peers)>1 and math.isclose(value,max(p[key] for p in peers),rel_tol=0,abs_tol=1e-12):
        return r'\textbf{'+rendered+'}'
    return rendered
rows=[]
for r in ordered:
    rows.append([names[r['family']],tex(r['model']),tex(r['split']),f"{r['scored']}/{r['total']}",
                 *[highlight(r,k) for k in ('accuracy','mismatch_precision','mismatch_recall','mismatch_f1','macro_f1','auroc','average_precision')]])
table('main-metrics',r'All classification experiments and controls. Bold: highest observed score within each protocol and evaluation set (ties included; singleton groups unhighlighted). Intermediary metrics are conditional on unequal scored subsets, not a controlled ranking.',
      ['Protocol','Model','Evaluation',r'$n/N$','Acc.',r'$P_-$',r'$R_-$',r'$F1_-$','Macro F1','AUROC','AP'],rows,'lllrrrrrrrr',group_column=0)
rows=[]
for r in ordered:
    (tp,fn),(fp,tn)=r['confusion_matrix']
    matrix=r'$\left[\begin{smallmatrix}'+f'{tp}&{fn}'+r'\\'+f'{fp}&{tn}'+r'\end{smallmatrix}\right]$'
    rows.append([names[r['family']],tex(r['model']),tex(r['split']),matrix,str(fn),str(fp)])
table('main-confusion','All confusion matrices: actual rows / predicted columns; order (mismatch, match). False acceptance = FN; false rejection = FP.',
      ['Protocol','Model','Evaluation','Matrix','False accepts','False rejects'],rows,'lllcrr')

panels=defaultdict(list)
for r in ordered: panels[(r['family'],r['split'])].append(r)
def read(p):
    p=ROOT/p
    return json.loads(p.read_text()) if p.suffix=='.json' else [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines()]
plt.rcParams.update({'font.size':6,'axes.titlesize':6.5,'axes.labelsize':6})
for kind in ('roc','pr'):
    fig,axes=plt.subplots(math.ceil(len(panels)/3),3,figsize=(7.2,7.7),squeeze=False)
    for ax,((family,split),rs) in zip(axes.flat,panels.items()):
        for r in rs:
            truth={x['id']:x['label'] for x in read(r['truth_source'])}
            pred=[x for x in read(r['prediction_source']) if x['id'] in truth and type(x.get('prediction')) is bool]
            y=[not truth[x['id']] for x in pred]; score=[-float(x[r['score_field']]) for x in pred]
            if kind=='roc': x,z,_=roc_curve(y,score)
            else: z,x,_=precision_recall_curve(y,score)
            ax.plot(x,z,label=r['model'],lw=.9)
        if kind=='roc': ax.plot([0,1],[0,1],'--',color='gray',lw=.5)
        ax.set(title=names[family]+' / '+split,xlim=(-.03,1.03),ylim=(-.03,1.03),
               xlabel='False positive rate' if kind=='roc' else 'Mismatch recall',
               ylabel='Mismatch recall' if kind=='roc' else 'Mismatch precision')
        ax.legend(fontsize=5,loc='best',framealpha=.85,labelspacing=.15,handlelength=1)
        ax.grid(alpha=.15)
    for ax in list(axes.flat)[len(panels):]: ax.set_visible(False)
    fig.tight_layout(pad=.7,h_pad=1,w_pad=1)
    fig.savefig(FIGURES/f'main-{kind}.pdf',bbox_inches='tight')
    plt.close(fig)
print(f'Restored {len(records)} metric rows, {len(records)} matrices, and {len(panels)} panels per ROC/PR figure.')
