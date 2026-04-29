"""Numerical integration: composite Simpson's 1/3, Gaussian (Legendre)
quadrature on [-1, 1] mapped to [a, b], and a wrapper that integrates a
discrete ODE-output trajectory.

References: Burden et al., Chapter 4.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def composite_simpson(f: Callable[[float], float], a: float, b: float, n: int) -> float:
    """Composite Simpson's 1/3 rule over [a, b] with n subintervals.

    n must be even. Truncation error is O(h^4) where h = (b-a)/n.

        I = (h/3) [ f(x_0) + 4 sum_{odd i} f(x_i) + 2 sum_{even i, 0<i<n} f(x_i) + f(x_n) ]
    """
    if n <= 0 or n % 2 != 0:
        raise ValueError(f"composite_simpson requires even n > 0, got n={n}")
    if b <= a:
        raise ValueError("composite_simpson requires b > a")
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = np.array([f(xi) for xi in x], dtype=float)
    # weight pattern: 1, 4, 2, 4, ..., 4, 1
    odd = np.sum(y[1:-1:2])
    even = np.sum(y[2:-1:2])
    return float((h / 3.0) * (y[0] + 4.0 * odd + 2.0 * even + y[-1]))


# Gauss-Legendre nodes and weights on [-1, 1] for n_points = 2, 3, 5.
# Hardcoded from standard tables. n-point Gauss-Legendre is exact for any
# polynomial of degree <= 2n - 1.
_GAUSS_LEGENDRE: dict[int, tuple[np.ndarray, np.ndarray]] = {
    2: (
        np.array([-1.0 / np.sqrt(3.0), 1.0 / np.sqrt(3.0)]),
        np.array([1.0, 1.0]),
    ),
    3: (
        np.array([-np.sqrt(3.0 / 5.0), 0.0, np.sqrt(3.0 / 5.0)]),
        np.array([5.0 / 9.0, 8.0 / 9.0, 5.0 / 9.0]),
    ),
    5: (
        np.array([
            -0.9061798459386640,
            -0.5384693101056831,
            0.0,
            0.5384693101056831,
            0.9061798459386640,
        ]),
        np.array([
            0.2369268850561891,
            0.4786286704993665,
            0.5688888888888889,
            0.4786286704993665,
            0.2369268850561891,
        ]),
    ),
}


def gaussian_quadrature(
    f: Callable[[float], float], a: float, b: float, n_points: int = 5
) -> float:
    """Gauss-Legendre quadrature on [a, b] with hardcoded nodes for n in {2,3,5}.

    Exact for polynomials of degree <= 2 n_points - 1.

        I = ((b-a)/2) * sum_i w_i * f( ((b-a)/2) x_i + (a+b)/2 )
    """
    if n_points not in _GAUSS_LEGENDRE:
        raise ValueError(
            f"gaussian_quadrature supports n_points in {sorted(_GAUSS_LEGENDRE)}; got {n_points}"
        )
    if b <= a:
        raise ValueError("gaussian_quadrature requires b > a")
    nodes, weights = _GAUSS_LEGENDRE[n_points]
    half = 0.5 * (b - a)
    mid = 0.5 * (a + b)
    total = 0.0
    for xi, wi in zip(nodes, weights):
        total += wi * f(half * xi + mid)
    return float(half * total)


def integrate_trajectory(t_array: np.ndarray, y_array: np.ndarray) -> float:
    """Apply Simpson's rule to discrete ODE output y(t).

    Used for cumulative metrics: total revenue = ∫ R(t) dt, total burn,
    customer lifetime value over a window. Requires uniform spacing — the
    linspace rule in ode_solvers.py guarantees this for any of our solvers.

    The number of subintervals n = len(t_array) - 1 may be even or odd.
    When n is even we apply Simpson's 1/3 rule to the whole interval. When
    n is odd we apply Simpson's 1/3 rule to the first n-1 (even) intervals
    and add a single trapezoid on the final interval. Trapezoid is O(h^2)
    vs. Simpson's O(h^4); for one trailing interval the contribution is
    asymptotically negligible compared to the n-1 Simpson terms, so the
    overall order is preserved. This avoids the surprise where a user
    feeds the linspace solver output (which can have odd n) into the
    integrator and gets a ValueError.
    """
    t_array = np.asarray(t_array, dtype=float)
    y_array = np.asarray(y_array, dtype=float)
    n = t_array.size - 1
    if n < 2:
        raise ValueError("integrate_trajectory requires at least 3 grid points")
    diffs = np.diff(t_array)
    if not np.allclose(diffs, diffs[0]):
        raise ValueError(
            "integrate_trajectory requires a uniformly spaced t_array"
        )
    h = float(diffs[0])
    if n % 2 == 0:
        odd = np.sum(y_array[1:-1:2])
        even = np.sum(y_array[2:-1:2])
        return float((h / 3.0) * (y_array[0] + 4.0 * odd + 2.0 * even + y_array[-1]))
    # Odd n: Simpson on the first n-1 (even) intervals + trapezoid on the last.
    odd = np.sum(y_array[1:-2:2])
    even = np.sum(y_array[2:-2:2])
    simpson_part = (h / 3.0) * (y_array[0] + 4.0 * odd + 2.0 * even + y_array[-2])
    trapezoid_tail = 0.5 * h * (y_array[-2] + y_array[-1])
    return float(simpson_part + trapezoid_tail)
