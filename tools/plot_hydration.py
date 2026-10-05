#!/usr/bin/env python3
"""Plot hydration profiles from the recomputed replica-level MBAR results."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1];rows=json.loads((root/'verification/hydration_reanalysis.json').read_text())['replica_components']
styles={'classical':('Classical, softcore','#4d4d4d','o'),'degauss':('DEGAUSS, direct','#0571b0','s'),'degauss_pref':('DEGAUSS, exponential prefactor','#ca0020','^')}
fig,axes=plt.subplots(2,3,figsize=(7.2,4.6),sharex=True)
for j,solute in enumerate(['benzene','methanol','ethanol']):
 for i,stage in enumerate(['elec','vdw']):
  for model,(label,color,marker) in styles.items():
   if stage=='elec' and model=='degauss_pref':continue
   selected=sorted([r for r in rows if r['solute']==solute and r['model']==model and r['leg']==stage],key=lambda x:int(x['replica']))
   data=np.array([r['profile_kcal_mol'] for r in selected]);x=selected[0]['lambda_values']
   if stage=='elec':
    gas=sorted([r for r in rows if r['solute']==solute and r['model']==model and r['leg']=='elec_gas'],key=lambda x:int(x['replica']))
    data-=np.array([r['profile_kcal_mol'] for r in gas])
   mean=data.mean(0);sd=data.std(0,ddof=1);ax=axes[i,j]
   ax.plot(x,mean,color=color,marker=marker,markersize=3,label=label);ax.fill_between(x,mean-sd,mean+sd,color=color,alpha=.2)
  axes[i,j].axhline(0,color='.8',lw=.6);axes[i,j].spines[['top','right']].set_visible(False)
  if i==0:axes[i,j].set_title(solute)
  else:axes[i,j].set_xlabel(r'$\lambda$')
  if j==0:axes[i,j].set_ylabel(('Electrostatic' if i==0 else 'van der Waals')+'\n'+r'$\Delta G$ (kcal mol$^{-1}$)')
handles,labels=axes[1,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,fontsize=8,frameon=False);fig.tight_layout(rect=[0,.08,1,1]);fig.savefig(root/'verification/hydration_profiles.pdf');fig.savefig(root/'verification/hydration_profiles.png',dpi=200)
