#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


GPA_PER_EV_A3 = 160.21766208


def solve_3x3(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    a = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    n = 3
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(a[r][i]))
        a[i], a[pivot] = a[pivot], a[i]
        factor = a[i][i]
        if abs(factor) < 1e-14:
            raise SystemExit("Singular matrix in EOS fit")
        for j in range(i, n + 1):
            a[i][j] /= factor
        for r in range(n):
            if r == i:
                continue
            scale = a[r][i]
            for j in range(i, n + 1):
                a[r][j] -= scale * a[i][j]
    return [a[i][n] for i in range(n)]


def analyze(path: Path) -> dict[str, object]:
    rows = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        rows.append((float(parts[0]), float(parts[1])))
    if len(rows) < 3:
        raise SystemExit("At least three (V,E) points are required")
    s_v4 = sum(v**4 for v, _ in rows)
    s_v3 = sum(v**3 for v, _ in rows)
    s_v2 = sum(v**2 for v, _ in rows)
    s_v1 = sum(v for v, _ in rows)
    s_e = sum(e for _, e in rows)
    s_v2e = sum(v * v * e for v, e in rows)
    s_ve = sum(v * e for v, e in rows)
    a, b, c = solve_3x3(
        [
            [s_v4, s_v3, s_v2],
            [s_v3, s_v2, s_v1],
            [s_v2, s_v1, float(len(rows))],
        ],
        [s_v2e, s_ve, s_e],
    )
    if abs(a) < 1e-14:
        raise SystemExit("Quadratic coefficient vanished in EOS fit")
    v0 = -b / (2.0 * a)
    e0 = a * v0 * v0 + b * v0 + c
    bulk_gpa = v0 * (2.0 * a) * GPA_PER_EV_A3
    residuals = [a * v * v + b * v + c - e for v, e in rows]
    rmse_eV = (sum(value * value for value in residuals) / len(residuals)) ** 0.5
    max_abs_residual_meV = max(abs(value) for value in residuals) * 1000.0
    compressibility_tpa = 1000.0 / bulk_gpa if abs(bulk_gpa) > 1e-14 else None
    if max_abs_residual_meV < 1.0:
        quality = "exact-like"
    elif max_abs_residual_meV < 5.0:
        quality = "good-fit-like"
    else:
        quality = "noisy-fit-like"
    return {
        "path": str(path),
        "equilibrium_volume_A3": v0,
        "minimum_energy_eV": e0,
        "quadratic_a": a,
        "bulk_modulus_GPa": bulk_gpa,
        "compressibility_TPa^-1": compressibility_tpa,
        "fit_rmse_meV": rmse_eV * 1000.0,
        "max_abs_residual_meV": max_abs_residual_meV,
        "eos_quality_class": quality,
        "observations": ["Quadratic equation-of-state fit completed."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an energy-volume dataset.")
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.path).expanduser().resolve())
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
