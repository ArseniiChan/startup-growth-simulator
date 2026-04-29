# Startup Growth Simulator

**In one sentence:** I built a tool that finds the exact monthly user-cancellation
rate above which a typical SaaS startup runs out of money before it can ever
recover, and put a confidence interval around the answer using only numerical
methods I implemented from scratch.

For the default-SaaS profile that rate is **about 14% per month**, with
calibration uncertainty putting the 95% confidence range at **8%–16%**.
Above 14% monthly user churn, the business ends a 10-year horizon cash-negative;
below, it survives. We call this μ\* — the *runway-survival threshold at T = 120*.

This is the final project for **CSC 30100 (Numerical Analysis), City College of
New York, Spring 2026**. Every numerical method here — five ODE solvers,
gradient descent, Adam, Newton/bisection/secant, finite differences, Richardson
extrapolation, the Thomas algorithm, cubic splines, composite Simpson, Gaussian
quadrature, Monte Carlo with Kahan summation — was implemented from scratch.
No SciPy.

The driving question:
> At what user-churn rate does a startup's growth become *mathematically
> irreversible* — and how confident can we be in that answer?

(For precision in the report: μ\* is the runway-survival threshold at the
specific 10-year horizon we evaluate, not the abstract phase-portrait
separatrix. The two coincide for the regimes we tested.)

## The two findings I'm proudest of

**1. The headline answer with a real confidence interval.** μ\* ≈ 14.2% per month,
95% CI [8.0%, 16.0%], obtained by sampling the calibrated parameters from
their posterior, solving the ODE for each sample, and bisecting on the
terminal-cash sign change. Newton converges in 3 iterations, secant in 4,
bisection in 20 — exactly the textbook ordering.

**2. A structural-identifiability finding.** When I fit the model to noisy
revenue data, two of its parameters — growth rate $g$ and the billing-cycle
lag $\mu_R$ — can't be separately identified from a finite observation
window. The fit produces a curved valley in parameter space, not a single
best-fit point. I then asked the harder question: does that ambiguity
matter for the answer? Walking the valley via the smallest-eigenvalue
eigenvector of the calibration loss Hessian, μ\* varies by ~2.4%.
**Even though the calibration is ambiguous, the answer it produces is
robust to that ambiguity.** That's a kind of result undergraduate
projects don't typically uncover, and it's documented honestly in
[Notebook 5](notebooks/05_sensitivity_analysis.ipynb).

> ⚠ **One caveat in the headline number:** the 95% CI above propagates
> uncertainty in $(g, \mu_R)$ only — the conversion rate $\alpha$ is
> held at its calibrated MAP. Because $\alpha$ has the largest sensitivity
> ($\partial\mu^*/\partial\alpha \approx 3.04$, vs. 1.18 for $\mu_R$ and 0.51
> for $g$), the marginal CI under joint uncertainty is wider than the
> conditional CI reported. A full joint posterior is deferred to Phase 4
> per `IMPLEMENTATION_PLAN.md`.

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
  calibration on synthetic data with the structural-identifiability
  finding).
- **Phase 3 (shipped):** composite Simpson + Gauss-Legendre quadrature
  + `integrate_trajectory`, Thomas algorithm + natural & clamped cubic
  splines, Monte Carlo (Kahan summation, antithetic variates,
  convergence study). Notebooks 4 (Monte Carlo valuation), 5 (sensitivity
  + break-even μ\* with Monte Carlo CI + profile-likelihood slice),
  6 (cubic-spline funding rounds), 7 (comprehensive comparison +
  driving-question answer). Streamlit dashboard `app.py` with 4
  tabs. **113 tests passing.**
- **Phase 4-5 (remaining):** real-data calibration (hand-curated S-1
  filings for Shopify/Zoom), Streamlit Cloud deployment, presentation
  slides, written report.

## Headline answer

**μ\* ≈ 14.2% per month, 95% CI [8.0%, 16.0%]** — the critical user-churn
rate above which the default-SaaS profile never recovers within a 10-year
horizon. Identifiable despite the calibration valley in (g, μ_R) — the
profile-likelihood slice in Notebook 5 (along the smallest-eigenvalue
eigenvector of the calibration-loss Hessian) shows μ\* varies by ~2.4%
along the valley span — small enough that the answer is meaningfully
robust to the calibration ambiguity. See `notebooks/07_comprehensive_comparison.ipynb`
for the full synthesis.

Numerical methods are implemented from scratch — no `scipy.integrate`,
`scipy.optimize`, or `scipy.interpolate`. NumPy is used for array
operations only.

## Layout

```
engine/                  Pure numerical methods. No UI imports.
  growth_model.py        4D ODE on (Users, Active, Revenue, Cash) + mse_loss.
  ode_solvers.py         Euler, Heun, RK4, AB4, AM-PECE.
  optimizer.py           gradient_descent, adam, numerical_gradient.
  differentiation.py     forward / central / 5-point / Richardson +
                         parameter sensitivity via adaptive h.
  root_finding.py        Newton (with bounds-fallback), bisection, secant,
                         find_brackets.
  integration.py         composite Simpson, Gauss-Legendre 2/3/5-pt,
                         integrate_trajectory.
  interpolation.py       Thomas algorithm, natural & clamped cubic splines.
  monte_carlo.py         Kahan + naive sum, run_simulation, antithetic,
                         convergence_study.
  utils.py               error metrics, convergence-order, linear interp,
                         timer, latex_table.

app.py                   Streamlit dashboard — 4 tabs (trajectory, MC,
                         break-even μ*, sensitivity).

tests/                   pytest. 113 tests. Validation-first: no engine
                         module is imported by a notebook until its tests
                         pass.

notebooks/               7 of 7 shipped.
  01_growth_ode_system.ipynb       4D model + parameter exploration.
  02_ode_solvers_comparison.ipynb  Convergence orders + timing + agreement.
  03_model_calibration.ipynb       Synthetic recovery + the valley.
  04_monte_carlo_valuation.ipynb   P(unicorn) + Kahan + antithetic.
  05_sensitivity_analysis.ipynb    Tornado + U-curve + μ* with MC CI +
                                   profile-likelihood slice.
  06_interpolation_funding_rounds.ipynb  Splines vs ODE comparison.
  07_comprehensive_comparison.ipynb      Synthesis + driving-question answer.

data/                    Datasets and the synthetic generator.
  s1_filings/            Real quarterly revenue (populated in Phase 4-5).
  funding_rounds/        Public funding-round data (populated in Phase 4-5).
  generate_synthetic.py  Replayable synthetic generator with fixed seeds.

slides/                  Lecture PPTXs (gitignored — local copy only).
report/figures/          Notebook-exported figures (25 PNGs, gitignored).
```

## Install and run

```bash
pip install -r requirements.txt
python -m pytest tests/                                # 113 tests, ~25s
python -m data.generate_synthetic                      # writes data/synthetic/*.json
jupyter notebook notebooks/                            # 7 notebooks
streamlit run app.py                                   # interactive dashboard
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
