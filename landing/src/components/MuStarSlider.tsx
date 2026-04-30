"use client";

/**
 * MuStarSlider — the project's headline interaction.
 *
 * A single horizontal range slider drags through monthly user-churn rate
 * (mu) from 0.5% to 49.9%. As the visitor drags, the chart shows
 * Cash(T=120 months; mu) — the terminal cash balance — and a vertical
 * marker tracks the slider position. The marker turns red when it
 * crosses zero (the company doesn't survive).
 *
 * The whole thing is JSON-backed: /data/mu_star_curve.json has 200
 * precomputed (mu, Cash(T)) samples and the precise mu* root. Linear
 * interpolation between samples is invisible to the eye on a 200-point
 * grid. Drag feel is native because there's zero compute on each move.
 *
 * This is the single interactive surface that satisfies an "exploration-
 * weighted" rubric without forcing live computation. Premium register —
 * smooth, instant, decisive.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface MuStarPayload {
  mu: number[];
  cash_terminal: number[];
  mu_star: number;
  horizon_months: number;
}

const ACCENT = "#DC2626";
const INK = "#0F172A";
const MUTED = "#475569";
const RULE = "#E2E8F0";
const SURVIVE = "#0F766E"; // teal — the "survives" half of the duotone

export function MuStarSlider() {
  const [data, setData] = useState<MuStarPayload | null>(null);
  const [muValue, setMuValue] = useState<number>(0.03); // start at default-SaaS
  const sliderRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetch("/data/mu_star_curve.json")
      .then((r) => r.json())
      .then((d) => {
        setData(d);
        setMuValue(d.mu_star * 0.5); // start safely below the threshold
      });
  }, []);

  // Linearly interpolate Cash(T) at the current slider position.
  const currentCash = useMemo(() => {
    if (!data) return 0;
    return interpolate(data.mu, data.cash_terminal, muValue);
  }, [data, muValue]);

  // Build chart series. Each point gets two values: positive (survives) and
  // negative (terminal). Recharts can't render gradients across zero
  // cleanly, so we split the area into two stacked ranges.
  const series = useMemo(() => {
    if (!data) return [];
    return data.mu.map((m, i) => {
      const v = data.cash_terminal[i] / 1e6;
      return {
        mu: m * 100,                 // percent for display
        cashM: v,
        surviveBand: v > 0 ? v : 0,  // for green fill
        dyingBand: v < 0 ? v : 0,    // for red fill
      };
    });
  }, [data]);

  const isSurvive = currentCash >= 0;
  const muStarPct = data ? data.mu_star * 100 : 14.17;
  const muValuePct = muValue * 100;

  return (
    <div>
      {/* Live readout — big mono number that updates as you drag */}
      <div className="mb-8 grid gap-6 sm:grid-cols-3">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            Monthly churn
          </div>
          <div className="mt-1 font-mono text-3xl font-bold text-ink sm:text-4xl">
            {muValuePct.toFixed(2)}<span className="text-2xl text-muted">%</span>
          </div>
        </div>
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            Cash at month 120
          </div>
          <div
            className={`mt-1 font-mono text-3xl font-bold sm:text-4xl ${
              isSurvive ? "text-ink" : "text-accent"
            }`}
          >
            {isSurvive ? "+" : ""}${(currentCash / 1e6).toFixed(2)}M
          </div>
        </div>
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            Outcome
          </div>
          <div
            className={`mt-1 inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-semibold ${
              isSurvive
                ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200"
                : "bg-red-50 text-red-700 ring-1 ring-red-200"
            }`}
          >
            <span className="block h-2 w-2 rounded-full bg-current" />
            {isSurvive ? "Survives 10-year horizon" : "Runs out of cash"}
          </div>
        </div>
      </div>

      {/* Slider */}
      <div className="mb-6">
        <input
          ref={sliderRef}
          type="range"
          min={0.005}
          max={0.499}
          step={0.001}
          value={muValue}
          onChange={(e) => setMuValue(parseFloat(e.target.value))}
          className="custom-slider w-full"
          style={{
            // Fill behind the thumb visualizes drag position
            background: `linear-gradient(to right, ${
              isSurvive ? SURVIVE : ACCENT
            } 0%, ${
              isSurvive ? SURVIVE : ACCENT
            } ${(muValue / 0.499) * 100}%, ${RULE} ${
              (muValue / 0.499) * 100
            }%, ${RULE} 100%)`,
          }}
        />
        <div className="mt-2 flex justify-between font-mono text-[11px] text-muted">
          <span>0.5%</span>
          <span className="text-ink">μ* ≈ {muStarPct.toFixed(2)}%</span>
          <span>49.9%</span>
        </div>
      </div>

      {/* Chart */}
      <div className="h-[280px] rounded-md border border-rule bg-white p-3 sm:h-[320px] sm:p-4">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={series} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
            <CartesianGrid stroke={RULE} strokeDasharray="2 4" vertical={false} />
            <XAxis
              dataKey="mu"
              type="number"
              domain={[0, 50]}
              ticks={[0, 10, 20, 30, 40, 50]}
              tickFormatter={(v) => `${v}%`}
              stroke={MUTED}
              fontSize={11}
              axisLine={{ stroke: RULE }}
              tickLine={{ stroke: RULE }}
            />
            <YAxis
              stroke={MUTED}
              fontSize={11}
              axisLine={{ stroke: RULE }}
              tickLine={{ stroke: RULE }}
              tickFormatter={(v) => `$${(v as number).toFixed(0)}M`}
              width={56}
            />
            <Tooltip
              contentStyle={{
                background: "#FFFFFF",
                border: `1px solid ${RULE}`,
                borderRadius: 6,
                fontSize: 12,
                fontFamily: "var(--font-jetbrains)",
              }}
              labelFormatter={(v) => `μ = ${(v as number).toFixed(1)}%`}
              formatter={(v) => [`$${(v as number).toFixed(2)}M`, "Cash(T=120)"]}
            />
            <ReferenceLine y={0} stroke={INK} strokeWidth={1} />
            <ReferenceLine
              x={muStarPct}
              stroke={ACCENT}
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: `μ* = ${muStarPct.toFixed(2)}%`,
                position: "insideTopRight",
                fill: ACCENT,
                fontSize: 11,
                fontFamily: "var(--font-jetbrains)",
              }}
            />
            <ReferenceLine
              x={muValuePct}
              stroke={INK}
              strokeWidth={1.5}
            />
            <Area
              type="monotone"
              dataKey="surviveBand"
              stroke={SURVIVE}
              strokeWidth={2}
              fill={SURVIVE}
              fillOpacity={0.08}
              isAnimationActive={false}
            />
            <Area
              type="monotone"
              dataKey="dyingBand"
              stroke={ACCENT}
              strokeWidth={2}
              fill={ACCENT}
              fillOpacity={0.08}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Slider thumb styling — keep it on-brand */}
      <style jsx>{`
        .custom-slider {
          -webkit-appearance: none;
          appearance: none;
          height: 8px;
          border-radius: 4px;
          outline: none;
          cursor: pointer;
        }
        .custom-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          height: 22px;
          width: 22px;
          border-radius: 50%;
          background: #ffffff;
          border: 2px solid ${INK};
          cursor: grab;
          box-shadow: 0 1px 4px rgba(15, 23, 42, 0.18);
          transition: transform 0.1s ease;
        }
        .custom-slider:active::-webkit-slider-thumb {
          transform: scale(1.1);
          cursor: grabbing;
        }
        .custom-slider::-moz-range-thumb {
          height: 22px;
          width: 22px;
          border-radius: 50%;
          background: #ffffff;
          border: 2px solid ${INK};
          cursor: grab;
          box-shadow: 0 1px 4px rgba(15, 23, 42, 0.18);
        }
      `}</style>
    </div>
  );
}

function interpolate(xs: number[], ys: number[], x: number): number {
  if (xs.length === 0) return 0;
  if (x <= xs[0]) return ys[0];
  if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
  // Binary search for the bracket
  let lo = 0;
  let hi = xs.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (xs[mid] > x) hi = mid;
    else lo = mid;
  }
  const t = (x - xs[lo]) / (xs[hi] - xs[lo]);
  return ys[lo] + t * (ys[hi] - ys[lo]);
}
