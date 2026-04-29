"""Tests for engine/differentiation.py."""

from __future__ import annotations

import numpy as np
import pytest

from engine.differentiation import (
    central_diff,
    five_point,
    forward_diff,
    optimal_h_study,
    richardson,
    second_derivative,
    sensitivity_analysis,
)
from engine.growth_model import default_params
from engine.utils import convergence_order


# Reference functions with known derivatives.

def f_sin(x):
    return np.sin(x)


def df_sin(x):
    return np.cos(x)


def d2f_sin(x):
    return -np.sin(x)


def f_poly5(x):
    """f(x) = x^5; f'(x) = 5 x^4."""
    return x**5


def df_poly5(x):
    return 5.0 * x**4


# --- accuracy at a single x -------------------------------------------------


def test_forward_diff_basic_accuracy():
    err = abs(forward_diff(f_sin, 1.0, h=1e-5) - df_sin(1.0))
    assert err < 1e-3


def test_central_diff_basic_accuracy():
    err = abs(central_diff(f_sin, 1.0, h=1e-5) - df_sin(1.0))
    assert err < 1e-8


def test_five_point_basic_accuracy():
    err = abs(five_point(f_sin, 1.0, h=1e-3) - df_sin(1.0))
    assert err < 1e-12


def test_polynomial_exactness_high_order():
    """5-point is O(h^4); exact for polynomials of degree <= 4. On x^5 the
    truncation error is c * h^4 (here ~4 h^4 since the 5th derivative is
    120 and the leading coefficient in the error term is 1/30). At h = 1e-3
    the error should be ~4e-12 — round-off dominated, not truncation."""
    err = abs(five_point(f_poly5, 2.0, h=1e-3) - df_poly5(2.0))
    assert err < 1e-9


def test_second_derivative_accuracy():
    err = abs(second_derivative(f_sin, 1.0, h=1e-3) - d2f_sin(1.0))
    assert err < 1e-5


# --- convergence order tests ------------------------------------------------


def test_forward_diff_convergence_order():
    """Forward difference: |error| ~ h, slope ~ 1."""
    h_values = np.array([1e-2, 5e-3, 2.5e-3, 1.25e-3, 6.25e-4])
    errs = np.array([
        abs(forward_diff(f_sin, 1.0, h=h) - df_sin(1.0)) for h in h_values
    ])
    slope = convergence_order(errs, h_values)
    assert abs(slope - 1.0) < 0.2


def test_central_diff_convergence_order():
    """Central difference: |error| ~ h^2, slope ~ 2."""
    h_values = np.array([1e-2, 5e-3, 2.5e-3, 1.25e-3, 6.25e-4])
    errs = np.array([
        abs(central_diff(f_sin, 1.0, h=h) - df_sin(1.0)) for h in h_values
    ])
    slope = convergence_order(errs, h_values)
    assert abs(slope - 2.0) < 0.2


def test_five_point_convergence_order():
    """5-point: |error| ~ h^4, slope ~ 4."""
    h_values = np.array([1e-2, 5e-3, 2.5e-3, 1.25e-3, 6.25e-4])
    errs = np.array([
        abs(five_point(f_sin, 1.0, h=h) - df_sin(1.0)) for h in h_values
    ])
    slope = convergence_order(errs, h_values)
    assert abs(slope - 4.0) < 0.4


# --- richardson extrapolation -----------------------------------------------


def test_richardson_lifts_central_to_order_4():
    """Richardson on central diff should be at least 4th order accurate."""
    err_central = abs(central_diff(f_sin, 1.0, h=1e-2) - df_sin(1.0))
    err_rich = abs(richardson(f_sin, 1.0, h=1e-2, method="central") - df_sin(1.0))
    assert err_rich < err_central * 1e-3  # at least three orders better


def test_richardson_unknown_method_raises():
    with pytest.raises(ValueError):
        richardson(f_sin, 1.0, method="banana")


# --- optimal h sweep --------------------------------------------------------


def test_optimal_h_study_returns_u_curve():
    """The error vs h plot should descend then rise (truncation -> round-off)."""
    out = optimal_h_study(f_sin, 1.0, df_sin(1.0), h_range=np.logspace(-15, -1, 30))
    central_errors = out["central"]
    # The minimum should be in the interior, not at either end.
    argmin = np.argmin(central_errors)
    assert 0 < argmin < central_errors.size - 1


# --- sensitivity analysis on the ODE ----------------------------------------


def test_sensitivity_analysis_g_recovers_growth_rate_sign():
    """Higher growth rate g produces higher terminal MRR. Partial w.r.t. g must be > 0."""
    from engine.growth_model import growth_system
    from engine.ode_solvers import rk4

    base = default_params()
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])

    def valuation(p):
        _, y = rk4(growth_system, y0, (0.0, 36.0), 0.1, p)
        return float(y[-1, 2])  # terminal MRR

    out = sensitivity_analysis(base, "g", valuation)
    assert out["forward"] > 0
    assert out["central"] > 0
    assert out["five_point"] > 0
    assert out["richardson"] > 0


def test_sensitivity_analysis_unknown_param_raises():
    with pytest.raises(ValueError):
        sensitivity_analysis(default_params(), "banana", lambda p: 1.0)
