# Implementation Plan: Startup Growth Dynamics & Valuation
## Full Technical Specification

---

## 1. Tech Stack

| Layer | Technology | Version | Why |
|---|---|---|---|
| Language | Python | 3.11+ | Course standard, NumPy/SciPy ecosystem |
| Notebooks | Jupyter | 7.x | Required for submission |
| Numerics | NumPy | 1.26+ | Array ops only (no solvers — we build those) |
| Plotting | Matplotlib | 3.8+ | Static plots for notebooks and report |
| Interactive plots | Plotly | 5.18+ | 3D surface rotation, hover tooltips in dashboard |
| Dashboard | Streamlit | 1.30+ | Free hosting, fast prototyping, sliders/inputs |
| Market data | yfinance | 0.2.31+ | Optional: quarterly revenue for public companies |
| Testing | pytest | 8.x | Unit tests for engine modules |
| Formatting | black + isort | latest | Code style consistency |

### What we DON'T use (and why)
- **No `scipy.integrate`** — we implement Euler, Heun, RK4, AB4 ourselves. That's the point.
- **No `scipy.optimize`** — we implement gradient descent and Adam ourselves.
- **No `scipy.interpolate`** — we implement cubic splines ourselves.
- **No pandas** — overkill for this project. Plain NumPy arrays + JSON files.
- **NumPy is allowed** for array operations, random number generation, and linear algebra (np.linalg.solve for tridiagonal). The numerical METHODS are ours. NumPy is just the calculator.

---

## 2. Repo Structure (Final)

```
CSC301-Startup-Growth/
│
├── engine/                          ← Pure numerical methods (NO dependencies on UI)
│   ├── __init__.py
│   ├── growth_model.py              ← ODE system definition + parameter dataclass
│   ├── ode_solvers.py               ← Euler, Heun, RK4, AB4, AM predictor-corrector
│   ├── optimizer.py                 ← Gradient descent, Adam optimizer
│   ├── monte_carlo.py               ← MC simulation, Kahan summation, antithetic variates
│   ├── root_finding.py              ← Newton, bisection, secant
│   ├── differentiation.py           ← Forward, central, 5-point, Richardson extrapolation
│   ├── interpolation.py             ← Cubic spline (natural + clamped), Thomas algorithm
│   ├── integration.py               ← Composite Simpson's, Gaussian quadrature
│   └── utils.py                     ← Error metrics, timing decorator, convergence helpers
│
├── tests/                           ← pytest unit tests
│   ├── test_growth_model.py
│   ├── test_ode_solvers.py
│   ├── test_optimizer.py
│   ├── test_monte_carlo.py
│   ├── test_root_finding.py
│   ├── test_differentiation.py
│   ├── test_interpolation.py
│   └── test_integration.py
│
├── notebooks/                       ← Analysis + visualizations (submitted)
│   ├── 01_growth_ode_system.ipynb
│   ├── 02_ode_solvers_comparison.ipynb
│   ├── 03_model_calibration.ipynb
│   ├── 04_monte_carlo_valuation.ipynb
│   ├── 05_sensitivity_analysis.ipynb
│   ├── 06_interpolation_funding_rounds.ipynb
│   └── 07_comprehensive_comparison.ipynb
│
├── data/
│   ├── s1_filings/                  ← Real quarterly revenue from SEC S-1 filings
│   │   ├── shopify.json             ← { "company": "Shopify", "quarters": [...], "revenue_millions": [...] }
│   │   ├── zoom.json
│   │   ├── datadog.json
│   │   └── snowflake.json
│   ├── funding_rounds/              ← Public funding data (Wikipedia, TechCrunch)
│   │   ├── stripe.json              ← { "company": "Stripe", "rounds": [{"date": "2011-06", "series": "Seed", "valuation_millions": 20}, ...] }
│   │   └── airbnb.json
│   └── generate_synthetic.py        ← Script to create synthetic startup data with noise
│
├── app.py                           ← Streamlit dashboard (single file)
├── requirements.txt
├── README.md
├── .gitignore
└── report/                          ← Final deliverables
    ├── figures/                     ← Exported plots from notebooks
    ├── report.pdf
    └── presentation.pptx
```

---

## 3. Engine Module Specifications

### 3.1 `growth_model.py`

