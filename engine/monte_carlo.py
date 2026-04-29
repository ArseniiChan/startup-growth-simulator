"""Monte Carlo simulation of startup outcomes under parameter uncertainty.

Public API:
    kahan_sum(values)              — compensated summation; reduces FP error.
    naive_sum(values)              — for-loop reference for the comparison.
    run_simulation(...)            — sample params, solve ODE, record valuations.
    convergence_study(...)         — std error vs N over M repeated batches.

The terminal valuation is a simple revenue multiple, V(T) = multiple * R(T).
Notebook 4 uses run_simulation for the histogram of P(unicorn) / E[V] / VaR;
Notebook 5 wires the sampled posterior into root-finding for the critical
churn rate mu*.
"""

from __future__ import annotations

import time
from dataclasses import replace
from typing import Iterable

import numpy as np

from engine.growth_model import StartupParams, growth_system
from engine.ode_solvers import rk4


# -- summation primitives ----------------------------------------------------


def kahan_sum(values: Iterable[float]) -> float:
    """Compensated (Kahan) summation. Reduces accumulated round-off error
    by tracking the lost low-order bits in a separate compensation variable.

        sum + c is the running estimate of the true sum.

    For a sum of N IEEE-754 doubles, naive summation has worst-case error
    O(N * eps * max|values|); Kahan reduces that to O(eps * max|values|),
    independent of N.
    """
    s = 0.0
    c = 0.0  # compensation for lost low-order bits
    for v in values:
        y = v - c
        t = s + y
        c = (t - s) - y
        s = t
    return float(s)


def naive_sum(values: Iterable[float]) -> float:
    """Plain Python for-loop summation. Reference for the Kahan comparison."""
    s = 0.0
    for v in values:
        s = s + v
    return float(s)


# -- parameter sampling ------------------------------------------------------


def _sample_params(
    base: StartupParams, uncertainty: dict, rng: np.random.Generator
) -> StartupParams:
    """Draw one perturbed parameter set.

    `uncertainty` maps a parameter name -> 1-sigma standard deviation:
        {'g': 0.03, 'mu': 0.01, 'K': 0.2}

    K is sampled lognormal (its uncertainty std is on log(K)). Everything
    else is sampled normal around the base value, then clipped to the
    physical bounds in StartupParams.LOWER / UPPER so the ODE gets sensible
    inputs.
    """
    out = base
    for name, sigma in uncertainty.items():
        base_val = getattr(out, name)
        if name == "K":
            new_val = float(np.exp(np.log(base_val) + rng.normal(0.0, sigma)))
        else:
            new_val = float(base_val + rng.normal(0.0, sigma))
        out = replace(out, **{name: new_val})
    # Clip to physical bounds (per StartupParams class attributes)
    bounded = {}
    for i, n in enumerate(("g", "K", "alpha", "mu", "p", "mu_R", "F", "v")):
        bounded[n] = float(np.clip(getattr(out, n), StartupParams.LOWER[i], StartupParams.UPPER[i]))
    return StartupParams(**bounded)


# -- valuation per draw ------------------------------------------------------


def _valuation_from_params(
    params: StartupParams,
    y0: np.ndarray,
    T: float,
    h: float,
    multiple: float,
    solver,
) -> float:
    """Solve the ODE with these params and return V(T) = multiple * R(T)."""
    _, y = solver(growth_system, y0, (0.0, T), h, params)
    return float(multiple * y[-1, 2])


# -- driver ------------------------------------------------------------------


