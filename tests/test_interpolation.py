"""Tests for engine/interpolation.py."""

from __future__ import annotations

import numpy as np
import pytest

from engine.interpolation import (
    cubic_spline_clamped,
    cubic_spline_natural,
    thomas_solve,
)


# --- Thomas algorithm -----------------------------------------------------


def test_thomas_solves_known_tridiagonal():
    """Solve a 4x4 system and check against np.linalg.solve as reference."""
    a = np.array([0.0, -1.0, -1.0, -1.0])
    b = np.array([2.0, 2.0, 2.0, 2.0])
    c = np.array([-1.0, -1.0, -1.0, 0.0])
    d = np.array([1.0, 0.0, 0.0, 1.0])
    A = np.array([
        [2.0, -1.0, 0.0, 0.0],
        [-1.0, 2.0, -1.0, 0.0],
        [0.0, -1.0, 2.0, -1.0],
        [0.0, 0.0, -1.0, 2.0],
    ])
    expected = np.linalg.solve(A, d)
    got = thomas_solve(a, b, c, d)
    assert np.allclose(got, expected, atol=1e-12)


def test_thomas_does_not_mutate_inputs():
    a = np.array([0.0, -1.0, -1.0])
    b = np.array([2.0, 2.0, 2.0])
    c = np.array([-1.0, -1.0, 0.0])
    d = np.array([1.0, 0.0, 1.0])
    a0, b0, c0, d0 = a.copy(), b.copy(), c.copy(), d.copy()
    thomas_solve(a, b, c, d)
    for orig, after in [(a0, a), (b0, b), (c0, c), (d0, d)]:
        assert np.array_equal(orig, after)


# --- natural cubic spline -------------------------------------------------


def test_natural_spline_passes_through_data():
    x = np.linspace(0.0, 4.0, 5)
    y = np.array([1.0, 2.0, 0.0, -1.0, 2.0])
    sp = cubic_spline_natural(x, y)
    for xi, yi in zip(x, y):
        assert abs(sp["eval"](float(xi)) - yi) < 1e-12


def test_natural_spline_endpoint_curvatures_are_zero():
    x = np.linspace(0.0, np.pi, 6)
    y = np.sin(x)
    sp = cubic_spline_natural(x, y)
    assert abs(sp["second_derivative"](float(x[0]))) < 1e-12
    assert abs(sp["second_derivative"](float(x[-1]))) < 1e-12


def test_natural_spline_C2_continuity_at_interior_knots():
    x = np.linspace(0.0, 4.0, 5)
    y = np.array([1.0, 2.0, 0.0, -1.0, 2.0])
    sp = cubic_spline_natural(x, y)
    # Approach each interior knot from below and above by a tiny epsilon;
    # all of S, S', S'' should agree to high precision.
    eps = 1e-9
    for xi in x[1:-1]:
        for func_name in ("eval", "derivative", "second_derivative"):
            f = sp[func_name]
            assert abs(f(float(xi) - eps) - f(float(xi) + eps)) < 1e-6


def test_natural_spline_approximates_sin_smoothly():
    x = np.linspace(0.0, 2.0 * np.pi, 11)
    y = np.sin(x)
    sp = cubic_spline_natural(x, y)
    test_pts = np.linspace(0.1, 2.0 * np.pi - 0.1, 50)
    err = np.max(np.abs(sp["eval"](test_pts) - np.sin(test_pts)))
    assert err < 1e-2


# --- clamped cubic spline -------------------------------------------------


def test_clamped_spline_recovers_cubic_polynomial_exactly():
    """A cubic spline with the correct endpoint derivatives should
    reproduce a cubic polynomial to machine precision."""

    def p(t):
        return t**3 - 2.0 * t**2 + t - 1.0

    def dp(t):
        return 3.0 * t**2 - 4.0 * t + 1.0

    x = np.linspace(0.0, 3.0, 7)
    y = p(x)
    sp = cubic_spline_clamped(x, y, d0=dp(x[0]), dn=dp(x[-1]))
    test_pts = np.linspace(0.05, 2.95, 50)
    err = np.max(np.abs(sp["eval"](test_pts) - p(test_pts)))
    assert err < 1e-10


def test_clamped_spline_endpoint_derivatives_match():
    x = np.linspace(0.0, 1.0, 4)
    y = x * x
    d0 = 0.0   # f'(0) = 0
    dn = 2.0   # f'(1) = 2
    sp = cubic_spline_clamped(x, y, d0=d0, dn=dn)
    assert abs(sp["derivative"](float(x[0])) - d0) < 1e-9
    assert abs(sp["derivative"](float(x[-1])) - dn) < 1e-9


# --- error paths ----------------------------------------------------------


def test_natural_spline_unsorted_x_raises():
    x = np.array([0.0, 2.0, 1.0, 3.0])
    y = np.zeros_like(x)
    with pytest.raises(ValueError):
        cubic_spline_natural(x, y)


def test_natural_spline_too_few_points_raises():
    with pytest.raises(ValueError):
        cubic_spline_natural(np.array([0.0, 1.0]), np.array([0.0, 1.0]))