```python
@dataclass
class StartupParams:
    g: float       # growth rate (e.g., 0.15 = 15% per month)
    K: float       # carrying capacity / market size (e.g., 1_000_000)
    alpha: float   # conversion rate: signups → paying (e.g., 0.05)
    mu: float      # user churn rate (e.g., 0.03 = 3% monthly)
    p: float       # ARPU - average revenue per user (e.g., 50.0)
    mu_R: float    # revenue decay rate: cancellations + downgrades combined (e.g., 0.04)
    F: float       # fixed monthly costs (e.g., 50_000)
    v: float       # variable cost per new user acquired (e.g., 10.0)

    # Parameter bounds for optimizer (class-level constants)
    LOWER = np.array([0.001, 10_000, 0.001, 0.0, 1.0, 0.0, 1_000, 0.0])
    UPPER = np.array([1.0, 1_000_000_000, 0.8, 0.5, 1000.0, 0.5, 10_000_000, 500.0])

def growth_system(t: float, y: np.ndarray, params: StartupParams) -> np.ndarray:
    """
    The 4D ODE system in standard form.
    y = [U, A, R, Cash]

    dU/dt    = g * U * (1 - U/K)
    dA/dt    = alpha * g * U * (1 - U/K) - mu * A
    dR/dt    = p * alpha * g * U * (1 - U/K) - mu_R * R
    dCash/dt = R - F - v * g * U * (1 - U/K)

    Returns dy/dt as a 4-element array.
    """

def default_params() -> StartupParams:
    """Reasonable defaults for an early-stage SaaS startup."""

def preset_profiles() -> dict[str, StartupParams]:
    """Pre-configured profiles: 'saas', 'marketplace', 'enterprise', 'viral'."""

def params_to_array(params: StartupParams, fit_indices: list[int] = None) -> np.ndarray:
    """Convert StartupParams to flat array. If fit_indices given, return only those."""

def array_to_params(theta: np.ndarray, base_params: StartupParams, fit_indices: list[int] = None) -> StartupParams:
    """Unpack flat array back to StartupParams. Unfitted params come from base_params."""

def clip_params(theta: np.ndarray) -> np.ndarray:
    """Clip parameter array to physical bounds. Called after every optimizer step."""
```

**Key design decisions:**
- The `growth_system` function signature matches what all ODE solvers expect: `f(t, y, *args) -> dy/dt`. This means every solver works with any ODE system, not just ours.
- Revenue equation uses `p * alpha * dU/dt - mu_R * R` (NOT `p * dA/dt`) to avoid double-counting churn.
- Cash(t) is cash balance (starts at initial funding), not cumulative burn. dCash/dt can be positive or negative.
- `params_to_array` / `array_to_params` handle the optimizer interface. `fit_indices` lets us fit only a subset of parameters (e.g., [0,1,3] for g, K, mu) while holding the rest fixed.
- `clip_params` enforces physical bounds after every optimizer step (prevents g<0, K<0, alpha>1, etc.).

### 3.2 `ode_solvers.py`

```python
def euler(f, y0, t_span, h, *args) -> (np.ndarray, np.ndarray):
    """Forward Euler. Returns (t_array, y_array). O(h)."""

def heun(f, y0, t_span, h, *args) -> (np.ndarray, np.ndarray):
    """Heun's method (improved Euler / RK2). O(h²)."""

def rk4(f, y0, t_span, h, *args) -> (np.ndarray, np.ndarray):
    """Classical 4th-order Runge-Kutta. O(h⁴)."""

def adams_bashforth4(f, y0, t_span, h, *args) -> (np.ndarray, np.ndarray):
    """4-step Adams-Bashforth (explicit). Bootstraps with RK4. O(h⁴)."""

def adams_moulton_pc(f, y0, t_span, h, *args) -> (np.ndarray, np.ndarray):
    """Adams-Bashforth-Moulton predictor-corrector. O(h⁴)."""
```

**Uniform interface:** Every solver takes the same arguments and returns the same shape. This makes the comparison notebook and dashboard trivial — just swap the function.

**Time grid rule (all solvers must follow this):**
```python
n_steps = math.ceil((t_span[1] - t_span[0]) / h)
t = np.linspace(t_span[0], t_span[1], n_steps + 1)
h_actual = (t_span[1] - t_span[0]) / n_steps
```
All solvers return: `t` shape `(n_steps+1,)`, `y` shape `(n_steps+1, state_dim)`.
This ensures all solvers hit the exact same final time regardless of h.

