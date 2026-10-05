# DEGAUSS implementation: data and analysis

Supporting data for **DEGAUSS in AMBER: GPU Molecular Dynamics and Alchemical Free-Energy Calculations**, by Zhen Huang, Yong Duan, Xiongwu Wu, and Ray Luo (JCTC manuscript ct-2026-02085p).

This repository contains simulation inputs and parameters, numerical samples underlying the reported results, and scripts for reanalysis. The datasets cover molecular-dynamics validation, GPU timing, alchemical energy evaluation, hydration free energies, and liquid thermodynamic properties.

## Reproduce the analyses

Use Python 3.12 and the package versions in `requirements-analysis.txt`:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-analysis.txt
sh tools/reanalyze_all.sh
```

`tools/unpack.py` verifies SHA-256 checksums and extracts the datasets into `data/`. Run individual `tools/reanalyze_*.py` scripts from the repository root to analyze one dataset. Results are written to `verification/`. The checks compare reconstructed results against the deposited reference values; hydration profiles can be plotted with `tools/plot_hydration.py`.

## Dataset guide

| Dataset | Contents | Manuscript results |
|---|---|---|
| `hydration_*` | AMBER multistate energy samples, topologies, coordinates, window inputs, replica estimates | Three-solute hydration free energies; SI S7 |
| `gromacs_*` | GROMACS target-state energy differences, system files and MD parameters | GROMACS hydration reference; SI S7 |
| `neutral_paths` | Adjacent-state BAR work samples, state definitions and simulation inputs | Neutral-solute path comparison; SI S8 |
| `sodium` | Multistate energy matrices, parameters, BAR/MBAR analysis | Sodium charge transformation; SI S9 |
| `fixed_coordinate`, `static_pme`, `independent_validation` | Forces, energies, input structures and independent reference calculations | Fixed-coordinate accuracy; SI S3–S5 |
| `nve` | Energy time series, timing output and simulation inputs | Energy conservation and ordinary MD throughput; SI S4 |
| `gpu_alchemy` | Benchmark inputs, coefficient data, timing records and reconstruction controls | GPU alchemical performance and numerical checks; SI S5 |
| `aqueous_properties`, `pure_liquid` | Scalar MD records, parameters, replica summaries and validation results | Thermodynamic comparison; SI S6 |

The archives preserve simulation-relative paths so that parameters and state definitions can be traced to their calculations. Identical input files are stored once per archive using hard links. Files are split only where needed to remain below GitHub's per-file limit; the unpacker rejoins them automatically. `archives.json` contains the file inventory and checksums. `source_provenance.json` records the source checksums for the deposited selection.

## Numerical data and analysis conventions

- **AMBER hydration:** All 5,000 printed multistate records per window are stored as float64 NumPy arrays. The analysis discards the first 1,000 records. The stored values are the parsed printed values, with no additional rounding. Energies are in kcal/mol.
- **GROMACS hydration:** Arrays contain time in ps followed by the 20 target-state energy differences in kJ/mol. The deposited samples are the analysis interval, time ≥ 1,000 ps. The reference temperature is 298.15 K.
- **Neutral-solute paths:** The deposited arrays contain the forward and reverse dimensionless energy differences used by adjacent-state BAR, after the original 1,000-record discard. State indices, lambda values and kT are in `data/neutral/index.json`. The 20 retained benzene states and all reported additional replicas are included. Unused target-state energies are omitted. Nonfinite work samples are excluded by the same finite-value rule as the original analysis; retained sample counts are reported.
- **Aqueous solutions:** The scalar reanalysis uses the 69 completed NVT/NPT replicas reported in SI S6; conditions with three replicas remain separate from four-replica comparisons. Uncompleted entries in the original metadata are excluded.
- **Pure liquids:** Final methanol estimates combine the original analysis interval with the 1 ns continuation. The original ethanol, benzene and gas-reference samples are unchanged. Replica-level 95% intervals include shared gas-reference uncertainty for absolute vaporization enthalpies; that uncertainty cancels in paired backend differences. The deposited protocol specifies the remaining settings.
- **Fixed-coordinate tests:** Default-mesh and explicit matched-mesh suites are separate. Use the corresponding summary for each suite.
- **GPU benchmarks:** Individual rates and process wall times are provided. These measurements describe the reported sampling and energy-collection workload.

The release excludes production trajectories, redundant final restart files, unsuccessful setup attempts, scheduler logs, and development history. Scalar MD output and benchmark output have been trimmed to retain the numerical records used in analysis. These exclusions do not remove samples used by the supplied reanalysis scripts. The thermodynamic datasets support the properties reported in the paper; this release does not include trajectory data for unrelated transport-property analyses.

## Software

The analysis scripts and independent reference calculations are included. Running new simulations requires the corresponding AMBER/DEGAUSS or GROMACS implementation and the deposited input files. AMBER source code and executables are not distributed in this data repository.

## Citation

Bibliographic metadata are in `CITATION.cff`. A journal DOI will be added when available.
