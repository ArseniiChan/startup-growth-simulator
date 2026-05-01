"use client";

/**
 * TrajectoryChart — the 4-panel U(t) / A(t) / R(t) / Cash(t) line chart.
 *
 * Reads from /data/profiles.json (5 profiles × 121 timesteps each, ~48 KB).
 * Profile chips along the top let the visitor switch between default-SaaS,
 * SaaS, marketplace, enterprise, viral. Charts re-render with smooth
 * transitions thanks to Recharts' default animationDuration.
 *
 * Editorial Navy palette — pure white panel backgrounds, slate-200 grid,
 * slate-600 axis labels, navy/red/amber series colors that contrast cleanly.
 */

import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface ProfileData {
  params: Record<string, number>;
  t: number[];
  U: number[];
  A: number[];
  R: number[];
  Cash: number[];
  peak_users: number;
  peak_mrr: number;
  terminal_cash: number;
}

interface ProfilesPayload {
  [key: string]: ProfileData;
}

// Profile chip labels are deliberately written in the audience's
// vocabulary — a VC recruiter reads "Stripe-like SaaS" and instantly
// pattern-matches to a known company shape. The underlying data
// (default-saas / saas / marketplace / enterprise / viral) is the
// generic synthetic profile from the engine's preset_profiles().
// The brand names are illustrative shapes, not real-company calibrations.
const PROFILES: { key: string; label: string; subtitle: string }[] = [
  { key: "default-saas", label: "Stripe-like SaaS",      subtitle: "high ARPU, low churn" },
  { key: "saas",         label: "Slack-like SaaS",       subtitle: "mid-market, freemium" },
  { key: "marketplace",  label: "Airbnb-like marketplace", subtitle: "two-sided, low ARPU" },
  { key: "enterprise",   label: "Workday-like enterprise", subtitle: "long sales cycle" },
  { key: "viral",        label: "TikTok-like viral",     subtitle: "very high g, high churn" },
];

// Editorial palette tokens (must match tailwind.config.ts)
const INK = "#0F172A";
const MUTED = "#475569";
const RULE = "#E2E8F0";
const ACCENT = "#DC2626";
const NAVY = "#1E3A8A";

export function TrajectoryChart() {
  const [data, setData] = useState<ProfilesPayload | null>(null);
  const [active, setActive] = useState<string>("default-saas");

  useEffect(() => {
    fetch("/data/profiles.json")
      .then((r) => r.json())
      .then(setData);
  }, []);

  const series = useMemo(() => {
    if (!data || !data[active]) return [];
    const p = data[active];
    return p.t.map((t, i) => ({
      t,
      U: p.U[i],
      A: p.A[i],
      R: p.R[i],
      Cash: p.Cash[i] / 1000, // $ thousands for readability
    }));
  }, [data, active]);

  const profile = data?.[active];
  const activeProfile = PROFILES.find((p) => p.key === active);

  return (
    <div>
      {/* Profile chips */}
      <div className="mb-2 flex flex-wrap gap-2">
        {PROFILES.map((p) => (
          <button
            key={p.key}
            onClick={() => setActive(p.key)}
            title={p.subtitle}
            className={`rounded-full px-4 py-1.5 text-xs font-semibold transition ${
              active === p.key
                ? "bg-ink text-white"
                : "border border-rule bg-white text-muted hover:border-ink hover:text-ink"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>
      {/* Subtitle for active profile — gives the chip a one-line caption
          that lands the company-shape interpretation for a VC reader. */}
      <p className="mb-8 font-mono text-xs text-muted">
        <span className="text-ink">▸</span> {activeProfile?.subtitle ?? ""}
      </p>

      {/* Headline metrics for the active profile */}
      {profile && (
        <div className="mb-8 grid grid-cols-3 gap-4 sm:gap-8">
          <Metric label="Peak users" value={fmtNum(profile.peak_users)} />
          <Metric label="Peak MRR" value={`$${fmtNum(profile.peak_mrr)}`} />
          <Metric
            label="Terminal cash"
            value={`$${fmtNum(profile.terminal_cash)}`}
            negative={profile.terminal_cash < 0}
          />
        </div>
      )}

      {/* 4-panel grid of small multiples */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <PanelChart
          data={series}
          dataKey="U"
          title="Users"
          subtitle="logistic acquisition"
          color={NAVY}
          format={fmtNum}
        />
        <PanelChart
          data={series}
          dataKey="A"
          title="Active paying users"
          subtitle="conversion − churn"
          color="#0F766E"
          format={fmtNum}
        />
        <PanelChart
          data={series}
          dataKey="R"
          title="MRR"
          subtitle="dollars per month"
          color={ACCENT}
          format={(v) => `$${fmtNum(v)}`}
        />
        <PanelChart
          data={series}
          dataKey="Cash"
          title="Cash balance"
          subtitle="thousands of dollars"
          color="#7C3AED"
          format={(v) => `$${fmtNum(v)}K`}
          showZero
        />
      </div>
    </div>
  );
}

function Metric({
  label,
  value,
  negative = false,
}: {
  label: string;
  value: string;
  negative?: boolean;
}) {
  return (
    <div>
      <div className="text-[11px] font-semibold uppercase tracking-wider text-muted">
        {label}
      </div>
      <div
        className={`mt-1 font-mono text-xl font-bold sm:text-2xl ${
          negative ? "text-accent" : "text-ink"
        }`}
      >
        {value}
      </div>
    </div>
  );
}

function PanelChart({
  data,
  dataKey,
  title,
  subtitle,
  color,
  format,
  showZero = false,
}: {
  data: any[];
  dataKey: string;
  title: string;
  subtitle: string;
  color: string;
  format: (v: number) => string;
  showZero?: boolean;
}) {
  return (
    <div className="rounded-md border border-rule bg-white p-4 sm:p-5">
      <div className="mb-3 flex items-baseline justify-between">
        <div>
          <div className="text-sm font-semibold text-ink">{title}</div>
          <div className="text-[11px] text-muted">{subtitle}</div>
        </div>
      </div>
      <div className="h-[180px] sm:h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid stroke={RULE} strokeDasharray="2 4" vertical={false} />
            <XAxis
              dataKey="t"
              type="number"
              domain={[0, 60]}
              ticks={[0, 15, 30, 45, 60]}
              tickFormatter={(v) => `${v}m`}
              stroke={MUTED}
              fontSize={10}
              axisLine={{ stroke: RULE }}
              tickLine={{ stroke: RULE }}
            />
            <YAxis
              stroke={MUTED}
              fontSize={10}
              axisLine={{ stroke: RULE }}
              tickLine={{ stroke: RULE }}
              tickFormatter={(v) => fmtNum(v as number)}
              width={48}
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
              formatter={(v) => [format(v as number), title]}
            />
            {showZero && (
              <ReferenceLine y={0} stroke={INK} strokeWidth={0.75} />
            )}
            <Line
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              strokeWidth={2}
              dot={false}
              isAnimationActive={true}
              animationDuration={400}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// Compact number formatter: 1234567 -> 1.23M, 1234 -> 1.23K
function fmtNum(v: number): string {
  const abs = Math.abs(v);
  if (abs >= 1e9) return `${(v / 1e9).toFixed(2)}B`;
  if (abs >= 1e6) return `${(v / 1e6).toFixed(2)}M`;
  if (abs >= 1e3) return `${(v / 1e3).toFixed(1)}K`;
  return `${v.toFixed(abs < 1 ? 2 : 0)}`;
}
