#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze(path: Path) -> dict[str, object]:
    rows = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 6:
            continue
        rows.append([float(x) for x in parts[:6]])
    if len(rows) != 6:
        raise SystemExit("Elastic tensor file must contain 6 rows with at least 6 columns")
    c11, c22, c33 = rows[0][0], rows[1][1], rows[2][2]
    c12, c13, c23 = rows[0][1], rows[0][2], rows[1][2]
    c44, c55, c66 = rows[3][3], rows[4][4], rows[5][5]
    bulk = (c11 + c22 + c33 + 2.0 * (c12 + c13 + c23)) / 9.0
    shear = (c11 + c22 + c33 - c12 - c13 - c23 + 3.0 * (c44 + c55 + c66)) / 15.0
    return {
        "path": str(path),
        "bulk_modulus_voigt_GPa": bulk,
        "shear_modulus_voigt_GPa": shear,
        "average_diagonal_GPa": (c11 + c22 + c33) / 3.0,
        "observations": ["Voigt elastic averages extracted from the 6x6 tensor."],
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
