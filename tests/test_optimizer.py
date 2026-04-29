"""Tests for engine/optimizer.py.

Strategy:
- Drive the optimizers against textbook problems with known minimizers
  (a quadratic and Rosenbrock) to validate the optimizer in isolation.
- Then drive them through mse_loss against synthetic startup data with
  known true parameters to validate the calibration end-to-end.
"""

from __future__ import annotations

import numpy as np
import pytest

from engine.growth_model import (
    array_to_params,
    clip_params,
    default_params,
    growth_system,
    make_loss_fn,
    params_to_array,
)
from engine.ode_solvers import rk4
from engine.optimizer import adam, gradient_descent, numerical_gradient


# --- numerical_gradient ----------------------------------------------------


def test_numerical_gradient_matches_analytic_quadratic():
    """f(x, y) = (x-2)^2 + 10(y+1)^2 ; analytic grad = [2(x-2), 20(y+1)]."""

    def loss(theta):
        return (theta[0] - 2.0) ** 2 + 10.0 * (theta[1] + 1.0) ** 2

    theta = np.array([0.5, -0.5])
    grad = numerical_gradient(loss, theta)
    assert np.allclose(grad, [2.0 * (0.5 - 2.0), 20.0 * (-0.5 + 1.0)], atol=1e-6)


def test_numerical_gradient_one_sided_at_lower_bound():
    """If theta_i sits at its lower bound, central diff would evaluate at
    theta_i - h (unphysical, e.g. negative mu_R). With bounds passed,
    numerical_gradient must switch to a forward difference there."""

    calls: list[float] = []

    def loss(theta):
        # f(x) = x^2; gradient at x=0 should be 0.
        # Critically, the loss is undefined for negative x — track and
        # raise if we ever see one.
        if theta[0] < 0:
            raise AssertionError(f"loss called at unphysical theta={theta[0]}")
        calls.append(theta[0])
        return theta[0] ** 2

    theta = np.array([0.0])  # at lower bound
    grad = numerical_gradient(loss, theta, lower=np.array([0.0]))
    assert np.all(np.isfinite(grad))
    # all evaluations should be at >=0
    assert min(calls) >= 0


def test_numerical_gradient_adaptive_h_handles_scale_disparity():
    """Param scale spans 6 decades; adaptive h must keep gradients finite."""

    def loss(theta):
        # theta[0] ~ 0.1, theta[1] ~ 1e6
        return theta[0] ** 2 + (theta[1] / 1e6) ** 2

    theta = np.array([0.15, 1_000_000.0])
    grad = numerical_gradient(loss, theta)  # adaptive h
    assert np.all(np.isfinite(grad))
    # The first component should be ~ 2*0.15; the second ~ 2*1.0/1e6.
    assert abs(grad[0] - 0.30) < 1e-3
    assert abs(grad[1] - 2.0e-6) < 1e-9


# --- gradient descent on a quadratic ---------------------------------------


def test_gradient_descent_quadratic_converges():
    def loss(theta):
        return (theta[0] - 2.0) ** 2 + 10.0 * (theta[1] + 1.0) ** 2

    def grad(theta):
        return np.array([2.0 * (theta[0] - 2.0), 20.0 * (theta[1] + 1.0)])

    out = gradient_descent(loss, grad, np.array([0.0, 0.0]), lr=0.05, max_iter=500)
    assert out["converged"]
    assert np.allclose(out["theta"], [2.0, -1.0], atol=1e-3)
    assert out["loss_history"][-1] < 1e-6


# --- Adam on Rosenbrock ----------------------------------------------------


def test_adam_rosenbrock_makes_progress():
    """Rosenbrock is hard; we just require Adam to drop loss by 100x in 5000 iters."""

    def loss(theta):
        return (1.0 - theta[0]) ** 2 + 100.0 * (theta[1] - theta[0] ** 2) ** 2

    def grad(theta):
        x, y = theta
        return np.array(
            [-2.0 * (1.0 - x) - 400.0 * x * (y - x * x), 200.0 * (y - x * x)]
        )

    out = adam(loss, grad, np.array([-1.2, 1.0]), lr=1e-2, max_iter=5000)
    initial = out["loss_history"][0]
    final = out["loss_history"][-1]
    assert final < initial / 100.0


# --- end-to-end calibration on synthetic startup data ----------------------


def test_synthetic_recovery_via_adam_recovers_growth_rate():
    """1-parameter recovery: scramble g, hold all other params at truth, let
    Adam pull g back. This is the well-conditioned cousin of the full
    calibration; it validates the optimizer + loss + interpolation pipeline.

    Multi-parameter recovery (g, mu_R together) is genuinely harder because
    mu_R is a lag rate and can partially mimic changes in g over a finite
    window. That story belongs in Notebook 3 with non-dimensionalization
    and a longer observation window — not in a unit test.
    """
    base = default_params()
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    T = 36.0

    _, y_true = rk4(growth_system, y0, (0.0, T), 0.1, base)
    obs_t = np.linspace(0.0, T, 13)
    obs_R = np.interp(obs_t, np.linspace(0.0, T, y_true.shape[0]), y_true[:, 2])

    fit_indices = [0]  # g only
    loss = make_loss_fn(obs_t, obs_R, base, fit_indices, rk4, y0, (0.0, T))

    def project(theta):
        return clip_params(theta, fit_indices)

    def grad(theta):
        return numerical_gradient(loss, theta)

    theta0 = np.array([2.0 * base.g])  # start far from truth
    out = adam(loss, grad, theta0, lr=5e-3, max_iter=1500, project=project)

    g_hat = float(out["theta"][0])
    rel_g = abs(g_hat - base.g) / base.g
    assert rel_g < 0.10, f"g recovery: rel_err={rel_g:.3f}"
    assert out["loss_history"][-1] < 0.01 * out["loss_history"][0]


# --- bounds projection -----------------------------------------------------


def test_gradient_descent_respects_projection():
    """A loss minimized outside the feasible set must be projected back in."""

    def loss(theta):
        return (theta[0] - 100.0) ** 2  # min at x=100

    def grad(theta):
        return np.array([2.0 * (theta[0] - 100.0)])

    def project(theta):
        return np.minimum(theta, 5.0)  # box ceiling at 5

    out = gradient_descent(
        loss, grad, np.array([0.0]), lr=0.5, max_iter=200, project=project
    )
    assert out["theta"][0] <= 5.0 + 1e-12
