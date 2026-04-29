"""Error metrics, timing, convergence helpers."""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

import numpy as np


def absolute_error(computed: float | np.ndarray, exact: float | np.ndarray) -> float:
    """Max absolute error between computed and exact values."""
    return float(np.max(np.abs(np.asarray(computed) - np.asarray(exact))))


def relative_error(computed: float | np.ndarray, exact: float | np.ndarray) -> float:
    """Max relative error. Falls back to absolute error where exact is zero."""
    computed = np.asarray(computed, dtype=float)
    exact = np.asarray(exact, dtype=float)
    denom = np.where(np.abs(exact) > 0, np.abs(exact), 1.0)
    return float(np.max(np.abs(computed - exact) / denom))


def convergence_order(errors: np.ndarray, h_values: np.ndarray) -> float:
    """Estimate convergence order from log-log slope of error vs. step size."""
    errors = np.asarray(errors, dtype=float)
    h_values = np.asarray(h_values, dtype=float)
    log_e = np.log(errors)
    log_h = np.log(h_values)
    slope, _ = np.polyfit(log_h, log_e, 1)
    return float(slope)


def linear_interpolate(
    x_grid: np.ndarray, y_grid: np.ndarray, x_query: np.ndarray
) -> np.ndarray:
    """Linear interpolation of y_grid sampled at x_grid, evaluated at x_query.

    y_grid may be 1D (shape (n,)) or 2D (shape (n, d)). x_grid must be sorted.
    """
    x_grid = np.asarray(x_grid, dtype=float)
    y_grid = np.asarray(y_grid, dtype=float)
    x_query = np.atleast_1d(np.asarray(x_query, dtype=float))

    if y_grid.ndim == 1:
        return np.interp(x_query, x_grid, y_grid)

    out = np.empty((x_query.shape[0], y_grid.shape[1]), dtype=float)
    for j in range(y_grid.shape[1]):
        out[:, j] = np.interp(x_query, x_grid, y_grid[:, j])
    return out


@contextmanager
def timer() -> Iterator[dict]:
    """Context manager that records elapsed wall-clock seconds in result['elapsed']."""
    result: dict = {}
    start = time.perf_counter()
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - start


def latex_table(data: dict, headers: list[str]) -> str:
    """Generate a LaTeX tabular block from a dict of column -> sequence."""
    n_rows = len(next(iter(data.values())))
    cols = "l" + "r" * (len(headers) - 1)
    lines = [
        "\\begin{tabular}{" + cols + "}",
        "\\hline",
        " & ".join(headers) + " \\\\",
        "\\hline",
    ]
    for i in range(n_rows):
        row = [str(data[h][i]) for h in headers]
        lines.append(" & ".join(row) + " \\\\")
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    return "\n".join(lines)
