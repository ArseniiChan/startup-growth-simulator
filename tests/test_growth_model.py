"""Tests for engine/growth_model.py."""

from __future__ import annotations

import numpy as np
import pytest

from engine.growth_model import (
    PARAM_NAMES,
    StartupParams,
    array_to_params,
    clip_params,
    default_params,
    growth_system,
    make_loss_fn,
    mse_loss,
    params_to_array,
    preset_profiles,
)
from engine.ode_solvers import rk4


def test_growth_system_returns_4d_array():
    p = default_params()
    y = np.array([100.0, 5.0, 250.0, 1_000_000.0])
    dy = growth_system(0.0, y, p)
    assert dy.shape == (4,)
    assert np.all(np.isfinite(dy))


def test_growth_system_zero_users_zero_growth():
    p = default_params()
    y = np.array([0.0, 0.0, 0.0, 1_000_000.0])
    dy = growth_system(0.0, y, p)
    assert dy[0] == 0.0  # no users -> no new users
    assert dy[1] == 0.0  # no active users to churn
    assert dy[2] == 0.0  # no revenue
    assert dy[3] == -p.F  # cash burns at fixed cost rate


def test_growth_system_revenue_lags_toward_pA_at_saturation():
    """At saturation (U=K, dU/dt=0) revenue lags toward p*A, not toward zero.

    With R0 < p*A0 the lag pushes R upward; with R0 > p*A0 the lag pulls it
    down. Either way the equilibrium is p*A, never zero (which would be the
    case under the discarded dR/dt = p*alpha*dU/dt - mu_R*R formulation).
    """
    p = default_params()
    A0 = 1_000.0
    R_below = 0.5 * p.p * A0
    R_above = 2.0 * p.p * A0
    y_below = np.array([p.K, A0, R_below, 0.0])
    y_above = np.array([p.K, A0, R_above, 0.0])
    dy_below = growth_system(0.0, y_below, p)
    dy_above = growth_system(0.0, y_above, p)
    assert dy_below[0] == pytest.approx(0.0, abs=1e-9)
    assert dy_below[2] == pytest.approx(p.mu_R * (p.p * A0 - R_below))
    assert dy_below[2] > 0  # R below p*A pushes upward
    assert dy_above[2] < 0  # R above p*A pulls downward


def test_growth_system_revenue_at_pA_is_stationary():
    """If R = p*A then dR/dt = 0 regardless of acquisition rate."""
    p = default_params()
    A = 5_000.0
    y = np.array([100.0, A, p.p * A, 0.0])
    dy = growth_system(0.0, y, p)
    assert dy[2] == pytest.approx(0.0, abs=1e-9)


def test_growth_system_cash_at_break_even():
    """Construct a state where R = F + v * dU/dt and check dCash/dt == 0."""
    p = default_params()
    U = p.K * 0.5
    new_users = p.g * U * (1 - U / p.K)
    R = p.F + p.v * new_users
    y = np.array([U, 0.0, R, 0.0])
    dy = growth_system(0.0, y, p)
    assert dy[3] == pytest.approx(0.0, abs=1e-9)


def test_default_params_returns_startup_params():
    p = default_params()
    assert isinstance(p, StartupParams)
    assert p.g > 0 and p.K > 0


def test_preset_profiles_keys():
    profiles = preset_profiles()
    assert set(profiles.keys()) == {"saas", "marketplace", "enterprise", "viral"}
    for prof in profiles.values():
        assert isinstance(prof, StartupParams)


def test_params_to_array_full_roundtrip():
    p = default_params()
    theta = params_to_array(p)
    assert theta.shape == (8,)
    p2 = array_to_params(theta, p)
    for name in PARAM_NAMES:
        assert getattr(p2, name) == getattr(p, name)


def test_params_to_array_subset_roundtrip():
    p = default_params()
    fit = [0, 1, 5]  # g, K, mu_R
    theta = params_to_array(p, fit_indices=fit)
    assert theta.shape == (3,)
    assert theta[0] == p.g
    assert theta[1] == p.K
    assert theta[2] == p.mu_R

    new_theta = np.array([0.30, 5_000_000.0, 0.10])
    p2 = array_to_params(new_theta, p, fit_indices=fit)
    assert p2.g == 0.30
    assert p2.K == 5_000_000.0
    assert p2.mu_R == 0.10
    # untouched parameters preserved
    assert p2.alpha == p.alpha
    assert p2.mu == p.mu
    assert p2.p == p.p
    assert p2.F == p.F
    assert p2.v == p.v


