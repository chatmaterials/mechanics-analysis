# mechanics-analysis

[![CI](https://img.shields.io/github/actions/workflow/status/chatmaterials/mechanics-analysis/ci.yml?branch=main&label=CI)](https://github.com/chatmaterials/mechanics-analysis/actions/workflows/ci.yml) [![Release](https://img.shields.io/github/v/release/chatmaterials/mechanics-analysis?display_name=tag)](https://github.com/chatmaterials/mechanics-analysis/releases)

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
