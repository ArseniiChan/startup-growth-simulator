"""Render a presentation-quality root-finder convergence figure.

The README and report cite "Newton 3 iterations, secant 4, bisection 20"
on the cash break-even problem. This script reproduces those iterations
on the actual μ* break-even root-finding problem and plots
log10|x_n − x*| vs. iteration n for all three methods, on a shared axis.

Output: report/figures/pres_root_finder_convergence.png

The figure is the textbook visualization of root-finder convergence
orders: bisection's slope is linear (order 1), secant's slope tracks
the golden ratio φ ≈ 1.618 (super-linear), Newton's slope doubles each
step (quadratic, order 2).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# We need the engine on the path. Running from repo root makes this work.
import sys

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from engine import (  # noqa: E402
    StartupParams,
    bisection,
    default_params,
    newton,
    rk4,
    secant,
    growth_system,
)

OUT_PATH = REPO / "report" / "figures" / "pres_root_finder_convergence.png"

# Palette aligned with the deck.
INK = "#1E2761"
ACCENT = "#F96167"
NAVY = "#1E2761"
TEAL = "#0F766E"
RULE = "#E2E8F0"
MUTED = "#64748B"


def terminal_cash_at_mu(mu_value: float) -> float:
    """Run the model with churn rate mu and return Cash(T=120 months)."""
    p = default_params()
    # Override only churn; leave everything else at the default-SaaS profile.
    p_swept = StartupParams(
        g=p.g, K=p.K, alpha=p.alpha, mu=mu_value,
        p=p.p, mu_R=p.mu_R, F=p.F, v=p.v,
    )
    # Initial state: 100 users, 0 paying users, 0 MRR, $1M seed cash.
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    t, y = rk4(growth_system, y0, (0.0, 120.0), 0.5, p_swept)
    return y[-1, 3]  # Cash(T)


def main() -> None:
    # Each engine root-finder returns a dict with a "history" array recording
    # every iterate. We use the engine implementations directly — no custom
    # reimplementation needed.

    # Use a high-precision bisection as the "true" root for error reference.
    mu_star_ref = bisection(
        terminal_cash_at_mu, a=0.005, b=0.49, tol=1e-9, max_iter=80,
    )["root"]

    # Numerical derivative for Newton (central difference, h tuned small).
    def df(x: float, h: float = 1e-4) -> float:
        return (terminal_cash_at_mu(x + h) - terminal_cash_at_mu(x - h)) / (2 * h)

    # Newton: warm start near the root — typical when bracketing has already
    # narrowed it via prior coarse search.
    newton_res = newton(terminal_cash_at_mu, df, x0=0.13, tol=1e-6, max_iter=30)
    # Secant: a moderately-tight two-point initialization that brackets the root.
    secant_res = secant(terminal_cash_at_mu, x0=0.10, x1=0.20, tol=1e-6, max_iter=30)
    # Bisection: full physical range, to demonstrate the linear-rate cost when
    # we can only assume a sign change exists.
    bisect_res = bisection(terminal_cash_at_mu, a=0.005, b=0.49, tol=1e-6, max_iter=60)

    newton_iters = newton_res["history"]
    secant_iters = secant_res["history"]
    bisect_iters = bisect_res["history"]

    # Compute |x_n - x*| for each method.
    newton_err = np.abs(np.array(newton_iters) - mu_star_ref)
    secant_err = np.abs(np.array(secant_iters) - mu_star_ref)
    bisect_err = np.abs(np.array(bisect_iters) - mu_star_ref)

    # Replace zero with floor for log plotting
    floor = 1e-12
    newton_err = np.maximum(newton_err, floor)
    secant_err = np.maximum(secant_err, floor)
    bisect_err = np.maximum(bisect_err, floor)

    fig, ax = plt.subplots(figsize=(7.0, 4.5), dpi=150)

    ax.semilogy(
        range(len(newton_err)), newton_err,
        marker="o", color=ACCENT, linewidth=2, markersize=7,
        label=f"Newton ({len(newton_err) - 1} iterations)",
    )
    ax.semilogy(
        range(len(secant_err)), secant_err,
        marker="s", color=TEAL, linewidth=2, markersize=6,
        label=f"Secant ({len(secant_err) - 1} iterations)",
    )
    ax.semilogy(
        range(len(bisect_err)), bisect_err,
        marker="^", color=NAVY, linewidth=2, markersize=5,
        label=f"Bisection ({len(bisect_err) - 1} iterations)",
    )

    ax.set_xlabel("Iteration n", fontsize=11, color=INK)
    ax.set_ylabel(r"|$\mu_n - \mu^*$|  (log scale)", fontsize=11, color=INK)
    ax.set_title(
        "Root-finder convergence on the cash break-even problem",
        fontsize=12, color=INK, pad=10,
    )
    ax.tick_params(axis="both", colors=MUTED, labelsize=10)
    ax.grid(which="both", color=RULE, linestyle="--", linewidth=0.5, alpha=0.6)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(RULE)
    ax.legend(loc="upper right", frameon=True, fontsize=10, framealpha=0.95)
    ax.set_axisbelow(True)

    fig.tight_layout()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT_PATH}")
    print(f"  reference root mu* = {mu_star_ref:.6f}")
    print(f"  Newton:    {len(newton_err) - 1} iterations, final err = {newton_err[-1]:.2e}")
    print(f"  Secant:    {len(secant_err) - 1} iterations, final err = {secant_err[-1]:.2e}")
    print(f"  Bisection: {len(bisect_err) - 1} iterations, final err = {bisect_err[-1]:.2e}")


def _run_newton_record(f, x0, tol=1e-6, max_iter=30, h=1e-4):
    """Newton's method recording every iterate. Uses central-difference derivative."""
    iterates = [x0]
    x = x0
    for _ in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return iterates
        # Central-difference derivative
        fpx = (f(x + h) - f(x - h)) / (2 * h)
        if fpx == 0:
            return iterates
        x_new = x - fx / fpx
        iterates.append(x_new)
        if abs(x_new - x) < tol:
            return iterates
        x = x_new
    return iterates


def _run_secant_record(f, x0, x1, tol=1e-6, max_iter=30):
    """Secant method recording every iterate."""
    iterates = [x0, x1]
    f0 = f(x0)
    f1 = f(x1)
    for _ in range(max_iter):
        if abs(f1) < tol:
            return iterates
        denom = f1 - f0
        if denom == 0:
            return iterates
        x_new = x1 - f1 * (x1 - x0) / denom
        iterates.append(x_new)
        if abs(x_new - x1) < tol:
            return iterates
        x0, f0 = x1, f1
        x1 = x_new
        f1 = f(x1)
    return iterates


def _run_bisect_record(f, a, b, tol=1e-6, max_iter=60):
    """Bisection recording the midpoint at each iteration."""
    fa = f(a)
    fb = f(b)
    if fa * fb > 0:
        raise ValueError("bisection requires sign change on [a, b]")
    iterates = []
    for _ in range(max_iter):
        c = 0.5 * (a + b)
        iterates.append(c)
        fc = f(c)
        if abs(fc) < tol or 0.5 * (b - a) < tol:
            return iterates
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    return iterates


if __name__ == "__main__":
    main()
