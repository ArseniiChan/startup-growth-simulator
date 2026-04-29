"""Startup growth ODE system and parameter handling."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from typing import Sequence

import numpy as np


# Order of parameters in flat arrays (used by params_to_array, array_to_params, optimizer).
PARAM_NAMES: tuple[str, ...] = ("g", "K", "alpha", "mu", "p", "mu_R", "F", "v")


@dataclass
class StartupParams:
    """Parameters for the 4D startup growth ODE system.

    g     : monthly growth rate of user acquisition (e.g., 0.15 = 15%/month).
    K     : carrying capacity / total addressable market in users.
    alpha : conversion rate of new signups to paying users.
    mu    : monthly user churn rate for paying users.
    p     : ARPU (average revenue per paying user per month).
    mu_R  : monthly revenue decay rate (cancellations + downgrades combined).
    F     : fixed monthly costs.
    v     : variable cost per newly acquired user.
    """

    g: float
    K: float
    alpha: float
    mu: float
    p: float
    mu_R: float
    F: float
    v: float

    LOWER = np.array([0.001, 10_000, 0.001, 0.0, 1.0, 0.0, 1_000, 0.0])
    UPPER = np.array(
        [1.0, 1_000_000_000, 0.8, 0.5, 1000.0, 0.5, 10_000_000, 500.0]
    )


def growth_system(t: float, y: np.ndarray, params: StartupParams) -> np.ndarray:
    """The 4D ODE system in standard form f(t, y, params) -> dy/dt.

    State y = [U, A, R, Cash]:
        dU/dt    = g * U * (1 - U/K)
        dA/dt    = alpha * g * U * (1 - U/K) - mu * A
        dR/dt    = p * alpha * g * U * (1 - U/K) - mu_R * R
        dCash/dt = R - F - v * g * U * (1 - U/K)

    The system is autonomous (no explicit t dependence), but t is kept in the
    signature so every solver can use a single uniform interface.
    """
    U, A, R, Cash = y[0], y[1], y[2], y[3]
    new_users = params.g * U * (1.0 - U / params.K)

    dU = new_users
    dA = params.alpha * new_users - params.mu * A
    dR = params.p * params.alpha * new_users - params.mu_R * R
    dCash = R - params.F - params.v * new_users
    return np.array([dU, dA, dR, dCash], dtype=float)


def default_params() -> StartupParams:
    """Reasonable defaults for an early-stage SaaS startup."""
    return StartupParams(
        g=0.15,
        K=1_000_000,
        alpha=0.05,
        mu=0.03,
        p=50.0,
        mu_R=0.04,
        F=50_000.0,
        v=10.0,
    )


def preset_profiles() -> dict[str, StartupParams]:
    """Pre-configured parameter profiles for common startup archetypes."""
    return {
        "saas": StartupParams(
            g=0.12, K=500_000, alpha=0.06, mu=0.025,
            p=60.0, mu_R=0.03, F=80_000.0, v=12.0,
        ),
        "marketplace": StartupParams(
            g=0.20, K=5_000_000, alpha=0.02, mu=0.05,
            p=15.0, mu_R=0.06, F=120_000.0, v=4.0,
        ),
        "enterprise": StartupParams(
            g=0.07, K=50_000, alpha=0.20, mu=0.01,
            p=500.0, mu_R=0.015, F=300_000.0, v=200.0,
        ),
        "viral": StartupParams(
            g=0.35, K=20_000_000, alpha=0.01, mu=0.08,
            p=8.0, mu_R=0.10, F=60_000.0, v=2.0,
        ),
    }


def params_to_array(
    params: StartupParams, fit_indices: Sequence[int] | None = None
) -> np.ndarray:
    """Flatten StartupParams to a NumPy array.

    If fit_indices is given, return only those entries (for partial calibration).
    Indices follow PARAM_NAMES order: 0=g, 1=K, 2=alpha, 3=mu, 4=p, 5=mu_R, 6=F, 7=v.
    """
    full = np.array([getattr(params, name) for name in PARAM_NAMES], dtype=float)
    if fit_indices is None:
        return full
    return full[list(fit_indices)]


def array_to_params(
    theta: np.ndarray,
    base_params: StartupParams,
    fit_indices: Sequence[int] | None = None,
) -> StartupParams:
    """Unpack a flat array back to StartupParams.

    If fit_indices is given, theta has only the fitted entries and the rest come
    from base_params. Otherwise theta is a full 8-element array.
    """
    theta = np.asarray(theta, dtype=float)
    if fit_indices is None:
        if theta.shape[0] != len(PARAM_NAMES):
            raise ValueError(
                f"theta must have length {len(PARAM_NAMES)} when fit_indices is None"
            )
        return StartupParams(**{name: float(theta[i]) for i, name in enumerate(PARAM_NAMES)})

    if len(fit_indices) != theta.shape[0]:
        raise ValueError("len(fit_indices) must match len(theta)")
    updates = {PARAM_NAMES[idx]: float(theta[i]) for i, idx in enumerate(fit_indices)}
    return replace(base_params, **updates)


def clip_params(theta: np.ndarray, fit_indices: Sequence[int] | None = None) -> np.ndarray:
    """Clip a parameter array to the StartupParams physical bounds.

    If fit_indices is given, theta and bounds are subset to those indices.
    """
    theta = np.asarray(theta, dtype=float)
    if fit_indices is None:
        return np.clip(theta, StartupParams.LOWER, StartupParams.UPPER)
    idx = list(fit_indices)
    return np.clip(theta, StartupParams.LOWER[idx], StartupParams.UPPER[idx])
