"""Generate synthetic startup revenue trajectories for calibration validation.

Each generated dataset contains:
- the "true" parameters used to simulate
- a noisy quarterly revenue series sampled from the RK4 trajectory

Output JSON files go in data/synthetic/. Run as a script.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from engine.growth_model import StartupParams, growth_system, preset_profiles
from engine.ode_solvers import rk4
from engine.utils import linear_interpolate


def generate_trajectory(
    params: StartupParams,
    y0: np.ndarray,
    T: float = 60.0,
    h: float = 0.1,
    noise_pct: float = 0.05,
    quarters: int = 20,
    seed: int | None = None,
) -> dict:
    """Solve the ODE with RK4, sample at quarterly cadence, add gaussian noise.

    noise_pct is a fraction of revenue magnitude (default 5%).
    """
    rng = np.random.default_rng(seed)
    t, y = rk4(growth_system, y0, (0.0, T), h, params)
    quarter_t = np.linspace(0.0, T, quarters)
    sampled = linear_interpolate(t, y, quarter_t)
    R_clean = sampled[:, 2]
    noise = rng.normal(scale=noise_pct * np.abs(R_clean) + 1.0)
    R_noisy = np.maximum(0.0, R_clean + noise)
    return {
        "true_params": asdict(params),
        "y0": y0.tolist(),
        "T_months": T,
        "quarters": quarter_t.tolist(),
        "revenue_clean": R_clean.tolist(),
        "revenue_noisy": R_noisy.tolist(),
        "users_clean": sampled[:, 0].tolist(),
        "active_users_clean": sampled[:, 1].tolist(),
        "cash_clean": sampled[:, 3].tolist(),
        "noise_pct": noise_pct,
        "seed": seed,
    }


def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    profiles = preset_profiles()
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    for name, params in profiles.items():
        data = generate_trajectory(params, y0, seed=hash(name) & 0xFFFF)
        path = out_dir / f"{name}.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"wrote {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "synthetic",
        help="output directory",
    )
    args = parser.parse_args()
    main(args.out)
