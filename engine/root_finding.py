"""Root finding: Newton's method, bisection, secant, and a bracket scanner.

Notebook 5 uses these to find break-even (dCash/dt = 0) and runway death
(Cash(t) = 0) on the ODE output. The bracket scanner ``find_brackets`` is
the right entry point when the root location is not known a priori — it
returns every sign-change interval on a sample grid, which can then be
fed to bisection or as Newton's initial guess.

References: Burden et al., Chapter 2.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def newton(
    f: Callable[[float], float],
    df: Callable[[float], float],
    x0: float,
    tol: float = 1e-10,
    max_iter: int = 100,
    bounds: tuple[float, float] | None = None,
) -> dict:
    """Newton's method with two safeguards:

    - If |df(x)| < 1e-14 the iteration stops with converged=False rather
      than dividing by zero.
    - If ``bounds`` is given and a Newton step jumps outside the interval,
      the routine falls back to a bisection-style halving step inside the
      interval. This keeps a runaway Newton from leaving the feasible set.
    """
    history: list[float] = [float(x0)]
    x = float(x0)
    converged = False
    for it in range(1, max_iter + 1):
        fx = f(x)
        dfx = df(x)
        if abs(dfx) < 1e-14:
            return {
                "root": x,
                "iterations": it - 1,
                "history": np.array(history),
                "converged": False,
                "reason": "zero_derivative",
            }
        x_new = x - fx / dfx
        if bounds is not None:
            a, b = bounds
            if x_new < a or x_new > b:
                # Newton overshot the feasible interval. Take a bisection
                # step on whichever sub-interval brackets the root: pick the
                # side of x where f changes sign. If x itself is outside
                # the interval, halve the full interval. Either way we stay
                # in [a, b] and make a real bisection-style move.
                fa = f(a)
                if a <= x <= b and fx * fa < 0:
                    x_new = 0.5 * (a + x)
                elif a <= x <= b:
                    x_new = 0.5 * (x + b)
                else:
                    x_new = 0.5 * (a + b)
        history.append(float(x_new))
        if abs(x_new - x) < tol:
            x = x_new
            converged = True
            break
        x = x_new
    return {
        "root": x,
        "iterations": len(history) - 1,
        "history": np.array(history),
        "converged": converged,
        "reason": "tolerance" if converged else "max_iter",
    }


def bisection(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1e-10,
    max_iter: int = 100,
) -> dict:
    """Bisection. Requires f(a)*f(b) < 0 — raises ValueError otherwise."""
    fa = f(a)
    fb = f(b)
    if fa * fb > 0:
        raise ValueError(
            f"bisection requires a sign change: f({a})={fa}, f({b})={fb}"
        )
    if fa == 0:
        return {"root": a, "iterations": 0, "history": np.array([a]), "converged": True}
    if fb == 0:
        return {"root": b, "iterations": 0, "history": np.array([b]), "converged": True}
    history: list[float] = []
    converged = False
    for it in range(max_iter):
        c = 0.5 * (a + b)
        history.append(float(c))
        fc = f(c)
        if fc == 0 or 0.5 * (b - a) < tol:
            converged = True
            return {
                "root": c,
                "iterations": it + 1,
                "history": np.array(history),
                "converged": True,
            }
        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc
    return {
        "root": 0.5 * (a + b),
        "iterations": max_iter,
        "history": np.array(history),
        "converged": False,
    }


def secant(
    f: Callable[[float], float],
    x0: float,
    x1: float,
    tol: float = 1e-10,
    max_iter: int = 100,
) -> dict:
    """Secant method. Returns the same shape as newton()."""
    history: list[float] = [float(x0), float(x1)]
    x_prev, x = float(x0), float(x1)
    f_prev = f(x_prev)
    converged = False
    for it in range(1, max_iter + 1):
        fx = f(x)
        denom = fx - f_prev
        if abs(denom) < 1e-14:
            return {
                "root": x,
                "iterations": it - 1,
                "history": np.array(history),
                "converged": False,
                "reason": "zero_difference",
            }
        x_new = x - fx * (x - x_prev) / denom
        history.append(float(x_new))
        if abs(x_new - x) < tol:
            converged = True
            x = x_new
            break
        x_prev, f_prev = x, fx
        x = x_new
    return {
        "root": x,
        "iterations": len(history) - 2,
        "history": np.array(history),
        "converged": converged,
        "reason": "tolerance" if converged else "max_iter",
    }


def find_brackets(
    f: Callable[[float], float], grid: np.ndarray
) -> list[tuple[float, float]]:
    """Scan a sample grid for sign changes.

    Returns every interval (grid[i], grid[i+1]) where f(grid[i])*f(grid[i+1]) < 0.
    Endpoints where f == 0 exactly are reported as zero-width brackets.
    Empty list if no sign change exists in the grid.
    """
    grid = np.asarray(grid, dtype=float)
    if grid.size < 2:
        return []
    fvals = np.array([f(x) for x in grid])
    out: list[tuple[float, float]] = []
    for i in range(grid.size - 1):
        a, b = grid[i], grid[i + 1]
        fa, fb = fvals[i], fvals[i + 1]
        if fa == 0:
            out.append((float(a), float(a)))
        elif fa * fb < 0:
            out.append((float(a), float(b)))
    if grid.size and fvals[-1] == 0:
        out.append((float(grid[-1]), float(grid[-1])))
    return out
