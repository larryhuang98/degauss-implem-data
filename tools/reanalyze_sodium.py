#!/usr/bin/env python3
"""Reproduce sodium BAR and MBAR endpoints from the deposited state-energy matrices."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys,json,importlib.util
from pathlib import Path
sys.modules['jax']=None
import numpy as np
repo=Path(__file__).resolve().parents[1];data=Path(sys.argv[1] if len(sys.argv)>1 else 'data')/'paper_pmemd';p=data/'figures'
script=data/'simulations/sodium_radius_exponential/analyze_explicit_pmemd.py';sys.path.insert(0,str(script.parent))
spec=importlib.util.spec_from_file_location('sodium_analysis',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
a=np.load(p/'sodium_charge_pmemd_energy_matrices.npz');ref=json.loads((p/'sodium_charge_summary.json').read_text());rows=[]
for campaign,target in ref.items():
 for rep in range(3):
  energy=a[f'{campaign}_rep{rep}'];m,err,b,overlap,diag=module.analyze_matrix(energy)
  for kind,values in [('mbar',m),('bar',b)]:
   expected=target[f'{kind}_endpoint_by_replica_kcal_mol'][rep]
   assert abs(float(values[-1])-expected)<1e-6,(campaign,rep,kind,values[-1],expected)
  rows.append({'campaign':campaign,'replica':rep,'mbar':float(m[-1]),'bar':float(b[-1])})
print('Reproduced all 12 sodium replica endpoints with both estimators.')
(repo/'verification').mkdir(exist_ok=True);(repo/'verification/sodium_reanalysis.json').write_text(json.dumps(rows,indent=2)+'\n')
