#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def solve_linear_system(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    a = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    n = len(matrix)
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(a[r][i]))
        a[i], a[pivot] = a[pivot], a[i]
        factor = a[i][i]
        if abs(factor) < 1e-14:
            raise SystemExit("Singular elastic tensor encountered while solving a linear system")
        for j in range(i, n + 1):
            a[i][j] /= factor
        for r in range(n):
            if r == i:
                continue
            scale = a[r][i]
            for j in range(i, n + 1):
                a[r][j] -= scale * a[i][j]
    return [a[i][n] for i in range(n)]


def invert_matrix(matrix: list[list[float]]) -> list[list[float]]:
    size = len(matrix)
    inverse = []
    for column in range(size):
        rhs = [0.0] * size
        rhs[column] = 1.0
        inverse.append(solve_linear_system(matrix, rhs))
    return [[inverse[col][row] for col in range(size)] for row in range(size)]


def is_positive_definite(matrix: list[list[float]]) -> bool:
    lower = [[0.0] * len(matrix) for _ in range(len(matrix))]
    for i in range(len(matrix)):
        for j in range(i + 1):
            value = matrix[i][j] - sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if value <= 1e-12:
                    return False
                lower[i][j] = value**0.5
            else:
                lower[i][j] = value / lower[j][j]
    return True


def analyze(path: Path) -> dict[str, object]:
    rows = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 6:
            continue
        rows.append([float(x) for x in parts[:6]])
    if len(rows) != 6:
        raise SystemExit("Elastic tensor file must contain 6 rows with at least 6 columns")
    tensor = [[0.5 * (rows[i][j] + rows[j][i]) for j in range(6)] for i in range(6)]
    c11, c22, c33 = tensor[0][0], tensor[1][1], tensor[2][2]
    c12, c13, c23 = tensor[0][1], tensor[0][2], tensor[1][2]
    c44, c55, c66 = tensor[3][3], tensor[4][4], tensor[5][5]
    bulk_voigt = (c11 + c22 + c33 + 2.0 * (c12 + c13 + c23)) / 9.0
    shear_voigt = (c11 + c22 + c33 - c12 - c13 - c23 + 3.0 * (c44 + c55 + c66)) / 15.0
    compliance = invert_matrix(tensor)
    s11, s22, s33 = compliance[0][0], compliance[1][1], compliance[2][2]
    s12, s13, s23 = compliance[0][1], compliance[0][2], compliance[1][2]
    s44, s55, s66 = compliance[3][3], compliance[4][4], compliance[5][5]
    bulk_reuss = 1.0 / (s11 + s22 + s33 + 2.0 * (s12 + s13 + s23))
    shear_reuss = 15.0 / (
        4.0 * (s11 + s22 + s33)
        - 4.0 * (s12 + s13 + s23)
        + 3.0 * (s44 + s55 + s66)
    )
    bulk_hill = 0.5 * (bulk_voigt + bulk_reuss)
    shear_hill = 0.5 * (shear_voigt + shear_reuss)
    pugh_ratio = bulk_hill / shear_hill if abs(shear_hill) > 1e-14 else None
    youngs = 9.0 * bulk_hill * shear_hill / (3.0 * bulk_hill + shear_hill) if abs(3.0 * bulk_hill + shear_hill) > 1e-14 else None
    poisson = (3.0 * bulk_hill - 2.0 * shear_hill) / (2.0 * (3.0 * bulk_hill + shear_hill)) if abs(3.0 * bulk_hill + shear_hill) > 1e-14 else None
    universal_anisotropy = 5.0 * (shear_voigt / shear_reuss) + (bulk_voigt / bulk_reuss) - 6.0 if abs(shear_reuss) > 1e-14 and abs(bulk_reuss) > 1e-14 else None
    zener_ratio = (2.0 * c44 / (c11 - c12)) if abs(c11 - c12) > 1e-14 else None
    cauchy_pressure = ((c12 + c13 + c23) / 3.0) - ((c44 + c55 + c66) / 3.0)
    k_ratio = shear_hill / bulk_hill if abs(bulk_hill) > 1e-14 else None
    hardness = max(0.0, 2.0 * ((k_ratio * k_ratio * shear_hill) ** 0.585) - 3.0) if k_ratio is not None and k_ratio > 0 and shear_hill > 0 else None
    stable = is_positive_definite(tensor)
    if hardness is None:
        hardness_class = None
    elif hardness >= 20.0:
        hardness_class = "hard-like"
    elif hardness >= 4.0:
        hardness_class = "moderate-hardness-like"
    else:
        hardness_class = "soft-like"
    return {
        "path": str(path),
        "bulk_modulus_voigt_GPa": bulk_voigt,
        "shear_modulus_voigt_GPa": shear_voigt,
        "bulk_modulus_reuss_GPa": bulk_reuss,
        "shear_modulus_reuss_GPa": shear_reuss,
        "bulk_modulus_hill_GPa": bulk_hill,
        "shear_modulus_hill_GPa": shear_hill,
        "average_diagonal_GPa": (c11 + c22 + c33) / 3.0,
        "pugh_ratio": pugh_ratio,
        "youngs_modulus_GPa": youngs,
        "poisson_ratio": poisson,
        "universal_anisotropy_index": universal_anisotropy,
        "zener_ratio": zener_ratio,
        "cauchy_pressure_GPa": cauchy_pressure,
        "hardness_estimate_GPa": hardness,
        "hardness_class": hardness_class,
        "mechanically_stable_heuristic": stable,
        "ductility_hint": "ductile-like" if pugh_ratio is not None and pugh_ratio > 1.75 else "brittle-like",
        "observations": ["Voigt, Reuss, and Hill elastic averages were extracted from the 6x6 tensor."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a 6x6 elastic tensor.")
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
