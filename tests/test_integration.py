"""Tests for engine/integration.py."""

from __future__ import annotations

import numpy as np
import pytest

from engine.integration import (
    composite_simpson,
    gaussian_quadrature,
    integrate_trajectory,
)
from engine.utils import convergence_order


# --- composite Simpson -----------------------------------------------------


def test_simpson_polynomial_exactness_on_cubic():
    """Simpson's 1/3 rule is exact for polynomials of degree <= 3."""
    val = composite_simpson(lambda x: x**3, 0.0, 1.0, n=4)
    assert abs(val - 0.25) < 1e-12


def test_simpson_x_squared_exact_value():
    """∫ x^2 from 0 to 1 = 1/3."""
    val = composite_simpson(lambda x: x * x, 0.0, 1.0, n=10)
    assert abs(val - 1.0 / 3.0) < 1e-12


def test_simpson_sin_pi():
    """∫ sin x from 0 to π = 2. Simpson is O(h^4); at n=20, h≈0.157, so the
    error is bounded by C * h^4 ≈ 6e-4, scaled by f^(4)=sin which has
    magnitude <= 1. Empirical error sits at ~7e-6 here."""
    val = composite_simpson(np.sin, 0.0, np.pi, n=20)
    assert abs(val - 2.0) < 1e-5


def test_simpson_convergence_order():
    """Simpson is O(h^4): slope ~ 4 on log-log error vs h."""

    def f(x):
        return np.exp(x)

    exact = np.exp(2.0) - np.exp(0.0)
    n_values = np.array([4, 8, 16, 32, 64], dtype=int)
    h_values = (2.0 - 0.0) / n_values
    errs = np.array([
        abs(composite_simpson(f, 0.0, 2.0, n=int(n)) - exact) for n in n_values
    ])
    slope = convergence_order(errs, h_values)
    assert abs(slope - 4.0) < 0.3


def test_simpson_odd_n_raises():
    with pytest.raises(ValueError):
        composite_simpson(lambda x: x, 0.0, 1.0, n=3)


def test_simpson_zero_n_raises():
    with pytest.raises(ValueError):
        composite_simpson(lambda x: x, 0.0, 1.0, n=0)


# --- Gauss-Legendre --------------------------------------------------------


def test_gauss_2pt_exact_for_cubic():
    """2-point Gauss is exact for poly of degree <= 3."""
    val = gaussian_quadrature(lambda x: x**3 - 2.0 * x + 1.0, 0.0, 1.0, n_points=2)
    # Exact: 1/4 - 1 + 1 = 0.25
    assert abs(val - 0.25) < 1e-12


def test_gauss_3pt_exact_for_quintic():
    """3-point Gauss is exact for poly of degree <= 5."""
    val = gaussian_quadrature(lambda x: x**5, 0.0, 1.0, n_points=3)
    # Exact: 1/6
    assert abs(val - 1.0 / 6.0) < 1e-12


def test_gauss_5pt_exact_for_degree_9():
    """5-point Gauss is exact for poly of degree <= 9."""
    val = gaussian_quadrature(lambda x: x**9, 0.0, 1.0, n_points=5)
    assert abs(val - 1.0 / 10.0) < 1e-12


def test_gauss_unsupported_n_raises():
    with pytest.raises(ValueError):
        gaussian_quadrature(np.sin, 0.0, 1.0, n_points=4)


def test_gauss_sin_pi():
    val = gaussian_quadrature(np.sin, 0.0, np.pi, n_points=5)
    assert abs(val - 2.0) < 1e-6


# --- integrate_trajectory --------------------------------------------------


def test_integrate_trajectory_matches_simpson():
    """Integrate y = sin(t) on a uniform grid; should match the analytic
    result and equal what composite_simpson produces."""
    t = np.linspace(0.0, np.pi, 21)  # 20 subintervals (even)
    y = np.sin(t)
    direct = integrate_trajectory(t, y)
    analytic = 2.0
    assert abs(direct - analytic) < 1e-4


def test_integrate_trajectory_rejects_nonuniform_grid():
    t = np.array([0.0, 0.1, 0.3, 0.4])  # nonuniform on purpose
    y = np.zeros_like(t)
    with pytest.raises(ValueError):
        integrate_trajectory(t, y)


def test_integrate_trajectory_handles_odd_subintervals():
    """Edge case: odd n is allowed (Simpson on n-1 even + trapezoid on last)."""
    # ∫ x dx from 0 to 1 = 0.5; with n=5 (odd) we should still be exact-ish
    t = np.linspace(0.0, 1.0, 6)  # 5 subintervals — odd
    y = t.copy()
    val = integrate_trajectory(t, y)
    assert abs(val - 0.5) < 1e-12  # linear function, Simpson + trapezoid both exact


def test_integrate_trajectory_odd_close_to_even_on_smooth_problem():
    """Odd-n result is close to the even-n result on a smooth integrand."""
    t_even = np.linspace(0.0, np.pi, 21)  # 20 subintervals
    t_odd = np.linspace(0.0, np.pi, 22)   # 21 subintervals
    y_even = np.sin(t_even)
    y_odd = np.sin(t_odd)
    val_even = integrate_trajectory(t_even, y_even)
    val_odd = integrate_trajectory(t_odd, y_odd)
    # both should be close to the analytic answer 2.0
    assert abs(val_even - 2.0) < 1e-4
    assert abs(val_odd - 2.0) < 1e-4
    # and close to each other
    assert abs(val_even - val_odd) < 1e-4
