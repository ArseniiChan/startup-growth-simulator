"use client";

/**
 * ShopifyAnchor — the real-data anchor section.
 *
 * Reads /data/shopify_calibration.json (output of the engine's Adam
 * optimizer fitting g against Shopify's pre-IPO S-1 quarterly revenue,
 * 9 quarters from 2012-Q4 through 2014-Q4). Displays:
 *
 *   - The recovered growth rate g (the only fitted parameter)
 *   - The anchored (held-fixed) parameters with public-data citations
 *   - A line chart overlaying the engine's fitted trajectory against the
 *     observed quarterly points
 *
 * This is the section that closes the credibility gap on the synthetic-
 * archetype story: "yes, we showed you 5 illustrative shapes upstream;
 * here is the engine fit against actual SEC-filed numbers from a real
 * company you can look up yourself."
 */

import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ComposedChart,
} from "recharts";

interface ShopifyPayload {
  company: string;
  ticker: string;
  source: string;
  calibrated: {
    g: number;
    K: number;
    mu_R: number;
    alpha_anchored: number;
    mu_anchored: number;
    p_anchored: number;
    F_anchored: number;
    v_anchored: number;
  };
  loss_history: number[];
  final_loss: number;
  iterations: number;
  converged: boolean;
  observed: { month: number; revenue_monthly_usd: number; quarter_label: string }[];
  fitted: { month: number; revenue_monthly_usd: number }[];
  mu_star: number | null;
  horizon_months: number;
}

const ACCENT = "#DC2626";
const INK = "#0F172A";
const MUTED = "#475569";
const RULE = "#E2E8F0";

export function ShopifyAnchor() {
  const [data, setData] = useState<ShopifyPayload | null>(null);

  useEffect(() => {
    fetch("/data/shopify_calibration.json")
      .then((r) => r.json())
      .then(setData);
  }, []);

  // Build the merged chart data: fitted curve as continuous line + observed
  // quarterly points as scatter overlays.
  const chartData = useMemo(() => {
    if (!data) return [];
    const obsByMonth = new Map<number, number>();
    data.observed.forEach((o) => obsByMonth.set(o.month, o.revenue_monthly_usd));
    return data.fitted.map((f) => ({
      month: f.month,
      fitted: f.revenue_monthly_usd / 1e6,
      observed: obsByMonth.has(f.month) ? obsByMonth.get(f.month)! / 1e6 : null,
    }));
  }, [data]);

  if (!data) {
    return <div className="aspect-[2/1] w-full animate-pulse rounded-md border border-rule bg-cream" />;
  }

  return (
    <div className="grid gap-10 lg:grid-cols-[2fr_3fr] lg:items-start lg:gap-16">
      {/* Left column: parameter table + caveat */}
      <div>
        <div className="rounded-md border border-rule bg-white p-5 sm:p-6">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            Calibrated against {data.company}
          </p>
          <p className="mt-2 font-mono text-xs text-muted">{data.source}</p>

          <div className="mt-6 flex items-baseline gap-2">
            <span className="font-mono text-4xl font-bold text-accent">
              {(data.calibrated.g * 100).toFixed(1)}<span className="text-2xl">%</span>
            </span>
            <span className="font-mono text-sm text-muted">
              monthly user-growth (recovered)
            </span>
          </div>

          <p className="mt-2 text-xs leading-relaxed text-muted">
            Adam optimizer, 1-parameter fit (g only). Converged in{" "}
            <span className="text-ink">{data.iterations}</span> iterations.
            K, mu_R held at anchored values — short revenue data alone
            cannot distinguish them from g (the curved-valley finding upstream).
          </p>

          <div className="mt-6 border-t border-rule pt-5">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">
              Anchored parameters (held fixed during fit)
            </p>
            <dl className="mt-3 grid grid-cols-2 gap-2 font-mono text-xs">
              <ParamRow label="ARPU (p)" value={`$${data.calibrated.p_anchored}/mo`} />
              <ParamRow label="Churn (μ)" value={`${(data.calibrated.mu_anchored * 100).toFixed(1)}%/mo`} />
              <ParamRow label="Conversion (α)" value={`${(data.calibrated.alpha_anchored * 100).toFixed(0)}%`} />
              <ParamRow label="Lag (μ_R)" value={`${data.calibrated.mu_R.toFixed(2)}`} />
              <ParamRow label="Fixed costs (F)" value={`$${(data.calibrated.F_anchored / 1e6).toFixed(1)}M/mo`} />
              <ParamRow label="CAC (v)" value={`$${data.calibrated.v_anchored}`} />
              <ParamRow label="Market (K)" value={`${(data.calibrated.K / 1e6).toFixed(1)}M`} />
            </dl>
          </div>

          {data.mu_star == null && (
            <div className="mt-6 rounded-md bg-cream p-4">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">
                A real finding
              </p>
              <p className="mt-2 text-sm leading-relaxed text-ink">
                At these calibrated parameters, the survival boundary μ\* is
                undefined within the physical churn range (μ ∈ [0.5%, 49.9%]).
                Shopify's cost structure relative to revenue keeps the company
                cash-positive over the 10-year horizon at every churn rate
                we tested.
              </p>
              <p className="mt-2 text-sm leading-relaxed text-muted">
                The boundary exists for less-funded archetypes (default-SaaS:
                14.2%) but not for a company at Shopify's scale. The model
                tells you not just where the line is — but whether your cost
                structure is even close to it.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Right column: fitted vs observed chart */}
      <div>
        <div className="rounded-md border border-rule bg-white p-4 sm:p-6">
          <div className="mb-4 flex items-baseline justify-between">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">
              Engine fit vs S-1 quarterly revenue
            </p>
            <p className="font-mono text-[10px] text-muted">
              R² visual; loss = {(data.final_loss / 1e12).toFixed(2)}×10¹²
            </p>
          </div>

          <div className="h-[360px] sm:h-[420px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 12, right: 16, left: 4, bottom: 12 }}>
                <CartesianGrid stroke={RULE} strokeDasharray="2 4" vertical={false} />
                <XAxis
                  dataKey="month"
                  type="number"
                  domain={[0, 27]}
                  ticks={[0, 6, 12, 18, 24]}
                  tickFormatter={(v) => `${v}m`}
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
                  labelFormatter={(v) => `month ${v}`}
                  formatter={(v, name) => {
                    if (v == null) return ["—", String(name ?? "")];
                    return [`$${(v as number).toFixed(2)}M`, String(name ?? "")];
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="fitted"
                  stroke={INK}
                  strokeWidth={2}
                  dot={false}
                  name="Engine fit"
                  isAnimationActive={false}
                />
                <Scatter
                  dataKey="observed"
                  fill={ACCENT}
                  name="Shopify S-1 quarterly"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-3 flex items-center gap-4 font-mono text-[10px] text-muted">
            <span className="flex items-center gap-1.5">
              <span className="block h-0.5 w-4 bg-ink" /> Engine RK4 fit (continuous)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="block h-2 w-2 rounded-full" style={{ background: ACCENT }} />
              Shopify S-1 quarterly (observed)
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function ParamRow({ label, value }: { label: string; value: string }) {
  return (
    <>
      <dt className="text-muted">{label}</dt>
      <dd className="text-ink">{value}</dd>
    </>
  );
}
