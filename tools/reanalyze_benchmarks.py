"""Recompute medians and matched GPU timing ratios from individual benchmark records."""
from pathlib import Path
import json,statistics
root=Path(__file__).resolve().parents[1];doc=json.loads((root/'summaries/gpu_alchemy_benchmark_data.json').read_text());result={}
for sol in sorted({r['system'] for r in doc['runs']}):
 rows=[r for r in doc['runs'] if r['system']==sol];m={}
 for variant in sorted({r['variant'] for r in rows}):
  a=[r for r in rows if r['variant']==variant];assert len(a)==3
  m[variant]={k:statistics.median(r[k] for r in a) for k in ['ns_day','wall_seconds']}
 m['wall_speedup_vs_gti_rdc']=m['ti_rdc']['wall_seconds']/m['graph_basis']['wall_seconds'];result[sol]=m
(root/'verification/benchmark_reanalysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
