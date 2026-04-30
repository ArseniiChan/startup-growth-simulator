"use client";

/**
 * PosteriorHistogram — the Monte Carlo posterior over μ*.
 *
 * Reads /data/mc_posterior.json (200 sample mu* values + bin histogram)
 * and renders the distribution with a 95% credible-interval band shaded
 * underneath. The point estimate is marked with a red vertical line.
 *
 * Renders as Recharts BarChart for a clean editorial bar histogram.
 */

import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface PosteriorPayload {
  samples: number[];
  bin_edges: number[];
  bin_counts: number[];
  mean_mu_star: number;
  ci_low: number;
  ci_high: number;
  n_samples: number;
}

const ACCENT = "#DC2626";
const INK = "#0F172A";
const MUTED = "#475569";
const RULE = "#E2E8F0";

export function PosteriorHistogram() {
  const [data, setData] = useState<PosteriorPayload | null>(null);

  useEffect(() => {
    fetch("/data/mc_posterior.json")
      .then((r) => r.json())
      .then(setData);
  }, []);

  const series = useMemo(() => {
    if (!data) return [];
    return data.bin_counts.map((count, i) => ({
      bin: ((data.bin_edges[i] + data.bin_edges[i + 1]) / 2) * 100, // mu* in %
      count,
    }));
  }, [data]);

  if (!data) {
    return <div className="aspect-[2/1] w-full animate-pulse rounded-md border border-rule bg-cream" />;
  }

  const meanPct = data.mean_mu_star * 100;
  const ciLowPct = data.ci_low * 100;
  const ciHighPct = data.ci_high * 100;

  return (
    <div>
      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <Stat label="Mean μ*" value={`${meanPct.toFixed(2)}%`} accent />
        <Stat label="95% CI low" value={`${ciLowPct.toFixed(2)}%`} />
        <Stat label="95% CI high" value={`${ciHighPct.toFixed(2)}%`} />
      </div>

      <div className="h-[260px] rounded-md border border-rule bg-white p-3 sm:h-[300px] sm:p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={series} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
            <CartesianGrid stroke={RULE} strokeDasharray="2 4" vertical={false} />
            <XAxis
              dataKey="bin"
              type="number"
              domain={["dataMin", "dataMax"]}
              tickFormatter={(v) => `${(v as number).toFixed(1)}%`}
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
              width={36}
            />
            <Tooltip
              contentStyle={{
                background: "#FFFFFF",
                border: `1px solid ${RULE}`,
                borderRadius: 6,
                fontSize: 12,
                fontFamily: "var(--font-jetbrains)",
              }}
              labelFormatter={(v) => `μ* ≈ ${(v as number).toFixed(2)}%`}
            />
            <ReferenceArea
              x1={ciLowPct}
              x2={ciHighPct}
              fill={ACCENT}
              fillOpacity={0.06}
              ifOverflow="visible"
            />
            <ReferenceLine
              x={meanPct}
              stroke={ACCENT}
              strokeWidth={2}
              strokeDasharray="4 4"
              label={{
                value: `mean ${meanPct.toFixed(1)}%`,
                position: "top",
                fill: ACCENT,
                fontSize: 11,
                fontFamily: "var(--font-jetbrains)",
              }}
            />
            <Bar dataKey="count" fill={INK} fillOpacity={0.85} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="mt-4 text-xs text-muted">
        Posterior over μ* from {data.n_samples} Monte Carlo draws of (g, μ_R)
        from their calibration distribution. Each draw triggers a fresh
        bisection on Cash(T=120). The shaded band is the 95% credible
        interval; the dashed line is the posterior mean.
      </p>
    </div>
  );
}

function Stat({
  label,
  value,
  accent = false,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div className="rounded-md border border-rule bg-white px-4 py-3">
      <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
        {label}
      </div>
      <div
        className={`mt-1 font-mono text-xl font-bold ${
          accent ? "text-accent" : "text-ink"
        }`}
      >
        {value}
      </div>
    </div>
  );
}
