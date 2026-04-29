# Startup Growth Simulator

A 4D ODE simulator that models a SaaS startup's user acquisition, revenue,
and cash trajectory — built from scratch in Python for **CSC 30100
(Numerical Analysis), City College of New York, Spring 2026**. Final project.

The driving question:
> At what user-churn rate does a startup's growth become *mathematically
> irreversible* — and how confident can we be in that answer?

## Headline Phase 2 result

The 2-parameter calibration of $(g, \mu_R)$ does **not** recover a point —
it recovers a curved valley in parameter space. Growth rate $g$ is
identified to <1%, but $\mu_R$ (the billing-cycle lag rate) lives on a
non-identifiable submanifold over a finite observation window. This is
not a bug; it is a structural-identifiability finding, and it is what
will drive the confidence-interval story for the critical churn rate
$\mu^*$ in Phase 3.

![convergence](report/figures/nb02_convergence.png)
![valley](report/figures/nb03_loss_surface_2param.png)

## Status

- **Phase 1 (shipped):** 4D ODE system, Euler / Heun / RK4, error metrics,
  synthetic data generator, Notebook 1 (model + parameter sweep).
- **Phase 2 (shipped):** Adams-Bashforth-4, Adams-Moulton predictor-corrector,
  numerical differentiation (forward/central/5-point/Richardson),
  gradient descent and Adam optimizers with adaptive numerical gradients,
  Newton/bisection/secant root-finders, MSE loss + closure-factory loss
  builder. Notebooks 2 (solver comparison + convergence) and 3 (model
  calibration on synthetic data). 81 tests passing.
- **Phase 3 (planned):** Monte Carlo (Kahan sum, antithetic variates),
  cubic-spline interpolation (Thomas algorithm), Simpson + Gaussian
  quadrature, Notebooks 4-7, Streamlit dashboard, real S-1 calibration
  data for Shopify/Zoom/Datadog/Snowflake.

Numerical methods are implemented from scratch — no `scipy.integrate`,
`scipy.optimize`, or `scipy.interpolate`. NumPy is used for array
operations only.

## Layout

```
engine/             Pure numerical methods. No UI imports.
  growth_model.py   The 4D ODE on (Users, Active, Revenue, Cash) + mse_loss.
  ode_solvers.py    Euler, Heun, RK4, AB4, AM-PECE.
  optimizer.py      gradient_descent, adam, numerical_gradient.
  differentiation.py forward / central / 5-point / Richardson, plus
                    parameter sensitivity via adaptive h.
  root_finding.py   Newton (with bounds-fallback), bisection, secant,
                    find_brackets.
  utils.py          Error metrics, convergence-order estimation, helpers.

tests/              pytest. 81 tests. Validation-first: no engine module
                    is imported by a notebook until its tests pass.

notebooks/          Analysis notebooks. 3 of 7 currently shipped.
  01_growth_ode_system.ipynb     The 4D model + parameter exploration.
  02_ode_solvers_comparison.ipynb Convergence orders, timing, agreement
                                  on the full 4D system.
  03_model_calibration.ipynb     Synthetic recovery; the valley story.

data/               Datasets and the synthetic generator.
  s1_filings/        Real quarterly revenue (populated Week 3 of Phase 3).
  funding_rounds/    Public funding-round data (populated Week 3).
  generate_synthetic.py  Replayable synthetic generator with fixed seeds.

slides/             Lecture PPTXs (gitignored — local copy only).
report/figures/     Notebook-exported figures (gitignored).
```

## Install and run

```bash
pip install -r requirements.txt
python -m pytest tests/                                # 81 tests, ~17s
python -m data.generate_synthetic                      # writes data/synthetic/*.json
jupyter notebook notebooks/                            # open Notebook 1, 2, or 3
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

See `IMPLEMENTATION_PLAN.md` for the full task breakdown and
`FULL_PROJECT_PLAN.md` for the math, theory, and report outline.
