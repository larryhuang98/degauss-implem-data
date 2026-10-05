#!/usr/bin/env python3
"""Recompute force comparison statistics directly from all deposited force arrays."""
from pathlib import Path
import json,sys
import numpy as np
repo=Path(__file__).resolve().parents[1];root=Path(sys.argv[1] if len(sys.argv)>1 else 'data')/'paper_pmemd/simulations/devdw_three_solutes/gpu_validation_codex/direct_md_path/hfe_pilot_direct/native_basis_gpu/cpu_gpu_properties_20260928';result={}
for suite,summary in [('fixed','fixed_summary.json'),('fixed_matched_mesh','fixed_matched_mesh_summary.json')]:
 ref=json.loads((root/summary).read_text());assert len(ref)==33
 for key,engines in ref.items():
  p=root/suite/key;cpu=np.load(p/'cpu.forces.npy');assert np.isfinite(cpu).all()
  for engine,target in engines.items():
   if engine not in ['spfp','dpfp']:continue
   gpu=np.load(p/f'{engine}.forces.npy');assert gpu.shape==cpu.shape and np.isfinite(gpu).all()
   diff=gpu-cpu;rms=float(np.sqrt(np.mean(diff**2)));maximum=float(abs(diff).max())
   assert abs(rms-target['force_rms_kcal_mol_A'])<1e-12,(suite,key,engine,rms)
   assert abs(maximum-target['force_max_kcal_mol_A'])<1e-12
   result[f'{suite}/{key}/{engine}']={'force_rms_kcal_mol_A':rms,'force_max_kcal_mol_A':maximum}
print('Verified 198 finite force arrays and 132 CPU/GPU comparisons.')
(repo/'verification').mkdir(exist_ok=True);(repo/'verification/fixed_force_reanalysis.json').write_text(json.dumps(result,indent=2)+'\n')
