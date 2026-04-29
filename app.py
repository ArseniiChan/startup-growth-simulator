"""Streamlit dashboard — interactive front-end for the engine.

Run locally:
    streamlit run app.py

Deploy: connect this repo to Streamlit Community Cloud and select app.py.

The dashboard imports ONLY from the engine package — no inline numerics.
Every solver, optimizer, root-finder, integrator, and Monte Carlo loop
on this page lives in engine/* and is covered by the test suite.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from engine import (
    StartupParams,
    adams_bashforth4,
    adams_moulton_pc,
    bisection,
    central_diff,
    cubic_spline_natural,
    default_params,
    euler,
    find_brackets,
    growth_system,
    heun,
    newton,
    preset_profiles,
    rk4,
    run_simulation,
    secant,
    sensitivity_analysis,
)


SOLVERS = {
    "Euler": euler,
    "Heun": heun,
    "RK4": rk4,
    "AB4": adams_bashforth4,
    "AB-AM PECE": adams_moulton_pc,
}


# ----------------------------------------------------------------------------
# Sidebar — startup parameter controls
# ----------------------------------------------------------------------------

st.set_page_config(page_title="Startup Growth Simulator", layout="wide")
st.title("Startup Growth Simulator")
st.caption(
    "A 4D ODE simulator built from scratch in Python. CSC 30100 final project. "
    "Driving question: *at what user-churn rate does growth become "
    "mathematically irreversible — and how confident can we be in that answer?*"
)

with st.sidebar:
    st.header("Startup profile")
    profile_names = ["custom", *list(preset_profiles().keys())]
    profile = st.selectbox("Preset", profile_names, index=0)

    if profile == "custom":
        base = default_params()
    else:
        base = preset_profiles()[profile]

    st.header("Parameters")
    g = st.slider("growth rate g", 0.005, 0.5, float(base.g), 0.005)
    K = st.number_input("market size K", 10_000, 1_000_000_000, int(base.K), step=10_000)
    alpha = st.slider("conversion α", 0.001, 0.5, float(base.alpha), 0.005)
    mu = st.slider("user churn μ", 0.001, 0.499, float(base.mu), 0.005)
    p = st.slider("ARPU $p", 1.0, 1000.0, float(base.p), 1.0)
    mu_R = st.slider("billing-cycle lag rate μ_R", 0.005, 0.499, float(base.mu_R), 0.005)
    F = st.number_input("fixed costs F ($)", 1_000, 10_000_000, int(base.F), step=1_000)
    v = st.slider("variable cost v per acquisition ($)", 0.0, 500.0, float(base.v), 1.0)

    params = StartupParams(g=g, K=K, alpha=alpha, mu=mu, p=p, mu_R=mu_R, F=F, v=v)

    st.header("Horizon & solver")
    T = st.slider("horizon (months)", 12, 240, 60)
    h = st.select_slider("step h", [0.05, 0.1, 0.2, 0.5, 1.0], value=0.2)
    solver_name = st.selectbox("ODE solver", list(SOLVERS.keys()), index=2)
    solver = SOLVERS[solver_name]


# ----------------------------------------------------------------------------
# Solve once and cache for the tabs to share.
# ----------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def _solve(params_tuple, T, h, solver_name):
    params = StartupParams(*params_tuple)
    s = SOLVERS[solver_name]
    y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
    t, y = s(growth_system, y0, (0.0, T), h, params)
    return t, y


t, y = _solve(
    (params.g, params.K, params.alpha, params.mu,
     params.p, params.mu_R, params.F, params.v),
    T, h, solver_name,
)
U, A, R, Cash = y[:, 0], y[:, 1], y[:, 2], y[:, 3]


# ----------------------------------------------------------------------------
# Tabs
# ----------------------------------------------------------------------------

tab_traj, tab_mc, tab_breakeven, tab_sens = st.tabs(
    ["Growth trajectory", "Monte Carlo", "Break-even", "Sensitivity"]
)


# ---- Tab 1: Growth trajectory ---------------------------------------------

with tab_traj:
    st.subheader("4D state trajectory")
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.5), sharex=True)
    axes[0, 0].plot(t, U, color="#1f77b4")
    axes[0, 0].set_ylabel("Total users U(t)")
    axes[0, 0].axhline(params.K, color="grey", lw=0.6, ls="--")

    axes[0, 1].plot(t, A, color="#2ca02c")
    axes[0, 1].set_ylabel("Active paying users A(t)")

    axes[1, 0].plot(t, R, color="#d62728")
    axes[1, 0].set_ylabel("MRR R(t) ($)")
    axes[1, 0].set_xlabel("Months")

    axes[1, 1].plot(t, Cash, color="#9467bd")
    axes[1, 1].axhline(0, color="black", lw=0.6)
    axes[1, 1].set_ylabel("Cash balance ($)")
    axes[1, 1].set_xlabel("Months")

    fig.tight_layout()
    st.pyplot(fig)

    st.subheader("Headline metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("peak users", f"{U.max():,.0f}")
    c2.metric("peak MRR", f"${R.max():,.0f}")
    c3.metric("terminal cash", f"${Cash[-1]:,.0f}")
    runway_idx = np.argmax(Cash < 0) if np.any(Cash < 0) else None
    if runway_idx and runway_idx > 0:
        c4.metric("runway dies at", f"month {t[runway_idx]:.1f}")
    else:
        c4.metric("runway", "intact" if Cash[-1] >= 0 else "at risk")


# ---- Tab 2: Monte Carlo ---------------------------------------------------

with tab_mc:
    st.subheader("Monte Carlo over parameter uncertainty")
    st.caption(
        "Sample perturbed parameters, solve the ODE for each draw, build the "
        "distribution of terminal valuation V(T) = multiple × R(T)."
    )

    col1, col2 = st.columns(2)
    with col1:
        N = st.select_slider("N (trials)", [100, 500, 1_000, 2_500, 5_000], value=1_000)
        sigma_g = st.slider("σ on growth rate g", 0.0, 0.10, 0.04, 0.005)
        sigma_mu = st.slider("σ on churn μ", 0.0, 0.05, 0.015, 0.005)
    with col2:
        sigma_K = st.slider("σ on log(K)", 0.0, 0.50, 0.30, 0.05)
        multiple = st.slider("revenue multiple", 1.0, 20.0, 5.0, 0.5)
        antithetic = st.checkbox("antithetic variates", value=False)

    st.info(
        "Click **Run Monte Carlo** to sample N parameter sets, solve the ODE "
        "for each, and produce a histogram of terminal valuations. Returns "
        "P(unicorn), expected value (Kahan-summed), Value-at-Risk, and "
        "standard error. Wall time scales linearly with N."
    )
    if st.button("Run Monte Carlo", type="primary"):
        with st.spinner(f"running {N} trials..."):
            res = run_simulation(
                params,
                {"g": sigma_g, "mu": sigma_mu, "K": sigma_K},
                N=N, T=float(T), h=h, multiple=multiple,
                antithetic=antithetic, seed=2026,
            )
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("P(unicorn)", f"{res['p_unicorn']*100:.1f}%")
        c2.metric("E[V]", f"${res['expected_value_kahan']/1e6:,.1f}M")
        c3.metric("VaR(5%)", f"${res['var_5']/1e6:,.1f}M")
        c4.metric("std error", f"${res['std_error']/1e6:,.2f}M")

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.hist(res["valuations"] / 1e6, bins=40, color="#1f77b4", alpha=0.85, edgecolor="white")
        ax.axvline(1000, color="#d62728", lw=2, ls="--", label="unicorn $1B")
        ax.set_xlabel("V(T) ($M)"); ax.set_ylabel("count")
        ax.set_title(f"{N} simulated outcomes  (wall: {res['computation_time']:.1f}s)")
        ax.legend()
        st.pyplot(fig)


# ---- Tab 3: Break-even / runway -------------------------------------------

with tab_breakeven:
    st.subheader("μ* — the critical churn threshold")
    st.caption(
        "Find the user-churn rate at which Cash(T) = 0 — above this μ, the startup "
        "ends the horizon cash-negative. Three root-finders compared."
    )

    T_breakeven = st.slider(
        "horizon for μ* search (months)", 24, 240, max(120, int(T)),
    )

    def cash_terminal(mu_value, p=params, T=T_breakeven, h=0.5):
        pp = replace(p, mu=float(mu_value))
        y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
        _, ys = rk4(growth_system, y0, (0.0, T), h, pp)
        return float(ys[-1, 3])

    st.info(
        "Click **Find μ\\*** to scan the physical churn range, bracket the sign "
        "change in Cash(T), then triangulate the threshold with Newton, "
        "bisection, and secant. Reports iteration counts for each method. "
        "Above μ\\*, the company ends the horizon cash-negative; below, it survives."
    )
    if st.button("Find μ*", type="primary"):
        mu_grid = np.linspace(0.005, 0.499, 60)
        with st.spinner("scanning for sign change..."):
            brackets = find_brackets(cash_terminal, mu_grid)
        if not brackets:
            st.error(
                "No sign change found in [0.005, 0.499]. Either the startup "
                "is too profitable (always survives) or too unprofitable "
                "(never survives) at every churn rate. Try other parameters."
            )
        else:
            a, b = brackets[0]
            df = lambda m: central_diff(cash_terminal, float(m), h=5e-4)
            res_n = newton(cash_terminal, df, x0=0.5*(a+b), tol=1e-6, max_iter=30, bounds=(a, b))
            res_b = bisection(cash_terminal, a, b, tol=1e-6, max_iter=60)
            res_s = secant(cash_terminal, a, b, tol=1e-6, max_iter=30)

            c1, c2, c3 = st.columns(3)
            c1.metric("Newton μ*", f"{res_n['root']*100:.3f}%", f"{res_n['iterations']} iters")
            c2.metric("Bisection μ*", f"{res_b['root']*100:.3f}%", f"{res_b['iterations']} iters")
            c3.metric("Secant μ*", f"{res_s['root']*100:.3f}%", f"{res_s['iterations']} iters")

            mu_dense = np.linspace(0.005, 0.499, 100)
            f_dense = np.array([cash_terminal(m) for m in mu_dense]) / 1e6
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(mu_dense, f_dense, color="#1f77b4")
            ax.axhline(0, color="black", lw=0.8)
            ax.axvline(res_n["root"], color="#d62728", lw=2, ls="--", label=f"μ* ≈ {res_n['root']*100:.2f}%")
            ax.set_xlabel("churn rate μ (per month)"); ax.set_ylabel("Cash(T) ($M)")
            ax.legend()
            st.pyplot(fig)


# ---- Tab 4: Sensitivity ---------------------------------------------------

with tab_sens:
    st.subheader("∂(metric) / ∂(parameter)")
    st.caption(
        "Numerical derivative of a chosen metric with respect to each parameter, "
        "via central differences with adaptive per-parameter step size."
    )

    metric_name = st.selectbox(
        "Metric",
        ["terminal MRR R(T)", "terminal cash Cash(T)", "peak users U_peak"],
    )

    def metric_of(p):
        y0 = np.array([100.0, 0.0, 0.0, 1_000_000.0])
        _, ys = rk4(growth_system, y0, (0.0, T), h, p)
        if metric_name.startswith("terminal MRR"):
            return float(ys[-1, 2])
        if metric_name.startswith("terminal cash"):
            return float(ys[-1, 3])
        return float(np.max(ys[:, 0]))

    st.info(
        "Click **Compute sensitivities** to compute the partial derivative of "
        "the chosen metric with respect to each model parameter via central "
        "differences with adaptive per-parameter step size. Bars are sorted "
        "by absolute size — the longest bar moves the metric the most."
    )
    if st.button("Compute sensitivities", type="primary"):
        names = ("g", "K", "alpha", "mu", "p", "mu_R", "F", "v")
        vals = []
        for n in names:
            try:
                out = sensitivity_analysis(params, n, metric_of)
                vals.append(out["central"])
            except Exception:
                vals.append(0.0)
        order = sorted(range(len(names)), key=lambda i: -abs(vals[i]))
        names_sorted = [names[i] for i in order]
        vals_sorted = [vals[i] for i in order]

        fig, ax = plt.subplots(figsize=(8, 4.5))
        colors = ["#d62728" if v < 0 else "#2ca02c" for v in vals_sorted]
        ax.barh(names_sorted, vals_sorted, color=colors)
        ax.axvline(0, color="black", lw=0.6)
        ax.set_xlabel(f"∂({metric_name}) / ∂(parameter)")
        ax.invert_yaxis()
        st.pyplot(fig)
