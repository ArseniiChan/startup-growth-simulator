"""Render Figure 8 (sensitivity tornado) from the current tornado.json.

The earlier figure embedded in the report (rendered from notebook 05 long ago)
shows the historical sensitivity values 3.04 / 1.18 / 0.51 for alpha / mu_R / g,
but the report body now cites the values from the current tornado.json
(2.70 / 1.35 / negligible). This script regenerates the figure so it agrees
with the report's caption.

Reads:   landing/public/data/tornado.json
Writes:  report/figures/nb05_tornado.png
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
TORNADO_JSON = REPO / "landing" / "public" / "data" / "tornado.json"
OUT_PNG = REPO / "report" / "figures" / "nb05_tornado.png"


def render() -> None:
    payload = json.loads(TORNADO_JSON.read_text())
    params: list[str] = payload["params"]
    values: list[float] = payload["values"]

    # Pair param-name to value and sort by |value| ascending so the
    # largest bars land at the TOP after matplotlib's barh draws bottom-up.
    pairs = list(zip(params, values))
    pairs.sort(key=lambda x: abs(x[1]))

    sorted_params = [p for p, _ in pairs]
    sorted_values = [v for _, v in pairs]

    # Colors: green for positive, red for negative, light gray for zero
    colors = []
    for v in sorted_values:
        if v > 0:
            colors.append("#2E8B57")
        elif v < 0:
            colors.append("#C04A4A")
        else:
            colors.append("#C8C8C8")

    fig, ax = plt.subplots(figsize=(7.0, 4.0), dpi=150)
    ax.barh(sorted_params, sorted_values, color=colors,
            edgecolor="black", linewidth=0.4)
    ax.axvline(0, color="black", linewidth=0.6)
    ax.set_xlabel(r"$\partial\mu^*/\partial\theta$  (1/(unit of $\theta$))",
                  fontsize=11)
    ax.set_title(r"Sensitivity of $\mu^*$ to each model parameter (central difference)",
                 fontsize=11)
    ax.tick_params(axis="both", labelsize=10)
    ax.set_xlim(left=min(0, min(sorted_values) * 1.1),
                right=max(sorted_values) * 1.1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT_PNG}")
    print(f"  values: " + ", ".join(f"{p}={v:.3f}" for p, v in pairs[::-1]))


if __name__ == "__main__":
    render()