**Exact AB4 formula:**
```
y_{n+1} = y_n + (h/24) * (55*f_n - 59*f_{n-1} + 37*f_{n-2} - 9*f_{n-3})
```
Bootstrap first 4 steps with RK4.

**Exact AB4-AM4 predictor-corrector:**
```
Predict:  y^p_{n+1} = y_n + (h/24) * (55*f_n - 59*f_{n-1} + 37*f_{n-2} - 9*f_{n-3})
Correct:  y_{n+1}   = y_n + (h/24) * (9*f(t_{n+1}, y^p_{n+1}) + 19*f_n - 5*f_{n-1} + f_{n-2})
```
This is PECE (predict-evaluate-correct-evaluate), not fully implicit.

**All convergence orders refer to global error:** Euler O(h), Heun O(h²), RK4 O(h⁴), AB4 O(h⁴). Local truncation errors are one order higher.

**Testing strategy:**
- Test against exponential growth dy/dt = ky (known solution y = y₀eᵏᵗ)
- Test against decay dy/dt = -2y, y(0)=3 (known solution y = 3e^{-2t})
- Test against logistic equation (known closed-form solution)
- Verify convergence orders numerically over h = [0.4, 0.2, 0.1, 0.05, 0.025]:
  ```python
  slope = convergence_order(errors, h_values)
  assert abs(slope - expected_order) < 0.3
  ```
- Verify Euler instability with large h

### 3.3 `optimizer.py`

```python
def gradient_descent(loss_fn, grad_fn, theta0, lr=0.01, max_iter=1000, tol=1e-8) -> dict:
    """
    Vanilla gradient descent.
    Returns {'theta': final_params, 'loss_history': [...], 'iterations': n}
    """

def adam(loss_fn, grad_fn, theta0, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8, max_iter=1000, tol=1e-8) -> dict:
    """
    Adam optimizer (Kingma & Ba 2015).
    Returns {'theta': final_params, 'loss_history': [...], 'iterations': n}
    """

def numerical_gradient(loss_fn, theta, h=None) -> np.ndarray:
    """
    Central difference gradient of loss_fn w.r.t. each element of theta.
    If h is None, use adaptive step: h_i = eps^(1/3) * max(|theta_i|, 1.0)
    This handles parameters at wildly different scales (g=0.15 vs K=1,000,000).
    """
```

**`mse_loss` lives in `growth_model.py`, NOT here.** The optimizer is generic — it takes any loss function and gradient function. The startup-specific loss is defined in `growth_model.py`:

```python
# In growth_model.py:
def mse_loss(theta, observed_t, observed_R, base_params, fit_indices, solver, y0, t_span, h=1.0) -> float:
    """
    MSE between model prediction and observed revenue.
    1. Unpack theta into StartupParams (unfitted params from base_params)
    2. Clip to bounds
    3. Solve ODE
    4. Interpolate model R(t) to observed_t (linear interpolation from utils.py)
    5. Return MSE
    """

def make_loss_fn(observed_t, observed_R, base_params, fit_indices, solver, y0, t_span):
    """Returns a closure loss(theta) -> float for the optimizer. Keeps optimizer.py generic."""
```

**Calibration scope:** Fit only 2-3 parameters (g, K, mu_R) while holding alpha, p, F, v fixed at domain-reasonable values. Fitting all 7 from one revenue curve is underdetermined.

**Testing strategy:**
- Minimize known quadratic f(x,y) = (x-2)² + 10(y+1)² → should converge to (2, -1)
- Minimize Rosenbrock f(x,y) = (1-x)² + 100(y-x²)² → verify Adam converges faster than GD (optional stretch)
- Synthetic recovery test: generate revenue data with known (g, K, mu_R), add noise, verify optimizer recovers them within 10% tolerance. Only fit 3 params, not all 7.

### 3.4 `monte_carlo.py`

