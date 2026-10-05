#!/usr/bin/env python3
"""Recompute the water-box NVE statistics and recorded simulation rates."""
from pathlib import Path
import re,json,sys
import numpy as np
repo=Path(__file__).resolve().parents[1];root=Path(sys.argv[1] if len(sys.argv)>1 else 'data')/'_overnight'
cases={'DEGAUSS_IPS_SPFP':'nve_fair/raw_ips_spfp.out','DEGAUSS_IPS_DPFP':'nve_fair/raw_ips_dpfp.out','DEGAUSS_PME_SPFP':'nve_fair/raw_pme_spfp.out','DEGAUSS_PME_DPFP':'nve_fair/raw_pme_dpfp.out','Classical_IPS_SPFP':'nve_classical/nve_ips.out','Classical_IPS_DPFP':'nve_matrix/cl_ips_dpfp.out','Classical_PME_SPFP':'pme_hi/cl_pme_spfp.out','Classical_PME_DPFP':'pme_hi/cl_pme_dpfp.out'}
slopes={'DEGAUSS_IPS_SPFP':3.9e-8,'DEGAUSS_IPS_DPFP':2.1e-10,'DEGAUSS_PME_SPFP':3.0e-8,'DEGAUSS_PME_DPFP':3.5e-9,'Classical_IPS_SPFP':4.4e-8,'Classical_IPS_DPFP':-3.0e-10,'Classical_PME_SPFP':3.5e-8,'Classical_PME_DPFP':5.6e-9}
results={}
for name,path in cases.items():
 text=(root/path).read_text();prod=text.split('A V E R A G E S')[0]
 times=np.array([float(x) for x in re.findall(r'TIME\(PS\)\s*=\s*([-\d.]+)',prod)])
 energy=np.array([float(x) for x in re.findall(r'Etot\s*=\s*(-?[\d.]+)',prod)])
 assert len(times)==len(energy);keep=times>=80;times=times[keep];energy=energy[keep];fit=np.polyfit(times,energy,1);drift=float(fit[0]/12288)
 assert f'{drift:.1e}'==f'{slopes[name]:.1e}',(name,drift)
 results[name]={'file':path,'samples':len(times),'mean_energy_kcal_mol':float(energy.mean()),'detrended_rms_kcal_mol':float(np.std(energy-np.polyval(fit,times))),'drift_kcal_mol_atom_ps':drift,'ns_per_day':float(re.findall(r'ns/day\s*=\s*([0-9.]+)',text)[-1])}
(repo/'verification/nve_statistics.json').write_text(json.dumps(results,indent=2)+'\n');print('Eight NVE drift values reproduce the SI at its printed precision.')
