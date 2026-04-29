"""Tests for engine/ode_solvers.py."""

from __future__ import annotations

import math

import numpy as np
import pytest

from engine.ode_solvers import euler, heun, rk4
from engine.utils import absolute_error, convergence_order


# --- test problems with known closed-form solutions -------------------------


def f_exp_growth(t, y, k):
    """dy/dt = k*y, exact: y(t) = y0 * exp(k*t)."""
    return k * y


def f_decay(t, y):
    """dy/dt = -2*y, exact: y(t) = y0 * exp(-2*t)."""
    return -2.0 * y


def f_logistic(t, y, r, K):
    """dy/dt = r*y*(1 - y/K)."""
    return r * y * (1.0 - y / K)


def logistic_exact(t, y0, r, K):
    """Closed-form logistic: K / (1 + ((K-y0)/y0) * exp(-r*t))."""
    return K / (1.0 + ((K - y0) / y0) * np.exp(-r * t))


# --- shape and grid tests ---------------------------------------------------


@pytest.mark.parametrize("solver", [euler, heun, rk4])
def test_solver_output_shapes(solver):
    t, y = solver(f_decay, 1.0, (0.0, 1.0), 0.1)
    assert t.shape == (11,)
    assert y.shape == (11, 1)


@pytest.mark.parametrize("solver", [euler, heun, rk4])
def test_solver_hits_exact_final_time(solver):
    """Linspace rule: regardless of h, solver hits t_span[1] exactly."""
    t, _ = solver(f_decay, 1.0, (0.0, 1.0), 0.4)  # 1/0.4 = 2.5 -> 3 steps
    assert t[0] == 0.0
    assert t[-1] == pytest.approx(1.0, abs=1e-12)
    assert len(t) == 4  # ceil(1/0.4) + 1


@pytest.mark.parametrize("solver", [euler, heun, rk4])
def test_solver_handles_vector_state(solver):
    """A 2D ODE: dy1/dt = -y1, dy2/dt = -2*y2 (uncoupled decays)."""

    def f(t, y):
        return np.array([-y[0], -2.0 * y[1]])

    y0 = np.array([1.0, 2.0])
    t, y = solver(f, y0, (0.0, 1.0), 0.05)
    assert y.shape == (t.shape[0], 2)
    # both components decay monotonically
    assert np.all(np.diff(y[:, 0]) < 0)
    assert np.all(np.diff(y[:, 1]) < 0)


# --- accuracy tests ---------------------------------------------------------


def test_rk4_exponential_growth_high_accuracy():
    """RK4 should give very small error on dy/dt = 0.5*y over [0,2]."""
    k = 0.5
    y0 = 1.0
    T = 2.0
    h = 0.05
    t, y = rk4(f_exp_growth, y0, (0.0, T), h, k)
    exact = y0 * np.exp(k * t)
    err = absolute_error(y[:, 0], exact)
    assert err < 1e-6


def test_heun_decay_moderate_accuracy():
    t, y = heun(f_decay, 3.0, (0.0, 1.0), 0.05)
    exact = 3.0 * np.exp(-2.0 * t)
    err = absolute_error(y[:, 0], exact)
    assert err < 1e-2


def test_euler_decay_loose_accuracy():
    t, y = euler(f_decay, 3.0, (0.0, 1.0), 0.01)
    exact = 3.0 * np.exp(-2.0 * t)
    err = absolute_error(y[:, 0], exact)
    assert err < 0.05


@pytest.mark.parametrize("solver", [euler, heun, rk4])
def test_solver_logistic(solver):
    """All solvers should track the logistic curve to a sensible tolerance."""
    r, K, y0 = 1.0, 100.0, 10.0
    t, y = solver(f_logistic, y0, (0.0, 5.0), 0.01, r, K)
    exact = logistic_exact(t, y0, r, K)
    err = absolute_error(y[:, 0], exact)
    # Euler gets the loosest tolerance, RK4 the tightest.
    tol = {"euler": 0.5, "heun": 1e-2, "rk4": 1e-4}[solver.__name__]
    assert err < tol


# --- convergence-order tests -----------------------------------------------


def _final_error(solver, h, y0, T, k):
    """Run solver on dy/dt = k*y, return |y_numeric(T) - y_exact(T)|."""
    t, y = solver(f_exp_growth, y0, (0.0, T), h, k)
    exact_T = y0 * np.exp(k * T)
    return abs(y[-1, 0] - exact_T)


@pytest.mark.parametrize(
    "solver,expected_order",
    [(euler, 1.0), (heun, 2.0), (rk4, 4.0)],
)
def test_solver_convergence_order(solver, expected_order):
    """Verify global error scales like h^p for the expected p."""
    y0 = 1.0
    k = -1.0
    T = 1.0
    requested_h = np.array([0.4, 0.2, 0.1, 0.05, 0.025])
    errs = []
    actual_h = []
    for h in requested_h:
        n_steps = max(1, math.ceil(T / h))
        actual_h.append(T / n_steps)
        errs.append(_final_error(solver, h, y0, T, k))
    actual_h = np.array(actual_h)
    errs = np.array(errs)
    # all errors should be positive and shrinking
    assert np.all(errs > 0)
    slope = convergence_order(errs, actual_h)
    assert abs(slope - expected_order) < 0.3, (
        f"{solver.__name__} slope={slope:.3f}, expected≈{expected_order}"
    )


def test_rk4_exact_one_step_coefficients():
    """Lock in RK4's k1/k2/k3/k4 weights against a hand-computed step.

    For dy/dt = y, y(0)=1, h=0.5, exact one-step RK4 gives:
        k1 = 1
        k2 = 1 + 0.25*1 = 1.25
        k3 = 1 + 0.25*1.25 = 1.3125
        k4 = 1 + 0.5*1.3125 = 1.65625
        y(0.5) = 1 + (0.5/6)*(1 + 2*1.25 + 2*1.3125 + 1.65625) = 1.6484375

    A wrong coefficient (e.g., k4 weight 0.5 instead of 1, or the (1/6,2/6,
    2/6,1/6) blend off) would still pass the loose slope-tolerance test but
    fails this. Catches one kind of bug the convergence test cannot.
    """

    def f(t, y):
        return y

    _, y = rk4(f, 1.0, (0.0, 0.5), 0.5)
    assert y.shape == (2, 1)
    assert y[1, 0] == pytest.approx(1.6484375, abs=1e-12)


def test_all_solvers_share_t_grid():
    """AB4 in Phase 2 will bootstrap from RK4 — the bootstrap is correct only
    if all solvers produce identical t arrays for the same h. The linspace
    rule guarantees this; this test is the contract."""
    t_eul, _ = euler(f_decay, 1.0, (0.0, 1.0), 0.137)  # h that doesn't divide T
    t_heun, _ = heun(f_decay, 1.0, (0.0, 1.0), 0.137)
    t_rk4, _ = rk4(f_decay, 1.0, (0.0, 1.0), 0.137)
    assert np.array_equal(t_eul, t_heun)
    assert np.array_equal(t_eul, t_rk4)


def test_euler_instability_with_large_h():
    """For dy/dt = -50*y, Euler with h=0.05 has |1-50h|=1.5>1 so iterates blow
    up, while RK4 at the same h stays inside its stability region and decays."""

    def f(t, y):
        return -50.0 * y

    h = 0.05
    _, y_eul = euler(f, 1.0, (0.0, 5.0), h)
    _, y_rk4 = rk4(f, 1.0, (0.0, 5.0), h)
    assert np.max(np.abs(y_eul[:, 0])) > 1.0
    assert abs(y_rk4[-1, 0]) < 1.0
