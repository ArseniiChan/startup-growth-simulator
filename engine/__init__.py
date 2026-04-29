"""Pure numerical methods engine. No UI dependencies.

Public API
----------
ODE solvers (uniform interface, all share the linspace rule):
    euler, heun, rk4, adams_bashforth4, adams_moulton_pc

Startup model:
    StartupParams, default_params, preset_profiles, growth_system,
    mse_loss, make_loss_fn, params_to_array, array_to_params, clip_params,
    PARAM_NAMES

Optimizers:
    gradient_descent, adam, numerical_gradient

Numerical differentiation:
    forward_diff, central_diff, five_point, second_derivative,
    richardson, optimal_h_study, sensitivity_analysis

Root finding:
    newton, bisection, secant, find_brackets

Integration:
    composite_simpson, gaussian_quadrature, integrate_trajectory

Interpolation:
    thomas_solve, cubic_spline_natural, cubic_spline_clamped

Monte Carlo:
    kahan_sum, naive_sum, run_simulation, convergence_study

Utilities:
    absolute_error, relative_error, convergence_order,
    linear_interpolate, timer, latex_table
"""

from engine.differentiation import (
    central_diff,
    five_point,
    forward_diff,
    optimal_h_study,
    richardson,
    second_derivative,
    sensitivity_analysis,
)
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
from engine.ode_solvers import (
    adams_bashforth4,
    adams_moulton_pc,
    euler,
    heun,
    rk4,
)
from engine.integration import (
    composite_simpson,
    gaussian_quadrature,
    integrate_trajectory,
)
from engine.interpolation import (
    cubic_spline_clamped,
    cubic_spline_natural,
    thomas_solve,
)
from engine.monte_carlo import (
    convergence_study,
    kahan_sum,
    naive_sum,
    run_simulation,
)
from engine.optimizer import adam, gradient_descent, numerical_gradient
from engine.root_finding import bisection, find_brackets, newton, secant
from engine.utils import (
    absolute_error,
    convergence_order,
    latex_table,
    linear_interpolate,
    relative_error,
    timer,
)

__all__ = [
    # ode_solvers
    "euler", "heun", "rk4", "adams_bashforth4", "adams_moulton_pc",
    # growth_model
    "StartupParams", "default_params", "preset_profiles", "growth_system",
    "mse_loss", "make_loss_fn", "params_to_array", "array_to_params",
    "clip_params", "PARAM_NAMES",
    # optimizer
    "gradient_descent", "adam", "numerical_gradient",
    # differentiation
    "forward_diff", "central_diff", "five_point", "second_derivative",
    "richardson", "optimal_h_study", "sensitivity_analysis",
    # root_finding
    "newton", "bisection", "secant", "find_brackets",
    # integration
    "composite_simpson", "gaussian_quadrature", "integrate_trajectory",
    # interpolation
    "thomas_solve", "cubic_spline_natural", "cubic_spline_clamped",
    # monte_carlo
    "kahan_sum", "naive_sum", "run_simulation", "convergence_study",
    # utils
    "absolute_error", "relative_error", "convergence_order",
    "linear_interpolate", "timer", "latex_table",
]
