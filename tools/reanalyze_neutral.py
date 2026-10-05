"""Adjacent-state BAR from the deposited forward/reverse work samples."""
import os,sys,json
os.environ['OPENBLAS_NUM_THREADS']='1';sys.modules['jax']=None;sys.modules['jaxlib']=None
from pathlib import Path
import numpy as np
from pymbar import other_estimators
root=Path(__file__).resolve().parents[1];data=root/'data';results=[]
refs={(r['solute'],r['model']):r['endpoints'] for r in json.loads((root/'summaries/neutral_expected.json').read_text())}
for row in json.loads((data/'neutral/index.json').read_text()):
 a=np.load(data/row['file'],allow_pickle=False);inc=[];counts=[]
 for i in range(len(row['lambda'])-1):
  f=a[f'forward_{i:02d}'];r=a[f'reverse_{i:02d}'];assert np.isfinite(f).all() and np.isfinite(r).all()
  inc.append(float(other_estimators.bar(f,r)['Delta_f'])*row['kT_kcal_mol']);counts.append([len(f),len(r)])
 profile=np.r_[0,np.cumsum(inc)]
 if row['replica']<3:assert abs(profile[-1]-refs[(row['solute'],row['model'])][row['replica']])<5.1e-7
 results.append({**{k:row[k] for k in ['solute','model','replica','lambda']},'profile_kcal_mol':profile.tolist(),'sample_counts':counts})
 print(row['solute'],row['model'],row['replica'],profile[-1],flush=True)
(root/'verification/neutral_reanalysis.json').write_text(json.dumps(results,indent=2)+'\n')
