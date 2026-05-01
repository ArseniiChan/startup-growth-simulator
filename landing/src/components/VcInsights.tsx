/**
 * VcInsights — the dark-navy band that breaks the editorial-light flow.
 *
 * Positioned right after the μ* slider section (where the visitor has
 * just dragged the threshold and seen the finding). This is the moment
 * a VC reader is asking themselves "OK but what does this mean for me?"
 * — and the band answers in their language.
 *
 * Three numbered takeaways, intentionally written in VC vocabulary
 * (boundary, calibration uncertainty, defensible-CI). The band
 * inverts the page's normal palette (navy bg, white type, slate-300
 * for muted) which gives it visual weight as a "stop and read" moment.
 */

const ACCENT = "#F87171"; // softer accent on dark — pure red-600 reads too hot

const INSIGHTS = [
  {
    n: "01",
    headline: "Retention dominates growth in survival math.",
    body:
      "On the sensitivity tornado, conversion rate α moves the boundary ~6× more than growth rate g; billing-cycle lag μ_R moves it ~2× more than g. The VC instinct that retention matters more than acquisition has a closed-form math version — and the multiple is sharper than most people guess.",
  },
  {
    n: "02",
    headline: "Calibration ambiguity barely shifts the answer.",
    body:
      "When (g, μ_R) can't be separately identified from data — a curved valley in parameter space — the boundary μ* still varies by only ~2.4% along the worst direction. Caveat: this is the conditional CI, holding α at its calibrated MAP. The marginal CI under joint (α, g, μ_R) uncertainty is wider; full joint posterior is deferred work.",
  },
  {
    n: "03",
    headline: "The boundary exists, and a bad quarter walks you toward it.",
    body:
      "Default profiles sit around μ ≈ 3% monthly churn — well below the 14.2% non-viability boundary. But every company within ~5pp of the boundary is one cohort retention shock away from non-recovery. The model's job isn't to say 'companies are safe' — it's to draw the line and quantify the daylight.",
  },
];

export function VcInsights() {
  return (
    <section id="insights" className="scroll-mt-20 bg-ink text-white">
      <div className="mx-auto max-w-6xl px-6 py-20 sm:px-10 sm:py-24">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">
          What a VC would learn from this model
        </p>
        <h2 className="mt-5 max-w-3xl text-3xl font-semibold leading-tight tracking-tight text-white sm:text-4xl">
          Three takeaways the math earns.
        </h2>

        <ol className="mt-14 grid gap-12 sm:grid-cols-3 sm:gap-10">
          {INSIGHTS.map((insight) => (
            <li key={insight.n} className="flex flex-col gap-4">
              <span
                className="font-mono text-sm font-semibold"
                style={{ color: ACCENT }}
              >
                {insight.n}
              </span>
              <h3 className="text-lg font-semibold leading-snug text-white">
                {insight.headline}
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                {insight.body}
              </p>
            </li>
          ))}
        </ol>

        <div className="mt-14 max-w-3xl border-t border-white/10 pt-8">
          <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-400">
            About the data
          </p>
          <p className="mt-3 text-sm leading-relaxed text-slate-300">
            The five archetype profiles above (High-ARPU SaaS, Horizontal
            SaaS, Two-sided marketplace, Enterprise-cycle, Consumer
            subscription) are{" "}
            <span className="text-white">illustrative parameter sets</span>{" "}
            chosen to span the realistic shape space of subscription
            businesses. They are <span className="text-white">not</span>{" "}
            calibrated to any specific company's financials. The 14.2%
            headline is the bisection root of Cash(T=120) for the default-SaaS
            archetype, computed by the from-scratch numerical pipeline.
          </p>
          <p className="mt-3 text-sm leading-relaxed text-slate-300">
            The structural findings — that μ* exists, that it is robust to
            calibration ambiguity (~2.4%), that the sensitivity ordering is
            α &gt; μ_R &gt; g — survive any recalibration to a real subscription
            business with comparable cost structure. The methodology is the
            artifact, not the specific number.
          </p>
        </div>
      </div>
    </section>
  );
}
