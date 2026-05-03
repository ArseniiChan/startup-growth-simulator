"""Render presentation-quality figures for the deck.

Two outputs go to ``report/figures/``:

1. ``nb_shopify_fit.png`` — engine RK4 fit overlaid on Shopify's 9 F-1
   quarterly revenue points (reads ``shopify_calibration.json``).
2. ``pres_loss_surface.png`` — clean redraw of the calibration loss
   surface (reads ``valley_surface.json``). The notebook-exported version
   has overlapping contour value labels in the dense valley region; this
   redraw uses a filled colormap + unlabeled contour lines + truth marker
   so the curved-valley shape reads cleanly at slide size.

Both inputs are JSON files the Vercel landing already consumes, so this
script depends only on ``json`` and ``matplotlib``.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent
SHOPIFY_JSON = REPO / "landing" / "public" / "data" / "shopify_calibration.json"
VALLEY_JSON = REPO / "landing" / "public" / "data" / "valley_surface.json"
SHOPIFY_OUT = REPO / "report" / "figures" / "nb_shopify_fit.png"
VALLEY_OUT = REPO / "report" / "figures" / "pres_loss_surface.png"

# Palette aligned with the deck (navy ink, coral accent for the data points)
INK = "#1E2761"
ACCENT = "#F96167"
MUTED = "#64748B"
RULE = "#E2E8F0"


def render_shopify() -> None:
    payload = json.loads(SHOPIFY_JSON.read_text())

    fitted_months = [pt["month"] for pt in payload["fitted"]]
    fitted_rev_m = [pt["revenue_monthly_usd"] / 1e6 for pt in payload["fitted"]]
    obs_months = [pt["month"] for pt in payload["observed"]]
    obs_rev_m = [pt["revenue_monthly_usd"] / 1e6 for pt in payload["observed"]]

    fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=150)

    # Engine RK4 fit — continuous line in ink
    ax.plot(
        fitted_months,
        fitted_rev_m,
        color=INK,
        linewidth=2.2,
        label="Engine RK4 fit (g recovered)",
        zorder=2,
    )
    # Observed F-1 quarterly revenue — coral scatter
    ax.scatter(
        obs_months,
        obs_rev_m,
        color=ACCENT,
        s=72,
        edgecolor="white",
        linewidth=1.5,
        zorder=3,
        label="Shopify F-1 quarterly (observed)",
    )

    ax.set_xlabel("Month (0 = 2012-Q4)", fontsize=11, color=INK)
    ax.set_ylabel("Monthly revenue (USD millions)", fontsize=11, color=INK)
    ax.set_xlim(-0.5, 27.5)
    ax.set_ylim(0, max(max(fitted_rev_m), max(obs_rev_m)) * 1.08)
    ax.set_xticks([0, 6, 12, 18, 24])
    ax.tick_params(axis="both", colors=MUTED, labelsize=10)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(RULE)
    ax.grid(axis="y", color=RULE, linestyle="--", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False, fontsize=10)

    fig.tight_layout()
    SHOPIFY_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SHOPIFY_OUT, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {SHOPIFY_OUT}")
    print(f"  iterations: {payload['iterations']}")
    print(f"  g recovered: {payload['calibrated']['g']:.4f} ({payload['calibrated']['g']*100:.2f}%/mo)")


def render_valley() -> None:
    """Redraw the calibration loss surface without the overlapping clabel
    annotations the notebook export has. We use a filled colormap to show
    loss magnitude and overlay sparse contour lines (no text labels) so the
    curved valley reads as a clean shape at slide size."""
    payload = json.loads(VALLEY_JSON.read_text())

    g_axis = np.array(payload["g"])
    mu_R_axis = np.array(payload["mu_R"])
    # The JSON stores raw MSE loss values (range ~568 .. 1.5e9). The
    # log_loss_min/max fields are pre-computed natural logs. Take log here
    # so the colormap and contours operate on the same dynamic range the
    # axis bounds describe.
    raw_loss = np.array(payload["loss"])
    log_loss = np.log(raw_loss)
    truth = payload["truth"]

    G, M = np.meshgrid(g_axis, mu_R_axis)

    fig, ax = plt.subplots(figsize=(7.0, 4.5), dpi=150)

    # Filled magnitude background — viridis_r so dark = low loss (the valley).
    pcm = ax.pcolormesh(
        G, M, log_loss,
        cmap="viridis_r",
        shading="auto",
        vmin=payload["log_loss_min"],
        vmax=payload["log_loss_max"],
    )

    # Sparse contour lines, no text labels.
    levels = np.linspace(payload["log_loss_min"], payload["log_loss_max"], 14)
    ax.contour(
        G, M, log_loss,
        levels=levels,
        colors="#0F172A",
        linewidths=0.6,
        alpha=0.45,
    )

    # Truth marker
    ax.scatter(
        [truth["g"]],
        [truth["mu_R"]],
        marker="*",
        s=240,
        color=ACCENT,
        edgecolor="white",
        linewidth=1.5,
        zorder=5,
        label="truth (g=0.15, μ_R=0.04)",
    )

    ax.set_xlabel("g  (growth rate)", fontsize=11, color=INK)
    ax.set_ylabel("μ_R  (lag rate)", fontsize=11, color=INK)
    ax.set_title(
        "Calibration loss surface — the curved valley",
        fontsize=12, color=INK, pad=10,
    )
    ax.tick_params(axis="both", colors=MUTED, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color(RULE)
    ax.legend(loc="upper right", frameon=True, fontsize=10, framealpha=0.92)

    cbar = fig.colorbar(pcm, ax=ax, pad=0.02, fraction=0.045)
    cbar.set_label("ln(MSE loss)", fontsize=10, color=INK)
    cbar.ax.tick_params(labelsize=9, colors=MUTED)
    cbar.outline.set_edgecolor(RULE)

    fig.tight_layout()
    VALLEY_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(VALLEY_OUT, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {VALLEY_OUT}")
    print(f"  grid: {len(g_axis)}x{len(mu_R_axis)},  log_loss in "
          f"[{payload['log_loss_min']:.2f}, {payload['log_loss_max']:.2f}]")


if __name__ == "__main__":
    render_shopify()
    render_valley()
