"""Recompute aqueous scalar thermodynamic estimates; trajectory-based dynamics are excluded."""
import os,json,sys,importlib.util
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
from scipy.stats import t
repo=Path(__file__).resolve().parents[1]
root=repo/'data/paper_pmemd/simulations/devdw_three_solutes/gpu_validation_codex/direct_md_path/hfe_pilot_direct/native_basis_gpu/cpu_gpu_properties_20260928'
spec=importlib.util.spec_from_file_location('record_parser',root/'common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ref=json.loads((root/'property_metrics.json').read_text());result={};count=0
for key,engines in ref.items():
 sol,ensemble=key.split('/');n=len(m.values((root/'systems'/sol/'reference.prmtop').read_text(),'MASS'));result[key]={}
 if ensemble not in ['nvt','npt']:continue
 for engine,replicas in engines.items():
  vals=[]
  for rep,expected in enumerate(replicas,1):
   if expected is None:continue
   rows=[r for r in m.records(root/'production'/sol/engine/f'{ensemble}_r{rep}.out') if r['step']>20000]
   u=np.array([r['EPtot'] for r in rows]);a={'temperature_K':float(np.mean([r['TEMP(K)'] for r in rows])),'potential_kcal_mol_atom':float(u.mean()/n),'potential_variance_kcal2_mol2':float(u.var(ddof=1)),'samples':len(rows)}
   if ensemble=='npt':a.update(density_g_cm3=float(np.mean([r['Density'] for r in rows])),volume_A3=float(np.mean([r['VOLUME'] for r in rows])))
   for k,v in a.items():assert abs(v-expected[k])<1e-9,(key,engine,rep,k,v,expected[k])
   vals.append(a);count+=1
  result[key][engine]=vals
print('Reproduced',count,'aqueous NVT/NPT scalar replica estimates.')
(repo/'verification/aqueous_reanalysis.json').write_text(json.dumps(result,indent=2)+'\n')
