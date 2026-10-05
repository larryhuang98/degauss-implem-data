#!/usr/bin/env python3
"""Recompute every reported AMBER hydration component from archived energy samples."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import sys,csv,gzip,json,re
from pathlib import Path
sys.modules['jax']=None;sys.modules['jaxlib']=None
import numpy as np
from pymbar import MBAR
repo=Path(__file__).resolve().parents[1];root=Path(sys.argv[1] if len(sys.argv)>1 else 'data')/'paper_pmemd/simulations/devdw_three_solutes/runs_freesolv'
expected=list(csv.DictReader((repo/'summaries/hydration_replica_mbar.csv').open()));results=[]
KT=.0019872041*300
for r in expected:
 n=int(r['n_windows']);arrays=[];counts=[];state_lambdas=[]
 for k in range(n):
  f=root/r['solute']/r['model']/r['leg']/f"replica_{r['replica']}"/f'lambda_{k:02d}'/'output.out.mbar.npy'
  state_lambdas.append(float(re.search(r'clambda\s*=\s*([-+0-9.Ee]+)',(f.parent/'prod.in').read_text())[1]))
  arr=np.load(f,allow_pickle=False)
  assert arr.shape==(5000,n) and np.isfinite(arr).all(),(f,arr.shape)
  arr=arr[1000:];arrays.append(arr/KT);counts.append(len(arr))
 estimator=MBAR(np.concatenate(arrays,axis=0).T,np.array(counts))
 profile=estimator.compute_free_energy_differences()['Delta_f'][0]*KT
 value=float(profile[-1])
 error=abs(value-float(r['delta_g_removal_kcal_mol']))
 assert error<1e-6,(r,value,error)
 labels=json.loads(Path(str(f).removesuffix('.npy')+'.json').read_text())['target_lambda']
 results.append(dict(r,recomputed=value,absolute_difference=error,lambda_values=state_lambdas,profile_kcal_mol=profile.tolist()))
 print(r['solute'],r['model'],r['leg'],r['replica'],value,flush=True)
(repo/'verification').mkdir(exist_ok=True)
(repo/'verification/hydration_reanalysis.json').write_text(json.dumps({'replica_components':results,'max_absolute_difference':max(x['absolute_difference'] for x in results)},indent=2)+'\n')
