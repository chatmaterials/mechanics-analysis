---
name: "mechanics-analysis"
description: "Use when the task is to analyze mechanics-relevant quantities from DFT results, including equation-of-state fits, bulk modulus estimates, elastic tensor summaries, elastic-stability heuristics, anisotropy and hardness descriptors, candidate ranking, stress-state interpretation, and compact markdown reports from finished calculations."
---

# Mechanics Analysis

Use this skill for mechanics-oriented post-processing rather than generic workflow setup.

## When to use

- fit an energy-volume curve
- estimate an equilibrium volume and bulk modulus
- summarize an elastic tensor
- screen elastic stability heuristics, anisotropy, hardness, and ductility descriptors
- rank multiple mechanics candidates with a compact bulk-plus-stability heuristic
- interpret a stress tensor or stress state
- write a compact mechanics-analysis report from existing calculations

## Use the bundled helpers

- `scripts/analyze_equation_of_state.py`
  Fit a simple quadratic equation of state and estimate the bulk modulus.
- `scripts/analyze_elastic_tensor.py`
  Summarize a 6x6 elastic tensor, estimate Voigt/Reuss/Hill moduli, and report stability, anisotropy, hardness, and ductility heuristics.
- `scripts/analyze_stress_state.py`
  Summarize a stress tensor and estimate mean stress and a von Mises-like equivalent stress.
- `scripts/compare_mechanical_candidates.py`
  Rank multiple cases with a compact bulk-plus-stability screening heuristic.
- `scripts/export_mechanics_report.py`
  Export a markdown mechanics-analysis report.

## Guardrails

- Treat the simple EOS fit as a compact estimate, not a full published EOS treatment.
- State whether the elastic stability criteria used are heuristic or rigorous.
- Distinguish mean stress from a sign-convention-specific pressure.
