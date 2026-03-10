#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from analyze_elastic_tensor import analyze as analyze_elastic
from analyze_equation_of_state import analyze as analyze_eos
from analyze_stress_state import analyze as analyze_stress


def render_markdown(eos: dict[str, object] | None, elastic: dict[str, object] | None, stress: dict[str, object] | None) -> str:
    lines = ["# Mechanics Analysis Report", ""]
    if eos is not None:
        lines.extend(
            [
                "## Equation of State",
                f"- Equilibrium volume (A^3): `{eos['equilibrium_volume_A3']:.4f}`",
                f"- Minimum energy (eV): `{eos['minimum_energy_eV']:.6f}`",
                f"- Bulk modulus (GPa): `{eos['bulk_modulus_GPa']:.4f}`",
                "",
            ]
        )
    if elastic is not None:
        lines.extend(
            [
                "## Elastic Tensor",
                f"- Voigt bulk modulus (GPa): `{elastic['bulk_modulus_voigt_GPa']:.4f}`",
                f"- Voigt shear modulus (GPa): `{elastic['shear_modulus_voigt_GPa']:.4f}`",
                "",
            ]
        )
    if stress is not None:
        lines.extend(
            [
                "## Stress State",
                f"- Mean normal stress (GPa): `{stress['mean_normal_stress_GPa']:.4f}`",
                f"- Von-Mises-like stress (GPa): `{stress['von_mises_like_GPa']:.4f}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a markdown mechanics-analysis report.")
    parser.add_argument("--eos-path")
    parser.add_argument("--elastic-path")
    parser.add_argument("--stress-path")
    parser.add_argument("--output")
    args = parser.parse_args()
    eos = analyze_eos(Path(args.eos_path).expanduser().resolve()) if args.eos_path else None
    elastic = analyze_elastic(Path(args.elastic_path).expanduser().resolve()) if args.elastic_path else None
    stress = analyze_stress(Path(args.stress_path).expanduser().resolve()) if args.stress_path else None
    if eos is None and elastic is None and stress is None:
        raise SystemExit("Provide at least one of --eos-path, --elastic-path, or --stress-path")
    output = Path(args.output).expanduser().resolve() if args.output else Path.cwd() / "MECHANICS_REPORT.md"
    output.write_text(render_markdown(eos, elastic, stress))
    print(output)


if __name__ == "__main__":
    main()
