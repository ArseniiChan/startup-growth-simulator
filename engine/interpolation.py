"""Cubic-spline interpolation built on the Thomas algorithm for the
underlying tridiagonal system.

Public API:
    thomas_solve            — direct solver for tridiagonal Ax = d.
    cubic_spline_natural    — natural spline (S''=0 at endpoints).
    cubic_spline_clamped    — clamped spline (S' specified at endpoints).

Both spline builders return a dict with the per-interval coefficients
(a, b, c, d) and three callables: eval, derivative, second_derivative.
The coefficients are exposed so a test can verify C^2 continuity at
interior knots without going through the callable.

References: Burden et al., Chapter 3 (splines), Chapter 6 (Thomas algorithm).
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def thomas_solve(
    a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray
) -> np.ndarray:
    """Solve a tridiagonal system Ax = d in O(n).

    a : sub-diagonal, length n,   a[0] is unused
    b : main diagonal, length n
    c : super-diagonal, length n, c[-1] is unused
    d : right-hand side, length n

    Returns x of length n.

    Implementation note: we copy b and d so the caller's arrays are not
    mutated (the standard in-place Thomas trick is fast but surprises
    callers).
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float).copy()
    c = np.asarray(c, dtype=float)
    d = np.asarray(d, dtype=float).copy()
    n = b.size
    if a.size != n or c.size != n or d.size != n:
        raise ValueError("thomas_solve requires a, b, c, d of equal length")
    # Forward sweep
    for i in range(1, n):
        if b[i - 1] == 0.0:
            raise ZeroDivisionError("thomas_solve: zero pivot encountered")
        m = a[i] / b[i - 1]
        b[i] = b[i] - m * c[i - 1]
        d[i] = d[i] - m * d[i - 1]
    # Back substitution
    x = np.empty(n, dtype=float)
    if b[-1] == 0.0:
        raise ZeroDivisionError("thomas_solve: zero pivot at last row")
    x[-1] = d[-1] / b[-1]
    for i in range(n - 2, -1, -1):
        x[i] = (d[i] - c[i] * x[i + 1]) / b[i]
    return x


def _make_callables(
    x: np.ndarray, a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray
) -> tuple[Callable, Callable, Callable]:
    """Build evaluator + first/second derivative callables from coefficients.

    On interval [x_i, x_{i+1}]:
        S(t)   = a_i + b_i (t - x_i) + c_i (t - x_i)^2 + d_i (t - x_i)^3
        S'(t)  =       b_i + 2 c_i (t - x_i)        + 3 d_i (t - x_i)^2
        S''(t) =                  2 c_i             + 6 d_i (t - x_i)
    """
    n_intervals = len(a)

    def _interval_index(t: float) -> int:
        # np.searchsorted returns the insertion index; clip into [0, n-1].
        i = int(np.searchsorted(x, t, side="right") - 1)
        return min(max(i, 0), n_intervals - 1)

    def evaluate(t):
        scalar = np.isscalar(t)
        ts = np.atleast_1d(np.asarray(t, dtype=float))
        out = np.empty_like(ts, dtype=float)
        for j, tj in enumerate(ts):
            i = _interval_index(tj)
            dt = tj - x[i]
            out[j] = a[i] + dt * (b[i] + dt * (c[i] + dt * d[i]))
        return float(out[0]) if scalar else out

    def derivative(t):
        scalar = np.isscalar(t)
        ts = np.atleast_1d(np.asarray(t, dtype=float))
        out = np.empty_like(ts, dtype=float)
        for j, tj in enumerate(ts):
            i = _interval_index(tj)
            dt = tj - x[i]
            out[j] = b[i] + dt * (2.0 * c[i] + 3.0 * d[i] * dt)
        return float(out[0]) if scalar else out

    def second_derivative(t):
        scalar = np.isscalar(t)
        ts = np.atleast_1d(np.asarray(t, dtype=float))
        out = np.empty_like(ts, dtype=float)
        for j, tj in enumerate(ts):
            i = _interval_index(tj)
            dt = tj - x[i]
            out[j] = 2.0 * c[i] + 6.0 * d[i] * dt
        return float(out[0]) if scalar else out

    return evaluate, derivative, second_derivative