```python
def kahan_sum(values: np.ndarray) -> float:
    """Compensated summation. Returns sum with reduced floating-point error."""

def naive_sum(values: np.ndarray) -> float:
    """Simple loop summation for comparison."""

def run_simulation(params: StartupParams, uncertainty: dict, N: int,
                   T: float = 60, solver=rk4, antithetic=False) -> dict:
    """
    Monte Carlo simulation.
    
    uncertainty = {'g': 0.03, 'mu': 0.01, 'K': 0.2} — std dev for each param
    
    Returns {
        'valuations': np.ndarray of terminal valuations,
        'p_unicorn': float,
        'expected_value': float (Kahan sum),
        'expected_value_naive': float (naive sum),
        'var_5': float (5th percentile),
        'std_error': float,
        'computation_time': float
    }
    """

def convergence_study(params, uncertainty, N_values=[100, 1000, 10000, 50000],
                      M_batches=20, **kwargs) -> dict:
    """
    Run M independent estimates at each N. Returns data for convergence plot.
    Using repeated batches gives a cleaner -1/2 slope than a single run per N.
    """
```

**Testing strategy:**
- Kahan vs naive: sum [1e8] + [1e-8]*1_000_000 (exact sum = 100000000.01). Kahan should be closer.
- Convergence: verify std error (across M=20 batches) decreases as 1/√N (slope -0.5 on log-log)
- Antithetic: verify variance is lower than standard MC with same N. Do NOT assume this — measure it. If monotonicity breaks, report honestly.

### 3.5 `root_finding.py`

```python
def newton(f, df, x0, tol=1e-10, max_iter=100, bounds=None) -> dict:
    """
    Newton's method with safeguards.
    - If |df(x)| < 1e-14, stop and report 'converged': False
    - If bounds given and Newton jumps outside, fall back to bisection step
    Returns {'root': x, 'iterations': n, 'history': [...], 'converged': bool}
    """

def bisection(f, a, b, tol=1e-10, max_iter=100) -> dict:
    """Bisection method. Raises ValueError if f(a)*f(b) > 0 (no sign change)."""

def secant(f, x0, x1, tol=1e-10, max_iter=100) -> dict:
    """Secant method. Returns same format as newton."""

def find_brackets(f, t_grid: np.ndarray) -> list[tuple[float, float]]:
    """
    Scan a grid for sign changes. Returns list of (a, b) intervals where f(a)*f(b) < 0.
    Use this BEFORE calling bisection/Newton on the break-even or runway problem.
    Returns empty list if no root exists within the grid.
    """
```

**Testing strategy:**
- All three find root of f(x) = x² - 4 → should get x = 2.0
- Newton on sin(x) near x₀ = 3 → should converge to π
- Verify iteration counts: Newton < secant < bisection for well-behaved functions
- Verify convergence orders from history arrays
- **Failure cases:** f(x) = x² + 1 → bisection should raise ValueError (no real root)
- **Near-zero derivative:** f(x) = x³ near x₀ = 0 → Newton should not divide by zero
- **find_brackets:** verify it returns [] for functions with no root, and correct intervals for functions with multiple roots

### 3.6 `differentiation.py`

```python
def forward_diff(f, x, h=1e-5) -> float:
    """Forward difference: [f(x+h) - f(x)] / h. O(h)."""

def central_diff(f, x, h=1e-5) -> float:
    """Central difference: [f(x+h) - f(x-h)] / 2h. O(h²)."""

def five_point(f, x, h=1e-5) -> float:
    """5-point midpoint formula: [-f(x+2h) + 8f(x+h) - 8f(x-h) + f(x-2h)] / (12h). O(h⁴)."""

def second_derivative(f, x, h=1e-5) -> float:
    """Central second derivative: [f(x+h) - 2f(x) + f(x-h)] / h². O(h²)."""

def richardson(f, x, h=1e-3, method='central', p=None) -> float:
    """
    Richardson extrapolation: D_rich = D(h/2) + [D(h/2) - D(h)] / (2^p - 1)
    p = order of the base method: p=1 for forward, p=2 for central, p=4 for five-point.
    If p is None, infer from method name.
    """

def optimal_h_study(f, x, f_exact, h_range=np.logspace(-15, 0, 100)) -> dict:
    """Compute error vs h for all methods. Returns data for the U-curve plot."""

def sensitivity_analysis(params: StartupParams, param_name: str, solver=rk4, T=60) -> dict:
    """
    Compute ∂V/∂param using all differentiation methods.
    Uses ADAPTIVE step size per parameter: h_i = eps^(1/3) * max(|param_value|, 1.0)
    Do NOT use fixed h=1e-5 for all params — g=0.15 and K=1,000,000 need different h.
    Returns derivatives and errors for the tornado chart.
    """
```

