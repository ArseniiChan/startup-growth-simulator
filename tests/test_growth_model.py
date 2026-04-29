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
    params_to_array,
    preset_profiles,
)


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


def test_growth_system_revenue_decay_with_no_acquisition():
    """If U=K (saturated) then no new users; dR/dt = -mu_R * R."""
    p = default_params()
    R0 = 500_000.0
    y = np.array([p.K, 1000.0, R0, 0.0])
    dy = growth_system(0.0, y, p)
    assert dy[0] == pytest.approx(0.0, abs=1e-9)
    assert dy[2] == pytest.approx(-p.mu_R * R0)


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
