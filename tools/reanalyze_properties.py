#!/usr/bin/env python3
"""Recompute pure-liquid replica means and GPU/CPU intervals from printed MD records."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys,json,re
from pathlib import Path
import numpy as np
from scipy.stats import t
repo=Path(__file__).resolve().parents[1]
root=Path(sys.argv[1] if len(sys.argv)>1 else 'data')/'paper_pmemd/simulations/devdw_three_solutes/gpu_validation_codex/direct_md_path/hfe_pilot_direct/native_basis_gpu/pure_liquid_validation_20260930/n512'
expected=json.loads((root/'extension_methanol/summary.json').read_text());result={};largest=0
R=.00198720425864083;PV=1e5*1e-30*6.02214076e23/4184

def rows(f,discard):
 txt=f.read_text().split('A V E R A G E S')[0];ans=[]
 for m in re.finditer(r'NSTEP\s*=\s*(\d+)\s+TIME\(PS\)\s*=\s*([-+\d.Ee]+)(.*?)(?=NSTEP\s*=|\Z)',txt,re.S):
  if int(m[1])<=discard:continue
  d={k.strip():float(v) for k,v in re.findall(r'([A-Za-z0-9()_ /-]+?)\s*=\s*([-+]?\d+(?:\.\d*)?(?:[Ee][-+]?\d+)?)',m[3])};ans.append(d)
 return ans

def interval(a):
 a=np.array(a);mean=float(a.mean());half=float(t.ppf(.975,len(a)-1)*a.std(ddof=1)/np.sqrt(len(a)));return {'mean':mean,'ci95':[mean-half,mean+half]}
for sol in ['methanol','ethanol','benzene']:
 ref=expected['systems'][sol];liq={};gas={}
 for rep in range(1,5):
  r=rows(root/'gas'/sol/f'r{rep}.out',100000);assert len(r)==10000
  gas[rep]=np.mean([v['EPtot'] for v in r])
 for engine in ['cpu','spfp','dpfp']:
  liq[engine]={}
  for rep in range(1,5):
   r=rows(root/'liquid'/sol/engine/f'r{rep}.out',100000);assert len(r)==5000
   if sol=='methanol':
    extra=rows(root/'extension_methanol/liquid'/sol/engine/f'r{rep}.out',0);assert len(extra)==5000;r+=extra
   vals={k:float(np.mean([v[label] for v in r])) for k,label in [('energy','EPtot'),('density','Density'),('temperature','TEMP(K)'),('volume','VOLUME')]}
   assert all(np.isfinite(x) for x in vals.values())
   vals['hvap']=gas[rep]-vals['energy']/512+R*300-PV*vals['volume']/512
   for key in vals:
    error=abs(vals[key]-ref['liquid_replicas'][engine][str(rep)][key]);largest=max(largest,error);assert error<1e-8,(sol,engine,rep,key,error)
   liq[engine][rep]=vals
 absolute={engine:{key:interval([liq[engine][r][key] for r in range(1,5)]) for key in ['density','hvap','temperature','energy']} for engine in liq}
 for engine in absolute:
  for key in absolute[engine]:
   assert np.allclose(absolute[engine][key]['ci95'],ref['summary'][engine][key]['ci95'],atol=1e-8,rtol=0),(sol,engine,key)
 comparison={};cpu_mean=np.mean([x['density'] for x in liq['cpu'].values()])
 for engine in ['spfp','dpfp']:
  d=interval([100*(liq[engine][r]['density']-liq['cpu'][r]['density'])/cpu_mean for r in range(1,5)])
  h=interval([-(liq[engine][r]['energy']-liq['cpu'][r]['energy'])/512-PV*(liq[engine][r]['volume']-liq['cpu'][r]['volume'])/512 for r in range(1,5)])
  for name,value in [('density_relative_percent',d),('hvap_kcal_mol',h)]:
   assert np.allclose(value['ci95'],ref['comparison'][engine][name]['ci95'],atol=1e-8,rtol=0)
  comparison[engine]={'density_relative_percent':d,'hvap_kcal_mol':h}
 result[sol]={'replicas':liq,'absolute_estimates':absolute,'comparison':comparison}
print('All 36 liquid estimates, 12 gas references, 12 methanol continuations and 12 comparison intervals reproduced.')
(repo/'verification').mkdir(exist_ok=True);(repo/'verification/pure_liquid_reanalysis.json').write_text(json.dumps({'max_absolute_mean_difference':largest,'results':result},indent=2)+'\n')
