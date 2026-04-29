"""Numerical differentiation: forward, central, 5-point, second derivative,
Richardson extrapolation, U-curve study, and ODE-output sensitivity analysis.

All scalar derivative routines have signature ``f(x) -> float``. They accept
``h`` as an optional argument. Order of accuracy refers to truncation error
(global, in the sense the slope of |error| vs h on a log-log plot is what's
quoted): forward O(h), central O(h^2), five_point O(h^4), second_derivative
O(h^2). Richardson extrapolation lifts the order of the base method by 2.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from engine.growth_model import (
    PARAM_NAMES,
    StartupParams,
    array_to_params,
    params_to_array,
)


def forward_diff(f: Callable[[float], float], x: float, h: float = 1e-5) -> float:
    """Forward difference: [f(x+h) - f(x)] / h. Truncation O(h)."""
    return (f(x + h) - f(x)) / h


def central_diff(f: Callable[[float], float], x: float, h: float = 1e-5) -> float:
    """Central difference: [f(x+h) - f(x-h)] / (2h). Truncation O(h^2)."""
    return (f(x + h) - f(x - h)) / (2.0 * h)


def five_point(f: Callable[[float], float], x: float, h: float = 1e-5) -> float:
    """5-point midpoint: [-f(x+2h) + 8f(x+h) - 8f(x-h) + f(x-2h)] / (12h).
    Truncation O(h^4)."""
    return (-f(x + 2 * h) + 8 * f(x + h) - 8 * f(x - h) + f(x - 2 * h)) / (12.0 * h)


def second_derivative(
    f: Callable[[float], float], x: float, h: float = 1e-4
) -> float:
    """Central second derivative: [f(x+h) - 2 f(x) + f(x-h)] / h^2. O(h^2)."""
    return (f(x + h) - 2.0 * f(x) + f(x - h)) / (h * h)


_BASE_ORDERS = {"forward": 1, "central": 2, "five_point": 4}
_BASE_FUNCS = {"forward": forward_diff, "central": central_diff, "five_point": five_point}


def richardson(
    f: Callable[[float], float],
    x: float,
    h: float = 1e-3,
    method: str = "central",
    p: int | None = None,
) -> float:
    """Richardson extrapolation lifts a base derivative method by two orders.

    D_richardson = D(h/2) + (D(h/2) - D(h)) / (2^p - 1)

    where p is the order of the base method. p is inferred from ``method`` if
    not given (forward=1, central=2, five_point=4).
    """
    if method not in _BASE_FUNCS:
        raise ValueError(f"unknown method {method!r}; expected one of {list(_BASE_FUNCS)}")
    if p is None:
        p = _BASE_ORDERS[method]
    base = _BASE_FUNCS[method]
    Dh = base(f, x, h)
    Dh2 = base(f, x, h / 2.0)
    return Dh2 + (Dh2 - Dh) / (2.0**p - 1.0)


def optimal_h_study(
    f: Callable[[float], float],
    x: float,
    f_exact: float,
    h_range: np.ndarray | None = None,
) -> dict:
    """Sweep h over many decades and record |error| for each method.

    Used to draw the U-curve: truncation error decreases with h, round-off
    error increases as h shrinks, and the optimum sits at the bottom of the U.
    """
    if h_range is None:
        h_range = np.logspace(-15, 0, 100)
    fwd = np.empty_like(h_range)
    ctr = np.empty_like(h_range)
    fpt = np.empty_like(h_range)
    for i, h in enumerate(h_range):
        fwd[i] = abs(forward_diff(f, x, h) - f_exact)
        ctr[i] = abs(central_diff(f, x, h) - f_exact)
        # five-point uses 2h offsets, so guard against h that pushes outside
        # any practical domain. We just compute and let np handle inf.
        fpt[i] = abs(five_point(f, x, h) - f_exact)
    return {
        "h": h_range,
        "forward": fwd,
        "central": ctr,
        "five_point": fpt,
    }


def _adaptive_h(value: float) -> float:
    """Per-parameter step size: h = eps^(1/3) * max(|value|, 1).

    eps^(1/3) is the standard balancing point between O(h^p) truncation and
    machine-precision round-off for first-order central differences. Scaling
    by max(|value|, 1) keeps h sensible across parameters spanning many
    orders of magnitude (g ~ 0.1 vs K ~ 1e6).
    """
    eps = np.finfo(float).eps
    return (eps ** (1.0 / 3.0)) * max(abs(value), 1.0)


def sensitivity_analysis(
    params: StartupParams,
    param_name: str,
    valuation_fn: Callable[[StartupParams], float],
) -> dict:
    """Compute partial derivative of a scalar valuation w.r.t. one parameter.

    valuation_fn maps a StartupParams to a scalar (e.g. terminal MRR, NPV).
    Returns derivatives from each of the four methods plus the adaptive h
    used. Step is adaptive per parameter — a fixed h=1e-5 cannot work when
    g=0.15 and K=1_000_000 are evaluated by the same loop.
    """
    if param_name not in PARAM_NAMES:
        raise ValueError(f"unknown param {param_name!r}; expected one of {PARAM_NAMES}")
    base_theta = params_to_array(params)
    idx = PARAM_NAMES.index(param_name)
    h = _adaptive_h(base_theta[idx])

    def f(x: float) -> float:
        theta = base_theta.copy()
        theta[idx] = x
        return valuation_fn(array_to_params(theta, params))

    x0 = float(base_theta[idx])
    return {
        "param": param_name,
        "h": h,
        "forward": forward_diff(f, x0, h),
        "central": central_diff(f, x0, h),
        "five_point": five_point(f, x0, h),
        "richardson": richardson(f, x0, h, method="central"),
    }
