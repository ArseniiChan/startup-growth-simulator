# Startup Growth Simulator

A 4D ODE simulator that models a SaaS startup's user acquisition, revenue,
and cash trajectory — built from scratch in Python for **CSC 30100
(Numerical Analysis), City College of New York, Spring 2026**. Final project.

The driving question:
> At what user-churn rate does a startup's growth become *mathematically
> irreversible* — and how confident can we be in that answer?

## What's inside

```
engine/             Pure numerical methods. No UI imports.
  growth_model.py   The 4D ODE on (Users, Active, Revenue, Cash)
  ode_solvers.py    Euler, Heun, RK4 (AB4 + Adams-Moulton in Phase 2)
  utils.py          Error metrics, convergence-order estimation, helpers

tests/              pytest. 34 tests. Validation-first: no engine module
                    is imported by a notebook until its tests pass.

notebooks/          Analysis notebooks. 1 of 7 currently shipped.
data/               S-1 filings, funding-round data, synthetic generator.
slides/             Lecture PPTXs (gitignored — local copy only).
report/figures/     Notebook-exported figures (gitignored).
```

Every numerical method is implemented from scratch — no
`scipy.integrate`, no `scipy.optimize`, no `scipy.interpolate`. NumPy is
used for array operations only. The point is to *build* the methods, not
call them.

## Install and run

```bash
pip install -r requirements.txt
python -m pytest tests/                      # 34 tests, ~0.2s
python -m data.generate_synthetic            # writes data/synthetic/*.json
jupyter notebook notebooks/01_growth_ode_system.ipynb
```

Python 3.11+. NumPy 1.26+ (or 2.x).

## The model

```
dU/dt    = g · U · (1 - U/K)             logistic acquisition
dA/dt    = α · g · U · (1 - U/K) - μ · A conversion - churn
dR/dt    = μ_R · (p · A - R)             first-order lag toward p·A
dCash/dt = R - F - v · g · U · (1 - U/K) revenue - costs
```

The revenue equation is a first-order lag toward the algebraic identity
R = p·A. The 1/μ_R timescale is the *billing-cycle lag* — the gap
between user state changes and recognized MRR (annual contracts,
deferred revenue, dunning).

## Project status

This is in-progress coursework, not a shipped library. Phase 1 (the
ODE system + Euler/Heun/RK4 + the calibration scaffolding) is complete
and tested. Phase 2 will add Adams-Bashforth-4, an Adams-Moulton
predictor-corrector, gradient descent, the Adam optimizer, numerical
differentiation, and root-finding. Phase 3 adds Monte Carlo, cubic
splines, and a Streamlit dashboard.

See `IMPLEMENTATION_PLAN.md` for the full task breakdown and
`FULL_PROJECT_PLAN.md` for the math, theory, and report outline.
