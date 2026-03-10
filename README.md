# mechanics-analysis

Standalone skill for mechanics-relevant DFT result analysis.

## Install

```bash
npx skills add chatmaterials/mechanics-analysis -g -y
```

## Local Validation

```bash
python3 -m py_compile scripts/*.py
npx skills add . --list
python3 scripts/analyze_equation_of_state.py fixtures/eos/eos.dat --json
python3 scripts/analyze_elastic_tensor.py fixtures/elastic/elastic_tensor.dat --json
python3 scripts/analyze_stress_state.py fixtures/stress/stress_tensor.dat --json
python3 scripts/export_mechanics_report.py --eos-path fixtures/eos/eos.dat --elastic-path fixtures/elastic/elastic_tensor.dat --stress-path fixtures/stress/stress_tensor.dat
python3 scripts/run_regression.py
```