def test_clip_params_enforces_bounds():
    out_of_bounds = np.array(
        [10.0, 1e12, 5.0, 2.0, 1e6, 5.0, 1e10, 1e5]
    )
    clipped = clip_params(out_of_bounds)
    assert np.all(clipped <= StartupParams.UPPER + 1e-9)
    assert np.all(clipped >= StartupParams.LOWER - 1e-9)


def test_clip_params_subset():
    fit = [0, 3]  # g, mu
    theta = np.array([10.0, 5.0])
    clipped = clip_params(theta, fit_indices=fit)
    assert clipped[0] == StartupParams.UPPER[0]
    assert clipped[1] == StartupParams.UPPER[3]


def test_growth_system_integrates_cleanly_through_rk4():
    """End-to-end sanity: integrate the coupled 4D system from a seed-stage
    state for 24 months and check the trajectory is finite, monotone where it
    should be, and bounded by the carrying capacity. This is the regression
    guard against catastrophic cancellation at large K, NaN propagation, and
    sign errors in the coupling between equations."""
    p = default_params()
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    t, y = rk4(growth_system, y0, (0.0, 24.0), 0.1, p)
    U, A, R, Cash = y[:, 0], y[:, 1], y[:, 2], y[:, 3]
    assert np.all(np.isfinite(y))
    assert np.all(np.diff(U) >= 0)  # users grow monotonically (logistic)
    assert U[-1] < p.K  # never crosses carrying capacity
    assert A[-1] > 0 and R[-1] > 0  # acquisition + lag both produce signal
    assert Cash[-1] < y0[3]  # seed-stage burns cash over 24 months


def test_mse_loss_zero_at_truth():
    """If theta equals the true params used to generate the data, loss is 0."""
    base = default_params()
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    T = 24.0
    t, y = rk4(growth_system, y0, (0.0, T), 0.1, base)
    obs_t = np.linspace(0.0, T, 9)
    obs_R = np.interp(obs_t, t, y[:, 2])

    fit_indices = [0, 5]  # g, mu_R
    theta_truth = params_to_array(base, fit_indices)
    loss = mse_loss(theta_truth, obs_t, obs_R, base, fit_indices, rk4, y0, (0.0, T))
    assert loss < 1e-3  # tiny nonzero from the linear interpolation


def test_mse_loss_grows_when_params_drift():
    """Perturbing g away from truth must strictly increase the loss."""
    base = default_params()
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    T = 24.0
    t, y = rk4(growth_system, y0, (0.0, T), 0.1, base)
    obs_t = np.linspace(0.0, T, 9)
    obs_R = np.interp(obs_t, t, y[:, 2])

    fit_indices = [0]  # only g
    truth = mse_loss(np.array([base.g]), obs_t, obs_R, base, fit_indices, rk4, y0, (0.0, T))
    drift = mse_loss(np.array([0.5 * base.g]), obs_t, obs_R, base, fit_indices, rk4, y0, (0.0, T))
    assert drift > truth + 1e-3


def test_make_loss_fn_returns_callable_with_correct_value():
    base = default_params()
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    T = 12.0
    t, y = rk4(growth_system, y0, (0.0, T), 0.1, base)
    obs_t = np.linspace(0.0, T, 5)
    obs_R = np.interp(obs_t, t, y[:, 2])
    fit_indices = [0, 5]
    loss = make_loss_fn(obs_t, obs_R, base, fit_indices, rk4, y0, (0.0, T))
    theta = params_to_array(base, fit_indices)
    direct = mse_loss(theta, obs_t, obs_R, base, fit_indices, rk4, y0, (0.0, T))
    assert loss(theta) == direct


def test_growth_system_bounded_at_large_carrying_capacity():
    """K=1e9 is at the upper bound; verify no overflow / cancellation when
    U/K is computed near the upper end of the parameter range."""
    p = StartupParams(
        g=0.1, K=1_000_000_000, alpha=0.05, mu=0.03,
        p=50.0, mu_R=0.04, F=50_000.0, v=10.0,
    )
    y0 = np.array([1_000.0, 0.0, 0.0, 1_000_000.0])
    _, y = rk4(growth_system, y0, (0.0, 12.0), 0.1, p)
    assert np.all(np.isfinite(y))
