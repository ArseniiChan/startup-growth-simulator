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


def _rk4_step(f, ti, yi, h, args) -> np.ndarray:
    """One RK4 step. Used to bootstrap the multistep methods."""
    half = 0.5 * h
    k1 = f(ti, yi, *args)
    k2 = f(ti + half, yi + half * k1, *args)
    k3 = f(ti + half, yi + half * k2, *args)
    k4 = f(ti + h, yi + h * k3, *args)
    return yi + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def adams_bashforth4(
    f: Callable, y0, t_span: tuple[float, float], h: float, *args
) -> tuple[np.ndarray, np.ndarray]:
    """4-step Adams-Bashforth (explicit). Global error O(h^4).

    y_{n+1} = y_n + (h/24) * (55 f_n - 59 f_{n-1} + 37 f_{n-2} - 9 f_{n-3})

    Bootstrap: the first three steps are taken with RK4 so that
    f_0, f_1, f_2, f_3 are available before the AB4 recurrence starts. From
    n >= 3 the method is one function evaluation per step (vs RK4's four).
    """
    t, h_actual, n = _make_grid(t_span, h)
    y0_arr, dim = _init_state(y0)
    y = np.empty((n + 1, dim), dtype=float)
    y[0] = y0_arr
    if n < 4:
        # Not enough steps to even start the multistep recurrence; fall back
        # to RK4 for the whole window so the linspace contract holds.
        for i in range(n):
            y[i + 1] = _rk4_step(f, t[i], y[i], h_actual, args)
        return t, y
    # Bootstrap with RK4
    for i in range(3):
        y[i + 1] = _rk4_step(f, t[i], y[i], h_actual, args)
    f_buf = [f(t[i], y[i], *args) for i in range(4)]
    for i in range(3, n):
        # f_buf is [f_{i-3}, f_{i-2}, f_{i-1}, f_i]
        y[i + 1] = y[i] + (h_actual / 24.0) * (
            55.0 * f_buf[3] - 59.0 * f_buf[2] + 37.0 * f_buf[1] - 9.0 * f_buf[0]
        )
        if i + 1 < n:
            f_buf = [f_buf[1], f_buf[2], f_buf[3], f(t[i + 1], y[i + 1], *args)]
    return t, y


def adams_moulton_pc(
    f: Callable, y0, t_span: tuple[float, float], h: float, *args
) -> tuple[np.ndarray, np.ndarray]:
    """Adams-Bashforth-Moulton predictor-corrector (PECE). Global error O(h^4).

    Predict (AB4):
        y^p_{n+1} = y_n + (h/24) (55 f_n - 59 f_{n-1} + 37 f_{n-2} - 9 f_{n-3})
    Correct (AM4, one PECE iteration):
        y_{n+1}   = y_n + (h/24) (9 f(t_{n+1}, y^p_{n+1}) + 19 f_n - 5 f_{n-1} + f_{n-2})

    PECE = predict / evaluate / correct / evaluate. We use exactly one
    correction step (not iterated to convergence). Same RK4 bootstrap as
    AB4. Two function evaluations per step (the predicted f and the
    corrected f), still cheaper than RK4.
    """
    t, h_actual, n = _make_grid(t_span, h)
    y0_arr, dim = _init_state(y0)
    y = np.empty((n + 1, dim), dtype=float)
    y[0] = y0_arr
    if n < 4:
        for i in range(n):
            y[i + 1] = _rk4_step(f, t[i], y[i], h_actual, args)
        return t, y
    for i in range(3):
        y[i + 1] = _rk4_step(f, t[i], y[i], h_actual, args)
    f_buf = [f(t[i], y[i], *args) for i in range(4)]
    for i in range(3, n):
        # Predict (AB4)
        y_pred = y[i] + (h_actual / 24.0) * (
            55.0 * f_buf[3] - 59.0 * f_buf[2] + 37.0 * f_buf[1] - 9.0 * f_buf[0]
        )
        # Evaluate
        f_pred = f(t[i + 1], y_pred, *args)
        # Correct (AM4 with one PECE iteration)
        y[i + 1] = y[i] + (h_actual / 24.0) * (
            9.0 * f_pred + 19.0 * f_buf[3] - 5.0 * f_buf[2] + 1.0 * f_buf[1]
        )
        if i + 1 < n:
            f_buf = [f_buf[1], f_buf[2], f_buf[3], f(t[i + 1], y[i + 1], *args)]
    return t, y
