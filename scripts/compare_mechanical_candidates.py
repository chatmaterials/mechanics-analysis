#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_elastic_tensor import analyze as analyze_elastic
from analyze_equation_of_state import analyze as analyze_eos
from analyze_stress_state import analyze as analyze_stress


def locate_required(root: Path, relative_paths: list[str]) -> Path:
    for relative in relative_paths:
        candidate = root / relative
        if candidate.exists():
            return candidate
    raise SystemExit(f"Could not locate any of {relative_paths} in {root}")


def locate_optional(root: Path, relative_paths: list[str]) -> Path | None:
    for relative in relative_paths:
        candidate = root / relative
        if candidate.exists():
            return candidate
    return None


def analyze_case(root: Path, bulk_min: float, bulk_max: float) -> dict[str, object]:
    eos_path = locate_required(root, ["eos.dat", "eos/eos.dat"])
    elastic_path = locate_required(root, ["elastic_tensor.dat", "elastic/elastic_tensor.dat"])
    stress_path = locate_optional(root, ["stress_tensor.dat", "stress/stress_tensor.dat"])
    eos = analyze_eos(eos_path)
    elastic = analyze_elastic(elastic_path)
    stress = analyze_stress(stress_path) if stress_path is not None else None
    bulk = float(elastic["bulk_modulus_hill_GPa"])
    if bulk < bulk_min:
        bulk_penalty = bulk_min - bulk
    elif bulk > bulk_max:
        bulk_penalty = bulk - bulk_max
    else:
        bulk_penalty = 0.0
    stability_penalty = 100.0 if not elastic["mechanically_stable_heuristic"] else 0.0
    stress_penalty = float(stress["von_mises_like_GPa"]) if stress is not None else 0.0
    anisotropy_penalty = max(0.0, float(elastic["universal_anisotropy_index"]) - 1.0) if elastic["universal_anisotropy_index"] is not None else 0.0
    ductility_penalty = 5.0 if elastic["ductility_hint"] == "brittle-like" else 0.0
    score = bulk_penalty + stability_penalty + 0.1 * stress_penalty + anisotropy_penalty + ductility_penalty
    return {
        "case": root.name,
        "path": str(root),
        "equilibrium_volume_A3": eos["equilibrium_volume_A3"],
        "bulk_modulus_hill_GPa": bulk,
        "shear_modulus_hill_GPa": elastic["shear_modulus_hill_GPa"],
        "universal_anisotropy_index": elastic["universal_anisotropy_index"],
        "hardness_estimate_GPa": elastic["hardness_estimate_GPa"],
        "mechanically_stable_heuristic": elastic["mechanically_stable_heuristic"],
        "ductility_hint": elastic["ductility_hint"],
        "von_mises_like_GPa": stress["von_mises_like_GPa"] if stress is not None else None,
        "bulk_penalty_GPa": bulk_penalty,
        "stability_penalty": stability_penalty,
        "stress_penalty": stress_penalty,
        "anisotropy_penalty": anisotropy_penalty,
        "ductility_penalty": ductility_penalty,
        "screening_score": score,
    }


def analyze_cases(roots: list[Path], bulk_min: float, bulk_max: float) -> dict[str, object]:
    cases = [analyze_case(root, bulk_min, bulk_max) for root in roots]
    ranked = sorted(cases, key=lambda item: item["screening_score"])
    return {
        "target_bulk_window_GPa": [bulk_min, bulk_max],
        "ranking_basis": "screening_score = bulk_penalty + stability_penalty + 0.1 * residual_stress + anisotropy_penalty + ductility_penalty",
        "cases": ranked,
        "best_case": ranked[0]["case"] if ranked else None,
        "observations": [
            "This is a compact mechanics-screening heuristic intended for candidate ranking, not a full finite-strain study."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank mechanical candidates with a simple bulk-plus-stability heuristic.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--bulk-min", type=float, default=100.0)
    parser.add_argument("--bulk-max", type=float, default=200.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze_cases([Path(path).expanduser().resolve() for path in args.paths], args.bulk_min, args.bulk_max)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
