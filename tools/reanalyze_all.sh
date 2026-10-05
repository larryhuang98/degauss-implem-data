#!/bin/sh
set -eu
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PYTHON=${PYTHON:-python3}
cd "$(dirname "$0")/.."
mkdir -p verification
"$PYTHON" tools/unpack.py
for script in hydration gromacs properties aqueous fixed sodium nve neutral benchmarks; do
 "$PYTHON" "tools/reanalyze_${script}.py" > "verification/${script}.log" 2>&1
 echo "$script passed"
done
"$PYTHON" tools/plot_hydration.py