**Testing strategy:**
- Differentiate f(x) = sin(x) at x = 1 → compare to cos(1)
- Differentiate f(x) = x⁵ at x = 2 → compare to 5*2⁴ = 80 (polynomial exactness)
- Verify convergence orders over a range of h: forward O(h), central O(h²), 5-point O(h⁴)
- Verify U-curve shape (error decreases then increases)

### 3.7 `interpolation.py`

```python
def thomas_solve(a, b, c, d) -> np.ndarray:
    """Thomas algorithm for tridiagonal system. O(n)."""

def cubic_spline_natural(x, y) -> dict:
    """
    Natural cubic spline (S''=0 at endpoints).
    Returns {
        'x': x, 'a': a, 'b': b, 'c': c, 'd': d,  # coefficients per interval
        'eval': callable,                            # S(t) -> float
        'derivative': callable,                      # S'(t) -> float
        'second_derivative': callable                # S''(t) -> float
    }
    Returning coefficients (not just a callable) makes C² continuity testing easy.
    """

def cubic_spline_clamped(x, y, d0, dn) -> dict:
    """Clamped cubic spline (S'=d0 at left, S'=dn at right). Same return format as natural."""
```

**Note:** Thomas algorithm is the whole point of SP 21. Do NOT use `np.linalg.solve` inside the spline builder. Use `np.linalg.solve` only in the test as a reference answer.

**Testing strategy:**
- Thomas algorithm: solve a known tridiagonal system, verify against np.linalg.solve
- Spline through sin(x) at 10 points: error should be small everywhere
- **Cubic polynomial exactness:** spline through f(x) = x³ - 2x² + x - 1 with correct clamped derivatives should reproduce the polynomial exactly (within machine precision)
- Verify C² continuity: check S, S', S'' are continuous at interior knots using the returned derivative callables

### 3.8 `integration.py`

```python
def composite_simpson(f, a, b, n) -> float:
    """Composite Simpson's 1/3 rule. n must be even — raises ValueError if odd. O(h⁴)."""

def gaussian_quadrature(f, a, b, n_points=5) -> float:
    """
    Gaussian quadrature with hardcoded Legendre nodes/weights for n_points = 2, 3, 5.
    Exact for poly degree ≤ 2n-1. Do NOT compute nodes from scratch — use lookup tables.
    Raises ValueError for unsupported n_points.
    """

def integrate_trajectory(t_array, y_array) -> float:
    """
    Simpson's rule on discrete ODE output. For total revenue, total burn, LTV.
    Asserts uniform spacing: np.allclose(np.diff(t_array), t_array[1] - t_array[0]).
    Asserts even number of subintervals (len(t_array) - 1 must be even).
    """
```

