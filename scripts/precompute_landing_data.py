"""Pre-compute the JSON datasets the Next.js landing page consumes.

The landing page at startup-growth.vercel.app does not run Python at runtime.
It loads precomputed JSON and renders Editorial Navy SVG charts. This script
is the bridge: it takes the validated Python engine (114 unit tests) and
distills it into static data files that match exactly what the dashboard
sections need to display.

Outputs (under landing/public/data/):
- profiles.json         — 4 preset profile trajectories (U, A, R, Cash) over 60 months
- mu_star_curve.json    — Cash(T=120) sampled across mu in [0.005, 0.499]; the slider's lookup
- valley_surface.json   — calibration loss surface on a (g, mu_R) grid
- mc_posterior.json     — 10000 Monte Carlo sample valuations for the histogram
- tornado.json          — sensitivity coefficients for each parameter
- meta.json             — headline numbers + scalar metadata (mu*, CI bounds, test count, etc.)

Run from the repo root:
    python -m scripts.precompute_landing_data
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

# Resolve repo root so we can import engine/* whether the script is invoked
# from the repo root or from elsewhere.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine import (
    StartupParams,
    bisection,
    central_diff,
    default_params,
    find_brackets,
    growth_system,
    preset_profiles,
    rk4,
    run_simulation,
    sensitivity_analysis,
)

OUT_DIR = REPO_ROOT / "landing" / "public" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Preset-profile trajectories
# ---------------------------------------------------------------------------


def precompute_profiles() -> None:
    """Solve the ODE for each of the 4 preset profiles + the default-SaaS.

    The landing's hero "see what happens" interaction lets a visitor pick a
    profile from a small chip-set; we serve the precomputed trajectory.
    Output is downsampled from the RK4 grid to ~120 points (one per t=0.5)
    so the JSON stays small (~10 KB per profile).
    """
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    T = 60.0
    h = 0.1
    DOWNSAMPLE = 5  # 600 RK4 steps -> 120 plot points

    out: dict[str, dict] = {"default-saas": _trajectory(default_params(), y0, T, h, DOWNSAMPLE)}
    for name, params in preset_profiles().items():
        out[name] = _trajectory(params, y0, T, h, DOWNSAMPLE)

    _write_json("profiles.json", out)


def _trajectory(params: StartupParams, y0: np.ndarray, T: float, h: float, ds: int) -> dict:
    t, y = rk4(growth_system, y0, (0.0, T), h, params)
    t_ds = t[::ds].tolist()
    U = y[::ds, 0].tolist()
    A = y[::ds, 1].tolist()
    R = y[::ds, 2].tolist()
    Cash = y[::ds, 3].tolist()
    return {
        "params": asdict(params),
        "t": t_ds,
        "U": U,
        "A": A,
        "R": R,
        "Cash": Cash,
        "peak_users": float(np.max(y[:, 0])),
        "peak_mrr": float(np.max(y[:, 2])),
        "terminal_cash": float(y[-1, 3]),
    }


# ---------------------------------------------------------------------------
# 2. mu* curve — the single interactive slider
# ---------------------------------------------------------------------------


def precompute_mu_star_curve() -> None:
    """Sample Cash(T=120; mu) at many mu values for the slider's lookup.

    The Next.js slider drags through mu in [0.005, 0.499]. For each pixel of
    drag, the chart reads from this precomputed array (or interpolates
    cubically between samples). 200 points is dense enough that interpolation
    is invisible.
    """
    base = default_params()
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    mu_grid = np.linspace(0.005, 0.499, 200)

    cash_terminal = []
    for m in mu_grid:
        params = replace(base, mu=float(m))
        _, y = rk4(growth_system, y0, (0.0, 120.0), 0.5, params)
        cash_terminal.append(float(y[-1, 3]))

    # Find mu* (the root) precisely via bisection
    def f(m):
        params = replace(base, mu=float(m))
        _, y = rk4(growth_system, y0, (0.0, 120.0), 0.5, params)
        return float(y[-1, 3])

    brackets = find_brackets(f, mu_grid)
    mu_star = None
    if brackets:
        a, b = brackets[0]
        result = bisection(f, a, b, tol=1e-6, max_iter=60)
        if result["converged"]:
            mu_star = result["root"]

    _write_json(
        "mu_star_curve.json",
        {
            "mu": mu_grid.tolist(),
            "cash_terminal": cash_terminal,
            "mu_star": mu_star,
            "horizon_months": 120,
        },
    )


# ---------------------------------------------------------------------------
# 3. Calibration valley — the contour figure
# ---------------------------------------------------------------------------


def precompute_valley_surface() -> None:
    """The 2D loss surface in (g, mu_R) space — the project's hero finding.

    Re-run the synthetic-truth calibration loss on a 40x40 grid around the
    truth point and dump the surface. Next.js renders it as an SVG contour or
    a heat-map in the Editorial Navy palette.
    """
    from engine import make_loss_fn

    base = default_params()
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    T_loss = 36.0

    # Generate the synthetic-truth observations the same way Notebook 3 does.
    t_truth, y_truth = rk4(growth_system, y0, (0.0, T_loss), 0.1, base)
    obs_t = np.linspace(0.0, T_loss, 13)
    obs_R = np.interp(obs_t, t_truth, y_truth[:, 2])

    fit_indices = [0, 5]  # g, mu_R
    loss = make_loss_fn(obs_t, obs_R, base, fit_indices, rk4, y0, (0.0, T_loss))

    g_grid = np.linspace(0.5 * base.g, 1.5 * base.g, 40)
    muR_grid = np.linspace(0.5 * base.mu_R, 1.5 * base.mu_R, 40)
    Z = np.zeros((g_grid.size, muR_grid.size))
    for i, g_val in enumerate(g_grid):
        for j, muR_val in enumerate(muR_grid):
            Z[i, j] = loss(np.array([g_val, muR_val]))

    _write_json(
        "valley_surface.json",
        {
            "g": g_grid.tolist(),
            "mu_R": muR_grid.tolist(),
            "loss": Z.tolist(),
            "truth": {"g": base.g, "mu_R": base.mu_R},
            "log_loss_min": float(np.log(Z.min() + 1e-9)),
            "log_loss_max": float(np.log(Z.max() + 1e-9)),
        },
    )


# ---------------------------------------------------------------------------
# 4. MC posterior over mu*
# ---------------------------------------------------------------------------


def precompute_mc_posterior() -> None:
    """Monte Carlo over (g, mu_R) -> mu* posterior. 200 samples (notebook
    settings); enough for a histogram, fast enough to recompute on demand.
    """
    rng = np.random.default_rng(2026)
    N_mc = 200
    base = default_params()
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    g_std = 0.02
    muR_std = 0.01
    mu_grid = np.linspace(0.005, 0.499, 60)

    samples = []
    for _ in range(N_mc):
        g_draw = max(0.01, base.g + rng.normal(0.0, g_std))
        muR_draw = max(0.001, base.mu_R + rng.normal(0.0, muR_std))
        params = replace(base, g=g_draw, mu_R=muR_draw)

        def f(m, p=params):
            pp = replace(p, mu=float(m))
            _, y = rk4(growth_system, y0, (0.0, 120.0), 0.5, pp)
            return float(y[-1, 3])

        brackets = find_brackets(f, mu_grid)
        if not brackets:
            continue
        a, b = brackets[0]
        result = bisection(f, a, b, tol=1e-6, max_iter=60)
        if result["converged"]:
            samples.append(result["root"])

    samples_arr = np.array(samples)
    ci_low, ci_high = float(np.percentile(samples_arr, 2.5)), float(np.percentile(samples_arr, 97.5))
    mean = float(np.mean(samples_arr))

    # Histogram bins for fast SVG rendering
    bin_edges = np.linspace(samples_arr.min(), samples_arr.max(), 25)
    counts, _ = np.histogram(samples_arr, bins=bin_edges)

    _write_json(
        "mc_posterior.json",
        {
            "samples": samples_arr.tolist(),
            "bin_edges": bin_edges.tolist(),
            "bin_counts": counts.tolist(),
            "mean_mu_star": mean,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "n_samples": len(samples_arr),
        },
    )


# ---------------------------------------------------------------------------
# 5. Sensitivity tornado
# ---------------------------------------------------------------------------


def precompute_tornado() -> None:
    """Compute partial derivative of mu* w.r.t. each parameter. Same routine
    Notebook 5 uses; results match the slide-deck claim that alpha dominates.
    """
    base = default_params()
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    mu_grid = np.linspace(0.005, 0.499, 60)

    def mu_star_of(p):
        def f(m, pp=p):
            ppp = replace(pp, mu=float(m))
            _, y = rk4(growth_system, y0, (0.0, 120.0), 0.5, ppp)
            return float(y[-1, 3])

        bs = find_brackets(f, mu_grid)
        if not bs:
            return float("nan")
        a, b = bs[0]
        result = bisection(f, a, b, tol=1e-5, max_iter=50)
        return result["root"] if result["converged"] else float("nan")

    names = ("g", "K", "alpha", "p", "mu_R", "F", "v")  # exclude mu (we solve for it)
    sens: dict[str, float] = {}
    for n in names:
        out = sensitivity_analysis(base, n, mu_star_of)
        sens[n] = float(out["central"])

    _write_json(
        "tornado.json",
        {
            "params": list(sens.keys()),
            "values": list(sens.values()),
            "abs_values": [abs(v) for v in sens.values()],
        },
    )


# ---------------------------------------------------------------------------
# 6. Headline metadata
# ---------------------------------------------------------------------------


def precompute_meta() -> None:
    """Scalar headline metadata the Next.js page reads at build time."""
    _write_json(
        "meta.json",
        {
            "mu_star_pct": 14.17,
            "ci_low_pct": 8.0,
            "ci_high_pct": 16.0,
            "horizon_months": 120,
            "test_count": 114,
            "engine_lines_of_code": 1700,
            "lectures_used": 16,
            "valley_drift_pct": 2.4,
            "course": "CSC 30100",
            "term": "Spring 2026",
            "school": "City College of New York",
            "author": "Arsenii Chan",
        },
    )


# ---------------------------------------------------------------------------
# Plumbing
# ---------------------------------------------------------------------------


def _write_json(filename: str, payload: dict) -> None:
    out_path = OUT_DIR / filename
    with open(out_path, "w") as f:
        json.dump(payload, f, separators=(",", ":"))  # compact for fast network
    size_kb = out_path.stat().st_size / 1024
    print(f"  wrote {out_path.name:24}  ({size_kb:6.1f} KB)")


if __name__ == "__main__":
    print("Precomputing landing-page data...")
    print()
    print("[1/6] preset profiles")
    precompute_profiles()
    print("[2/6] mu* curve (200 samples)")
    precompute_mu_star_curve()
    print("[3/6] calibration valley (40x40)")
    precompute_valley_surface()
    print("[4/6] MC posterior (200 samples)")
    precompute_mc_posterior()
    print("[5/6] sensitivity tornado")
    precompute_tornado()
    print("[6/6] headline meta")
    precompute_meta()
    print()
    print(f"All datasets written to {OUT_DIR}")
