"use client";

/**
 * TornadoChart — sensitivity bars for d(mu_star) / d(param).
 *
 * Reads /data/tornado.json. Sorted by absolute magnitude. Positive bars
 * (parameter increase pushes μ* up — companies become harder to kill)
 * point right in green; negative bars (parameter increase pushes μ* down)
 * point left in red. The convention echoes financial tornado charts
 * (good news right, bad news left) which is what a VC reader expects.
 */

import { useEffect, useMemo, useState } from "react";

interface TornadoPayload {
  params: string[];
  values: number[];
  abs_values: number[];
}

const SURVIVE = "#0F766E";
const ACCENT = "#DC2626";
const INK = "#0F172A";
const MUTED = "#475569";
const RULE = "#E2E8F0";

const PARAM_LABELS: Record<string, string> = {
  g: "g · growth rate",
  K: "K · market size",
  alpha: "α · conversion rate",
  p: "p · ARPU",
  mu_R: "μ_R · billing-cycle lag",
  F: "F · fixed costs",
  v: "v · variable cost per acquisition",
};

export function TornadoChart() {
  const [data, setData] = useState<TornadoPayload | null>(null);

  useEffect(() => {
    fetch("/data/tornado.json")
      .then((r) => r.json())
      .then(setData);
  }, []);

  const sorted = useMemo(() => {
    if (!data) return [];
    return data.params
      .map((p, i) => ({ name: p, value: data.values[i], abs: data.abs_values[i] }))
      .sort((a, b) => b.abs - a.abs);
  }, [data]);

  if (!data) {
    return <div className="aspect-[2/1] w-full animate-pulse rounded-md border border-rule bg-cream" />;
  }

  const maxAbs = sorted.length > 0 ? sorted[0].abs : 1;

  return (
    <div className="rounded-md border border-rule bg-white p-5 sm:p-7">
      <ul className="space-y-4">
        {sorted.map((row) => {
          const widthPct = (row.abs / maxAbs) * 50;
          const isPositive = row.value >= 0;
          return (
            <li key={row.name} className="grid grid-cols-[120px_1fr_80px] items-center gap-4 sm:grid-cols-[180px_1fr_100px] sm:gap-6">
              <span className="font-mono text-xs text-muted sm:text-sm">
                {PARAM_LABELS[row.name] ?? row.name}
              </span>
              <div className="relative h-7 sm:h-8">
                {/* Center line */}
                <div className="absolute left-1/2 top-0 h-full w-px bg-rule" />
                {/* Bar */}
                <div
                  className="absolute top-0 h-full rounded-sm transition-all duration-500"
                  style={{
                    width: `${widthPct}%`,
                    background: isPositive ? SURVIVE : ACCENT,
                    opacity: 0.85,
                    left: isPositive ? "50%" : `${50 - widthPct}%`,
                  }}
                />
              </div>
              <span
                className={`font-mono text-xs font-semibold sm:text-sm ${
                  isPositive ? "text-emerald-700" : "text-accent"
                }`}
              >
                {row.value > 0 ? "+" : ""}
                {row.value.toFixed(2)}
              </span>
            </li>
          );
        })}
      </ul>
      <div className="mt-6 flex items-center justify-between text-[11px] text-muted">
        <span>← decreases μ* (makes failure easier)</span>
        <span>increases μ* (makes failure harder) →</span>
      </div>
    </div>
  );
}