def run_simulation(
    base: StartupParams,
    uncertainty: dict,
    N: int,
    T: float = 60.0,
    h: float = 0.1,
    y0: np.ndarray | None = None,
    multiple: float = 50.0,
    unicorn_threshold: float = 1e9,
    antithetic: bool = False,
    solver=rk4,
    seed: int = 0,
) -> dict:
    """Run N Monte Carlo trials and report aggregate statistics.

    For each trial: sample perturbed parameters, solve the 4D ODE for T
    months, record terminal valuation V(T) = multiple * R(T). Return a
    dict with the full valuation array, P(unicorn), expected value
    (computed both naively and with Kahan for comparison), the 5th
    percentile (Value-at-Risk), and wall-clock timing.

    If antithetic=True, draws are paired: each random vector Z is used to
    produce one trajectory, and -Z produces a paired trajectory; the
    paired pair is averaged into a single valuation, then the array of N
    averages is reported. When the valuation is approximately monotonic
    in the perturbation, this halves the variance for the same N.

    Caveat (Phase 3 council review): the post-clip to physical bounds
    breaks the perfect symmetry between +Z and -Z when one sign of the
    pair lands at LOWER or UPPER. The pair is then biased toward the
    feasible region. In practice this is a small effect when the
    uncertainty std is well below the distance to either bound — which is
    the regime the dashboard uses. For unbiased antithetic near a bound,
    set the relevant uncertainty entry to zero or pre-truncate the
    sampling distribution.
    """
    if y0 is None:
        y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    rng = np.random.default_rng(seed)
    valuations = np.empty(N, dtype=float)
    t0 = time.perf_counter()

    if not antithetic:
        for i in range(N):
            params = _sample_params(base, uncertainty, rng)
            valuations[i] = _valuation_from_params(params, y0, T, h, multiple, solver)
    else:
        # For antithetic we need a SymmetricRNG: capture each draw and
        # produce its negation. We do this by sampling a vector of standard
        # normals up front and consuming them by hand for the K (lognormal)
        # path versus everything else (normal).
        param_names = list(uncertainty.keys())
        n_dims = len(param_names)
        for i in range(N):
            z = rng.standard_normal(n_dims)
            for sign in (+1.0, -1.0):
                # Reconstruct a perturbed StartupParams from these signed z's.
                out = base
                for k, name in enumerate(param_names):
                    sigma = uncertainty[name]
                    base_val = getattr(out, name)
                    if name == "K":
                        new_val = float(np.exp(np.log(base_val) + sign * z[k] * sigma))
                    else:
                        new_val = float(base_val + sign * z[k] * sigma)
                    out = replace(out, **{name: new_val})
                # Bound-clip
                clipped = {}
                for j, n in enumerate(("g", "K", "alpha", "mu", "p", "mu_R", "F", "v")):
                    clipped[n] = float(
                        np.clip(getattr(out, n), StartupParams.LOWER[j], StartupParams.UPPER[j])
                    )
                trial_params = StartupParams(**clipped)
                v = _valuation_from_params(trial_params, y0, T, h, multiple, solver)
                if sign == +1.0:
                    plus = v
                else:
                    valuations[i] = 0.5 * (plus + v)

    elapsed = time.perf_counter() - t0
    p_unicorn = float(np.mean(valuations >= unicorn_threshold))
    e_v_naive = naive_sum(valuations) / N
    e_v_kahan = kahan_sum(valuations) / N
    var_5 = float(np.percentile(valuations, 5))
    std_error = float(np.std(valuations, ddof=1) / np.sqrt(N)) if N > 1 else float("nan")
    return {
        "valuations": valuations,
        "p_unicorn": p_unicorn,
        "expected_value_kahan": e_v_kahan,
        "expected_value_naive": e_v_naive,
        "var_5": var_5,
        "std_error": std_error,
        "computation_time": elapsed,
        "N": N,
        "antithetic": antithetic,
    }


def convergence_study(
    base: StartupParams,
    uncertainty: dict,
    N_values: tuple[int, ...] = (100, 1_000, 10_000),
    M_batches: int = 20,
    **kwargs,
) -> dict:
    """For each N, run M independent batches and report the std-dev across
    those M estimates. The expected scaling is std_dev(N) ~ 1/sqrt(N) —
    slope -0.5 on a log-log plot. Repeated batches give a much cleaner
    slope than a single run per N.

    Returns:
        N_values        the tested batch sizes
        mean_estimates  M-batch mean of E[V] at each N
        std_estimates   M-batch std of E[V] at each N (this is the slope)
    """
    means = np.empty(len(N_values), dtype=float)
    stds = np.empty(len(N_values), dtype=float)
    for i, N in enumerate(N_values):
        batch_means = np.empty(M_batches, dtype=float)
        for m in range(M_batches):
            res = run_simulation(base, uncertainty, N, seed=10_000 * (i + 1) + m, **kwargs)
            batch_means[m] = res["expected_value_kahan"]
        means[i] = float(np.mean(batch_means))
        stds[i] = float(np.std(batch_means, ddof=1))
    return {
        "N_values": np.array(N_values),
        "mean_estimates": means,
        "std_estimates": stds,
    }
