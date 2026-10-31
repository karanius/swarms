import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
BASE=Path(__file__).resolve().parents[1]/'paper-6-corpus'
def main():
 data=json.loads((BASE/'patterns/index.json').read_text());rules=json.loads((BASE/'patterns/all-rules.json').read_text());out=BASE/'patterns/figures';out.mkdir(exist_ok=True)
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
 s=data['stats'];fig,ax=plt.subplots(figsize=(8,3.6));names=['Assessable edge neighborhoods','No recorded incident edge','Unknown incident record / self-loop','Above 24-feature bound'];counts=[s['assessableNeighborhoods'],s['excludedNeighborhoods'].get('no-recorded-incident-edge',0),s['excludedNeighborhoods'].get('unknown-endpoint-type-port-or-self-loop',0),s['excludedNeighborhoods'].get('neighborhood-size-bound',0)]
 ax.barh(names[::-1],counts[::-1],color=['#b8bfc8','#c89a77','#bbaad9','#468b80']);ax.set_xlabel('Component occurrences (not independent observations)');ax.set_title('Neighborhood inclusion in 1,149 nonfixture graph objects')
 for y,v in enumerate(counts[::-1]):ax.text(v+50,y,f'{v:,}',va='center')
 ax.set_xlim(0,max(counts)*1.12);fig.tight_layout();fig.savefig(out/'coverage.png',dpi=160);plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(10,3.8));axes[0].hist([r['confidence'] for r in rules],bins=10,range=(0,1),color='#468b80',edgecolor='white');axes[0].set_xlabel('Observed neighborhood confidence');axes[0].set_ylabel('Directional associations');axes[0].set_title('890 associations (paired directions included)')
 axes[1].scatter([r['jointFamilyCount'] for r in rules],[r['confidence'] for r in rules],s=12,alpha=.55,color='#78649c');axes[1].set_xlabel('Recorded source groups with joint witnesses');axes[1].set_ylabel('Observed confidence');axes[1].set_ylim(0,1.04);axes[1].set_title('Confidence and source breadth are different')
 fig.tight_layout();fig.savefig(out/'association-distribution.png',dpi=160);plt.close(fig)
 print('Saved two measured-data figures.')
if __name__=='__main__':main()
