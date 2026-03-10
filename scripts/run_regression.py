#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=True)


def run_json(*args: str):
    return json.loads(run(*args).stdout)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    eos = run_json("scripts/analyze_equation_of_state.py", "fixtures/eos/eos.dat", "--json")
    ensure(abs(eos["equilibrium_volume_A3"] - 10.0) < 1e-6, "mechanics-analysis should fit the EOS minimum")
    ensure(abs(eos["bulk_modulus_GPa"] - 64.087064832) < 1e-3, "mechanics-analysis should estimate the bulk modulus")
    elastic = run_json("scripts/analyze_elastic_tensor.py", "fixtures/elastic/elastic_tensor.dat", "--json")
    ensure(abs(elastic["bulk_modulus_voigt_GPa"] - 146.6666667) < 1e-3, "mechanics-analysis should summarize the elastic tensor")
    stress = run_json("scripts/analyze_stress_state.py", "fixtures/stress/stress_tensor.dat", "--json")
    ensure(abs(stress["mean_normal_stress_GPa"] - 10.0) < 1e-6, "mechanics-analysis should compute mean stress")
    temp_dir = Path(tempfile.mkdtemp(prefix="mechanics-analysis-report-"))
    try:
        report_path = Path(
            run(
                "scripts/export_mechanics_report.py",
                "--eos-path",
                "fixtures/eos/eos.dat",
                "--elastic-path",
                "fixtures/elastic/elastic_tensor.dat",
                "--stress-path",
                "fixtures/stress/stress_tensor.dat",
                "--output",
                str(temp_dir / "MECHANICS_REPORT.md"),
            ).stdout.strip()
        )
        report_text = report_path.read_text()
        ensure("# Mechanics Analysis Report" in report_text, "mechanics report should have a heading")
        ensure("## Equation of State" in report_text and "## Elastic Tensor" in report_text and "## Stress State" in report_text, "mechanics report should include all sections")
    finally:
        shutil.rmtree(temp_dir)
    print("mechanics-analysis regression passed")


if __name__ == "__main__":
    main()
