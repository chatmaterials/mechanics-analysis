#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze(path: Path) -> dict[str, object]:
    rows = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        rows.append([float(x) for x in parts[:3]])
    if len(rows) != 3:
        raise SystemExit("Stress tensor file must contain 3 rows with at least 3 columns")
    sxx, syy, szz = rows[0][0], rows[1][1], rows[2][2]
    sxy, syz, szx = rows[0][1], rows[1][2], rows[2][0]
    mean = (sxx + syy + szz) / 3.0
    von_mises = (
        0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2)
        + 3.0 * (sxy**2 + syz**2 + szx**2)
    ) ** 0.5
    hydrostatic_pressure = -mean
    ratio = von_mises / abs(mean) if abs(mean) > 1e-14 else None
    if von_mises < 2.0:
        stress_class = "well-relaxed-like"
    elif von_mises < 8.0:
        stress_class = "moderately-stressed-like"
    else:
        stress_class = "high-residual-stress-like"
    return {
        "path": str(path),
        "mean_normal_stress_GPa": mean,
        "hydrostatic_pressure_GPa": hydrostatic_pressure,
        "von_mises_like_GPa": von_mises,
        "deviatoric_to_mean_ratio": ratio,
        "stress_state_class": stress_class,
        "observations": ["Mean normal stress and a von-Mises-like equivalent stress were computed."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a 3x3 stress tensor.")
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