**Testing strategy:**
- Integrate x² from 0 to 1 → should get 1/3 exactly (Simpson's is exact for cubics)
- Integrate sin(x) from 0 to π → should get 2.0
- Convergence: verify error shrinks as O(h⁴) for Simpson's
- **Gauss-Legendre exactness:** 3-point should integrate degree-5 polynomial exactly
- **Simpson odd-n:** verify ValueError is raised when n is odd
- **integrate_trajectory:** verify assertion fires on non-uniform t_array

### 3.9 `utils.py`

```python
def absolute_error(computed, exact) -> float:
def relative_error(computed, exact) -> float:
def convergence_order(errors, h_values) -> float:
    """Estimate convergence order from log-log slope."""

def linear_interpolate(x_grid, y_grid, x_query) -> np.ndarray:
    """
    Simple linear interpolation of y_grid at x_query points.
    Used in calibration: ODE solver output is at fine grid, observed data is quarterly.
    """

@contextmanager
def timer():
    """Context manager for timing code blocks."""

def latex_table(data: dict, headers: list) -> str:
    """Generate a LaTeX-formatted table for the report."""
```

---

## 4. Data Files Specification

### S-1 Filing Data Format (`data/s1_filings/shopify.json`)
```json
{
    "company": "Shopify",
    "ticker": "SHOP",
    "ipo_date": "2015-05-21",
    "source": "SEC S-1 Filing, Amendment No. 4",
    "metric": "quarterly_revenue_millions_usd",
    "data": [
        {"quarter": "2012-Q1", "revenue": 8.7},
        {"quarter": "2012-Q2", "revenue": 10.1},
        ...
    ]
}
```

### Funding Round Data Format (`data/funding_rounds/stripe.json`)
```json
{
    "company": "Stripe",
    "source": "Wikipedia, TechCrunch",
    "rounds": [
        {"date": "2011-06", "series": "Seed", "amount_millions": 2, "valuation_millions": 20},
        {"date": "2012-02", "series": "A", "amount_millions": 18, "valuation_millions": 100},
        {"date": "2014-01", "series": "B", "amount_millions": 80, "valuation_millions": 1750},
        ...
    ]
}
```

---

## 5. Notebook Specifications

### The Driving Question

Every notebook is in service of one central question:

> **"At what churn rate does a startup's growth become mathematically irreversible — and how confident can we be in that answer?"**

**Precise definition:** μ* is the smallest user churn rate such that the startup never reaches break-even (dCash/dt > 0) within the time horizon T. Formally:

```
μ* = min { μ : max_{t in [0,T]} dCash/dt(t; μ) < 0 }
```

This is a clean bisection problem on μ: for each candidate μ, solve the ODE, check if dCash/dt ever reaches zero. The outer bisection finds the critical threshold.

This ties the numerical methods to a real VC decision. It's not "I implemented 16 methods." It's "I can tell you the exact churn threshold where no amount of growth saves this startup, and here's the probability distribution around that answer."

### Model Validity Caveat (must appear in Notebook 1 and the report)

The ODE model treats startup growth as smooth and continuous. Real startup growth is noisy, discrete (quarterly data), and subject to structural breaks (pivots, funding rounds, leadership changes). The model is a useful approximation for understanding dynamics and sensitivity — not a prediction engine. The report must explicitly state: "This model captures growth dynamics under steady-state assumptions. It does not account for discrete shocks, pivots, or market regime changes."

### Validation-First Rule

**No engine module is used in a notebook until its tests pass.** The order is always:
1. Implement the module
2. Write and pass tests against known analytical solutions
3. Only then import it in a notebook

### Notebook Structure
1. **Header:** Title, purpose, which lectures/methods are used
2. **Theory:** Brief math explanation (written for the reader, not copy-paste)
3. **Implementation:** Import from engine/, run the method
4. **Visualization:** Matplotlib plots with proper labels, titles, legends
5. **Analysis:** Interpret results, discuss errors, compare methods
6. **Report paragraph:** Write 1-2 paragraphs of report prose while the analysis is fresh (these get compiled into the final report in Week 5)
7. **Export:** Save key figures to `report/figures/` for the written report

### How Each Notebook Connects to the Driving Question

| Notebook | Methods | Connection to "At what churn rate does growth become irreversible?" |
|---|---|---|
| 1 — Growth ODE System | ODE formulation, Euler/RK4 | Shows how churn (μ) changes the shape of growth curves. Visual intuition for the threshold. |
| 2 — Solver Comparison | Euler, Heun, RK4, AB4, AM | Establishes that our numerical answers are trustworthy (convergence verification). Without this, the churn threshold number means nothing. |
| 3 — Model Calibration | Adam optimizer, least squares | Grounds the model in real data. Shows what μ looks like for companies that made it (Shopify) vs. struggled. |
| 4 — Monte Carlo | MC simulation, Kahan, antithetic | Answers "how confident?" — gives a probability distribution around the threshold, not just a point estimate. |
| 5 — Sensitivity | Numerical differentiation, Newton's method | Finds the exact threshold (root of dCash/dt = 0 for break-even, Cash(t)=0 for runway death) and shows which parameter dominates the tornado chart. |
| 6 — Interpolation | Cubic splines, Thomas algorithm | Shows how sparse real-world data (funding rounds) can be interpolated to compare against the continuous model. [CUTTABLE] |
| 7 — Comprehensive | All methods | The "so what" notebook: assembles the final answer with confidence intervals. |

### Dependency Order
```
Notebook 1 (growth system)     → needs: growth_model.py, ode_solvers.py
Notebook 2 (solver comparison) → needs: ode_solvers.py, utils.py
Notebook 3 (calibration)       → needs: optimizer.py, differentiation.py, data/s1_filings/
Notebook 4 (Monte Carlo)       → needs: monte_carlo.py
Notebook 5 (sensitivity)       → needs: differentiation.py, root_finding.py
Notebook 6 (interpolation)     → needs: interpolation.py, data/funding_rounds/
Notebook 7 (comparison)        → needs: everything above
```

---

## 6. Dashboard Specification (`app.py`)

### Layout
```
┌──────────────────────────────────────────────────┐
│  SIDEBAR                                          │
│  ┌──────────────────┐                             │
│  │ Startup Profile   │  ← dropdown                │
│  │ [Early SaaS ▼]   │                             │
│  ├──────────────────┤                             │
│  │ Growth rate: 0.15 │  ← slider                  │
│  │ Churn rate:  0.03 │  ← slider                  │
│  │ Market size: 1M   │  ← number input            │
│  │ ARPU:        $50  │  ← slider                  │
│  │ Fixed costs: $50K │  ← slider                  │
│  │ ...              │                             │
│  └──────────────────┘                             │
│                                                    │
│  MAIN AREA (tabs)                                  │
│  ┌─────┬──────┬──────┬────────┬──────────┐       │
│  │Growth│Monte │Sensi-│Break-  │Funding   │       │
│  │Curve │Carlo │tivity│Even    │Rounds    │       │
│  └─────┴──────┴──────┴────────┴──────────┘       │
│                                                    │
│  [Active tab content with plots]                   │
└──────────────────────────────────────────────────┘
```

### Panel Details

**Tab 1 — Growth Trajectory**
- Solver picker: Euler / Heun / RK4 / AB4
- 4 subplots: U(t), A(t), R(t), Cash(t)
- Metrics sidebar: peak users, peak MRR, total burn
- Caching: `@st.cache_data` on ODE solve for responsiveness

**Tab 2 — Monte Carlo**
- N slider: 100 → 10,000 (log scale)
- Run button (not auto-run — too expensive)
- Plotly histogram of valuations
- KPI cards: P(unicorn), E[V], VaR(5%), std error
- Toggle: antithetic variates on/off

**Tab 3 — Sensitivity**
- Tornado chart (horizontal bar): ∂V/∂param for each parameter
- Click a parameter → line plot of V vs. that parameter
- U-curve plot showing optimal h

**Tab 4 — Break-Even & Runway**
- Cash balance curve with break-even point (dCash/dt=0) and runway death (Cash=0) marked
- Newton iteration table: step, t_n, f(t_n), |correction|
- Comparison: Newton vs. bisection vs. secant iteration counts
- "No break-even within T months" message if no root exists

**Tab 5 — Funding Rounds** (maps to cuttable Notebook 6)
- Input table: date + valuation for each round
- Cubic spline curve through points
- Overlay ODE model prediction
- 3D Plotly surface: growth rate × time → valuation

### Performance
- ODE solves are fast (< 100ms). No caching needed for Tabs 1, 4.
- Monte Carlo is slow for large N. Use `@st.cache_data` keyed on all params + N. Show spinner.
- Sensitivity requires ~20 ODE solves per parameter (sweep). Cache aggressively.
- 3D surface requires a grid of solves. Pre-compute on button click, not on slider change.

---

## 7. Detailed Task Breakdown

### Phase 1: Foundation
```
1.1  Create GitHub repo, .gitignore, requirements.txt, README stub
1.2  Create engine/ directory with __init__.py
1.3  Implement growth_model.py (StartupParams dataclass, growth_system function, presets)
1.4  Implement ode_solvers.py (euler, heun, rk4)
1.5  Write tests for growth_model and ode_solvers (exponential, logistic, convergence)
1.6  *** GATE: all tests in 1.5 pass before proceeding ***
1.7  Implement generate_synthetic.py
1.8  Build Notebook 1 (growth ODE system — plots, parameter exploration)
```

### Phase 2: Core Methods
```
2.1  Implement ode_solvers.py continued (adams_bashforth4, adams_moulton_pc)
2.2  Implement differentiation.py (all methods + Richardson + optimal_h_study)
2.3  Implement root_finding.py (newton, bisection, secant)
2.4  Implement optimizer.py (gradient_descent, adam, numerical_gradient, mse_loss)
2.5  Write tests for ALL of 2.1-2.4 (differentiation, root_finding, optimizer, AB4/AM)
2.6  *** GATE: all tests in 2.5 pass before proceeding ***
2.7  Hand-curate S-1 filing data (Shopify, Zoom, Datadog, Snowflake)
2.8  Build Notebook 2 (solver comparison + convergence plots)
2.9  Build Notebook 3 (calibration — synthetic recovery first, then real S-1 data)
2.10 Start app.py — sidebar + Tab 1 (growth trajectory)
```

### Phase 3: Monte Carlo + Remaining Methods
```
3.1  Implement monte_carlo.py (kahan_sum, run_simulation, convergence_study)
3.2  Implement interpolation.py (thomas_solve, cubic_spline_natural, cubic_spline_clamped)
3.3  Implement integration.py (composite_simpson, gaussian_quadrature, integrate_trajectory)
3.4  Write tests for monte_carlo, interpolation, integration
3.5  *** GATE: all tests in 3.4 pass before proceeding ***
3.6  Hand-curate funding round data (Stripe, Airbnb)
3.7  Build Notebook 4 (Monte Carlo — histogram, convergence, Kahan, antithetic)
3.8  Build Notebook 5 (sensitivity — tornado, U-curve, break-even)
3.9  Build Notebook 6 (interpolation — splines, 3D surface) [CUTTABLE]
3.10 Build Notebook 7 (comprehensive comparison — master table, hero plot)
3.11 Complete app.py — Tabs 2-5
3.12 Deploy to Streamlit Community Cloud
3.13 Test deployment, verify all panels work
```

### Phase 4: Presentation
```
4.1  Build presentation slides (12 slides)
4.2  Export key figures from notebooks to report/figures/
4.3  Generate QR code for Streamlit URL
4.4  Embed dashboard screenshots as fallback slides
4.5  Practice presentation (time it, refine live demo script)
4.6  Present in class
```

### Phase 5: Report + Polish
```
5.1  Write report (12-15 pages double-spaced)
5.2  Insert figures from report/figures/
5.3  Write README.md for GitHub (overview, screenshots, how to run)
5.4  Add docstrings to all engine modules
5.5  Final cleanup: remove debug code, ensure all notebooks run clean
5.6  Submit report + charts
```

---

## 8. Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Adam optimizer doesn't converge on real S-1 data | Medium | Medium | Tune learning rate, try multiple initial guesses, fall back to synthetic data for that notebook |
| Streamlit Cloud is slow for Monte Carlo | Low | High | Cap N at 10,000 in dashboard. Full 50,000 runs stay in notebook only. |
| S-1 filing data is hard to extract | Low | Medium | Only need 4 companies × ~20 quarters. Worst case, use 2 companies. |
| Notebook 6 takes too long | Low | Medium | It's explicitly cuttable. Drop it, project is still strong. |
| Professor wants different ODE system | Medium | Low | Our engine is generic — growth_system is just one function. Can swap in a different model. |
| Convergence plots don't show clean slopes | Medium | Low | Test on known problems first. If the startup ODE is messy, show convergence on a clean test problem alongside. |
| Calibrated params diverge from real S-1 data | Medium | Medium | Real companies have discrete shocks (pivots, funding rounds) our smooth ODE can't capture. Show the fit honestly, quantify the residual, and explain why the gap exists. A bad fit is a valid result if you explain it. |
| Narrative falls flat ("I implemented 16 methods") | Medium | Low | Every notebook ties back to the driving question: "At what churn rate does growth become irreversible?" If a method doesn't connect to that question, cut it or reframe it. |

---

## 9. Dependencies (What Must Come Before What)

```
growth_model.py ──→ ode_solvers.py ──→ optimizer.py ──→ monte_carlo.py
                          │                   │
                          │                   ├──→ differentiation.py
                          │                   │
                          ▼                   ▼
                    root_finding.py    integration.py
                          
interpolation.py (independent — only needs numpy)

Notebook 1 → Notebook 2 → Notebook 3 → Notebook 4 → Notebook 7
                                    ↘                ↗
                              Notebook 5 ──────────
                              Notebook 6 ──────────
```

---

## 10. Definition of Done

The project is complete when:
- [ ] All 8 engine modules pass their tests (validation-first: no module used in a notebook until tests pass)
- [ ] All 7 notebooks run top-to-bottom without errors
- [ ] Every notebook explicitly connects its results to the driving question
- [ ] Model validity caveat appears in Notebook 1 and the report
- [ ] Dashboard deploys to Streamlit Cloud and all 5 tabs work
- [ ] Presentation delivered in class with live demo
- [ ] QR code works and audience can access dashboard
- [ ] Report is 12-15 pages, double-spaced, with all required figures
- [ ] Report answers the driving question with a clear number and confidence interval
- [ ] GitHub repo has clean README, docstrings, and .gitignore