def _solve_for_M(
    x: np.ndarray, y: np.ndarray, M0: float | None, Mn: float | None,
    dprime0: float | None = None, dprimeN: float | None = None
) -> np.ndarray:
    """Solve the tridiagonal system for M_i = S''(x_i).

    Natural spline: pass M0 = Mn = 0 (the M values at endpoints are forced).
    Clamped spline: pass dprime0 = S'(x_0), dprimeN = S'(x_n) (the M values
    at endpoints come from the boundary equations involving derivatives).

    The interior system (i = 1 .. n-1) is:
        h_{i-1} M_{i-1} + 2(h_{i-1}+h_i) M_i + h_i M_{i+1}
            = 6 [ (y_{i+1}-y_i)/h_i - (y_i-y_{i-1})/h_{i-1} ]
    """
    n = x.size - 1  # number of intervals
    h = np.diff(x)
    M = np.zeros(n + 1, dtype=float)
    if M0 is not None and Mn is not None:
        # Natural: M_0 and M_n are fixed; solve for M_1 .. M_{n-1}.
        size = n - 1
        if size <= 0:
            return M
        a = np.zeros(size)
        b = np.zeros(size)
        c = np.zeros(size)
        d = np.zeros(size)
        for k in range(size):
            i = k + 1  # i in 1..n-1
            a[k] = h[i - 1] if k > 0 else 0.0
            b[k] = 2.0 * (h[i - 1] + h[i])
            c[k] = h[i] if k < size - 1 else 0.0
            d[k] = 6.0 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])
        # Apply known boundary M_0 and M_n into the RHS of first/last rows.
        d[0] -= h[0] * M0
        d[-1] -= h[-1] * Mn
        x_int = thomas_solve(a, b, c, d)
        M[0] = M0
        M[-1] = Mn
        M[1:-1] = x_int
        return M
    # Clamped: derivative known at both ends.
    assert dprime0 is not None and dprimeN is not None
    size = n + 1
    a = np.zeros(size)
    b = np.zeros(size)
    c = np.zeros(size)
    d = np.zeros(size)
    # First row: 2 h_0 M_0 + h_0 M_1 = 6 ( (y_1 - y_0)/h_0 - dprime0 )
    b[0] = 2.0 * h[0]
    c[0] = h[0]
    d[0] = 6.0 * ((y[1] - y[0]) / h[0] - dprime0)
    # Last row: h_{n-1} M_{n-1} + 2 h_{n-1} M_n = 6 ( dprimeN - (y_n - y_{n-1})/h_{n-1} )
    a[-1] = h[-1]
    b[-1] = 2.0 * h[-1]
    d[-1] = 6.0 * (dprimeN - (y[-1] - y[-2]) / h[-1])
    # Interior rows
    for i in range(1, n):
        a[i] = h[i - 1]
        b[i] = 2.0 * (h[i - 1] + h[i])
        c[i] = h[i]
        d[i] = 6.0 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])
    return thomas_solve(a, b, c, d)


def _coefficients_from_M(
    x: np.ndarray, y: np.ndarray, M: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Translate the M_i values into per-interval coefficients (a,b,c,d).

    On [x_i, x_{i+1}] with h = h_i and dt = t - x_i:
        S(t) = a_i + b_i dt + c_i dt^2 + d_i dt^3
        a_i = y_i
        c_i = M_i / 2
        d_i = (M_{i+1} - M_i) / (6 h_i)
        b_i = (y_{i+1} - y_i)/h_i - h_i (2 M_i + M_{i+1}) / 6
    """
    h = np.diff(x)
    n = h.size
    a = y[:-1].astype(float)
    c = (M[:-1] / 2.0).astype(float)
    d = ((M[1:] - M[:-1]) / (6.0 * h)).astype(float)
    b = ((y[1:] - y[:-1]) / h - h * (2.0 * M[:-1] + M[1:]) / 6.0).astype(float)
    return a, b, c, d


def cubic_spline_natural(x: np.ndarray, y: np.ndarray) -> dict:
    """Natural cubic spline interpolant: S''(x_0) = S''(x_n) = 0.

    Returns a dict with x, the per-interval coefficients (a, b, c, d),
    and three callables (eval, derivative, second_derivative).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size < 3 or x.size != y.size:
        raise ValueError("cubic_spline_natural requires x.size == y.size >= 3")
    if not np.all(np.diff(x) > 0):
        raise ValueError("cubic_spline_natural requires strictly increasing x")
    M = _solve_for_M(x, y, M0=0.0, Mn=0.0)
    a, b, c, d = _coefficients_from_M(x, y, M)
    evaluate, derivative, second_derivative = _make_callables(x, a, b, c, d)
    return {
        "x": x, "y": y,
        "a": a, "b": b, "c": c, "d": d,
        "eval": evaluate,
        "derivative": derivative,
        "second_derivative": second_derivative,
    }


def cubic_spline_clamped(
    x: np.ndarray, y: np.ndarray, d0: float, dn: float
) -> dict:
    """Clamped cubic spline: S'(x_0) = d0, S'(x_n) = dn.

    Returns the same dict shape as cubic_spline_natural.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size < 3 or x.size != y.size:
        raise ValueError("cubic_spline_clamped requires x.size == y.size >= 3")
    if not np.all(np.diff(x) > 0):
        raise ValueError("cubic_spline_clamped requires strictly increasing x")
    M = _solve_for_M(x, y, M0=None, Mn=None, dprime0=float(d0), dprimeN=float(dn))
    a, b, c, d = _coefficients_from_M(x, y, M)
    evaluate, derivative, second_derivative = _make_callables(x, a, b, c, d)
    return {
        "x": x, "y": y,
        "a": a, "b": b, "c": c, "d": d,
        "eval": evaluate,
        "derivative": derivative,
        "second_derivative": second_derivative,
    }
