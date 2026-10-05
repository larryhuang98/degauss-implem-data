"""Recompute the nine GROMACS MBAR estimates from compact state-energy arrays."""
import os,sys,json
os.environ['OPENBLAS_NUM_THREADS']='1';sys.modules['jax']=None;sys.modules['jaxlib']=None
from pathlib import Path
import numpy as np
from pymbar import MBAR
root=Path(__file__).resolve().parents[1];data=root/'data/paper_pmemd/simulations/gmx_freesolv/runs'
expected=json.loads((root/'summaries/gromacs_expected.json').read_text())['rows'];rows=[]
for ref in expected:
 sol=ref['solute'];rep=ref['replica'];arrays=[];counts=[]
 for k in range(20):
  a=np.load(data/sol/f'replica_{rep}'/f'state_{k:02d}/dhdl.xvg.npy',allow_pickle=False)
  assert a.shape[1]==21 and (a[:,0]>=1000).all() and np.isfinite(a).all()
  arrays.append(a[:,1:].T/(.0083144621*298.15));counts.append(len(a))
 assert counts==ref['samples_per_state']
 m=MBAR(np.concatenate(arrays,axis=1),np.array(counts),relative_tolerance=1e-10)
 f=(m.f_k-m.f_k[0])*(.0083144621*298.15)/4.184
 assert np.allclose(f,ref['profile_kcal_mol'],rtol=0,atol=1e-9)
 rows.append({'solute':sol,'replica':rep,'profile_kcal_mol':f.tolist()})
 print(sol,rep,float(f[-1]),flush=True)
(root/'verification/gromacs_reanalysis.json').write_text(json.dumps(rows,indent=2)+'\n')
