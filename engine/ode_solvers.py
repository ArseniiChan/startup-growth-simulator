"""ODE solvers with a uniform interface.

Every solver has the signature::

    solver(f, y0, t_span, h, *args) -> (t_array, y_array)

where ``f(t, y, *args) -> dy/dt`` is the right-hand side of dy/dt = f(t, y).

All solvers use the same time-grid rule (the "linspace rule"): the number of
steps is ``ceil((t1 - t0) / h)``, the grid is ``np.linspace(t0, t1, n+1)``, and
the actual step ``h_actual = (t1 - t0) / n`` is what every step uses. This
guarantees every solver hits exactly the same final time regardless of the
requested h.

Outputs::

    t_array : shape (n+1,)
    y_array : shape (n+1, state_dim)
"""

from __future__ import annotations

import math
from typing import Callable

import numpy as np


Solver = Callable[..., tuple[np.ndarray, np.ndarray]]


def _make_grid(t_span: tuple[float, float], h: float) -> tuple[np.ndarray, float, int]:
    """Build the shared time grid. Returns (t, h_actual, n_steps)."""
    t0, t1 = float(t_span[0]), float(t_span[1])
    if t1 <= t0:
        raise ValueError("t_span must satisfy t_span[1] > t_span[0]")
    if h <= 0:
        raise ValueError("h must be positive")
    n_steps = max(1, math.ceil((t1 - t0) / h))
    t = np.linspace(t0, t1, n_steps + 1)
    h_actual = (t1 - t0) / n_steps
    return t, h_actual, n_steps


def _init_state(y0) -> tuple[np.ndarray, int]:
    y0_arr = np.atleast_1d(np.asarray(y0, dtype=float))
    return y0_arr, y0_arr.shape[0]


def euler(
    f: Callable, y0, t_span: tuple[float, float], h: float, *args
) -> tuple[np.ndarray, np.ndarray]:
    """Forward Euler. Global error O(h)."""
    t, h_actual, n = _make_grid(t_span, h)
    y0_arr, dim = _init_state(y0)
    y = np.empty((n + 1, dim), dtype=float)
    y[0] = y0_arr
    for i in range(n):
        y[i + 1] = y[i] + h_actual * f(t[i], y[i], *args)
    return t, y


def heun(
    f: Callable, y0, t_span: tuple[float, float], h: float, *args
) -> tuple[np.ndarray, np.ndarray]:
    """Heun's method (improved Euler / explicit RK2). Global error O(h^2)."""
    t, h_actual, n = _make_grid(t_span, h)
    y0_arr, dim = _init_state(y0)
    y = np.empty((n + 1, dim), dtype=float)
    y[0] = y0_arr
    for i in range(n):
        k1 = f(t[i], y[i], *args)
        y_pred = y[i] + h_actual * k1
        k2 = f(t[i] + h_actual, y_pred, *args)
        y[i + 1] = y[i] + 0.5 * h_actual * (k1 + k2)
    return t, y


def rk4(
    f: Callable, y0, t_span: tuple[float, float], h: float, *args
) -> tuple[np.ndarray, np.ndarray]:
    """Classical 4th-order Runge-Kutta. Global error O(h^4)."""
    t, h_actual, n = _make_grid(t_span, h)
    y0_arr, dim = _init_state(y0)
    y = np.empty((n + 1, dim), dtype=float)
    y[0] = y0_arr
    half = 0.5 * h_actual
    for i in range(n):
        ti = t[i]
        yi = y[i]
        k1 = f(ti, yi, *args)
        k2 = f(ti + half, yi + half * k1, *args)
        k3 = f(ti + half, yi + half * k2, *args)
        k4 = f(ti + h_actual, yi + h_actual * k3, *args)
        y[i + 1] = yi + (h_actual / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return t, y
