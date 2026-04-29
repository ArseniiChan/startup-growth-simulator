"""Tests for engine/root_finding.py."""

from __future__ import annotations

import numpy as np
import pytest

from engine.root_finding import bisection, find_brackets, newton, secant


# --- shared test problem: f(x) = x^2 - 4 has roots at +/-2 ------------------


def f_quad(x):
    return x * x - 4.0


def df_quad(x):
    return 2.0 * x


def test_newton_finds_root_of_quadratic():
    out = newton(f_quad, df_quad, x0=3.0)
    assert out["converged"]
    assert abs(out["root"] - 2.0) < 1e-10
    # quadratic convergence should reach tol in well under 20 iterations
    assert out["iterations"] < 15


def test_bisection_finds_root_of_quadratic():
    out = bisection(f_quad, 0.0, 5.0)
    assert out["converged"]
    assert abs(out["root"] - 2.0) < 1e-9


def test_secant_finds_root_of_quadratic():
    out = secant(f_quad, 0.0, 5.0)
    assert out["converged"]
    assert abs(out["root"] - 2.0) < 1e-9


# --- iteration counts: Newton < secant < bisection on smooth problems -----


def test_iteration_counts_ordering():
    """Newton (quadratic conv) needs fewer steps than secant (~1.618)
    needs fewer steps than bisection (linear) on a well-behaved problem.
    Compare at the same tolerance."""
    tol = 1e-10
    n_newton = newton(f_quad, df_quad, 3.0, tol=tol)["iterations"]
    n_secant = secant(f_quad, 1.0, 3.0, tol=tol)["iterations"]
    n_bisect = bisection(f_quad, 0.0, 5.0, tol=tol)["iterations"]
    assert n_newton <= n_secant <= n_bisect


# --- Newton on sin(x) near pi ---------------------------------------------


def test_newton_sin_converges_to_pi():
    out = newton(np.sin, np.cos, x0=3.0)
    assert out["converged"]
    assert abs(out["root"] - np.pi) < 1e-10


# --- failure cases --------------------------------------------------------


def test_bisection_no_sign_change_raises():
    """f(x) = x^2 + 1 has no real root; bisection must refuse."""

    def f(x):
        return x * x + 1.0

    with pytest.raises(ValueError):
        bisection(f, -1.0, 1.0)


def test_newton_handles_zero_derivative_gracefully():
    """f(x) = x^3 has f'(0) = 0; Newton near x=0 must not divide by zero."""

    def f(x):
        return x**3

    def df(x):
        return 3.0 * x**2

    out = newton(f, df, x0=0.0)
    # may not converge but must not crash; converged is False on zero deriv
    assert out["converged"] is False
    assert "reason" in out


def test_newton_with_bounds_falls_back():
    """Tight bounds force Newton's overshoot to use bisection-style fallback."""

    def f(x):
        return x * x - 4.0

    def df(x):
        return 2.0 * x

    out = newton(f, df, x0=1.5, bounds=(1.0, 3.0))
    assert out["converged"]
    assert abs(out["root"] - 2.0) < 1e-9


def test_newton_bounds_fallback_does_real_bisection_step():
    """Regression: an earlier version of newton's bounds fallback collapsed
    to the midpoint of [a, b] regardless of the current iterate. That
    snapped to one fixed point and then declared convergence on the next
    iteration (delta = 0). Verify a problem where Newton overshoots
    early actually converges to the correct root, not to (a+b)/2.

    f(x) = x - 1 - 0.5 sin(x), f(0) = -1, f(2) = 1 - 0.5 sin(2) > 0.
    Root is near x = 1.498. Bounds [0, 2]; midpoint of bounds is 1, which
    is NOT the root. A starting Newton iterate that overshoots forces
    the fallback to be exercised."""

    def f(x):
        return x - 1.0 - 0.5 * np.sin(x)

    def df(x):
        return 1.0 - 0.5 * np.cos(x)

    out = newton(f, df, x0=0.01, bounds=(0.0, 2.0))
    assert out["converged"]
    # midpoint of bounds is 1.0; root is near 1.498 — must be far from 1.0
    assert abs(out["root"] - 1.0) > 0.4
    assert abs(f(out["root"])) < 1e-9


# --- find_brackets ---------------------------------------------------------


def test_find_brackets_returns_empty_for_no_root():
    """f(x) = x^2 + 1 stays positive on [-1, 1]; no brackets."""

    def f(x):
        return x * x + 1.0

    out = find_brackets(f, np.linspace(-1.0, 1.0, 11))
    assert out == []


def test_find_brackets_finds_two_intervals_for_quadratic():
    """f(x) = x^2 - 4 has roots at +/-2; expect 2 sign-change intervals on
    a grid that spans both."""
    out = find_brackets(f_quad, np.linspace(-3.0, 3.0, 21))
    assert len(out) == 2
    # First bracket contains -2, second contains +2
    a1, b1 = out[0]
    a2, b2 = out[1]
    assert a1 <= -2.0 <= b1
    assert a2 <= 2.0 <= b2


def test_find_brackets_handles_exact_zero():
    """If a grid point lands exactly on a root, return a zero-width bracket."""

    def f(x):
        return x

    out = find_brackets(f, np.array([-1.0, 0.0, 1.0]))
    assert any(a == b == 0.0 for a, b in out)
