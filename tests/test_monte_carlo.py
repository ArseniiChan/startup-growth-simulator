"""Tests for engine/monte_carlo.py."""

from __future__ import annotations

import numpy as np
import pytest

from engine.growth_model import default_params
from engine.monte_carlo import (
    convergence_study,
    kahan_sum,
    naive_sum,
    run_simulation,
)
from engine.utils import convergence_order


# --- summation primitives -------------------------------------------------


def test_kahan_beats_naive_on_pathological_sum():
    """Sum 1e8 + 1e6 copies of 1e-8: exact = 1.01e8.

    Pure-Python naive sum loses precision in the low-order bits as the
    running total grows; Kahan recovers it via the compensation variable.
    """
    big = 1e8
    small = 1e-8
    n_small = 1_000_000
    # Build the sequence: big first, then a million tiny additions
    values = np.empty(n_small + 1, dtype=float)
    values[0] = big
    values[1:] = small
    exact = big + n_small * small  # 1.01e8

    naive = naive_sum(values)
    kahan = kahan_sum(values)
    naive_err = abs(naive - exact)
    kahan_err = abs(kahan - exact)
    assert kahan_err <= naive_err
    # Kahan error should be at most a few ULPs at this magnitude
    assert kahan_err < 1e-6


def test_kahan_sum_simple_case():
    values = np.array([1.0, 2.0, 3.0, 4.0])
    assert abs(kahan_sum(values) - 10.0) < 1e-12


# --- run_simulation contract ----------------------------------------------


def test_run_simulation_returns_expected_keys():
    base = default_params()
    out = run_simulation(base, {"g": 0.01, "mu": 0.005}, N=50, T=12.0, h=0.5, seed=1)
    for k in (
        "valuations", "p_unicorn", "expected_value_kahan", "expected_value_naive",
        "var_5", "std_error", "computation_time", "N", "antithetic"
    ):
        assert k in out
    assert out["valuations"].shape == (50,)
    assert 0.0 <= out["p_unicorn"] <= 1.0
    assert np.all(np.isfinite(out["valuations"]))


def test_run_simulation_reproducible_with_seed():
    base = default_params()
    out1 = run_simulation(base, {"g": 0.02}, N=20, T=12.0, h=0.5, seed=42)
    out2 = run_simulation(base, {"g": 0.02}, N=20, T=12.0, h=0.5, seed=42)
    assert np.array_equal(out1["valuations"], out2["valuations"])


def test_run_simulation_different_seeds_differ():
    base = default_params()
    out1 = run_simulation(base, {"g": 0.02}, N=20, T=12.0, h=0.5, seed=1)
    out2 = run_simulation(base, {"g": 0.02}, N=20, T=12.0, h=0.5, seed=2)
    assert not np.array_equal(out1["valuations"], out2["valuations"])


def test_kahan_and_naive_means_close_for_small_N():
    base = default_params()
    out = run_simulation(base, {"g": 0.01}, N=100, T=12.0, h=0.5, seed=1)
    # For small N the difference between methods is tiny; main point is
    # that both keys exist and are close.
    assert abs(out["expected_value_kahan"] - out["expected_value_naive"]) < 1.0


# --- convergence study ---------------------------------------------------


def test_mc_convergence_study_slope_near_minus_half():
    """std error vs N should fall as 1/sqrt(N) — slope -0.5 on log-log."""
    base = default_params()
    out = convergence_study(
        base,
        {"g": 0.02, "mu": 0.01},
        N_values=(50, 200, 800),  # small for test speed
        M_batches=10,
        T=12.0,
        h=0.5,
    )
    # std_estimates ~ C / sqrt(N). The convergence_order helper expects
    # error vs h-like quantity; here the "step" is 1/sqrt(N).
    one_over_sqrt_N = 1.0 / np.sqrt(out["N_values"].astype(float))
    slope = convergence_order(out["std_estimates"], one_over_sqrt_N)
    # The relationship is std ∝ 1/sqrt(N), so std vs (1/sqrt(N)) has slope ~ +1.
    assert abs(slope - 1.0) < 0.5  # MC noise is high at small N; loose tol


# --- antithetic variates -------------------------------------------------


def test_antithetic_variance_no_worse_than_standard_at_large_N():
    """Antithetic should not increase variance noticeably; on smooth
    valuations it usually decreases it. We require variance(antithetic)
    <= 1.5 * variance(standard) — antithetic is not guaranteed to win,
    so we only check it doesn't substantially hurt."""
    base = default_params()
    N = 200
    res_std = run_simulation(base, {"g": 0.03}, N=N, T=12.0, h=0.5, seed=1, antithetic=False)
    res_anti = run_simulation(base, {"g": 0.03}, N=N, T=12.0, h=0.5, seed=1, antithetic=True)
    var_std = float(np.var(res_std["valuations"], ddof=1))
    var_anti = float(np.var(res_anti["valuations"], ddof=1))
    assert var_anti <= 1.5 * var_std
