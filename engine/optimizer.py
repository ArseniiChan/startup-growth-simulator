"""Gradient descent and Adam optimizers, plus the numerical gradient that
both consume.

The optimizers are generic — they take a loss function ``loss(theta) -> float``
and a gradient function ``grad(theta) -> ndarray``. The startup-specific
loss lives in ``engine.growth_model.mse_loss`` and is plumbed in via
``make_loss_fn``. Keeping the optimizer agnostic means the tests can drive
it against textbook problems (quadratics, Rosenbrock) before the calibration
notebook runs.

References
----------
- Burden et al., Chapter 10 (gradient descent on least-squares loss).
- Kingma & Ba, "Adam: A Method for Stochastic Optimization", ICLR 2015.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def numerical_gradient(
    loss_fn: Callable[[np.ndarray], float],
    theta: np.ndarray,
    h: np.ndarray | None = None,
    lower: np.ndarray | None = None,
    upper: np.ndarray | None = None,
) -> np.ndarray:
    """Central-difference gradient of loss_fn w.r.t. each entry of theta.

    If ``h`` is None, an adaptive step is used per coordinate:
        h_i = eps^(1/3) * max(|theta_i|, 1.0)
    This is essential for parameter vectors spanning many decades (g ~ 0.1
    next to K ~ 1e6) — a single fixed h cannot resolve both.

    If ``lower``/``upper`` bounds are given and a coordinate sits within
    h_i of either bound, that coordinate is computed with a one-sided
    forward or backward difference instead of central. This avoids
    evaluating loss_fn at unphysical theta (e.g. negative mu_R when the
    physical lower bound is 0).
    """
    theta = np.asarray(theta, dtype=float)
    n = theta.shape[0]
    if h is None:
        eps = np.finfo(float).eps
        h_vec = (eps ** (1.0 / 3.0)) * np.maximum(np.abs(theta), 1.0)
    else:
        h_vec = np.broadcast_to(np.asarray(h, dtype=float), theta.shape).copy()
    lower = None if lower is None else np.asarray(lower, dtype=float)
    upper = None if upper is None else np.asarray(upper, dtype=float)
    f0 = None
    grad = np.empty(n, dtype=float)
    for i in range(n):
        e = np.zeros(n, dtype=float)
        e[i] = h_vec[i]
        near_lower = lower is not None and theta[i] - h_vec[i] < lower[i]
        near_upper = upper is not None and theta[i] + h_vec[i] > upper[i]
        if near_lower and not near_upper:
            if f0 is None:
                f0 = loss_fn(theta)
            grad[i] = (loss_fn(theta + e) - f0) / h_vec[i]
        elif near_upper and not near_lower:
            if f0 is None:
                f0 = loss_fn(theta)
            grad[i] = (f0 - loss_fn(theta - e)) / h_vec[i]
        else:
            grad[i] = (loss_fn(theta + e) - loss_fn(theta - e)) / (2.0 * h_vec[i])
    return grad


def gradient_descent(
    loss_fn: Callable[[np.ndarray], float],
    grad_fn: Callable[[np.ndarray], np.ndarray],
    theta0: np.ndarray,
    lr: float = 1e-2,
    max_iter: int = 1000,
    tol: float = 1e-8,
    project: Callable[[np.ndarray], np.ndarray] | None = None,
) -> dict:
    """Vanilla gradient descent with optional projection onto a feasible set.

    ``project`` is the parameter-clipping hook used during calibration so
    every step stays inside StartupParams.LOWER/UPPER. If omitted, no
    projection is applied (textbook unconstrained problems).

    Convergence is declared when ||theta_{n+1} - theta_n|| / max(1, ||theta_n||)
    falls below ``tol`` (relative-step criterion — robust across scales).
    """
    theta = np.array(theta0, dtype=float, copy=True)
    if project is not None:
        theta = project(theta)
    history: list[float] = [float(loss_fn(theta))]
    converged = False
    for it in range(1, max_iter + 1):
        g = grad_fn(theta)
        new_theta = theta - lr * g
        if project is not None:
            new_theta = project(new_theta)
        step = np.linalg.norm(new_theta - theta)
        scale = max(1.0, float(np.linalg.norm(theta)))
        theta = new_theta
        history.append(float(loss_fn(theta)))
        if step / scale < tol:
            converged = True
            break
    return {
        "theta": theta,
        "loss_history": np.array(history),
        "iterations": len(history) - 1,
        "converged": converged,
    }


def adam(
    loss_fn: Callable[[np.ndarray], float],
    grad_fn: Callable[[np.ndarray], np.ndarray],
    theta0: np.ndarray,
    lr: float = 1e-3,
    beta1: float = 0.9,
    beta2: float = 0.999,
    eps: float = 1e-8,
    max_iter: int = 1000,
    tol: float = 1e-8,
    project: Callable[[np.ndarray], np.ndarray] | None = None,
) -> dict:
    """Adam (Kingma & Ba, 2015).

    m_t = beta1 m_{t-1} + (1 - beta1) g_t
    v_t = beta2 v_{t-1} + (1 - beta2) g_t^2
    m_hat = m_t / (1 - beta1^t)
    v_hat = v_t / (1 - beta2^t)
    theta_t = theta_{t-1} - lr * m_hat / (sqrt(v_hat) + eps)

    The ``project`` hook (clip-to-bounds) and the relative-step convergence
    criterion match gradient_descent so the two routines are drop-in
    interchangeable for the calibration notebook.
    """
    theta = np.array(theta0, dtype=float, copy=True)
    if project is not None:
        theta = project(theta)
    n = theta.shape[0]
    m = np.zeros(n, dtype=float)
    v = np.zeros(n, dtype=float)
    history: list[float] = [float(loss_fn(theta))]
    converged = False
    for t in range(1, max_iter + 1):
        g = grad_fn(theta)
        m = beta1 * m + (1.0 - beta1) * g
        v = beta2 * v + (1.0 - beta2) * (g * g)
        m_hat = m / (1.0 - beta1**t)
        v_hat = v / (1.0 - beta2**t)
        new_theta = theta - lr * m_hat / (np.sqrt(v_hat) + eps)
        if project is not None:
            new_theta = project(new_theta)
        step = np.linalg.norm(new_theta - theta)
        scale = max(1.0, float(np.linalg.norm(theta)))
        theta = new_theta
        history.append(float(loss_fn(theta)))
        if step / scale < tol:
            converged = True
            break
    return {
        "theta": theta,
        "loss_history": np.array(history),
        "iterations": len(history) - 1,
        "converged": converged,
    }
